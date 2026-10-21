# SPDX-FileCopyrightText: 2026 Medulla <support@medulla-tech.io>
# SPDX-License-Identifier: GPL-3.0-or-later
"""Exercise inventory batching with real queue SQL and isolated MMC functions."""

import ast
from contextlib import contextmanager, nullcontext
import datetime
import logging
import time
from pathlib import Path
import types
import unittest
from unittest.mock import Mock

from sqlalchemy import (
    Column, DateTime, ForeignKey, Integer, MetaData, String, Table, and_, create_engine,
    not_, or_, text,
)
from sqlalchemy.orm import declarative_base, sessionmaker


SERVICES = Path(__file__).resolve().parents[2]
MSC = SERVICES / "mmc/plugins/msc"
Base = declarative_base()


def load_functions(path, names, namespace, class_name=None):
    tree = ast.parse(path.read_text())
    nodes = tree.body
    if class_name:
        nodes = next(
            node.body for node in nodes
            if isinstance(node, ast.ClassDef) and node.name == class_name
        )
    selected = [
        node for node in nodes
        if isinstance(node, ast.FunctionDef) and node.name in names
    ]
    if {node.name for node in selected} != set(names):
        raise AssertionError("Missing functions in %s" % path)
    for node in selected:
        node.decorator_list = []
    exec(compile(ast.Module(body=selected, type_ignores=[]), str(path), "exec"), namespace)


class Command(Base):
    __tablename__ = "commands"
    id = Column(Integer, primary_key=True)
    state = Column(String)
    start_date = Column(DateTime)
    end_date = Column(DateTime)


class Deploy(Base):
    __tablename__ = "deploy"
    id = Column(Integer, primary_key=True)
    command = Column(Integer)
    inventoryuuid = Column(String)
    state = Column(String)


class Target(Base):
    __tablename__ = "target"
    id = Column(Integer, primary_key=True)
    target_uuid = Column(String)


class CommandsOnHost(Base):
    __tablename__ = "commands_on_host"
    id = Column(Integer, primary_key=True)
    fk_commands = Column(Integer)
    fk_target = Column(Integer, ForeignKey("target.id"))


class CommandsOnHostPhase(Base):
    __tablename__ = "commands_on_host_phase"
    id = Column(Integer, primary_key=True)
    fk_commands_on_host = Column(Integer, ForeignKey("commands_on_host.id"))
    state = Column(String)


