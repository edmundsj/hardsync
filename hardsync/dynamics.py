from types import ModuleType
from hardsync.interfaces import Exchange
from hardsync.defaults import DEFAULT_TYPE_MAPPING
from hardsync.encodings import AsciiEncoding
from dataclasses import dataclass
import abc
import inspect


def apply_defaults(module: ModuleType):
    if not hasattr(module, 'TypeMapping'):
        module.TypeMapping = DEFAULT_TYPE_MAPPING

    old_exchagnes = get_exchanges_permissive(module)
    for exchange in old_exchagnes:
        new_exchange = type(exchange.__name__, (Exchange,), dict(exchange.__dict__))
        if inspect.isabstract(new_exchange.Encoding):
            new_exchange.Encoding = AsciiEncoding
        setattr(module, exchange.__name__, new_exchange)

    transform_to_dataclasses(module)


def get_exchanges_permissive(module: ModuleType):
    possible_exchanges = inspect.getmembers(module, predicate=inspect.isclass)
    exchanges = []
    for poss in possible_exchanges:
        if hasattr(poss[1], 'Request'):
            exchanges.append(poss[1])
    return exchanges


def transform_to_dataclasses(module: ModuleType):
    exchanges = get_exchanges_permissive(module)
    for ex in exchanges:
        setattr(ex, 'Request', dataclass(ex.Request))
        setattr(ex, 'Response', dataclass(ex.Response))


def get_exchanges(module: ModuleType):
    exchanges = []
    for item in inspect.getmembers(module, predicate=inspect.isclass):
        if issubclass(item[1], Exchange):
            exchanges.append(item[1])
    return exchanges

