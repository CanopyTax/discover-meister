import asyncio
import urllib.parse

import pytest
from pytest import fixture
from starlette.testclient import TestClient

from dmeister import core


@fixture(scope='session')
def app():
    app = core.init()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(core.pg_init())
    return app


@fixture(scope='module')
def client(app):
    return TestClient(app)


def test_index(client):
    response = client.get('/')
    assert response.status_code == 200


def test_get_services_smoke(client):
    response = client.get('/api/services')
    assert response.status_code == 200


_endpoints = [{'path': '/api/highground', 'methods': ['post', 'get']},
              {'path': '/api/the_force', 'methods': ['post', 'get']},
              {'path': '/api/wookies/{name}/bandoliers', 'methods': ['post', 'get']},
              {'path': '/api/clones/{id}/blasters/{id}', 'methods': ['post', 'get']},
              {'path': '/api/bad_feeling', 'methods': ['post', 'get']},
              {'path': '/api/bad_feeling/{about_this}', 'methods': ['post', 'get']},
              {'path': '/api/bad_feeling/traps', 'methods': ['post', 'get']},
              {'path': '/api/bad_feeling/{}/traps/{}', 'methods': ['post', 'get']},
              {'path': '/api/mouse_droid/{id}:discover', 'methods': ['post', 'get']},
              {'path': '/api/mouse_droid/favorite:discover', 'methods': ['post', 'get']},
              {'path': '/api/hello_there', 'methods': ['get']}]


def test_put_service(client):
    body = {
        'name': 'obi_wan',
        'protocols': {'http': {'host': 'http://obiwan'}},
        'meta': {'master': True, 'squad': 'council'},
        'endpoints': _endpoints
    }

    response = client.put('/api/services/obi_wan', json=body)
    assert response.status_code == 200
    j = response.json()
    assert 'name' in j
    assert 'protocols' in j
    assert 'meta' in j
    assert 'endpoints' in j


def test_get_service(client):
    response = client.get('/api/services/obi_wan')
    assert response.status_code == 200
    body = response.json()
    assert body.get('name') == 'obi_wan'


def test_get_services(client):
    response = client.get('/api/services')
    assert response.status_code == 200
    body = response.json()
    services = body.get('services')
    assert isinstance(services, list)
    found = False
    for service in services:
        if service['name'] == 'obi_wan':
            found = True
            break

    assert found


def test_get_service_endpoints(client):
    response = client.get('/api/services/obi_wan/endpoints')
    assert response.status_code == 200
    body = response.json()
    assert 'endpoints' in body
    endpoints = body['endpoints']
    assert isinstance(endpoints, list)
    assert len(endpoints) == len(_endpoints)


def test_put_another_service(client):
    body = {
        'name': 'han',
        'protocols': {'http': {'host': 'http://han'}},
        'meta': {'master': False, 'squad': 'rebels'},
        'endpoints': [{'path': '/api/parts', 'methods': ['get']},
                      {'path': '/api/jobs', 'methods': ['post', 'get']}]
    }
    response = client.put('/api/services/han', json=body)
    assert response.status_code == 200
    j = response.json()
    assert 'name' in j
    assert 'protocols' in j
    assert 'meta' in j
    assert 'endpoints' in j


def test_get_all_endpoints(client):
    # endpoints defined on PUT services should now show up
    response = client.get('/api/endpoints')
    assert response.status_code == 200
    body = response.json()
    endpoints = body.get('endpoints')
    assert isinstance(endpoints, list)
    assert len(endpoints) == len(_endpoints) + 2


def test_delete_endpoints(client):
    body = {
        'name': 'han',
        'protocols': {'http': {'host': 'http://han'}},
        'meta': {'master': False, 'squad': 'rebels'},
        'endpoints': []
    }
    response = client.put('/api/services/han', json=body)
    assert response.status_code == 200


def test_get_endpoints(client):
    # endpoints defined on PUT services should now show up
    response = client.get('/api/endpoints')
    assert response.status_code == 200
    body = response.json()
    endpoints = body.get('endpoints')
    assert isinstance(endpoints, list)
    assert len(endpoints) == len(_endpoints)
    found = False
    for endpoint in endpoints:
        # these things should always be in the body
        assert 'id' in endpoint
        assert 'service' in endpoint
        assert 'path' in endpoint
        assert 'methods' in endpoint
        assert 'deprecated' in endpoint

        # these things should NOT be in the body
        assert 'toggle' not in endpoint
        assert 'locked' not in endpoint
        assert 'new_service' not in endpoint

        # now check for our specific endpoint
        if endpoint['path'] == '/api/hello_there':
            found = True

    assert found


