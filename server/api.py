# -*- coding: utf-8 -*-

from flask import Blueprint, jsonify, request

from server.data import find_most_popular_products_in_search_area


api = Blueprint('api', __name__)


class EmptyParam(Exception):
    def __init__(self, param_name):
        self.param_name = param_name

    def __str__(self):
        return "No {param} provided.".format(
            param=self.param_name)


class InvalidParam(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def _get_and_validate_get_params():
    count = request.args.get('count')
    if not count:
        raise EmptyParam('count')
    count = int(count)

    radius = request.args.get('radius')
    if not radius:
        raise EmptyParam('radius')
    radius = float(radius) / 1000.0
    if radius < 0 or radius > 2:
        raise InvalidParam("Search distance must be between 0 and 2000m")

    lat = request.args.get('lat')
    if not lat:
        raise EmptyParam('latitude')
    lat = float(lat)
    if abs(lat) > 90:
        raise InvalidParam("Latitude must be between -90 and 90 degrees")

    lng = request.args.get('lng')
    if not lng:
        raise EmptyParam('longitude')
    lng = float(lng)
    if abs(lng) > 180:
        raise InvalidParam("Longitude must be between -180 and 180 degrees")

    tags = request.args.get('tags')
    tags = tags.split(',') if tags else []

    return count, radius, lat, lng, tags


@api.route('/search', methods=['GET'])
def search():
    """Search endpoint.

    :param count, number of products to return
    :param radius
    :param lat
    :param lng

    :return array of products
    """
    try:
        count, radius, lat, lng, tags = _get_and_validate_get_params()
    except (InvalidParam, EmptyParam) as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

    products = find_most_popular_products_in_search_area(
        lat, lng, radius, count, tags)

    return jsonify({'products': products})