class TestInventoryConvergence(unittest.TestCase):
    def test_inventory_shares_historical_cron_without_an_extra_task(self):
        tree = ast.parse((MSC / "__init__.py").read_text())
        activation = next(
            node for node in tree.body
            if isinstance(node, ast.FunctionDef) and node.name == "activate"
        )
        tasks = {}
        for node in ast.walk(activation):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Attribute)
                and node.func.attr == "addTask"
            ):
                tasks[node.args[0].value] = next(
                    kw.value for kw in node.keywords if kw.arg == "cron_expression"
                )
        self.assertEqual(set(tasks), {"msc.convergence_reschedule"})
        historical = tasks["msc.convergence_reschedule"]
        self.assertIsInstance(historical, ast.Attribute)
        self.assertEqual(historical.attr, "convergence_reschedule")
        scheduled = next(
            node for node in ast.walk(activation)
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
            and node.func.attr == "addTask"
        )
        self.assertEqual(scheduled.args[1].elts[0].id, "convergence_scheduled")

    def test_inventory_and_historical_maintenance_share_one_group_result(self):
        self.enqueue(["UUID9"])
        self.manager.getRestrictedComputersList.return_value = ["UUID9", "UUID10"]
        self.database._get_convergence_soon_ended_commands.return_value = [26]
        self.worker()
        self.assertEqual(self.manager.getRestrictedComputersList.call_count, 2)
        calls = self.database.addMachinesToCommand.call_args_list
        self.assertEqual(calls[0].args[2], ["UUID9", "UUID10"])
        self.assertEqual(calls[1].args[2], ["UUID9"])
        self.namespace["_update_convergence_dates"].assert_called_once_with(26)

    def setUp(self):
        self.engine = create_engine("sqlite://")
        self.addCleanup(self.engine.dispose)
        namespace = {
            "Column": Column, "Integer": Integer, "MetaData": MetaData,
            "String": String, "Table": Table, "text": text,
        }
        load_functions(
            SERVICES / "mmc/plugins/dyngroup/database.py",
            {
                "ensureInventoryConvergenceQueue", "getInventoryConvergenceRequests",
                "acknowledgeInventoryConvergenceRequests",
            },
            namespace, "DyngroupDatabase",
        )
        self.queue = types.SimpleNamespace(db=self.engine)
        for name in (
            "ensureInventoryConvergenceQueue", "getInventoryConvergenceRequests",
            "acknowledgeInventoryConvergenceRequests",
        ):
            setattr(self.queue, name, types.MethodType(namespace[name], self.queue))
        self.queue.ensureInventoryConvergenceQueue()
        self.queue._get_convergence_active_commands_ids = Mock(return_value=[26, 27])
        self.database = Mock()
        self.database.convergenceCommandLock.side_effect = lambda cmd: nullcontext()
        self.database.prepareInventoryConvergenceWindow.return_value = True
        self.database.addMachinesToCommand.side_effect = lambda ctx, cmd, *a, **kw: cmd
        self.database._get_convergence_soon_ended_commands.return_value = []
        self.database._filter_convergence_candidates.side_effect = lambda cmd, uuids: uuids
        self.manager = Mock()
        self.manager.getRestrictedComputersList.return_value = ["UUID9"]
        self.namespace = {
            "logging": logging, "time": time,
            "ComputerManager": lambda: self.manager,
            "MscDatabase": lambda: self.database,
            "DyngroupDatabase": lambda: self.queue,
            "_get_convergence_deploy_group_id_and_user": Mock(return_value=(7, "owner")),
            "getContext": Mock(return_value="owner-context"),
            "_get_convergence_phases": Mock(return_value={"do_inventory": "on"}),
            "_get_convergence_new_machines_to_add": Mock(),
            "_update_convergence_dates": Mock(),
        }
        load_functions(
            MSC / "__init__.py",
            {"convergence_scheduled", "_convergence_scheduled_command"},
            self.namespace,
        )
        self.worker = self.namespace["convergence_scheduled"]

    def enqueue(self, uuids):
        with self.engine.begin() as connection:
            connection.execute(
                text(
                    "INSERT INTO substitute_inventory_convergence (machine_uuid) "
                    "VALUES (:machine_uuid) ON CONFLICT(machine_uuid) DO UPDATE "
                    "SET revision = revision + 1"
                ),
                [{"machine_uuid": uuid} for uuid in uuids],
            )

    def test_large_pass_evaluates_once_per_command_and_adds_bounded_chunks(self):
        for count in (1, 10, 10000, 100000, 300000):
            with self.subTest(notifications=count):
                uuids = ["UUID%s" % number for number in range(count)]
                self.enqueue(uuids)
                self.manager.getRestrictedComputersList.return_value = uuids
                self.manager.reset_mock()
                self.database.addMachinesToCommand.reset_mock()
                self.worker()
                self.assertEqual(self.manager.getRestrictedComputersList.call_count, 2)
                calls = self.database.addMachinesToCommand.call_args_list
                self.assertEqual(len(calls), 2 * ((count + 999) // 1000))
                self.assertTrue(all(0 < len(call.args[2]) <= 1000 for call in calls))
                for cmd_id in (26, 27):
                    inserted = [
                        uuid for call in calls if call.args[1] == cmd_id
                        for uuid in call.args[2]
                    ]
                    self.assertEqual(inserted, uuids)
                self.assertEqual(self.queue.getInventoryConvergenceRequests(), [])

    def test_duplicate_notifications_are_coalesced(self):
        self.enqueue(["UUID9"] * 50)
        self.worker()
        self.assertEqual(
            self.manager.getRestrictedComputersList.call_count, 2
        )
        for call in self.database.addMachinesToCommand.call_args_list:
            self.assertEqual(call.args[2], ["UUID9"])

    def test_notification_arriving_during_evaluation_is_not_acknowledged(self):
        self.enqueue(["UUID9"])
        self.database.addMachinesToCommand.side_effect = (
            lambda ctx, cmd, *a, **kw: (self.enqueue(["UUID10"]), cmd)[1]
        )
        self.worker()
        self.assertEqual(
            [row[1] for row in self.queue.getInventoryConvergenceRequests()],
            ["UUID10"],
        )

    def test_error_retains_batch_and_does_not_skip_other_commands(self):
        self.enqueue(["UUID9"])
        self.database.addMachinesToCommand.side_effect = [-2, 27]
        with self.assertLogs(level="ERROR"):
            self.worker()
        self.assertEqual(self.database.addMachinesToCommand.call_count, 2)
        self.assertEqual(len(self.queue.getInventoryConvergenceRequests()), 1)

    def test_database_failure_does_not_stop_scheduled_task(self):
        self.database.convergenceCommandLock.side_effect = RuntimeError("unavailable")
        with self.assertLogs(level="ERROR"):
            self.worker()

    def test_conforming_batch_does_not_change_command_window(self):
        self.enqueue(["UUID9"])
        self.manager.getRestrictedComputersList.return_value = []
        self.worker()
        self.database.prepareInventoryConvergenceWindow.assert_not_called()
        self.database.addMachinesToCommand.assert_not_called()

    def test_inactive_convergence_is_not_evaluated(self):
        self.queue._get_convergence_active_commands_ids.return_value = []
        self.namespace["_convergence_scheduled_command"](26, {"UUID9"}, False)
        self.manager.getRestrictedComputersList.assert_not_called()

    def test_disabled_command_is_not_scheduled(self):
        self.database.prepareInventoryConvergenceWindow.return_value = False
        self.namespace["_convergence_scheduled_command"](26, {"UUID9"}, False)
        self.database.addMachinesToCommand.assert_not_called()

    def test_empty_queue_does_not_evaluate_groups(self):
        self.worker()
        self.manager.getRestrictedComputersList.assert_not_called()

    def test_empty_queue_still_runs_due_historical_commands(self):
        self.database._get_convergence_soon_ended_commands.return_value = [26]
        self.worker()
        self.assertEqual(self.manager.getRestrictedComputersList.call_count, 1)
        self.namespace["_update_convergence_dates"].assert_called_once_with(26)

    def test_repeated_notifications_update_one_pending_request(self):
        self.enqueue(["UUID9"] * 10)
        rows = self.queue.getInventoryConvergenceRequests()
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0][2], 10)
        self.worker()
        self.assertEqual(self.queue.getInventoryConvergenceRequests(), [])

    def test_new_inventory_for_same_machine_survives_old_acknowledgement(self):
        self.enqueue(["UUID9"])
        self.database.addMachinesToCommand.side_effect = (
            lambda ctx, cmd, *a, **kw: (self.enqueue(["UUID9"]), cmd)[1]
        )
        self.worker()
        remaining = self.queue.getInventoryConvergenceRequests()
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0][1:], ("UUID9", 3))

    def test_acknowledgement_does_not_remove_recreated_request(self):
        self.enqueue(["UUID9"])
        old = self.queue.getInventoryConvergenceRequests()
        self.queue.acknowledgeInventoryConvergenceRequests(old)
        # Real MariaDB AUTO_INCREMENT does not reuse the deleted ID.
        with self.engine.begin() as connection:
            connection.execute(
                self.queue.inventory_convergence_queue.insert(),
                {"id": old[0][0] + 1, "machine_uuid": "UUID9"},
            )
        self.queue.acknowledgeInventoryConvergenceRequests(old)
        self.assertEqual(len(self.queue.getInventoryConvergenceRequests()), 1)

    def test_partial_failure_retries_without_duplicate_chunks(self):
        uuids = ["UUID%s" % number for number in range(1001)]
        self.enqueue(uuids)
        self.manager.getRestrictedComputersList.return_value = uuids
        inserted = {}
        failed = False

        def schedule(ctx, cmd, targets, *args, **kwargs):
            nonlocal failed
            if cmd == 26 and targets == ["UUID1000"] and not failed:
                failed = True
                return -2
            existing = inserted.setdefault(cmd, set())
            self.assertFalse(existing.intersection(targets))
            existing.update(targets)
            return cmd

        self.database.addMachinesToCommand.side_effect = schedule
        self.database._filter_convergence_candidates.side_effect = (
            lambda cmd, targets: [u for u in targets if u not in inserted.get(cmd, set())]
        )
        with self.assertLogs(level="ERROR"):
            self.worker()
        self.assertEqual(len(self.queue.getInventoryConvergenceRequests()), 1001)
        self.worker()
        self.assertEqual(self.queue.getInventoryConvergenceRequests(), [])
        self.assertEqual(inserted, {26: set(uuids), 27: set(uuids)})

    def test_retry_does_not_reinsert_previously_scheduled_targets(self):
        self.enqueue(["UUID9"])
        scheduled = {}

        def eligible(cmd, targets):
            return list(set(targets) - scheduled.get(cmd, set()))

        def schedule(ctx, cmd, targets, *args, **kwargs):
            scheduled.setdefault(cmd, set()).update(targets)
            return cmd

        self.database._filter_convergence_candidates.side_effect = eligible
        self.database.addMachinesToCommand.side_effect = schedule
        self.worker()
        self.enqueue(["UUID9"])
        self.worker()
        self.assertEqual(self.database.addMachinesToCommand.call_count, 2)

    def test_periodic_and_explicit_additions_recheck_under_same_lock(self):
        load_functions(
            MSC / "__init__.py", {"_add_machines_to_convergence_command"},
            self.namespace,
        )
        locked = []

        @contextmanager
        def lock(cmd_id):
            locked.append(cmd_id)
            try:
                yield
            finally:
                locked.remove(cmd_id)

        self.database.convergenceCommandLock.side_effect = lock

        def eligible(ctx, cmd, group):
            self.assertEqual(locked, [26])
            return ["UUID9"]

        self.namespace["_get_convergence_new_machines_to_add"].side_effect = eligible
        result = self.namespace["_add_machines_to_convergence_command"](
            "owner-context", 26, ["UUID9", "UUID10"], 7, {}
        )
        self.assertEqual(result, 26)
        self.assertEqual(self.database.addMachinesToCommand.call_args.args[2], ["UUID9"])

    def test_candidate_filter_and_inflight_guard(self):
        manager, xmpp = Mock(), Mock()
        manager.getRestrictedComputersList.return_value = ["UUID9", "UUID10", "UUID11"]
        xmpp.getPendingConvergenceMachineUuids.return_value = ["UUID9"]
        namespace = {
            "ComputerManager": lambda: manager, "XmppMasterDatabase": lambda: xmpp,
        }
        load_functions(
            MSC / "database.py",
            {"_get_convergence_new_machines_to_add", "_filter_convergence_candidates"},
            namespace, "MscDatabase",
        )
        database = Mock()
        database._get_machines_in_command.return_value = ["UUID10"]
        database._filter_convergence_candidates.side_effect = (
            lambda cmd, targets: namespace["_filter_convergence_candidates"](
                database, Mock(), cmd, targets
            )
        )
        result = namespace["_get_convergence_new_machines_to_add"](
            database, Mock(), "owner", 26, 7, {"UUID9", "UUID10"}
        )
        self.assertEqual(result, [])
        self.assertEqual(manager.getRestrictedComputersList.call_count, 1)
        filt = manager.getRestrictedComputersList.call_args.kwargs["filt"]
        self.assertEqual(filt["gid"], 7)
        self.assertEqual(set(filt["uuids"]), {"UUID9", "UUID10"})
        xmpp.getPendingConvergenceMachineUuids.assert_called_once_with(26, ["UUID9"])


