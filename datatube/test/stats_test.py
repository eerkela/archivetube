from datetime import datetime, timedelta
from pathlib import Path
import random
import unittest

import pandas as pd
from pandas.testing import assert_frame_equal

from datatube import ROOT_DIR
from datatube.stats import Stats, check_dtypes, coerce_dtypes


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


class DTypeTests(unittest.TestCase):

    def test_check_dtypes_no_na(self):
        df = pd.DataFrame({"a": [1], "b": [2.1], "c": ["abc"], "d": [True],
                           "e": [datetime.now()], "f": [timedelta(seconds=10)],
                           "g": [None]})

        # check works on expected input
        expected_types = {
            "a": int,
            "b": float,
            "c": str,
            "d": bool,
            "e": datetime,
            "f": timedelta
            # "g" can be any type
        }
        for col_name, typespec in expected_types.items():
            check_dtypes(df, **{col_name: typespec})

        # check errors when input type doesn't match
        available_types = [int, float, str, bool, datetime, timedelta]
        for col_name in expected_types:
            for typespec in available_types:
                try:
                    self.assertEqual(check_dtypes(df, **{col_name: typespec}),
                                     typespec == expected_types[col_name])
                except AssertionError as exc:
                    err_msg = (f"col_name: {repr(col_name)}, typespec: "
                               f"{typespec}")
                    raise AssertionError(err_msg) from exc

    def test_check_dtypes_with_na(self):
        df = pd.DataFrame({"a": [1, None],
                           "b": [2.1, None],
                           "c": ["abc", None],
                           "d": [True, None],
                           "e": [datetime.now(), None],
                           "f": [timedelta(seconds=10), None],
                           "g": [None, None]})
        # check works on expected input
        expected_types = {
            "a": int,
            "b": float,
            "c": str,
            "d": bool,
            "e": datetime,
            "f": timedelta
            # "g" can be any type
        }
        for col_name, typespec in expected_types.items():
            check_dtypes(df, **{col_name: typespec})

        # check errors when input type doesn't match
        available_types = [int, float, str, bool, datetime, timedelta]
        for col_name in expected_types:
            for typespec in available_types:
                try:
                    self.assertEqual(check_dtypes(df, **{col_name: typespec}),
                                     typespec == expected_types[col_name])
                except AssertionError as exc:
                    err_msg = (f"col_name: {repr(col_name)}, typespec: "
                               f"{typespec}")
                    raise AssertionError(err_msg) from exc


class BasicStatsTests(unittest.TestCase):

    csv_path = Path(ROOT_DIR, "datatube", "test", "test_data", "test_stats.csv")

    def test_raw_init(self):
        # pre-existing df
        df = pd.DataFrame(TEST_PROPERTIES, index=[0])
        s = Stats(df)
        assert_frame_equal(s.data, coerce_dtypes(df, **EXPECTED_TYPES))

        # no input
        df = pd.DataFrame(dict.fromkeys(list(TEST_PROPERTIES), []))
        s = Stats()
        assert_frame_equal(s.data, coerce_dtypes(df, **EXPECTED_TYPES))

        # empty input
        df = pd.DataFrame

        # df columns out of order
        keys = list(TEST_PROPERTIES.keys())
        random.seed(123)  # guarantees a swap
        random.shuffle(keys)
        df = pd.DataFrame({k: TEST_PROPERTIES[k] for k in keys}, index=[0])
        s = Stats(df)
        expected = pd.DataFrame(TEST_PROPERTIES, index=[0])  # original order
        assert_frame_equal(s.data, coerce_dtypes(expected, **EXPECTED_TYPES))

    def test_add_row(self):
        s = Stats()
        s.add_row(**TEST_PROPERTIES)
        df = pd.DataFrame(TEST_PROPERTIES, index=[0])
        assert_frame_equal(s.data, coerce_dtypes(df, **EXPECTED_TYPES))

    def test_to_and_from_csv(self):
        s = Stats()
        s.add_row(**TEST_PROPERTIES)
        self.csv_path.unlink(missing_ok=True)

        # all video_ids
        s.to_csv(self.csv_path)
        self.assertTrue(self.csv_path.exists())
        result = coerce_dtypes(pd.read_csv(self.csv_path), **EXPECTED_TYPES)
        assert_frame_equal(s.data, result)

        # a specific video_id
        s.add_row(video_id="differentId", timestamp=datetime.now(), views=50,
                  rating=3.4)
        self.assertTrue(len(s.data) > 1)  # append actually worked
        self.csv_path.unlink()
        s.to_csv(self.csv_path, TEST_PROPERTIES["video_id"])  # save to csv
        result = coerce_dtypes(pd.read_csv(self.csv_path), **EXPECTED_TYPES)
        subset = s.data[s.data["video_id"] == TEST_PROPERTIES["video_id"]]
        subset = subset.reset_index(drop=True)
        assert_frame_equal(subset, result)

        # from_csv
        s = Stats.from_csv(self.csv_path)
        expected = coerce_dtypes(pd.DataFrame(TEST_PROPERTIES, index=[0]),
                                 **EXPECTED_TYPES)
        assert_frame_equal(s.data, expected)


