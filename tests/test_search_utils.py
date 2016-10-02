from unittest import TestCase
from server.search_utils import find_bounding_box


class TestSearchUtils(TestCase):

    def test_find_bounding_box(self):
        bounding_box = find_bounding_box(59.33258, 59.33258, 0.5)
        self.assertTrue(hasattr(bounding_box, 'lat_min'))
        self.assertTrue(hasattr(bounding_box, 'lat_max'))
        self.assertTrue(hasattr(bounding_box, 'lng_min'))
        self.assertTrue(hasattr(bounding_box, 'lng_max'))
