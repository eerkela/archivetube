from datetime import datetime, timezone
import json
from pathlib import Path
import reprlib
from time import time
import unittest

if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from datatube.info import ChannelInfo
from datatube.test import DATA_DIR


HTML_PROPERTIES = {
    "about": "some html code",
    "community": "some html code",
    "featured_channels": "some html code",
    "videos": "some html code"
}
TEST_PROPERTIES = {
    "channel_id": "UC_24_character_channel_",
    "channel_name": "Some Channel",
    "last_updated": datetime.now(timezone.utc),
    "about_html": HTML_PROPERTIES["about"],
    "community_html": HTML_PROPERTIES["community"],
    "featured_channels_html": HTML_PROPERTIES["featured_channels"],
    "videos_html": HTML_PROPERTIES["videos"]
}
EXPECTED_CHANNELINFO = {
    "channel_id": TEST_PROPERTIES["channel_id"],
    "channel_name": TEST_PROPERTIES["channel_name"],
    "last_updated": TEST_PROPERTIES["last_updated"],
    "html": HTML_PROPERTIES
}
JSON_PATH = Path(DATA_DIR, "test_channel_info.json")
DB_NAME = "datatube_test"


class HtmlDictGetterSetterTests(unittest.TestCase):

    maxDiff = None

    def test_init_good_input(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html.about, HTML_PROPERTIES["about"])
        self.assertEqual(html.community, HTML_PROPERTIES["community"])
        self.assertEqual(html.featured_channels,
                         HTML_PROPERTIES["featured_channels"])
        self.assertEqual(html.videos, HTML_PROPERTIES["videos"])

    def test_init_immutable_bad_type(self):
        test_val = 123
        err_msg = (f"[datatube.info.HtmlDict.__init__] `immutable` must be a "
                   f"boolean (received object of type: {type(test_val)})")

        with self.assertRaises(TypeError) as err:
            ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=test_val)
        self.assertEqual(str(err.exception), err_msg)

    def test_set_about_html(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["about"])

        # from init
        html = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, "about": test_val})
        self.assertEqual(html.about, test_val)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html.about = test_val
        self.assertEqual(html.about, test_val)

        # from getitem/setitem
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html["about"] = test_val
        self.assertEqual(html["about"], test_val)

    def test_set_about_html_immutable_instance(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["about"])
        err_msg = ("[datatube.info.HtmlDict.about] cannot reassign `about`: "
                   "HtmlDict instance is immutable")

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            html.about = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["about"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_about_html_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, HTML_PROPERTIES["about"])
        err_msg = (f"[datatube.info.HtmlDict.about] `about` must be a string "
                   f"(received object of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, "about": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            html.about = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            html["about"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_community_html(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["community"])

        # from init
        html = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES,
                                       "community": test_val})
        self.assertEqual(html.community, test_val)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html.community = test_val
        self.assertEqual(html.community, test_val)

        # from getitem/setitem
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html["community"] = test_val
        self.assertEqual(html["community"], test_val)

    def test_set_community_html_immutable_instance(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["community"])
        err_msg = ("[datatube.info.HtmlDict.community] cannot reassign "
                   "`community`: HtmlDict instance is immutable")

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            html.community = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["community"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_community_html_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, HTML_PROPERTIES["community"])
        err_msg = (f"[datatube.info.HtmlDict.community] `community` must be a "
                   f"string (received object of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, "community": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            html.community = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            html["community"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_featured_channels_html(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["featured_channels"])

        # from init
        html = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES,
                                       "featured_channels": test_val})
        self.assertEqual(html.featured_channels, test_val)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html.featured_channels = test_val
        self.assertEqual(html.featured_channels, test_val)

        # from getitem/setitem
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html["featured_channels"] = test_val
        self.assertEqual(html["featured_channels"], test_val)

    def test_set_featured_channels_html_immutable_instance(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["featured_channels"])
        err_msg = ("[datatube.info.HtmlDict.featured_channels] cannot reassign "
                   "`featured_channels`: HtmlDict instance is immutable")

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            html.featured_channels = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["featured_channels"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_featured_channels_html_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, HTML_PROPERTIES["featured_channels"])
        err_msg = (f"[datatube.info.HtmlDict.featured_channels] "
                   f"`featured_channels` must be a string (received object "
                   f"of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo.HtmlDict(**{**HTML_PROPERTIES,
                                    "featured_channels": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            html.featured_channels = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            html["featured_channels"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_videos_html(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["videos"])

        # from init
        html = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, "videos": test_val})
        self.assertEqual(html.videos, test_val)

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html.videos = test_val
        self.assertEqual(html.videos, test_val)

        # from getitem/setitem
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html["videos"] = test_val
        self.assertEqual(html["videos"], test_val)

    def test_set_videos_html_immutable_instance(self):
        test_val = "some other html code"
        self.assertNotEqual(test_val, HTML_PROPERTIES["videos"])
        err_msg = ("[datatube.info.HtmlDict.videos] cannot reassign "
                   "`videos`: HtmlDict instance is immutable")

        # from property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            html.videos = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["videos"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_videos_html_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, HTML_PROPERTIES["videos"])
        err_msg = (f"[datatube.info.HtmlDict.videos] `videos` must be a "
                   f"string (received object of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, "videos": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter + property getter/setter
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            html.videos = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter + getitem/setitem
        with self.assertRaises(TypeError) as err:
            html["videos"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_getitem_key_error(self):
        test_key = "this key does not exist"
        self.assertNotIn(test_key, HTML_PROPERTIES)
        err_msg = (f"[datatube.info.HtmlDict.__getitem__] KeyError: "
                   f"{repr(test_key)}")

        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        with self.assertRaises(KeyError) as err:
            html[test_key]
        self.assertEqual(str(err.exception), repr(err_msg))

    def test_setitem_key_error(self):
        test_key = "this key does not exist"
        self.assertNotIn(test_key, HTML_PROPERTIES)
        err_msg = (f"[datatube.info.HtmlDict.__setitem__] KeyError: "
                   f"{repr(test_key)}")

        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        with self.assertRaises(KeyError) as err:
            html[test_key] = "something"
        self.assertEqual(str(err.exception), repr(err_msg))


class HtmlDictIterationTests(unittest.TestCase):

    def test_items(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(tuple(html.items()), tuple(HTML_PROPERTIES.items()))

    def test_keys(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html.keys(), tuple(HTML_PROPERTIES))

    def test_values(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html.values(), tuple(HTML_PROPERTIES.values()))

    def test_iter(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        expected = tuple(HTML_PROPERTIES)
        for index, key in enumerate(html):
            self.assertEqual(key, expected[index])


class HtmlDictDunderTests(unittest.TestCase):

    maxDiff = None

    def test_contains(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)

        # True
        for key in HTML_PROPERTIES:
            self.assertTrue(key in html)

        # False
        self.assertFalse("" in html)  # empty string
        self.assertFalse("this key does not exist" in html)

    def test_equality_htmldict_instances(self):
        # True
        html1 = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html2 = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html1, html2)

        # False
        test_val = "different from html1"
        for key, val in HTML_PROPERTIES.items():
            self.assertNotEqual(val, test_val)
            html3 = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, key: test_val})
            self.assertNotEqual(html1, html3)

    def test_equality_base_dicts(self):
        # True
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html, HTML_PROPERTIES)

        # False - unequal values
        test_val = "different from html"
        for key, val in HTML_PROPERTIES.items():
            self.assertNotEqual(val, test_val)
            self.assertNotEqual(html, {**HTML_PROPERTIES, key: test_val})

        # False - missing/extra key
        for key in HTML_PROPERTIES:
            missing = {k: v for k, v in HTML_PROPERTIES.items() if k != key}
            self.assertNotEqual(html, missing)
        self.assertNotIn("extra key", HTML_PROPERTIES)
        self.assertNotEqual(html, {**HTML_PROPERTIES,
                                   "extra key": "some value"})

    def test_hash(self):
        # equal values
        html1 = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        html2 = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        self.assertEqual(hash(html1), hash(html2))

        # unequal values
        test_val = "different from html1"
        for key in HTML_PROPERTIES:
            html3 = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, key: test_val},
                                         immutable=True)
            self.assertNotEqual(hash(html1), hash(html3))

        # instance not immutable
        html4 = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=False)
        with self.assertRaises(TypeError) as err:
            hash(html4)
        err_msg = ("[datatube.info.HtmlDict.__hash__] ChannelInfo.HtmlDict "
                   "object cannot be hashed: instance must be immutable")
        self.assertEqual(str(err.exception), err_msg)

    def test_repr(self):
        fields = {
            **HTML_PROPERTIES,
            "immutable": False
        }
        str_repr = reprlib.Repr()
        formatted = []
        for k, v in fields.items():
            if isinstance(v, str):
                formatted.append(f"{k}={str_repr.repr(v)}")
            else:
                formatted.append(f"{k}={repr(v)}")
        expected = f"ChannelInfo.HtmlDict({', '.join(formatted)})"
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(repr(html), expected)

    def test_str(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)

        # short values
        self.assertEqual(str(html), str(HTML_PROPERTIES))

        # long values
        test_val = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                    "sed do eiusmod tempor incididunt ut labore et dolore "
                    "magna aliqua. Ut enim ad minim veniam, quis nostrud "
                    "exercitation ullamco laboris nisi ut aliquip ex ea "
                    "commodo consequat. Duis aute irure dolor in reprehenderit "
                    "in voluptate velit esse cillum dolore eu fugiat nulla "
                    "pariatur. Excepteur sint occaecat cupidatat non proident, "
                    "sunt in culpa qui officia deserunt mollit anim id est "
                    "laborum.")
        str_repr = reprlib.Repr()
        expected = {}
        for k in HTML_PROPERTIES:
            html[k] = test_val
            expected[k] = str_repr.repr(test_val)[1:-1]
        self.assertEqual(str(html), str(expected))


