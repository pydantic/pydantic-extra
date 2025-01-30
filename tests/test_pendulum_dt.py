from datetime import date, datetime, timedelta, time
from datetime import timezone as tz

import pendulum
import pytest
from pydantic import BaseModel, TypeAdapter, ValidationError

from pydantic_extra_types.pendulum_dt import Date, DateTime, Duration, Time

UTC = tz.utc

DtTypeAdapter = TypeAdapter(datetime)


class DtModel(BaseModel):
    dt: DateTime


class TimeModel(BaseModel):
    t: Time


class DateTimeNonStrict(DateTime, strict=False):
    pass


class DtModelNotStrict(BaseModel):
    dt: DateTimeNonStrict


class DateModel(BaseModel):
    d: Date


class DurationModel(BaseModel):
    delta_t: Duration


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.now(),
        datetime.now(),
        datetime.now(UTC),
    ],
)
def test_existing_instance(instance):
    """Verifies that constructing a model with an existing pendulum dt doesn't throw."""
    model = DtModel(dt=instance)
    if isinstance(instance, datetime):
        assert model.dt == pendulum.instance(instance)
        if instance.tzinfo is None and isinstance(instance, datetime):
            instance = model.dt.replace(tzinfo=UTC)  # pendulum defaults to UTC
        dt = model.dt
    else:
        assert model.dt == instance
        dt = model.dt

    assert dt.day == instance.day
    assert dt.month == instance.month
    assert dt.year == instance.year
    assert dt.hour == instance.hour
    assert dt.minute == instance.minute
    assert dt.second == instance.second
    assert dt.microsecond == instance.microsecond
    assert isinstance(dt, pendulum.DateTime)
    assert type(dt) is DateTime
    if dt.tzinfo != instance.tzinfo:
        assert dt.tzinfo.utcoffset(dt) == instance.tzinfo.utcoffset(instance)


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.today(),
        date.today(),
    ],
)
def test_pendulum_date_existing_instance(instance):
    """Verifies that constructing a model with an existing pendulum date doesn't throw."""
    model = DateModel(d=instance)
    if isinstance(instance, datetime):
        assert model.d == pendulum.instance(instance).date()
    else:
        assert model.d == instance
    d = model.d
    assert d.day == instance.day
    assert d.month == instance.month
    assert d.year == instance.year
    assert isinstance(d, pendulum.Date)
    assert type(d) is Date


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.duration(days=42, hours=13, minutes=37),
        pendulum.duration(days=-42, hours=13, minutes=37),
        pendulum.duration(weeks=97),
        pendulum.duration(days=463),
        pendulum.duration(milliseconds=90122),
        pendulum.duration(microseconds=90122),
        pendulum.duration(
            years=2,
            months=3,
            weeks=19,
            days=1,
            hours=25,
            seconds=732,
            milliseconds=123,
            microseconds=1324,
        ),
        timedelta(days=42, hours=13, minutes=37),
        timedelta(days=-42, hours=13, minutes=37),
        timedelta(
            weeks=19,
            days=1,
            hours=25,
            seconds=732,
            milliseconds=123,
            microseconds=1324,
        ),
    ],
)
def test_duration_timedelta__existing_instance(instance):
    """Verifies that constructing a model with an existing pendulum duration doesn't throw."""
    model = DurationModel(delta_t=instance)

    assert model.delta_t.total_seconds() == instance.total_seconds()
    assert isinstance(model.delta_t, pendulum.Duration)
    assert model.delta_t


@pytest.mark.parametrize(
    'dt',
    [
        pendulum.now().to_iso8601_string(),
        pendulum.now().to_w3c_string(),
    ],
)
def test_pendulum_dt_from_serialized(dt):
    """Verifies that building an instance from serialized, well-formed strings decode properly."""
    dt_actual = pendulum.parse(dt)
    model = DtModel(dt=dt)
    assert model.dt == dt_actual
    assert type(model.dt) is DateTime
    assert isinstance(model.dt, pendulum.DateTime)


@pytest.mark.parametrize(
    'dt',
    [
        pendulum.now().to_iso8601_string(),
        pendulum.now().to_w3c_string(),
    ],
)
def test_pendulum_dt_from_serialized_preserves_timezones(dt):
    """Verifies that building an instance from serialized, well-formed strings decode
    properly and preserves the timezone information across all of the Pendulum DateTime
    properties.  Regression test for pydantic/pydantic-extra-types#188.
    """
    dt_actual = pendulum.parse(dt)
    model = DtModel(dt=dt)
    assert model.dt == dt_actual
    assert type(model.dt) is DateTime
    assert isinstance(model.dt, pendulum.DateTime)
    assert model.dt.tzinfo is not None
    assert model.dt.tzinfo.utcoffset(model.dt) == dt_actual.tzinfo.utcoffset(dt_actual)
    assert model.dt.tz is not None
    assert model.dt.tz.utcoffset(model.dt) == dt_actual.tz.utcoffset(dt_actual)
    assert model.dt.timezone is not None
    assert model.dt.timezone.utcoffset(model.dt) == dt_actual.timezone.utcoffset(dt_actual)


