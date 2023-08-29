import inspect

import pytest

from hardsync.dynamics import (
    get_exchanges_permissive,
    transform_to_dataclasses,
    apply_defaults,
    get_exchanges,
    input_types,
    validate_type_mapping,
    validate,
    SPECIAL_CLASS_NAMES,
)
from hardsync.interfaces import (
    Exchange,
    TypeMapping as TypeMappingI,
    ContractError,
)
from hardsync.encodings import AsciiEncoding
from types import ModuleType
from typing import List
from dataclasses import is_dataclass, fields, field, dataclass


def test_get_exchanges_permissive():
    module = ModuleType('hi')

    class MeasureVoltage:
        class Request:
            pass

    module.MeasureVoltage = MeasureVoltage
    exchanges = get_exchanges_permissive(module)
    assert exchanges == [MeasureVoltage]


def test_get_exchanges_permissive_exclusions():
    module = ModuleType('hi')

    class MeasureVoltage:
        class Request:
            pass

    class TypeMapping:
        pass

    class Encoding:
        pass

    class Channel:
        pass

    module.MeasureVoltage = MeasureVoltage
    module.TypeMapping = TypeMapping
    module.Encoding = Encoding
    module.Channel = Channel
    exchanges = get_exchanges_permissive(module)
    assert len(exchanges) == 1
    assert exchanges == [MeasureVoltage]


def test_get_exchanges_permissive_none():
    module = ModuleType('hi')

    exchanges = get_exchanges_permissive(module)
    assert exchanges == []


def test_transform_to_dataclasses():
    class ExchangeClass:
        class Request:
            pass

        class Response:
            pass
    module = ModuleType('hi')
    module.ExchangeClass = ExchangeClass

    transform_to_dataclasses(module)
    assert is_dataclass(module.ExchangeClass.Request)
    assert is_dataclass(module.ExchangeClass.Response)


def test_apply_defaults_class_properties():
    class ExchangeClass:
        class Request:
            channel: int

        class Response:
            pass

    module = ModuleType('hi')
    module.ExchangeClass = ExchangeClass
    apply_defaults(module)

    assert issubclass(module.ExchangeClass, Exchange)
    assert hasattr(module, 'TypeMapping')
    assert hasattr(module, 'ExchangeClass')
    assert fields(module.ExchangeClass.Request)

    assert is_dataclass(module.ExchangeClass.Request)
    assert is_dataclass(module.ExchangeClass.Response)


def test_apply_defaults_encoding():
    class ExchangeClass:
        class Request:
            channel: int

        class Response:
            pass

    module = ModuleType('hi')
    module.ExchangeClass = ExchangeClass
    apply_defaults(module)

    assert hasattr(module, 'Encoding')
    assert not inspect.isabstract(module.Encoding)
    assert issubclass(module.Encoding, AsciiEncoding)


def test_get_exchanges():
    class MeasureVoltage(Exchange):
        @dataclass
        class Request:
            channel: int

        @dataclass
        class Response:
            voltage: float

    module = ModuleType('my_module')
    module.MeasureVoltage = MeasureVoltage
    desired = [MeasureVoltage]
    actual = get_exchanges(module)
    assert actual == desired


def test_input_types():
    class MeasureVoltage(Exchange):
        @dataclass
        class Request:
            channel: int

        @dataclass
        class Response:
            voltage: float
    desired_types = [int, float]
    actual_types = input_types(exchange=MeasureVoltage)
    assert actual_types == desired_types


def test_input_types_none():
    class MeasureVoltage(Exchange):
        @dataclass
        class Request:
            pass

        @dataclass
        class Response:
            pass

    desired_types = []
    actual_types = input_types(exchange=MeasureVoltage)
    assert actual_types == desired_types


def test_getitem_type_mapping():
    class MyMapping(TypeMappingI):
        double: float
        String: str
        int: int

    assert MyMapping[float] == 'double'
    assert MyMapping[str] == 'String'
    assert MyMapping[int] == 'int'


def test_validate_type_mapping():
    class MyMapping(TypeMappingI):
        double: float
        String: str
        int: int

    required_types = {float, str, int}
    validate_type_mapping(required_types=required_types, type_mapping=MyMapping)


def test_validate_type_mapping_missing():
    class MyMapping(TypeMappingI):
        double: float
        String: str
        int: int

    required_types = {float, str, List[str], int}
    with pytest.raises(ContractError) as e:
        validate_type_mapping(required_types=required_types, type_mapping=MyMapping)


def test_validate_happy():
    class DoSomething(Exchange):
        @dataclass
        class Request:
            pass

        @dataclass
        class Response:
            pass

    class TypeMapping(TypeMappingI):
        double: float
        String: str
        int: int

    module = ModuleType('mod')
    module.TypeMapping = TypeMapping
    module.DoSomething = DoSomething

    validate(module)


def test_validate_sad():
    class DoSomething:
        class Request:
            pass

    class TypeMapping(TypeMappingI):
        double: float
        String: str
        int: int

    module = ModuleType('mod')
    module.TypeMapping = TypeMapping
    module.DoSomething = DoSomething

    with pytest.raises(ContractError):
        validate(module)




