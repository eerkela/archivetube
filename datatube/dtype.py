from __future__ import annotations
from datetime import datetime, timedelta, timezone
from typing import Callable

import numpy as np
import pandas as pd

from datatube.error import error_trace


CONVERSIONS = {
    int: {
        float:
            lambda x: np.nan if pd.isnull(x) else float(x),
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x, 0),
        str:
            lambda x: pd.NA if pd.isnull(x) else str(int(x)),
        bool:
            lambda x: pd.NA if pd.isnull(x) else bool(x) if bool(x) == x
                      else ValueError,
        datetime:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timestamp.fromtimestamp(x, tz=timezone.utc),
        timedelta:
            lambda x: pd.NaT if pd.isnull(x) else pd.Timedelta(seconds=x)
    },
    float: {
        int:
            lambda x: np.nan if pd.isnull(x) else int(x) if int(x) == x
                      else ValueError,
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x, 0),
        str:
            lambda x: pd.NA if pd.isnull(x) else str(x),
        bool:
            lambda x: pd.NA if pd.isnull(x) else bool(x) if bool(x) == x
                      else ValueError,
        datetime:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timestamp.fromtimestamp(x, tz=timezone.utc),
        timedelta:
            lambda x: pd.NaT if pd.isnull(x) else pd.Timedelta(seconds=x)
    },
    complex: {
        int:
            lambda x: np.nan if pd.isnull(x)
                      else int(x.real) if int(x.real) == x
                      else ValueError,
        float:
            lambda x: np.nan if pd.isnull(x) else x.real if x.real == x
                      else ValueError,
        str:
            lambda x: pd.NA if pd.isnull(x) else str(x),
        bool:
            lambda x: pd.NA if pd.isnull(x)
                      else bool(x.real) if bool(x.real) == x
                      else ValueError,
        datetime:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timestamp.fromtimestamp(x.real, tz=timezone.utc)
                      if x.imag == 0
                      else ValueError,
        timedelta:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timedelta(seconds=x.real) if x.imag == 0
                      else ValueError
    },
    str: {
        int:
            lambda x: np.nan if pd.isnull(x) else int(x.strip()),
        float:
            lambda x: np.nan if pd.isnull(x) else float(x.strip()),
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x.strip()),
        bool:
            lambda x: pd.NA if pd.isnull(x)
                      else True if x.strip().lower() in ("true", "t")
                      else False if x.strip().lower() in ("false", "f")
                      else ValueError,
        timedelta:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timedelta(seconds=float(x.strip()))
    },
    bool: {
        int:
            lambda x: np.nan if pd.isnull(x) else int(x),
        float:
            lambda x: np.nan if pd.isnull(x) else float(x),
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x, 0),
        str:
            lambda x: np.nan if pd.isnull(x) else str(x),
        datetime:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timestamp.fromtimestamp(x, tz=timezone.utc),
        timedelta:
            lambda x: pd.NaT if pd.isnull(x) else pd.Timedelta(seconds=x)
    },
    datetime: {
        int:
            lambda x: np.nan if pd.isnull(x) else int(x.timestamp())
                      if int(x.timestamp()) == x.timestamp()
                      else ValueError,
        float:
            lambda x: np.nan if pd.isnull(x) else x.timestamp(),
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x.timestamp(), 0),
        str:
            lambda x: pd.NA if pd.isnull(x) else x.isoformat(),
        bool:
            lambda x: pd.NA if pd.isnull(x) else bool(x.timestamp())
                      if bool(x.timestamp()) == x.timestamp()
                      else ValueError,
        timedelta:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timedelta(seconds=x.timestamp())
    },
    timedelta: {
        int:
            lambda x: np.nan if pd.isnull(x) else int(x.total_seconds())
                      if int(x.total_seconds()) == x.total_seconds()
                      else ValueError,
        float:
            lambda x: np.nan if pd.isnull(x) else x.total_seconds(),
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x.total_seconds(), 0),
        str:
            lambda x: pd.NA if pd.isnull(x) else str(x),
        bool:
            lambda x: pd.NA if pd.isnull(x) else bool(x.total_seconds())
                      if bool(x.total_seconds()) == x.total_seconds()
                      else ValueError,
        datetime:
            lambda x: pd.NaT if pd.isnull(x)
                      else pd.Timestamp.fromtimestamp(x.total_seconds(),
                                                      tz=timezone.utc)
    },
    object: {
        int:
            lambda x: np.nan if pd.isnull(x) else int(x),
        float:
            lambda x: np.nan if pd.isnull(x) else float(x),
        complex:
            lambda x: np.nan if pd.isnull(x) else complex(x),
        str:
            lambda x: pd.NA if pd.isnull(x) else str(x),
        bool:
            lambda x: pd.NA if pd.isnull(x) else bool(x),
        datetime:  # TODO: remap the function used for this
            lambda x: pd.NaT if pd.isnull(x) else x.to_datetime(),
        timedelta:  # TODO: remap the function used for this
            lambda x: pd.NaT if pd.isnull(x) else x.to_timedelta()
    }
}

