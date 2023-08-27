from types import ModuleType
from typing import Type, List, Any, Set
from hardsync.interfaces import Exchange, Encoding, TypeMapping
from hardsync.defaults import DEFAULT_TYPE_MAPPING, DEFAULT_ENCODING
from dataclasses import dataclass, fields, is_dataclass
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
def apply_type_mapping_inheritance(module: ModuleType, type_mapping: Type[TypeMapping]):
    if not hasattr(module, 'TypeMapping'):
        module.TypeMapping = type_mapping
    else:
        if not issubclass(module.TypeMapping, TypeMapping):
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


def input_types(exchange: Type[Exchange]) -> List[Any]:
    request_types = [f.type for f in fields(exchange.Request)]
    response_type = [f.type for f in fields(exchange.Response)]
    return request_types + response_type


def validate(contract: ModuleType):
    exchanges = get_exchanges_permissive(module=contract)
    for ex in exchanges:
        validate_exchange(ex)
    all_input_types = set(flatten([input_types(ex) for ex in exchanges]))
    validate_type_mapping(required_types=all_input_types, type_mapping=contract.TypeMapping)


def validate_type_mapping(required_types: Set[Any], type_mapping: Type[TypeMapping]):
    available_types = set(type_mapping.keys())
    missing_types = set()
    for t in required_types:
        if t not in available_types:
            missing_types.add(t)
    if missing_types:
        raise AssertionError(f"Type mapping is missing {missing_types}")


def validate_exchange(exchange: Type):
    messages = []
    if not issubclass(exchange, Exchange):
        messages.append(f"exchange {exchange} is not a subclass of Exchange class")
    if not hasattr(exchange, 'Request'):
        messages.append(f"exchange {exchange} must have a Request specified")
    else:
        if not is_dataclass(exchange.Request):
            messages.append(f"exchange.Request must be a dataclass")
    if not hasattr(exchange, 'Response'):
        messages.append(f"exchange {exchange} must have a response specified")
    else:
        if not is_dataclass(exchange.Response):
            messages.append(f"exchange.Response must be a dataclass")

    if messages:
        raise AssertionError(messages)
