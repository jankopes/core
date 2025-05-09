#!/usr/bin/env python3
from typing import Any, TypedDict

from modules.common.abstract_device import AbstractInverter
from modules.common.component_state import InverterState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.modbus import ModbusDataType, ModbusTcpClient_
from modules.common.store import get_inverter_value_store
from modules.devices.studer.studer.config import StuderInverterSetup


class KwargsDict(TypedDict):
    client: ModbusTcpClient_


class StuderInverter(AbstractInverter):
    def __init__(self, component_config: StuderInverterSetup, **kwargs: Any) -> None:
        self.component_config = component_config
        self.kwargs: KwargsDict = kwargs

    def initialize(self) -> None:
        self.__tcp_client: ModbusTcpClient_ = self.kwargs['client']
        self.store = get_inverter_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def update(self) -> None:
        vc_count = self.component_config.configuration.vc_count
        vc_type = self.component_config.configuration.vc_type

        with self.__tcp_client:
            if vc_type == 'VS':
                mb_unit = 40
                mb_register = 20  # MB:20; ID: 15010; PV power kW
            elif vc_type == 'VT':
                mb_unit = 20
                mb_register = 8  # MB:8; ID: 11004; Power of the PV generator kW
            else:
                raise ValueError("Unbekannter VC-Typ: "+str(vc_type))
            power = 0
            for i in range(1, vc_count+1):
                mb_unit_dev = mb_unit+i
                power += self.__tcp_client.read_input_registers(mb_register, ModbusDataType.FLOAT_32, unit=mb_unit_dev)
            power = power * -1000

            if vc_type == 'VS':
                mb_register = 46  # MB:46; ID: 15023; Desc: Total PV produced energy MWh
            elif vc_type == 'VT':
                mb_register = 18  # MB:18; ID: 11009; Desc: Total produced energy MWh
            exported = 0
            for i in range(1, vc_count + 1):
                mb_unit_dev = mb_unit + i
                exported += self.__tcp_client.read_input_registers(mb_register, ModbusDataType.FLOAT_32,
                                                                   unit=mb_unit_dev)
            exported = exported * 1000000

        inverter_state = InverterState(
            power=power,
            exported=exported
        )
        self.store.set(inverter_state)


component_descriptor = ComponentDescriptor(configuration_factory=StuderInverterSetup)
