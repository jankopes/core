#!/usr/bin/env python3
import logging

from modules.common.abstract_device import AbstractBat
from modules.common.component_state import BatState
from modules.common.component_type import ComponentDescriptor
from modules.common.fault_state import ComponentInfo, FaultState
from modules.common.store import get_bat_value_store
from modules.devices.rct.rct.config import RctBatSetup
from modules.devices.rct.rct.rct_lib import RCT

log = logging.getLogger(__name__)


class RctBat(AbstractBat):
    def __init__(self, component_config: RctBatSetup) -> None:
        self.component_config = component_config

    def initialize(self) -> None:
        self.store = get_bat_value_store(self.component_config.id)
        self.fault_state = FaultState(ComponentInfo.from_component_config(self.component_config))

    def update(self, rct_client: RCT) -> None:
        my_tab = []
        socx = rct_client.add_by_name(my_tab, 'battery.soc')
        watt1 = rct_client.add_by_name(my_tab, 'g_sync.p_acc_lp')
        watt2 = rct_client.add_by_name(my_tab, 'battery.stored_energy')
        watt3 = rct_client.add_by_name(my_tab, 'battery.used_energy')
        stat1 = rct_client.add_by_name(my_tab, 'battery.bat_status')
        stat2 = rct_client.add_by_name(my_tab, 'battery.status')
        stat3 = rct_client.add_by_name(my_tab, 'battery.status2')

        # read all parameters
        rct_client.read(my_tab)

        bat_state = BatState(
            power=watt1.value * -1,
            soc=socx.value * 100,
            imported=watt2.value,
            exported=watt3.value
        )
        self.store.set(bat_state)
        if (stat1.value + stat2.value + stat3.value) > 0:
            # Werte werden trotz Fehlercode übermittelt.
            self.fault_state.warning(
                f"Speicher-Status ist ungleich 0. Status 1: {stat1.value}, Status 2: {stat2.value}, "
                f"Status 3: {stat3.value}")


component_descriptor = ComponentDescriptor(configuration_factory=RctBatSetup)
