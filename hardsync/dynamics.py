from types import ModuleType
from typing import Type, List, Any, Set, get_args
from hardsync.interfaces import Exchange, Encoding, TypeMapping, ContractError, Channel, Contract
from hardsync.encodings import AsciiEncoding
from hardsync.defaults import DEFAULT_TYPE_MAPPING, DEFAULT_ENCODING, DEFAULT_CHANNEL
from hardsync.types import BaudRateT
from dataclasses import dataclass, fields, is_dataclass
from hardsync.utils import flatten
import inspect


SPECIAL_CLASS_NAMES = ['Encoding', 'Channel', 'TypeMapping']


def apply_defaults(module: ModuleType):
    apply_encoding(module=module, encoding=DEFAULT_ENCODING)
    apply_exchange_inheritance(module)
    apply_type_mapping_inheritance(module=module, type_mapping=DEFAULT_TYPE_MAPPING)
    apply_channel(module=module, channel=DEFAULT_CHANNEL)

    transform_to_dataclasses(module)
    validate(contract=module)


def apply_encoding(module: ModuleType, encoding: Type[Encoding]):
    if hasattr(module, 'Encoding'):
        if inspect.isabstract(module.Encoding):
            module.Encoding = encoding
    else:
        module.Encoding = encoding


def apply_channel(module: ModuleType, channel: Type[Channel]):
    if not hasattr(module, 'Channel'):
        module.Channel = channel

    if not issubclass(module.Channel, Channel):
        new_channel = type('Channel', (Channel,), dict(module.Channel.__dict__))
        setattr(module, 'Channel', new_channel)


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
            new_type_mapping = type('TypeMapping', (TypeMapping,), dict(module.TypeMapping.__dict__))
            setattr(module, 'TypeMapping', new_type_mapping)


def get_exchanges_permissive(module: ModuleType):
    possible_exchanges = [mem[1] for mem in inspect.getmembers(module, predicate=inspect.isclass)]
    no_special_classes = [ex for ex in possible_exchanges if ex.__name__ not in SPECIAL_CLASS_NAMES]
    return no_special_classes


def transform_to_dataclasses(module: ModuleType):
    exchanges = get_exchanges_permissive(module)
    for ex in exchanges:
        setattr(ex, 'Request', dataclass(ex.Request))
        setattr(ex, 'Response', dataclass(ex.Response))


def get_exchanges(module: Contract):
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
    required_classes = ['Encoding', 'TypeMapping', 'Channel']
    for cls in required_classes:
        if not hasattr(contract, cls):
            raise ContractError(f"Contract missing special class: {cls}")

    exchanges = get_exchanges_permissive(module=contract)
    for ex in exchanges:
        validate_exchange(ex)

    all_input_types = set(flatten([input_types(ex) for ex in exchanges]))
    validate_type_mapping(required_types=all_input_types, type_mapping=contract.TypeMapping)

    validate_encoding(encoding=contract.Encoding)


def validate_type_mapping(required_types: Set[Any], type_mapping: Type[TypeMapping]):
    available_types = set(type_mapping.keys())
    missing_types = set()
    for t in required_types:
        if t not in available_types:
            missing_types.add(t)
    if missing_types:
        raise ContractError(f"Type mapping is missing {missing_types}")


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
        raise ContractError(messages)


def validate_encoding(encoding: Type[Encoding]):
    if not issubclass(encoding, AsciiEncoding):
        raise AssertionError("Only ASCII encoding is currently supported.")


def validate_channel(channel: Type[Channel]):
    if not hasattr(channel, 'baud_rate'):
        raise ContractError("Channel class missing baud_rate variable.")
    allowed_values = get_args(BaudRateT)
    if channel.baud_rate not in allowed_values:
        raise ContractError(f"Using improper baud rate. Available values are {allowed_values}")