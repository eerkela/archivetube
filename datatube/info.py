from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Iterable, Iterator

from datatube.error import error_trace


class ChannelInfo:

    __slots__ = ("_channel_id", "_channel_name", "_last_updated", "_html",
                 "_immutable")

    def __init__(self,
                 channel_id: str,
                 channel_name: str,
                 last_updated: datetime,
                 about_html: str = "",
                 community_html: str = "",
                 featured_channels_html: str = "",
                 videos_html: str = "",
                 immutable: bool = False):
        if not isinstance(immutable, bool):
            err_msg = (f"[{error_trace()}] `immutable` must be a boolean "
                       f"(received object of type: {type(immutable)})")
            raise TypeError(err_msg)
        self._immutable = immutable

        self.channel_id = channel_id
        self.channel_name = channel_name
        self.last_updated = last_updated
        self.html = ChannelInfo.HtmlDict(
            about=about_html,
            community=community_html,
            featured_channels=featured_channels_html,
            videos=videos_html,
            immutable=immutable
        )

    @property
    def channel_id(self) -> str:
        return self._channel_id

    @channel_id.setter
    def channel_id(self, new_id: str) -> None:
        if self._immutable and hasattr(self, "_channel_id"):
            err_msg = (f"[{error_trace()}] cannot reassign `channel_id`: "
                       f"ChannelInfo instance is immutable")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace()}] `channel_id` must be a 24-character "
                   f"ExternalId string starting with 'UC'")
        if not isinstance(new_id, str):
            context = f"(received object of type: {type(new_id)})"
            raise TypeError(f"{err_msg} {context}")
        if len(new_id) != 24 or not new_id.startswith("UC"):
            context = f"(received: {repr(new_id)})"
            raise ValueError(f"{err_msg} {context}")
        self._channel_id = new_id

    @property
    def channel_name(self) -> str:
        return self._channel_name

    @channel_name.setter
    def channel_name(self, new_name: str) -> None:
        if self._immutable and hasattr(self, "_channel_name"):
            err_msg = (f"[{error_trace()}] cannot reassign `channel_name`: "
                       f"ChannelInfo instance is immutable")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace()}] `channel_name` must be a non-empty "
                   f"string")
        if not isinstance(new_name, str):
            context = f"(received object of type: {type(new_name)})"
            raise TypeError(f"{err_msg} {context}")
        if not new_name:
            context = f"(received: {repr(new_name)})"
            raise ValueError(f"{err_msg} {context}")
        self._channel_name = new_name

    @property
    def last_updated(self) -> datetime:
        return self._last_updated

    @last_updated.setter
    def last_updated(self, new_time: datetime) -> None:
        if self._immutable and hasattr(self, "_last_updated"):
            err_msg = (f"[{error_trace()}] cannot reassign `last_updated`: "
                       f"ChannelInfo instance is immutable")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace()}] `last_updated` must be a timezone-aware "
                   f"datetime.datetime object stating the last time this "
                   f"channel's information was checked for updates")
        if not isinstance(new_time, datetime):
            context = f"(received object of type: {type(new_time)})"
            raise TypeError(f"{err_msg} {context}")
        if new_time.tzinfo is None:
            context = (f"(timestamp has no timezone information: "
                       f"{repr(new_time)})")
            raise ValueError(f"{err_msg} {context}")
        current_time = datetime.now(timezone.utc)
        if new_time > current_time:
            context = f"(timestamp in the future: {new_time} > {current_time})"
            raise ValueError(f"{err_msg} {context}")
        self._last_updated = new_time

    @property
    def html(self) -> ChannelInfo.HtmlDict:
        return self._html

    @html.setter
    def html(self, new_html: ChannelInfo.HtmlDict | dict[str, str]) -> None:
        if self._immutable and hasattr(self, "_html"):
            err_msg = (f"[{error_trace()}] cannot reassign `html`: "
                       f"ChannelInfo instance is immutable")
            raise AttributeError(err_msg)
        err_msg = (f"[{error_trace()}] `html` must be a ChannelInfo.HtmlDict "
                   f"object or a base dictionary containing equivalent "
                   f"information")
        if not isinstance(new_html, (ChannelInfo.HtmlDict, dict)):
            context = f"(received object of type: {type(new_html)})"
            raise TypeError(f"{err_msg} {context}")
        if isinstance(new_html, dict):
            try:
                new_html = ChannelInfo.HtmlDict(**new_html)
            except (TypeError, ValueError) as err:
                context = (f"(could not convert base dictionary: "
                           f"{repr(new_html)})")
                raise type(err)(f"{err_msg} {context}") from err
        new_html._immutable = self._immutable
        self._html = new_html

    def items(self):
        return zip(self.keys(), self.values())

    def keys(self):
        return ("channel_id", "channel_name", "last_updated", "html")

    def values(self):
        return (self.channel_id, self.channel_name, self.last_updated,
                self.html)

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __eq__(self, other: ChannelInfo | dict) -> bool:
        if not isinstance(other, (ChannelInfo, dict)):
            err_msg = (f"[{error_trace()}] `other` must be another "
                       f"ChannelInfo object or a base dictionary containing "
                       f"equivalent information (received object of type: "
                       f"{type(other)})")
            raise TypeError(err_msg)
        if isinstance(other, ChannelInfo):
            return (self.channel_id == other.channel_id and
                    self.channel_name == other.channel_name and
                    self.last_updated == other.last_updated and
                    self.html == other.html)
            # return hash(self) == hash(other)
        try:
            return (self.channel_id == other["channel_id"] and
                    self.channel_name == other["channel_name"] and
                    self.last_updated == other["last_updated"] and
                    self.html.about == other["html"]["about"] and
                    self.html.community == other["html"]["community"] and
                    self.html.featured_channels == \
                        other["html"]["featured_channels"] and
                    self.html.videos == other["html"]["videos"])
        except KeyError:
            return False

    def __getitem__(self, key: str):
        if not isinstance(key, str):
            err_msg = (f"[{error_trace()}] key must be a string (received "
                       f"object of type: {type(key)})")
            raise TypeError(err_msg)
        if key not in self.keys():
            err_msg = f"[{error_trace()}] KeyError: {repr(key)}"
            raise KeyError(err_msg)
        return getattr(self, key)

    def __hash__(self) -> int:
        return hash(self.keys())

    def __iter__(self) -> Iterable[str]:
        yield from self.keys()

    def __setitem__(self, key: str, val) -> None:
        if not isinstance(key, str):
            err_msg = (f"[{error_trace()}] key must be a string (received "
                       f"object of type: {type(key)})")
            raise TypeError(err_msg)
        if key not in self.keys():
            err_msg = f"[{error_trace()}] KeyError: {repr(key)}"
            raise KeyError(err_msg)
        setattr(self, key, val)

    def __str__(self) -> str:
        max_width = 50
        contents = []
        for k, v in self.items():
            if len(v) > max_width:
                contents.append(f"'{k}': '{v[:max_width]}...'")
            else:
                contents.append(f"'{k}': '{v}'")
        return f"{{{', '.join(contents)}}}"

    class HtmlDict:

        __slots__ = ("_about", "_community", "_featured_channels", "_videos",
                     "_immutable")

        def __init__(self,
                     about: str = "",
                     community: str = "",
                     featured_channels: str = "",
                     videos: str = "",
                     immutable: bool = False):
            if not isinstance(immutable, bool):
                err_msg = (f"[{error_trace()}] `immutable` must be a boolean "
                           f"(received object of type: {type(immutable)})")
                raise TypeError(err_msg)
            self._immutable = immutable

            self.about = about
            self.community = community
            self.featured_channels = featured_channels
            self.videos = videos

        @property
        def about(self) -> str:
            return self._about

        @about.setter
        def about(self, new_html: str) -> None:
            if self._immutable and hasattr(self, "_about"):
                err_msg = (f"[{error_trace()}] cannot reassign `about`: "
                           f"HtmlDict instance is immutable")
                raise AttributeError(err_msg)
            err_msg = f"[{error_trace()}] `about` must be a string"
            if not isinstance(new_html, str):
                context = f"(received object of type: {type(new_html)})"
                raise TypeError(f"{err_msg} {context}")
            self._about = new_html

        @property
        def community(self) -> str:
            return self._community

        @community.setter
        def community(self, new_html: str) -> None:
            if self._immutable and hasattr(self, "_community"):
                err_msg = (f"[{error_trace()}] cannot reassign `community`: "
                           f"HtmlDict instance is immutable")
                raise AttributeError(err_msg)
            err_msg = f"[{error_trace()}] `community` must be a string"
            if not isinstance(new_html, str):
                context = f"(received object of type: {type(new_html)})"
                raise TypeError(f"{err_msg} {context}")
            self._community = new_html

        @property
        def featured_channels(self) -> str:
            return self._featured_channels

        @featured_channels.setter
        def featured_channels(self, new_html: str) -> None:
            if self._immutable and hasattr(self, "_featured_channels"):
                err_msg = (f"[{error_trace()}] cannot reassign "
                           f"`featured_channels`: HtmlDict instance is "
                           f"immutable")
                raise AttributeError(err_msg)
            err_msg = f"[{error_trace()}] `featured_channels` must be a string"
            if not isinstance(new_html, str):
                context = f"(received object of type: {type(new_html)})"
                raise TypeError(f"{err_msg} {context}")
            self._featured_channels = new_html

        @property
        def videos(self) -> str:
            return self._videos

        @videos.setter
        def videos(self, new_html: str) -> None:
            if self._immutable and hasattr(self, "_videos"):
                err_msg = (f"[{error_trace()}] cannot reassign `videos`: "
                           f"HtmlDict instance is immutable")
                raise AttributeError(err_msg)
            err_msg = f"[{error_trace()}] `videos` must be a string"
            if not isinstance(new_html, str):
                context = f"(received object of type: {type(new_html)})"
                raise TypeError(f"{err_msg} {context}")
            self._videos = new_html

        def items(self):
            return zip(self.keys(), self.values())

        def keys(self):
            return ("about", "community", "featured_channels", "videos")

        def values(self):
            return (self.about, self.community, self.featured_channels,
                    self.videos)

        def __contains__(self, key: str) -> bool:
            return key in self.keys()

        def __eq__(self, other: ChannelInfo.HtmlDict | dict) -> bool:
            if not isinstance(other, (ChannelInfo.HtmlDict, dict)):
                err_msg = (f"[{error_trace()}] `other` must be another "
                           f"ChannelInfo.HtmlDict object or a base dictionary "
                           f"containing equivalent information (received "
                           f"object of type: {type(other)})")
                raise TypeError(err_msg)
            if isinstance(other, ChannelInfo.HtmlDict):
                return hash(self) == hash(other)
            try:
                if set(self.keys()) != set(other.keys()):
                    return False
                for key, value in self.items():
                    if other[key] != value:
                        return False
            except KeyError:
                return False
            return True

        def __getitem__(self, key: str):
            if not isinstance(key, str):
                err_msg = (f"[{error_trace()}] key must be a string (received "
                           f"object of type: {type(key)})")
                raise TypeError(err_msg)
            if key not in self.keys():
                err_msg = f"[{error_trace()}] KeyError: {repr(key)}"
                raise KeyError(err_msg)
            return getattr(self, key)

        def __hash__(self) -> int:
            return hash(self.values())

        def __iter__(self) -> Iterator[str]:
            yield from self.keys()

        def __setitem__(self, key: str, val) -> None:
            if not isinstance(key, str):
                err_msg = (f"[{error_trace()}] key must be a string (received "
                           f"object of type: {type(key)})")
                raise TypeError(err_msg)
            if key not in self.keys():
                err_msg = f"[{error_trace()}] KeyError: {repr(key)}"
                raise KeyError(err_msg)
            setattr(self, key, val)

        def __str__(self) -> str:
            max_width = 50
            contents = []
            for k, v in self.items():
                if len(v) > max_width:
                    contents.append(f"'{k}': '{v[:max_width]}...'")
                else:
                    contents.append(f"'{k}': '{v}'")
            return f"{{{', '.join(contents)}}}"
