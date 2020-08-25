from dataclasses import is_dataclass

import pytest

from link.use_cases.refresh import RefreshResponseModel


def test_if_dataclass():
    assert is_dataclass(RefreshResponseModel)


@pytest.fixture
def refreshed():
    return ["identifiers" + str(i) for i in range(10)]


@pytest.fixture
def model(refreshed):
    return RefreshResponseModel(refreshed=refreshed)


def test_n_refreshed_property(model, refreshed):
    assert model.n_refreshed == len(refreshed)