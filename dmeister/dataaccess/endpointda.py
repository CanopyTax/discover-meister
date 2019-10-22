from typing import List

from asyncpgsa import pg
from sqlalchemy import text

from ..models import Endpoint
from . import db


async def get_endpoints(service_name=None) -> List[Endpoint]:
    query = db.endpoints.select()
    if service_name:
        query = query.where(db.endpoints.c.service == service_name)

    results = await pg.fetch(query)
    endpoints = []
    for row in results:
        endpoint = Endpoint.from_db(row)
        endpoints.append(endpoint)

    return endpoints


async def add_endpoint(endpoint: Endpoint):
    insert = db.endpoints.insert()\
        .values(path=endpoint.path,
                stripped_path=endpoint.stripped_path,
                methods=endpoint.methods,
                service=endpoint.service,
                locked=True)
    ep_id = await pg.fetchval(insert)
    return ep_id


async def delete_endpoint(stripped_path):
    await pg.fetchval(db.endpoints.delete()
                      .where(db.endpoints.c.stripped_path == stripped_path))


async def delete_endpoints_for_service(service, connection=None):
    if not connection:
        connection = pg
    await connection.fetchval(db.endpoints.delete()
                              .where(db.endpoints.c.service == service))


async def update_endpoint(endpoint: Endpoint) -> Endpoint:
    values = {'service': endpoint.service,
              'methods': endpoint.methods,
              'locked': endpoint.locked,
              'deprecated': endpoint.deprecated,
              'new_service': endpoint.new_service,
              'toggle': endpoint.toggle,
              'path': endpoint.path}

    update = db.endpoints.update().values(values) \
        .where(db.endpoints.c.stripped_path == endpoint.stripped_path).returning(text('*'))

    ep = await pg.fetchrow(update)
    return Endpoint.from_db(ep)
