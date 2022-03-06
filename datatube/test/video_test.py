from datetime import datetime, timedelta
import json
from pathlib import Path
import time
import unittest

import pytube

from datatube import DATATUBE_VERSION_NUMBER, ROOT_DIR, VIDEO_DIR
from datatube.youtube import Channel, Video, is_url, video_id_to_url


TEST_VIDEO_ID = "dQw4w9WgXcQ"
TEST_CHANNEL_ID = "UCuAXFkgsw1L7xaCfnd5JJOw"
TEST_CHANNEL_PROPERTIES = {
    "source": "local",
    "channel_id": TEST_CHANNEL_ID,
    "channel_name": "Rick Astley",
    "video_ids": [TEST_VIDEO_ID, "DifferentId"],
    "last_updated": datetime.now(),
    "about_html": "",
    "community_html": "",
    "featured_channels_html": "",
    "videos_html": "",
    "workers": 1,
    "target_dir": Path(ROOT_DIR, "datatube", "test", "test_data",
                       TEST_CHANNEL_ID)
}
TEST_PROPERTIES = {
    "source": "local",
    "video_id": TEST_VIDEO_ID,
    "video_title": ("Rick Astley - Never Gonna Give You Up (Official "
                    "Music Video)"),
    "publish_date": datetime(2009, 10, 24),
    "last_updated": datetime.now(),
    "duration": timedelta(minutes=3, seconds=32),
    "views": 1159577739,
    "rating": 4.86,
    "likes": 13000000,
    "dislikes": 364000,
    "description": """
        The official video for “Never Gonna Give You Up” by Rick Astley

        “Never Gonna Give You Up” was a global smash on its release in July 1987, topping the charts in 25 countries including Rick’s native UK and the US Billboard Hot 100.  It also won the Brit Award for Best single in 1988. Stock Aitken and Waterman wrote and produced the track which was the lead-off single and lead track from Rick’s debut LP “Whenever You Need Somebody”.  The album was itself a UK number one and would go on to sell over 15 million copies worldwide.

        The legendary video was directed by Simon West – who later went on to make Hollywood blockbusters such as Con Air, Lara Croft – Tomb Raider and The Expendables 2.  The video passed the 1bn YouTube views milestone on 28 July 2021.

        Subscribe to the official Rick Astley YouTube channel: https://RickAstley.lnk.to/YTSubID

        Follow Rick Astley:
        Facebook: https://RickAstley.lnk.to/FBFollowID 
        Twitter: https://RickAstley.lnk.to/TwitterID 
        Instagram: https://RickAstley.lnk.to/InstagramID 
        Website: https://RickAstley.lnk.to/storeID 
        TikTok: https://RickAstley.lnk.to/TikTokID

        Listen to Rick Astley:
        Spotify: https://RickAstley.lnk.to/SpotifyID 
        Apple Music: https://RickAstley.lnk.to/AppleMusicID 
        Amazon Music: https://RickAstley.lnk.to/AmazonMusicID 
        Deezer: https://RickAstley.lnk.to/DeezerID 

        Lyrics:
        We’re no strangers to love
        You know the rules and so do I
        A full commitment’s what I’m thinking of
        You wouldn’t get this from any other guy

        I just wanna tell you how I’m feeling
        Gotta make you understand

        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you

        We’ve known each other for so long
        Your heart’s been aching but you’re too shy to say it
        Inside we both know what’s been going on
        We know the game and we’re gonna play it

        And if you ask me how I’m feeling
        Don’t tell me you’re too blind to see

        Never gonna give you up
        Never gonna let you down
        Never gonna run around and desert you
        Never gonna make you cry
        Never gonna say goodbye
        Never gonna tell a lie and hurt you

        #RickAstley #NeverGonnaGiveYouUp #WheneverYouNeedSomebody #OfficialMusicVideo
    """,
    "keywords": ["RickAstley", "NeverGonnaGiveYouUp",
                    "WheneverYouNeedSomebody", "OfficialMusicVideo"],
    "thumbnail_url": "asdf",
    "target_dir": Path(VIDEO_DIR, TEST_CHANNEL_ID, TEST_VIDEO_ID),
    "streams": pytube.StreamQuery([]),
    "captions": pytube.CaptionQuery([]),
    "channel": Channel(**TEST_CHANNEL_PROPERTIES)
}


