from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import reprlib
import time
import unittest
from xml.dom.minidom import Attr

from pyrsistent import immutable

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datatube.info import VideoInfo
from datatube.test import DATA_DIR


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
EXPECTED_VIDEOINFO = TEST_PROPERTIES
JSON_PATH = Path(DATA_DIR, "test_video_info.json")
EXPECTED_JSON = {
    "channel_id": TEST_PROPERTIES["channel_id"],
    "channel_name": TEST_PROPERTIES["channel_name"],
    "video_id": TEST_PROPERTIES["video_id"],
    "video_title": TEST_PROPERTIES["video_title"],
    "publish_date": TEST_PROPERTIES["publish_date"].isoformat(),
    "last_updated": TEST_PROPERTIES["last_updated"].isoformat(),
    "duration": TEST_PROPERTIES["duration"].total_seconds(),
    "description": TEST_PROPERTIES["description"],
    "keywords": TEST_PROPERTIES["keywords"],
    "thumbnail_url": TEST_PROPERTIES["thumbnail_url"]
}
DB_NAME = "datatube_test"


unittest.TestCase.maxDiff = None


class VideoInfoGetterSetterTests(unittest.TestCase):

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

    def test_immutable_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, bool)
        err_msg = (f"[datatube.info.VideoInfo.__init__] `immutable` must be "
                   f"a boolean (received object of type: {type(test_val)})")

        with self.assertRaises(TypeError) as err:
            VideoInfo(**TEST_PROPERTIES, immutable=test_val)
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id(self):
        test_val = "UC_some_other_channel_id"  # still 24 characters
        self.assertEqual(len(test_val), 24)
        self.assertTrue(test_val.startswith("UC"))
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(info.channel_id, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.channel_id = test_val
        self.assertEqual(info.channel_id, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["channel_id"] = test_val
        self.assertEqual(info["channel_id"], test_val)

    def test_set_channel_id_immutable_instance(self):
        test_val = "UC_some_other_channel_id"  # still 24 characters
        self.assertEqual(len(test_val), 24)
        self.assertTrue(test_val.startswith("UC"))
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])
        err_msg = ("[datatube.info.VideoInfo.channel_id] cannot reassign "
                   "`channel_id`: VideoInfo instance is immutable")

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, str)
        err_msg = (f"[datatube.info.VideoInfo.channel_id] `channel_id` must "
                   f"be a 24-character ExternalId string starting with 'UC' "
                   f"(received object of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_bad_length(self):
        test_val = "UC_not_24_chars"
        self.assertNotEqual(len(test_val), 24)
        self.assertTrue(test_val.startswith("UC"))
        err_msg = (f"[datatube.info.VideoInfo.channel_id] `channel_id` must "
                   f"be a 24-character ExternalId string starting with 'UC' "
                   f"(received: {repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_doesnt_start_with_UC(self):
        test_val = "_does_not_start_with_UC_"  # still 24 characters
        self.assertEqual(len(test_val), 24)
        self.assertFalse(test_val.startswith("UC"))
        err_msg = (f"[datatube.info.VideoInfo.channel_id] `channel_id` must "
                   f"be a 24-character ExternalId string starting with 'UC' "
                   f"(received: {repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info =  VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_name(self):
        test_val = "Some Other Channel Name"
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_name"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        self.assertEqual(info.channel_name, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.channel_name = test_val
        self.assertEqual(info.channel_name, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["channel_name"] = test_val
        self.assertEqual(info["channel_name"], test_val)

    def test_set_channel_name_immutable_instance(self):
        test_val = "Some Other Channel Name"
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_name"])
        err_msg = ("[datatube.info.VideoInfo.channel_name] cannot reassign "
                   "`channel_name`: VideoInfo instance is immutable")

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_name_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, str)
        err_msg = (f"[datatube.info.VideoInfo.channel_name] `channel_name` "
                   f"must be a non-empty string (received object of type: "
                   f"{type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_name_empty_string(self):
        test_val = ""
        self.assertEqual(test_val, "")
        err_msg = (f"[datatube.info.VideoInfo.channel_name] `channel_name` "
                   f"must be a non-empty string (received: {repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_video_id(self):
        test_val = "abcdefghijk"  # 11 characters
        self.assertEqual(len(test_val), 11)
        self.assertNotEqual(test_val, TEST_PROPERTIES["video_id"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "video": test_val})
        self.assertEqual(info.video_id, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.video_id = test_val
        self.assertEqual(info.video_id, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["video_id"] = test_val
        self.assertEqual(info["video_id"], test_val)

    def test_set_video_id_immutable_instance(self):
        test_val = "abcdefghijk"  # 11 characters
        self.assertEqual(len(test_val), 11)
        self.assertNotEqual(test_val, TEST_PROPERTIES["video_id"])
        err_msg = ("[datatube.info.VideoInfo.video_id] cannot reassign "
                   "`video_id`: VideoInfo instance is immutable")

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.video_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["video_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_video_id_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, str)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.video_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["video_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_video_id_bad_length(self):
        test_val = "not11characters"
        self.assertNotEqual(len(test_val), 11)
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.video_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["video_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_video_title(self):
        test_val = "Some Other Video Title"
        self.assertNotEqual(test_val, TEST_PROPERTIES["video_title"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        self.assertEqual(info.video_title, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.video_title = test_val
        self.assertEqual(info.video_title, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["video_title"] = test_val
        self.assertEqual(info["video_title"], test_val)

    def test_set_video_title_immutable_instance(self):
        test_val = "Some Other Video Title"
        self.assertNotEqual(test_val, TEST_PROPERTIES["video_title"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(AttributeError) as err:
            info.video_title = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["video_title"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_video_title_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, str)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.video_title = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["video_title"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_video_title_empty_string(self):
        test_val = ""
        self.assertEqual(test_val, "")
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "video_title": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.video_title = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["video_title"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_publish_date(self):
        test_val = datetime(2020, 1, 1, tzinfo=timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["publish_date"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "publish_date": test_val})
        self.assertEqual(info.publish_date, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.publish_date = test_val
        self.assertEqual(info.publish_date, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["publish_date"] = test_val
        self.assertEqual(info["publish_date"], test_val)

    def test_set_publish_date_immutable_instance(self):
        test_val = datetime(202, 1, 1, tzinfo=timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["publish_date"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(AttributeError) as err:
            info.publish_date = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["publish_date"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_publish_date_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, datetime)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "publish_date": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.publish_date = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["publish_date"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_publish_date_has_no_timezone(self):
        test_val = datetime(2020, 1, 1)
        self.assertIsNone(test_val.tzinfo)
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "publish_date": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.publish_date = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["publish_date"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_publish_date_in_future(self):
        test_val = datetime(9999, 12, 31, tzinfo=timezone.utc)
        self.assertGreater(test_val, datetime.now(timezone.utc))
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "publish_date": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.publish_date = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["publish_date"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_publish_date_greater_than_last_updated(self):
        test_val = datetime.now(timezone.utc)
        self.assertGreater(test_val, TEST_PROPERTIES["last_updated"])
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "publish_date": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.publish_date = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["publish_date"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated(self):
        test_val = datetime.now(timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(info.last_updated, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.last_updated = test_val
        self.assertEqual(info.last_updated, test_val)

        # from getitem/setitem
        info["last_updated"] = test_val
        self.assertEqual(info["last_updated"], test_val)

    def test_set_last_updated_immutable_instance(self):
        test_val = datetime.now(timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(AttributeError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, datetime)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_has_no_timezone(self):
        test_val = datetime.now()
        self.assertIsNone(test_val.tzinfo)
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_in_future(self):
        test_val = datetime(9999, 12, 31, tzinfo=timezone.utc)
        self.assertGreater(test_val, datetime.now(timezone.utc))
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_less_than_publish_date(self):
        test_val = datetime(1950, 1, 1, tzinfo=timezone.utc)
        self.assertLess(test_val, TEST_PROPERTIES["publish_date"])
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_duration(self):
        test_val = timedelta(seconds=10)
        self.assertNotEqual(test_val, TEST_PROPERTIES["duration"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        self.assertEqual(info.duration, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.duration = test_val
        self.assertEqual(info.duration, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["duration"] = test_val
        self.assertEqual(info["duration"], test_val)

    def test_set_duration_immutable_instance(self):
        test_val = timedelta(seconds=10)
        self.assertNotEqual(test_val, TEST_PROPERTIES["duration"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.duration = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["duration"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_duration_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, timedelta)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.duration = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["duration"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_duration_negative_interval(self):
        test_val = timedelta(seconds=-1)
        self.assertLess(test_val, timedelta())
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "duration": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.duration = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["duration"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_description(self):
        test_val = "Some Other Description"
        self.assertNotEqual(test_val, TEST_PROPERTIES["description"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "description": test_val})
        self.assertEqual(info.description, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.description = test_val
        self.assertEqual(info.description, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["description"] = test_val
        self.assertEqual(info["description"], test_val)

    def test_set_description_immutable_instance(self):
        test_val = "Some Other Description"
        self.assertNotEqual(test_val, TEST_PROPERTIES["description"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(AttributeError) as err:
            info.description = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["description"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_description_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, str)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "description": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.description = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_keywords(self):
        test_val = ["these", "are", "different", "from", "normal"]
        self.assertNotEqual(test_val, TEST_PROPERTIES["keywords"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "keywords": test_val})
        self.assertEqual(info.keywords, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.keywords = test_val
        self.assertEqual(info.keywords, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["keywords"] = test_val
        self.assertEqual(info["keywords"], test_val)

    def test_set_keywords_immutable_instance(self):
        test_val = ["these", "are", "different", "from", "normal"]
        self.assertNotEqual(test_val, TEST_PROPERTIES["keywords"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.keywords = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["keywords"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_keywords_bad_type(self):
        test_val = "does not accept naked strings"
        self.assertNotIsInstance(test_val, (list, tuple, set))
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "keywords": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.keywords = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["keywords"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_keywords_bad_keyword_type(self):
        test_val = ["fine", "great", 123]
        self.assertFalse(all(isinstance(k, str) for k in test_val))
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "keywords": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.keywords = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["keywords"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_keywords_empty_string(self):
        test_val = ["fine", "great", ""]
        self.assertFalse(all(test_val))
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "keywords": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.keywords = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["keywords"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_thumbnail_url(self):
        test_val = "https://i.kym-cdn.com/entries/icons/mobile/000/023/397/C-658VsXoAo3ovC.jpg"
        self.assertNotEqual(test_val, TEST_PROPERTIES["thumbnail_url"])

        # from init
        info = VideoInfo(**{**TEST_PROPERTIES, "thumbnail_url": test_val})
        self.assertEqual(info.thumbnail_url, test_val)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        info.thumbnail_url = test_val
        self.assertEqual(info.thumbnail_url, test_val)

        # from getitem/setitem
        info = VideoInfo(**TEST_PROPERTIES)
        info["thumbnail_url"] = test_val
        self.assertEqual(info["thumbnail_url"], test_val)

    def test_set_thumbnail_url_immutable_instance(self):
        test_val = "https://i.kym-cdn.com/entries/icons/mobile/000/023/397/C-658VsXoAo3ovC.jpg"
        self.assertNotEqual(test_val, TEST_PROPERTIES["thumbnail_url"])
        err_msg = ""

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.thumbnail_url = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["thumbnail_url"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_thumbnail_url_bad_type(self):
        test_val = 123
        self.assertNotIsInstance(test_val, str)
        err_msg = ""

        # from init
        with self.assertRaises(TypeError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "thumbnail_url": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.thumbnail_url = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["thumbnail_url"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_thumbnail_url_not_a_url(self):
        test_val = "this is not a valid url"
        self.assertNotEqual(test_val, TEST_PROPERTIES["thumbnail_url"])
        err_msg = ""

        # from init
        with self.assertRaises(ValueError) as err:
            VideoInfo(**{**TEST_PROPERTIES, "thumbnail_url": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.thumbnail_url = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["thumbnail_url"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_getitem_key_error(self):
        test_key = "this key does not exist"
        self.assertNotIn(test_key, TEST_PROPERTIES)
        err_msg = repr(test_key)

        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(KeyError) as err:
            info[test_key]
        self.assertEqual(str(err.exception), err_msg)

    def test_setitem_key_error(self):
        test_key = "this key does not exist"
        self.assertNotIn(test_key, TEST_PROPERTIES)
        err_msg = repr(test_key)

        info = VideoInfo(**TEST_PROPERTIES)
        with self.assertRaises(KeyError) as err:
            info[test_key] = "something"
        self.assertEqual(str(err.exception), err_msg)


class VideoInfoIterationTests(unittest.TestCase):

    def test_items(self):
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(tuple(info.items()), tuple(EXPECTED_VIDEOINFO.items()))

    def test_keys(self):
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(tuple(info.keys()), tuple(EXPECTED_VIDEOINFO.keys()))

    def test_values(self):
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(tuple(info.values()),
                         tuple(EXPECTED_VIDEOINFO.values()))

    def test_iter(self):
        info = VideoInfo(**TEST_PROPERTIES)
        expected = tuple(EXPECTED_VIDEOINFO)
        for index, key in enumerate(info):
            self.assertEqual(key, expected[index])


class VideoInfoDunderTests(unittest.TestCase):

    def test_contains(self):
        info = VideoInfo(**TEST_PROPERTIES)

        # True
        for key in EXPECTED_VIDEOINFO:
            self.assertTrue(key in info)

        # False
        self.assertFalse("" in info)  # empty string
        self.assertFalse("this key does not exist" in info)

    def test_equality_videoinfo_instances(self):
        # True
        info1 = VideoInfo(**TEST_PROPERTIES)
        info2 = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(info1, info2)

        # False
        different = {
            "channel_id": "UC_different_from_info1_",
            "channel_name": "Some Other Channel Name",
            "video_id": "_different_",
            "video_title": "Some Other Video Title",
            "publish_date": datetime(1950, 1, 1, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "duration": timedelta(hours=1),
            "description": "Some Other Description",
            "keywords": ["foo", "bar", "baz"],
            "thumbnail_url": "https://i.kym-cdn.com/entries/icons/mobile/000/023/397/C-658VsXoAo3ovC.jpg"
        }
        for key, test_val in different.items():
            self.assertNotEqual(test_val, TEST_PROPERTIES[key])
            info3 = VideoInfo(**{**TEST_PROPERTIES, key: test_val})
            self.assertNotEqual(info1, info3)

    def test_equality_base_dict(self):
        # True
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(info, EXPECTED_VIDEOINFO)

        # False - unequal values
        different = {
            "channel_id": "UC_different_from_info1_",
            "channel_name": "Some Other Channel Name",
            "video_id": "_different_",
            "video_title": "Some Other Video Title",
            "publish_date": datetime(1950, 1, 1, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "duration": timedelta(hours=1),
            "description": "Some Other Description",
            "keywords": ["foo", "bar", "baz"],
            "thumbnail_url": "https://i.kym-cdn.com/entries/icons/mobile/000/023/397/C-658VsXoAo3ovC.jpg"
        }
        for key, test_val in different.items():
            self.assertNotEqual(test_val, TEST_PROPERTIES[key])
            expected = {**EXPECTED_VIDEOINFO, key: test_val}
            self.assertNotEqual(info, expected)

        # False - missing/extra key
        for key in TEST_PROPERTIES:
            missing = {k: v for k, v in EXPECTED_VIDEOINFO.items() if k != key}
            self.assertNotEqual(info, missing)
        self.assertNotIn("extra key", EXPECTED_VIDEOINFO)
        self.assertNotEqual(info, {**EXPECTED_VIDEOINFO,
                                   "extra key": "some value"})

    def test_hash(self):
        # equal values
        info1 = VideoInfo(**TEST_PROPERTIES, immutable=True)
        info2 = VideoInfo(**TEST_PROPERTIES, immutable=True)
        self.assertEqual(hash(info1), hash(info2))

        # unequal values
        different = {
            "channel_id": "UC_different_from_info1_",
            "channel_name": "Some Other Channel Name",
            "video_id": "_different_",
            "video_title": "Some Other Video Title",
            "publish_date": datetime(1950, 1, 1, tzinfo=timezone.utc),
            "last_updated": datetime.now(timezone.utc),
            "duration": timedelta(hours=1),
            "description": "Some Other Description",
            "keywords": ["foo", "bar", "baz"],
            "thumbnail_url": "https://i.kym-cdn.com/entries/icons/mobile/000/023/397/C-658VsXoAo3ovC.jpg"
        }
        for key, test_val in different.items():
            self.assertNotEqual(test_val, TEST_PROPERTIES[key])
            info3 = VideoInfo(**{**TEST_PROPERTIES, key: test_val},
                              immutable=True)
            self.assertNotEqual(hash(info1), hash(info3))

        # instance not immutable
        info4 = VideoInfo(**TEST_PROPERTIES, immutable=False)
        with self.assertRaises(TypeError) as err:
            hash(info4)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_len(self):
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(len(info), len(EXPECTED_VIDEOINFO))

    def test_repr(self):
        fields = {**TEST_PROPERTIES, "immutable": False}
        str_repr = reprlib.Repr()
        formatted = []
        for k, v in fields.items():
            if isinstance(v, str):
                formatted.append(f"{k}={str_repr.repr(v)}")
            else:
                formatted.append(f"{k}={repr(v)}")
        expected = f"VideoInfo({', '.join(formatted)})"
        info = VideoInfo(**TEST_PROPERTIES)
        self.assertEqual(repr(info), expected)

    def test_str(self):
        info = VideoInfo(**TEST_PROPERTIES)

        # short values
        self.assertEqual(str(info), str(EXPECTED_VIDEOINFO))

        # long values
        lorem_ipsum = ("Lorem ipsum dolor sit amet, consectetur adipiscing "
                       "elit, sed do eiusmod tempor incididunt ut labore et "
                       "dolore magna aliqua. Ut enim ad minim veniam, quis "
                       "nostrud exercitation ullamco laboris nisi ut aliquip "
                       "ex ea commodo consequat. Duis aute irure dolor in "
                       "reprehenderit in voluptate velit esse cillum dolore "
                       "eu fugiat nulla pariatur. Excepteur sint occaecat "
                       "cupidatat non proident, sunt in culpa qui officia "
                       "deserunt mollit anim id est laborum.")
        different = {
            "channel_id": TEST_PROPERTIES["channel_id"],
            "channel_name": lorem_ipsum,
            "video_id": TEST_PROPERTIES["video_id"],
            "video_title": lorem_ipsum,
            "publish_date": TEST_PROPERTIES["publish_date"],
            "last_updated": TEST_PROPERTIES["last_updated"],
            "duration": TEST_PROPERTIES["duration"],
            "description": lorem_ipsum,
            "keywords": TEST_PROPERTIES["keywords"],
            "thumbnail_url": TEST_PROPERTIES["thumbnail_url"]
        }
        str_repr = reprlib.Repr()
        expected = {}
        for key, val in different.items():
            if isinstance(val, str):
                val = str_repr.repr(val)[1:-1]
            info[key] = val
            expected[key] = val
        self.assertEqual(str(info), str(expected))


class VideoInfoJSONTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        with JSON_PATH.open("w") as json_file:
            json.dump(EXPECTED_JSON, json_file)

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

        # immutable
        info = VideoInfo.from_json(JSON_PATH, immutable=True)
        self.assertTrue(info.immutable)
        with self.assertRaises(AttributeError):
            info.video_title = "Some Other Video Title"

    def test_to_json(self):
        info = VideoInfo(**TEST_PROPERTIES)
        test_path = Path(JSON_PATH.parent, "temp_video_info_to_json.json")
        test_path.unlink(missing_ok=True)
        info.to_json(test_path)
        self.assertTrue(test_path.exists())
        with test_path.open("r") as json_file:
            saved = json.load(json_file)
        self.assertEqual(saved, EXPECTED_JSON)
        test_path.unlink()

    def test_from_json_errors(self):
        # bad path type
        test_val = 123
        self.assertNotIsInstance(test_val, Path)
        with self.assertRaises(TypeError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path does not exist
        test_val = Path(JSON_PATH.parent, "this_path_does_not_exist.json")
        self.assertFalse(test_val.exists())
        with self.assertRaises(ValueError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path points to directory
        test_val = Path(JSON_PATH.parent)
        self.assertTrue(test_val.is_dir())
        with self.assertRaises(ValueError) as err:
            VideoInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # file does not end in .json
        test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
        self.assertNotEqual(test_val.suffix, ".json")
        test_val.touch()
        with self.assertRaises(ValueError) as err:
            VideoInfo.from_json(test_val)
        test_val.unlink()
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_to_json_errors(self):
        info = VideoInfo(**TEST_PROPERTIES)

        # bad path type
        test_val = 123
        self.assertNotIsInstance(test_val, Path)
        with self.assertRaises(TypeError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path points to directory
        test_val = Path(JSON_PATH.parent)
        self.assertTrue(test_val.is_dir())
        with self.assertRaises(ValueError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # file does not end in .json
        test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
        self.assertNotEqual(test_val.suffix, ".json")
        with self.assertRaises(ValueError) as err:
            info.to_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)


if __name__ == "__main__":
    unittest.main()
