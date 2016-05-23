import pytest
from decimal import Decimal

from hypothesis import given
from hypothesis.strategies import floats, data, sampled_from

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
def test_set_voltage_setpoint_level(instrument, data):
    channel_id = data.draw(sampled_from(instrument.channel_ids))
    channel = instrument.channel(channel_id)
    voltage = data.draw(
        floats(channel.voltage.protection.min, channel.voltage.protection.max).map(
            lambda v: round(v, 3)))
    channel.voltage.level = voltage
    assert channel.voltage.level == voltage


@given(data=data())
def test_set_current_setpoint_level(instrument, data):
    channel_id = data.draw(sampled_from(instrument.channel_ids))
    channel = instrument.channel(channel_id)
    current = data.draw(floats(channel.current.protection.min, channel.current.protection.max).map(lambda v: round(v, 3)))
    channel.current.level = current
    assert channel.current.level == current


@given(data=data())
def test_set_voltage_protection_level(instrument, data):
    channel_id = data.draw(sampled_from(instrument.channel_ids))
    channel = instrument.channel(channel_id)
    voltage = data.draw(floats(channel.voltage.protection.min, channel.voltage.protection.max).map(lambda v: round(v, 3)))
    channel.voltage.protection.level = voltage
    assert channel.voltage.protection.level == voltage


@given(data=data())
def test_set_current_protection_level(instrument, data):
    channel_id = data.draw(sampled_from(instrument.channel_ids))
    channel = instrument.channel(channel_id)
    current = data.draw(floats(channel.current.protection.min, channel.current.protection.max).map(lambda v: round(v, 3)))
    channel.current.protection.level = current
    assert channel.current.protection.level == current


def test_voltage_protection_enabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.voltage.protection.enable()
        assert channel.voltage.protection.is_enabled


def test_voltage_protection_disabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.voltage.protection.disable()
        assert not channel.voltage.protection.is_enabled


def test_voltage_channel_is_enabled_enabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.voltage.protection.is_enabled = True
        assert channel.voltage.protection.is_enabled


def test_voltage_channel_is_enabled_disabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.voltage.protection.is_enabled = False
        assert not channel.voltage.protection.is_enabled


def test_current_protection_enabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.current.protection.enable()
        assert channel.current.protection.is_enabled


def test_current_protection_disabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.current.protection.disable()
        assert not channel.current.protection.is_enabled


def test_current_channel_is_enabled_enabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.current.protection.is_enabled = True
        assert channel.current.protection.is_enabled


def test_current_channel_is_enabled_disabled(instrument):
    for channel_id in instrument.channel_ids:
        channel = instrument.channel(channel_id)
        channel.current.protection.is_enabled = False
        assert not channel.current.protection.is_enabled
