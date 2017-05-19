from unittest import TestCase as UnitTestCase
from django.utils.safestring import mark_safe
from .templatetags.misc_extras import bleach


class TestBleach(UnitTestCase):
    def test_escape_script(self):
        value = "<script>alert('hi');</script>"
        escaped = bleach(value)
        self.assertTrue(escaped.startswith("&lt;"), escaped)

    def test_keep_safe(self):
        """ if it's been marked as safe coming in, leave it untouched """
        value = "<script>alert('hi');</script>"
        unescaped = bleach(mark_safe(value))
        self.assertEqual(unescaped, value)

    def test_keep_good_tags(self):
        value = "<b>bold</b>"
        escaped = bleach(value)
        self.assertEqual(escaped, value)