class StatsErrorTests(unittest.TestCase):

    def test_raw_init_errors(self):
        # bad arg type
        with self.assertRaises(TypeError) as err:
            Stats(123)
        err_msg = ("[Stats.__init__] `data` must be a pandas.DataFrame object "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # extra column
        df = pd.DataFrame({**TEST_PROPERTIES, "extra_column": 0}, index=[0])
        with self.assertRaises(ValueError) as err:
            Stats(df)
        err_msg = ("[Stats.__init__] columns of `data` do not match expected "
                   "(extra columns: {'extra_column'})")
        self.assertEqual(str(err.exception), err_msg)

        # missing column
        missing_column = {k: v for k, v in TEST_PROPERTIES.items()
                          if k != "views"}
        df = pd.DataFrame(missing_column, index=[0])
        with self.assertRaises(ValueError) as err:
            Stats(df)
        err_msg = ("[Stats.__init__] columns of `data` do not match expected "
                   "(missing columns: {'views'})")
        self.assertEqual(str(err.exception), err_msg)

        # both missing and extra columns
        df = pd.DataFrame({**missing_column, "extra_column": 0}, index=[0])
        with self.assertRaises(ValueError) as err:
            Stats(df)
        err_msg = ("[Stats.__init__] columns of `data` do not match expected "
                   "(missing columns: {'views'}, extra columns: "
                   "{'extra_column'})")
        self.assertEqual(str(err.exception), err_msg)

        # bad video_id data type
        df = pd.DataFrame({**TEST_PROPERTIES, "video_id": 123}, index=[0])
        with self.assertRaises(TypeError) as err:
            Stats(df)
        err_msg = "[Stats.__init__] column 'video_id' must contain string data"
        self.assertEqual(str(err.exception), err_msg)

        # bad timestamp data type
        df = pd.DataFrame({**TEST_PROPERTIES, "timestamp": 123}, index=[0])
        with self.assertRaises(TypeError) as err:
            Stats(df)
        err_msg = ("[Stats.__init__] column 'timestamp' must contain datetime "
                   "data")
        self.assertEqual(str(err.exception), err_msg)

        # bad views data type
        df = pd.DataFrame({**TEST_PROPERTIES, "views": "abc"}, index=[0])
        with self.assertRaises(TypeError) as err:
            Stats(df)
        err_msg = "[Stats.__init__] column 'views' must contain integer data"
        self.assertEqual(str(err.exception), err_msg)

        # bad rating data type
        df = pd.DataFrame({**TEST_PROPERTIES, "rating": "abc"}, index=[0])
        with self.assertRaises(TypeError) as err:
            Stats(df)
        err_msg = "[Stats.__init__] column 'rating' must contain numeric data"
        self.assertEqual(str(err.exception), err_msg)

        # bad likes data type
        df = pd.DataFrame({**TEST_PROPERTIES, "likes": "abc"}, index=[0])
        with self.assertRaises(TypeError) as err:
            Stats(df)
        err_msg = "[Stats.__init__] column 'likes' must contain integer data"
        self.assertEqual(str(err.exception), err_msg)

        # bad dislikes data type
        df = pd.DataFrame({**TEST_PROPERTIES, "dislikes": "abc"}, index=[0])
        with self.assertRaises(TypeError) as err:
            Stats(df)
        err_msg = "[Stats.__init__] column 'dislikes' must contain integer data"
        self.assertEqual(str(err.exception), err_msg)

    # def test_from_csv_errors()

    def test_append_video_id_errors(self):
        s = Stats()

        # bad video_id type
        with self.assertRaises(TypeError) as err:
            s.add_row(**{**TEST_PROPERTIES, "video_id": 123})
        err_msg = ("[Stats.add_row] `video_id` must be an 11-character video "
                   "id string (received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad video_id length
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "video_id": "not11characters"})
        err_msg = ("[Stats.add_row] `video_id` must be an 11-character video "
                   "id string (received: 'not11characters')")
        self.assertEqual(str(err.exception), err_msg)

    def test_append_timestamp_errors(self):
        s = Stats()

        # bad timestamp type
        with self.assertRaises(TypeError) as err:
            s.add_row(**{**TEST_PROPERTIES, "timestamp": 123})
        err_msg = ("[Stats.add_row] `timestamp` must be a datetime.datetime "
                   "object (received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "timestamp": datetime(9999, 12, 31)})
        err_msg = (f"[Stats.add_row] `timestamp` must be a datetime.datetime "
                   f"object (timestamp in the future: "
                   f"{datetime(9999, 12, 31)} > ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

    def test_append_views_errors(self):
        s = Stats()

        # bad views type
        with self.assertRaises(TypeError) as err:
            s.add_row(**{**TEST_PROPERTIES, "views": "abc"})
        err_msg = ("[Stats.add_row] `views` must be an integer > 0 (received "
                   "object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative views
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "views": -1})
        err_msg = ("[Stats.add_row] `views` must be an integer > 0 (received: "
                   "-1)")
        self.assertEqual(str(err.exception), err_msg)

    def test_append_rating_errors(self):
        s = Stats()

        # bad rating type
        with self.assertRaises(TypeError) as err:
            s.add_row(**{**TEST_PROPERTIES, "rating": "abc"})
        err_msg = ("[Stats.add_row] `rating` must be a numeric between 0 and 5 "
                   "(received object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative rating
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "rating": -1})
        err_msg = ("[Stats.add_row] `rating` must be a numeric between 0 and 5 "
                   "(received: -1)")
        self.assertEqual(str(err.exception), err_msg)

        # rating too high
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "rating": 5.3})
        err_msg = ("[Stats.add_row] `rating` must be a numeric between 0 and 5 "
                   "(received: 5.3)")
        self.assertEqual(str(err.exception), err_msg)

    def test_append_likes_errors(self):
        s = Stats()

        # bad likes type
        with self.assertRaises(TypeError) as err:
            s.add_row(**{**TEST_PROPERTIES, "likes": "abc"})
        err_msg = ("[Stats.add_row] `likes` must be an integer > 0 (received "
                   "object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative likes
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "likes": -1})
        err_msg = ("[Stats.add_row] `likes` must be an integer > 0 (received: "
                   "-1)")
        self.assertEqual(str(err.exception), err_msg)

    def test_append_dislikes_errors(self):
        s = Stats()

        # bad dislikes type
        with self.assertRaises(TypeError) as err:
            s.add_row(**{**TEST_PROPERTIES, "dislikes": "abc"})
        err_msg = ("[Stats.add_row] `dislikes` must be an integer > 0 "
                   "(received object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative dislikes
        with self.assertRaises(ValueError) as err:
            s.add_row(**{**TEST_PROPERTIES, "dislikes": -1})
        err_msg = ("[Stats.add_row] `dislikes` must be an integer > 0 "
                   "(received: -1)")
        self.assertEqual(str(err.exception), err_msg)
