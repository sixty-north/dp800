from test.patterns import compile_pattern


class FakeVisaDP832:

    def __init__(self):
        self._channel_states = [None, 'OFF', 'OFF', 'OFF']
        self._channel_voltage_setpoint_levels = [None, 0.0, 0.0, 0.0]
        self._channel_current_setpoint_levels = [None, 0.0, 0.0, 0.0]
        self._voltage_setpoint_step_default = 0.001
        self._channel_voltage_setpoint_step = [None] + [self._voltage_setpoint_step_default] * 3
        self._channel_current_setpoint_step = [None, 0.001, 0.001, 0.001]
        self._channel_voltage_protection_levels = [None, 33.0, 33.0, 5.5]
        self._channel_current_protection_levels = [None, 3.3, 3.3, 3.3]  # Check!
        self._channel_voltage_protection_states = [None, 'OFF', 'OFF', 'OFF']
        self._channel_current_protection_states = [None, 'OFF', 'OFF', 'OFF']
        self._channel_voltage_setpoint_step = [None, 0.001, 0.001, 0.001]

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

    def _voltage_setpoint_level_command(self, channel, voltage):
        channel_index = int(channel)
        self._channel_voltage_setpoint_levels[channel_index] = float(voltage)

    def _voltage_setpoint_level_query(self, channel):
        channel_index = int(channel)
        return str(self._channel_voltage_setpoint_levels[channel_index]) + '\n'

    def _current_setpoint_level_command(self, channel, current):
        channel_index = int(channel)
        self._channel_current_setpoint_levels[channel_index] = float(current)

    def _current_setpoint_level_query(self, channel):
        channel_index = int(channel)
        return str(self._channel_current_setpoint_levels[channel_index]) + '\n'

    def _voltage_setpoint_step_command(self, channel, increment):
        channel_index = int(channel)
        self._channel_voltage_setpoint_step[channel_index] = float(increment)

    def _voltage_setpoint_step_query(self, channel, default):
        channel_index = int(channel)
        is_default = default and 'DEFAULT'.startswith(default)
        increment = self._voltage_setpoint_step_default if is_default else self._channel_voltage_setpoint_step[channel_index]
        return str(increment) + '\n'

    def _voltage_protection_level_command(self, channel, voltage):
        channel_index = int(channel)
        self._channel_voltage_protection_levels[channel_index] = float(voltage)

    def _voltage_protection_level_query(self, channel, limit):
        channel_index = int(channel)
        # TODO: Handle the limit flag
        return str(self._channel_voltage_protection_levels[channel_index]) + '\n'

    def _current_protection_level_command(self, channel, current):
        channel_index = int(channel)
        self._channel_current_protection_levels[channel_index] = float(current)

    def _current_protection_level_query(self, channel, limit):
        channel_index = int(channel)
        # TODO: Handle the limit flag
        return str(self._channel_current_protection_levels[channel_index]) + '\n'

    def _voltage_protection_state_command(self, channel, state):
        channel_index = int(channel)
        self._channel_voltage_protection_states[channel_index] = state

    def _voltage_protection_state_query(self, channel):
        channel_index = int(channel)
        return self._channel_voltage_protection_states[channel_index] + '\n'

    def _current_protection_state_command(self, channel, state):
        channel_index = int(channel)
        self._channel_current_protection_states[channel_index] = state

    def _current_protection_state_query(self, channel):
        channel_index = int(channel)
        return self._channel_current_protection_states[channel_index] + '\n'

