Unfortunately,
    # given that the shops are all relatively close to each other, this doesn't
    # narrow down the search as much as I had hoped.

"""
TODO: Initially I thought that using scipy's KDTree to find all shops
within a given distane of the search location wouldn't help us since
lat/long are not linear with distance.
However, after reading http://stackoverflow.com/questions/20654918/
python-how-to-speed-up-calculation-of-distances-between-cities
I see now that I could first convert to x,y,z coordinates and then use
a kd-tree.

In this case it would not be necessary to construct SHOPS_BY_LAT and
SHOPS_BY_LNG, but instead an array of tuples of the form
(shop_lat, shop_lng, shop_id), along with SHOPS_BY_ID and SHOPS_BY_TAG. Then
_find_shops_within_search_radius_with_tag will need to be rewritten.
"""


1. How would your design change if the data was not static (i.e updated frequently
during the day)?

2. Do you think your design can handle 1000 concurrent requests per second? If not, what
would you change?
