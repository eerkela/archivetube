from __future__ import annotations
from datetime import datetime, timedelta, timezone
import warnings

import numpy as np
import pandas as pd
import pandas.api.types as pdtypes

from datatube.error import error_trace


AVAILABLE_DTYPES = (object, int, float, complex, str, bool, datetime, timedelta)
CONVERSIONS = {
    int: {
        float:
            lambda x: float(x) if not pd.isnull(x) else np.nan,
        complex:
            lambda x: complex(x, 0) if not pd.isnull(x) else np.nan,
        str:
            lambda x: str(int(x)) if not pd.isnull(x) else pd.NA,
        bool:
            lambda x: bool(x) if not pd.isnull(x) and bool(x) == x
                      else pd.NA if pd.isnull(x)
                      else ValueError,
        datetime:
            lambda x: datetime.fromtimestamp(x, tz=timezone.utc)
                      if not pd.isnull(x) else pd.NaT,
        timedelta:
            lambda x: timedelta(seconds=x) if not pd.isnull(x)
                      else pd.NaT
    },
    float: {
        int:
            lambda x: int(x) if not pd.isnull(x) and int(x) == x
                      else np.nan if pd.isnull(x)
                      else ValueError,
        complex:
            lambda x: complex(x, 0) if not pd.isnull(x) else np.nan,
        str:
            lambda x: str(x) if not pd.isnull(x) else pd.NA,
        bool:
            lambda x: bool(x) if not pd.isnull(x) and bool(x) == x
                      else pd.NA if pd.isnull(x)
                      else ValueError,
        datetime:
            lambda x: datetime.fromtimestamp(x, tz=timezone.utc)
                      if not pd.isnull(x) else pd.NaT,
        timedelta:
            lambda x: timedelta(seconds=x) if not pd.isnull(x)
                      else pd.NaT
    },
    complex: {
        int:
            lambda x: int(x.real) if not pd.isnull(x) and int(x.real) == x
                      else np.nan if pd.isnull(x)
                      else ValueError,
        float:
            lambda x: x.real if not pd.isnull(x) and x.real == x
                      else np.nan if pd.isnull(x)
                      else ValueError,
        str:
            lambda x: str(x) if not pd.isnull(x) else pd.NA,
        bool:
            lambda x: bool(x.real) if not pd.isnull(x) and bool(x.real) == x
                      else pd.NA if pd.isnull(x)
                      else ValueError,
        datetime:
            lambda x: datetime.fromtimestamp(x.real, tz=timezone.utc)
                      if not pd.isnull(x) and x.imag == 0
                      else pd.NaT if pd.isnull(x)
                      else ValueError,
        timedelta:
            lambda x: timedelta(seconds=x.real)
                      if not pd.isnull(x) and x.imag == 0
                      else pd.NaT if pd.isnull(x)
                      else ValueError
    },
    str: {
        int:
            lambda x: int(x.strip()) if not pd.isnull(x) else np.nan,
        float:
            lambda x: float(x.strip()) if not pd.isnull(x) else np.nan,
        complex:
            lambda x: complex(x.strip()) if not pd.isnull(x) else np.nan,
        bool:
            lambda x: pd.NA if pd.isnull(x)
                      else True if x.strip().lower() in ("true", "t")
                      else False if x.strip().lower() in ("false", "f")
                      else ValueError,
        timedelta:
            lambda x: timedelta(seconds=float(x.strip())) if not pd.isnull(x)
                      else pd.NaT
    },
    bool: {
        int:
            lambda x: int(x) if not pd.isnull(x) else np.nan,
        float:
            lambda x: float(x) if not pd.isnull(x) else np.nan,
        complex:
            lambda x: complex(x, 0) if not pd.isnull(x) else np.nan,
        str:
            lambda x: str(x) if not pd.isnull(x) else np.nan,
        datetime:
            lambda x: datetime.fromtimestamp(x, tz=timezone.utc)
                      if not pd.isnull(x) else pd.NaT,
        timedelta:
            lambda x: timedelta(seconds=x) if not pd.isnull(x)
                      else pd.NaT
    },
    datetime: {
        int:
            lambda x: int(x.timestamp()) if not pd.isnull(x) and
                      int(x.timestamp()) == x.timestamp()
                      else np.nan if pd.isnull(x)
                      else ValueError,
        float:
            lambda x: x.timestamp() if not pd.isnull(x) else np.nan,
        complex:
            lambda x: complex(x.timestamp(), 0) if not pd.isnull(x)
                      else np.nan,
        str:
            lambda x: x.isoformat() if not pd.isnull(x) else pd.NA,
        bool:
            lambda x: bool(x.timestamp()) if not pd.isnull(x) and
                      bool(x.timestamp()) == x.timestamp()
                      else pd.NA if pd.isnull(x)
                      else ValueError,
        timedelta:
            lambda x: timedelta(seconds=x.timestamp()) if not pd.isnull(x)
                      else pd.NaT
    },
    timedelta: {
        int:
            lambda x: int(x.total_seconds()) if not pd.isnull(x) and
                      int(x.total_seconds()) == x.total_seconds()
                      else np.nan if pd.isnull(x)
                      else ValueError,
        float:
            lambda x: x.total_seconds() if not pd.isnull(x) else np.nan,
        complex:
            lambda x: complex(x.total_seconds(), 0) if not pd.isnull(x)
                      else np.nan,
        str:
            lambda x: str(x) if not pd.isnull(x) else pd.NA,
        bool:
            lambda x: bool(x.total_seconds()) if not pd.isnull(x) and
                      bool(x.total_seconds()) == x.total_seconds()
                      else pd.NA if pd.isnull(x)
                      else ValueError,
        datetime:
            lambda x: datetime.fromtimestamp(x.total_seconds(),
                                             tz=timezone.utc)
                      if not pd.isnull(x) else pd.NaT
    }
}


