import pytest
from decimal import Decimal

from hypothesis import given
from hypothesis.strategies import floats, data, sampled_from, integers

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


@given(data=data())
def test_set_voltage_setpoint(instrument, data):
    channel_id = data.draw(sampled_from(instrument.channel_ids))
    channel = instrument.channel(channel_id)
    voltage = data.draw(floats(channel.voltage.over_min, channel.voltage.over_max).map(lambda v: round(v, 3)))
    channel.voltage.setpoint = voltage
    assert channel.voltage.setpoint == voltage


@given(data=data())
def test_set_current_setpoint(instrument, data):
    channel_id = data.draw(sampled_from(instrument.channel_ids))
    channel = instrument.channel(channel_id)
    current = data.draw(floats(channel.current.over_min, channel.current.over_max).map(lambda v: round(v, 3)))
    channel.current.setpoint = current
    assert channel.current.setpoint == current