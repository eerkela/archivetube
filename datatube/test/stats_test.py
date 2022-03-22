from datetime import datetime, timedelta, timezone
from pathlib import Path
import random
from sre_constants import ASSERT_NOT
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datatube import ROOT_DIR
from datatube.stats import AVAILABLE_DTYPES, Stats, check_dtypes, coerce_dtypes


TEST_PROPERTIES = {
    "video_id": "test_video_",
    "timestamp": datetime.now(),
    "views": 100,
    "rating": 4.25,
    "likes": 34,
    "dislikes": 6
}
EXPECTED_TYPES = {
    "video_id": str,
    "timestamp": datetime,
    "views": int,
    "rating": "numeric",
    "likes": int,
    "dislikes": int
}


unittest.TestCase.maxDiff = None


class DTypeTests(unittest.TestCase):

    class TestObj:
        pass

    no_na = pd.DataFrame({"a": [1],  # integer
                          "b": [2.1],  # float
                          "c": [complex(1, 0.5)],  # complex
                          "d": ["abc"],  # string
                          "e": [True],  # bool
                          "f": [datetime.now(timezone.utc)],  # datetime
                          "g": [timedelta(seconds=10)],  # timedelta
                          "h": [None],  # object
                          "i": [TestObj()]})  # object
    with_na = pd.DataFrame({"a": [1, None],
                            "b": [2.1, None],
                            "c": [complex(1, 0.5), None],
                            "d": ["abc", None],
                            "e": [True, None],
                            "f": [datetime.now(timezone.utc), None],
                            "g": [timedelta(seconds=10), None],
                            "h": [None, None],
                            "i": [TestObj(), None]})
    expected_types = {  # columns are expected to be of the following types:
        "a": int,
        "b": float,
        "c": complex,
        "d": str,
        "e": bool,
        "f": datetime,
        "g": timedelta,
        "h": object,
        "i": object
    }
    conversions = {  # columns can be converted to following types:
        "a": (int, float, complex, str, object, datetime),
        "b": (float, complex, str, object, datetime),
        "c": (complex, str, object, datetime),
        "d": (str, object),
        "e": (bool, str, object),
        "f": (datetime, str, object),
        "g": (timedelta, str, object),
        "h": (object, int, float, complex, bool, str, datetime, timedelta),
        "i": (object, str)
    }

    def test_check_dtypes_kwargless_no_na(self):
        result = check_dtypes(self.no_na)
        self.assertEqual(result, self.expected_types)

    def test_check_dtypes_kwargless_with_na(self):
        result = check_dtypes(self.with_na)
        self.assertEqual(result, self.expected_types)

    def test_check_dtypes_kwargs_no_na(self):
        # loop through available types, return True iff type matches
        # self.expected_types[col_name]
        for col_name, expected in self.expected_types.items():
            for typespec in AVAILABLE_DTYPES:
                result = check_dtypes(self.no_na, **{col_name: typespec})
                try:
                    self.assertEqual(result, typespec == expected)
                except AssertionError as exc:  # add context
                    err_msg = (f"col_name: {repr(col_name)}, typespec: "
                               f"{typespec}, expected: {expected}")
                    raise AssertionError(err_msg) from exc

    def test_check_dtypes_kwargs_with_na(self):
        # loop through available types, return True iff type matches
        # self.expected_types[col_name]
        for col_name, expected in self.expected_types.items():
            for typespec in AVAILABLE_DTYPES:
                try:
                    result = check_dtypes(self.with_na, **{col_name: typespec})
                    self.assertEqual(result, typespec == expected)
                except AssertionError as exc:  # add context
                    err_msg = (f"col_name: {repr(col_name)}, typespec: "
                               f"{typespec}, expected: {expected}")
                    raise AssertionError(err_msg) from exc

    def test_check_dtypes_multiple_kwargs_no_na(self):
        all_dtypes = tuple(AVAILABLE_DTYPES)
        for col_name in self.expected_types:
            result = check_dtypes(self.no_na, **{col_name: all_dtypes})
            self.assertTrue(result)

    def test_check_dtypes_multiple_kwargs_with_na(self):
        all_dtypes = tuple(AVAILABLE_DTYPES)
        for col_name in self.expected_types:
            result = check_dtypes(self.with_na, **{col_name: all_dtypes})
            self.assertTrue(result)

    def test_coerce_dtypes_kwargless_error(self):
        atomics = [t.__name__ if isinstance(t, type) else str(t)
                   for t in AVAILABLE_DTYPES]
        err_msg = (f"[datatube.stats.coerce_dtypes] `coerce_dtypes` must be "
                   f"invoked with at least one keyword argument mapping a "
                   f"column in `data` to an atomic data type: "
                   f"{tuple(atomics)}")
        with self.assertRaises(RuntimeError) as err:
            coerce_dtypes(self.no_na)
        self.assertEqual(str(err.exception), err_msg)

    def test_coerce_dtypes_kwargs_no_na(self):
        for col_name, expected in self.conversions.items():
            for conv in expected:
                coerce_dtypes(self.no_na, **{col_name: conv})

    def test_coerce_dtypes_kwargs_with_na(self):
        for col_name, expected in self.conversions.items():
            for conv in expected:
                coerce_dtypes(self.with_na, **{col_name: conv})

    def test_coerce_dtypes_matches_check_dtypes(self):
        # This does not work for coercion to <class 'object'> because of the
        # automatic convert_dtypes() step of check_dtypes.  These columns will
        # always be better represented by some other data type, unless it was
        # an object to begin with.
        for col_name, expected in self.conversions.items():
            for conv in expected:
                result = coerce_dtypes(self.no_na, **{col_name: conv})
                na_result = coerce_dtypes(self.with_na, **{col_name: conv})
                check_result = check_dtypes(result, **{col_name: conv})
                check_na_result = check_dtypes(na_result, **{col_name: conv})
                if conv != object:
                    try:
                        self.assertTrue(check_result)
                        self.assertTrue(check_na_result)
                    except AssertionError as exc:
                        err_msg = (f"col_name: {repr(col_name)}, typespec: "
                                f"{conv}, expected: {expected}")
                        raise AssertionError(err_msg) from exc

    def test_coerce_dtypes_returns_copy(self):
        result = coerce_dtypes(self.with_na, a=float)
        self.assertNotEqual(list(result.dtypes), list(self.with_na.dtypes))