def _check_column(column: pd.Series,
                  typespec: type,
                  convert: bool = True) -> bool:
    dtype_lookup = {  # order indicates priority in kwargless lookup
        object: pdtypes.is_object_dtype,  # convert_dtypes -> not a str
        int: pdtypes.is_integer_dtype,
        float: pdtypes.is_float_dtype,
        complex: pdtypes.is_complex_dtype,
        str: pdtypes.is_string_dtype,
        bool: pdtypes.is_bool_dtype,
        datetime: pdtypes.is_datetime64_any_dtype,
        timedelta: pdtypes.is_timedelta64_dtype
    }
    if convert:
        # convert_dtypes always emits an np.ComplexWarning for complex dtypes
        warnings.simplefilter("ignore", np.ComplexWarning)
        try:
            column = column.convert_dtypes()
        except TypeError:
            pass

    # repair falsely identified objects:
    if dtype_lookup[object](column):
        if typespec == str:
            return False
        if typespec == datetime and len(column.dropna()) > 0:
            try:
                pd.to_datetime(column, utc=True)
                return True
            except (TypeError, ValueError):
                return False
        if typespec == object and len(column.dropna()) > 0:
            try:
                pd.to_datetime(column, utc=True)
                return False
            except (TypeError, ValueError):
                return True
    return dtype_lookup[typespec](column)


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
            for ts in AVAILABLE_DTYPES:
                if _check_column(data, ts):
                    return ts
            err_msg = (f"[{error_trace()}] could not identify series dtype "
                       f"(head: {data.head()})")
            raise RuntimeError(err_msg)
        if isinstance(typespec, type):
            return _check_column(data, typespec)
        err_msg = (f"[{error_trace()}] when used on a series, `typespec` must "
                   f"be an atomic data type or None (received object of type: "
                   f"{type(typespec)})")
        raise TypeError(err_msg)

    if isinstance(data, pd.DataFrame):
        if typespec is None:
            result = {}
            for col_name in data.columns:
                for typespec in AVAILABLE_DTYPES:
                    if _check_column(data[col_name], typespec):
                        result[col_name] = typespec
                        break
            return result
        if isinstance(typespec, type):
            result = []
            for col_name in data.columns:
                if _check_column(data[col_name], typespec):
                    result.append(col_name)
            return result
        if isinstance(typespec, dict):
            return all(_coerce_column(data[col_name], ts)
                       for col_name, ts in typespec.items())
        err_msg = (f"[{error_trace()}] when used on a dataframe, `typespec` "
                   f"must be an atomic data type, a map of column names and "
                   f"atomic data types, or None (received object of type: "
                   f"{type(typespec)})")
        raise TypeError(err_msg)

    err_msg = (f"[{error_trace()}] `data` must be either a pandas.Series or "
               f"pandas.DataFrame instance (received object of type: "
               f"{type(data)})")
    raise TypeError(err_msg)


def coerce_dtypes(data: pd.Series | pd.DataFrame,
                  typespec: type | dict[str, type]) -> pd.Series | pd.DataFrame:
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