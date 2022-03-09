from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import time
import unittest

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datatube.info import VideoInfo
from datatube.test import DATA_DIR


"""
TODO: Check video JSON format matches expected
"""


TEST_PROPERTIES = {
    "channel_id": "UC_24_character_channel_",
    "channel_name": "Some Channel",
    "video_id": "11character",
    "video_title": "Some Video",
    "publish_date": datetime(2020, 1, 1, tzinfo=timezone.utc),
    "last_updated": datetime.now(timezone.utc),
    "duration": timedelta(minutes=5),
    "description": "Video description...",
    "keywords": ["datatube", "test", "foo", "bar", "baz"],
    "thumbnail_url": "https://i.kym-cdn.com/photos/images/original/000/581/296/c09.jpg"
}
JSON_PATH = Path(DATA_DIR, "test_video_info.json")
DB_NAME = "datatube_test"


class BasicVideoInfoTests(unittest.TestCase):

    def test_init_good_input(self):
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(info.channel_id, TEST_PROPERTIES["channel_id"])
        self.assertEqual(info.channel_name, TEST_PROPERTIES["channel_name"])
        self.assertEqual(info.video_id, TEST_PROPERTIES["video_id"])
        self.assertEqual(info.video_title, TEST_PROPERTIES["video_title"])
        self.assertEqual(info.publish_date, TEST_PROPERTIES["publish_date"])
        self.assertEqual(info.last_updated, TEST_PROPERTIES["last_updated"])
        self.assertEqual(info.duration, TEST_PROPERTIES["duration"])
        self.assertEqual(info.description, TEST_PROPERTIES["description"])
        self.assertEqual(info.keywords, TEST_PROPERTIES["keywords"])
        self.assertEqual(info.thumbnail_url, TEST_PROPERTIES["thumbnail_url"])

    def test_bad_channel_id(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # bad length
        test_val = "UC_not_24_chars"
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # doesn't start with 'UC'
        test_val = "_does_not_start_with_UC_"
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_channel_name(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # empty string
        test_val = ""
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_video_id(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_id": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # bad length
        test_val = "not11characters"
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_id": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_video_title(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # empty string
        test_val = ""
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_publish_date(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "publish_date": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        test_val = datetime(9999, 12, 31, tzinfo=timezone.utc)
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # greater than last_updated
        time.sleep(0.5)  # to ensure datetime.now() resolves to different time
        test_val = datetime.now(timezone.utc)
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_last_updated(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        test_val = datetime(9999, 12, 31, tzinfo=timezone.utc)
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_duration(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # negative duration
        test_val = timedelta(seconds=-1)
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_description(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "description": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_keywords(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "keywords": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # bad keyword type
        test_val = ["fine", "great", 123]
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # empty string
        test_val = ["fine", "great", ""]
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_bad_thumbnail_url(self):
        # bad type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "thumbnail_url": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # not a url
        test_val = "this is not a url"
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "thumbnail_url": test_val})
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)


class VideoInfoJSONTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        with JSON_PATH.open("w") as json_file:
            json.dump(TEST_PROPERTIES, json_file, default=str)

    def test_from_json(self):
        info = VideoInfo.from_json(JSON_PATH)
        self.assertEqual(info.channel_id, TEST_PROPERTIES["channel_id"])
        self.assertEqual(info.channel_name, TEST_PROPERTIES["channel_name"])
        self.assertEqual(info.video_id, TEST_PROPERTIES["video_id"])
        self.assertEqual(info.video_title, TEST_PROPERTIES["video_title"])
        self.assertEqual(info.publish_date, TEST_PROPERTIES["publish_date"])
        self.assertEqual(info.last_updated, TEST_PROPERTIES["last_updated"])
        self.assertEqual(info.duration, TEST_PROPERTIES["duration"])
        self.assertEqual(info.description, TEST_PROPERTIES["description"])
        self.assertEqual(info.keywords, TEST_PROPERTIES["keywords"])
        self.assertEqual(info.thumbnail_url, TEST_PROPERTIES["thumbnail_url"])

    def test_to_json(self):
        info = VideoInfo(**TEST_PROPERTIES)
        test_path = Path(JSON_PATH.parent, "temp_channel_info_to_json.json")
        test_path.unlink(missing_ok=True)
        info.to_json(test_path)
        self.assertTrue(test_path.exists())
        with test_path.open("r") as json_file:
            saved = json.load(json_file)
        self.assertEqual(saved, json.dumps(TEST_PROPERTIES, default=str))
        test_path.unlink()

    def test_from_json_errors(self):
        # bad path type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path does not exist
        test_val = Path(JSON_PATH.parent, "this_path_does_not_exist.json")
        with self.assertRaises(ValueError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path points to directory
        test_val = Path(JSON_PATH.parent)
        with self.assertRaises(ValueError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # file does not end in .json
        test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
        with self.assertRaises(ValueError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_to_json_errors(self):
        info = VideoInfo(**TEST_PROPERTIES)

        # bad path type
        test_val = 123
        with self.assertRaises(TypeError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path does not exist
        test_val = Path(JSON_PATH.parent, "this_path_does_not_exist.json")
        with self.assertRaises(ValueError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path points to directory
        test_val = Path(JSON_PATH.parent)
        with self.assertRaises(ValueError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # file does not end in .json
        test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
        with self.assertRaises(ValueError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)


class ChannelInfoSQLTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()
