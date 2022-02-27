from datetime import datetime
import json
from pathlib import Path
import unittest

from archivetube import ROOT_DIR, VIDEO_DIR
from archivetube.youtube import Channel, channel_id_to_url


TEST_CHANNEL_ID = "UCBR8-60-B28hp2BmDPdntcQ"  # YouTube official


class BasicChannelTests(unittest.TestCase):

    current_time = datetime.now()
    properties = {
        "source": "local",
        "channel_id": TEST_CHANNEL_ID,
        "channel_name": "YouTube",
        "video_ids": ["NeOBvwRfBWc", "QltYNmVUvh0", "SYQJPkiNJfE", "3WSmP7i9my8",
                      "TBuNVQ54dgg"],  # taken from official YouTube channel,
        "last_updated": current_time,
        "about_html": "",
        "community_html": "",
        "featured_channels_html": "",
        "videos_html": "",
        "workers": 1,
        "target_dir": Path(ROOT_DIR, "archivetube", "test", "test_channels",
                           TEST_CHANNEL_ID)
    }

    def test_init_good_input(self):
        c = Channel(**self.properties)
        self.assertEqual(c.source, "local")
        self.assertEqual(c.id, TEST_CHANNEL_ID)
        self.assertEqual(c.name, "YouTube")
        self.assertEqual(c.video_ids, ["NeOBvwRfBWc", "QltYNmVUvh0",
                                       "SYQJPkiNJfE", "3WSmP7i9my8",
                                       "TBuNVQ54dgg"]),
        self.assertEqual(c.last_updated, self.current_time)
        self.assertEqual(c.html["about"], "")
        self.assertEqual(c.html["community"], "")
        self.assertEqual(c.html["featured_channels"], "")
        self.assertEqual(c.html["videos"], "")
        self.assertEqual(c.workers, 1)
        self.assertEqual(c.target_dir, self.properties["target_dir"])

    def test_source_errors(self):
        # bad source type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "source": 123})
        err_msg = ("[Channel.source] `source` must be a string with one of "
                   "the following values: ('local', 'pytube', 'sql') "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad source value
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties, "source": "bad source value"})
        err_msg = ("[Channel.source] `source` must be a string with one of "
                   "the following values: ('local', 'pytube', 'sql') "
                   "(received: 'bad source value')")
        self.assertEqual(str(err.exception), err_msg)

    def test_channel_id_errors(self):
        # bad channel id type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "channel_id": 123})
        err_msg = ("[Channel.id] `id` must be a unique 24-character "
                   "ExternalId starting with 'UC', which is used by the "
                   "YouTube backend to track channels (received object of "
                   "type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad channel id length
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties, "channel_id": TEST_CHANNEL_ID[:-2]})
        err_msg = (f"[Channel.id] `id` must be a unique 24-character "
                   f"ExternalId starting with 'UC', which is used by the "
                   f"YouTube backend to track channels (received: "
                   f"{repr(TEST_CHANNEL_ID[:-2])})")
        self.assertEqual(str(err.exception), err_msg)

        # channel id doesn't start with 'UC'
        bad_start = f"XX{TEST_CHANNEL_ID[2:]}"
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties, "channel_id": bad_start})
        err_msg = (f"[Channel.id] `id` must be a unique 24-character "
                   f"ExternalId starting with 'UC', which is used by the "
                   f"YouTube backend to track channels (received: "
                   f"{repr(bad_start)})")
        self.assertEqual(str(err.exception), err_msg)

    def test_channel_name_errors(self):
        # bad channel name type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "channel_name": 123})
        err_msg = ("[Channel.name] `name` must be a non-empty string "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # empty channel name
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties, "channel_name": ""})
        err_msg = ("[Channel.name] `name` must be a non-empty string "
                   "(received: '')")
        self.assertEqual(str(err.exception), err_msg)

    def test_last_updated_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "last_updated": 123})
        err_msg = ("[Channel.last_updated] `last_updated` must be a "
                   "datetime.datetime object stating the last time this "
                   "channel was checked for updates (received object of type: "
                   "<class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties,
                       "last_updated": datetime(9999, 12, 31)})
        err_msg = (f"[Channel.last_updated] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"channel was checked for updates "
                   f"({datetime(9999, 12, 31)} > ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

    def test_video_ids_errors(self):
        test_ids = self.properties["video_ids"]

        # bad id type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "video_ids": str(test_ids)})
        err_msg = ("[Channel.video_ids] `video_ids` must be a list, tuple, or "
                   "set of unique 11-character video id strings referencing "
                   "the video contents of this channel (received object of "
                   "type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad id type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "video_ids": test_ids + [123]})
        err_msg = ("[Channel.video_ids] `video_ids` must be a list, tuple, or "
                   "set of unique 11-character video id strings referencing "
                   "the video contents of this channel (received video id of "
                   "type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad id length
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties,
                       "video_ids": test_ids + ["not11characters"]})
        err_msg = ("[Channel.video_ids] `video_ids` must be a list, tuple, or "
                   "set of unique 11-character video id strings referencing "
                   "the video contents of this channel (received malformed "
                   "video id: 'not11characters')")
        self.assertEqual(str(err.exception), err_msg)

    def test_about_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "about_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'about')")
        self.assertEqual(str(err.exception), err_msg)

    def test_community_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "community_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'community')")
        self.assertEqual(str(err.exception), err_msg)

    def test_featured_channels_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "featured_channels_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'featured_channels')")
        self.assertEqual(str(err.exception), err_msg)

    def test_videos_html_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "videos_html": 123})
        err_msg = ("[Channel.html] `html` must be a registry of raw html "
                   "response strings for the current channel (received value "
                   "of type: <class 'int'> for key: 'videos')")
        self.assertEqual(str(err.exception), err_msg)

    def test_workers_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "workers": 1.5})
        err_msg = ("[Channel.workers] `workers` must be an integer > 0 or "
                   "None to use all available resources (received object of "
                   "type: <class 'float'>)")
        self.assertEqual(str(err.exception), err_msg)

        # < 1
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties, "workers": 0})
        err_msg = ("[Channel.workers] `workers` must be an integer > 0 or "
                   "None to use all available resources (received: 0)")
        self.assertEqual(str(err.exception), err_msg)

    def test_target_dir_errors(self):
        # bad type
        with self.assertRaises(TypeError) as err:
            Channel(**{**self.properties, "target_dir": "abc"})
        err_msg = ("[Channel.target_dir] `target_dir` must be a Path-like "
                   "object pointing to a directory on local storage in which "
                   "to store the contents of this channel (received object of "
                   "type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # points to file
        with self.assertRaises(ValueError) as err:
            Channel(**{**self.properties, "target_dir": Path(__file__)})
        err_msg = ("[Channel.target_dir] `target_dir` must be a Path-like "
                   "object pointing to a directory on local storage in which "
                   "to store the contents of this channel (path points to "
                   "file: ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

    def test_to_json(self):
        c = Channel(**self.properties)
        json_path = Path(ROOT_DIR, "archivetube", "test", "test_json.json")
        json_path.unlink(missing_ok=True)
        json_dict = c.to_json(json_path=json_path)
        expected = {
            "channel_id": self.properties["channel_id"],
            "channel_name": self.properties["channel_name"],
            "last_updated": self.properties["last_updated"].isoformat(),
            "html": {
                "about": self.properties["about_html"],
                "community": self.properties["community_html"],
                "featured_channels": self.properties["featured_channels_html"],
                "videos": self.properties["videos_html"]
            } 
        }
        self.assertEqual(json_dict, expected)
        self.assertTrue(json_path.exists())
        with json_path.open("r") as json_file:
            test_json = json.load(json_file)
        self.assertEqual(test_json, expected)

    def test_length(self):
        c = Channel(**self.properties)
        self.assertEqual(len(c), len(self.properties["video_ids"]))

    def test_equality(self):
        c1 = Channel(**self.properties)
        c2 = Channel(**self.properties)
        self.assertEqual(c1, c2)
        c1.id = "UCuAXFkgsw1L7xaCfnd5JJOw"  # Rick Astley
        self.assertNotEqual(c1, c2)
        c1.id = TEST_CHANNEL_ID
        c1.last_updated = datetime.now()
        self.assertNotEqual(c1, c2)


class PytubeChannelTests(unittest.TestCase):

    channel_url = channel_id_to_url(TEST_CHANNEL_ID)

    def test_load_from_pytube(self):
        c = Channel.from_pytube(self.channel_url, progress_bar=False)