# class StatsInitTests(unittest.TestCase):

#     def test_no_input(self):
#         stats = Stats()
#         expected_cols = ("video_id", "timestamp", "views", "rating", "likes",
#                          "dislikes")
#         self.assertEqual(tuple(stats.data.columns), expected_cols)
#         # check dtypes
#         self.assertEqual(len(stats.data), 0)

#     def test_single_video_good_input(self):
#         test_data = pd.DataFrame({
#             "video_id": ["video_id_01", "video_id_01"],
#             "timestamp": [datetime(2020, 1, 1, tzinfo=timezone.utc),
#                           datetime(2020, 1, 2, tzinfo=timezone.utc)],
#             "views": [100, 120],
#             "rating": [4.75, 4.58333],
#             "likes": [19, 22],
#             "dislikes": [1, 2]
#         })
#         stats = Stats(test_data)
#         assert_frame_equal(stats.data, test_data)

#     def test_multiple_videos_good_input(self):
#         test_df = pd.DataFrame({
#             "video_id": ["video_id_01", "video_id_02"],
#             "timestamp": [datetime(2020, 1, 1, tzinfo=timezone.utc),
#                           datetime(2020, 1, 2, tzinfo=timezone.utc)],
#             "views": [100, 120],
#             "rating": [4.75, 4.58333],
#             "likes": [19, 22],
#             "dislikes": [1, 2]
#         })

#     def test_duplicate_rows(self):
#         raise NotImplementedError()

#     def test_duplicate_id_and_timestamp(self):
#         raise NotImplementedError()

#     def test_bad_dtype(self):
#         raise NotImplementedError()

#     def test_missing_column(self):
#         raise NotImplementedError()

#     def test_extra_column(self):
#         raise NotImplementedError()

#     def test_na(self):
#         raise NotImplementedError()

#     def test_na_in_required_column(self):
#         raise NotImplementedError()



# class BasicStatsTests(unittest.TestCase):

#     csv_path = Path(ROOT_DIR, "datatube", "test", "test_data", "test_stats.csv")

#     # def test_raw_init(self):
#     #     # pre-existing df
#     #     df = pd.DataFrame(TEST_PROPERTIES, index=[0])
#     #     s = Stats(df)
#     #     assert_frame_equal(s.data, coerce_dtypes(df, **EXPECTED_TYPES))

#     #     # no input
#     #     df = pd.DataFrame(dict.fromkeys(list(TEST_PROPERTIES), []))
#     #     s = Stats()
#     #     assert_frame_equal(s.data, coerce_dtypes(df, **EXPECTED_TYPES))

#     #     # empty input
#     #     df = pd.DataFrame

#     #     # df columns out of order
#     #     keys = list(TEST_PROPERTIES.keys())
#     #     random.seed(123)  # guarantees a swap
#     #     random.shuffle(keys)
#     #     df = pd.DataFrame({k: TEST_PROPERTIES[k] for k in keys}, index=[0])
#     #     s = Stats(df)
#     #     expected = pd.DataFrame(TEST_PROPERTIES, index=[0])  # original order
#     #     assert_frame_equal(s.data, coerce_dtypes(expected, **EXPECTED_TYPES))

