from tests.utils import TestDBHelper


def test_create_test_db_name():
    res = TestDBHelper.create_test_db_name(postfix="my_db")

    assert "my_db" in res
