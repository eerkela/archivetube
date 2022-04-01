from datetime import datetime, timedelta, timezone
import random
from tabnanny import check
import unittest

import pandas as pd
import pytz

if __name__ == "__main__":
    from pathlib import Path
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datatube.dtype import check_dtypes


unittest.TestCase.maxDiff = None


class CheckDtypeTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        class TestObj:
            pass
        
        random.seed(12345)
        size = 3
        cls.integers = {
            "integers":
                [-1 * size // 2 + i + 1 for i in range(size)],
            "integer strings":
                [str(-1 * size // 2 + i + 1) for i in range(size)],
            "whole floats":
                [-1 * size // 2 + i + 1.0 for i in range(size)],
            "whole float strings":
                [str(-1 * size // 2 + i + 1.0) for i in range(size)],
            "real whole complex":
                [complex(-1 * size // 2 + i + 1, 0) for i in range(size)],
            "real whole complex strings":
                [str(complex(-1 * size // 2 + i + 1, 0)) for i in range(size)],
        }
        cls.floats = {
            "whole floats":
                [-1 * size // 2 + i + 1.0 for i in range(size)],
            "whole float strings":
                [str(-1 * size // 2 + i + 1.0) for i in range(size)],
            "decimal floats":
                [-1 * size // 2 + i + 1 + random.random() for i in range(size)],
            "decimal float strings":
                [str(-1 * size // 2 + i + 1 + random.random())
                 for i in range(size)],
            "real decimal complex":
                [complex(-1 * size // 2 + i + 1 + random.random(), 0)
                 for i in range(size)],
            "real decimal complex strings":
                [str(complex(-1 * size // 2 + i + 1 + random.random(), 0))
                 for i in range(size)]
        }
        cls.complex = {
            "real whole complex":
                [complex(-1 * size // 2 + i + 1, 0) for i in range(size)],
            "real whole complex strings":
                [str(complex(-1 * size // 2 + i + 1, 0)) for i in range(size)],
            "real decimal complex":
                [complex(-1 * size // 2 + i + 1 + random.random(), 0)
                 for i in range(size)],
            "real decimal complex strings":
                [str(complex(-1 * size // 2 + i + 1 + random.random(), 0))
                 for i in range(size)],
            "imaginary complex":
                [complex(-1 * size // 2 + i + 1 + random.random(),
                         -1 * size // 2 + i + 1 + random.random())
                 for i in range(size)],
            "imaginary complex strings":
                [str(complex(-1 * size // 2 + i + 1 + random.random(),
                             -1 * size // 2 + i + 1 + random.random()))
                 for i in range(size)]
        }
        cls.strings = {
            "integer strings":
                [str(-1 * size // 2 + i + 1) for i in range(size)],
            "whole float strings":
                [str(-1 * size // 2 + i + 1.0) for i in range(size)],
            "decimal float strings":
                [str(-1 * size // 2 + i + 1 + random.random())
                 for i in range(size)],
            "real whole complex strings":
                [str(complex(-1 * size // 2 + i + 1, 0)) for i in range(size)],
            "real decimal complex strings":
                [str(complex(-1 * size // 2 + i + 1 + random.random(), 0))
                 for i in range(size)],
            "imaginary complex strings":
                [str(complex(-1 * size // 2 + i + 1 + random.random(),
                             -1 * size // 2 + i + 1 + random.random()))
                 for i in range(size)],
            "character strings":
                [chr(i % 26 + ord("a")) for i in range(size)],
            "boolean strings":
                [str(bool((i + 1) % 2)) for i in range(size)],
            "aware datetime strings":
                [str(datetime.fromtimestamp(i, tz=timezone.utc))
                 for i in range(size)],
            "aware ISO 8601 strings":
                [datetime.fromtimestamp(i, tz=timezone.utc).isoformat()
                 for i in range(size)],
            "naive datetime strings":
                [str(datetime.fromtimestamp(i)) for i in range(size)],
            "naive ISO 8601 strings":
                [datetime.fromtimestamp(i).isoformat() for i in range(size)],
            "aware/naive datetime strings":
                [str(datetime.fromtimestamp(i, tz=timezone.utc)) if i % 2
                 else str(datetime.fromtimestamp(i)) for i in range(size)],
            "aware/naive ISO 8601 strings":
                [datetime.fromtimestamp(i, tz=timezone.utc).isoformat() if i % 2
                 else datetime.fromtimestamp(i).isoformat()
                 for i in range(size)],
            "mixed timezone datetime strings":
                [str(
                    datetime.fromtimestamp(
                        i,
                        tz=pytz.timezone(
                            pytz.all_timezones[i % len(pytz.all_timezones)]
                        )
                    )
                 ) for i in range(size)],
            "mixed timezone ISO 8601 strings":
                [datetime.fromtimestamp(
                    i,
                    tz=pytz.timezone(
                        pytz.all_timezones[i % len(pytz.all_timezones)]
                    )
                ).isoformat() for i in range(size)],
            "timedelta strings":
                [str(timedelta(seconds=i + 1)) for i in range(size)],
            "pd.Timedelta strings":
                [str(pd.Timedelta(timedelta(seconds=i + 1)))
                 for i in range(size)]
        }
        cls.booleans = {
            "booleans":
                [bool((i + 1) % 2) for i in range(size)],
            "boolean strings":
                [str(bool((i + 1) % 2)) for i in range(size)],
            "integer bool flags":
                [(i + 1) % 2 for i in range(size)],
            "integer bool flag strings":
                [str((i + 1) % 2) for i in range(size)],
            "float bool flags":
                [(i + 1.0) % 2 for i in range(size)],
            "float bool flag strings":
                [str((i + 1) % 2) for i in range(size)],
            "complex bool flags":
                [complex((i + 1) % 2) for i in range(size)],
            "complex bool flag strings":
                [str(complex((i + 1) % 2)) for i in range(size)]
        }
        cls.datetimes = {
            "aware datetimes":
                [datetime.fromtimestamp(i, tz=timezone.utc)
                 for i in range(size)],
            "aware datetime strings":
                [str(datetime.fromtimestamp(i, tz=timezone.utc))
                 for i in range(size)],
            "aware ISO 8601 strings":
                [datetime.fromtimestamp(i, tz=timezone.utc).isoformat()
                 for i in range(size)],
            "naive datetimes":
                [datetime.fromtimestamp(i) for i in range(size)],
            "naive datetime strings":
                [str(datetime.fromtimestamp(i)) for i in range(size)],
            "naive ISO 8601 strings":
                [datetime.fromtimestamp(i).isoformat() for i in range(size)],
            "aware/naive datetimes":
                [datetime.fromtimestamp(i, tz=timezone.utc) if i % 2
                 else datetime.fromtimestamp(i) for i in range(size)],
            "aware/naive datetime strings":
                [str(datetime.fromtimestamp(i, tz=timezone.utc)) if i % 2
                 else str(datetime.fromtimestamp(i)) for i in range(size)],
            "aware/naive ISO 8601 strings":
                [datetime.fromtimestamp(i, tz=timezone.utc).isoformat() if i % 2
                 else datetime.fromtimestamp(i).isoformat()
                 for i in range(size)],
            "mixed timezone datetimes":
                [datetime.fromtimestamp(
                    i,
                    tz = pytz.timezone(
                        pytz.all_timezones[i % len(pytz.all_timezones)]
                    )
                ) for i in range(size)],
            "mixed timezone datetime strings":
                [str(
                    datetime.fromtimestamp(
                        i,
                        tz=pytz.timezone(
                            pytz.all_timezones[i % len(pytz.all_timezones)]
                        )
                    )
                 ) for i in range(size)],
            "mixed timezone ISO 8601 strings":
                [datetime.fromtimestamp(
                    i,
                    tz=pytz.timezone(
                        pytz.all_timezones[i % len(pytz.all_timezones)]
                    )
                ).isoformat() for i in range(size)],
        }
        cls.timedeltas = {
            "timedeltas":
                [timedelta(seconds=i + 1) for i in range(size)],
            "timedelta strings":
                [str(timedelta(seconds=i + 1)) for i in range(size)],
            "pd.Timedelta strings":
                [str(pd.Timedelta(timedelta(seconds=i + 1)))
                 for i in range(size)]
        }
        cls.objects = {
            "Nones":
                [None for _ in range(size)],
            "custom objects":
                [TestObj() for _ in range(size)]
        }
        cls.all_data = {**cls.integers, **cls.floats, **cls.complex,
                        **cls.strings, **cls.booleans, **cls.datetimes,
                        **cls.timedeltas, **cls.objects}

    def test_check_dtypes_series_no_typespec_no_na(self):
        type_lookup = {
            int: self.integers,
            float: self.floats,
            complex: self.complex,
            str: self.strings,
            bool: self.booleans,
            datetime: self.booleans,
            timedelta: self.timedeltas,
            object: self.objects
        }
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series)
            lookup = [typespec for typespec, subset in type_lookup.items()
                      if col_name in subset]
            expected = tuple(lookup)
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}]) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_dtypes_series_no_typespec_with_na(self):
        type_lookup = {
            int: self.integers,
            float: self.floats,
            complex: self.complex,
            str: self.strings,
            bool: self.booleans,
            datetime: self.booleans,
            timedelta: self.timedeltas,
            object: self.objects
        }
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series)
            lookup = [typespec for typespec, subset in type_lookup.items()
                      if col_name in subset]
            expected = tuple(lookup)
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}]) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_dtypes_df_no_typespec_no_na(self):
        type_lookup = {
            int: self.integers,
            float: self.floats,
            complex: self.complex,
            str: self.strings,
            bool: self.booleans,
            datetime: self.booleans,
            timedelta: self.timedeltas,
            object: self.objects
        }
        df = pd.DataFrame(self.all_data)
        result = check_dtypes(df)
        expected = {}
        for col_name in df.columns:
            lookup = [typespec for typespec, subset in type_lookup.items()
                      if col_name in subset]
            expected[col_name] = tuple(lookup)
        self.assertEqual(result, expected)

    def test_check_dtypes_df_no_typespec_with_na(self):
        type_lookup = {
            int: self.integers,
            float: self.floats,
            complex: self.complex,
            str: self.strings,
            bool: self.booleans,
            datetime: self.booleans,
            timedelta: self.timedeltas,
            object: self.objects
        }
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        result = check_dtypes(df)
        expected = {}
        for col_name in df.columns:
            lookup = [typespec for typespec, subset in type_lookup.items()
                      if col_name in subset]
            expected[col_name] = tuple(lookup)
        self.assertEqual(result, expected)

    def test_check_integers_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, int)
            expected = col_name in self.integers
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], int) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_integers_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, int)
            expected = col_name in self.integers
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], int) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_integers_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: int})
            expected = col_name in self.integers
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: int}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_integers_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: int})
            expected = col_name in self.integers
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: int}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_floats_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, float)
            expected = col_name in self.floats
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], float) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_floats_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, float)
            expected = col_name in self.floats
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], float) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_floats_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: float})
            expected = col_name in self.floats
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: float}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_floats_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: float})
            expected = col_name in self.floats
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: float}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_complex_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, complex)
            expected = col_name in self.complex
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], complex) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_complex_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, complex)
            expected = col_name in self.complex
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], complex) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_complex_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: complex})
            expected = col_name in self.complex
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: complex}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_complex_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: complex})
            expected = col_name in self.complex
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: complex}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_strings_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, str)
            expected = col_name in self.strings
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], str) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_strings_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, str)
            expected = col_name in self.strings
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], str) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_strings_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: str})
            expected = col_name in self.strings
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: str}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_strings_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: str})
            expected = col_name in self.strings
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: str}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_booleans_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, bool)
            expected = col_name in self.booleans
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], bool) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_booleans_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, bool)
            expected = col_name in self.booleans
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], bool) "
                           f"!= {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_booleans_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: bool})
            expected = col_name in self.booleans
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: bool}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_booleans_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: bool})
            expected = col_name in self.booleans
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: bool}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_datetimes_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, datetime)
            expected = col_name in self.datetimes
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], "
                           f"datetime) != {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_datetimes_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, datetime)
            expected = col_name in self.datetimes
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], "
                           f"datetime) != {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_datetimes_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: datetime})
            expected = col_name in self.datetimes
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: datetime}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_datetimes_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: datetime})
            expected = col_name in self.datetimes
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: datetime}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_timedeltas_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, timedelta)
            expected = col_name in self.timedeltas
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], "
                           f"timedelta) != {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_timedeltas_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, timedelta)
            expected = col_name in self.timedeltas
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], "
                           f"timedelta) != {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_timedeltas_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: timedelta})
            expected = col_name in self.timedeltas
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: timedelta}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_timedeltas_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: timedelta})
            expected = col_name in self.timedeltas
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: timedelta}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_objects_series_no_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data)
            result = check_dtypes(series, object)
            expected = col_name in self.objects
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], "
                           f"object) != {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_objects_series_with_na(self):
        failed = []
        for col_name, data in self.all_data.items():
            series = pd.Series(data + [None])
            result = check_dtypes(series, object)
            expected = col_name in self.objects
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(all_data[{repr(col_name)}], "
                           f"object) != {expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_objects_df_no_na(self):
        df = pd.DataFrame(self.all_data)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: object})
            expected = col_name in self.objects
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: object}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")

    def test_check_object_df_with_na(self):
        with_na = {k: v + [None] for k, v in self.all_data.items()}
        df = pd.DataFrame(with_na)
        failed = []
        for col_name in df.columns:
            result = check_dtypes(df, {col_name: object})
            expected = col_name in self.objects
            try:
                self.assertEqual(result, expected)
            except AssertionError:
                context = (f"check_dtypes(df, {{{col_name}: object}}) != "
                           f"{expected}")
                failed.append(context)
        if len(failed) > 0:
            joined = "\n\t".join(failed)
            raise AssertionError(f"{len(failed)} failed checks:\n\t{joined}")