#     def test_add_row(self):
#         s = Stats()
#         s.add_row(**TEST_PROPERTIES)
#         df = pd.DataFrame(TEST_PROPERTIES, index=[0])
#         assert_frame_equal(s.data, coerce_dtypes(df, **EXPECTED_TYPES))

#     def test_add_row_bad_video_id(self):
#         raise NotImplementedError()

#     def test_add_row_bad_timestamp(self):
#         raise NotImplementedError()


# class StatsCSVTests(unittest.TestCase):

#     def test_to_and_from_csv(self):
#         s = Stats()
#         s.add_row(**TEST_PROPERTIES)
#         self.csv_path.unlink(missing_ok=True)

#         # all video_ids
#         s.to_csv(self.csv_path)
#         self.assertTrue(self.csv_path.exists())
#         result = coerce_dtypes(pd.read_csv(self.csv_path), **EXPECTED_TYPES)
#         assert_frame_equal(s.data, result)

#         # a specific video_id
#         s.add_row(video_id="differentId", timestamp=datetime.now(), views=50,
#                   rating=3.4)
#         self.assertTrue(len(s.data) > 1)  # append actually worked
#         self.csv_path.unlink()
#         s.to_csv(self.csv_path, TEST_PROPERTIES["video_id"])  # save to csv
#         result = coerce_dtypes(pd.read_csv(self.csv_path), **EXPECTED_TYPES)
#         subset = s.data[s.data["video_id"] == TEST_PROPERTIES["video_id"]]
#         subset = subset.reset_index(drop=True)
#         assert_frame_equal(subset, result)

#         # from_csv
#         s = Stats.from_csv(self.csv_path)
#         expected = coerce_dtypes(pd.DataFrame(TEST_PROPERTIES, index=[0]),
#                                  **EXPECTED_TYPES)
#         assert_frame_equal(s.data, expected)


# class StatsErrorTests(unittest.TestCase):

#     def test_raw_init_errors(self):
#         # bad arg type
#         with self.assertRaises(TypeError) as err:
#             Stats(123)
#         err_msg = ("[datatube.stats.Stats.__init__] `data` must be a pandas.DataFrame object "
#                    "(received object of type: <class 'int'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # extra column
#         df = pd.DataFrame({**TEST_PROPERTIES, "extra_column": 0}, index=[0])
#         with self.assertRaises(ValueError) as err:
#             Stats(df)
#         err_msg = ("[datatube.stats.Stats.__init__] columns of `data` do not match expected "
#                    "(extra columns: {'extra_column'})")
#         self.assertEqual(str(err.exception), err_msg)

#         # missing column
#         missing_column = {k: v for k, v in TEST_PROPERTIES.items()
#                           if k != "views"}
#         df = pd.DataFrame(missing_column, index=[0])
#         with self.assertRaises(ValueError) as err:
#             Stats(df)
#         err_msg = ("[datatube.stats.Stats.__init__] columns of `data` do not match expected "
#                    "(missing columns: {'views'})")
#         self.assertEqual(str(err.exception), err_msg)

#         # both missing and extra columns
#         df = pd.DataFrame({**missing_column, "extra_column": 0}, index=[0])
#         with self.assertRaises(ValueError) as err:
#             Stats(df)
#         err_msg = ("[datatube.stats.Stats.__init__] columns of `data` do not match expected "
#                    "(missing columns: {'views'}, extra columns: "
#                    "{'extra_column'})")
#         self.assertEqual(str(err.exception), err_msg)

#         # bad video_id data type
#         df = pd.DataFrame({**TEST_PROPERTIES, "video_id": 123}, index=[0])
#         with self.assertRaises(TypeError) as err:
#             Stats(df)
#         err_msg = "[datatube.stats.Stats.__init__] column 'video_id' must contain string data"
#         self.assertEqual(str(err.exception), err_msg)

#         # bad timestamp data type
#         df = pd.DataFrame({**TEST_PROPERTIES, "timestamp": 123}, index=[0])
#         with self.assertRaises(TypeError) as err:
#             Stats(df)
#         err_msg = ("[datatube.stats.Stats.__init__] column 'timestamp' must contain datetime "
#                    "data")
#         self.assertEqual(str(err.exception), err_msg)

#         # bad views data type
#         df = pd.DataFrame({**TEST_PROPERTIES, "views": "abc"}, index=[0])
#         with self.assertRaises(TypeError) as err:
#             Stats(df)
#         err_msg = "[datatube.stats.Stats.__init__] column 'views' must contain integer data"
#         self.assertEqual(str(err.exception), err_msg)

