import pytest

from tests.utils import TestDBHelper


@pytest.fixture(scope="session")
def app_settings():
    from src.infrastructure.di.providers.config import get_settings

    return get_settings()


@pytest.fixture(scope='session')
def create_test_db_engine(app_settings):
    del app_settings
    _test_db_name = TestDBHelper.create_test_db_name(postfix="hajj_umrah_test")

    # создать engine

    # создать конфиг алембик

    # применить миграции алембик




@pytest.fixture(scope='session')
def test_db_session(create_test_db_engine):
    pass
