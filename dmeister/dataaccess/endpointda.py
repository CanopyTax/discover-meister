from asyncpgsa import pg
from sqlalchemy import text

from . import db


async def get_endpoints(service_name=None, internal_data=False):
    query = db.endpoints.select()
    if service_name:
        query.where(db.endpoints.c.service == service_name)

    results = await pg.fetch(query)
    endpoints = []
    for row in results:
        endpoint = _clean_endpoint(row, internal_data=internal_data)
        endpoints.append(endpoint)

    return endpoints


async def add_endpoint(path, methods, service_name):
    insert = db.endpoints.insert().values(path=path,
                                          methods=methods,
                                          service=service_name,
                                          locked=True)
    ep_id = await pg.fetchval(insert)
    return ep_id


async def delete_endpoint(path):
    await pg.fetchval(db.endpoints.delete()
                      .where(db.endpoints.c.path == path))


async def update_endpoint(path, service_name,
                          methods=None, locked=None, deprecated=None, new_service=None, toggle=None):
    values = {'path': path, 'service': service_name}
    if methods:
        values['methods'] = methods
    if locked is not None:
        values['locked'] = locked
    if deprecated is not None:
        values['deprecated'] = deprecated
    if new_service:
        values['new_service'] = new_service
    if toggle:
        values['toggle'] = toggle

    update = db.endpoints.update().values(values) \
        .where(db.endpoints.c.path == path).returning(text('*'))

    ep = await pg.fetchrow(update)
    return _clean_endpoint(ep)


def _clean_endpoint(endpoint, internal_data=True):
    ep = {'id': endpoint['id'],
          'path': endpoint['path'],
          'service': endpoint['service'],
          'methods': endpoint['methods'],
          'deprecated': endpoint['deprecated']}
    if internal_data:
        ep['locked'] = endpoint['locked']
        ep['new_service'] = endpoint['new_service']
        ep['toggle'] = endpoint['toggle']
    return ep