IDN_QUERY                        = compile_pattern(r'\*IDN\?')
OUTPUT_STATE_COMMAND             = compile_pattern(r':%OUTPut%(?::%STATe%)? CH(\d+),(ON|OFF)')
OUTPUT_STATE_QUERY               = compile_pattern(r':%OUTPut%(?::%STATe%)?\? CH(\d+)')
VOLTAGE_SETPOINT_LEVEL_COMMAND   = compile_pattern(r':%SOURce%(\d+):%VOLTage%(?::%LEVel%)?(?::%IMMediate%)?(?::%AMPLitude%)? (\d+\.\d+)')
VOLTAGE_SETPOINT_LEVEL_QUERY     = compile_pattern(r':%SOURce%(\d+):%VOLTage%(?::%LEVel%)?(?::%IMMediate%)?(?::%AMPLitude%)?\?')
CURRENT_SETPOINT_LEVEL_COMMAND   = compile_pattern(r':%SOURce%(\d+):%CURRent%(?::%LEVel%)?(?::%IMMediate%)?(?::%AMPLitude%)? (\d+\.\d+)')
CURRENT_SETPOINT_LEVEL_QUERY     = compile_pattern(r':%SOURce%(\d+):%CURRent%(?::%LEVel%)?(?::%IMMediate%)?(?::%AMPLitude%)?\?')
VOLTAGE_SETPOINT_STEP_COMMAND    = compile_pattern(r':%SOURce%(\d+):%VOLTage%(?::%LEVel%)?(?::%IMMediate%)?:%STEP%(?::%INCRement%)? ((?:\d+\.\d+)|%DEFault%)')
VOLTAGE_SETPOINT_STEP_QUERY      = compile_pattern(r':%SOURce%(\d+):%VOLTage%(?::%LEVel%)?(?::%IMMediate%)?:%STEP%(?::%INCRement%)?\?(?: (%DEFault%))?')
VOLTAGE_PROTECTION_LEVEL_COMMAND = compile_pattern(r':%SOURce%(\d+):%VOLTage%:%PROTection%(?::%LEVel%)? ((?:\d+\.\d+)|MIN|MAX)')
VOLTAGE_PROTECTION_LEVEL_QUERY   = compile_pattern(r':%SOURce%(\d+):%VOLTage%:%PROTection%(?::%LEVel%)?\?(?: (MIN|MAX))?')
CURRENT_PROTECTION_LEVEL_COMMAND = compile_pattern(r':%SOURce%(\d+):%CURRent%:%PROTection%(?::%LEVel%)? ((?:\d+\.\d+)|MIN|MAX)')
CURRENT_PROTECTION_LEVEL_QUERY   = compile_pattern(r':%SOURce%(\d+):%CURRent%:%PROTection%(?::%LEVel%)?\?(?: (MIN|MAX))?')
VOLTAGE_PROTECTION_STATE_COMMAND = compile_pattern(r':%SOURce%(\d+):%VOLTage%:%PROTection%:%STATe% (ON|OFF)')
VOLTAGE_PROTECTION_STATE_QUERY   = compile_pattern(r':%SOURce%(\d+):%VOLTage%:%PROTection%:%STATe%\?')
CURRENT_PROTECTION_STATE_COMMAND = compile_pattern(r':%SOURce%(\d+):%CURRent%:%PROTection%:%STATe% (ON|OFF)')
CURRENT_PROTECTION_STATE_QUERY   = compile_pattern(r':%SOURce%(\d+):%CURRent%:%PROTection%:%STATe%\?')

ACTIONS = (
    (IDN_QUERY, FakeVisaDP832._id_query),
    (OUTPUT_STATE_COMMAND, FakeVisaDP832._output_state_command),
    (OUTPUT_STATE_QUERY, FakeVisaDP832._output_state_query),
    (VOLTAGE_SETPOINT_LEVEL_COMMAND, FakeVisaDP832._voltage_setpoint_level_command),
    (VOLTAGE_SETPOINT_LEVEL_QUERY, FakeVisaDP832._voltage_setpoint_level_query),
    (CURRENT_SETPOINT_LEVEL_COMMAND, FakeVisaDP832._current_setpoint_level_command),
    (CURRENT_SETPOINT_LEVEL_QUERY, FakeVisaDP832._current_setpoint_level_query),
    (VOLTAGE_SETPOINT_STEP_COMMAND, FakeVisaDP832._voltage_setpoint_step_command),
    (VOLTAGE_SETPOINT_STEP_QUERY, FakeVisaDP832._voltage_setpoint_step_query),
    (VOLTAGE_PROTECTION_LEVEL_COMMAND, FakeVisaDP832._voltage_protection_level_command),
    (VOLTAGE_PROTECTION_LEVEL_QUERY, FakeVisaDP832._voltage_protection_level_query),
    (CURRENT_PROTECTION_LEVEL_COMMAND, FakeVisaDP832._current_protection_level_command),
    (CURRENT_PROTECTION_LEVEL_QUERY, FakeVisaDP832._current_protection_level_query),
    (VOLTAGE_PROTECTION_STATE_COMMAND, FakeVisaDP832._voltage_protection_state_command),
    (VOLTAGE_PROTECTION_STATE_QUERY, FakeVisaDP832._voltage_protection_state_query),
    (CURRENT_PROTECTION_STATE_COMMAND, FakeVisaDP832._current_protection_state_command),
    (CURRENT_PROTECTION_STATE_QUERY, FakeVisaDP832._current_protection_state_query),
)
