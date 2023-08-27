from serial.tools import list_ports
import serial
import logging
from typing import Optional, Type, TypeVar
from datetime import timedelta
import time

from hardsync.channels import DeviceNotFoundError
from hardsync.interfaces import Encoding, Channel
from hardsync.defaults import Ping
from typing import List, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DEFAULT_TIMEOUT = timedelta(seconds=2)


def pyserial_discover(
        encoding: Type[Encoding],
        channel: Channel,
        preferred_serial: Optional[str] = None,
        timeout: timedelta = DEFAULT_TIMEOUT,
) -> List[str]:

    available_ports = list_ports.comports()
    target_ports = _filter_ports_by_serial(available_ports, preferred_serial)

    discovered_serials = []
    for port in target_ports:
        discovered_serial = _attempt_connection(port=port, channel=channel, encoding=encoding, timeout=timeout.seconds)
        if discovered_serial:
            discovered_serials.append(discovered_serial)

    if not discovered_serial and available_ports:
        logger.error('Unable to find compatible device. Ensure you have uploaded hardsync firmware, and try again')
    elif not available_ports:
        logger.error('Unable to find any connected devices. Are you sure your device is on and plugged in?')

    return discovered_serials


Port = TypeVar('Port')


def _filter_ports_by_serial(available_ports: List[Port], preferred_serial: Optional[str]) -> List[Port]:
    if preferred_serial:
        preferred_ports = [port for port in available_ports if port.serial_number == preferred_serial]
        nonpreferred_ports = [port for port in available_ports if port.serial_number != preferred_serial]
        return preferred_ports + nonpreferred_ports

    return available_ports


def _attempt_connection(port: Port, channel: Channel, encoding: Type[Encoding], timeout: float) -> Optional[str]:
    start_time = time.monotonic()
    end_time = start_time + timeout
    current_time = time.monotonic()

    while current_time < end_time:
        ser = serial.Serial(port=port.device, baudrate=channel.baud_rate)
        logger.info(f'Trying candidate device {port}...')
        contents = encoding.encode(exchange=Ping, values={}, is_request=True)
        ser.write(contents)
        response = ser.read_until(encoding.exchange_terminator.encode('ascii'))
        decoded_response = encoding.decode(exchange=Ping, contents=response)

        if decoded_response.name == 'PingResponse':
            logger.info('Success! found device.')
            return port.serial_number
        else:
            logger.info('Incompatible device.')

        current_time = time.monotonic()

    return None

