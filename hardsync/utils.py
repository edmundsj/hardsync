import contextlib
import hardsync
import os
import platform
import itertools
from typing import Sequence, List, TypeVar
import traceback
from pathlib import Path


T = TypeVar('T')


def flatten(nested_list: Sequence[Sequence[T]]) -> List[T]:
    return list(itertools.chain.from_iterable(nested_list))


def dump() -> str:
    snippets = [
        f'hardsync_version: {hardsync.__version__}',
        f'hardsync_hash: {hardsync.__hash__}',
        f'os_name: {os.name}',
        f'platform: {platform.system()}',
        f'platform_version: {platform.uname()[3]}',
        f'python_version: {platform.python_version()}',
    ]
    dump_string = "\n".join(snippets)
    return dump_string


@contextlib.contextmanager
def wrap_assertion_error(contract_path: Path):
    try:
        yield
    except AssertionError as e:
        dump_info = dump()
        with open(contract_path, 'r') as contract:
            contract_contents = contract.read()

        tb = traceback.format_exc()
        header = (
            "Congratulations! You managed to find an error I left behind. This means that you did"
            "something I didn't expect or are looking for a feature I haven't yet implemented. Please submit a bug "
            "report to the following URL: https://github.com/edmundsj/hardsync/issues/new?assignees=&labels=bug"
            "&projects=&template=bug_report.md&title=AssertionError%20bug%20report and copy-paste the following:\n"
        )
        full_message_snippets = [
            (header,),
            ('Contract:', contract_contents),
            ('Traceback:', tb),
            ('Output of hardsync dump:',dump_info),
        ]
        strings = ['\n'.join(field) for field in full_message_snippets]
        full_message = '\n'.join(strings)

        raise AssertionError(f"{full_message}") from None
    except Exception as e:
        # Pass through all other errors
        raise e