#         # bad rating data type
#         df = pd.DataFrame({**TEST_PROPERTIES, "rating": "abc"}, index=[0])
#         with self.assertRaises(TypeError) as err:
#             Stats(df)
#         err_msg = "[datatube.stats.Stats.__init__] column 'rating' must contain numeric data"
#         self.assertEqual(str(err.exception), err_msg)

#         # bad likes data type
#         df = pd.DataFrame({**TEST_PROPERTIES, "likes": "abc"}, index=[0])
#         with self.assertRaises(TypeError) as err:
#             Stats(df)
#         err_msg = "[datatube.stats.Stats.__init__] column 'likes' must contain integer data"
#         self.assertEqual(str(err.exception), err_msg)

#         # bad dislikes data type
#         df = pd.DataFrame({**TEST_PROPERTIES, "dislikes": "abc"}, index=[0])
#         with self.assertRaises(TypeError) as err:
#             Stats(df)
#         err_msg = "[datatube.stats.Stats.__init__] column 'dislikes' must contain integer data"
#         self.assertEqual(str(err.exception), err_msg)

#     # def test_from_csv_errors()

#     def test_append_video_id_errors(self):
#         s = Stats()

#         # bad video_id type
#         with self.assertRaises(TypeError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "video_id": 123})
#         err_msg = ("[datatube.stats.Stats.add_row] `video_id` must be an 11-character video "
#                    "id string (received object of type: <class 'int'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # bad video_id length
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "video_id": "not11characters"})
#         err_msg = ("[datatube.stats.Stats.add_row] `video_id` must be an 11-character video "
#                    "id string (received: 'not11characters')")
#         self.assertEqual(str(err.exception), err_msg)

#     def test_append_timestamp_errors(self):
#         s = Stats()

#         # bad timestamp type
#         with self.assertRaises(TypeError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "timestamp": 123})
#         err_msg = ("[datatube.stats.Stats.add_row] `timestamp` must be a datetime.datetime "
#                    "object (received object of type: <class 'int'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # in the future
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "timestamp": datetime(9999, 12, 31)})
#         err_msg = (f"[datatube.stats.Stats.add_row] `timestamp` must be a datetime.datetime "
#                    f"object (timestamp in the future: "
#                    f"{datetime(9999, 12, 31)} > ")
#         self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

#     def test_append_views_errors(self):
#         s = Stats()

#         # bad views type
#         with self.assertRaises(TypeError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "views": "abc"})
#         err_msg = ("[datatube.stats.Stats.add_row] `views` must be an integer > 0 (received "
#                    "object of type: <class 'str'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # negative views
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "views": -1})
#         err_msg = ("[datatube.stats.Stats.add_row] `views` must be an integer > 0 (received: "
#                    "-1)")
#         self.assertEqual(str(err.exception), err_msg)

#     def test_append_rating_errors(self):
#         s = Stats()

#         # bad rating type
#         with self.assertRaises(TypeError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "rating": "abc"})
#         err_msg = ("[datatube.stats.Stats.add_row] `rating` must be a numeric between 0 and 5 "
#                    "(received object of type: <class 'str'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # negative rating
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "rating": -1})
#         err_msg = ("[datatube.stats.Stats.add_row] `rating` must be a numeric between 0 and 5 "
#                    "(received: -1)")
#         self.assertEqual(str(err.exception), err_msg)

#         # rating too high
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "rating": 5.3})
#         err_msg = ("[datatube.stats.Stats.add_row] `rating` must be a numeric between 0 and 5 "
#                    "(received: 5.3)")
#         self.assertEqual(str(err.exception), err_msg)

#     def test_append_likes_errors(self):
#         s = Stats()

#         # bad likes type
#         with self.assertRaises(TypeError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "likes": "abc"})
#         err_msg = ("[datatube.stats.Stats.add_row] `likes` must be an integer > 0 (received "
#                    "object of type: <class 'str'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # negative likes
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "likes": -1})
#         err_msg = ("[datatube.stats.Stats.add_row] `likes` must be an integer > 0 (received: "
#                    "-1)")
#         self.assertEqual(str(err.exception), err_msg)

#     def test_append_dislikes_errors(self):
#         s = Stats()

#         # bad dislikes type
#         with self.assertRaises(TypeError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "dislikes": "abc"})
#         err_msg = ("[datatube.stats.Stats.add_row] `dislikes` must be an integer > 0 "
#                    "(received object of type: <class 'str'>)")
#         self.assertEqual(str(err.exception), err_msg)

#         # negative dislikes
#         with self.assertRaises(ValueError) as err:
#             s.add_row(**{**TEST_PROPERTIES, "dislikes": -1})
#         err_msg = ("[datatube.stats.Stats.add_row] `dislikes` must be an integer > 0 "
#                    "(received: -1)")
#         self.assertEqual(str(err.exception), err_msg)


if __name__ == "__main__":
    unittest.main()