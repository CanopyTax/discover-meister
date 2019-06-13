import json

from asyncpgsa import pg
from sqlalchemy.sql import text
from sqlalchemy.dialects.postgresql import insert

from . import db


async def insert_service(service_name, protocols, meta):
    values = dict(name=service_name, protocols=protocols, meta=meta)
    upsert = insert(db.services).values(**values) \
        .on_conflict_do_update(
        index_elements=[db.services.c.name],
        set_=values
    ).returning(text('*'))
    result = await pg.fetchrow(upsert)
    return {
        'name': result['name'],
        'protocols': json.loads(result['protocols']),
        'meta': json.loads(result['meta'])
    }


async def get_services(service_name=None):
    query = db.services.select()
    if service_name:
        query.where(db.services.c.name == service_name)

    results = await pg.fetch(query)
    return [{'name': row['name'],
             'protocols': json.loads(row['protocols']),
             'meta': json.loads(row['meta'])} for row in results]
