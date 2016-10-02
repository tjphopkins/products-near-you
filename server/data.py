import csv
from copy import deepcopy
from collections import defaultdict

from server.search_utils import find_bounding_box, is_within_search_radius


SHOPS_BY_LAT = {}
SHOPS_BY_LNG = {}
SHOPS_BY_TAG = defaultdict(list)
TAGS_BY_NAME = {}
SHOPS_BY_ID = {}


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


def _process_shops():
    """
    Process shops.csv. Populates three dicts:
    * SHOPS_BY_LAT: shop_id keyed on lat
    * SHOPS_BY_LONG: shop_id keyed on lng
    * SHOPS_BY_ID: shop info keyed on id
    """
    with open('data/shops.csv') as csvfile:
        shops_reader = csv.reader(csvfile)
        shops_reader.next() # ignore the first row since these are headings
        for row in shops_reader:
            shop_id, shop_name, shop_lat, shop_lng = row
            SHOPS_BY_LAT[float(shop_lat)] = shop_id
            SHOPS_BY_LNG[float(shop_lng)] = shop_id
            SHOPS_BY_ID[shop_id] = {
                'lat': shop_lat, 'lng': shop_lng, 'products': []
            }


def _process_products():
    """Process products.csv. Populates SHOPS_BY_ID with products."""
    with open('data/products.csv') as csvfile:
        products_reader = csv.reader(csvfile)
        products_reader.next()
        for row in products_reader:
            product_id, shop_id, title, popularity, quantity = row
            if quantity > 0:
                SHOPS_BY_ID[shop_id]['products'].append({
                    'id': product_id,
                    'title': title,
                    'popularity': popularity
                })

def _process_tags():
    """
    Process tags.csv and taggings.csv. Populates:
    * SHOPS_BY_TAG
    * TAGS_BY_NAME
    """
    with open('data/tags.csv') as csvfile:
        tags_reader = csv.reader(csvfile)
        tags_reader.next()
        for row in tags_reader:
            tag_id, tag_name = row
            TAGS_BY_NAME[tag_name] = tag_id

    with open('data/taggings.csv') as csvfile:
        taggings_reader = csv.reader(csvfile)
        taggings_reader.next()
        for row in taggings_reader:
            tagging_id, shop_id, tag_id = row
            SHOPS_BY_TAG[tag_id].append(shop_id)


def process_data():
    """Process csv files and store data in memory."""
    _process_shops()
    _process_products()
    _process_tags()


def find_most_popular_products_in_search_area(
        search_lat, search_lng, search_radius, num_products, tags):
    """
    :arg search_lat float - latitude of search location in degrees
    :arg search_lng float - longitude of serch location in degrees
    :arg num_products int - number of products to return
    """
    shop_ids = _find_shops_within_search_radius_with_tag(
        search_lat, search_lng, search_radius, tags)
    return _find_most_popular_products_by_shops(shop_ids, num_products)


def _filter_shops_by_tag(shops, tags):
    shops_with_at_least_one_tag = []
    tag_ids = [TAGS_BY_NAME[tag_name] for tag_name in tags
               if TAGS_BY_NAME.get(tag_name)]
    for tag_id in tag_ids:
        shops_with_at_least_one_tag += SHOPS_BY_TAG[tag_id]

    return set(shops_with_at_least_one_tag).intersection(shops)


def _find_shops_within_search_radius_with_tag(
        search_lat, search_lng, search_radius, tags):
    """
    Returns a list of shop_ids corresponding to shops within search_radius
    from the search location.

    :arg lat float - latitude of search location in degrees
    :arg lng float - longitude of search location in degrees
    :arg search_radius int - search radius
    :arg tags array  - array of tag names
    """

    """
    Find a bound lat/lng box to narrow down the search. Unfortunately,
    given that the shops are all relatively close to each other, this doesn't
    narrow down the search as much as I had hoped.
    """
    bounding_box = find_bounding_box(search_lat, search_lng, search_radius)

    shops_in_lat_bounds = [
        SHOPS_BY_LAT[lat] for lat in SHOPS_BY_LAT.keys() if
        lat <= bounding_box.lat_max and lat >= bounding_box.lat_min
    ]

    shops_in_lng_bounds = [
        SHOPS_BY_LNG[lng] for lng in SHOPS_BY_LNG.keys() if
        lng <= bounding_box.lng_max and lng >= bounding_box.lng_min
    ]

    shops_in_bounding_box = set(shops_in_lat_bounds).intersection(
        set(shops_in_lng_bounds))

    # Narrow down further by tag before checking actual distances from
    # search location
    if tags:
        shops_to_check = _filter_shops_by_tag(shops_in_bounding_box, tags)
    else:
        shops_to_check = shops_in_bounding_box

    shops_in_search_radius = []
    for shop_id in shops_to_check:
        shop = SHOPS_BY_ID[shop_id]
        if is_within_search_radius(
                search_lat, search_lng, shop['lat'],
                shop['lng'], search_radius):
            shops_in_search_radius.append(shop_id)

    return shops_in_search_radius


def _find_most_popular_products_by_shops(shop_ids, num_products):
    """Given a list of shop ids, returns a list of the num_products
    most popular products in these shops.
    """
    products = []
    for shop_id in shop_ids:
        # append location info to products
        shop_products = deepcopy(SHOPS_BY_ID[shop_id]['products'])
        for product in shop_products:
            product['shop'] = {
                'lat': SHOPS_BY_ID[shop_id]['lat'],
                'lng': SHOPS_BY_ID[shop_id]['lng']
            }
            products.append(product)

    # sort by descending popularity
    sorted_products = sorted(
        products, key=lambda product: product['popularity'], reverse=True)

    return sorted_products[:num_products]
