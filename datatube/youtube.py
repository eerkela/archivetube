from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from functools import lru_cache
import json
from pathlib import Path
import re
from socket import gaierror
import subprocess
from typing import Iterator
from urllib.error import URLError

import pytube
from tqdm import tqdm
import validators

from datatube import DATATUBE_VERSION_NUMBER, VIDEO_DIR
from datatube.error import error_trace


"""
TODO: write an automatic retry method using expressvpn
"""


AVAILABLE_SOURCES = ("local", "pytube", "sql")


def is_channel_id(string: str) -> bool:
    return len(string) == 24 and string.startswith("UC")


def is_readable(path: Path) -> bool:
    return path.is_dir() and len(path.glob("info.json")) > 0


def is_url(string: str) -> bool:
    result = validators.url(string)
    if isinstance(result, validators.ValidationFailure):
        return False
    return True


def is_video_id(string: str) -> bool:
    return len(string) == 11


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
                 last_updated: datetime,
                 video_ids: dict[str, str | Path],
                 target_dir: Path,
                 about_html: str = "",
                 community_html: str = "",
                 featured_channels_html: str = "",
                 videos_html: str = "",
                 workers: int | None = 1):
        self.source = source
        self.id = channel_id
        self.name = channel_name
        self.last_updated = last_updated
        self.html = {
            "about": about_html,
            "community": community_html,
            "featured_channels": featured_channels_html,
            "videos": videos_html
        }
        self.video_ids = video_ids
        self.target_dir = target_dir
        self.workers = workers

    #############################
    ####    CLASS METHODS    ####
    #############################

    @classmethod
    @lru_cache(maxsize=32)
    def from_local(cls, channel_path: Path) -> Channel:
        if not isinstance(channel_path, Path):
            err_msg = (f"[{error_trace(cls)}] `channel_path` must be a "
                       f"Path-like object (received object of type: "
                       f"{type(channel_path)})")
            raise TypeError(err_msg)
        if not is_readable(channel_path):
            err_msg = (f"[{error_trace(cls)}] `channel_path` either does not "
                       f"exist, is not a directory, or has no info.json file: "
                       f"{channel_path}")
            raise ValueError(err_msg)
        with Path(channel_path, "info.json").open("r") as info_file:
            saved = json.load(info_file)
        dir_contents = tqdm(channel_path.iterdir(), leave=False)
        video_ids = {d.name: d for d in dir_contents if is_readable(d)}
        return cls(source="local",
                   channel_id=saved["id"],
                   channel_name=saved["name"],
                   last_updated=datetime.fromisoformat(saved["fetched_at"]),
                   video_ids=video_ids,
                   target_dir=channel_path,
                   about_html=saved["about_html"],
                   community_html=saved["community_html"],
                   featured_channels_html=saved["featured_channels_html"],
                   videos_html=saved["videos_html"])

    @classmethod
    @lru_cache(maxsize=32)
    def from_pytube(cls, channel_url: str) -> Channel:
        if not isinstance(channel_url, str):
            err_msg = (f"[{error_trace(cls)}] `channel_url` must be a string "
                       f"(received object of type: {type(channel_url)})")
            raise TypeError(err_msg)
        channel_url = channel_url.strip()
        if not is_url(channel_url):
            err_msg = (f"[{error_trace(cls)}] `channel_url` must be a valid "
                       f"url (received: {repr(channel_url)})")
            raise ValueError(err_msg)
        try:
            online = pytube.Channel(channel_url)
            channel_contents = tqdm(online.url_generator(), leave=False)
            video_ids = [video_url_to_id(url) for url in channel_contents]
            return cls(source="pytube",
                       channel_id=online.channel_id,
                       channel_name=online.channel_name,
                       last_updated=datetime.now(),
                       video_ids=video_ids,
                       target_dir=Path(VIDEO_DIR, online.channel_id),
                       about_html=online.about_html,
                       community_html=online.community_html,
                       featured_channels_html=online.featured_channels_html,
                       videos_html=online.html)
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

    ##########################
    ####    PROPERTIES    ####
    ##########################

    @property
    def html(self) -> dict[str, str]:
        return self._html

    @html.setter
    def html(self, new_html_dict: dict[str, str]) -> None:
        result = {
            "about": "",
            "community": "",
            "featured_channels": "",
            "videos": ""
        }
        err_msg = (f"[{error_trace(self)}] `html` must be a registry of raw "
                   f"html response strings for the current channel")
        for k, v in new_html_dict.items():
            if not isinstance(k, str):
                context = f"(received key of type: {type(k)})"
                raise TypeError(f"{err_msg} {context}")
            if not isinstance(v, str):
                context = (f"(received value of type: {type(v)} for key: "
                           f"{repr(k)})")
                raise TypeError(f"{err_msg} {context}")
            result[k] = v
        self._html = result

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, new_id: str) -> None:
        if hasattr(self, "_id"):
            err_msg = (f"[{error_trace(self)}] `id` cannot be changed outside "
                       f"of init")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `id` must be a unique 24-character "
                   f"ExternalId starting with 'UC', which is used by the "
                   f"YouTube backend to track channels")
        if not isinstance(new_id, str):
            context = (f"(received object of type: {type(new_id)})")
            raise TypeError(f"{err_msg} {context}")
        if len(new_id) != 24 or not new_id.startswith("UC"):
            context = (f"(received: {repr(new_id)})")
            raise ValueError(f"{err_msg} {context}")
        self._id = new_id

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    @last_updated.setter
    def last_updated(self, new_timestamp: datetime) -> None:
        if hasattr(self, "_last_updated"):
            err_msg = (f"[{error_trace(self)}] `last_updated` cannot be "
                       f"changed outside of init")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"channel was checked for updates")
        if not isinstance(new_timestamp, datetime):
            context = f"(received object of type: {type(new_timestamp)})"
            raise TypeError(f"{err_msg} {context}")
        if new_timestamp > datetime.now():
            context = f"({new_timestamp} > {datetime.now()})"
            raise ValueError(f"{err_msg} {context}")
        self._last_updated = new_timestamp

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, new_name: str) -> None:
        err_msg = f"[{error_trace(self)}] `name` must be a non-empty string"
        if not isinstance(new_name, str):
            context = f"(received object of type: {type(new_name)})"
            raise TypeError(f"{err_msg} {context}")
        if not new_name:  # channel_name is empty string
            context = f"(received: {repr(new_name)})"
            raise ValueError(f"{err_msg} {context}")
        self._name = new_name

    @property
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, new_source: str) -> None:
        if hasattr(self, "_source"):
            err_msg = (f"[{error_trace(self)}] `source` cannot be changed "
                       f"outside of init.  Construct a new Channel object "
                       f"instead")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `source` must be a string with one "
                   f"of the following values: {repr(AVAILABLE_SOURCES)}")
        if not isinstance(new_source, str):
            context = f"(received object of type: {type(new_source)})"
            raise TypeError(f"{err_msg} {context}")
        if new_source not in AVAILABLE_SOURCES:
            context = f"(received: {repr(new_source)})"
            raise ValueError(f"{err_msg} {context}")
        self._source = new_source

    @property
    def target_dir(self) -> Path:
        return self._target_dir

    @target_dir.setter
    def target_dir(self, new_dir: Path) -> None:
        err_msg = (f"[{error_trace(self)}] `target_dir` must be a Path-like "
                   f"object pointing to a directory on local storage in which "
                   f"to store the contents of this channel")
        if not isinstance(new_dir, Path):
            context = f"(received object of type: {type(new_dir)})"
            raise TypeError(f"{err_msg} {context}")
        if new_dir.exists() and not new_dir.is_dir():
            context = f"(path points to file: {new_dir})"
            raise ValueError(f"{err_msg} {context}")
        self._target_dir = new_dir

    @property
    def video_ids(self) -> list[str | Path]:
        return self._video_ids

    @video_ids.setter
    def video_ids(self, new_ids: list[str] | tuple[str] | set[str]) -> None:
        err_msg = (f"[{error_trace(self)}] `video_ids` must be a list, tuple, "
                   f"or set of 11-character video ids used by the YouTube "
                   f"backend to track videos")
        if not isinstance(new_ids, (list, tuple, set)):
            context = f"(received object of type: {type(new_ids)})"
            raise TypeError(f"{err_msg} {context}")
        for video_id in new_ids:
            if not isinstance(video_id, str):
                context = f"(received id of type: {type(video_id)})"
                raise TypeError(f"{err_msg} {context}")
            if not is_video_id(video_id):
                context = f"(encountered malformed video id: {repr(video_id)})"
                raise ValueError(f"{err_msg} {context}")
        self._video_ids = new_ids

    @property
    def workers(self) -> int:
        return self._workers

    @workers.setter
    def workers(self, new_workers: int) -> None:
        err_msg = (f"[{error_trace(self)}] `workers` must be an integer > 0 "
                   f"or None to use all available resources")
        if new_workers is not None:
            if not isinstance(new_workers, int):
                context = f"(received object of type: {type(new_workers)})"
                raise TypeError(f"{err_msg} {context}")
            if new_workers <= 0:
                context = f"(received: {new_workers})"
                raise ValueError(f"{err_msg} {context}")
        self._workers = new_workers

    #######################
    ####    METHODS    ####
    #######################

    def download(
        self,
        to: Path | None = None,
        date_range: tuple[datetime | None, datetime | None] = (None, None),
        **kwargs
    ) -> None:
        def in_date_range(video: Video) -> bool:
            min_date, max_date = date_range
            if min_date is not None and max_date is not None:
                return min_date <= video.publish_date <= max_date
            if min_date is not None:
                return min_date <= video.publish_date
            if max_date is not None:
                return video.publish_date <= max_date
            return True

        def dispatch(video, executor=None):
            if executor is None:
                return video.download(**kwargs)
            return executor.submit(video.download, **kwargs)

        if to is not None:
            self.target_dir = to
        if self.workers is not None and self.workers == 1:
            for video in self.__iter__():
                if in_date_range(video):
                    dispatch(video)
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                try:
                    futures = []
                    for video in self.__iter__():
                        if in_date_range(video):
                            futures.append(dispatch(video))
                except (KeyboardInterrupt, SystemExit) as exc:
                    print("Received kill signal.  Shutting down threads...")
                    executor.shutdown(cancel_futures=True)
                    raise exc

    def to_json(self, json_path: Path | None = None) -> dict[str, str]:
        result = {
            "datatube_version": DATATUBE_VERSION_NUMBER,
            "channel_id": self.id,
            "channel_name": self.name,
            "last_updated": self.last_updated.isoformat(),
            "html": self.html
        }
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

    ####################################
    ####    DUNDER/MAGIC METHODS    ####
    ####################################

    def __contains__(self, video: Video | str) -> bool:
        if isinstance(video, str):
            return video in self.video_ids
        return video.id in self.video_ids

    def __eq__(self, other: Channel) -> bool:
        return self.id == other.id and self.last_updated == other.last_updated

    def __hash__(self) -> int:
        return hash(id(self))

    def __iter__(self) -> Iterator[Video]:
        # define dispatch functions
        if self.source == "local":
            def dispatch(video_id, executor=None):
                path = Path(self.target_dir, video_id)
                if executor is None:
                    return Video.from_local(path, channel=self)
                return executor.submit(Video.from_local, path, channel=self)
        elif self.source == "pytube":
            def dispatch(video_id, executor=None):
                url = video_id_to_url(video_id)
                if executor is None:
                    return Video.from_pytube(url, channel=self)
                return executor.submit(Video.from_pytube, url, channel=self)
        elif self.source == "sql":
            def dispatch(video_id, executor=None):
                if executor is None:
                    return Video.from_sql(video_id, channel=self)
                return executor.submit(Video.from_sql, video_id, channel=self)

        # perform iteration
        if self.workers is not None and self.workers == 1:
            for v_id in self.video_ids:
                try:
                    yield dispatch(v_id)
                except (KeyboardInterrupt, SystemExit):
                    raise
                except Exception as exc:
                    print(exc)
                    continue
        else:
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                try:
                    fs = [dispatch(v_id, executor) for v_id in self.video_ids]
                    for future in as_completed(fs):
                        exc = future.exception()
                        if exc is not None:
                            print(exc)
                            continue
                        yield future.result()
                except (KeyboardInterrupt, SystemExit) as exc:
                    print("Received kill signal.  Shutting down threads...")
                    executor.shutdown(cancel_futures=True)
                    raise exc

    def __len__(self) -> int:
        return len(self.video_ids)

    def __repr__(self) -> str:
        def crop_contents(id_list: list[str], threshold: int = 5) -> str:
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
            "channel_id": repr(self.id),
            "channel_name": repr(self.name),
            "last_updated": repr(self.last_updated),
            "video_ids": crop_contents(self.video_ids),
            "target_dir": repr(self.target_dir),
            "about_html": crop_html(self.html["about"]),
            "community_html": crop_html(self.html["community"]),
            "featured_channels_html": crop_html(self.html["featured_channels"]),
            "videos_html": crop_html(self.html["videos"]),
            "workers": repr(self.workers)
        }
        formatted = [f"{k}={v}" for k, v in prop_dict.items()]
        return f"Channel({', '.join(formatted)})"

    def __str__(self) -> str:
        return f"[{self.last_updated}] {self.name} ({self.__len__()})"


