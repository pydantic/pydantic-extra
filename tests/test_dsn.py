import pytest
from pydantic import BaseModel, ValidationError

from pydantic_extra_types.dsn import (
    AmqpDsn,
    ClickHouseDsn,
    CockroachDsn,
    KafkaDsn,
    MariaDBDsn,
    MongoDsn,
    MySQLDsn,
    NatsDsn,
    PostgresDsn,
    RedisDsn,
)


@pytest.mark.parametrize(
    'dsn',
    [
        'postgres://user:pass@localhost:5432/app',
        'postgresql://user:pass@localhost:5432/app',
        'postgresql+asyncpg://user:pass@localhost:5432/app',
        'postgres://user:pass@host1.db.net,host2.db.net:6432/app',
        'postgres://user:pass@%2Fvar%2Flib%2Fpostgresql/dbname',
    ],
)
def test_postgres_dsns(dsn):
    class Model(BaseModel):
        a: PostgresDsn

    assert str(Model(a=dsn).a) == dsn


@pytest.mark.parametrize(
    'dsn,error_message',
    (
        (
            'postgres://user:pass@host1.db.net:4321,/foo/bar:5432/app',
            {
                'type': 'url_parsing',
                'loc': ('a',),
                'msg': 'Input should be a valid URL, empty host',
                'input': 'postgres://user:pass@host1.db.net:4321,/foo/bar:5432/app',
            },
        ),
        (
            'postgres://user:pass@host1.db.net,/app',
            {
                'type': 'url_parsing',
                'loc': ('a',),
                'msg': 'Input should be a valid URL, empty host',
                'input': 'postgres://user:pass@host1.db.net,/app',
            },
        ),
        (
            'postgres://user:pass@/foo/bar:5432,host1.db.net:4321/app',
            {
                'type': 'url_parsing',
                'loc': ('a',),
                'msg': 'Input should be a valid URL, empty host',
                'input': 'postgres://user:pass@/foo/bar:5432,host1.db.net:4321/app',
            },
        ),
        (
            'postgres://user@/foo/bar:5432/app',
            {
                'type': 'url_parsing',
                'loc': ('a',),
                'msg': 'Input should be a valid URL, empty host',
                'input': 'postgres://user@/foo/bar:5432/app',
            },
        ),
        (
            'http://example.org',
            {
                'type': 'url_scheme',
                'loc': ('a',),
                'msg': (
                    "URL scheme should be 'postgres', 'postgresql', 'postgresql+asyncpg', 'postgresql+pg8000', "
                    "'postgresql+psycopg', 'postgresql+psycopg2', 'postgresql+psycopg2cffi', "
                    "'postgresql+py-postgresql' or 'postgresql+pygresql'"
                ),
                'input': 'http://example.org',
            },
        ),
    ),
)
def test_postgres_dsns_validation_error(dsn, error_message):
    class Model(BaseModel):
        a: PostgresDsn

    with pytest.raises(ValidationError) as exc_info:
        Model(a=dsn)
    error = exc_info.value.errors(include_url=False)[0]
    error.pop('ctx', None)
    assert error == error_message


def test_multihost_postgres_dsns():
    class Model(BaseModel):
        a: PostgresDsn

    any_multihost_url = Model(a='postgres://user:pass@host1.db.net:4321,host2.db.net:6432/app').a
    assert str(any_multihost_url) == 'postgres://user:pass@host1.db.net:4321,host2.db.net:6432/app'
    assert any_multihost_url.scheme == 'postgres'
    assert any_multihost_url.path == '/app'
    # insert_assert(any_multihost_url.hosts())
    assert any_multihost_url.hosts() == [
        {'username': 'user', 'password': 'pass', 'host': 'host1.db.net', 'port': 4321},
        {'username': None, 'password': None, 'host': 'host2.db.net', 'port': 6432},
    ]

    any_multihost_url = Model(a='postgres://user:pass@host.db.net:4321/app').a
    assert any_multihost_url.scheme == 'postgres'
    assert str(any_multihost_url) == 'postgres://user:pass@host.db.net:4321/app'
    assert any_multihost_url.path == '/app'
    # insert_assert(any_multihost_url.hosts())
    assert any_multihost_url.hosts() == [{'username': 'user', 'password': 'pass', 'host': 'host.db.net', 'port': 4321}]


