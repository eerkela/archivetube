from datetime import datetime, timedelta, timezone
from pathlib import Path
import random
from typing import Any
import unittest

import numpy as np
import pandas as pd
from pandas.testing import assert_frame_equal, assert_series_equal
import pytz

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datatube.dtype import _check_column, _coerce_column, check_dtypes, coerce_dtypes


SIZE = 3
TEST_COLUMN_NAME = "test_col"
unittest.TestCase.maxDiff = None


class TestObj:
        pass


def coercion_test(input_data: pd.Series,
                  typeconv: type,
                  output_data: pd.Series) -> None:
    # Series
    result = coerce_dtypes(input_data, typeconv)
    assert_series_equal(result, output_data)

    # DataFrame
    input_df = pd.DataFrame({TEST_COLUMN_NAME: input_data})
    result = coerce_dtypes(input_df, {TEST_COLUMN_NAME: typeconv})
    output_df = pd.DataFrame({TEST_COLUMN_NAME: output_data})
    assert_frame_equal(result, output_df)


def info_loss_test(test_manager,
                   input_data: pd.Series,
                   typeconv: type) -> None:
    series_err_msg = (f"[datatube.dtype.coerce_dtypes] cannot coerce series "
                      f"values to {typeconv} without losing information "
                      f"(head: {list(input_data.head())})")
    dataframe_err_msg = (f"[datatube.dtype.coerce_dtypes] cannot coerce "
                         f"column {repr(TEST_COLUMN_NAME)} to {typeconv} "
                         f"without losing information (head: "
                         f"{list(input_data.head())})")
    with test_manager.assertRaises(ValueError) as err:
        coerce_dtypes(input_data, typeconv)
    test_manager.assertEqual(str(err.exception), series_err_msg)
    with test_manager.assertRaises(ValueError) as err:
        df = pd.DataFrame({TEST_COLUMN_NAME: input_data})
        coerce_dtypes(df, {TEST_COLUMN_NAME: typeconv})
    test_manager.assertEqual(str(err.exception), dataframe_err_msg)


