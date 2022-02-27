from __future__ import annotations
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
import json
from pathlib import Path
import re
from socket import gaierror
from typing import Iterator, Type
from urllib.error import URLError

import pytube
from tqdm import tqdm

from archivetube import VIDEO_DIR, error_trace


"""
TODO: move checks into getter/setter properties for more pythonic approach
TODO: write an automatic retry method using expressvpn
"""



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
                 last_updated: datetime,
                 video_ids: list[str] | tuple[str] | set[str],
                 about_html: str = "",
                 community_html: str = "",
                 featured_channels_html: str = "",
                 videos_html: str = "",
                 workers: int | None = 1,
                 target_dir: Path | None = None):
        self.source = source
        self.id = channel_id
        self.name = channel_name
        self.last_updated = last_updated
        self.video_ids = video_ids
        self.html = {
            "about": about_html,
            "community": community_html,
            "featured_channels": featured_channels_html,
            "videos": videos_html
        }
        self.workers = workers
        if target_dir is not None:
            self.target_dir = target_dir
        else:
            self.target_dir = Path(VIDEO_DIR, self.id)

    #############################
    ####    CLASS METHODS    ####
    #############################

    @classmethod
    def from_local(cls,
                   channel_path: Path,
                   progress_bar: bool = True) -> Channel:
        channel_id = channel_path.name
        info_path = Path(channel_path, "info.json")
        if not channel_path.exists():
            err_msg = (f"[{error_trace(cls)}] Channel directory does not "
                       f"exist: {channel_path}")
            raise ValueError(err_msg)
        if not channel_path.is_dir():
            err_msg = (f"[{error_trace(cls)}] Channel directory is not a "
                       f"directory: {channel_path}")
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
                   video_ids=video_ids,
                   about_html=saved["about_html"],
                   community_html=saved["community_html"],
                   featured_channels_html=saved["featured_channels_html"],
                   videos_html=saved["videos_html"],
                   target_dir=channel_path)

    @classmethod
    def from_pytube(cls,
                    channel_url: str,
                    target_dir: Path | None = None,
                    progress_bar: bool = True) -> Channel:
        try:
            online = pytube.Channel(channel_url)
            if progress_bar:
                channel_contents = tqdm(online.url_generator(), leave=False)
            else:
                channel_contents = online.url_generator()
            video_ids = [video_url_to_id(url) for url in channel_contents]
            return cls(source="pytube",
                       channel_id=online.channel_id,
                       channel_name=online.channel_name,
                       last_updated=datetime.now(),
                       about_html=online.about_html,
                       community_html=online.community_html,
                       featured_channels_html=online.featured_channels_html,
                       videos_html=online.html,
                       video_ids=video_ids,
                       target_dir=target_dir)
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
        return self._channel_id

    @id.setter
    def id(self, new_id: str) -> None:
        err_msg = (f"[{error_trace(self)}] `id` must be a unique 24-character "
                   f"ExternalId starting with 'UC', which is used by the "
                   f"YouTube backend to track channels")
        if not isinstance(new_id, str):
            context = (f"(received object of type: {type(new_id)})")
            raise TypeError(f"{err_msg} {context}")
        if len(new_id) != 24 or not new_id.startswith("UC"):
            context = (f"(received: {repr(new_id)})")
            raise ValueError(f"{err_msg} {context}")
        self._channel_id = new_id

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    @last_updated.setter
    def last_updated(self, new_timestamp: datetime) -> None:
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
        return self._channel_name

    @name.setter
    def name(self, new_name: str) -> None:
        err_msg = f"[{error_trace(self)}] `name` must be a non-empty string"
        if not isinstance(new_name, str):
            context = f"(received object of type: {type(new_name)})"
            raise TypeError(f"{err_msg} {context}")
        if not new_name:  # channel_name is empty string
            context = f"(received: {repr(new_name)})"
            raise ValueError(f"{err_msg} {context}")
        self._channel_name = new_name

    @property
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, new_source: str) -> None:
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
                # TODO: update channel information
                raise NotImplementedError()
        else:
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
    def video_ids(self) -> list[str]:
        return self._video_ids

    @video_ids.setter
    def video_ids(self, new_ids: list[str] | tuple[str] | set[str]) -> None:
        err_msg = (f"[{error_trace(self)}] `video_ids` must be a list, tuple, "
                   f"or set of unique 11-character video id strings "
                   f"referencing the video contents of this channel")
        if not isinstance(new_ids, (list, tuple, set)):
            context = f"(received object of type: {type(new_ids)})"
            raise TypeError(f"{err_msg} {context}")
        for v_id in new_ids:
            if not isinstance(v_id, str):
                context = f"(received video id of type: {type(v_id)})"
                raise TypeError(f"{err_msg} {context}")
            if len(v_id) != 11:
                context = f"(received malformed video id: {repr(v_id)})"
                raise ValueError(f"{err_msg} {context}")
        self._video_ids = list(new_ids)

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

    def to_json(self, json_path: Path | None = None) -> dict[str, str]:
        result = {
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

    def __eq__(self, other: Channel) -> bool:
        return self.id == other.id and self.last_updated == other.last_updated

    def __iter__(self) -> Iterator[Video]:
        if self.workers is not None and self.workers == 1:
            if self.source == "local":
                for video_id in self.video_ids:
                    yield Video.from_local(Path(self.target_dir, video_id))
            elif self.source == "pytube":
                for video_id in self.video_ids:
                    yield Video.from_pytube(video_id_to_url(video_id))
            elif self.source == "sql":
                for video_id in self.video_ids:
                    yield Video.from_sql(video_id)
        else:  # multithreading
            with ThreadPoolExecutor(max_workers=self.workers) as executor:
                try:
                    if self.source == "local":
                        def dispatch(v_id):
                            video_path = Path(self.target_dir, v_id)
                            return executor.submit(Video.from_local, video_path)
                        futures = [dispatch(v_id) for v_id in self.video_ids]
                    elif self.source == "pytube":
                        def dispatch(v_id):
                            video_url = video_id_to_url(v_id)
                            return executor.submit(Video.from_pytube, video_url)
                        futures = [dispatch(v_id) for v_id in self.video_ids]
                    elif self.source == "sql":
                        def dispatch(v_id):
                            return executor.submit(Video.from_sql, v_id)
                        futures = [dispatch(v_id) for v_id in self.video_ids]
                    for future in as_completed(futures):
                        yield future.result()
                except (KeyboardInterrupt, SystemExit) as exc:
                    print("Received kill signal.  Shutting down threads...")
                    executor.shutdown(cancel_futures=True)
                    raise exc

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
            "channel_id": repr(self.id),
            "channel_name": repr(self.name),
            "last_updated": repr(self.last_updated),
            "video_ids": crop_ids(self.video_ids),
            "about_html": crop_html(self.html["about"]),
            "community_html": crop_html(self.html["community"]),
            "featured_channels_html": crop_html(self.html["featured_channels"]),
            "videos_html": crop_html(self.html["videos"]),
            "workers": repr(self.workers),
            "target_dir": repr(self.target_dir)
        }
        chained = [f"{k}={v}" for k, v in prop_dict.items()]
        return f"Channel({', '.join(chained)})"

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
        self.stats = {
            "views": views,
            "rating": rating,
            "likes": likes,
            "dislikes": dislikes
        }
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

    #############################
    ####    CLASS METHODS    ####
    #############################

    @classmethod
    def from_local(cls,
                   video_path: Path,
                   channel: Channel | None = None) -> Video:
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

    @classmethod
    def from_pytube(cls,
                    video_url: str,
                    channel: Channel | None = None,
                    target_dir: Path | None = None) -> Video:
        try:
            online = pytube.YouTube(video_url)
            return cls(source="local",
                       video_id=video_url_to_id(video_url),
                       video_title=online.title,
                       publish_date=online.publish_date,
                       last_updated=datetime.now(),
                       duration=timedelta(seconds=online.length),
                       views=online.views,
                       rating=online.rating,
                       likes=None,
                       dislikes=None,
                       description=online.description,
                       keywords=online.keywords,
                       thumbnail_url=online.thumbnail_url,
                       target_dir=target_dir,
                       streams=online.streams,
                       captions=online.captions,
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

    ##########################
    ####    PROPERTIES    ####
    ##########################

    @property
    def captions(self) -> pytube.CaptionQuery:
        return self._captions

    @captions.setter
    def captions(self, new_captions: pytube.CaptionQuery | None) -> None:
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
                               f"{repr(new_channel.video_ids)}")
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
                context = f"(recieved empty keyword: {repr(keyword)})"
                raise ValueError(f"{err_msg} {context}")
        self._keywords = new_keywords

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    @last_updated.setter
    def last_updated(self, new_date: datetime) -> None:
        err_msg = (f"[{error_trace(self)}] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"video was checked for updates")
        if not isinstance(new_date, datetime):
            context = f"(received object of type: {type(new_date)}"
            raise TypeError(f"{err_msg} {context}")
        if new_date > datetime.now():
            context = f"('{str(new_date)}' > '{str(datetime.now())}')"
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
            context = f"(received object of type: {type(new_date)}"
            raise TypeError(f"{err_msg} {context}")
        if new_date > datetime.now():
            context = f"('{str(new_date)}' > '{str(datetime.now())}')"
            raise ValueError(f"{err_msg} {context}")
        self._publish_date = new_date

    @property
    def source(self) -> str:
        return self._source

    @source.setter
    def source(self, new_source: str) -> None:
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
        # TODO: check for existence of views and rating or likes + dislikes
        err_msg = (f"[{error_trace(self)}] `stats` must be a dictionary "
                   f"containing the view and rating statistics of the video")
        if not isinstance(new_stats, dict):
            context = f"(received object of type: {type(new_stats)})"
            raise TypeError(f"{err_msg} {context}")
        for k, v in new_stats.items():
            if not isinstance(k, str):
                context = f"(received non-string key of type: {type(k)})"
                raise TypeError(f"{err_msg} {context}")
            if not isinstance(v, (int, float)):
                context = (f"(received non-numeric value of type: {type(v)} "
                           f"for key: {repr(k)}")
                raise TypeError(f"{err_msg} {context}")
            if k == "views":
                if not isinstance(v, int):
                    context = (f"('views' must be an integer, received object "
                               f"of type: {type(v)})")
                    raise TypeError(f"{err_msg} {context}")
                if v < 0:
                    context = (f"('views' must be >= 0, received: {v})")
                    raise ValueError(f"{err_msg} {context}")
            elif k == "rating":
                if not 0 <= v <= 5:
                    context = (f"('rating' must be between 0 and 5, received: "
                               f"{v})")
                    raise ValueError(f"{err_msg} {context}")
            elif k == "likes":
                if not isinstance(v, int):
                    context = (f"('likes' must be an integer, received object "
                               f"of type: {type(v)})")
                    raise TypeError(f"{err_msg} {context}")
                if v < 0:
                    context = (f"('likes' must be >= 0, received: {v})")
                    raise ValueError(f"{err_msg} {context}")
            elif k == "dislikes":
                if not isinstance(v, int):
                    context = (f"('dislikes' must be an integer, received "
                               f"object of type: {type(v)})")
                    raise TypeError(f"{err_msg} {context}")
                if v < 0:
                    context = (f"('dislikes' must be >= 0, received: {v})")
                    raise ValueError(f"{err_msg} {context}")
        if ("likes" in new_stats and
            "dislikes" in new_stats and
            "rating" not in new_stats):
            likes = new_stats["likes"]
            dislikes = new_stats["dislikes"]
            new_stats["rating"] = 5 * likes / (likes + dislikes)
        self._stats = {"views": new_stats["views"],
                       "rating": new_stats["rating"]}

    @property
    def streams(self) -> pytube.StreamQuery:
        return self._streams

    @streams.setter
    def streams(self, new_streams: pytube.StreamQuery | None) -> None:
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
        if new_dir.exists() and not new_dir.is_dir():
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

    def to_json(self, json_path: Path = None) -> dict[str, str]:
        result = {
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

    def __len__(self) -> timedelta:
        return self.duration