def test_cockroach_dsns():
    class Model(BaseModel):
        a: CockroachDsn

    assert str(Model(a='cockroachdb://user:pass@localhost:5432/app').a) == 'cockroachdb://user:pass@localhost:5432/app'
    assert (
        str(Model(a='cockroachdb+psycopg2://user:pass@localhost:5432/app').a)
        == 'cockroachdb+psycopg2://user:pass@localhost:5432/app'
    )
    assert (
        str(Model(a='cockroachdb+asyncpg://user:pass@localhost:5432/app').a)
        == 'cockroachdb+asyncpg://user:pass@localhost:5432/app'
    )

    with pytest.raises(ValidationError) as exc_info:
        Model(a='http://example.org')
    assert exc_info.value.errors(include_url=False)[0]['type'] == 'url_scheme'


def test_amqp_dsns():
    class Model(BaseModel):
        a: AmqpDsn

    m = Model(a='amqp://user:pass@localhost:1234/app')
    assert str(m.a) == 'amqp://user:pass@localhost:1234/app'
    assert m.a.username == 'user'
    assert m.a.password == 'pass'

    m = Model(a='amqps://user:pass@localhost:5432//')
    assert str(m.a) == 'amqps://user:pass@localhost:5432//'

    with pytest.raises(ValidationError) as exc_info:
        Model(a='http://example.org')
    assert exc_info.value.errors(include_url=False)[0]['type'] == 'url_scheme'

    # Password is not required for AMQP protocol
    m = Model(a='amqp://localhost:1234/app')
    assert str(m.a) == 'amqp://localhost:1234/app'
    assert m.a.username is None
    assert m.a.password is None

    # Only schema is required for AMQP protocol.
    # https://www.rabbitmq.com/uri-spec.html
    m = Model(a='amqps://')
    assert m.a.scheme == 'amqps'
    assert m.a.host is None
    assert m.a.port is None
    assert m.a.path is None


def test_redis_dsns():
    class Model(BaseModel):
        a: RedisDsn

    m = Model(a='redis://user:pass@localhost:1234/app')
    assert str(m.a) == 'redis://user:pass@localhost:1234/app'
    assert m.a.username == 'user'
    assert m.a.password == 'pass'

    m = Model(a='rediss://user:pass@localhost:1234/app')
    assert str(m.a) == 'rediss://user:pass@localhost:1234/app'

    m = Model(a='rediss://:pass@localhost:1234')
    assert str(m.a) == 'rediss://:pass@localhost:1234/0'

    with pytest.raises(ValidationError) as exc_info:
        Model(a='http://example.org')
    assert exc_info.value.errors(include_url=False)[0]['type'] == 'url_scheme'

    # Password is not required for Redis protocol
    m = Model(a='redis://localhost:1234/app')
    assert str(m.a) == 'redis://localhost:1234/app'
    assert m.a.username is None
    assert m.a.password is None

    # Only schema is required for Redis protocol. Otherwise it will be set to default
    # https://www.iana.org/assignments/uri-schemes/prov/redis
    m = Model(a='rediss://')
    assert m.a.scheme == 'rediss'
    assert m.a.host == 'localhost'
    assert m.a.port == 6379
    assert m.a.path == '/0'


def test_mongodb_dsns():
    class Model(BaseModel):
        a: MongoDsn

    # TODO: Need to unit tests about "Replica Set", "Sharded cluster" and other deployment modes of MongoDB
    m = Model(a='mongodb://user:pass@localhost:1234/app')
    assert str(m.a) == 'mongodb://user:pass@localhost:1234/app'
    # insert_assert(m.a.hosts())
    assert m.a.hosts() == [{'username': 'user', 'password': 'pass', 'host': 'localhost', 'port': 1234}]

    with pytest.raises(ValidationError) as exc_info:
        Model(a='http://example.org')
    assert exc_info.value.errors(include_url=False)[0]['type'] == 'url_scheme'

    # Password is not required for MongoDB protocol
    m = Model(a='mongodb://localhost:1234/app')
    assert str(m.a) == 'mongodb://localhost:1234/app'
    # insert_assert(m.a.hosts())
    assert m.a.hosts() == [{'username': None, 'password': None, 'host': 'localhost', 'port': 1234}]

    # Only schema and host is required for MongoDB protocol
    m = Model(a='mongodb://localhost')
    assert m.a.scheme == 'mongodb'
    # insert_assert(m.a.hosts())
    assert m.a.hosts() == [{'username': None, 'password': None, 'host': 'localhost', 'port': 27017}]


