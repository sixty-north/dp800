from collections import OrderedDict
from enum import Enum
from itertools import count


class DP832:

    def __init__(self, instrument):
        identification = instrument.query('*IDN?')
        if 'DP832' not in identification:
            raise ValueError("Instrument identified by {!r} is not a Rigol DP832".format(identification))
        self._inst = instrument

        self._channels = OrderedDict([
            (1, Channel(self, 1, over_voltage_min=0.001, over_voltage_max=33.000, over_current_min=0.001, over_current_max=3.300)),
            (2, Channel(self, 2, over_voltage_min=0.001, over_voltage_max=33.000, over_current_min=0.001, over_current_max=3.300)),
            (3, Channel(self, 3, over_voltage_min=0.001, over_voltage_max=5.500,  over_current_min=0.001, over_current_max=3.300))])

    @property
    def channel_ids(self):
        return list(self._channels.keys())

    def channel(self, channel_id):
        try:
            return self._channels[channel_id]
        except KeyError:
            channel_ids = self.channel_ids
            raise ValueError("Invalid channel id {} not in range {}-{}".format(
                channel_id, channel_ids[0], channel_ids[-1]))

    def write(self, command, *args, **kwargs):
        return self._inst.write(command.format(*args, **kwargs))

    def query(self, command, *args, **kwargs):
        return self._inst.query(command.format(*args, **kwargs))


class ChannelMode(Enum):

    @staticmethod
    def from_response(response):
        stripped_response = response.strip()
        try:
            return CHANNEL_MODE_RESPONSES[stripped_response]
        except KeyError:
            raise ValueError("Response {!r} not recognized as a channel mode from {}".format(
                stripped_response, ', '.join(CHANNEL_MODE_RESPONSES.keys())))

    unregulated = 0
    constant_voltage = 1
    constant_current = 2


CHANNEL_MODE_RESPONSES = {
    'CC': ChannelMode.constant_current,
    'CV': ChannelMode.constant_voltage,
    'UR': ChannelMode.unregulated
}

BOOLEAN_RESPONSES = ('OFF', 'ON')


def from_boolean_response(response):
    stripped_response = response.strip()
    try:
        return bool(BOOLEAN_RESPONSES.index(stripped_response))
    except ValueError as e:
        raise ValueError("Unexpected boolean response {!r} not one of {}".format(
            stripped_response, ', '.join(BOOLEAN_RESPONSES))) from e


def to_boolean(value):
    try:
        return BOOLEAN_RESPONSES[value]
    except IndexError as e:
        raise ValueError("Invalid boolean value {!r}".format(value)) from e


class Channel:

    def __init__(self, device, channel_id, over_voltage_min, over_voltage_max, over_current_min, over_current_max):
        self._device = device
        self._channel_id = channel_id
        self._over_voltage_min = over_voltage_min
        self._over_voltage_max = over_voltage_max
        self._over_current_min = over_current_min
        self._over_current_max = over_current_max

    @property
    def device(self):
        return self._device

    @property
    def channel_id(self):
        return self._channel_id

    @property
    def over_voltage_min(self):
        return self._over_voltage_min

    @property
    def over_voltage_max(self):
        return self._over_voltage_max

    @property
    def over_current_min(self):
        return self._over_current_min

    @property
    def over_current_max(self):
        return self._over_current_max

    def _write(self, command, *args, **kwargs):
        return self._device.write(command, *args, **kwargs)

    def _query(self, command, *args, **kwargs):
        return self._device.query(command, *args, **kwargs)

    @property
    def is_on(self):
        response = self._query('OUTPUT:STATE? CH{}', self._channel_id)
        try:
            return from_boolean_response(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response: {!r}") from e

    @is_on.setter
    def is_on(self, value):
        state = to_boolean(value)
        self._write('OUTPUT:STATE CH{},{}', self._channel_id, state)

    def on(self):
        self.is_on = True

    def off(self):
        self.is_on = False

    @property
    def mode(self):
        response = self._query('OUTPUT:MODE? CH{}', self._channel_id)
        try:
            return ChannelMode.from_response(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response: {!r}".format(response)) from e

    @property
    def voltage_setpoint(self):
        response = self._query('SOURCE{}:VOLTAGE:IMMEDIATE?', self._channel_id)
        try:
            return float(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response: {!r}".format(response)) from e

    @voltage_setpoint.setter
    def voltage_setpoint(self, value):
        if not (self.over_voltage_min <= value <= self.over_voltage_max):
            raise ValueError("Voltage {} V outside range {} V to {} V".format(
                value, self.over_voltage_min, self.over_voltage_max))
        self._write(':SOURCE{}:VOLTAGE:IMMEDIATE {}', self._channel_id, value)

    @property
    def current_setpoint(self):
        response = self._query('SOURCE{}:CURRENT:IMMEDIATE?', self._channel_id)
        try:
            return float(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response: {!r}".format(response)) from e

    @current_setpoint.setter
    def current_setpoint(self, value):
        if not (self.over_current_min <= value <= self.over_current_max):
            raise ValueError("Current {} A outside range {} A to {} A".format(
                value, self.over_voltage_min, self.over_voltage_max))
        self._write(':SOURCE{}:CURRENT:IMMEDIATE {}', self._channel_id, value)

if __name__ == '__main__':
    import visa
    rm = visa.ResourceManager('@py')
    instrument = rm.get_instrument('TCPIP0::10.0.0.145::INSTR')
    dp832 = DP832(instrument)
    print(dp832.channel_ids)
    for channel_id in dp832.channel_ids:
        channel = dp832.channel(channel_id)
        print("is_on    = ", channel.is_on)
        print("mode  = ", channel.mode)
        channel.on()
        print("is_on    = ", channel.is_on)
        channel.voltage_setpoint = channel_id
        print("voltage_setpoint =", channel.voltage_setpoint)