class TestInventoryConvergenceSql(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite://")
        self.addCleanup(self.engine.dispose)
        Base.metadata.create_all(self.engine)
        self.session = sessionmaker(bind=self.engine)()
        self.addCleanup(self.session.close)
        self.namespace = {
            "Commands": Command, "Deploy": Deploy, "datetime": datetime,
            "CommandsOnHost": CommandsOnHost, "Target": Target,
            "CommandsOnHostPhase": CommandsOnHostPhase,
            "and_": and_, "or_": or_, "not_": not_,
            "contextmanager": contextmanager, "text": text,
        }
        load_functions(
            MSC / "database.py",
            {
                "prepareInventoryConvergenceWindow", "convergenceCommandLock",
                "_get_machines_in_command",
            },
            self.namespace, "MscDatabase",
        )
        self.namespace["convergenceCommandLock"] = contextmanager(
            self.namespace["convergenceCommandLock"]
        )
        load_functions(
            SERVICES / "pulse2/database/xmppmaster/__init__.py",
            {"getPendingConvergenceMachineUuids"}, self.namespace, "XmppMasterDatabase",
        )

    def test_only_nonterminal_xmpp_executions_block_redeployment(self):
        states = [
            "DEPLOYMENT SUCCESS", "ABORT PACKAGE EXECUTION ERROR",
            "ERROR UNKNOWN ERROR", "DEPLOYMENT START",
            "WAITING MACHINE ONLINE", None, "DEPLOYMENT PARTIAL SUCCESS",
        ]
        self.session.add_all([
            Deploy(command=26, inventoryuuid="UUID%s" % index, state=state)
            for index, state in enumerate(states)
        ])
        self.session.commit()
        pending = self.namespace["getPendingConvergenceMachineUuids"](
            Mock(), self.session, 26, ["UUID%s" % index for index in range(7)]
        )
        self.assertEqual(set(pending), {"UUID3", "UUID4", "UUID5"})

    def test_queued_target_without_phases_is_not_added_again(self):
        for number in range(3):
            self.session.add(Target(id=number, target_uuid="UUID%s" % number))
            self.session.add(CommandsOnHost(
                id=number, fk_commands=26, fk_target=number
            ))
        self.session.add_all([
            CommandsOnHostPhase(fk_commands_on_host=1, state="done"),
            CommandsOnHostPhase(fk_commands_on_host=2, state="ready"),
        ])
        self.session.commit()
        result = self.namespace["_get_machines_in_command"](Mock(), self.session, 26)
        self.assertEqual(set(result), {"UUID0", "UUID2"})

    def test_only_expired_active_command_window_changes(self):
        now = datetime.datetime.now()
        future = now + datetime.timedelta(hours=12)
        for index, state, end in (
            (1, "active", now - datetime.timedelta(days=1)),
            (2, "active", future),
            (3, "disabled", now - datetime.timedelta(days=1)),
        ):
            self.session.add(Command(
                id=index, state=state, start_date=now, end_date=end
            ))
        self.session.commit()
        prepare = self.namespace["prepareInventoryConvergenceWindow"]
        self.assertTrue(prepare(Mock(), self.session, 1))
        self.assertTrue(prepare(Mock(), self.session, 2))
        self.assertFalse(prepare(Mock(), self.session, 3))
        self.assertGreater(self.session.get(Command, 1).end_date, now)
        self.assertEqual(self.session.get(Command, 2).end_date, future)
        self.assertLess(self.session.get(Command, 3).end_date, now)

    def test_command_lock_is_released_even_on_error(self):
        calls = []
        with self.engine.connect() as connection:
            driver = connection.connection
            driver.create_function(
                "GET_LOCK", 2, lambda name, timeout: calls.append(("get", name)) or 1
            )
            driver.create_function(
                "RELEASE_LOCK", 1, lambda name: calls.append(("release", name)) or 1
            )
        database = types.SimpleNamespace(db=self.engine)
        with self.assertRaisesRegex(ValueError, "failure"):
            with self.namespace["convergenceCommandLock"](database, 26):
                raise ValueError("failure")
        self.assertEqual(calls, [
            ("get", "msc.convergence.26"), ("release", "msc.convergence.26")
        ])


if __name__ == "__main__":
    unittest.main()
