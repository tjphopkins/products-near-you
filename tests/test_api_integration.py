class TestAPI(object):

    def test_empty_param(self, get):
        response = get('/search?count=&radius=2000')
        assert response.json['message'] == 'No count provided.'
        assert response.json['success'] is False

    def test_invalid_param(self, get):
        response = get('/search?count=10&radius=2001')
        assert response.json['message'] == \
            'Search distance must be between 0 and 2000m'
        assert response.json['success'] is False

    def test_search_without_tags(self, get):
        # Note that this doesn't test the validity of the results, only
        # the expected structure of the response.
        response = get(
            '/search?count=10&radius=2000&lat=59.32830&lng=18.06353&tags=')
        response_json = response.json
        assert response_json['success']
        assert len(response_json['products']) == 10
        for product in response_json['products']:
            assert 'shop' in product
            assert 'popularity' in product
            assert 'id' in product
            assert 'title' in product
            assert 'lat' in product['shop']
            assert 'lng' in product['shop']

    def test_search_with_tags(self, get):
        # Note that this doesn't test the validity of the results, only
        # the expected structure of the response.
        response = get(
            '/search?count=10&radius=2000&lat=59.32830&lng=18.06353&'
            'tags=trousers,tshirts')
        response_json = response.json
        assert response_json['success']
        assert len(response_json['products']) == 10
        for product in response_json['products']:
            assert 'shop' in product
            assert 'popularity' in product
            assert 'id' in product
            assert 'title' in product
            assert 'lat' in product['shop']
            assert 'lng' in product['shop']

    def test_search_no_products(self, get):
        response = get('/search?count=10&radius=2000&lat=18.06353&lng=59.32830')
        response_json = response.json
        assert response_json['success']
        assert response_json['products'] == []
