from datetime import datetime, timedelta
import json
from pathlib import Path
import time
import unittest

import pytube

from datatube import DATATUBE_VERSION_NUMBER, ROOT_DIR, VIDEO_DIR
from datatube.youtube import Channel, channel_id_to_url, Video, is_video_id


TEST_PROPERTIES = {
    "source": "local",
    "channel_id": "UCBR8-60-B28hp2BmDPdntcQ",  # official YouTube channel
    "channel_name": "YouTube",
    "video_ids": ["NeOBvwRfBWc", "QltYNmVUvh0", "SYQJPkiNJfE", "3WSmP7i9my8",
                  "TBuNVQ54dgg"],  # from official YouTube
    "last_updated": datetime.now(),
    "target_dir": Path(ROOT_DIR, "datatube", "test", "test_channels",
                       "UCBR8-60-B28hp2BmDPdntcQ"),
    "about_html": "",
    "community_html": "",
    "featured_channels_html": "",
    "videos_html": "",
    "workers": 1
}


class ChannelErrorTests(unittest.TestCase):

    def test_init_good_input(self):
        c = Channel(**TEST_PROPERTIES)
        self.assertEqual(c.source, TEST_PROPERTIES["source"])
        self.assertEqual(c.id, TEST_PROPERTIES["channel_id"])
        self.assertEqual(c.name, TEST_PROPERTIES["channel_name"])
        self.assertEqual(c.video_ids, TEST_PROPERTIES["video_ids"]),
        self.assertEqual(c.last_updated, TEST_PROPERTIES["last_updated"])
        self.assertEqual(c.html["about"], TEST_PROPERTIES["about_html"])
        self.assertEqual(c.html["community"], TEST_PROPERTIES["community_html"])
        self.assertEqual(c.html["featured_channels"],
                         TEST_PROPERTIES["featured_channels_html"])
        self.assertEqual(c.html["videos"], TEST_PROPERTIES["videos_html"])
        self.assertEqual(c.workers, TEST_PROPERTIES["workers"])
        self.assertEqual(c.target_dir, TEST_PROPERTIES["target_dir"])

    def test_source_errors(self):
        # bad source type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "source": 123})
        err_msg = ("[Channel.source] `source` must be a string with one of "
                   "the following values: ('local', 'pytube', 'sql') "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad source value
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES, "source": "bad source value"})
        err_msg = ("[Channel.source] `source` must be a string with one of "
                   "the following values: ('local', 'pytube', 'sql') "
                   "(received: 'bad source value')")
        self.assertEqual(str(err.exception), err_msg)

        # assignment outside init
        c = Channel(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            c.source = "something else"
        err_msg = ("[Channel.source] `source` cannot be changed outside of "
                   "init.  Construct a new Channel object instead")
        self.assertEqual(str(err.exception), err_msg)

    def test_channel_id_errors(self):
        # bad channel id type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "channel_id": 123})
        err_msg = ("[Channel.id] `id` must be a unique 24-character "
                   "ExternalId starting with 'UC', which is used by the "
                   "YouTube backend to track channels (received object of "
                   "type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad channel id length
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES,
                       "channel_id": TEST_PROPERTIES["channel_id"][:-2]})
        err_msg = (f"[Channel.id] `id` must be a unique 24-character "
                   f"ExternalId starting with 'UC', which is used by the "
                   f"YouTube backend to track channels (received: "
                   f"{repr(TEST_PROPERTIES['channel_id'][:-2])})")
        self.assertEqual(str(err.exception), err_msg)

        # channel id doesn't start with 'UC'
        bad_start = f"XX{TEST_PROPERTIES['channel_id'][2:]}"
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES, "channel_id": bad_start})
        err_msg = (f"[Channel.id] `id` must be a unique 24-character "
                   f"ExternalId starting with 'UC', which is used by the "
                   f"YouTube backend to track channels (received: "
                   f"{repr(bad_start)})")
        self.assertEqual(str(err.exception), err_msg)

        # assignment outside init
        c = Channel(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            c.id = "something else"
        err_msg = "[Channel.id] `id` cannot be changed outside of init"
        self.assertEqual(str(err.exception), err_msg)

    def test_channel_name_errors(self):
        # bad channel name type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "channel_name": 123})
        err_msg = ("[Channel.name] `name` must be a non-empty string "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # empty channel name
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES, "channel_name": ""})
        err_msg = ("[Channel.name] `name` must be a non-empty string "
                   "(received: '')")
        self.assertEqual(str(err.exception), err_msg)

    def test_last_updated_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "last_updated": 123})
        err_msg = ("[Channel.last_updated] `last_updated` must be a "
                   "datetime.datetime object stating the last time this "
                   "channel was checked for updates (received object of type: "
                   "<class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES,
                       "last_updated": datetime(9999, 12, 31)})
        err_msg = (f"[Channel.last_updated] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"channel was checked for updates "
                   f"({datetime(9999, 12, 31)} > ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

        # assignment outside init
        c = Channel(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            c.last_updated = datetime.now()
        err_msg = ("[Channel.last_updated] `last_updated` cannot be changed "
                   "outside of init")
        self.assertEqual(str(err.exception), err_msg)

    def test_video_ids_errors(self):
        self.maxDiff = None
        test_ids = TEST_PROPERTIES["video_ids"]

        # bad id type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "video_ids": str(test_ids)})
        err_msg = ("[Channel.video_ids] `video_ids` must be a list, tuple, or "
                   "set of 11-character video ids used by the YouTube backend "
                   "to track videos (received object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad id type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "video_ids": test_ids + [123]})
        err_msg = ("[Channel.video_ids] `video_ids` must be a list, tuple, or "
                   "set of 11-character video ids used by the YouTube backend "
                   "to track videos (received id of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad id length
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES,
                       "video_ids": test_ids + ["not11characters"]})
        err_msg = ("[Channel.video_ids] `video_ids` must be a list, tuple, or "
                   "set of 11-character video ids used by the YouTube backend "
                   "to track videos (encountered malformed video id: "
                   "'not11characters')")
        self.assertEqual(str(err.exception), err_msg)

    def test_about_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "about_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'about')")
        self.assertEqual(str(err.exception), err_msg)

    def test_community_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "community_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'community')")
        self.assertEqual(str(err.exception), err_msg)

    def test_featured_channels_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "featured_channels_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'featured_channels')")
        self.assertEqual(str(err.exception), err_msg)

    def test_videos_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "videos_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'videos')")
        self.assertEqual(str(err.exception), err_msg)

    def test_workers_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "workers": 1.5})
        err_msg = ("[Channel.workers] `workers` must be an integer > 0 or "
                   "None to use all available resources (received object of "
                   "type: <class 'float'>)")
        self.assertEqual(str(err.exception), err_msg)

        # < 1
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES, "workers": 0})
        err_msg = ("[Channel.workers] `workers` must be an integer > 0 or "
                   "None to use all available resources (received: 0)")
        self.assertEqual(str(err.exception), err_msg)

    def test_target_dir_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**TEST_PROPERTIES, "target_dir": "abc"})
        err_msg = ("[Channel.target_dir] `target_dir` must be a Path-like "
                   "object pointing to a directory on local storage in which "
                   "to store the contents of this channel (received object of "
                   "type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # points to file
        with self.assertRaises(ValueError) as err:
            Channel(**{**TEST_PROPERTIES, "target_dir": Path(__file__)})
        err_msg = (f"[Channel.target_dir] `target_dir` must be a Path-like "
                   f"object pointing to a directory on local storage in which "
                   f"to store the contents of this channel (path points to "
                   f"file: {Path(__file__)})")
        self.assertEqual(str(err.exception), err_msg)


class BasicChannelTests(unittest.TestCase):

    def test_to_json(self):
        c = Channel(**TEST_PROPERTIES)
        json_path = Path(ROOT_DIR, "datatube", "test", 
                         "channel_test_json.json")
        json_path.unlink(missing_ok=True)
        json_dict = c.to_json(json_path=json_path)
        expected = {
            "datatube_version": DATATUBE_VERSION_NUMBER,
            "channel_id": TEST_PROPERTIES["channel_id"],
            "channel_name": TEST_PROPERTIES["channel_name"],
            "last_updated": TEST_PROPERTIES["last_updated"].isoformat(),
            "html": {
                "about": TEST_PROPERTIES["about_html"],
                "community": TEST_PROPERTIES["community_html"],
                "featured_channels": TEST_PROPERTIES["featured_channels_html"],
                "videos": TEST_PROPERTIES["videos_html"]
            } 
        }
        self.assertEqual(json_dict, expected)
        self.assertTrue(json_path.exists())
        with json_path.open("r") as json_file:
            test_json = json.load(json_file)
        self.assertEqual(test_json, expected)

    def test_contains(self):
        c = Channel(**TEST_PROPERTIES)

        # in channel
        in_channel = {
            "source": "local",
            "video_id": "NeOBvwRfBWc",
            "video_title": "asdf",
            "publish_date": datetime.now(),
            "last_updated": datetime.now(),
            "duration": timedelta(seconds=1),
            "views": 1,
            "rating": 5,
            "likes": 1,
            "dislikes": 0,
            "description": "asdf",
            "keywords": [],
            "thumbnail_url": "asdf",
            "target_dir": Path(VIDEO_DIR, TEST_PROPERTIES["channel_id"],
                               "NeOBvwRfBWc"),
            "streams": pytube.StreamQuery([]),
            "captions": pytube.CaptionQuery([]),
            "channel": None
        }
        self.assertTrue(Video(**in_channel) in c)
        self.assertTrue(in_channel["video_id"] in c)

        # not in channel
        not_in_channel = {
            "source": "local",
            "video_id": "DifferentId",  # still 11 characters
            "video_title": "asdf",
            "publish_date": datetime.now(),
            "last_updated": datetime.now(),
            "duration": timedelta(seconds=1),
            "views": 1,
            "rating": 5,
            "likes": 1,
            "dislikes": 0,
            "description": "asdf",
            "keywords": [],
            "thumbnail_url": "asdf",
            "target_dir": Path(VIDEO_DIR, TEST_PROPERTIES["channel_id"],
                               "DifferentId"),
            "streams": pytube.StreamQuery([]),
            "captions": pytube.CaptionQuery([]),
            "channel": None
        }
        self.assertFalse(Video(**not_in_channel) in c)
        self.assertFalse(not_in_channel["video_id"] in c)

    def test_equality(self):
        c1 = Channel(**TEST_PROPERTIES)
        c2 = Channel(**TEST_PROPERTIES)
        self.assertEqual(c1, c2)
        # Rick Astley
        c3 = Channel(**{**TEST_PROPERTIES,
                        "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw"})
        self.assertNotEqual(c1, c3)
        c4 = Channel(**{**TEST_PROPERTIES, "last_updated": datetime.now()})
        self.assertNotEqual(c1, c4)

    def test_length(self):
        c = Channel(**TEST_PROPERTIES)
        self.assertEqual(len(c), len(TEST_PROPERTIES["video_ids"]))

    def test_str(self):
        c = Channel(**TEST_PROPERTIES)
        expected = (f"[{TEST_PROPERTIES['last_updated']}] "
                    f"{TEST_PROPERTIES['channel_name']} "
                    f"({len(TEST_PROPERTIES['video_ids'])})")
        self.assertEqual(str(c), expected)


class PytubeChannelTests(unittest.TestCase):

    channel_url = channel_id_to_url(TEST_PROPERTIES["channel_id"])

    def test_load_from_pytube_caching(self):
        def time_get():
            start = time.perf_counter()
            Channel.from_pytube(self.channel_url)
            end = time.perf_counter()
            return end - start

        times = [time_get() for _ in range(5)]
        self.assertTrue(sum(times) < 2 * times[0])

    def test_load_from_pytube(self):
        c = Channel.from_pytube(self.channel_url)
        self.assertEqual(c.source, "pytube")
        self.assertEqual(c.id, TEST_PROPERTIES["channel_id"])
        self.assertEqual(c.name, TEST_PROPERTIES["channel_name"])
        self.assertTrue(isinstance(c.video_ids, list))
        self.assertTrue(len(c.video_ids) > 0)
        self.assertTrue(all(isinstance(v_id, str) for v_id in c.video_ids))
        self.assertTrue(all(is_video_id(v_id) for v_id in c.video_ids))
        self.assertEqual(c.last_updated.date(), datetime.now().date())
        self.assertTrue(isinstance(c.html["about"], str) and
                        len(c.html["about"]) > 0)
        self.assertTrue(isinstance(c.html["community"], str) and
                        len(c.html["community"]) > 0)
        self.assertTrue(isinstance(c.html["featured_channels"], str) and
                        len(c.html["featured_channels"]) > 0)
        self.assertTrue(isinstance(c.html["videos"], str) and
                        len(c.html["videos"]) > 0)
        self.assertEqual(c.workers, TEST_PROPERTIES["workers"])
