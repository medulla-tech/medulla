# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2013 Mandriva, http://www.mandriva.com/
# SPDX-FileCopyrightText: 2018-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

from pulse2.database.msc.orm.commands import Commands
from pulse2.database.msc.orm.commands_on_host import CommandsOnHost
from pulse2.database.msc.orm.commands_on_host_phase import CommandsOnHostPhase
from pulse2.database.msc.orm.target import Target


class TableFactory(type):
    """
    Simulates a CoHQuery structure.

    Based on lists of all columns of msc tables, ORM-like object
    is mapped on a simple instance containing all needed attributes.

    Lists of columns can be generated from this query :

    select COLUMN_NAME from information_schema.columns
     where TABLE_SCHEMA = 'msc'
       and TABLE_NAME = '<table_name>';

    Its output is simply pasted into the factory attribute :
    <table_name>_cols

    ORM class to map must be named like :
    <table_name>_class

    This factory must be declared as __metaclass__.

    """
    coh_class = CommandsOnHost
    coh_cols = """
| id                     |
| fk_commands            |
| host                   |
| start_date             |
| end_date               |
| current_state          |
| stage                  |
| awoken                 |
| uploaded               |
| executed               |
| deleted                |
| inventoried            |
| rebooted               |
| halted                 |
| next_launch_date       |
| attempts_left          |
| attempts_failed        |
| balance                |
| next_attempt_date_time |
| current_launcher       |
| fk_target              |
| scheduler              |
| last_wol_attempt       |
| fk_use_as_proxy        |
| order_in_proxy         |
| max_clients_per_proxy  |
| imgmenu_changed        |
| pull_mode              |
    """
    cmd_class = Commands
    cmd_cols = """
| id                     |
| state                  |
| creation_date          |
| start_file             |
| parameters             |
| start_script           |
| clean_on_success       |
| files                  |
| start_date             |
| end_date               |
| connect_as             |
| creator                |
| dispatched             |
| title                  |
| do_inventory           |
| do_wol                 |
| next_connection_delay  |
| max_connection_attempt |
| pre_command_hook       |
| post_command_hook      |
| pre_run_hook           |
| post_run_hook          |
| on_success_hook        |
| on_failure_hook        |
| maxbw                  |
| deployment_intervals   |
| do_reboot              |
| do_halt                |
| fk_bundle              |
| order_in_bundle        |
| package_id             |
| proxy_mode             |
| do_imaging_menu        |
| sum_running            |
| sum_failed             |
| sum_done               |
| sum_stopped            |
| sum_overtimed          |
    """
    target_class = Target
    target_cols = """
| id             |
| target_name    |
| mirrors        |
| id_group       |
| target_uuid    |
| target_ipaddr  |
| target_macaddr |
| target_bcast   |
| target_network |
    """
    phase_class = CommandsOnHostPhase
    phase_cols = """
| id                  |
| fk_commands_on_host |
| phase_order         |
| name                |
| state               |
    """
    coh = None
    cmd = None
    target = None
    phase = None

    def __new__(cls, name, bases, attrs):
        # all table names to generate
        tables = [t.replace('_cols','') for t in cls.__dict__.keys() if t.endswith ('_cols')]

        for attr_name in tables:
            # gets the ORM class
            klass =  getattr(cls, "%s_class" % attr_name)
            # columns parsing
            cols_attr = getattr(cls, "%s_cols" % attr_name)
            cols = cols_attr.replace("|","").replace(" ","").split("\n")
            tab_attrs = dict([(a, None) for a in cols])
            # columns are created and attached on ORM class
            table_class = type(attr_name, (klass,), tab_attrs)
            instance = table_class()
            attrs.update({attr_name: instance,})

        return type.__new__(cls,name, bases, attrs)