@pytest.mark.parametrize(
    ('dsn', 'expected'),
    [
        ('mongodb://user:pass@localhost/app', 'mongodb://user:pass@localhost:27017/app'),
        pytest.param(
            'mongodb+srv://user:pass@localhost/app',
            'mongodb+srv://user:pass@localhost/app',
            marks=pytest.mark.xfail(
                reason=(
                    'This case is not supported. '
                    'Check https://github.com/pydantic/pydantic/pull/7116 for more details.'
                )
            ),
        ),
    ],
)
def test_mongodsn_default_ports(dsn: str, expected: str):
    class Model(BaseModel):
        dsn: MongoDsn

    m = Model(dsn=dsn)
    assert str(m.dsn) == expected


def test_kafka_dsns():
    class Model(BaseModel):
        a: KafkaDsn

    m = Model(a='kafka://')
    assert m.a.scheme == 'kafka'
    assert m.a.host == 'localhost'
    assert m.a.port == 9092
    assert str(m.a) == 'kafka://localhost:9092'

    m = Model(a='kafka://kafka1')
    assert str(m.a) == 'kafka://kafka1:9092'

    with pytest.raises(ValidationError) as exc_info:
        Model(a='http://example.org')
    assert exc_info.value.errors(include_url=False)[0]['type'] == 'url_scheme'

    m = Model(a='kafka://kafka3:9093')
    assert m.a.username is None
    assert m.a.password is None


@pytest.mark.parametrize(
    'dsn,result',
    [
        ('nats://user:pass@localhost:4222', 'nats://user:pass@localhost:4222'),
        ('tls://user@localhost', 'tls://user@localhost:4222'),
        ('ws://localhost:2355', 'ws://localhost:2355/'),
        ('tls://', 'tls://localhost:4222'),
        ('ws://:password@localhost:9999', 'ws://:password@localhost:9999/'),
    ],
)
def test_nats_dsns(dsn, result):
    class Model(BaseModel):
        dsn: NatsDsn

    assert str(Model(dsn=dsn).dsn) == result


@pytest.mark.parametrize(
    'dsn',
    [
        'mysql://user:pass@localhost:3306/app',
        'mysql+mysqlconnector://user:pass@localhost:3306/app',
        'mysql+aiomysql://user:pass@localhost:3306/app',
        'mysql+asyncmy://user:pass@localhost:3306/app',
        'mysql+mysqldb://user:pass@localhost:3306/app',
        'mysql+pymysql://user:pass@localhost:3306/app?charset=utf8mb4',
        'mysql+cymysql://user:pass@localhost:3306/app',
        'mysql+pyodbc://user:pass@localhost:3306/app',
    ],
)
def test_mysql_dsns(dsn):
    class Model(BaseModel):
        a: MySQLDsn

    assert str(Model(a=dsn).a) == dsn


@pytest.mark.parametrize(
    'dsn',
    [
        'mariadb://user:pass@localhost:3306/app',
        'mariadb+mariadbconnector://user:pass@localhost:3306/app',
        'mariadb+pymysql://user:pass@localhost:3306/app',
    ],
)
def test_mariadb_dsns(dsn):
    class Model(BaseModel):
        a: MariaDBDsn

    assert str(Model(a=dsn).a) == dsn


@pytest.mark.parametrize(
    'dsn',
    [
        'clickhouse+native://user:pass@localhost:9000/app',
        'clickhouse+asynch://user:pass@localhost:9000/app',
    ],
)
def test_clickhouse_dsns(dsn):
    class Model(BaseModel):
        a: ClickHouseDsn

    assert str(Model(a=dsn).a) == dsn
