from sqlalchemy import Table, Column, Integer, String, Boolean, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
import sqlalchemy as sa

METADATA = sa.MetaData()

services = Table(
    'services', METADATA,
    Column('name', String(40), unique=True, primary_key=True),
    Column('protocols', JSONB),
    Column('meta', JSONB)
)

endpoints = Table(
    'endpoints', METADATA,
    Column('id', Integer, autoincrement=True, primary_key=True),
    Column('path', String, unique=True, index=True),
    Column('service', String, index=True),
    Column('methods', ARRAY(String)),
    Column('deprecated', Boolean, server_default=sa.text('false')),
    Column('locked', Boolean, server_default=sa.text('true')),
    Column('new_service', String, nullable=True),
    Column('toggle', String, nullable=True),
    Column('stripped_path', String, index=True, nullable=True)
)
