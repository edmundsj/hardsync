from types import ModuleType
from typing import Type, List, Any
from hardsync.interfaces import Exchange, Encoding, TypeMapping
from hardsync.defaults import DEFAULT_TYPE_MAPPING, DEFAULT_ENCODING
from dataclasses import dataclass, fields
from hardsync.utils import flatten
import inspect


def apply_defaults(module: ModuleType):
    apply_encoding(module=module, encoding=DEFAULT_ENCODING)
    apply_exchange_inheritance(module)
    apply_type_mapping_inheritance(module=module, type_mapping=DEFAULT_TYPE_MAPPING)

    transform_to_dataclasses(module)


def apply_encoding(module: ModuleType, encoding: Type[Encoding]):
    if hasattr(module, 'Encoding'):
        if inspect.isabstract(module.Encoding):
            module.Encoding = encoding
    else:
        module.Encoding = encoding


def apply_exchange_inheritance(module: ModuleType):
    old_exchagnes = get_exchanges_permissive(module)
    for exchange in old_exchagnes:
        new_exchange = type(exchange.__name__, (Exchange,), dict(exchange.__dict__))
        setattr(module, exchange.__name__, new_exchange)


# TODO: THIS IS A BUG. FIX
def apply_type_mapping_inheritance(module: ModuleType, type_mapping: TypeMapping):
    if not hasattr(module, 'TypeMapping'):
        module.TypeMapping = type_mapping
    else:
        if not isinstance(module.TypeMapping, TypeMapping):
            new_type_mapping = type('TypeMapping', (TypeMapping,), dict(module.TypeMapping.__class__.__dict__))
            setattr(module, 'TypeMapping', new_type_mapping)


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


def input_types(exchange: Exchange) -> List[Any]:
    request_types = [f.type for f in fields(exchange.Request)]
    response_type = [f.type for f in fields(exchange.Response)]
    return request_types + response_type


def validate_type_mapping(module: ModuleType, type_mapping: TypeMapping):
    exchanges = get_exchanges(module=module)
    required_types = set(flatten(
        [input_types(ex) for ex in exchanges]
    ))
    available_types = type_mapping.keys()
    for t in required_types:
        assert t in available_types


def to_type_mapping_instance(type_mapping: Type) -> TypeMapping:
    raise NotImplementedError()