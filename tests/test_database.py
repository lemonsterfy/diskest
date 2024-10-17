import pytest
from diskest.utils.database import ResultDatabase


@pytest.fixture
def result_database(tmp_path):
    db_path = tmp_path / "test.db"
    return ResultDatabase(str(db_path))


def test_save_and_get_result(result_database):
    test_result = {"test": "data"}
    result_id = result_database.save_result(test_result)
    assert result_id is not None
    retrieved_result = result_database.get_latest_result()
    assert retrieved_result == test_result


def test_get_all_results(result_database):
    test_results = [{"test": "data1"}, {"test": "data2"}]
    for result in test_results:
        result_database.save_result(result)
    all_results = result_database.get_all_results()
    assert len(all_results) == 2
    assert all(result[1] in test_results for result in all_results)