class CheckDtypeErrorTests(unittest.TestCase):

    def test_check_dtypes_series_bad_typespec_type(self):
        series = pd.Series([1, 2, 3])
        with self.assertRaises(TypeError) as err:
            check_dtypes(series, {"shouldn't be a dictionary": int})
        err_msg = ("[datatube.dtype.check_dtypes] when used on a series, "
                   "`typespec` must be an atomic data type or None (received "
                   "object of type: <class 'dict'>)")
        self.assertEqual(str(err.exception), err_msg)

    def test_check_dtypes_df_bad_typespec_type(self):
        df = pd.DataFrame({"column": [1, 2, 3]})
        with self.assertRaises(TypeError) as err:
            check_dtypes(df, "bad typespec")
        err_msg = ("[datatube.dtype.check_dtypes] when used on a dataframe, "
                   "`typespec` must be an atomic data type, a map of column "
                   "names and atomic data types, or None (received object of "
                   "type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

    def test_check_dtypes_bad_data_type(self):
        data = [1, 2, 3]
        with self.assertRaises(TypeError) as err:
            check_dtypes(data, int)
        err_msg = ("[datatube.dtype.check_dtypes] `data` must be either a "
                    "pandas.Series or pandas.DataFrame instance (received "
                    "object of type: <class 'list'>)")
        self.assertEqual(str(err.exception), err_msg)



if __name__ == "__main__":
    unittest.main()