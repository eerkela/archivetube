from __future__ import annotations
from datetime import datetime, timedelta
from pathlib import Path

from datatube import AVAILABLE_SOURCES
from datatube.error import error_trace

import validators


##############################
####    BOOLEAN CHECKS    ####
##############################


def is_channel_id(id_str: str) -> bool:
    return len(id_str) == 24 and id_str.startswith("UC")


def is_readable(path: Path) -> bool:
    return path.is_dir() and len(path.glob("info.json")) > 0


def is_url(url_str: str) -> bool:
    result = validators.url(url_str)
    return not isinstance(result, validators.ValidationFailure)

def is_video_id(id_str: str) -> bool:
    return len(id_str) == 11


############################
####    ERROR CHECKS    ####
############################


def channel_html(value: dict[str, str], err_msg: str) -> dict[str, str]:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, dict):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    for k, v in value.items():
        if not isinstance(k, str):
            context = f"(received key of type: {type(k)})"
            raise TypeError(f"{trace} {err_msg} {context}")
        if not isinstance(v, str):
            context = f"(received value of type: {type(v)} for key: {repr(k)})"
            raise TypeError(f"{trace} {err_msg} {context}")
    return value


def channel_id(value: str, err_msg: str) -> str:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, str):
        context = (f"(received object of type: {type(value)})")
        raise TypeError(f"{trace} {err_msg} {context}")
    if not is_channel_id(value):
        context = (f"(received: {repr(value)})")
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def duration(value: timedelta, err_msg: str) -> timedelta:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, timedelta):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if value < timedelta():
        context = f"({value} < {timedelta()})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def positive_int(value: int, err_msg: str) -> int:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, int):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if value <= 0:
        context = f"(received: {value})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def source(value: str, err_msg: str) -> str:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, str):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if value not in AVAILABLE_SOURCES:
        context = f"(received: {repr(value)})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def str_not_empty(value: str, err_msg: str) -> str:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, str):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if not value:  # value is empty string
        context = f"(received: {repr(value)})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def target_dir(value: Path, err_msg: str) -> Path:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, Path):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if value.exists() and not value.is_dir():
        context = f"(path points to file: {value})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def timestamp(value: datetime, err_msg: str) -> datetime:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, datetime):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if value > datetime.now():
        context = f"(timestamp in the future: {value} > {datetime.now()})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def video_id(value: str, err_msg: str) -> str:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, str):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    if not is_video_id(value):
        context = f"(received: {repr(value)})"
        raise ValueError(f"{trace} {err_msg} {context}")
    return value


def video_id_list(value: list[str] | tuple[str] | set[str],
                  err_msg: str) -> list[str]:
    trace = f"[{error_trace(stack_index=2)}]"
    if not isinstance(value, (list, tuple, set)):
        context = f"(received object of type: {type(value)})"
        raise TypeError(f"{trace} {err_msg} {context}")
    for v_id in value:
        if not isinstance(v_id, str):
            context = f"(received id of type: {type(v_id)})"
            raise TypeError(f"{trace} {err_msg} {context}")
        if not is_video_id(v_id):
            context = f"(encountered malformed video id: {repr(v_id)})"
            raise ValueError(f"{trace} {err_msg} {context}")
    return list(value)