def get_series_dtype(series: pd.Series) -> type:
    # complex case - can't use series.convert_dtypes()
    if pd.api.types.is_complex_dtype(series):
        def to_integer(x):
            if pd.isnull(x):
                return np.nan
            if x.imag == 0 and int(x.real) == x.real:
                return int(x.real)
            raise ValueError()

        def to_float(x):
            if pd.isnull(x):
                return np.nan
            if x.imag == 0:
                return x.real
            raise ValueError()

        try:
            series.apply(to_integer)
            return int
        except ValueError:
            pass
        try:
            series.apply(to_float)
            return float
        except ValueError:
            pass
        return complex

    series = series.convert_dtypes()
    if pd.api.types.is_object_dtype(series):
        if not len(series.dropna()):  # all missing values
            return object
        try:  # differentiate between objects and bad datetime columns
            pd.to_datetime(series, utc=True)
            return datetime
        except (TypeError, ValueError):
            return object
    if pd.api.types.is_integer_dtype(series):
        return int
    if pd.api.types.is_float_dtype(series):
        return float
    if pd.api.types.is_string_dtype(series):
        return str
    if pd.api.types.is_bool_dtype(series):
        return bool
    if pd.api.types.is_datetime64_any_dtype(series):
        return datetime
    if pd.api.types.is_timedelta64_dtype(series):
        return timedelta
    err_msg = (f"[{error_trace()}] unexpected error: could not interpret "
               f"series dtype ({series.dtype})")
    raise TypeError(err_msg)


def _coerce_column(column: pd.Series, to_type: type) -> pd.Series:
    def do_coercion(element):
        result = CONVERSIONS[from_type][to_type](element)
        if result == ValueError:
            err_msg = (f"[{error_trace(stack_index=5)}] cannot coerce series "
                       f"values to {to_type} without losing information "
                       f"(head: {list(column.head())})")
            raise ValueError(err_msg)
        return result

    if to_type == object:
        return column.astype(np.dtype("O"))
    from_type = check_dtypes(column)
    if from_type == to_type:
        return column.copy()
    if from_type == str:
        if to_type == datetime:
            return pd.to_datetime(column, infer_datetime_format=True)
        if to_type == timedelta:
            return pd.to_timedelta(column)
    return column.apply(do_coercion)


def check_dtypes(
    data: pd.Series | pd.DataFrame,
    typespec: type | dict[str, type] | None = None
) -> type | dict[str, type] | bool | list[str]:
    if isinstance(data, pd.Series):
        if typespec is None:
            return get_series_dtype(data)
        if isinstance(typespec, type):
            return get_series_dtype(data) == typespec
        if isinstance(typespec, (tuple, list, set)):
            return get_series_dtype(data) in typespec
        err_msg = (f"[{error_trace()}] when used on a series, `typespec` must "
                   f"be an atomic data type, sequence of atomic data types, "
                   f"or None (received object of type: {type(typespec)})")
        raise TypeError(err_msg)

    if isinstance(data, pd.DataFrame):
        if typespec is None:
            return {col_name: get_series_dtype(data[col_name])
                    for col_name in data.columns}
        if isinstance(typespec, type):
            return [col_name for col_name in data.columns
                    if get_series_dtype(data[col_name]) == typespec]
        if isinstance(typespec, (tuple, list, set)):
            return [col_name for col_name in data.columns
                    if get_series_dtype(data[col_name]) in typespec]
        if isinstance(typespec, dict):
            for col_name, ts in typespec.items():
                dtype = get_series_dtype(data[col_name])
                if isinstance(ts, (tuple, list, set)):
                    if not dtype in ts:
                        return False
                else:
                    if dtype != ts:
                        return False
            return True
        err_msg = (f"[{error_trace()}] when used on a dataframe, `typespec` "
                   f"must be an atomic data type, sequence of atomic data "
                   f"types, map of column names and atomic data types, or "
                   f"None (received object of type: {type(typespec)})")
        raise TypeError(err_msg)

    err_msg = (f"[{error_trace()}] `data` must be either a pandas.Series or "
               f"pandas.DataFrame instance (received object of type: "
               f"{type(data)})")
    raise TypeError(err_msg)


def coerce_dtypes(
    data: pd.Series | pd.DataFrame,
    typespec: type | dict[str, type],
    downcast: bool = True,
    signed: bool = True,
    datetime_format: str | list[str] | tuple[str] | set[str] | None = None,
    object_method: Callable | None = None
) -> pd.Series | pd.DataFrame:
    if isinstance(data, pd.Series):
        if isinstance(typespec, type):
            try:
                return _coerce_column(data, typespec)
            except ValueError as exc:
                err_msg = (f"[{error_trace()}] cannot coerce series values to "
                           f"{typespec} without losing information "
                           f"(head: {list(data.head())})")
                raise ValueError(err_msg) from exc
        err_msg = (f"[{error_trace()}] when used on a series, `typespec` must "
                   f"be an atomic data type (received object of type: "
                   f"{type(typespec)})")
        raise TypeError(err_msg)

    if isinstance(data, pd.DataFrame):
        if isinstance(typespec, dict):
            result = {}
            for col_name, ts in typespec.items():
                try:
                    result[col_name] = _coerce_column(data[col_name], ts)
                except ValueError as exc:
                    err_msg = (f"[{error_trace()}] cannot coerce column "
                               f"{repr(col_name)} to {ts} without losing "
                               f"information (head: "
                               f"{list(data[col_name].head())})")
                    raise ValueError(err_msg) from exc
            return pd.concat(result, axis=1)
        err_msg = (f"[{error_trace()}] when used on a dataframe, "
                   f"`typespec` must be a dictionary of column names and "
                   f"atomic data types (received object of type: "
                   f"{type(typespec)})")
        raise TypeError(err_msg)

    err_msg = (f"[{error_trace()}] `data` must be either a pandas.Series or "
               f"pandas.DataFrame instance (received object of type: "
               f"{type(data)})")
    raise TypeError(err_msg)


def convert_dtypes(data: pd.DataFrame) -> pd.DataFrame:
    return coerce_dtypes(data, **check_dtypes(data))

