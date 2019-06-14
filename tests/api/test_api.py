import asyncio

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


def test_put_service(client):
    body = {
        'name': 'obi_wan',
        'protocols': {'http': {'host': 'http://obiwan'}},
        'meta': {'master': True, 'squad': 'council'},
        'endpoints': [{'path': '/api/highground', 'methods': ['post', 'get']},
                      {'path': '/api/hello_there', 'methods': ['get']}]
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


def test_get_endpoints(client):
    # endpoints defined on PUT services should now show up
    response = client.get('/api/endpoints')
    assert response.status_code == 200
    body = response.json()
    endpoints = body.get('endpoints')
    assert isinstance(endpoints, list)
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
