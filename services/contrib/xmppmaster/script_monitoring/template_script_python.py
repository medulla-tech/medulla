#!/usr/bin/env python
# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2016-2023 Siveo <support@siveo.net> 
# SPDX-License-Identifier: GPL-2.0-or-later

import pickle # lib obligatoire pour la serialisation

# metadata a mettre dans le script python
serialisationpickleevent = """@@@@@event@@@@@"""

eventstruct = pickle.loads(serialisationpickleevent)
# on peut se servir de la structure eventstruct.
#exemple de structure event :
    #{'mon_devices_doc': '{"counters": {"reads": 25, "readErrors": "nnn"}}', 'mon_devices_mon_machine_id': 94L, 'mon_rules_user': None, 'mon_event_type_event': 'script_python', 'mon_devices_status': 'disable', 'mon_machine_hostname': 'deb10-90', 'mon_rules_error_on_binding': None, 'mon_devices_device_type': 'nfcReader', 'mon_event_ack_date': None, 'mon_rules_succes_binding_cmd': 'test.py', 'mon_devices_alarm_msg': '["NO_DEVICE"]', 'mon_event_parameter_other': None, 'mon_event_id': 430L, 'mon_devices_id': 360L, 'mon_machine_date': '2020-06-24 15:45:02', 'mon_event_machines_id': 94L, 'mon_devices_serial': 'xxxxxx', 'mon_rules_id': 11L, 'mon_rules_hostname': 'deb10-90', 'mon_rules_comment': None, 'mon_rules_binding': "resultbinding = True if int(data['counters']['reads']) >= 15 else False", 'mon_event_cmd': 'test.py', 'mon_event_id_device': 360L, 'mon_event_status_event': 1L, 'mon_machine_id': 94L, 'mon_event_id_rule': 11L, 'mon_rules_type_event': 'script_python', 'mon_machine_machines_id': 90L, 'mon_rules_device_type': 'nfcReader', 'mon_machine_statusmsg': '', 'mon_rules_no_success_binding_cmd': None, 'mon_devices_firmware': 'xxxx', 'mon_event_ack_user': None}

# j'affiche la structures en exemples
print("voici les informations de l'événement")
print(eventstruct)
