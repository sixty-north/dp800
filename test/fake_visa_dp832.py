from test.patterns import compile_pattern


class FakeVisaDP832:

    def __init__(self):
        self._channel_states = [None, 'OFF', 'OFF', 'OFF']
        self._channel_voltage_setpoints = [None, 0.0, 0.0, 0.0]
        self._channel_current_setpoints = [None, 0.0, 0.0, 0.0]

    def write(self, command):
        self.query(command)

    def query(self, command):
        for regex, function in ACTIONS:
            m = regex.match(command)
            if m:
                return function(self, *m.groups())
        raise RuntimeError("No match found for command {!r}".format(command))

    def _id_query(self):
        return 'RIGOL TECHNOLOGIES,DP832,DP8A000001,00.01.01\n'

    def _output_state_command(self, channel, state):
        channel_index = int(channel)
        self._channel_states[channel_index] = state

    def _output_state_query(self, channel):
        channel_index = int(channel)
        return self._channel_states[channel_index] + '\n'

    def _voltage_setpoint_command(self, channel, voltage):
        channel_index = int(channel)
        self._channel_voltage_setpoints[channel_index] = float(voltage)

    def _voltage_setpoint_query(self, channel):
        channel_index = int(channel)
        return str(self._channel_voltage_setpoints[channel_index]) + '\n'

    def _current_setpoint_command(self, channel, current):
        channel_index = int(channel)
        self._channel_current_setpoints[channel_index] = float(current)

    def _current_setpoint_query(self, channel):
        channel_index = int(channel)
        return str(self._channel_current_setpoints[channel_index]) + '\n'

IDN_QUERY                = compile_pattern(r'\*IDN\?')
OUTPUT_STATE_COMMAND     = compile_pattern(r':%OUTPut%(?::%STATe%) CH(\d+),(ON|OFF)')
OUTPUT_STATE_QUERY       = compile_pattern(r':%OUTPut%(?::%STATe%)\? CH(\d+)')
VOLTAGE_SETPOINT_COMMAND = compile_pattern(r':%SOURce%(\d+):%VOLTage%:%IMMEDIATE% (\d+\.\d+)')
VOLTAGE_SETPOINT_QUERY   = compile_pattern(r':%SOURce%(\d+):%VOLTage%:%IMMEDIATE%?')
CURRENT_SETPOINT_COMMAND = compile_pattern(r':%SOURce%(\d+):%CURRent%:%IMMEDIATE% (\d+\.\d+)')
CURRENT_SETPOINT_QUERY   = compile_pattern(r':%SOURce%(\d+):%CURRent%:%IMMEDIATE%?')

ACTIONS = (
    (IDN_QUERY, FakeVisaDP832._id_query),
    (OUTPUT_STATE_COMMAND, FakeVisaDP832._output_state_command),
    (OUTPUT_STATE_QUERY, FakeVisaDP832._output_state_query),
    (VOLTAGE_SETPOINT_COMMAND, FakeVisaDP832._voltage_setpoint_command),
    (VOLTAGE_SETPOINT_QUERY, FakeVisaDP832._voltage_setpoint_query),
    (CURRENT_SETPOINT_COMMAND, FakeVisaDP832._current_setpoint_command),
    (CURRENT_SETPOINT_QUERY, FakeVisaDP832._current_setpoint_query),
)
