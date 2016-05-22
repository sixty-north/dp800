from test.patterns import compile_pattern


class FakeVisaDP832:

    def __init__(self):
        self._channel_states = [None, 'OFF', 'OFF', 'OFF']

    def write(self, command):
        self.query(command)

    def query(self, command):
        for regex, function in ACTIONS:
            m = regex.match(command)
            if m:
                return function(self, m)
        raise RuntimeError("No match found for command {!r}".format(command))

    def _id_query(self, match):
        return 'RIGOL TECHNOLOGIES,DP832,DP8A000001,00.01.01\n'

    def _output_state_command(self, match):
        channel, state = match.groups()
        channel_index = int(channel)
        self._channel_states[channel_index] = state

    def _output_state_query(self, match):
        channel = match.group(1)
        channel_index = int(channel)
        return self._channel_states[channel_index] + '\n'


IDN_QUERY            = compile_pattern(r'\*IDN\?')
OUTPUT_STATE_COMMAND = compile_pattern(r':%OUTPut%(?::%STATe%) CH(\d+),(ON|OFF)')
OUTPUT_STATE_QUERY   = compile_pattern(r':%OUTPut%(?::%STATe%)\? CH(\d+)')

ACTIONS = (
    (IDN_QUERY, FakeVisaDP832._id_query),
    (OUTPUT_STATE_COMMAND, FakeVisaDP832._output_state_command),
    (OUTPUT_STATE_QUERY, FakeVisaDP832._output_state_query),
)




