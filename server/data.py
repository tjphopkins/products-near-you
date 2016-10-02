import csv
from collections import defaultdict

SHOPS_BY_LAT = defaultdict(dict)
SHOPS_BY_LNG = defaultdict(dict)


def process_data():
    """Process csv files and store data in memory"""
    process_shops()


def process_shops():
    """Process shops.csv. Store shop name and id keyed on lat, and lng
    seperately.
    """
    with open('data/shops.csv') as csvfile:
        shops_reader = csv.reader(csvfile)
        shops_reader.next() # skip the first row since these are headings
        for row in shops_reader:
            shop_id, shop_name, shop_lat, shop_lng = row
            SHOPS_BY_LAT[float(shop_lat)]['id'] = shop_id
            SHOPS_BY_LAT[float(shop_lat)]['name'] = shop_name
            SHOPS_BY_LAT[float(shop_lng)]['id'] = shop_id
            SHOPS_BY_LAT[float(shop_lng)]['name'] = shop_name
