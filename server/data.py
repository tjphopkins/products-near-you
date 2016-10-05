import csv
from copy import deepcopy
from collections import defaultdict

from server.search_utils import find_bounding_box, is_within_search_radius


SHOPS_BY_LAT = {}
SHOPS_BY_LNG = {}
SHOPS_BY_TAG = defaultdict(list)
SHOPS_BY_ID = {}
TAGS_BY_NAME = {}


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


def data_path(app):
    def data_path_fn(filename):
        data_path = app.config['DATA_PATH']
        return u"%s/%s" % (data_path, filename)

    return data_path_fn


def _process_shops(data_path_fn):
    """
    Process shops.csv. Populates three dicts:
    * SHOPS_BY_LAT: shop_id keyed on lat
    * SHOPS_BY_LONG: shop_id keyed on lng
    * SHOPS_BY_ID: shop info keyed on id
    """
    with open(data_path_fn('shops.csv')) as csvfile:
        shops_reader = csv.reader(csvfile)
        shops_reader.next() # ignore the first row since these are headings
        for row in shops_reader:
            shop_id, shop_name, shop_lat, shop_lng = row
            SHOPS_BY_LAT[float(shop_lat)] = shop_id
            SHOPS_BY_LNG[float(shop_lng)] = shop_id
            SHOPS_BY_ID[shop_id] = {
                'lat': shop_lat, 'lng': shop_lng, 'products': []
            }


def _process_products(data_path_fn):
    """Process products.csv. Populates SHOPS_BY_ID with products."""
    with open(data_path_fn('products.csv')) as csvfile:
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


def _process_tags(data_path_fn):
    """
    Process tags.csv and taggings.csv. Populates:
    * SHOPS_BY_TAG
    * TAGS_BY_NAME
    """
    with open(data_path_fn('tags.csv')) as csvfile:
        tags_reader = csv.reader(csvfile)
        tags_reader.next()
        for row in tags_reader:
            tag_id, tag_name = row
            TAGS_BY_NAME[tag_name] = tag_id

    with open(data_path_fn('taggings.csv')) as csvfile:
        taggings_reader = csv.reader(csvfile)
        taggings_reader.next()
        for row in taggings_reader:
            tagging_id, shop_id, tag_id = row
            SHOPS_BY_TAG[tag_id].append(shop_id)


def process_data(app):
    """This process the data stored in csv files and constructs dictionaries to
    store this data in memory. 5 dictionaries are created:
    * SHOPS_BY_LAT of the form {latitude: shop_id, ...}
    * SHOPS_BY_LNG of the form {longitude: shop_id, ...}
    * SHOPS_BY_TAG of the form {tag_id: shop_id}
    * SHOPS_BY_ID of the form {shop_id: {<shop_data>}}
    * TAGS_BY_NAME of the form {tag_name: tag_id}

    These are structured in such a way to aid efficient lookups in
    find_most_popular_products_in_search_area. This however comes as the expense
    of duplication of information and increased memory usuage. Given that there
    are currently only around 10000 products and 10000 shops, there is probably
    not much in it. But it paves the way for having more data items.
    """
    data_path_fn = data_path(app)
    _process_shops(data_path_fn)
    _process_products(data_path_fn)
    _process_tags(data_path_fn)


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
