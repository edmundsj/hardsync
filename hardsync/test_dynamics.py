import inspect

from hardsync.dynamics import get_exchanges_permissive, transform_to_dataclasses, apply_defaults, get_exchanges
from hardsync.interfaces import Exchange, TypeMapping
from hardsync.encodings import AsciiEncoding
from types import ModuleType
from dataclasses import is_dataclass, fields, field, dataclass


def test_get_exchanges_permissive():
    module = ModuleType('hi')

    class MeasureVoltage:
        class Request:
            pass

    module.MeasureVoltage = MeasureVoltage
    exchanges = get_exchanges_permissive(module)
    assert exchanges == [MeasureVoltage]


def test_get_exchanges_permissive_none():
    module = ModuleType('hi')

    class RandomClass:
        class OtherRandomClass:
            pass

    module.RandomClass = RandomClass

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
    raise AssertionError()


def test_validate_type_mapping():
    raise AssertionError()