class VideoErrorTests(unittest.TestCase):

    def test_init_good_input(self):
        v = Video(**TEST_PROPERTIES)
        self.assertEqual(v.source, TEST_PROPERTIES["source"])
        self.assertEqual(v.id, TEST_PROPERTIES["video_id"])
        self.assertEqual(v.title, TEST_PROPERTIES["video_title"])
        self.assertEqual(v.publish_date, TEST_PROPERTIES["publish_date"])
        self.assertEqual(v.last_updated, TEST_PROPERTIES["last_updated"])
        self.assertEqual(v.duration, TEST_PROPERTIES["duration"])
        self.assertEqual(v.stats["views"], TEST_PROPERTIES["views"])
        self.assertEqual(v.stats["rating"], TEST_PROPERTIES["rating"])
        self.assertEqual(v.stats["likes"], TEST_PROPERTIES["likes"])
        self.assertEqual(v.stats["dislikes"], TEST_PROPERTIES["dislikes"])
        self.assertEqual(v.description, TEST_PROPERTIES["description"])
        self.assertEqual(v.keywords, TEST_PROPERTIES["keywords"])
        self.assertEqual(v.thumbnail_url, TEST_PROPERTIES["thumbnail_url"])
        self.assertEqual(v.target_dir, TEST_PROPERTIES["target_dir"])
        self.assertEqual(v.streams, TEST_PROPERTIES["streams"])
        self.assertEqual(v.captions, TEST_PROPERTIES["captions"])
        self.assertEqual(v.channel, TEST_PROPERTIES["channel"])

    def test_source_errors(self):
        # bad source type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "source": 123})
        err_msg = ("[Video.source] `source` must be a string with one of "
                   "the following values: ('local', 'pytube', 'sql') "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad source value
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "source": "bad source value"})
        err_msg = ("[Video.source] `source` must be a string with one of "
                   "the following values: ('local', 'pytube', 'sql') "
                   "(received: 'bad source value')")
        self.assertEqual(str(err.exception), err_msg)

        # assignment outside init
        v = Video(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            v.source = "something else"
        err_msg = ("[Video.source] `source` cannot be changed outside of "
                   "init.  Construct a new Video object instead")
        self.assertEqual(str(err.exception), err_msg)

    def test_video_id_errors(self):
        # bad video_id type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "video_id": 123})
        err_msg = ("[Video.id] `id` must be a unique 11-character id string "
                   "used by the YouTube backend to track videos (received "
                   "object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # bad video_id length
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "video_id": "not11characters"})
        err_msg = ("[Video.id] `id` must be a unique 11-character id string "
                   "used by the YouTube backend to track videos (received: "
                   "'not11characters')")
        self.assertEqual(str(err.exception), err_msg)

        # assignment outside init
        v = Video(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            v.id = "something else"
        err_msg = "[Video.id] `id` cannot be changed outside of init"
        self.assertEqual(str(err.exception), err_msg)

    def test_video_title_errors(self):
        # bad video_title type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "video_title": 123})
        err_msg = ("[Video.title] `title` must be a non-empty string "
                   "(received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # title is empty string
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "video_title": ""})
        err_msg = ("[Video.title] `title` must be a non-empty string "
                   "(received: '')")
        self.assertEqual(str(err.exception), err_msg)

    def test_publish_date_errors(self):
        # bad publish_date type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "publish_date": 123})
        err_msg = ("[Video.publish_date] `publish_date` must be a "
                   "datetime.datetime object stating the last time this video "
                   "was checked for updates (received object of type: "
                   "<class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # publish_date in the future
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "publish_date": datetime(9999, 12, 31)})
        err_msg = (f"[Video.publish_date] `publish_date` must be a "
                   f"datetime.datetime object stating the last time this video "
                   f"was checked for updates ({datetime(9999, 12, 31)} > ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

    def test_last_updated_errors(self):
        # bad last_updated type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "last_updated": 123})
        err_msg = ("[Video.last_updated] `last_updated` must be a "
                   "datetime.datetime object stating the last time this "
                   "video was checked for updates (received object of type: "
                   "<class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # in the future
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "last_updated": datetime(9999, 12, 31)})
        err_msg = (f"[Video.last_updated] `last_updated` must be a "
                   f"datetime.datetime object stating the last time this "
                   f"video was checked for updates ({datetime(9999, 12, 31)} "
                   f"> ")
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

        # assignment outside init
        v = Video(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            v.last_updated = datetime.now()
        err_msg = ("[Video.last_updated] `last_updated` cannot be changed "
                   "outside of init")
        self.assertEqual(str(err.exception), err_msg)

    def test_duration_errors(self):
        # bad duration type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "duration": 123})
        err_msg = ("[Video.duration] `duration` must be a datetime.timedelta "
                   "object describing the duration of the video (received "
                   "object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative duration
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "duration": timedelta(seconds=-1)})
        err_msg = (f"[Video.duration] `duration` must be a datetime.timedelta "
                   f"object describing the duration of the video "
                   f"({timedelta(seconds=-1)} < {timedelta()})")
        self.assertEqual(str(err.exception), err_msg)

    def test_stats_errors(self):
        # bad views type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "views": "abc"})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('views' must be "
                   "an integer, received object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative views
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "views": -1})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('views' must be "
                   ">= 0, received: -1)")
        self.assertEqual(str(err.exception), err_msg)

        # bad rating type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "rating": "abc"})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('rating' must be "
                   "an integer or float, received object of type: "
                   "<class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative rating
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "rating": -0.1})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('rating' must be "
                   "between 0 and 5, received: -0.1)")
        self.assertEqual(str(err.exception), err_msg)

        # rating > 5
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "rating": 5.5})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('rating' must be "
                   "between 0 and 5, received: 5.5)")
        self.assertEqual(str(err.exception), err_msg)

        # bad likes type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "likes": "abc"})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('likes' must be "
                   "an integer, received object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative likes
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "likes": -1})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('likes' must be "
                   ">= 0, received: -1)")
        self.assertEqual(str(err.exception), err_msg)

        # bad likes type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "dislikes": "abc"})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('dislikes' must "
                   "be an integer, received object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # negative likes
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "dislikes": -1})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video ('dislikes' must "
                   "be >= 0, received: -1)")
        self.assertEqual(str(err.exception), err_msg)

        # likes + dislikes, but no rating
        v = Video(**{**TEST_PROPERTIES, "rating": None})
        self.assertAlmostEqual(v.stats["rating"], TEST_PROPERTIES["rating"],
                               places=2)
        self.assertTrue("likes" in v.stats)
        self.assertTrue("dislikes" in v.stats)

        # rating, but no likes + dislikes
        v = Video(**{**TEST_PROPERTIES, "likes": None, "dislikes": None})
        self.assertFalse("likes" in v.stats)
        self.assertFalse("dislikes" in v.stats)

        # not enough info to compute rating
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "rating": None, "dislikes": None})
        err_msg = ("[Video.stats] `stats` must be a dictionary containing the "
                   "view and rating statistics of the video (not enough "
                   "information to compute rating: no 'rating' entry and no "
                   "'likes' and 'dislikes' to compute it)")
        self.assertEqual(str(err.exception), err_msg)

    def test_description_errors(self):
        # bad description type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "description": 123})
        err_msg = ("[Video.description] `description` must be a string "
                   "containing the video's description (received object of "
                   "type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

    def test_keywords_errors(self):
        # bad keywords type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "keywords": "abc"})
        err_msg = ("[Video.keywords] `keywords` must be a list, tuple, or set "
                   "of keyword strings associated with this video (received "
                   "object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # keyword is not string
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "keywords": ["abc", "def", 123]})
        err_msg = ("[Video.keywords] `keywords` must be a list, tuple, or set "
                   "of keyword strings associated with this video (received "
                   "keyword of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # keyword is empty string
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "keywords": ["abc", "def", ""]})
        err_msg = ("[Video.keywords] `keywords` must be a list, tuple, or set "
                   "of keyword strings associated with this video (received "
                   "empty keyword: '')")
        self.assertEqual(str(err.exception), err_msg)

    def test_thumbnail_url_errors(self):
        # bad thumbnail_url type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "thumbnail_url": 123})
        err_msg = ("[Video.thumbnail_url] `thumbnail_url` must be a url "
                   "string pointing to the thumbnail image used for this "
                   "video (received object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

    def test_target_dir_errors(self):
        # bad target_dir type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "target_dir": "abc"})
        err_msg = ("[Video.target_dir] `target_dir` must be a Path-like "
                   "object pointing to a directory on local storage in which "
                   "to store the contents of this video (received object of "
                   "type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # target_dir points to file
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "target_dir": Path(__file__)})
        err_msg = (f"[Video.target_dir] `target_dir` must be a Path-like "
                   f"object pointing to a directory on local storage in which "
                   f"to store the contents of this video (path points to file: "
                   f"{Path(__file__)})")
        self.assertEqual(str(err.exception), err_msg)

    def test_streams_errors(self):
        # bad streams type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "streams": "abc"})
        err_msg = ("[Video.streams] `streams` must be a pytube.StreamQuery "
                   "object or None if the video has no streams (received "
                   "object of type: <class 'str'>)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        v = Video(**{**TEST_PROPERTIES, "streams": None})
        self.assertTrue(isinstance(v.streams, pytube.StreamQuery))
        self.assertEqual(len(v.streams), 0)

        # assignment outside init
        v = Video(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            v.streams = pytube.StreamQuery([])
        err_msg = ("[Video.streams] `streams` cannot be changed outside of "
                   "init")
        self.assertEqual(str(err.exception), err_msg)

    def test_captions_errors(self):
        # bad captions type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "captions": 123})
        err_msg = ("[Video.captions] `captions` must be a pytube.CaptionQuery "
                   "object or None if the video has no captions (received "
                   "object of type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # None
        v = Video(**{**TEST_PROPERTIES, "captions": None})
        self.assertTrue(isinstance(v.captions, pytube.CaptionQuery))
        self.assertEqual(len(v.captions), 0)

        # assignment outside init
        v = Video(**{**TEST_PROPERTIES})
        with self.assertRaises(AttributeError) as err:
            v.captions = pytube.CaptionQuery([])
        err_msg = ("[Video.captions] `captions` cannot be changed outside of "
                   "init")
        self.assertEqual(str(err.exception), err_msg)

    def test_channel_errors(self):
        # bad channel type
        with self.assertRaises(TypeError) as err:
            Video(**{**TEST_PROPERTIES, "channel": 123})
        err_msg = ("[Video.channel] `channel` must be a Channel object "
                   "pointing to the owner of this video (received object of "
                   "type: <class 'int'>)")
        self.assertEqual(str(err.exception), err_msg)

        # channel does not own video
        test_channel = {
            "source": "local",
            "channel_id": "UCBR8-60-B28hp2BmDPdntcQ",
            "channel_name": "YouTube",
            "video_ids": ["NeOBvwRfBWc", "QltYNmVUvh0", "SYQJPkiNJfE",
                          "3WSmP7i9my8", "TBuNVQ54dgg"],  # official YouTube
            "last_updated": datetime.now(),
            "about_html": "",
            "community_html": "",
            "featured_channels_html": "",
            "videos_html": "",
            "workers": 1,
            "target_dir": Path(ROOT_DIR, "datatube", "test", "test_data",
                               "UCBR8-60-B28hp2BmDPdntcQ")
        }
        with self.assertRaises(ValueError) as err:
            Video(**{**TEST_PROPERTIES, "channel": Channel(**test_channel)})
        err_msg = (f"[Video.channel] `channel` must be a Channel object "
                   f"pointing to the owner of this video (channel does not own "
                   f"this video: '{TEST_PROPERTIES['video_id']}' not in "
                   f"['NeOBvwRfBWc', 'QltYNmVUvh0', 'SYQJPkiNJfE', "
                   f"'3WSmP7i9my8', 'TBuNVQ54dgg'])")
        self.assertEqual(str(err.exception), err_msg)


class BasicVideoTests(unittest.TestCase):

    def test_to_json(self):
        v = Video(**TEST_PROPERTIES)
        json_path = Path(ROOT_DIR, "datatube", "test", "test_data",
                         "video_test_json.json")
        json_path.unlink(missing_ok=True)
        json_dict = v.to_json(json_path=json_path)
        expected = {
            "datatube_version": DATATUBE_VERSION_NUMBER,
            "video_id": TEST_PROPERTIES["video_id"],
            "video_title": TEST_PROPERTIES["video_title"],
            "publish_date": TEST_PROPERTIES["publish_date"].isoformat(),
            "last_updated": TEST_PROPERTIES["last_updated"].isoformat(),
            "duration": TEST_PROPERTIES["duration"].total_seconds(),
            "stats": {
                "views": TEST_PROPERTIES["views"],
                "rating": TEST_PROPERTIES["rating"],
                "likes": TEST_PROPERTIES["likes"],
                "dislikes": TEST_PROPERTIES["dislikes"]
            },
            "description": TEST_PROPERTIES["description"],
            "keywords": TEST_PROPERTIES["keywords"],
            "thumbnail_url": TEST_PROPERTIES["thumbnail_url"]
        }
        self.assertEqual(json_dict, expected)
        self.assertTrue(json_path.exists())
        with json_path.open("r") as json_file:
            test_json = json.load(json_file)
        self.assertEqual(test_json, expected)

    def test_equality(self):
        v1 = Video(**TEST_PROPERTIES)
        v2 = Video(**TEST_PROPERTIES)
        self.assertEqual(v1, v2)
        v3 = Video(**{**TEST_PROPERTIES, "video_id": "DifferentId"})
        self.assertNotEqual(v1, v3)
        v4 = Video(**{**TEST_PROPERTIES, "last_updated": datetime.now()})
        self.assertNotEqual(v1, v4)


class PytubeVideoTests(unittest.TestCase):

    video_url = video_id_to_url(TEST_PROPERTIES["video_id"])
    channel = TEST_PROPERTIES["channel"]

    def test_load_from_pytube_caching(self):
        def time_get(channel=None):
            start = time.perf_counter()
            Video.from_pytube(self.video_url, channel)
            end = time.perf_counter()
            return end - start

        # without channel
        times = [time_get() for _ in range(5)]
        self.assertTrue(sum(times) < 2 * times[0])

        # with channel
        times = [time_get(self.channel) for _ in range(5)]
        self.assertTrue(sum(times) < 2 * times[0])

    def test_load_from_pytube_no_channel(self):
        v = Video.from_pytube(self.video_url)
        self.assertEqual(v.source, "pytube")
        self.assertEqual(v.id, TEST_PROPERTIES["video_id"])
        self.assertEqual(v.title, TEST_PROPERTIES["video_title"])
        self.assertEqual(v.publish_date, TEST_PROPERTIES["publish_date"])
        self.assertEqual(v.last_updated.date(), datetime.now().date())
        self.assertEqual(v.duration, TEST_PROPERTIES["duration"])
        self.assertGreaterEqual(v.stats["views"], TEST_PROPERTIES["views"])
        # self.assertAlmostEqual(v.stats["rating"], TEST_PROPERTIES["rating"],
        #                        places=1)
        # self.assertGreaterEqual(v.stats["likes"], TEST_PROPERTIES["likes"])
        # self.assertGreaterEqual(v.stats["dislikes"],
        #                         TEST_PROPERTIES["dislikes"])
        self.assertTrue(isinstance(v.description, str) and
                        len(v.description) > 0)
        self.assertTrue(isinstance(v.keywords, list) and
                        len(v.keywords) > 0 and
                        all(isinstance(kw, str) for kw in v.keywords))
        self.assertTrue(isinstance(v.thumbnail_url, str) and
                        is_url(v.thumbnail_url))
        self.assertEqual(v.target_dir, Path(VIDEO_DIR, TEST_CHANNEL_ID, v.id))
        self.assertTrue(len(v.streams) > 0)
        self.assertTrue(len(v.captions) > 0)
        self.assertIsNone(v.channel)

    def test_load_from_pytube_with_channel(self):
        v = Video.from_pytube(self.video_url, self.channel)
        self.assertEqual(v.source, "pytube")
        self.assertEqual(v.id, TEST_PROPERTIES["video_id"])
        self.assertEqual(v.title, TEST_PROPERTIES["video_title"])
        self.assertEqual(v.publish_date, TEST_PROPERTIES["publish_date"])
        self.assertEqual(v.last_updated.date(), datetime.now().date())
        self.assertEqual(v.duration, TEST_PROPERTIES["duration"])
        self.assertGreaterEqual(v.stats["views"], TEST_PROPERTIES["views"])
        # self.assertAlmostEqual(v.stats["rating"], TEST_PROPERTIES["rating"],
        #                        places=1)
        # self.assertGreaterEqual(v.stats["likes"], TEST_PROPERTIES["likes"])
        # self.assertGreaterEqual(v.stats["dislikes"],
        #                         TEST_PROPERTIES["dislikes"])
        self.assertTrue(isinstance(v.description, str) and
                        len(v.description) > 0)
        self.assertTrue(isinstance(v.keywords, list) and
                        len(v.keywords) > 0 and
                        all(isinstance(kw, str) for kw in v.keywords))
        self.assertTrue(isinstance(v.thumbnail_url, str) and
                        is_url(v.thumbnail_url))
        self.assertEqual(v.target_dir, Path(v.channel.target_dir, v.id))
        self.assertTrue(len(v.streams) > 0)
        self.assertTrue(len(v.captions) > 0)
        self.assertEqual(v.channel, self.channel)
