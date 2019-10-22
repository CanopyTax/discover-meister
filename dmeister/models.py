from dataclasses import dataclass, field
from typing import List
import re

PATH_VARIABLE_REGEX = re.compile(r'{.*?}')
ALLOWED_METHODS = ['post', 'get', 'put', 'patch', 'delete', 'head', 'options']


@dataclass
class Endpoint:
    path: str
    methods: List[str] = field(default_factory=list)
    service: str = ''
    endpoint_id: int = -1
    deprecated: bool = False
    stripped_path: str = field(default=True, metadata={'internal': True})
    locked: bool = field(default=True, metadata={'internal': True})
    toggle: str = field(default='', metadata={'internal': True})
    new_service: str = field(default='', metadata={'internal': True})

    def __post_init__(self):
        self.path = self.path.strip('/')
        self.stripped_path = self.strip_path(self.path)
        self.methods = self._clean_methods(self.methods)

    @staticmethod
    def strip_path(path):
        return re.sub(PATH_VARIABLE_REGEX, '{}', path)

    @staticmethod
    def from_db(row) -> 'Endpoint':
        return Endpoint(
            path=row['path'],
            methods=row['methods'],
            service=row['service'],
            endpoint_id=row['id'],
            deprecated=row['deprecated'],
            locked=row['locked'],
            new_service=row['new_service'],
            toggle=row['toggle']

        )

    @staticmethod
    def _clean_methods(methods) -> List[str]:
        return list({m for m in methods if m.lower() in ALLOWED_METHODS})


@dataclass
class Endpoints:
    endpoints: List[Endpoint]
