from curses.ascii import HT
from datetime import datetime, timezone, tzinfo
import json
from pathlib import Path
from re import A
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
JSON_PATH = Path(DATA_DIR, "test_channel_info.json")
DB_NAME = "datatube_test"


class HtmlDictGetterSetterTests(unittest.TestCase):

    maxDiff = None

    def test_init_good_input(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html["about"], HTML_PROPERTIES["about"])
        self.assertEqual(html["community"], HTML_PROPERTIES["community"])
        self.assertEqual(html["featured_channels"],
                         HTML_PROPERTIES["featured_channels"])
        self.assertEqual(html["videos"], HTML_PROPERTIES["videos"])

    def test_getitem(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html["about"], HTML_PROPERTIES["about"])
        self.assertEqual(html["community"], HTML_PROPERTIES["community"])
        self.assertEqual(html["featured_channels"],
                         HTML_PROPERTIES["featured_channels"])
        self.assertEqual(html["videos"], HTML_PROPERTIES["videos"])

        # KeyError
        with self.assertRaises(KeyError) as err:
            html["this key does not exist"]
        err_msg = ("[datatube.info.HtmlDict.__getitem__] KeyError: 'this key "
                   "does not exist'")
        self.assertEqual(str(err.exception), repr(err_msg))

    def test_setitem(self):
        html = ChannelInfo.HtmlDict()
        for k, v in HTML_PROPERTIES.items():
            html[k] = v

        # KeyError
        with self.assertRaises(KeyError) as err:
            html["this key does not exist"] = "some value"
        err_msg = ("[datatube.info.HtmlDict.__setitem__] KeyError: 'this key "
                   "does not exist'")
        self.assertEqual(str(err.exception), repr(err_msg))

    def test_init_immutable_bad_type(self):
        test_val = 123
        err_msg = (f"[datatube.info.HtmlDict.__init__] `immutable` must be a "
                   f"boolean (received object of type: {type(test_val)})")

        with self.assertRaises(TypeError) as err:
            ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=test_val)
        self.assertEqual(str(err.exception), err_msg)

    def test_set_about_html_immutable_instance(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        test_val = "some other html code"
        err_msg = ("[datatube.info.HtmlDict.about] cannot reassign `about`: "
                   "HtmlDict instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            html.about = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["about"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_about_html_bad_type(self):
        test_val = 123
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

    def test_set_community_html_immutable_instance(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        test_val = "some other html code"
        err_msg = ("[datatube.info.HtmlDict.community] cannot reassign "
                   "`community`: HtmlDict instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            html.community = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["community"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_community_html_bad_type(self):
        test_val = 123
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

    def test_set_featured_channels_html_immutable_instance(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        test_val = "some other html code"
        err_msg = ("[datatube.info.HtmlDict.featured_channels] cannot reassign "
                   "`featured_channels`: HtmlDict instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            html.featured_channels = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["featured_channels"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_featured_channels_html_bad_type(self):
        test_val = 123
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

    def test_set_videos_html_immutable_instance(self):
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES, immutable=True)
        test_val = "some other html code"
        err_msg = ("[datatube.info.HtmlDict.videos] cannot reassign "
                   "`videos`: HtmlDict instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            html.videos = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            html["videos"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_videos_html_bad_type(self):
        test_val = 123
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
        expected_keys = tuple(HTML_PROPERTIES)
        for index, key in enumerate(html):
            self.assertEqual(key, expected_keys[index])


class HtmlDictDunderTests(unittest.TestCase):

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
        for key in HTML_PROPERTIES:
            html3 = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, key: test_val})
            self.assertNotEqual(html1, html3)

    def test_equality_base_dicts(self):
        # True
        html = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(html, HTML_PROPERTIES)

        # False - unequal values
        test_val = "different from html1"
        for key in HTML_PROPERTIES:
            self.assertNotEqual(html, {**HTML_PROPERTIES, key: test_val})

        # False - missing/extra key
        for key in HTML_PROPERTIES:
            missing = {k: v for k, v in HTML_PROPERTIES.items() if k != key}
            self.assertNotEqual(html, missing)
        self.assertNotEqual(html, {**HTML_PROPERTIES,
                                   "extra key": "some value"})

    def test_hash(self):
        # equal values
        html1 = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        html2 = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        self.assertEqual(hash(html1), hash(html2))

        # inequal values
        test_val = "different from html1"
        for key in HTML_PROPERTIES:
            html3 = ChannelInfo.HtmlDict(**{**HTML_PROPERTIES, key: test_val})
            self.assertNotEqual(hash(html1), hash(html3))

        # modified values
        test_val = "different from html1"
        html4 = ChannelInfo.HtmlDict(**HTML_PROPERTIES)
        for key in HTML_PROPERTIES:
            old_val = html4[key]
            html4[key] = test_val
            self.assertNotEqual(hash(html1), hash(html4))
            html4[key] = old_val
            self.assertEqual(hash(html1), hash(html4))

    def test_repr(self):
        raise NotImplementedError()

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
        max_width = 50
        expected = {}
        for k in HTML_PROPERTIES:
            html[k] = test_val
            expected[k] = f"{test_val[:max_width]}..."
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
        self.asssertEqual(info.html["videos"], TEST_PROPERTIES["videos_html"])

    def test_getitem(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        self.assertEqual(info["channel_id"], TEST_PROPERTIES["channel_id"])
        self.assertEqual(info["channel_name"], TEST_PROPERTIES["channel_name"])
        self.assertEqual(info["last_updated"], TEST_PROPERTIES["last_updated"])
        self.assertEqual(info["html"]["about"], TEST_PROPERTIES["about_html"])
        self.assertEqual(info["html"]["community"],
                         TEST_PROPERTIES["community_html"])
        self.assertEqual(info["html"]["featured_channels"],
                         TEST_PROPERTIES["featured_channels_html"])
        self.assertEqual(info["html"]["videos"],
                          TEST_PROPERTIES["videos_html"])

        # KeyError
        with self.assertRaises(KeyError) as err:
            info["this key does not exist"]
        err_msg = ("")
        self.assertEqual(str(err.exception), err_msg)

    def test_setitem(self):
        raise NotImplementedError()

    def test_init_immutable_bad_type(self):
        test_val = 123
        err_msg = (f"[datatube.info.ChannelInfo.__init__] `immutable` must be "
                   f"a boolean (received object of type: {type(test_val)})")

        with self.assertRaises(TypeError) as err:
            ChannelInfo(**TEST_PROPERTIES, immutable=test_val)
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_immutable_instance(self):
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        test_val = "UC_some_other_channel_id"  # still 24 characters
        err_msg = ("[datatube.info.ChannelInfo.channel_id] cannot reassign "
                   "`channel_id`: ChannelInfo instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            info.channel_id = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["channel_id"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_id_bad_type(self):
        test_val = 123
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

    def test_set_channel_name_immutable_instance(self):
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        test_val = "Some Other Channel Name"
        err_msg = ("[datatube.info.ChannelInfo.channel_name] cannot reassign "
                   "`channel_name`: ChannelInfo instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            info.channel_name = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["channel_name"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_channel_name_bad_type(self):
        test_val = 123
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

    def test_set_last_updated_immutable_instance(self):
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        test_val = datetime.now(timezone.utc)
        err_msg = ("[datatube.info.ChannelInfo.last_updated] cannot reassign "
                   "`last_updated`: ChannelInfo instance is immutable")

        # from property getter/setter
        with self.assertRaises(AttributeError) as err:
            info.last_updated = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(AttributeError) as err:
            info["last_updated"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_last_updated_bad_type(self):
        test_val = 123
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

    def test_set_html_dict(self):
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html",
                    "videos": "different html"}

        # TODO: equality checks will always fail
        # html dict instance from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        old_val = info.html
        info.html = ChannelInfo.HtmlDict(**test_val)
        self.assertEqual(info.html, old_val)

        # raw dict from property getter/setter
        info = ChannelInfo(**TEST_PROPERTIES)
        old_val = info.html
        info.html = test_val
        self.assertEqual(info.html, old_val)

        # html dict instance from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        old_val = info.html
        info["html"] = ChannelInfo.HtmlDict(**test_val)
        self.assertEqual(info.html, old_val)

        # raw dict from getitem/setitem
        info = ChannelInfo(**TEST_PROPERTIES)
        old_val = info.html
        info["html"] = test_val
        self.assertEqual(info.html, old_val)

    def test_set_html_immutable_instance(self):
        info = ChannelInfo(**TEST_PROPERTIES, immutable=True)
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html",
                    "videos": "different html"}
        err_msg = ("[datatube.info.ChannelInfo.html] cannot reassign `html`: "
                   "ChannelInfo instance is immutable")

        # html dict instance from property getter/setter
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
        info = ChannelInfo(**TEST_PROPERTIES)
        test_val = 123
        err_msg = ("[datatube.info.ChannelInfo.html] `html` must be a "
                   "ChannelInfo.HtmlDict object or a base dictionary "
                   "containing equivalent information")

        # from property getter/setter
        with self.assertRaises(TypeError) as err:
            info.html = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(TypeError) as err:
            info["html"] = test_val
        self.assertEqual(str(err.exception), err_msg)

    def test_set_html_bad_value(self):
        info = ChannelInfo(**TEST_PROPERTIES)
        test_val = {"about": "different html",
                    "community": "different html",
                    "featured_channels": "different html",
                    "videos": "different html",
                    "extra field": "shouldn't be here"}
        err_msg = ""

        # from property getter/setter
        with self.assertRaises(ValueError) as err:
            info.html = test_val
        self.assertEqual(str(err.exception), err_msg)

        # from getitem/setitem
        with self.assertRaises(ValueError) as err:
            info["html"] = test_val
        self.assertEqual(str(err.exception), err_msg)


class ChannelInfoIterationTests(unittest.TestCase):

    def test_keys(self):
        raise NotImplementedError()

    def test_values(self):
        raise NotImplementedError()

    def test_items(self):
        raise NotImplementedError()

    def test_iter(self):
        raise NotImplementedError()


class ChannelInfoDunderTests(unittest.TestCase):

    def test_contains(self):
        raise NotImplementedError()

    def test_equality_channelinfo_instances(self):
        raise NotImplementedError()

    def test_equality_base_dicts(self):
        raise NotImplementedError()

    def test_hashing(self):
        raise NotImplementedError()

    def test_repr(self):
        raise NotImplementedError()

    def test_str(self):
        raise NotImplementedError()


class ChannelInfoJSONTests(unittest.TestCase):

    # TODO: Check channel JSON format matches expected

    @classmethod
    def setUpClass(cls) -> None:
        saved_result = {
            "channel_id": TEST_PROPERTIES["channel_id"],
            "channel_name": TEST_PROPERTIES["channel_name"],
            "last_updated": TEST_PROPERTIES["last_updated"],
            "html": {
                "about": TEST_PROPERTIES["about_html"],
                "community": TEST_PROPERTIES["community_html"],
                "featured_channels": TEST_PROPERTIES["featured_channels_html"],
                "videos": TEST_PROPERTIES["videos_html"]
            }
        }
        with JSON_PATH.open("w") as json_file:
            json.dump(saved_result, json_file, default=str)

    def test_from_json(self):
        info = ChannelInfo.from_json(JSON_PATH)
        self.assertEqual(info.channel_id, TEST_PROPERTIES["channel_id"])
        self.assertEqual(info.channel_name, TEST_PROPERTIES["channel_name"])
        self.assertEqual(info.last_updated, TEST_PROPERTIES["last_updated"])
        self.assertEqual(info.html["about"], TEST_PROPERTIES["about_html"])
        self.assertEqual(info.html["community"],
                         TEST_PROPERTIES["community_html"])
        self.assertEqual(info.html["featured_channels"],
                         TEST_PROPERTIES["featured_channels_html"])
        self.asssertEqual(info.html["videos"], TEST_PROPERTIES["videos_html"])

    def test_to_json(self):
        info = ChannelInfo(**TEST_PROPERTIES)
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
            ChannelInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path does not exist
        test_val = Path(JSON_PATH.parent, "this_path_does_not_exist.json")
        with self.assertRaises(ValueError) as err:
            ChannelInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # path points to directory
        test_val = Path(JSON_PATH.parent)
        with self.assertRaises(ValueError) as err:
            ChannelInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

        # file does not end in .json
        test_val = Path(JSON_PATH.parent, f"{JSON_PATH.name}.txt")
        with self.assertRaises(ValueError) as err:
            ChannelInfo.from_json(test_val)
        err_msg = ""
        self.assertEqual(str(err.exception), err_msg)

    def test_to_json_errors(self):
        info = ChannelInfo(**TEST_PROPERTIES)

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
