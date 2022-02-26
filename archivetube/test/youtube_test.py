from datetime import datetime
from pathlib import Path
import unittest

from archivetube import VIDEO_DIR
from archivetube.youtube import Channel, channel_id_to_url


TEST_CHANNEL_ID = "UCBR8-60-B28hp2BmDPdntcQ"  # YouTube official


class ChannelParameterCheckTests(unittest.TestCase):

    def test_check_source(self):
        # good sources
        for source in ["local", "pytube", "sql"]:
            Channel.check.source(source)

        # bad source type
        with self.assertRaises(TypeError) as err:
            Channel.check.source(123)
        err_msg = ("[test_check_source] `source` must be a string with one "
                   "of the following values: ('local', 'pytube', 'sql') "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad source value
        with self.assertRaises(ValueError) as err:
            Channel.check.source("bad source value")
        err_msg = ("[test_check_source] `source` must be a string with one "
                   "of the following values: ('local', 'pytube', 'sql') "
                   "(received: 'bad source value')")
        self.assertEqual(str(err.exception), err_msg)

    def test_check_channel_id(self):
        # good channel id
        Channel.check.channel_id(TEST_CHANNEL_ID)

        # bad channel id type
        with self.assertRaises(TypeError) as err:
            Channel.check.channel_id(123)
        err_msg = ("[test_check_channel_id] `channel_id` must be a unique "
                   "24-character channel id starting with 'UC', which is used "
                   "by the YouTube backend to track channels (received object "
                   "of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad channel id length
        with self.assertRaises(ValueError) as err:
            Channel.check.channel_id(TEST_CHANNEL_ID[:-2])
        err_msg = (f"[test_check_channel_id] `channel_id` must be a unique "
                   f"24-character channel id starting with 'UC', which is used "
                   f"by the YouTube backend to track channels (received: "
                   f"{repr(TEST_CHANNEL_ID[:-2])})")
        self.assertEqual(str(err.exception), err_msg)

        # channel id doesn't start with 'UC'
        bad_start = f"XX{TEST_CHANNEL_ID[2:]}"
        with self.assertRaises(ValueError) as err:
            Channel.check.channel_id(bad_start)
        err_msg = (f"[test_check_channel_id] `channel_id` must be a unique "
                   f"24-character channel id starting with 'UC', which is used "
                   f"by the YouTube backend to track channels (received: "
                   f"{repr(bad_start)})")
        self.assertEqual(str(err.exception), err_msg)

    def test_check_channel_name(self):
        # good channel name
        Channel.check.channel_name("YouTube")

        # bad channel name type
        with self.assertRaises(TypeError) as err:
            Channel.check.channel_name(123)
        err_msg = ("[test_check_channel_name] `channel_name` must be a "
                   "non-empty string (received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # empty channel name
        with self.assertRaises(ValueError) as err:
            Channel.check.channel_name("")
        err_msg = ("[test_check_channel_name] `channel_name` must be a "
                   "non-empty string (received: '')")
        self.assertEqual(str(err.exception), err_msg)

    def test_check_video_ids(self):
        # good ids
        test_ids = ["NeOBvwRfBWc", "QltYNmVUvh0", "SYQJPkiNJfE", "3WSmP7i9my8",
                    "TBuNVQ54dgg"]  # taken from official YouTube channel
        Channel.check.video_ids(test_ids)

        # bad id type
        with self.assertRaises(TypeError) as err:
            Channel.check.video_ids(set(test_ids))
        err_msg = ("[test_check_video_ids] `video_ids` must be a list or "
                   "tuple of unique 11-character video ids referencing the "
                   "video contents of this channel (received object of type: "
                   "<class 'set'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad id type
        with self.assertRaises(TypeError) as err:
            Channel.check.video_ids(test_ids + [123])
        err_msg = ("[test_check_video_ids] `video_id` must be a unique "
                   "11-character video id used by the YouTube backend to "
                   "track videos (received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad id length
        with self.assertRaises(ValueError) as err:
            Channel.check.video_ids(test_ids + ["not11characters"])
        err_msg = ("[test_check_video_ids] `video_id` must be a unique "
                   "11-character video id used by the YouTube backend to "
                   "track videos (received: 'not11characters')")
        self.assertEqual(str(err.exception), err_msg)
                
    def test_check_last_updated(self):
        # good timestamp
        Channel.check.last_updated(datetime.now())

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.last_updated(123)
        err_msg = ("[test_check_last_updated] `last_updated` must be a "
                   "datetime.datetime object stating the last time this "
                   "channel was checked for updates (received object of type: "
                   "<class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        with self.assertRaises(ValueError) as err:
            Channel.check.last_updated(datetime(9999, 12, 31))
        err_msg = (f"[test_check_last_updated] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"channel was checked for updates "
                   f"({datetime(9999, 12, 31)} > ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

    def test_check_about_html(self):
        # good html
        Channel.check.about_html("some ridiculously long html code")

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.about_html(123)
        err_msg = ("[test_check_about_html] `about_html` must be a string "
                   "containing the html response of the channel's 'About' "
                   "page, or None if it does not have one (received object "
                   "of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        self.assertEqual(Channel.check.about_html(None), "")

    def test_check_community_html(self):
        # good html
        Channel.check.community_html("some ridiculously long html code")

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.community_html(123)
        err_msg = ("[test_check_community_html] `community_html` must be a "
                   "string containing the html response of the channel's "
                   "'Community' page, or None if it does not have one "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        self.assertEqual(Channel.check.community_html(None), "")

    def test_check_featured_channels_html(self):
        # good html
        Channel.check.featured_channels_html("some ridiculously long html code")

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.featured_channels_html(123)
        err_msg = ("[test_check_featured_channels_html] "
                   "`featured_channels_html` must be a string containing the "
                   "html response of the channel's 'Featured Channels' page, "
                   "or None if it does not have one (received object of type: "
                   "<class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        self.assertEqual(Channel.check.featured_channels_html(None), "")

    def test_check_videos_html(self):
        # good html
        Channel.check.videos_html("some ridiculously long html code")

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.videos_html(123)
        err_msg = ("[test_check_videos_html] `videos_html` must be a string "
                   "containing the html response of the channel's 'Videos' "
                   "page, or None if it does not have one (received object "
                   "of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        self.assertEqual(Channel.check.videos_html(None), "")

    def test_check_workers(self):
        # good workers
        Channel.check.workers(1)

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.workers(1.5)
        err_msg = ("[test_check_workers] `workers` must be an integer > 0, "
                   "or None to use all available resources (received object "
                   "of type: <class 'float'>)")
        self.assertEqual(str(err.exception), err_msg)

        # < 1
        with self.assertRaises(ValueError) as err:
            Channel.check.workers(0)
        err_msg = ("[test_check_workers] `workers` must be an integer > 0, "
                   "or None to use all available resources (received: 0)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        self.assertIsNone(Channel.check.workers(None))

    def test_check_parent_dir(self):
        # good dir
        Channel.check.parent_dir(Path(__file__).resolve().parent)

        # bad type
        with self.assertRaises(TypeError) as err:
            Channel.check.parent_dir("abc")
        err_msg = ("[test_check_parent_dir] `parent_dir` must be a Path-like "
                   "object pointing to a directory on local storage to "
                   "load/download content to, or None to use the default "
                   "directory structure (received object of type: "
                   "<class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # does not exist
        with self.assertRaises(ValueError) as err:
            Channel.check.parent_dir(Path("does_not_exist"))
        err_msg = ("[test_check_parent_dir] `parent_dir` must be a Path-like "
                   "object pointing to a directory on local storage to "
                   "load/download content to, or None to use the default "
                   "directory structure (directory does not exist: "
                   "does_not_exist)")
        self.assertEqual(str(err.exception), err_msg)

        # points to file
        with self.assertRaises(ValueError) as err:
            Channel.check.parent_dir(Path(__file__))
        err_msg = ("[test_check_parent_dir] `parent_dir` must be a Path-like "
                   "object pointing to a directory on local storage to "
                   "load/download content to, or None to use the default "
                   "directory structure (directory does not exist: ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

        # None
        self.assertEqual(Channel.check.parent_dir(None), VIDEO_DIR)


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
        "community_html": None,
        "featured_channels_html": "",
        "videos_html": None,
        "workers": 1,
        "parent_dir": VIDEO_DIR
    }

    def test_init_good_input(self):
        c = Channel(**self.properties)
        self.assertEqual(c.source, "local")
        self.assertEqual(c.info["channel_id"], TEST_CHANNEL_ID)
        self.assertEqual(c.info["channel_name"], "YouTube")
        self.assertEqual(c.video_ids, ["NeOBvwRfBWc", "QltYNmVUvh0",
                                       "SYQJPkiNJfE", "3WSmP7i9my8",
                                       "TBuNVQ54dgg"]),
        self.assertEqual(c.info["last_updated"], self.current_time)
        self.assertEqual(c.info["about_html"], "")
        self.assertEqual(c.info["community_html"], "")
        self.assertEqual(c.info["featured_channels_html"], "")
        self.assertEqual(c.info["videos_html"], "")
        self.assertEqual(c.workers, 1)
        self.assertEqual(c.target_dir, Path(VIDEO_DIR, c.info["channel_id"]))

    def test_init_bad_input(self):
        # bad source
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "source": 123})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "source": "bad source type"})

        # bad channel_id
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "channel_id": 123})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "channel_id": TEST_CHANNEL_ID[:-2]})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties,
                       "channel_id": f"XX{TEST_CHANNEL_ID[2:]}"})

        # bad channel_name
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "channel_name": 123})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "channel_name": ""})

        # bad video_ids
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "video_ids": set()})
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "video_ids": [123]})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "video_ids": ["not11characters"]})

        # bad last_updated
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "last_updated": 123})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties,
                       "last_updated": datetime(9999, 12, 31)})

        # bad about_html
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "about_html": 123})

        # bad community_html
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "community_html": 123})

        # bad featured_channels_html
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "featured_channels_html": 123})

        # bad videos_html
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "videos_html": 123})

        # bad workers
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "workers": "abc"})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "workers": 0})

        # bad parent_dir
        with self.assertRaises(TypeError):
            Channel(**{**self.properties, "parent_dir": "abc"})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "parent_dir": Path("does_not_exist")})
        with self.assertRaises(ValueError):
            Channel(**{**self.properties, "parent_dir": Path(__file__)})

    def test_length(self):
        c = Channel(**self.properties)
        self.assertEqual(len(c), len(self.properties["video_ids"]))

    def test_equality(self):
        c1 = Channel(**self.properties)
        c2 = Channel(**self.properties)
        self.assertEqual(c1, c2)
        c1.info["channel_id"] = "UCuAXFkgsw1L7xaCfnd5JJOw"  # Rick Astley
        self.assertNotEqual(c1, c2)
        c1.info["channel_id"] = TEST_CHANNEL_ID
        c1.info["last_updated"] = datetime.now()
        self.assertNotEqual(c1, c2)


class PytubeChannelTests(unittest.TestCase):

    channel_url = channel_id_to_url(TEST_CHANNEL_ID)

    def test_load_from_pytube(self):
        c = Channel.from_pytube(self.channel_url, progress_bar=False)
