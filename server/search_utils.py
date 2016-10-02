import math
from haversine import haversine


class BoundingBox(object):
    def __init__(self, lat_min, lat_max, lng_min, lng_max):
        self.lat_min = lat_min
        self.lng_min = lng_min
        self.lat_max = lat_max
        self.lng_max = lng_max


def find_bounding_box(search_lat, search_lng, search_radius):
    """Quick and dirty method to find bounding lat-lng box to narrow down
    search. Assumes Earth surface is flat near search area (fine for a small
    search radius). Inaccurate near the poles.

    search_lat and search_lng in degrees
    search_radius in km
    """
    search_lat_rads = math.radians(search_lat)
    search_lng_rads = math.radians(search_lng)

    mean_radius_of_earth = 6371.0
    adjacent_radius = mean_radius_of_earth * math.cos(search_lat_rads)

    # notice that the length of the bounding box is slightly increased 
    # for safety
    lat_min = search_lat_rads - 1.01 * (search_radius / mean_radius_of_earth)
    lat_max = search_lat_rads + 1.01 * (search_radius / mean_radius_of_earth)
    lng_min = search_lng_rads - 1.01 * (search_radius / adjacent_radius)
    lng_max = search_lng_rads + 1.01 * (search_radius / adjacent_radius)

    return BoundingBox(
        math.degrees(lat_min), math.degrees(lat_max),
        math.degrees(lng_min), math.degrees(lng_max)
    )


def is_within_search_radius(
        search_lat, search_lng, mark_lat, mark_lng, search_radius):
    """Use haversine formula to check if shop is within search_radius of
    shop location.

    all lat and lng in degrees
    search_radius in km
    """
    return haversine((float(search_lat), float(search_lng)),
                     (float(mark_lat), float(mark_lng))) <= float(search_radius)
