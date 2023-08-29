import pytest
from hardsync.utils import dump, wrap_assertion_error


def test_dump():
    output = dump().lower()
    assert 'hash' in output
    assert 'version' in output
    assert 'os' in output
    assert 'python' in output


def test_wrap_assertion_error(tmp_path):
    full_path = tmp_path / 'contract.py'
    with open(full_path, 'w') as contract:
        contract.write('class MyExchange:\n    pass')

    with pytest.raises(AssertionError) as err:
        with wrap_assertion_error(contract_path=full_path):
            raise AssertionError()

    message = str(err.value).lower()
    assert 'os' in message
    assert 'python' in message
    assert 'https://github.com/edmundsj/hardsync/issues/new' in message
    assert 'traceback' in message
    assert 'dump' in message

