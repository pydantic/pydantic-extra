import pandas as pd
import pytest
from pydantic import BaseModel

from pydantic_extra_types.pandas_types import Series


@pytest.fixture(scope='session', name='SeriesModel')
def series_model_fixture():
    class SeriesModel(BaseModel):
        data: Series

    return SeriesModel


@pytest.mark.parametrize(
    'data, expected',
    [
        ([1, 2, 3], [1, 2, 3]),
        ([], []),
        ([10, 20, 30, 40], [10, 20, 30, 40]),
    ],
)
def test_series_creation(data, expected):
    if pd.__version__ <= '1.5.3' and data == []:
        s = Series([1])
        expected = [1]
    else:
        s = Series(data)
    assert isinstance(s, Series)
    assert isinstance(s, pd.Series)
    assert s.tolist() == expected


def test_series_repr():
    data = [1, 2, 3]
    s = Series(data)
    assert repr(s) == repr(pd.Series(data))


def test_series_attribute_access():
    data = [1, 2, 3]
    s = Series(data)
    assert s.sum() == pd.Series(data).sum()


def test_series_equality():
    data = [1, 2, 3]
    s1 = Series(data)
    s2 = Series(data)
    assert s1.equals(other=s2)
    assert s2.equals(pd.Series(data))


def test_series_addition():
    data1 = [1, 2, 3]
    data2 = [4, 5, 6]
    s1 = Series(data1)
    s2 = Series(data2)
    s3 = s1 + s2
    assert isinstance(s3, pd.Series)
    assert s3.tolist() == [5, 7, 9]


@pytest.mark.parametrize(
    'data, other, expected',
    [
        ([1, 2, 3], [4, 5, 6], [5, 7, 9]),
        ([10, 20, 30], (1, 2, 3), [11, 22, 33]),
        ([5, 10, 15], pd.Series([1, 2, 3]), [6, 12, 18]),
    ],
)
def test_series_addition_with_types(data, other, expected):
    s = Series(data)
    result = s + other
    assert isinstance(result, pd.Series)
    assert result.tolist() == expected


@pytest.mark.parametrize(
    'data, other',
    [
        ([1, 2, 3], 'invalid'),  # Invalid type for addition
        ([1, 2, 3], {'a': 1, 'b': 2}),  # Invalid type for addition
    ],
)
def test_series_addition_invalid_type_error(data, other) -> None:
    s = Series(data)
    with pytest.raises(TypeError):
        s + other


@pytest.mark.parametrize(
    'data, other',
    [
        ([1, 2, 3], []),
    ],
)
def test_series_addition_invalid_value_error(data, other) -> None:
    s = Series(data)
    with pytest.raises(ValueError):
        s + other


def test_valid_series_model(SeriesModel) -> None:
    model = SeriesModel(data=[1, 2, 4])
    assert isinstance(model.data, pd.Series)
    assert model.data.equals(pd.Series([1, 2, 4]))


def test_valid_series_model_with_pd_series(SeriesModel) -> None:
    s = pd.Series([1, 2, 4])
    model = SeriesModel(data=s)
    assert isinstance(model.data, pd.Series)
    assert model.data.equals(s)
