from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
from os import stat
from pathlib import Path
import re
from socket import gaierror
from typing import Iterator
from urllib.error import URLError
from matplotlib.image import thumbnail

import pytube
from tqdm import tqdm

from archivetube import ROOT_DIR, VIDEO_DIR, error_trace


AVAILABLE_SOURCES = ("local", "pytube", "sql")


def channel_id_to_url(channel_id: str) -> str:
    return f"https://www.youtube.com/channel/{channel_id}"


def channel_url_to_id(channel_url: str) -> str:
    return re.split("/channel/", channel_url)[-1]


def video_id_to_url(video_id: str) -> str:
    return f"https://www.youtube.com/watch?v={video_id}"


def video_url_to_id(video_url: str) -> str:
    return re.split("v=", video_url)[-1]


class Channel:

    def __init__(self,
                 source: str,
                 channel_id: str,
                 channel_name: str,
                 video_ids: list[str] | tuple[str],
                 last_updated: datetime,
                 about_html: str | None = None,
                 community_html: str | None = None,
                 featured_channels_html: str | None = None,
                 videos_html: str | None = None,
                 workers: int | None = 1,
                 parent_dir: Path | None = None):
        self.info = {
            "channel_id": self.check.channel_id(channel_id, self),
            "channel_name": self.check.channel_name(channel_name, self),
            "last_updated": self.check.last_updated(last_updated, self),
            "about_html": self.check.about_html(about_html, self),
            "community_html": self.check.community_html(community_html, self),
            "featured_channels_html": self.check.featured_channels_html(
                featured_channels_html, self),
            "videos_html": self.check.videos_html(videos_html, self)
        }
        self.source = self.check.source(source, self)
        self.video_ids = self.check.video_ids(video_ids, self)
        self.workers = self.check.workers(workers, self)
        self.target_dir = Path(self.check.parent_dir(parent_dir, self),
                               self.info["channel_id"])

    @classmethod
    def from_local(cls,
                   channel_path: Path,
                   progress_bar: bool = True) -> Channel:
        parent_dir = channel_path.parent
        channel_id = channel_path.name
        info_path = Path(channel_path, "info.json")
        if not channel_path.exists():
            err_msg = (f"[{error_trace(cls)}] Channel directory does not "
                       f"exist: {channel_path}")
            raise ValueError(err_msg)
        if not info_path.exists():
            err_msg = (f"[{error_trace(cls)}] Channel directory has no "
                       f"info.json file: {channel_path}")
            raise ValueError(err_msg)

        with info_path.open("r") as info_file:
            saved = json.load(info_file)
        if progress_bar:
            dir_contents = tqdm(channel_path.iterdir(), leave=False)
        else:
            dir_contents = channel_path.iterdir()
        video_ids = [v_dir.name for v_dir in dir_contents if v_dir.is_dir()]
        return cls(source="local",
                   channel_id=channel_id,
                   channel_name=saved["name"],
                   last_updated=datetime.fromisoformat(saved["fetched_at"]),
                   about_html=saved["about_html"],
                   community_html=saved["community_html"],
                   featured_channels_html=saved["featured_channels_html"],
                   videos_html=saved["videos_html"],
                   video_ids=video_ids,
                   parent_dir=parent_dir)

    @classmethod
    def from_pytube(cls,
                    channel_url: str,
                    parent_dir: Path | None = None,
                    progress_bar: bool = True) -> Channel:
        # channel_id = cls.check.channel_id(channel_id, cls)
        # channel_url = channel_id_to_url(channel_id)
        try:
            online = pytube.Channel(channel_url)
            if progress_bar:
                channel_contents = tqdm(online.url_generator(), leave=False)
            else:
                channel_contents = online.url_generator()
            video_ids = [video_url_to_id(url) for url in channel_contents]
            return cls(source="pytube",
                       channel_id=channel_url_to_id(channel_url),
                       channel_name=online.channel_name,
                       last_updated=datetime.now(),
                       about_html=online.about_html,
                       community_html=online.community_html,
                       featured_channels_html=online.featured_channels_html,
                       videos_html=online.html,
                       video_ids=video_ids,
                       parent_dir=parent_dir)
        except (URLError, gaierror) as exc:
            err_msg = (f"[{error_trace(cls)}] Network error when accessing "
                       f"channel: {channel_url}")
            raise ConnectionError(err_msg) from exc
        except (KeyError,
                pytube.exceptions.ExtractError,
                pytube.exceptions.HTMLParseError,
                pytube.exceptions.RegexMatchError) as exc:
            err_msg = (f"[{error_trace(cls)}] Unable to parse pytube channel "
                       f"response: {channel_url}")
            raise KeyError(err_msg) from exc

    @property
    def videos(self) -> Iterator[Video]:
        self.check.source(self.source)
        self.check.workers(self.workers)
        if self.workers and self.workers == 1:
            if self.source == "local":
                for video_id in self.video_ids:
                    yield Video.from_local(self.info["channel_id"], video_id)
            elif self.source == "pytube":
                for video_id in self.video_ids:
                    yield Video.from_pytube(video_id)
            elif self.source == "sql":
                for video_id in self.video_ids:
                    yield Video.from_sql(video_id)
        else:  # multithreading
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                try:
                    if self.source == "local":
                        def dispatch(v_id):
                            return executor.submit(Video.from_local,
                                                   self.info["channel_id"],
                                                   v_id)
                        futures = [dispatch(v_id) for v_id in self.video_ids]
                    elif self.source == "pytube":
                        def dispatch(v_id):
                            return executor.submit(Video.from_pytube, v_id)
                        futures = [dispatch(v_id) for v_id in self.video_ids]
                    elif self.source == "sql":
                        def dispatch(v_id):
                            return executor.submit(Video.from_sql, v_id)
                        futures = [dispatch(v_id) for v_id in self.video_ids]
                    for future in as_completed(futures):
                        yield future.result()
                except (KeyboardInterrupt, SystemExit) as exc:
                    executor.shutdown(cancel_futures=True)
                    raise exc

    def to_json(self, json_path: Path | None = None) -> dict[str, str]:
        result = self.info.copy()
        result["last_updated"] = result["last_updated"].isoformat()
        if json_path:
            if not isinstance(json_path, Path):
                err_msg = (f"[{error_trace(self)}] if provided, `json_path` "
                           f"must be a Path-like object describing where to "
                           f"save the json dictionary")
                raise TypeError(err_msg)
            if json_path.suffix != ".json":
                err_msg = (f"[{error_trace(self)}] `json_path` must end with "
                           f"must end with '.json' extension: {json_path}")
                raise ValueError(err_msg)
            with json_path.open("w") as json_file:
                json_path.parent.mkdir(exist_ok=True)
                json.dump(result, json_file)
        return result


    def __eq__(self, other: Channel) -> bool:
        return (self.info["channel_id"] == other.info["channel_id"] and
                self.info["last_updated"] == other.info["last_updated"])

    def __len__(self) -> int:
        return len(self.video_ids)

    def __repr__(self) -> str:
        def crop_ids(id_list: list[str], threshold: int = 5) -> str:
            if len(id_list) > threshold:
                formatted = "', '".join(id_list[:threshold])
                return f"['{formatted}', ...]"
            return repr(id_list)

        def crop_html(html_response: str, threshold: int = 16) -> str:
            if len(html_response) > threshold:
                return f"'{html_response[:threshold]}...'"
            return repr(html_response)

        prop_dict = {
            "source": repr(self.source),
            "channel_id": repr(self.info["channel_id"]),
            "channel_name": repr(self.info["channel_name"]),
            "video_ids": crop_ids(self.video_ids),
            "last_updated": repr(self.info.last_updated),
            "about_html": crop_html(self.info["about_html"]),
            "community_html": crop_html(self.info["community_html"]),
            "featured_channels_html": crop_html(
                self.info["featured_channels_html"]),
            "videos_html": crop_html(self.info["videos_html"]),
            "workers": repr(self.workers),
            "parent_dir": repr(self.target_dir)
        }
        chained = [f"{k}={v}" for k, v in prop_dict.items()]
        return f"Channel({', '.join(chained)})"

    def __str__(self) -> str:
        return (f"[{self.info['last_updated']}] {self.info['channel_name']} "
                f"({self.__len__()})")


    class check:

        @staticmethod
        def source(source: str, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `source` must "
                       f"be a string with one of the following values: "
                       f"{repr(AVAILABLE_SOURCES)}")
            if not isinstance(source, str):
                context = f"(received object of type: {type(source)})"
                raise TypeError(f"{err_msg} {context}")
            if source not in AVAILABLE_SOURCES:
                context = f"(received: {repr(source)})"
                raise ValueError(f"{err_msg} {context}")
            return source

        @staticmethod
        def channel_id(channel_id: str, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `channel_id` "
                       f"must be a unique 24-character channel id starting "
                       f"with 'UC', which is used by the YouTube backend to "
                       f"track channels")
            if not isinstance(channel_id, str):
                context = (f"(received object of type: {type(channel_id)})")
                raise TypeError(f"{err_msg} {context}")
            if len(channel_id) != 24 or not channel_id.startswith("UC"):
                context = (f"(received: {repr(channel_id)})")
                raise ValueError(f"{err_msg} {context}")
            return channel_id

        @staticmethod
        def channel_name(channel_name: str, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `channel_name` "
                       f"must be a non-empty string")
            if not isinstance(channel_name, str):
                context = f"(received object of type: {type(channel_name)})"
                raise TypeError(f"{err_msg} {context}")
            if not channel_name:  # channel_name is empty string
                context = f"(received: {repr(channel_name)})"
                raise ValueError(f"{err_msg} {context}")
            return channel_name

        @staticmethod
        def video_ids(video_ids: list[str] | tuple[str],
                      *objs,
                      stack_index: int = 2) -> list[str]:
            err_msg = (f"[{error_trace(*objs, stack_index=stack_index)}] "
                       f"`video_ids` must be a list or tuple of unique "
                       f"11-character video ids referencing the video "
                       f"contents of this channel")
            if not isinstance(video_ids, (list, tuple)):
                context = f"(received object of type: {type(video_ids)})"
                raise TypeError(f"{err_msg} {context}")
            for v_id in video_ids:
                Video.check.video_id(v_id, *objs, stack_index=stack_index + 1)
            return list(video_ids)

        @staticmethod
        def last_updated(last_updated: datetime, *objs) -> datetime:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `last_updated` "
                       f"must be a datetime.datetime object stating the last "
                       f"time this channel was checked for updates")
            if not isinstance(last_updated, datetime):
                context = f"(received object of type: {type(last_updated)})"
                raise TypeError(f"{err_msg} {context}")
            if last_updated > datetime.now():
                context = f"({last_updated} > {datetime.now()})"
                raise ValueError(f"{err_msg} {context}")
            return last_updated

        @staticmethod
        def about_html(about_html: str | None, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `about_html` "
                       f"must be a string containing the html response of the "
                       f"channel's 'About' page, or None if it does not have "
                       f"one")
            if about_html is not None:
                if not isinstance(about_html, str):
                    context = f"(received object of type: {type(about_html)})"
                    raise TypeError(f"{err_msg} {context}")
                return about_html
            return ""

        @staticmethod
        def community_html(community_html: str | None, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] "
                       f"`community_html` must be a string containing the "
                       f"html response of the channel's 'Community' page, or "
                       f"None if it does not have one")
            if community_html is not None:
                if not isinstance(community_html, str):
                    context = (f"(received object of type: "
                                f"{type(community_html)})")
                    raise TypeError(f"{err_msg} {context}")
                return community_html
            return ""

        @staticmethod
        def featured_channels_html(
            featured_channels_html: str | None, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] "
                       f"`featured_channels_html` must be a string containing "
                       f"the html response of the channel's 'Featured "
                       f"Channels' page, or None if it does not have one")
            if featured_channels_html is not None:
                if not isinstance(featured_channels_html, str):
                    context = (f"(received object of type: "
                                f"{type(featured_channels_html)})")
                    raise TypeError(f"{err_msg} {context}")
                return featured_channels_html
            return ""

        @staticmethod
        def videos_html(videos_html: str | None, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `videos_html` "
                       f"must be a string containing the html response of the "
                       f"channel's 'Videos' page, or None if it does not have "
                       f"one")
            if videos_html is not None:
                if not isinstance(videos_html, str):
                    context = f"(received object of type: {type(videos_html)})"
                    raise TypeError(f"{err_msg} {context}")
                return videos_html
            return ""

        @staticmethod
        def workers(workers: int | None, *objs) -> int:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `workers` must "
                       f"be an integer > 0, or None to use all available "
                       f"resources")
            if workers is not None:
                if not isinstance(workers, int):
                    context = f"(received object of type: {type(workers)})"
                    raise TypeError(f"{err_msg} {context}")
                if workers <= 0:
                    context = f"(received: {workers})"
                    raise ValueError(f"{err_msg} {context}")
            return workers

        @staticmethod
        def parent_dir(parent_dir: Path | None, *objs) -> Path:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `parent_dir` "
                       f"must be a Path-like object pointing to a directory "
                       f"on local storage to load/download content to, or "
                       f"None to use the default directory structure")
            if parent_dir is not None:
                if not isinstance(parent_dir, Path):
                    context = f"(received object of type: {type(parent_dir)})"
                    raise TypeError(f"{err_msg} {context}")
                if not parent_dir.is_dir():  # is_dir = False if does not exist
                    context = f"(directory does not exist: {parent_dir})"
                    raise ValueError(f"{err_msg} {context}")
                return parent_dir
            return VIDEO_DIR


