from asyncpgsa import pg

from . import db


async def get_endpoints(service_name=None, internal_data=False):
    query = db.endpoints.select()
    if service_name:
        query.where(db.endpoints.c.service == service_name)

    results = await pg.fetch(query)
    endpoints = []
    for row in results:
        endpoint = {'id': row['id'],
                    'path': row['path'],
                    'service': row['service'],
                    'methods': row['methods'],
                    'deprecated': row['deprecated']}
        if internal_data:
            endpoint['locked'] = row['locked']
            endpoint['new_service'] = row['new_service']
            endpoint['toggle'] = row['toggle']

        endpoints.append(endpoint)

    return endpoints


async def add_endpoint(path, methods, service_name):
    insert = db.endpoints.insert().values(path=path, methods=methods, service=service_name)
    ep_id = await pg.fetchval(insert)
    return ep_id