@pytest.mark.parametrize(
    'dt',
    [
        pendulum.now().to_iso8601_string(),
        pendulum.now().to_w3c_string(),
        'Sat Oct 11 17:13:46 UTC 2003',  # date util parsing
        pendulum.now().to_iso8601_string()[:5],  # actualy valid or pendulum.parse(dt, strict=False) would fail here
    ],
)
def test_pendulum_dt_not_strict_from_serialized(dt):
    """Verifies that building an instance from serialized, well-formed strings decode properly."""
    dt_actual = pendulum.parse(dt, strict=False)
    model = DtModelNotStrict(dt=dt)
    assert model.dt == dt_actual
    assert type(model.dt) is DateTime
    assert isinstance(model.dt, pendulum.DateTime)


@pytest.mark.parametrize(
    'dt',
    [
        pendulum.now().to_iso8601_string(),
        pendulum.now().to_w3c_string(),
        1718096578,
        1718096578.5,
        -5,
        -5.5,
        float('-0'),
        '1718096578',
        '1718096578.5',
        '-5',
        '-5.5',
        '-0',
        '-0.0',
        '+0.0',
        '+1718096578.5',
        float('-2e10') - 1.0,
        float('2e10') + 1.0,
        -2e10 - 1,
        2e10 + 1,
    ],
)
def test_pendulum_dt_from_str_unix_timestamp(dt):
    """Verifies that building an instance from serialized, well-formed strings decode properly."""
    dt_actual = pendulum.instance(DtTypeAdapter.validate_python(dt))
    model = DtModel(dt=dt)
    assert model.dt == dt_actual
    assert type(model.dt) is DateTime
    assert isinstance(model.dt, pendulum.DateTime)


@pytest.mark.parametrize(
    'dt',
    [
        1718096578,
        1718096578.5,
        -5,
        -5.5,
        float('-0'),
        '1718096578',
        '1718096578.5',
        '-5',
        '-5.5',
        '-0',
        '-0.0',
        '+0.0',
        '+1718096578.5',
        float('-2e10') - 1.0,
        float('2e10') + 1.0,
        -2e10 - 1,
        2e10 + 1,
    ],
)
def test_pendulum_dt_from_str_unix_timestamp_is_utc(dt):
    """Verifies that without timezone information, it is coerced to UTC. As in pendulum"""
    model = DtModel(dt=dt)
    assert model.dt.tzinfo.tzname(model.dt) == 'UTC'


@pytest.mark.parametrize(
    'd',
    [
        pendulum.now().date().isoformat(),
        pendulum.now().to_w3c_string(),
        pendulum.now().to_iso8601_string(),
    ],
)
def test_pendulum_date_from_serialized(d):
    """Verifies that building an instance from serialized, well-formed strings decode properly."""
    date_actual = pendulum.parse(d).date()
    model = DateModel(d=d)
    assert model.d == date_actual
    assert type(model.d) is Date
    assert isinstance(model.d, pendulum.Date)


@pytest.mark.parametrize(
    'delta_t_str',
    [
        'P3.14D',
        'PT404H',
        'P1DT25H',
        'P2W',
        'P10Y10M10D',
    ],
)
def test_pendulum_duration_from_serialized(delta_t_str):
    """Verifies that building an instance from serialized, well-formed strings decode properly."""
    true_delta_t = pendulum.parse(delta_t_str)
    model = DurationModel(delta_t=delta_t_str)
    assert model.delta_t == true_delta_t
    assert type(model.delta_t) is Duration
    assert isinstance(model.delta_t, pendulum.Duration)


def get_invalid_dt_common():
    return [
        None,
        'malformed',
        'P10Y10M10D',
        float('inf'),
        float('-inf'),
        'inf',
        '-inf',
        'INF',
        '-INF',
        '+inf',
        'Infinity',
        '+Infinity',
        '-Infinity',
        'INFINITY',
        '+INFINITY',
        '-INFINITY',
        'infinity',
        '+infinity',
        '-infinity',
        float('nan'),
        'nan',
        'NaN',
        'NAN',
        '+nan',
        '-nan',
    ]


dt_strict = get_invalid_dt_common()
dt_strict.append(pendulum.now().to_iso8601_string()[:5])


@pytest.mark.parametrize(
    'dt',
    dt_strict,
)
def test_pendulum_dt_malformed(dt):
    """Verifies that the instance fails to validate if malformed dt is passed."""
    with pytest.raises(ValidationError):
        DtModel(dt=dt)