def test_search_endpoints(client):
    highground_path = '/api/highground'
    wookies_wildcard_path = '/api/wookies/chewbacca/bandoliers'
    wookies_non_existent_path = '/api/wookies/chewbacca/something_else/bandoliers'
    clones_non_existent_path = '/api/clones/ABC123'
    bad_feeling_wildcard_path = '/api/bad_feeling/its_a-trap'
    bad_feeling_traps_path = '/api/bad_feeling/traps'
    mouse_droid_wildcard_path = '/api/mouse_droid/123ABC:discover'
    mouse_droid_favorite_path = '/api/mouse_droid/favorite:discover'

    body = {'paths': [
        highground_path,
        wookies_wildcard_path,
        wookies_non_existent_path,
        clones_non_existent_path,
        bad_feeling_wildcard_path,
        bad_feeling_traps_path,
        mouse_droid_wildcard_path,
        mouse_droid_favorite_path
    ]}

    response = client.post('/api/endpoints:search', json=body)
    assert response.status_code == 200
    resp_body = response.json()
    for path in body['paths']:
        assert path in resp_body

    assert resp_body[highground_path]['path'] == '/api/highground'
    assert resp_body[wookies_wildcard_path]['path'] == '/api/wookies/{name}/bandoliers'
    assert resp_body[bad_feeling_wildcard_path]['path'] == '/api/bad_feeling/{about_this}'
    assert resp_body[bad_feeling_traps_path]['path'] == '/api/bad_feeling/traps'
    assert resp_body[mouse_droid_wildcard_path]['path'] == '/api/mouse_droid/{id}:discover'
    assert resp_body[mouse_droid_favorite_path]['path'] == '/api/mouse_droid/favorite:discover'

    assert not resp_body[wookies_non_existent_path]
    assert not resp_body[clones_non_existent_path]


@pytest.mark.parametrize('search_term, expected',
                         [('api', [e['path'] for e in _endpoints]),
                          ('/api/highground', ['/api/highground']),
                          ('highground', ['/api/highground']),
                          ('/api/bad_feeling', ['/api/bad_feeling', '/api/bad_feeling/{about_this}',
                                                '/api/bad_feeling/traps', '/api/bad_feeling/{}/traps/{}']),
                          ('bad_feeling/traps', ['/api/bad_feeling/traps']),
                          ('bad_feeling/wildcard', ['/api/bad_feeling/{about_this}', '/api/bad_feeling/{}/traps/{}']),
                          ('just_a_wildcard', []),
                          ('/just_a_wildcard', []),
                          ('just_a_wildcard/', [])])
def test_filter_endpoints(client, search_term, expected):
    response = client.get('/api/endpoints?path=' + urllib.parse.quote(search_term))
    assert response.status_code == 200
    body = response.json()
    assert body
    assert 'endpoints' in body
    endpoints = body['endpoints']
    assert isinstance(endpoints, list)
    assert len(endpoints) == len(expected)
    for e in endpoints:
        assert e['path'] in expected


def test_add_new_service_existing_route(client):
    body = {
        'name': 'anakin',
        'protocols': {'http': {'host': 'http://anakin.skywalker'}},
        'meta': {'master': False, 'squad': 'council'},
        'endpoints': [{'path': '/api/highground', 'methods': ['post', 'get']},
                      {'path': '/api/younglings', 'methods': ['delete']}]
    }
    response = client.put('/api/services/anakin', json=body)
    assert response.status_code == 409
    body = response.json()
    assert 'message' in body
    assert 'paths' in body
    assert '/api/highground' in body['paths']


def test_unlock_route(client):
    body = {
        'endpoints': [
            {'path': '/api/highground', 'locked': False}]
    }
    response = client.patch('/api/services/obi_wan/endpoints', json=body)
    assert response.status_code == 200
    body = response.json()
    endpoints = body.get('endpoints')
    assert isinstance(endpoints, list)
    assert len(endpoints) == 1


def test_takeover_route(client):
    body = {
        'name': 'anakin',
        'protocols': {'http': {'host': 'http://anakin.skywalker'}},
        'meta': {'master': False, 'squad': 'council'},
        'endpoints': [{'path': '/api/highground', 'methods': ['post', 'get'], 'toggle': 'death-star'},
                      {'path': '/api/younglings', 'methods': ['delete']}]
    }
    response = client.put('/api/services/anakin', json=body)
    assert response.status_code == 200
    j = response.json()
    assert 'name' in j
    assert 'protocols' in j
    assert 'meta' in j
    assert 'endpoints' in j


def test_add_new_service_transitioning_route(client):
    body = {
        'name': 'luke',
        'protocols': {'http': {'host': 'http://luke.skywalker'}},
        'meta': {'master': True, 'squad': 'jedi'},
        'endpoints': [{'path': '/api/highground', 'methods': ['patch']}]
    }
    response = client.put('/api/services/luke', json=body)
    assert response.status_code == 409
    body = response.json()
    assert 'message' in body
    assert 'paths' in body
    assert '/api/highground' in body['paths']


def test_complete_route_takeover(client):
    body = {
        'name': 'obi_wan',
        'protocols': {'http': {'host': 'http://obiwan'}},
        'meta': {'master': True, 'squad': 'council'},
        'endpoints': [{'path': '/api/hello_there', 'methods': ['get']}]
    }
    put_response = client.put('/api/services/obi_wan', json=body)
    assert put_response.status_code == 200
    get_response = client.get('/api/endpoints')
    assert get_response.status_code == 200
    body = get_response.json()
    endpoints = body.get('endpoints')
    for endpoint in endpoints:
        if endpoint['path'] == '/api/highground':
            assert endpoint['service'] == 'anakin'
            assert not endpoint.get('new_service')