class ChannelInfoGetterSetterTests(unittest.TestCase):

    maxDiff = None

    def test_init_good_input(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(info.channel_id, TEST_PROPERTIES["channel_id"])
        self.assertEqual(info.channel_name, TEST_PROPERTIES["channel_name"])
        self.assertEqual(info.last_updated, TEST_PROPERTIES["last_updated"])
        self.assertEqual(info.html["about"], TEST_PROPERTIES["about_html"])
        self.assertEqual(info.html["community"],
                         TEST_PROPERTIES["community_html"])
        self.assertEqual(info.html["featured_channels"],
                         TEST_PROPERTIES["featured_channels_html"])
        self.assertEqual(info.html["videos"], TEST_PROPERTIES["videos_html"])

    def test_init_immutable_bad_type(self):
        test_val = 123
        err_msg = (f"[datatube.info.ChannelInfo.__init__] `immutable` must be "
                   f"a boolean (received object of type: {type(test_val)})")

        with self.assertRaises(TypeError) as err:
            ChannelInfo(**TEST_PROPERTIES, immutable=test_val)
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id(self):
        test_val = "UC_some_other_channel_id"  # still 24 characters
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])

        # from init
        info = ChannelInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(info.channel_id, test_val)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        info.channel_id = test_val
        self.assertEqual(info.channel_id, test_val)

        # from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        info["channel_id"] = test_val
        self.assertEqual(info["channel_id"], test_val)

    def test_set_channel_id_immutable_instance(self):
        test_val = "UC_some_other_channel_id"  # still 24 characters
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])
        err_msg = ("[datatube.info.ChannelInfo.channel_id] cannot reassign "
                   "`channel_id`: ChannelInfo instance is immutable")

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])
        err_msg = (f"[datatube.info.ChannelInfo.channel_id] `channel_id` must "
                   f"be a 24-character ExternalId string starting with 'UC' "
                   f"(received object of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_bad_length(self):
        test_val = "UC_not_24_chars"
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])
        err_msg = (f"[datatube.info.ChannelInfo.channel_id] `channel_id` must "
                   f"be a 24-character ExternalId string starting with 'UC' "
                   f"(received: {repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_doesnt_start_with_UC(self):
        test_val = "_does_not_start_with_UC_"  # still 24 characters
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_id"])
        err_msg = (f"[datatube.info.ChannelInfo.channel_id] `channel_id` must "
                   f"be a 24-character ExternalId string starting with 'UC' "
                   f"(received: {repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "channel_id": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info =  ChannelInfo(**TEST_PROPERTIES)
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
        info = ChannelInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        self.assertEqual(info.channel_name, test_val)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        info.channel_name = test_val
        self.assertEqual(info.channel_name, test_val)

        # from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        info["channel_name"] = test_val
        self.assertEqual(info["channel_name"], test_val)

    def test_set_channel_name_immutable_instance(self):
        test_val = "Some Other Channel Name"
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_name"])
        err_msg = ("[datatube.info.ChannelInfo.channel_name] cannot reassign "
                   "`channel_name`: ChannelInfo instance is immutable")

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_name_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_name"])
        err_msg = (f"[datatube.info.ChannelInfo.channel_name] `channel_name` "
                   f"must be a non-empty string (received object of type: "
                   f"{type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_name_empty_string(self):
        test_val = ""
        self.assertNotEqual(test_val, TEST_PROPERTIES["channel_name"])
        err_msg = (f"[datatube.info.ChannelInfo.channel_name] `channel_name` "
                   f"must be a non-empty string (received: {repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "channel_name": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated(self):
        test_val = datetime.now(timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])

        # from init
        info = ChannelInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(info.last_updated, test_val)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        info.last_updated = test_val
        self.assertEqual(info.last_updated, test_val)

        # from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        info["last_updated"] = test_val
        self.assertEqual(info["last_updated"], test_val)

    def test_set_last_updated_immutable_instance(self):
        test_val = datetime.now(timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])
        err_msg = ("[datatube.info.ChannelInfo.last_updated] cannot reassign "
                   "`last_updated`: ChannelInfo instance is immutable")

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])
        err_msg = (f"[datatube.info.ChannelInfo.last_updated] `last_updated` "
                   f"must be a timezone-aware datetime.datetime object stating "
                   f"the last time this channel's information was checked for "
                   f"updates (received object of type: {type(test_val)})")

        # from init
        with self.assertRaises(TypeError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_has_no_timezone(self):
        test_val = datetime.now()  # no tzinfo
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])
        err_msg = (f"[datatube.info.ChannelInfo.last_updated] `last_updated` "
                   f"must be a timezone-aware datetime.datetime object stating "
                   f"the last time this channel's information was checked for "
                   f"updates (timestamp has no timezone information: "
                   f"{repr(test_val)})")

        # from init
        with self.assertRaises(ValueError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception), err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_in_future(self):
        test_val = datetime(9999, 12, 31, tzinfo=timezone.utc)
        self.assertNotEqual(test_val, TEST_PROPERTIES["last_updated"])
        err_msg = (f"[datatube.info.ChannelInfo.last_updated] `last_updated` "
                   f"must be a timezone-aware datetime.datetime object stating "
                   f"the last time this channel's information was checked for "
                   f"updates (timestamp in the future: {test_val} > ")

        # from init
        with self.assertRaises(ValueError) as err:
            ChannelInfo(**{**TEST_PROPERTIES, "last_updated": test_val})
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception)[:len(err_msg)], err_msg)

    def test_set_html(self):
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html",
                    "videos": "different html"}
        self.assertNotEqual(test_val, HTML_PROPERTIES)

        # from init
        init_dict = {f"{k}_html": v for k, v in test_val.items()}
        info = ChannelInfo(**{**TEST_PROPERTIES, **init_dict})
        self.assertEqual(info.html, ChannelInfo.HtmlDict(**test_val))
        self.assertEqual(info.html, test_val)

        # HtmlDict from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        info.html = ChannelInfo.HtmlDict(**test_val)
        self.assertEqual(info.html, ChannelInfo.HtmlDict(**test_val))
        self.assertEqual(info.html, test_val)

        # raw dict from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        info.html = test_val
        self.assertEqual(info.html, ChannelInfo.HtmlDict(**test_val))
        self.assertEqual(info.html, test_val)

        # html dict instance from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        info["html"] = ChannelInfo.HtmlDict(**test_val)
        self.assertEqual(info["html"], ChannelInfo.HtmlDict(**test_val))
        self.assertEqual(info["html"], test_val)

        # raw dict from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        info["html"] = test_val
        self.assertEqual(info["html"], ChannelInfo.HtmlDict(**test_val))
        self.assertEqual(info["html"], test_val)

    def test_set_html_immutable_instance(self):
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html",
                    "videos": "different html"}
        self.assertNotEqual(test_val, HTML_PROPERTIES)
        err_msg = ("[datatube.info.ChannelInfo.html] cannot reassign `html`: "
                   "ChannelInfo instance is immutable")

        # html dict instance from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        with self.assertRaises(AttributeError) as err:
            info.html = ChannelInfo.HtmlDict(**test_val)
        self.assertEqual(str(err.exception), err_msg)

        # raw dict from property getter/setter
        with self.assertRaises(AttributeError) as err:
            info.html = test_val
        self.assertEqual(str(err.exception), err_msg)

        # html dict instance from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["html"] = ChannelInfo.HtmlDict(**test_val)
        self.assertEqual(str(err.exception), err_msg)

        # raw dict from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["html"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_html_bad_type(self):
        test_val = 123
        self.assertNotEqual(test_val, HTML_PROPERTIES)
        err_msg = (f"[datatube.info.ChannelInfo.html] `html` must be a "
                   f"ChannelInfo.HtmlDict object or a base dictionary "
                   f"containing equivalent information (received object of "
                   f"type: {type(test_val)})")

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(TypeError) as err:
            info.html = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["html"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_html_extra_field(self):
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html",
                    "videos": "different html",
                    "extra field": "shouldn't be here"}
        self.assertNotEqual(test_val, HTML_PROPERTIES)
        err_msg = ("[datatube.info.ChannelInfo.html] `html` must be a "
                   "ChannelInfo.HtmlDict object or a base dictionary "
                   "containing equivalent information (could not convert base "
                   "dictionary)")

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.html = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["html"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_html_missing_field(self):
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html"}  # missing 'videos'
        self.assertNotEqual(test_val, HTML_PROPERTIES)
        err_msg = ("[datatube.info.ChannelInfo.html] `html` must be a "
                   "ChannelInfo.HtmlDict object or a base dictionary "
                   "containing equivalent information (could not convert base "
                   "dictionary)")

        # from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(ValueError) as err:
            info.html = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["html"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_getitem_key_error(self):
        test_key = "this key does not exist"
        self.assertNotIn(test_key, TEST_PROPERTIES)
        err_msg = (f"[datatube.info.ChannelInfo.__getitem__] KeyError: "
                   f"{repr(test_key)}")

        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(KeyError) as err:
            info[test_key]
        self.assertEqual(str(err.exception), repr(err_msg))

    def test_setitem_key_error(self):
        test_key = "this key does not exist"
        self.assertNotIn(test_key, TEST_PROPERTIES)
        err_msg = (f"[datatube.info.ChannelInfo.__setitem__] KeyError: "
                   f"{repr(test_key)}")

        info = ChannelInfo(**TEST_PROPERTIES)
        with self.assertRaises(KeyError) as err:
            info[test_key] = "something"
        self.assertEqual(str(err.exception), repr(err_msg))


class ChannelInfoIterationTests(unittest.TestCase):

    def test_items(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(tuple(info.items()),
                         tuple(EXPECTED_CHANNELINFO.items()))

    def test_keys(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(info.keys(), tuple(EXPECTED_CHANNELINFO))

    def test_values(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(info.values(), tuple(EXPECTED_CHANNELINFO.values()))

    def test_iter(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        expected = tuple(EXPECTED_CHANNELINFO)
        for index, key in enumerate(info):
            self.assertEqual(key, expected[index])


class ChannelInfoDunderTests(unittest.TestCase):

    maxDiff = None

    def test_contains(self):
        info = ChannelInfo(**TEST_PROPERTIES)

        # True
        for key in EXPECTED_CHANNELINFO:
            self.assertTrue(key in info)

        # False
        self.assertFalse("" in info)  # empty string
        self.assertFalse("this key does not exist" in info)

    def test_equality_channelinfo_instance(self):
        # True
        info1 = ChannelInfo(**TEST_PROPERTIES)
        info2 = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(info1, info2)

        # False
        for key, val in TEST_PROPERTIES.items():
            if isinstance(val, str):
                test_val = "UC_different_from_info1_"
            elif isinstance(val, datetime):
                test_val = datetime.now(timezone.utc)
            else:
                raise NotImplementedError()
            self.assertNotEqual(val, test_val)
            info3 = ChannelInfo(**{**TEST_PROPERTIES, key: test_val})
            self.assertNotEqual(info1, info3)

    def test_equality_base_dict(self):
        # True
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(info, EXPECTED_CHANNELINFO)

        # False - unequal values
        for key, val in TEST_PROPERTIES.items():
            if isinstance(val, str):
                test_val = "UC_different_from_info1_"
            elif isinstance(val, datetime):
                test_val = datetime.now(timezone.utc)
            else:
                raise NotImplementedError()
            self.assertNotEqual(val, test_val)
            if "_html" in key:
                html_key = key.split("_html", maxsplit=1)[0]
                html_dict = {**HTML_PROPERTIES, html_key: test_val}
                expected = {**EXPECTED_CHANNELINFO, "html": html_dict}
            else:
                expected = {**EXPECTED_CHANNELINFO, key: test_val}
            self.assertNotEqual(info, expected)

        # False - missing/extra key
        for key in TEST_PROPERTIES:
            if "_html" in key:
                html_key = key.split("_html", maxsplit=1)[0]
                html_dict = {k: v for k, v in HTML_PROPERTIES.items()
                             if k != html_key}
                missing = {**EXPECTED_CHANNELINFO, "html": html_dict}
            else:
                missing = {k: v for k, v in EXPECTED_CHANNELINFO.items()
                           if k != key}
            self.assertNotEqual(info, missing)
        self.assertNotIn("extra key", EXPECTED_CHANNELINFO)
        self.assertNotEqual(info, {**EXPECTED_CHANNELINFO,
                                   "extra key": "some value"})

    def test_hash(self):
        # equal values
        info1 = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        info2 = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        self.assertEqual(hash(info1), hash(info2))

        # unequal values
        for key, val in TEST_PROPERTIES.items():
            if isinstance(val, str):
                test_val = "UC_different_from_info1_"
            elif isinstance(val, datetime):
                test_val = datetime.now(timezone.utc)
            else:
                raise NotImplementedError()
            self.assertNotEqual(val, test_val)
            info3 = ChannelInfo(**{**TEST_PROPERTIES, key: test_val},
                                immutable=True)
            self.assertNotEqual(hash(info1), hash(info3))

        # instance not immutable
        info4 = ChannelInfo(**TEST_PROPERTIES, immutable=False)
        with self.assertRaises(TypeError) as err:
            hash(info4)
        err_msg = ("[datatube.info.ChannelInfo.__hash__] ChannelInfo object "
                   "cannot be hashed: instance must be immutable")
        self.assertEqual(str(err.exception), err_msg)

    def test_repr(self):
        fields = {
            **TEST_PROPERTIES,
            "immutable": False
        }
        str_repr = reprlib.Repr()
        formatted = []
        for k, v in fields.items():
            if isinstance(v, str):
                formatted.append(f"{k}={str_repr.repr(v)}")
            else:
                formatted.append(f"{k}={repr(v)}")
        expected = f"ChannelInfo({', '.join(formatted)})"
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(repr(info), expected)

    def test_str(self):
        info = ChannelInfo(**TEST_PROPERTIES)

        # short values
        self.assertEqual(str(info), str(EXPECTED_CHANNELINFO))

        # long values
        test_val = ("Lorem ipsum dolor sit amet, consectetur adipiscing elit, "
                    "sed do eiusmod tempor incididunt ut labore et dolore "
                    "magna aliqua. Ut enim ad minim veniam, quis nostrud "
                    "exercitation ullamco laboris nisi ut aliquip ex ea "
                    "commodo consequat. Duis aute irure dolor in reprehenderit "
                    "in voluptate velit esse cillum dolore eu fugiat nulla "
                    "pariatur. Excepteur sint occaecat cupidatat non proident, "
                    "sunt in culpa qui officia deserunt mollit anim id est "
                    "laborum.")
        str_repr = reprlib.Repr()
        expected = {}
        for key, val in EXPECTED_CHANNELINFO.items():
            if key == "html":
                val = {k: str_repr.repr(test_val)[1:-1] for k in val}
            elif key == "channl_name":
                val = str_repr.repr(test_val)[1:-1]
            info[key] = val
            expected[key] = val
        self.assertEqual(str(info), str(expected))


# class ChannelInfoJSONTests(unittest.TestCase):

#     # TODO: Check channel JSON format matches expected

#     @classmethod
#     def setUpClass(cls) -> None:
#         saved_result = {
#             "channel_id": TEST_PROPERTIES["channel_id"],
#             "channel_name": TEST_PROPERTIES["channel_name"],
#             "last_updated": TEST_PROPERTIES["last_updated"],
#             "html": {
#                 "about": TEST_PROPERTIES["about_html"],
#                 "community": TEST_PROPERTIES["community_html"],
#                 "featured_channels": TEST_PROPERTIES["featured_channels_html"],
#                 "videos": TEST_PROPERTIES["videos_html"]
#             }
#         }
#         with JSON_PATH.open("w") as json_file:
#             json.dump(saved_result, json_file, default=str)

#     def test_from_json(self):
#         info = ChannelInfo.from_json(JSON_PATH)
#         self.assertEqual(info.channel_id, TEST_PROPERTIES["channel_id"])
#         self.assertEqual(info.channel_name, TEST_PROPERTIES["channel_name"])
#         self.assertEqual(info.last_updated, TEST_PROPERTIES["last_updated"])
#         self.assertEqual(info.html["about"], TEST_PROPERTIES["about_html"])
#         self.assertEqual(info.html["community"],
#                          TEST_PROPERTIES["community_html"])
#         self.assertEqual(info.html["featured_channels"],
#                          TEST_PROPERTIES["featured_channels_html"])
#         self.asssertEqual(info.html["videos"], TEST_PROPERTIES["videos_html"])

#     def test_to_json(self):
#         info = ChannelInfo(**TEST_PROPERTIES)
#         test_path = Path(JSON_PATH.parent, "temp_channel_info_to_json.json")
#         test_path.unlink(missing_ok=True)
#         info.to_json(test_path)
#         self.assertTrue(test_path.exists())
#         with test_path.open("r") as json_file:
#             saved = json.load(json_file)
#         self.assertEqual(saved, json.dumps(TEST_PROPERTIES, default=str))
#         test_path.unlink()

#     def test_from_json_errors(self):
#         # bad path type
#         test_val = 123
#         with self.assertRaises(TypeError) as err:
#             ChannelInfo.from_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#         # path does not exist
#         test_val = Path(JSON_PATH.parent, "this_path_does_not_exist.json")
#         with self.assertRaises(ValueError) as err:
#             ChannelInfo.from_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#         # path points to directory
#         test_val = Path(JSON_PATH.parent)
#         with self.assertRaises(ValueError) as err:
#             ChannelInfo.from_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#         # file does not end in .json
#         test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
#         with self.assertRaises(ValueError) as err:
#             ChannelInfo.from_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#     def test_to_json_errors(self):
#         info = ChannelInfo(**TEST_PROPERTIES)

#         # bad path type
#         test_val = 123
#         with self.assertRaises(TypeError) as err:
#             info.to_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#         # path does not exist
#         test_val = Path(JSON_PATH.parent, "this_path_does_not_exist.json")
#         with self.assertRaises(ValueError) as err:
#             info.to_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#         # path points to directory
#         test_val = Path(JSON_PATH.parent)
#         with self.assertRaises(ValueError) as err:
#             info.to_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)

#         # file does not end in .json
#         test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
#         with self.assertRaises(ValueError) as err:
#             info.to_json(test_val)
#         err_msg = ""
#         self.assertEqual(str(err.exception), err_msg)


# class ChannelInfoSQLTests(unittest.TestCase):

#     @classmethod
#     def setUpClass(cls) -> None:
#         raise NotImplementedError()


if __name__ == "__main__":
    unittest.main()
