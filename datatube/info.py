from __future__ import annotations
from datetime import datetime, timedelta, timezone
import reprlib
from typing import Any, Iterable, Iterator

from datatube.error import error_trace



class PropertyDict:

    __slots__ = ("_immutable")

    def __init__(self, immutable: bool = False):
        if not isinstance(immutable, bool):
            err_msg = (f"[{error_trace()}] `immutable` must be a boolean "
                       f"(received object of type: {type(immutable)})")
            raise TypeError(err_msg)
        self._immutable = immutable

    @property
    def immutable(self) -> bool:
        return self._immutable

    def items(self) -> Iterator[tuple[str, Any]]:
        return zip(self.keys(), self.values())

    def keys(self) -> Iterator[str]:
        is_property = lambda a: isinstance(getattr(type(self), a), property)
        return (a for a in dir(type(self))
                if is_property(a) and a != "immutable")

    def values(self) -> Iterator[Any]:
        return (getattr(self, attr) for attr in self.keys())

    def __contains__(self, key: str) -> bool:
        return key in self.keys()

    def __eq__(self, other: dict | PropertyDict) -> bool:
        if not issubclass(type(other), (dict, PropertyDict)):
            err_msg = (f"[{error_trace()}] `other` must be another "
                       f"PropertyDict object or a base dictionary containing "
                       f"equivalent information (received object of type: "
                       f"{type(other)})")
            raise TypeError(err_msg)
        if len(self) != len(other):
            return False
        for key, val in self.items():
            if key not in other or val != other[key]:
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
        if not self._immutable:
            err_msg = (f"[{error_trace()}] PropertyDict cannot be hashed: "
                       f"instance must be immutable")
            raise TypeError(err_msg)  # hash(mutable) always throws TypeError
        return hash(tuple(self.items()))

    def __iter__(self) -> Iterable[str]:
        yield from self.keys()

    def __len__(self) -> int:
        # this will always evaluate to the number of @property attributes
        return len(list(self.keys()))

    def __repr__(self) -> str:
        return f"PropertyDict(immutable={self._immutable})"

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
        str_repr = reprlib.Repr()
        contents = []
        for k, v in self.items():
            if issubclass(type(v), PropertyDict):
                contents.append(f"{repr(k)}: {str(v)}")
            elif isinstance(v, str):
                contents.append(f"{repr(k)}: {str_repr.repr(v)}")
            else:
                contents.append(f"{repr(k)}: {repr(v)}")
        return f"{{{', '.join(contents)}}}"


class ChannelInfo(PropertyDict):

    __slots__ = ("_channel_id", "_channel_name", "_html", "_last_updated")

    def __init__(self,
                 channel_id: str,
                 channel_name: str,
                 last_updated: datetime,
                 about_html: str,
                 community_html: str,
                 featured_channels_html: str,
                 videos_html: str,
                 immutable: bool = False):
        super().__init__(immutable=immutable)
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
                context = (f"(could not convert base dictionary)")
                raise ValueError(f"{err_msg} {context}") from err
        new_html._immutable = self._immutable
        self._html = new_html

    def __repr__(self) -> str:
        fields = {
            "channel_id": self.channel_id,
            "channel_name": self.channel_name,
            "last_updated": self.last_updated,
            "about_html": self.html["about"],
            "community_html": self.html["community"],
            "featured_channels_html": self.html["featured_channels"],
            "videos_html": self.html["videos"],
            "immutable": self._immutable
        }
        str_repr = reprlib.Repr()
        contents = []
        for k, v in fields.items():
            if isinstance(v, str):
                contents.append(f"{k}={str_repr.repr(v)}")
            else:
                contents.append(f"{k}={repr(v)}")
        return f"ChannelInfo({', '.join(contents)})"

    class HtmlDict(PropertyDict):

        __slots__ = ("_about", "_community", "_featured_channels", "_videos")

        def __init__(self,
                     about: str,
                     community: str,
                     featured_channels: str,
                     videos: str,
                     immutable: bool = False):
            super().__init__(immutable=immutable)
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

        def __repr__(self) -> str:
            fields = {
                "about": self.about,
                "community": self.community,
                "featured_channels": self.featured_channels,
                "videos": self.videos,
                "immutable": self._immutable
            }
            str_repr = reprlib.Repr()
            contents = []
            for k, v in fields.items():
                if isinstance(v, str):
                    contents.append(f"{k}={str_repr.repr(v)}")
                else:
                    contents.append(f"{k}={repr(v)}")
            return f"ChannelInfo.HtmlDict({', '.join(contents)})"
