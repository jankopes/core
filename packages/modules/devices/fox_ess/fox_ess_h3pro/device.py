#!/usr/bin/env python3
import logging
from typing import Iterable, Union

from modules.common.abstract_device import DeviceDescriptor
from modules.common.configurable_device import ConfigurableDevice, ComponentFactoryByType, MultiComponentUpdater
from modules.common.modbus import ModbusTcpClient_
from modules.devices.fox_ess.fox_ess_h3pro.bat import FoxEssH3ProBat
from modules.devices.fox_ess.fox_ess_h3pro.counter import FoxEssH3ProCounter
from modules.devices.fox_ess.fox_ess_h3pro.inverter import FoxEssH3ProInverter
from modules.devices.fox_ess.fox_ess_h3pro.config import FoxEssH3Pro, FoxEssH3ProBatSetup, FoxEssH3ProCounterSetup, FoxEssH3ProInverterSetup

log = logging.getLogger(__name__)


def create_device(device_config: FoxEssH3Pro):
    client = None

    def create_bat_component(component_config: FoxEssH3ProBatSetup):
        nonlocal client
        return FoxEssH3ProBat(component_config=component_config, client=client)

    def create_counter_component(component_config: FoxEssH3ProCounterSetup):
        nonlocal client
        return FoxEssH3ProCounter(component_config=component_config, client=client)

    def create_inverter_component(component_config: FoxEssH3ProInverterSetup):
        nonlocal client
        return FoxEssH3ProInverter(component_config=component_config, client=client)

    def update_components(components: Iterable[Union[FoxEssH3ProBat, FoxEssH3ProCounter, FoxEssH3ProInverter]]):
        nonlocal client
        with client:
            for component in components:
                component.update()

    def initializer():
        nonlocal client
        client = ModbusTcpClient_(device_config.configuration.ip_address, device_config.configuration.port)

    return ConfigurableDevice(
        device_config=device_config,
        initializer=initializer,
        component_factory=ComponentFactoryByType(
            bat=create_bat_component,
            counter=create_counter_component,
            inverter=create_inverter_component,
        ),
        component_updater=MultiComponentUpdater(update_components)
    )


device_descriptor = DeviceDescriptor(configuration_factory=FoxEssH3Pro)