class Video:

    def __init__(self,
                 source: str,
                 video_id: str,
                 video_title: str,
                 publish_date: datetime,
                 last_updated: datetime,
                 duration: timedelta,
                 views: int,
                 rating: float | None = None,
                 likes: int | None = None,
                 dislikes: int | None = None,
                 description: str | None = None,
                 keywords: list[str] = [],
                 thumbnail_url: str | None = None,
                 target_dir: Path | None = None,
                 streams: pytube.StreamQuery | None = None,
                 captions: pytube.CaptionQuery | None = None,
                 channel: Channel | None = None):
        self.source = source
        self.id = video_id
        self.title = video_title
        self.publish_date = publish_date
        self.last_updated = last_updated
        self.duration = duration
        stats_dict = {
            "views": views,
            "rating": rating,
            "likes": likes,
            "dislikes": dislikes
        }
        self.stats = {k: v for k, v in stats_dict.items() if v is not None}
        self.description = description
        self.keywords = keywords
        self.thumbnail_url = thumbnail_url
        self.channel = channel
        self.streams = streams
        self.captions = captions
        if target_dir is not None:
            self.target_dir = target_dir
        elif self.channel is not None:
            self.target_dir = Path(self.channel.target_dir, self.id)
        else:
            self._target_dir = None  # naked pytube video

    #############################
    ####    CLASS METHODS    ####
    #############################

    @classmethod
    @lru_cache(maxsize=256)
    def from_local(cls,
                   video_path: Path,
                   channel: Channel | None = None) -> Video:
        if not isinstance(video_path, Path):
            err_msg = (f"[{error_trace(cls)}] `video_path` must be a "
                       f"Path-like object pointing to a video directory on "
                       f"local storage (received object of type: "
                       f"{type(video_path)})")
            raise TypeError(err_msg)
        if not is_readable(video_path):
            err_msg = (f"[{error_trace(cls)}] `video_path` is not readable "
                       f"(does not exist, is not a directory, or has no "
                       f"info.json file): {video_path}")
            raise ValueError(err_msg)
        if channel is not None and not isinstance(channel, Channel):
            err_msg = (f"[{error_trace(cls)}] `channel` must be an instance "
                       f"of Channel (received object of type: {type(channel)})")
            raise TypeError(err_msg)
        with Path(video_path, "info.json").open("r") as info_file:
            saved = json.load(info_file)
        result = cls(source="local",
                     video_id=saved["id"],
                     video_title=saved["title"],
                     publish_date=datetime.fromisoformat(saved["publish_date"]),
                     last_updated=datetime.fromisoformat(saved["fetched_at"]),
                     duration=timedelta(seconds=saved["length"]),
                     views=saved["views"],
                     rating=saved["rating"],
                     likes=None,
                     dislikes=None,
                     description=saved["description"],
                     keywords=saved["keywords"],
                     thumbnail_url=saved["thumbnail_url"],
                     target_dir=video_path,
                     streams=None,
                     captions=None,
                     channel=channel)
        if channel is not None and result not in channel:
            err_msg = (f"[{error_trace(cls)}] video is not contained in "
                       f"specified channel: {result.id}")
            raise ValueError(err_msg)
        return result

    @classmethod
    @lru_cache(maxsize=256)
    def from_pytube(cls,
                    video_url: str,
                    channel: Channel | None = None) -> Video:
        if not isinstance(video_url, str):
            err_msg = (f"[{error_trace(cls)}] `video_url` must be a url "
                       f"string (received object of type: {type(video_url)})")
            raise TypeError(err_msg)
        if not is_url(video_url):
            err_msg = (f"[{error_trace(cls)}] `video_url` is not a valid url "
                       f"(received: {repr(video_url)})")
            raise ValueError(err_msg)
        if channel is not None and not isinstance(channel, Channel):
            err_msg = (f"[{error_trace(cls)}] `channel` must be an instance "
                       f"of Channel (received object of type: {type(channel)})")
            raise TypeError(err_msg)
        try:
            yt = pytube.YouTube(video_url)
            video_id = video_url_to_id(video_url)
            if channel is not None:
                target_dir = Path(channel.target_dir, video_id)
            else:
                target_dir = Path(VIDEO_DIR, yt.channel_id, video_id)
            result = cls(source="pytube",
                         video_id=video_id,
                         video_title=yt.title,
                         publish_date=yt.publish_date,
                         last_updated=datetime.now(),
                         duration=timedelta(seconds=yt.length),
                         views=yt.views,
                         rating=yt.rating,
                         likes=None,
                         dislikes=None,
                         description=yt.description,
                         keywords=yt.keywords,
                         thumbnail_url=yt.thumbnail_url,
                         target_dir=target_dir,
                         streams=yt.streams,
                         captions=yt.captions,
                         channel=channel)
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
        else:
            if channel is not None and result not in channel:
                err_msg = (f"[{error_trace(cls)}] video is not contained in "
                           f"specified channel: {result.id}")
                raise ValueError(err_msg)
            return result

    ##########################
    ####    PROPERTIES    ####
    ##########################

    @property
    def captions(self) -> pytube.CaptionQuery:
        return self._captions

    @captions.setter
    def captions(self, new_captions: pytube.CaptionQuery | None) -> None:
        if hasattr(self, "_captions"):
            err_msg = (f"[{error_trace(self)}] `captions` cannot be changed "
                       f"outside of init")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `captions` must be a "
                   f"pytube.CaptionQuery object or None if the video has no "
                   f"captions")
        if new_captions is not None:
            if not isinstance(new_captions, pytube.CaptionQuery):
                context = f"(received object of type: {type(new_captions)})"
                raise TypeError(f"{err_msg} {context}")
            self._captions = new_captions
        else:
            self._captions = pytube.CaptionQuery([])

    @property
    def channel(self) -> Channel:
        return self._channel

    @channel.setter
    def channel(self, new_channel: Channel | None) -> None:
        err_msg = (f"[{error_trace(self)}] `channel` must be a Channel object "
                   f"pointing to the owner of this video")
        if new_channel is not None:
            if not isinstance(new_channel, Channel):
                context = f"(received object of type: {type(new_channel)})"
                raise TypeError(f"{err_msg} {context}")
            if self.id not in new_channel.video_ids:
                if len(new_channel.video_ids) > 5:
                    cropped = "', '".join(new_channel.video_ids[:5])
                    context = (f"(channel does not own this video: "
                               f"{repr(self.id)} not in ['{cropped}', ...])")
                else:
                    context = (f"(channel does not own this video: "
                               f"{repr(self.id)} not in "
                               f"{repr(new_channel.video_ids)})")
                raise ValueError(f"{err_msg} {context}")
        self._channel = new_channel

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, new_description: str) -> None:
        err_msg = (f"[{error_trace(self)}] `description` must be a string "
                   f"containing the video's description")
        if not isinstance(new_description, str):
            context = f"(received object of type: {type(new_description)})"
            raise TypeError(f"{err_msg} {context}")
        self._description = new_description

    @property
    def duration(self) -> timedelta:
        return self._duration

    @duration.setter
    def duration(self, new_duration: timedelta) -> None:
        err_msg = (f"[{error_trace(self)}] `duration` must be a "
                   f"datetime.timedelta object describing the duration of the "
                   f"video")
        if not isinstance(new_duration, timedelta):
            context = f"(received object of type: {type(new_duration)})"
            raise TypeError(f"{err_msg} {context}")
        if new_duration < timedelta():
            context = f"({new_duration} < {timedelta()})"
            raise ValueError(f"{err_msg} {context}")
        self._duration = new_duration

    @property
    def id(self) -> str:
        return self._id

    @id.setter
    def id(self, new_id: str) -> None:
        if hasattr(self, "_id"):
            err_msg = (f"[{error_trace(self)}] `id` cannot be changed outside "
                       f"of init")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `id` must be a unique 11-character "
                   f"id string used by the YouTube backend to track videos")
        if not isinstance(new_id, str):
            context = f"(received object of type: {type(new_id)})"
            raise TypeError(f"{err_msg} {context}")
        if len(new_id) != 11:
            context = f"(received: {repr(new_id)})"
            raise ValueError(f"{err_msg} {context}")
        self._id = new_id

    @property
    def keywords(self) -> list[str]:
        return self._keywords

    @keywords.setter
    def keywords(self, new_keywords: list[str] | tuple[str] | set[str]) -> None:
        err_msg = (f"[{error_trace(self)}] `keywords` must be a list, tuple, "
                   f"or set of keyword strings associated with this video")
        if not isinstance(new_keywords, (list, tuple, set)):
            context = f"(received object of type: {type(new_keywords)})"
            raise TypeError(f"{err_msg} {context}")
        for keyword in new_keywords:
            if not isinstance(keyword, str):
                context = f"(received keyword of type: {type(keyword)})"
                raise TypeError(f"{err_msg} {context}")
            if not keyword:  # keyword is empty string
                context = f"(received empty keyword: {repr(keyword)})"
                raise ValueError(f"{err_msg} {context}")
        self._keywords = new_keywords

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    @last_updated.setter
    def last_updated(self, new_date: datetime) -> None:
        if hasattr(self, "_last_updated"):
            err_msg = (f"[{error_trace(self)}] `last_updated` cannot be "
                       f"changed outside of init")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"video was checked for updates")
        if not isinstance(new_date, datetime):
            context = f"(received object of type: {type(new_date)})"
            raise TypeError(f"{err_msg} {context}")
        if new_date > datetime.now():
            context = f"({str(new_date)} > {str(datetime.now())})"
            raise ValueError(f"{err_msg} {context}")
        self._last_updated = new_date

    @property
    def publish_date(self) -> str:
        return self._publish_date

    @publish_date.setter
    def publish_date(self, new_date: datetime) -> None:
        err_msg = (f"[{error_trace(self)}] `publish_date` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"video was checked for updates")
        if not isinstance(new_date, datetime):
            context = f"(received object of type: {type(new_date)})"
            raise TypeError(f"{err_msg} {context}")
        if new_date > datetime.now():
            context = f"({str(new_date)} > {str(datetime.now())})"
            raise ValueError(f"{err_msg} {context}")
        self._publish_date = new_date

    @property
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, new_source: str) -> None:
        if hasattr(self, "_source"):
            err_msg = (f"[{error_trace(self)}] `source` cannot be changed "
                       f"outside of init.  Construct a new Video object "
                       f"instead")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `source` must be a string with one "
                   f"of the following values: {repr(AVAILABLE_SOURCES)}")
        if not isinstance(new_source, str):
            context = f"(received object of type: {type(new_source)})"
            raise TypeError(f"{err_msg} {context}")
        if new_source not in AVAILABLE_SOURCES:
            context = f"(received: {repr(new_source)})"
            raise ValueError(f"{err_msg} {context}")
        if hasattr(self, "_source"):
            old_source = getattr(self, "_source")
            self._source = new_source
            if self._source != old_source:
                # TODO: update video information
                raise NotImplementedError()
        else:
            self._source = new_source

    @property
    def stats(self) -> dict[str, int | float]:
        return self._stats

    @stats.setter
    def stats(self, new_stats: dict[str, int | float]) -> None:
        err_msg = (f"[{error_trace(self)}] `stats` must be a dictionary "
                   f"containing the view and rating statistics of the video")
        if not isinstance(new_stats, dict):
            context = f"(received object of type: {type(new_stats)})"
            raise TypeError(f"{err_msg} {context}")
        # if ("rating" not in new_stats and
        #     ("likes" not in new_stats or "dislikes" not in new_stats)):
        #     context = ("(not enough information to compute rating: no "
        #                "'rating' entry and no 'likes' and 'dislikes' to "
        #                "compute it)")
        #     raise ValueError(f"{err_msg} {context}")
        for k, v in new_stats.items():
            if not isinstance(k, str):
                context = f"(received non-string key of type: {type(k)})"
                raise TypeError(f"{err_msg} {context}")
            if k not in {"views", "rating", "likes", "dislikes"}:
                context = f"(received unexpected key: {repr(k)})"
                raise ValueError(f"{err_msg} {context}")
            if k == "rating":
                if not isinstance(v, (int, float)):
                    context = (f"('rating' must be an integer or float, "
                               f"received object of type: {type(v)})")
                    raise TypeError(f"{err_msg} {context}")
                if not 0 <= v <= 5:
                    context = (f"('rating' must be between 0 and 5, received: "
                               f"{v})")
                    raise ValueError(f"{err_msg} {context}")
            elif k in ["views", "likes", "dislikes"]:
                if not isinstance(v, int):
                    context = (f"({repr(k)} must be an integer, received "
                               f"object of type: {type(v)})")
                    raise TypeError(f"{err_msg} {context}")
                if v < 0:
                    context = f"({repr(k)} must be >= 0, received: {v})"
                    raise ValueError(f"{err_msg} {context}")
        if ("rating" not in new_stats and
            ("likes" in new_stats and "dislikes" in new_stats)):
            likes = new_stats["likes"]
            dislikes = new_stats["dislikes"]
            new_stats["rating"] = 5 * likes / (likes + dislikes)
        self._stats = new_stats

    @property
    def streams(self) -> pytube.StreamQuery:
        return self._streams

    @streams.setter
    def streams(self, new_streams: pytube.StreamQuery | None) -> None:
        if hasattr(self, "_streams"):
            err_msg = (f"[{error_trace(self)}] `streams` cannot be changed "
                       f"outside of init")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace(self)}] `streams` must be a "
                   f"pytube.StreamQuery object or None if the video has no "
                   f"streams")
        if new_streams is not None:
            if not isinstance(new_streams, pytube.StreamQuery):
                context = f"(received object of type: {type(new_streams)})"
                raise TypeError(f"{err_msg} {context}")
            self._streams = new_streams
        else:
            self._streams = pytube.StreamQuery([])

    @property
    def target_dir(self) -> Path:
        return self._target_dir

    @target_dir.setter
    def target_dir(self, new_dir: Path) -> None:
        err_msg = (f"[{error_trace(self)}] `target_dir` must be a Path-like "
                   f"object pointing to a directory on local storage in which "
                   f"to store the contents of this video")
        if not isinstance(new_dir, Path):
            context = f"(received object of type: {type(new_dir)})"
            raise TypeError(f"{err_msg} {context}")
        if new_dir.exists() and new_dir.is_file():
            context = f"(path points to file: {new_dir})"
            raise ValueError(f"{err_msg} {context}")
        self._target_dir = new_dir

    @property
    def thumbnail_url(self) -> str:
        return self._thumbnail_url

    @thumbnail_url.setter
    def thumbnail_url(self, new_url: str) -> str:
        err_msg = (f"[{error_trace(self)}] `thumbnail_url` must be a url "
                   f"string pointing to the thumbnail image used for this "
                   f"video")
        if not isinstance(new_url, str):
            context = f"(received object of type: {type(new_url)})"
            raise TypeError(f"{err_msg} {context}")
        self._thumbnail_url = new_url

    @property
    def title(self) -> str:
        return self._title

    @title.setter
    def title(self, new_title: str) -> None:
        err_msg = (f"[{error_trace(self)}] `title` must be a non-empty string")
        if not isinstance(new_title, str):
            context = f"(received object of type: {type(new_title)})"
            raise TypeError(f"{err_msg} {context}")
        if not new_title:  # new_title is empty string
            context = f"(received: {repr(new_title)})"
            raise ValueError(f"{err_msg} {context}")
        self._title = new_title

    #######################
    ####    METHODS    ####
    #######################

    def download(self,
                 to: Path | None = None,
                 quality: str | None = None,
                 verbose: bool = True,
                 timeout: int = 10,
                 max_retries: int = 10,
                 keep_separate: bool = False,
                 caption_language: str = "en",
                 dry_run: bool = False):
        if self.source in ["local", "sql"]:
            err_msg = (f"[{error_trace(self)}] cannot download a local or "
                       f"sql-based video object: {repr(self.id)}")
            raise RuntimeError(err_msg)
        if len(self.streams) == 0:
            err_msg = (f"[{error_trace(self)}] video has no available streams "
                       f"to download: {repr(self.id)}")
            raise RuntimeError(err_msg)
        if self.target_dir is None and to is None:
            err_msg = (f"[{error_trace(self)}] no target directory to "
                       f"download to (`self.target_dir` and `to` are both "
                       f"None): {repr(self.id)}")
            raise RuntimeError(err_msg)
        if to is not None:
            self.target_dir = to

        if verbose:
            print(f"[{self.publish_date.date()}] {self.title}")
        self.target_dir.mkdir(parents=True, exist_ok=True)
        self.to_json(Path(self.target_dir, "info.json"))
        self.stats.to_csv(Path(self.target_dir, "stats.csv"))
        audio_path = Path(self.target_dir, f"[audio] {self.id}.mp4")
        video_path = Path(self.target_dir, f"[video] {self.id}.mp4")
        captions_path = Path(self.target_dir,
                             f"[captions] ({caption_language}) {self.id}.srt")

        if not dry_run and not self.is_downloaded():
            self.streams.filter(adaptive=True, mime_type="video/mp4") \
                        .order_by("resolution") \
                        .desc() \
                        .first() \
                        .download(output_path=video_path.parent,
                                  filename=video_path.name,
                                  timeout=timeout,
                                  max_retries=max_retries)
            self.streams.filter(adaptive=True, mime_type="audio/mp4") \
                        .order_by("abr") \
                        .desc() \
                        .first() \
                        .download(output_path=audio_path.parent,
                                  filename=audio_path.name,
                                  timeout=timeout,
                                  max_retries=max_retries)
            caption_track = self.captions.get_by_language_code(caption_language)
            if caption_track is not None:
                caption_track.download(output_path=captions_path.parent,
                                       title=captions_path.name,
                                       srt=True)

    def is_downloaded(self, tolerance: int | float = 1):
        def duration(path):
            cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration',
                   '-of', 'default=noprint_wrappers=1:nokey=1', str(path)]
            result = subprocess.run(cmd,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    check=True)
            return timedelta(seconds=float(result.stdout))

        audio_path = Path(self.target_dir, f"[audio] {self.id}.mp4")
        video_path = Path(self.target_dir, f"[video] {self.id}.mp4")
        if any(not p.exists() for p in [audio_path, video_path]):
            return False
        audio_duration = duration(audio_path)
        video_duration = duration(video_path)
        min_diff = timedelta(seconds=tolerance)
        return (abs(audio_duration - self.duration) < min_diff and
                abs(video_duration - self.duration) < min_diff)

    def to_json(self, json_path: Path = None) -> dict[str, str]:
        result = {
            "datatube_version": DATATUBE_VERSION_NUMBER,
            "video_id": self.id,
            "video_title": self.title,
            "publish_date": self.publish_date.isoformat(),
            "last_updated": self.last_updated.isoformat(),
            "duration": self.duration.total_seconds(),
            "stats": self.stats,
            "description": self.description,
            "keywords": self.keywords,
            "thumbnail_url": self.thumbnail_url,
        }
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

    ####################################
    ####    DUNDER/MAGIC METHODS    ####
    ####################################

    def __eq__(self, other: Video) -> bool:
        return self.id == other.id and self.last_updated == other.last_updated