@pytest.mark.parametrize('dt', get_invalid_dt_common())
def test_pendulum_dt_non_strict_malformed(dt):
    """Verifies that the instance fails to validate if malformed dt are passed."""
    with pytest.raises(ValidationError):
        DtModelNotStrict(dt=dt)


@pytest.mark.parametrize(
    'instance',
    [
        pendulum.now().time(),
        datetime.now().time(),
        datetime.now(UTC).time(),
    ],
)
def test_existing_time_instance(instance):
    """Verifies that constructing a model with an existing pendulum time doesn't throw."""
    model = TimeModel(t=instance)
    if isinstance(instance, pendulum.Time):
        assert model.t == instance
        t = model.t
    else:
        assert model.t.replace(tzinfo=UTC) == pendulum.instance(instance)  # pendulum defaults to UTC
        t = model.t

    assert t.hour == instance.hour
    assert t.minute == instance.minute
    assert t.second == instance.second
    assert t.microsecond == instance.microsecond
    assert isinstance(t, pendulum.Time)
    assert type(t) is Time
    if t.tzinfo != instance.tzinfo:
        date = Date(2022, 1, 22)
        assert t.tzinfo.utcoffset(DateTime.combine(date, t)) == instance.tzinfo.utcoffset(DateTime.combine(date, instance))


@pytest.mark.parametrize(
    'dt',
    [
        "17:53:12.266369",
        "17:53:46",
    ],
)
def test_pendulum_time_from_serialized(dt):
    """Verifies that building an instance from serialized, well-formed strings decode properly."""
    dt_actual = pendulum.parse(dt, exact=True)
    model = TimeModel(t=dt)
    assert model.t == dt_actual.replace(tzinfo=UTC)
    assert type(model.t) is Time
    assert isinstance(model.t, pendulum.Time)


def get_invalid_dt_common():
    return [
        None,
        'malformed',
        'P10Y10M10D',
        float('inf'),
        float('-inf'),
        'inf',
        '-inf',
        'INF',
        '-INF',
        '+inf',
        'Infinity',
        '+Infinity',
        '-Infinity',
        'INFINITY',
        '+INFINITY',
        '-INFINITY',
        'infinity',
        '+infinity',
        '-infinity',
        float('nan'),
        'nan',
        'NaN',
        'NAN',
        '+nan',
        '-nan',
    ]


dt_strict = get_invalid_dt_common()
dt_strict.append(pendulum.now().to_iso8601_string()[:5])


@pytest.mark.parametrize(
    'dt',
    dt_strict,
)
def test_pendulum_time_malformed(dt):
    """Verifies that the instance fails to validate if malformed time is passed."""
    with pytest.raises(ValidationError):
        TimeModel(t=dt)


@pytest.mark.parametrize(
    'invalid_value',
    [None, 'malformed', pendulum.today().to_iso8601_string()[:5], 'P10Y10M10D'],
)
def test_pendulum_date_malformed(invalid_value):
    """Verifies that the instance fails to validate if malformed date are passed."""
    with pytest.raises(ValidationError):
        DateModel(d=invalid_value)


@pytest.mark.parametrize(
    'delta_t',
    [
        None,
        'malformed',
        pendulum.today().to_iso8601_string()[:5],
        42,
        '12m',
        '2021-01-01T12:00:00',
    ],
)
def test_pendulum_duration_malformed(delta_t):
    """Verifies that the instance fails to validate if malformed durations are passed."""
    with pytest.raises(ValidationError):
        DurationModel(delta_t=delta_t)


@pytest.mark.parametrize(
    'input_type, value, is_instance',
    [
        (Date, '2021-01-01', pendulum.Date),
        (Date, date(2021, 1, 1), pendulum.Date),
        (Date, pendulum.date(2021, 1, 1), pendulum.Date),
        (Time, '12:00:00', pendulum.Time),
        (Time, time(12, 0, 0), pendulum.Time),
        (Time, pendulum.time(12, 0, 0), pendulum.Time),
        (DateTime, '2021-01-01T12:00:00', pendulum.DateTime),
        (DateTime, datetime(2021, 1, 1, 12, 0, 0), pendulum.DateTime),
        (DateTime, pendulum.datetime(2021, 1, 1, 12, 0, 0), pendulum.DateTime),
        (Duration, 'P1DT25H', pendulum.Duration),
        (Duration, timedelta(days=1, hours=25), pendulum.Duration),
        (Duration, pendulum.duration(days=1, hours=25), pendulum.Duration),
    ],
)
def test_date_type_adapter(input_type: type, value, is_instance: type):
    validated = TypeAdapter(input_type).validate_python(value)
    assert type(validated) is input_type
    assert isinstance(validated, input_type)
    assert isinstance(validated, is_instance)


def test_pendulum_duration_months_are_preserved():
    m = DurationModel(delta_t=pendulum.Duration(months=1))

    assert m.delta_t.months == 1
