import pytest

from dp800.dp800 import DP832


@pytest.fixture
def instrument():
    from test.fake_visa_dp832 import FakeVisaDP832
    visa_dp832 = FakeVisaDP832()
    dp832 = DP832(visa_dp832)
    return dp832


def test_channel_ids(instrument):
    channel_ids = instrument.channel_ids
    assert all(channel_ids[i+1] == channel_ids[i] + 1 for i in range(len(instrument.channel_ids) - 1))


def test_channels(instrument):
    assert all(instrument.channel(id).id == id for id in instrument.channel_ids)


def test_channel_on(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.on()
        assert channel.is_on


def test_channel_off(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.off()
        assert not channel.is_on


def test_channel_is_on_on(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.is_on = True
        assert channel.is_on

def test_channel_is_on_off(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.is_on = False
        assert not channel.is_on

