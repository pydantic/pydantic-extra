import sys

if sys.version_info < (3, 9):  # pragma: no cover
    from typing_extensions import Annotated  # pragma: no cover
else:
    from typing import Annotated  # pragma: no cover

from pydantic import UrlConstraints
from pydantic_core import MultiHostUrl, Url

PostgresDsn = Annotated[
    MultiHostUrl,
    UrlConstraints(
        host_required=True,
        allowed_schemes=[
            'postgres',
            'postgresql',
            'postgresql+asyncpg',
            'postgresql+pg8000',
            'postgresql+psycopg',
            'postgresql+psycopg2',
            'postgresql+psycopg2cffi',
            'postgresql+py-postgresql',
            'postgresql+pygresql',
        ],
    ),
]
"""A type that will accept any Postgres DSN.

* User info required
* TLD not required
* Host required
* Supports multiple hosts

If further validation is required, these properties can be used by validators to enforce specific behaviour:

```py
from pydantic import (
    BaseModel,
    HttpUrl,
    PostgresDsn,
    ValidationError,
    field_validator,
)

class MyModel(BaseModel):
    url: HttpUrl

m = MyModel(url='http://www.example.com')

# the repr() method for a url will display all properties of the url
print(repr(m.url))
#> Url('http://www.example.com/')
print(m.url.scheme)
#> http
print(m.url.host)
#> www.example.com
print(m.url.port)
#> 80

class MyDatabaseModel(BaseModel):
    db: PostgresDsn

    @field_validator('db')
    def check_db_name(cls, v):
        assert v.path and len(v.path) > 1, 'database must be provided'
        return v

m = MyDatabaseModel(db='postgres://user:pass@localhost:5432/foobar')
print(m.db)
#> postgres://user:pass@localhost:5432/foobar

try:
    MyDatabaseModel(db='postgres://user:pass@localhost:5432')
except ValidationError as e:
    print(e)
    '''
    1 validation error for MyDatabaseModel
    db
      Assertion failed, database must be provided
    assert (None)
     +  where None = MultiHostUrl('postgres://user:pass@localhost:5432').path [type=assertion_error, input_value='postgres://user:pass@localhost:5432', input_type=str]
    '''
```
"""
CockroachDsn = Annotated[
    Url,
    UrlConstraints(
        host_required=True,
        allowed_schemes=[
            'cockroachdb',
            'cockroachdb+psycopg2',
            'cockroachdb+asyncpg',
        ],
    ),
]
"""A type that will accept any Cockroach DSN.

* User info required
* TLD not required
* Host required
"""
AmqpDsn = Annotated[Url, UrlConstraints(allowed_schemes=['amqp', 'amqps'])]  # +
"""A type that will accept any AMQP DSN.

* User info required
* TLD not required
* Host required
"""
RedisDsn = Annotated[
    Url,
    UrlConstraints(allowed_schemes=['redis', 'rediss'], default_host='localhost', default_port=6379, default_path='/0'),
]
"""A type that will accept any Redis DSN.

* User info required
* TLD not required
* Host required (e.g., `rediss://:pass@localhost`)
"""
MongoDsn = Annotated[MultiHostUrl, UrlConstraints(allowed_schemes=['mongodb', 'mongodb+srv'], default_port=27017)]  # +
"""A type that will accept any MongoDB DSN.

* User info not required
* Database name not required
* Port not required
* User info may be passed without user part (e.g., `mongodb://mongodb0.example.com:27017`).
"""
KafkaDsn = Annotated[Url, UrlConstraints(allowed_schemes=['kafka'], default_host='localhost', default_port=9092)]  # +
"""A type that will accept any Kafka DSN.

* User info required
* TLD not required
* Host required
"""
NatsDsn = Annotated[
    Url, UrlConstraints(allowed_schemes=['nats', 'tls', 'ws'], default_host='localhost', default_port=4222)  # +
]
"""A type that will accept any NATS DSN.

NATS is a connective technology built for the ever increasingly hyper-connected world.
It is a single technology that enables applications to securely communicate across
any combination of cloud vendors, on-premise, edge, web and mobile, and devices.
More: https://nats.io
"""
MySQLDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=[
            'mysql',
            'mysql+mysqlconnector',
            'mysql+aiomysql',
            'mysql+asyncmy',
            'mysql+mysqldb',
            'mysql+pymysql',
            'mysql+cymysql',
            'mysql+pyodbc',
        ],
        default_port=3306,
    ),
]
"""A type that will accept any MySQL DSN.

* User info required
* TLD not required
* Host required
"""
MariaDBDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=['mariadb', 'mariadb+mariadbconnector', 'mariadb+pymysql'],
        default_port=3306,
    ),
]
"""A type that will accept any MariaDB DSN.

* User info required
* TLD not required
* Host required
"""
ClickHouseDsn = Annotated[
    Url,
    UrlConstraints(
        allowed_schemes=['clickhouse+native', 'clickhouse+asynch'],
        default_host='localhost',
        default_port=9000,
    ),
]
"""A type that will accept any ClickHouse DSN.

* User info required
* TLD not required
* Host required
"""
