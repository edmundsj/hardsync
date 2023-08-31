import pytest
from hardsync.channels import SocketChannel


def test_read_until_single_byte(self):
    channel = SocketChannel(port=12345)
    stop_char = b'\n'
    with channel.open():
        channel.write(b'Hello\nWorld\n')
        desired = b'Hello\n'

        actual = self.reader.read_until(stop_char)
        assert actual == desired