class Video:

    def __init__(self,
                 source: str,
                 channel_id: str,
                 channel_name: str,
                 video_id: str,
                 video_title: str,
                 thumbnail_url: str,
                 publish_date: datetime,
                 last_updated: datetime,
                 duration: timedelta,
                 views: int,
                 rating: float | None = None,
                 description: str | None = None,
                 parent_dir: Path | None = None,
                 streams: pytube.StreamQuery | None = None,
                 captions: pytube.CaptionQuery | None = None):
        self.info = {
            "channel_id": self.check.channel_id(channel_id, self),
            "channel_name": self.check.channel_name(channel_name, self),
            "video_id": self.check.video_id(video_id, self),
            "video_title": self.check.video_title(video_title, self),
            "thumbnail_url": self.check.thumbnail_url(thumbnail_url, self),
            "publish_date": self.check.publish_date(publish_date, self),
            "last_updated": self.check.last_updated(last_updated, self),
            "duration": self.check.duration(duration, self),
            "views": self.check.views(views, self),
            "rating": self.check.rating(rating, self),
            "description": self.check.description(description, self)
        }
        self.source = self.check.source(source, self)
        self.streams = self.check.streams(streams, self)
        self.captions = self.check.captions(captions, self)
        self.target_dir = Path(self.check.parent_dir(parent_dir, self),
                               self.info["channel_id"], self.info["video_id"])

    @classmethod
    def from_local(cls,
                   channel_id: str,
                   video_id: str,
                   parent_dir: Path | None = None) -> Video:
        parent_dir = cls.check.parent_dir(parent_dir, cls)
        channel_id = cls.check.channel_id(channel_id, cls)
        video_id = cls.check.video_id(video_id, cls)
        video_path = Path(parent_dir, channel_id, video_id)
        info_path = Path(video_path, "info.json")
        if not video_path.exists() or not video_path.is_dir():
            err_msg = (f"[{error_trace(cls)}] video directory does not exist: "
                       f"{video_path}")
            raise ValueError(err_msg)
        if not info_path.exists():
            err_msg = (f"[{error_trace(cls)}] video directory has no "
                       f"info.json file: {video_path}")
            raise ValueError(err_msg)
        with info_path.open("r") as info_file:
            saved = json.load(info_file)
        return cls(source="local",
                   channel_id=saved["channel"]["id"],
                   channel_name=saved["channel"]["name"],
                   video_id=saved["id"],
                   video_title=saved["title"],
                   thumbnail_url=saved["thumbnail_url"],
                   publish_date=datetime.fromisoformat(saved["publish_date"]),
                   last_updated=datetime.fromisoformat(saved["fetched_at"]),
                   duration=timedelta(seconds=saved["length"]),
                   views=saved["views"],
                   rating=saved["rating"],
                   description=saved["description"],
                   parent_dir=parent_dir,
                   streams=None,
                   captions=None)

    @classmethod
    def from_pytube(cls,
                    video_id: str,
                    parent_dir: Path | None = None) -> Video:
        parent_dir = cls.check.parent_dir(parent_dir, cls)
        video_id = cls.check.video_id(video_id)
        video_url = video_id_to_url(video_id)
        try:
            online = pytube.YouTube(video_url)
            return cls(source="local",
                       channel_id=channel_url_to_id(online.channel_url),
                       channel_name=online.author,
                       video_id=video_id,
                       video_title=online.title,
                       thumbnail_url=online.thumbnail_url,
                       publish_date=online.publish_date,
                       last_updated=datetime.now(),
                       duration=timedelta(seconds=online.length),
                       views=online.views,
                       rating=online.rating,
                       description=online.description,
                       parent_dir=parent_dir,
                       streams=online.streams,
                       captions=online.captions)
        except (pytube.exceptions.AgeRestrictedError,
                pytube.exceptions.MembersOnly,
                pytube.exceptions.VideoPrivate,
                pytube.exceptions.VideoRegionBlocked) as exc:
            err_msg = f"[{error_trace(cls)}] Access denied: {video_url}"
            raise PermissionError(err_msg) from exc
        except (URLError, gaierror) as exc:
            err_msg = (f"[{error_trace(cls)}] Network error when fetching "
                       f"video response: {video_url}")
            raise ConnectionError(err_msg) from exc
        except (KeyError,
                pytube.exceptions.ExtractError,
                pytube.exceptions.HTMLParseError,
                pytube.exceptions.RegexMatchError) as exc:
            err_msg = (f"[{error_trace(cls)}] Pytube was unable to parse "
                       f"response for video: {video_url}")
            raise KeyError(err_msg) from exc
        except pytube.exceptions.LiveStreamError as exc:
            err_msg = f"[{error_trace(cls)}] Video is a livestream: {video_url}"
            raise NotImplementedError(err_msg) from exc
        except pytube.exceptions.VideoUnavailable as exc:
            err_msg = f"[{error_trace(cls)}] Video is unavailable: {video_url}"
            raise RuntimeError(err_msg) from exc


    def to_json(self, json_path: Path = None) -> dict[str, str]:
        pass


    class check:

        @staticmethod
        def source(source: str, *objs) -> str:
            return Channel.check.source(source, *objs)

        @staticmethod
        def channel_id(channel_id: str, *objs) -> str:
            return Channel.check.channel_id(channel_id, *objs)

        @staticmethod
        def channel_name(channel_name: str, *objs) -> str:
            return Channel.check.channel_name(channel_name, *objs)

        @staticmethod
        def video_id(video_id: str, *objs, stack_index: int = 2) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=stack_index)}] "
                       f"`video_id` must be a unique 11-character video id "
                       f"used by the YouTube backend to track videos")
            if not isinstance(video_id, str):
                context = f"(received object of type: {type(video_id)})"
                raise TypeError(f"{err_msg} {context}")
            if len(video_id) != 11:
                context = f"(received: {repr(video_id)})"
                raise ValueError(f"{err_msg} {context}")
            return video_id

        @staticmethod
        def video_title(video_title: str, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `video_title` "
                       f"must be a string")
            if not isinstance(video_title, str):
                context = f"(received object of type: {type(video_title)})"
                raise TypeError(f"{err_msg} {context}")
            return video_title

        @staticmethod
        def publish_date(publish_date: datetime, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `publish_date` "
                       f"must be a datetime object stating the last time this "
                       f"video was checked for updates")
            if not isinstance(publish_date, datetime):
                context = f"(received object of type: {type(publish_date)}"
                raise TypeError(f"{err_msg} {context}")
            if publish_date > datetime.now():
                context = f"('{str(publish_date)}' > '{str(datetime.now())}')"
                raise ValueError(f"{err_msg} {context}")
            return publish_date

        @staticmethod
        def last_updated(last_updated: datetime, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `last_updated` "
                       f"must be a datetime object stating the last time this "
                       f"video was checked for updates")
            if not isinstance(last_updated, datetime):
                context = f"(received object of type: {type(last_updated)}"
                raise TypeError(f"{err_msg} {context}")
            if last_updated > datetime.now():
                context = f"('{str(last_updated)}' > '{str(datetime.now())}')"
                raise ValueError(f"{err_msg} {context}")
            return last_updated

        @staticmethod
        def duration(duration: timedelta, *objs) -> timedelta:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `duration` "
                       f"must be a timedelta object describing the duration "
                       f"of the video")
            if not isinstance(duration, timedelta):
                context = f"(received object of type: {type(duration)})"
                raise TypeError(f"{err_msg} {context}")
            if duration < timedelta():
                context = f"({duration} < {timedelta()})"
                raise ValueError(f"{err_msg} {context}")
            return duration

        @staticmethod
        def views(views: int, *objs) -> int:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `views` must "
                       f"be an integer representing the number of views this "
                       f"video has received")
            if not isinstance(views, int):
                context = f"(received object of type: {type(views)})"
                raise TypeError(f"{err_msg} {context}")
            if views < 0:
                context = f"({views} < 0)"
                raise ValueError(f"{err_msg} {context}")
            return views

        @staticmethod
        def rating(rating: float | None, *objs) -> float | None:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `rating` must "
                       f"be a float describing the ratio of upvotes to "
                       f"upvotes + downvotes this video has received, "
                       f"multiplied by a factor of 5")
            if rating:
                if not isinstance(rating, float):
                    context = f"(received object of type: {type(rating)})"
                    raise TypeError(f"{err_msg} {context}")
                if rating < 0:
                    context = f"({rating} < 0)"
                    raise ValueError(f"{err_msg} {context}")
                if rating > 5:
                    context = f"({rating} > 5)"
                    raise ValueError(f"{err_msg} {context}")
            return rating

        @staticmethod
        def thumbnail_url(thumbnail_url: str, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `thumbnail_url` "
                       f"must be a url string pointing to the thumbnail image "
                       f"used for this video")
            if not isinstance(thumbnail_url, str):
                context = f"(received object of type: {type(thumbnail_url)})"
                raise TypeError(f"{err_msg} {context}")
            return thumbnail_url

        @staticmethod
        def description(description: str | None, *objs) -> str:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `description` "
                       f"must be a string containing the video's description "
                       f"or None if it does not have one")
            if description:
                if not isinstance(description, str):
                    context = f"(received object of type: {type(description)})"
                    raise TypeError(f"{err_msg} {context}")
                return description
            return ""

        @staticmethod
        def parent_dir(parent_dir: Path | None, *objs) -> Path:
            return Channel.check.parent_dir(parent_dir, *objs)

        @staticmethod
        def streams(streams: pytube.StreamQuery | None,
                    *objs) -> pytube.StreamQuery:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `streams` must "
                       f"be a pytube.StreamQuery object or None if the video "
                       f"has no streams")
            if streams:
                if not isinstance(streams, pytube.StreamQuery):
                    context = f"(received object of type: {type(streams)})"
                    raise TypeError(f"{err_msg} {context}")
                return streams
            return pytube.StreamQuery([])

        @staticmethod
        def captions(captions: pytube.CaptionQuery | None,
                     *objs) -> pytube.CaptionQuery:
            err_msg = (f"[{error_trace(*objs, stack_index=2)}] `captions` "
                       f"must be a pytube.CaptionQuery object or None if the "
                       f"video has no captions")
            if captions:
                if not isinstance(captions, pytube.CaptionQuery):
                    context = f"(received object of type: {type(captions)})"
                    raise TypeError(f"{err_msg} {context}")
                return captions
            return pytube.CaptionQuery([])
            