class CheckDtypesTests(unittest.TestCase):

    test_data = {
        int: {
            "integers": [-1 * SIZE // 2 + i + 1 for i in range(SIZE)],
            "whole_floats": [float(i + 1) for i in range(SIZE)],
            "int_bool_flags": [(i + 1) % 2 for i in range(SIZE)]
        },
        float: {
            "decimal_floats": [i + 0.5 for i in range(SIZE)]
        },
        complex: {
            "real_whole_complex": [complex(i + 1, 0) for i in range(SIZE)],
            "real_decimal_complex": [complex(i + 0.5, 0) for i in range(SIZE)],
            "imaginary_complex": [complex(i + 1, i + 1) for i in range(SIZE)]
        },
        str: {
            "character_strings": [chr(i % 26 + ord("a")) for i in range(SIZE)],
            "integer_strings": [str(i + 1) for i in range(SIZE)],
            "int_bool_flag_strings": [str((i + 1) % 2) for i in range(SIZE)],
            "whole_float_strings": [str(i + 1.0) for i in range(SIZE)],
            "decimal_strings": [str(i + 1.5) for i in range(SIZE)],
            "real_whole_complex_strings":
                [str(complex(i + 1, 0)) for i in range(SIZE)],
            "real_decimal_complex_strings":
                [str(complex(i + 1.5, 0)) for i in range(SIZE)],
            "imaginary_complex_strings":
                [str(complex(i + 1, i + 1)) for i in range(SIZE)],
            "boolean_strings": [str(bool((i + 1) % 2)) for i in range(SIZE)],
            "naive_ISO_8601_strings":
                [datetime.fromtimestamp(i).isoformat() for i in range(SIZE)],
            "aware_ISO_8601_strings":
                [datetime.fromtimestamp(i, tz=timezone.utc).isoformat()
                 for i in range(SIZE)]
        },
        bool: {
            "bools": [bool((i + 1) % 2) for i in range(SIZE)]
        },
        datetime: {
            "naive_datetimes": [datetime.fromtimestamp(i) for i in range(SIZE)],
            "aware_datetimes":
                [datetime.fromtimestamp(i, tz=timezone.utc)
                 for i in range(SIZE)],
            "mixed_datetimes_aware_naive":
                [datetime.fromtimestamp(i, tz=timezone.utc) if i % 2
                 else datetime.fromtimestamp(i) for i in range(SIZE)],
            "mixed_datetime_timezones":
                [datetime.fromtimestamp(
                    i,
                    tz=pytz.timezone(
                        pytz.all_timezones[i % len(pytz.all_timezones)]
                    )
                ) for i in range(SIZE)]
        },
        timedelta: {
            "timedeltas": [timedelta(seconds=i + 1) for i in range(SIZE)]
        },
        object: {
            "missing_values": [None for _ in range(SIZE)],
            "custom_objects": [TestObj() for _ in range(SIZE)]
        }
    }
    all_data = {k: v for tests in test_data.values() for k, v in tests.items()}

    def test_check_column_helper_no_na(self):
        test_df = pd.DataFrame(self.all_data)
        failed = []
        for typespec in self.test_data:
            for col_name in test_df.columns:
                column = test_df[col_name]
                result = _check_column(column, typespec)
                expected = col_name in self.test_data[typespec]
                try:
                    self.assertEqual(result, expected)
                except AssertionError:
                    context = (f"_check_column(test_df[{repr(col_name)}], "
                               f"{typespec.__name__}) != {expected}")
                    failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_column_helper_with_na(self):
        with_na = {k: [*v, None] for k, v in self.all_data.items()}
        test_df = pd.DataFrame(with_na)
        failed = []
        for typespec in self.test_data:
            for col_name in test_df.columns:
                column = test_df[col_name]
                result = _check_column(column, typespec)
                expected = col_name in self.test_data[typespec]
                try:
                    self.assertEqual(result, expected)
                except AssertionError:
                    context = (f"_check_column(test_df[{repr(col_name)}], "
                               f"{typespec.__name__}) != {expected}")
                    failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_dtypes_kwargless_no_na(self):
        test_df = pd.DataFrame(self.all_data)
        expected = {name: typespec for typespec, v in self.test_data.items()
                    for name in v}
        self.assertEqual(check_dtypes(test_df), expected)

    def test_check_dtypes_kwargless_with_na(self):
        with_na = {k: [*v, None] for k, v in self.all_data.items()}
        test_df = pd.DataFrame(with_na)
        expected = {name: typespec for typespec, v in self.test_data.items()
                    for name in v}
        self.assertEqual(check_dtypes(test_df), expected)

    def test_check_dtypes_kwargs_no_na(self):
        test_df = pd.DataFrame(self.all_data)
        failed = []
        for typespec in self.test_data:
            for col_name in test_df.columns:
                result = check_dtypes(test_df, **{col_name: typespec})
                expected = col_name in self.test_data[typespec]
                try:
                    self.assertEqual(result, expected)
                except AssertionError:
                    context = (f"check_dtypes(test_df, "
                               f"{col_name}={typespec.__name__}) != {expected}")
                    failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_dtypes_kwargs_with_na(self):
        with_na = {k: [*v, None] for k, v in self.all_data.items()}
        test_df = pd.DataFrame(with_na)
        failed = []
        for typespec in self.test_data:
            for col_name in test_df.columns:
                result = check_dtypes(test_df, **{col_name: typespec})
                expected = col_name in self.test_data[typespec]
                try:
                    self.assertEqual(result, expected)
                except AssertionError:
                    context = (f"check_dtypes(test_df, "
                               f"{col_name}={typespec.__name__}) != {expected}")
                    failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")


class CoerceDtypesTests(unittest.TestCase):

    example_data = {
        "integers": [-1 * SIZE // 2 + i + 1 for i in range(SIZE)],
        "decimal floats": [-1 * SIZE // 2 + i + 1.5 for i in range(SIZE)],
        "decimal floats (0, 1)": [random.random() for _ in range(SIZE)],
        "booleans": [bool((i + 1) % 2) for i in range(SIZE)],
        "character strings": [chr(i % 26 + ord("a")) for i in range(SIZE)],
        "random datetimes":
            [datetime.fromtimestamp(i + random.random(), tz=timezone.utc)
             for i in range(SIZE)],
        "random naive datetimes":
            [datetime.utcfromtimestamp(i) for i in range(SIZE)],
        "random timedeltas":
            [timedelta(seconds=i + random.random()) for i in range(SIZE)]
    }

    def test_coerce_from_integer_to_integer(self):
        # no NA
        input_data = self.example_data["integers"]
        output_data = self.example_data["integers"]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # with NA
        input_data = self.example_data["integers"] + [None]
        output_data = self.example_data["integers"] + [None]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

    def test_coerce_from_integer_to_float(self):
        # no NA
        input_data = self.example_data["integers"]
        output_data = [float(e) for e in self.example_data["integers"]]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # with NA
        input_data = self.example_data["integers"] + [None]
        output_data = ([float(e) for e in self.example_data["integers"]] +
                       [None])
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_integer_to_complex(self):
        # no NA
        input_data = self.example_data["integers"]
        output_data = [complex(e, 0) for e in self.example_data["integers"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = self.example_data["integers"] + [None]
        output_data = ([complex(e, 0) for e in self.example_data["integers"]] +
                       [None])
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_integer_to_string(self):
        # no NA
        input_data = self.example_data["integers"]
        output_data = [str(e) for e in self.example_data["integers"]]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = self.example_data["integers"] + [None]
        output_data = [str(e) for e in self.example_data["integers"]] + [None]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_integer_to_boolean(self):
        # generic integers - no NA
        input_data = self.example_data["integers"]
        info_loss_test(self, pd.Series(input_data), bool)

        # generic integers - with NA
        input_data = self.example_data["integers"] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # integer boolean flags, [1, 0, 1, ...] - no NA
        input_data = [int(e) for e in self.example_data["booleans"]]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # integer boolean flags, [1, 0, 1, ...] - with NA
        input_data = [int(e) for e in self.example_data["booleans"]] + [None]
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

    def test_coerce_from_integer_to_datetime(self):
        # no NA
        input_data = self.example_data["integers"]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["integers"]]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # with NA
        input_data = self.example_data["integers"] + [None]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["integers"]] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_integer_to_timedelta(self):
        # no NA
        input_data = self.example_data["integers"]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["integers"]]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # with NA
        input_data = self.example_data["integers"] + [None]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["integers"]] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_integer_to_object(self):
        # no NA
        input_series = pd.Series(self.example_data["integers"])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_series = pd.Series(self.example_data["integers"] + [None])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_float_to_integer(self):
        # generic floats - no NA
        input_data = self.example_data["decimal floats"]
        info_loss_test(self, pd.Series(input_data), int)

        # generic floats - with NA
        input_data = self.example_data["decimal floats"] + [None]
        info_loss_test(self, pd.Series(input_data), int)

        # whole floats - no NA
        input_data = [float(e) for e in self.example_data["integers"]]
        output_data = self.example_data["integers"]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # whole floats - with NA
        input_data = [float(e) for e in self.example_data["integers"]] + [None]
        output_data = self.example_data["integers"] + [None]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

    def test_coerce_from_float_to_float(self):
        # no NA
        input_data = self.example_data["decimal floats"]
        output_data = self.example_data["decimal floats"]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # with NA
        input_data = self.example_data["decimal floats"] + [None]
        output_data = self.example_data["decimal floats"] + [None]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_float_to_complex(self):
        # no NA
        input_data = self.example_data["decimal floats"]
        output_data = [complex(e, 0)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = self.example_data["decimal floats"] + [None]
        output_data = [complex(e, 0)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_float_to_string(self):
        # no NA
        input_data = self.example_data["decimal floats"]
        output_data = [str(e) for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = self.example_data["decimal floats"] + [None]
        output_data = ([str(e) for e in self.example_data["decimal floats"]] +
                       [None])
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_float_to_boolean(self):
        # generic floats - no NA
        input_data = self.example_data["decimal floats"]
        info_loss_test(self, pd.Series(input_data), bool)

        # generic floats - with NA
        input_data = self.example_data["decimal floats"] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # whole float bool flags [1.0, 0.0, 1.0, ...] - no NA
        input_data = [float(e) for e in self.example_data["booleans"]]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # whole float bool flags [1.0, 0.0, 1.0, ...] - with NA
        input_data = [float(e) for e in self.example_data["booleans"]] + [None]
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # bool flags between 0 and 1 - no NA
        input_data = self.example_data["decimal floats (0, 1)"]
        info_loss_test(self, pd.Series(input_data), bool)

        # bool flags between 0 and 1 - with NA
        input_data = self.example_data["decimal floats (0, 1)"] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

    def test_coerce_from_float_to_datetime(self):
        # no NA
        input_data = self.example_data["decimal floats"]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # with NA
        input_data = self.example_data["decimal floats"] + [None]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_float_to_timedelta(self):
        # no NA
        input_data = self.example_data["decimal floats"]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # with NA
        input_data = self.example_data["decimal floats"] + [None]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_float_to_object(self):
        # no NA
        input_series = pd.Series(self.example_data["decimal floats"])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_series = pd.Series(self.example_data["decimal floats"] + [None])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_complex_to_integer(self):
        # imaginary complex - no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), int)

        # imaginary complex - with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), int)

        # real decimal complex - no NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), int)

        # real decimal complex - with NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), int)

        # real whole complex - no NA
        input_data = [complex(e, 0) for e in self.example_data["integers"]]
        output_data = self.example_data["integers"]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # real whole complex - with NA
        input_data = ([complex(e, 0) for e in self.example_data["integers"]] +
                      [None])
        output_data = self.example_data["integers"] + [None]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

    def test_coerce_from_complex_to_float(self):
        # imaginary complex - no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), float)

        # imaginary complex - with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), float)

        # real decimal complex - no NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]]
        output_data = self.example_data["decimal floats"]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # real decimal complex - with NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]] + [None]
        output_data = self.example_data["decimal floats"] + [None]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_complex_to_complex(self):
        # no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        output_data = [complex(e, e)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        output_data = [complex(e, e)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_complex_to_string(self):
        # no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        output_data = [str(complex(e, e))
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        output_data = [str(complex(e, e))
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_complex_to_boolean(self):
        # imaginary complex - no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # imaginary complex - with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # real decimal complex - no NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # real decimal complex - with NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # real whole complex - no NA
        input_data = [complex(e, 0)
                      for e in self.example_data["integers"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # real whole complex - with NA
        input_data = [complex(e, 0)
                      for e in self.example_data["integers"]] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # complex bool flag [complex(1, 0), complex(0, 0), ...] - no NA
        input_data = [complex(e, 0) for e in self.example_data["booleans"]]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # complex bool flag [complex(1, 0), complex(0, 0), ...] - with NA
        input_data = ([complex(e, 0) for e in self.example_data["booleans"]] +
                      [None])
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # bool flags between 0 and 1 - no NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats (0, 1)"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # bool flags between 0 and 1 - with NA
        input_data = ([complex(e, 0)
                      for e in self.example_data["decimal floats (0, 1)"]] +
                      [None])
        info_loss_test(self, pd.Series(input_data), bool)

    def test_coerce_from_complex_to_datetime(self):
        # imaginary complex - no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # imaginary complex - with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # real complex - no NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # real complex - with NA
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]] + [None]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_complex_to_timedelta(self):
        # imaginary complex - no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # imaginary complex - with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # real complex
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # real complex
        input_data = [complex(e, 0)
                      for e in self.example_data["decimal floats"]] + [None]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_complex_to_object(self):
        # no NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]]
        input_series = pd.Series(input_data)
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_data = [complex(e, e)
                      for e in self.example_data["decimal floats"]] + [None]
        input_series = pd.Series(input_data)
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_string_to_integer(self):
        # integer strings
        input_data = [str(e) for e in self.example_data["integers"]]
        output_data = self.example_data["integers"]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

    def test_coerce_from_string_to_float(self):
        # no NA
        input_data = [str(e) for e in self.example_data["decimal floats"]]
        output_data = self.example_data["decimal floats"]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # with NA
        input_data = ([str(e) for e in self.example_data["decimal floats"]] +
                      [None])
        output_data = self.example_data["decimal floats"] + [None]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_string_to_complex(self):
        # no NA
        input_data = [str(complex(e, e))
                      for e in self.example_data["decimal floats"]]
        output_data = [complex(e, e)
                       for e in self.example_data["decimal floats"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = [str(complex(e, e))
                      for e in self.example_data["decimal floats"]] + [None]
        output_data = [complex(e, e)
                       for e in self.example_data["decimal floats"]] + [None]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_string_to_string(self):
        # no NA
        input_data = self.example_data["character strings"]
        output_data = self.example_data["character strings"]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = self.example_data["character strings"] + [None]
        output_data = self.example_data["character strings"] + [None]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_string_to_boolean(self):
        # no NA
        input_data = [str(e) for e in self.example_data["booleans"]]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # with NA
        input_data = [str(e) for e in self.example_data["booleans"]] + [None]
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

    def test_coerce_from_string_to_datetime(self):
        # naive datetime strings - no NA
        input_data = [str(e)
                      for e in self.example_data["random naive datetimes"]]
        output_data = self.example_data["random naive datetimes"]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # naive datetime strings - with NA
        input_data = ([str(e)
                      for e in self.example_data["random naive datetimes"]] +
                      [None])
        output_data = self.example_data["random naive datetimes"] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # aware datetime strings - no NA
        input_data = [str(e) for e in self.example_data["random datetimes"]]
        output_data = self.example_data["random datetimes"]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # aware datetime strings - with NA
        input_data = ([str(e) for e in self.example_data["random datetimes"]] +
                      [None])
        output_data = self.example_data["random datetimes"] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # naive ISO 8601 strings - no NA
        input_data = [e.isoformat()
                      for e in self.example_data["random naive datetimes"]]
        output_data = self.example_data["random naive datetimes"]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # naive ISO 8601 strings - with NA
        input_data = ([e.isoformat()
                      for e in self.example_data["random naive datetimes"]] +
                      [None])
        output_data = self.example_data["random naive datetimes"] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # aware ISO 8601 strings - no NA
        input_data = [e.isoformat()
                      for e in self.example_data["random datetimes"]]
        output_data = self.example_data["random datetimes"]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # aware ISO 8601 strings - with NA
        input_data = [e.isoformat()
                      for e in self.example_data["random datetimes"]] + [None]
        output_data = self.example_data["random datetimes"] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_string_to_timedelta(self):
        # no NA
        input_data = [str(e) for e in self.example_data["random timedeltas"]]
        output_data = self.example_data["random timedeltas"]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # with NA
        input_data = ([str(e) for e in self.example_data["random timedeltas"]] +
                      [None])
        output_data = self.example_data["random timedeltas"] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_string_to_object(self):
        # no NA
        input_series = pd.Series(self.example_data["character strings"])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_series = pd.Series(self.example_data["character strings"] +
                                 [None])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_boolean_to_integer(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = [int(e) for e in self.example_data["booleans"]]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = [int(e) for e in self.example_data["booleans"]] + [None]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

    def test_coerce_from_boolean_to_float(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = [float(e) for e in self.example_data["booleans"]]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = [float(e) for e in self.example_data["booleans"]] + [None]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_boolean_to_complex(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = [complex(e, 0) for e in self.example_data["booleans"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = ([complex(e, 0) for e in self.example_data["booleans"]] +
                       [None])
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_boolean_to_string(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = [str(e) for e in self.example_data["booleans"]]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = [str(e) for e in self.example_data["booleans"]] + [None]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_boolean_to_boolean(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

    def test_coerce_from_boolean_to_datetime(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["booleans"]]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                       for e in self.example_data["booleans"]] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_boolean_to_timedelta(self):
        # no NA
        input_data = self.example_data["booleans"]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["booleans"]]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # with NA
        input_data = self.example_data["booleans"] + [None]
        output_data = [timedelta(seconds=e)
                       for e in self.example_data["booleans"]] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_boolean_to_object(self):
        # no NA
        input_series = pd.Series(self.example_data["booleans"])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_series = pd.Series(self.example_data["booleans"] + [None])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_datetime_to_integer(self):
        # whole timestamp datetimes - no NA
        input_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                      for e in self.example_data["integers"]]
        output_data = self.example_data["integers"]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # whole timestamp datetimes - with NA
        input_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                      for e in self.example_data["integers"]] + [None]
        output_data = self.example_data["integers"] + [None]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # random datetimes - no NA
        input_data = self.example_data["random datetimes"]
        info_loss_test(self, pd.Series(input_data), int)

        # random datetimes - with NA
        input_data = self.example_data["random datetimes"] + [None]
        info_loss_test(self, pd.Series(input_data), int)

    def test_coerce_from_datetime_to_float(self):
        # no NA
        input_data = self.example_data["random datetimes"]
        output_data = [e.timestamp()
                       for e in self.example_data["random datetimes"]]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random datetimes"] + [None]
        output_data = [e.timestamp()
                       for e in self.example_data["random datetimes"]] + [None]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_datetime_to_complex(self):
        # no NA
        input_data = self.example_data["random datetimes"]
        output_data = [complex(e.timestamp(), 0)
                       for e in self.example_data["random datetimes"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random datetimes"] + [None]
        output_data = [complex(e.timestamp(), 0)
                       for e in self.example_data["random datetimes"]] + [None]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_datetime_to_string(self):
        # no NA
        input_data = self.example_data["random datetimes"]
        output_data = [e.isoformat()
                       for e in self.example_data["random datetimes"]]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random datetimes"] + [None]
        output_data = [e.isoformat()
                       for e in self.example_data["random datetimes"]] + [None]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_datetime_to_boolean(self):
        # datetime bool flag - no NA
        input_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                      for e in self.example_data["booleans"]]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # datetime bool flag - with NA
        input_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                      for e in self.example_data["booleans"]] + [None]
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))
        
        # random datetimes - no NA
        input_data = self.example_data["random datetimes"]
        info_loss_test(self, pd.Series(input_data), bool)

        # random datetimes - with NA
        input_data = self.example_data["random datetimes"] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

        # random datetimes between 0 and 1 - no NA
        input_data = [datetime.fromtimestamp(e, tz=timezone.utc)
                      for e in self.example_data["decimal floats (0, 1)"]]
        info_loss_test(self, pd.Series(input_data), bool)

        # random datetimes between 0 and 1 - with NA
        input_data = ([datetime.fromtimestamp(e, tz=timezone.utc)
                      for e in self.example_data["decimal floats (0, 1)"]] +
                      [None])
        info_loss_test(self, pd.Series(input_data), bool)

    def test_coerce_from_datetime_to_datetime(self):
        # no NA
        input_data = self.example_data["random datetimes"]
        output_data = self.example_data["random datetimes"]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random datetimes"] + [None]
        output_data = self.example_data["random datetimes"] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_datetime_to_timedelta(self):
        # no NA
        input_data = self.example_data["random datetimes"]
        output_data = [timedelta(seconds=e.timestamp())
                       for e in self.example_data["random datetimes"]]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random datetimes"] + [None]
        output_data = [timedelta(seconds=e.timestamp())
                       for e in self.example_data["random datetimes"]] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_datetime_to_object(self):
        # no NA
        input_series = pd.Series(self.example_data["random datetimes"])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_series = pd.Series(self.example_data["random datetimes"] + [None])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_timedelta_to_integer(self):
        # whole timedelta - no NA
        input_data = [timedelta(seconds=e)
                      for e in self.example_data["integers"]]
        output_data = self.example_data["integers"]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # whole timedelta - with NA
        input_data = [timedelta(seconds=e)
                      for e in self.example_data["integers"]] + [None]
        output_data = self.example_data["integers"] + [None]
        coercion_test(pd.Series(input_data), int, pd.Series(output_data))

        # random timedelta - no NA
        input_data = self.example_data["random timedeltas"]
        info_loss_test(self, pd.Series(input_data), int)

        # random timedelta - with NA
        input_data = self.example_data["random timedeltas"] + [None]
        info_loss_test(self, pd.Series(input_data), int)

    def test_coerce_from_timedelta_to_float(self):
        # no NA
        input_data = self.example_data["random timedeltas"]
        output_data = [e.total_seconds()
                       for e in self.example_data["random timedeltas"]]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random timedeltas"] + [None]
        output_data = [e.total_seconds()
                       for e in self.example_data["random timedeltas"]] + [None]
        coercion_test(pd.Series(input_data), float, pd.Series(output_data))

    def test_coerce_from_timedelta_to_complex(self):
        # no NA
        input_data = self.example_data["random timedeltas"]
        output_data = [complex(e.total_seconds(), 0)
                       for e in self.example_data["random timedeltas"]]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random timedeltas"] + [None]
        output_data = [complex(e.total_seconds(), 0)
                       for e in self.example_data["random timedeltas"]] + [None]
        coercion_test(pd.Series(input_data), complex, pd.Series(output_data))

    def test_coerce_from_timedelta_to_string(self):
        # no NA
        input_data = self.example_data["random timedeltas"]
        output_data = [str(pd.Timedelta(e))
                       for e in self.example_data["random timedeltas"]]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random timedeltas"] + [None]
        output_data = [str(pd.Timedelta(e))
                       for e in self.example_data["random timedeltas"]] + [None]
        coercion_test(pd.Series(input_data), str, pd.Series(output_data))

    def test_coerce_from_timedelta_to_boolean(self):
        # timedelta bool flags - no NA
        input_data = [timedelta(seconds=e)
                      for e in self.example_data["booleans"]]
        output_data = self.example_data["booleans"]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # timedelta bool flags - with NA
        input_data = [timedelta(seconds=e)
                      for e in self.example_data["booleans"]] + [None]
        output_data = self.example_data["booleans"] + [None]
        coercion_test(pd.Series(input_data), bool, pd.Series(output_data))

        # random timedeltas - no NA
        input_data = self.example_data["random timedeltas"]
        info_loss_test(self, pd.Series(input_data), bool)

        # random timedeltas - with NA
        input_data = self.example_data["random timedeltas"] + [None]
        info_loss_test(self, pd.Series(input_data), bool)

    def test_coerce_from_timedelta_to_datetime(self):
        # no NA
        input_data = self.example_data["random timedeltas"]
        output_data = [datetime.fromtimestamp(e.total_seconds(),
                                              tz=timezone.utc)
                       for e in self.example_data["random timedeltas"]]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random timedeltas"] + [None]
        output_data = [datetime.fromtimestamp(e.total_seconds(),
                                              tz=timezone.utc)
                       for e in self.example_data["random timedeltas"]] + [None]
        coercion_test(pd.Series(input_data), datetime, pd.Series(output_data))

    def test_coerce_from_timedelta_to_timedelta(self):
        # no NA
        input_data = self.example_data["random timedeltas"]
        output_data = self.example_data["random timedeltas"]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

        # with NA
        input_data = self.example_data["random timedeltas"] + [None]
        output_data = self.example_data["random timedeltas"] + [None]
        coercion_test(pd.Series(input_data), timedelta, pd.Series(output_data))

    def test_coerce_from_timedelta_to_object(self):
        # no NA
        input_series = pd.Series(self.example_data["random timedeltas"])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

        # with NA
        input_series = pd.Series(self.example_data["random timedeltas"] +
                                 [None])
        output_series = input_series.astype(np.dtype("O"))
        coercion_test(input_series, object, output_series)

    def test_coerce_from_object_to_integer(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_float(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_complex(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_string(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_boolean(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_datetime(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_timedelta(self):
        pass
        # raise NotImplementedError()

    def test_coerce_from_object_to_object(self):
        pass
        # raise NotImplementedError()

    def test_coerce_dtypes_returns_copy(self):
        # Series
        column = pd.Series(self.example_data["integers"])
        result = coerce_dtypes(column, float)
        self.assertNotEqual(id(column), id(result))

        # DataFrame
        df = pd.DataFrame({TEST_COLUMN_NAME: self.example_data["integers"]})
        result = coerce_dtypes(df, {TEST_COLUMN_NAME: float})
        self.assertNotEqual(id(df), id(result))



    # def test_check_dtypes_datetime_mixed_timezones(self):
    #     test_df = pd.DataFrame({"timestamp": [datetime.now(timezone.utc),
    #                                           datetime.now()]})
    #     self.assertTrue(check_dtypes(test_df, timestamp=datetime))

    # def test_coerce_dtypes_kwargless_error(self):
    #     atomics = [t.__name__ if isinstance(t, type) else str(t)
    #                for t in AVAILABLE_DTYPES]
    #     err_msg = (f"[datatube.stats.coerce_dtypes] `coerce_dtypes` must be "
    #                f"invoked with at least one keyword argument mapping a "
    #                f"column in `data` to an atomic data type: "
    #                f"{tuple(atomics)}")
    #     with self.assertRaises(RuntimeError) as err:
    #         coerce_dtypes(self.no_na)
    #     self.assertEqual(str(err.exception), err_msg)

    # def test_coerce_dtypes_kwargs_no_na_no_errors(self):
    #     for col_name, expected in self.conversions.items():
    #         for conv in expected:
    #             coerce_dtypes(self.no_na, **{col_name: conv})

    # def test_coerce_dtypes_kwargs_with_na_no_errors(self):
    #     for col_name, expected in self.conversions.items():
    #         for conv in expected:
    #             coerce_dtypes(self.with_na, **{col_name: conv})

    # def test_coerce_dtypes_matches_check_dtypes(self):
    #     # This does not work for coercion to <class 'object'> because of the
    #     # automatic convert_dtypes() step of check_dtypes.  These columns will
    #     # always be better represented by some other data type, unless it was
    #     # an object to begin with.
    #     for col_name, expected in self.conversions.items():
    #         for conv in expected:
    #             result = coerce_dtypes(self.no_na, **{col_name: conv})
    #             na_result = coerce_dtypes(self.with_na, **{col_name: conv})
    #             check_result = check_dtypes(result, **{col_name: conv})
    #             check_na_result = check_dtypes(na_result, **{col_name: conv})
    #             if conv != object:
    #                 try:
    #                     self.assertTrue(check_result)
    #                     self.assertTrue(check_na_result)
    #                 except AssertionError as exc:
    #                     err_msg = (f"col_name: {repr(col_name)}, typespec: "
    #                             f"{conv}, expected: {expected}")
    #                     raise AssertionError(err_msg) from exc

    # def test_coerce_dtypes_returns_copy(self):
    #     result = coerce_dtypes(self.with_na, a=float)
    #     self.assertNotEqual(list(result.dtypes), list(self.with_na.dtypes))

    # def test_coerce_dtypes_datetime_preserves_timezone(self):
    #     raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()