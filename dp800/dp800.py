from collections import OrderedDict
from enum import Enum


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
        self._id = channel_id
        self._voltage = Quantity(self, 'voltage', 'V', over_voltage_min, over_voltage_max)
        self._current = Quantity(self, 'current', 'A', over_current_min, over_current_max)

    @property
    def device(self):
        return self._device

    @property
    def id(self):
        return self._id

    def _write(self, command, *args, **kwargs):
        return self._device.write(command, *args, **kwargs)

    def _query(self, command, *args, **kwargs):
        return self._device.query(command, *args, **kwargs)

    @property
    def is_on(self):
        response = self._query(':OUTPUT:STATE? CH{}', self._id)
        try:
            return from_boolean_response(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response: {!r}") from e

    @is_on.setter
    def is_on(self, value):
        state = to_boolean(value)
        self._write(':OUTPUT:STATE CH{},{}', self._id, state)

    def on(self):
        self.is_on = True

    def off(self):
        self.is_on = False

    @property
    def voltage(self):
        return self._voltage

    @property
    def current(self):
        return self._current

    @property
    def mode(self):
        response = self._query('OUTPUT:MODE? CH{}', self._id)
        try:
            return ChannelMode.from_response(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response: {!r}".format(response)) from e


class Quantity:

    def __init__(self, channel, name, unit, over_min, over_max):
        self._channel = channel
        self._name = name
        self._unit = unit
        self._over_min = over_min
        self._over_max = over_max

    @property
    def setpoint(self):
        response = self._channel._query('SOURCE{}:{}:IMMEDIATE?', self._channel._id, self._name.upper())
        try:
            return float(response)
        except ValueError as e:
            raise RuntimeError("Unexpected response to {} query on channel {} : {!r}".format(self._name.lower(), self._channel._id, response)) from e

    @setpoint.setter
    def setpoint(self, value):
        if not (self._over_min <= value <= self._over_max):
            raise ValueError("{} {} A outside range {} A to {} A".format(
                self._name.title(), value, self._over_min, self._over_max))
        self._channel._write(':SOURCE{}:{}:IMMEDIATE {}', self._channel._id, self._name.upper(), value)

    @property
    def over_min(self):
        return self._over_min

    @property
    def over_max(self):
        return self._over_max


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
        channel.voltage.setpoint = channel_id
        print("voltage.setpoint =", channel.voltage.setpoint)