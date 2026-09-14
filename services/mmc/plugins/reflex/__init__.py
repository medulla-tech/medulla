# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Reflex plugin: supervision by probes.

Read and write API of the console. Evaluating conditions, raising alerts,
distributing the configuration and notifying run in the master substitute.
Every read is filtered on the calling login, whose entities are resolved
here, see _user_entities.
"""

import errno
import json
import logging
import smtplib
import socket
import ssl
from datetime import datetime

from mmc.plugins.reflex.config import ReflexConfig
from mmc.plugins.reflex.mail import build_test_message
from pulse2.database.reflex import (
    ALERT_SORT_SEVERITY,
    ALERT_STATUS_ACTIVE,
    RECIPIENTS_SEPARATOR,
    RefusalReason,
    ReflexDatabase,
    ReflexSecretError,
    ReflexValidationError,
    normalise_recipients,
)

try:
    from pulse2.managers.location import ComputerLocationManager
except ImportError:  # pragma: no cover - depends on the installed packages
    ComputerLocationManager = None

VERSION = "1.0.0"
APIVERSION = "1:0:0"

logger = logging.getLogger()

config = None


def getVersion():
    return VERSION


def getApiVersion():
    return APIVERSION


def _user_entities(login):
    """Entity identifiers a login reaches."""
    if ComputerLocationManager is None:
        return []
    try:
        locations = ComputerLocationManager().getUserLocations(login)
    except Exception as e:
        logger.error("Plugin reflex: the entities of login '%s' cannot be "
                     "read (%s)" % (login, e))
        return []

    entities = []
    for location in locations or []:
        if not isinstance(location, dict):
            continue
        # Key by key: the root entity carries the identifier 0.
        raw = location.get('uuid')
        if raw is None:
            raw = location.get('id')
        raw = str(raw if raw is not None else '').strip()
        if raw.upper().startswith('UUID'):
            raw = raw[4:]
        try:
            entity_id = int(raw)
        except (TypeError, ValueError):
            continue
        if entity_id >= 0 and entity_id not in entities:
            entities.append(entity_id)
    return entities


def activate():
    """Load the configuration and open the reflex database."""
    global config
    config = ReflexConfig("reflex")
    if config.disable:
        logger.warning("Plugin reflex: disabled by configuration.")
        return False
    if not ReflexDatabase().activate(config):
        logger.error(
            "Plugin reflex: an error occurred during the database initialization")
        return False
    ReflexDatabase().set_entity_resolver(_user_entities)
    if ComputerLocationManager is None:
        logger.warning("Plugin reflex: no computer location manager, the "
                       "probes scoped to an entity will be visible to their "
                       "owner only.")
    logger.info("Plugin reflex: activated successfully")
    return True


def _config():
    """Return the plugin configuration, loading it if activate() has not run."""
    global config
    if config is None:
        config = ReflexConfig("reflex")
    return config


def _login(value):
    """Normalise the login carried by every call that depends on rights."""
    return str(value or '').strip()


# =============================================================================
# Activation test
# =============================================================================
def tests():
    """Check that the plugin is activated and its database reachable."""
    return ReflexDatabase().tests()


# =============================================================================
# Dashboard
# =============================================================================
def get_dashboard_summary(login=''):
    """Figures of the supervision dashboard."""
    return ReflexDatabase().get_dashboard_summary(login=_login(login))


# =============================================================================
# Probes
# =============================================================================
def get_probes(login, start=0, limit=20, filter_str='', scope='all',
               entity_id=''):
    """Paginated list of the probes visible to a login, for one entity."""
    return ReflexDatabase().get_probes(
        _login(login), start=start, limit=limit, filter_str=filter_str,
        scope=scope, entity_id=entity_id)


def get_probe(login, probe_id, entity_id=''):
    """Probe with its conditions and its assignments."""
    return ReflexDatabase().get_probe(_login(login), probe_id, entity_id)


def create_probe(login, probe):
    """Create a scripted probe owned by the caller."""
    return ReflexDatabase().create_probe(_login(login), probe)


def update_probe(login, probe_id, probe):
    """Update the definition of a probe. Owner only, never a built-in one."""
    return ReflexDatabase().update_probe(_login(login), probe_id, probe)


def delete_probe(login, probe_id):
    """Delete a probe. Owner only, never a built-in one."""
    return ReflexDatabase().delete_probe(_login(login), probe_id)


def duplicate_probe(login, probe_id, label='', entity_id=None):
    """Duplicate a visible probe into a probe owned by the caller."""
    return ReflexDatabase().duplicate_probe(
        _login(login), probe_id, label=label, entity_id=entity_id)


def set_probe_visibility(login, probe_id, visibility, entity_id=None):
    """Change the scope of a probe. Owner only."""
    return ReflexDatabase().set_probe_visibility(
        _login(login), probe_id, visibility, entity_id=entity_id)


def get_probe_entity_settings(login, probe_id):
    """What this probe does, and what was set on it, in each estate."""
    return ReflexDatabase().get_probe_entity_settings(_login(login), probe_id)


def get_probe_collectors(login, probe_id):
    """Collection methods of a probe, one row per operating system."""
    return ReflexDatabase().get_probe_collectors(probe_id, login=_login(login))


def get_user_entities(login):
    """Entities the caller may scope a probe to."""
    return ReflexDatabase().entities_for_login(_login(login))


# =============================================================================
# Probe conditions
# =============================================================================
def set_probe_conditions(login, probe_id, conditions):
    """Bring the conditions of a probe to the complete set sent."""
    return ReflexDatabase().set_probe_conditions(
        _login(login), probe_id, conditions)


def set_condition_override(login, condition_id, overrides, entity_id=''):
    """Set what the caller chose for one shipped condition, for one entity."""
    return ReflexDatabase().set_condition_override(
        _login(login), condition_id, overrides, entity_id)


def reset_condition_override(login, condition_id, entity_id=''):
    """Give a condition back to what the product ships, for one entity."""
    return ReflexDatabase().reset_condition_override(
        _login(login), condition_id, entity_id)


# =============================================================================
# Probe assignments
# =============================================================================
def assign_probe(login, probe_id, target_type, target_id, interval_seconds,
                 language=None):
    """Place a probe on a target at a given cadence."""
    return ReflexDatabase().assign_probe(
        _login(login), probe_id, target_type, target_id, interval_seconds,
        language)


def assign_probe_bulk(login, probe_id, target_type, target_ids,
                      interval_seconds, language=None):
    """Place a probe on a selection of targets in a single call."""
    return ReflexDatabase().assign_probe_bulk(
        _login(login), probe_id, target_type, target_ids, interval_seconds,
        language)


def unassign_probe(login, assignment_id):
    """Remove an assignment."""
    return ReflexDatabase().unassign_probe(_login(login), assignment_id)


def update_assignment_interval(login, assignment_id, interval_seconds):
    """Change the cadence of one placement, and nothing else."""
    return ReflexDatabase().update_assignment_interval(
        _login(login), assignment_id, interval_seconds)


def unassign_probes_bulk(login, assignment_ids):
    """Remove several assignments. Returns how many were removed."""
    return ReflexDatabase().unassign_probes_bulk(_login(login), assignment_ids)


# =============================================================================
# Probe exclusions
# =============================================================================
def exclude_probe_on_machine(login, probe_id, machines_id, hostname='',
                             reason=''):
    """Take a probe off one machine without touching its assignments."""
    return ReflexDatabase().exclude_probe_on_machine(
        _login(login), probe_id, machines_id, hostname=hostname, reason=reason)


def include_probe_on_machine(login, probe_id, machines_id):
    """Lift the exception of a probe on one machine."""
    return ReflexDatabase().include_probe_on_machine(
        _login(login), probe_id, machines_id)


def get_probe_exclusions(login, probe_id):
    """Machines excepted from a probe, inside the estate the login reaches."""
    return ReflexDatabase().get_probe_exclusions(_login(login), probe_id)


# =============================================================================
# Alerts
# =============================================================================
def get_alerts(login, start=0, limit=20, filter_str='', severity='',
               status=ALERT_STATUS_ACTIVE, opened_from='', opened_to='',
               sort=ALERT_SORT_SEVERITY, probe_id=0):
    """Paginated list of the alerts raised by probes visible to the login."""
    return ReflexDatabase().get_alerts(
        _login(login), start=start, limit=limit, filter_str=filter_str,
        severity=severity, status=status, opened_from=opened_from,
        opened_to=opened_to, sort=sort, probe_id=probe_id)


def ack_alert(login, alert_id, comment=''):
    """Acknowledge an alert."""
    return ReflexDatabase().ack_alert(_login(login), alert_id, comment)


def ack_alerts_bulk(login, alert_ids, comment=''):
    """Acknowledge several alerts. Returns how many were acknowledged."""
    return ReflexDatabase().ack_alerts_bulk(_login(login), alert_ids, comment)


def get_alert(login, alert_id):
    """Everything there is to read about one alert."""
    return ReflexDatabase().get_alert(_login(login), alert_id)


# =============================================================================
# Machines
# =============================================================================
def get_machines_status(login, start=0, limit=20, filter_str=''):
    """Supervision state of the machines."""
    return ReflexDatabase().get_machines_status(
        _login(login), start=start, limit=limit, filter_str=filter_str)


def get_machine_detail(login, machines_id):
    """Probes, last measures and open alerts of one machine."""
    return ReflexDatabase().get_machine_detail(_login(login), machines_id)


def get_agent_config(machines_id, login=''):
    """Probe configuration distributed to the agent of a machine."""
    return ReflexDatabase().get_agent_config(machines_id, login=_login(login))


def get_measures_timeseries(login, machines_id, probe_id, days=7, hours=None,
                            max_points=None):
    """Measures of one probe on one machine over a period."""
    # A max_points left out keeps the default of the data layer; a zero sent
    # through would collapse the window to a single interval.
    try:
        points = int(max_points)
    except (TypeError, ValueError):
        points = 0
    extra = {'max_points': points} if points > 0 else {}
    return ReflexDatabase().get_measures_timeseries(
        _login(login), machines_id, probe_id, days=days, hours=hours, **extra)


def get_agent_presence(login, machines_id, days=7, hours=None):
    """When the agent of one machine was connected over a period."""
    return ReflexDatabase().get_agent_presence(
        _login(login), machines_id, days=days, hours=hours)


# =============================================================================
# Notification channels
# =============================================================================
def _expose_channel(channel):
    """Return a channel as the console may see it."""
    exposed = dict(channel)
    exposed['secret_configured'] = bool(exposed.get('secret_configured'))
    return exposed


def has_encryption_key():
    """Whether a channel password can be stored."""
    cfg = _config()
    return bool(cfg.has_aes_key()) or bool(cfg.ensure_aes_key())


def get_channels(login=''):
    """Notification channels, without any secret, ciphered or not."""
    return [_expose_channel(channel)
            for channel in ReflexDatabase().get_channels(login=_login(login))]


def create_channel(login, channel):
    """Create a notification channel."""
    cfg = _config()
    return ReflexDatabase().create_channel(
        channel, login=_login(login), aes_key=cfg.ensure_aes_key())


def update_channel(channel_id, channel, login=''):
    """Update a notification channel."""
    cfg = _config()
    return ReflexDatabase().update_channel(
        channel_id, channel, login=_login(login), aes_key=cfg.ensure_aes_key())


def delete_channel(channel_id, login=''):
    """Delete a notification channel and the rules that use it."""
    return ReflexDatabase().delete_channel(channel_id, login=_login(login))


def _channel_settings(channel):
    """Sending parameters of a channel, read from its own config_json."""
    try:
        conf = json.loads(channel.get('config_json') or '{}')
    except ValueError:
        conf = {}
    if not isinstance(conf, dict):
        conf = {}

    use_tls = conf.get('use_tls', False)
    if isinstance(use_tls, str):
        use_tls = use_tls.strip().lower() in ('1', 'true', 'yes', 'on')

    try:
        port = int(conf.get('port') or 25)
    except (TypeError, ValueError):
        port = 25

    from_address = str(conf.get('from_address') or '').strip()
    return {
        'host': str(conf.get('host') or '').strip(),
        'port': port,
        'use_tls': bool(use_tls),
        'username': str(conf.get('username') or '').strip(),
        'from_address': from_address,
        'from_name': str(conf.get('from_name') or 'Medulla Reflex').strip(),
    }


def _test_failure_reason(error):
    """Key the console words a failed test with, None when unclassified."""
    if isinstance(error, socket.gaierror):
        return 'smtp_host_unknown'
    if isinstance(error, ssl.SSLError):
        return 'smtp_tls_failed'
    if isinstance(error, (socket.timeout, TimeoutError)):
        return 'smtp_timeout'
    if isinstance(error, ConnectionRefusedError):
        return 'smtp_connect_refused'
    if isinstance(error, (ConnectionResetError, ConnectionAbortedError,
                          BrokenPipeError, smtplib.SMTPServerDisconnected)):
        return 'smtp_connection_lost'
    number = getattr(error, 'errno', None)
    if number == errno.ETIMEDOUT:
        return 'smtp_timeout'
    if number == errno.ECONNREFUSED:
        return 'smtp_connect_refused'
    if number in (errno.ENETUNREACH, errno.EHOSTUNREACH, errno.ENETDOWN):
        return 'smtp_unreachable'
    if isinstance(error, smtplib.SMTPAuthenticationError):
        return 'smtp_auth_refused'
    if isinstance(error, smtplib.SMTPSenderRefused):
        return 'smtp_sender_refused'
    if isinstance(error, smtplib.SMTPConnectError):
        return 'smtp_connect_refused'
    if isinstance(error, smtplib.SMTPException):
        return 'smtp_error'
    return None


def _test_recipient_refusal(recipient):
    """The single address a channel test is sent to, or why it is refused."""
    typed = str(recipient or '').strip()
    if not typed:
        return None, {'success': False, 'attempted': False,
                      'reason': RefusalReason.TEST_RECIPIENT_REQUIRED,
                      'field': 'recipient', 'details': [],
                      'error': "No address to send the test to"}
    try:
        address = normalise_recipients(typed, field='recipient')
    except ReflexValidationError as e:
        return None, {'success': False, 'attempted': False,
                      'reason': e.reason,
                      'field': 'recipient', 'details': e.details,
                      'error': str(e)}
    if RECIPIENTS_SEPARATOR in address:
        return None, {'success': False, 'attempted': False,
                      'reason': RefusalReason.TEST_RECIPIENT_SINGLE,
                      'field': 'recipient',
                      'details': address.split(RECIPIENTS_SEPARATOR),
                      'error': "A test is sent to one address only"}
    return address, None


def _send_test_email(cfg, channel, settings, recipient, language=None):
    """Send one real message through the SMTP server of a channel, to `recipient`
    alone, an address already checked.
    """
    if not settings['host']:
        return {'success': False, 'attempted': False,
                'error': "This channel has no SMTP server: fill in the Server field."}
    if not settings['from_address']:
        return {'success': False, 'attempted': False,
                'error': "This channel has no sender address: fill in the Sender address field."}

    password = ''
    if settings['username']:
        try:
            password = ReflexDatabase().get_channel_secret(
                channel.get('id'), cfg.keyAES32)
        except ReflexSecretError as e:
            return {'success': False, 'attempted': False, 'error': str(e)}
        if not password:
            return {'success': False, 'attempted': False,
                    'error': "This channel declares the user '%s' but no "
                             "password is recorded for it"
                             % settings['username']}

    message, message_id = build_test_message(
        channel.get('name'), settings, recipient, language)

    server = None
    try:
        server = smtplib.SMTP(settings['host'], settings['port'], timeout=15)
        server.ehlo()
        if settings['use_tls']:
            server.starttls()
            server.ehlo()
        if settings['username']:
            server.login(settings['username'], password)
        refused = server.sendmail(settings['from_address'],
                                  [recipient],
                                  message.as_string())
    except smtplib.SMTPResponseException as e:
        detail = e.smtp_error
        if isinstance(detail, bytes):
            detail = detail.decode('utf-8', 'replace')
        return {'success': False, 'attempted': True,
                'reason': ('smtp_auth_refused'
                           if isinstance(e, smtplib.SMTPAuthenticationError)
                           else 'smtp_server_error'),
                'error': "SMTP %s: %s" % (e.smtp_code, detail)}
    except smtplib.SMTPRecipientsRefused as e:
        parts = []
        for address, answer in (e.recipients or {}).items():
            code, detail = answer
            if isinstance(detail, bytes):
                detail = detail.decode('utf-8', 'replace')
            parts.append("%s: %s %s" % (address, code, detail))
        return {'success': False, 'attempted': True,
                'reason': 'smtp_recipients_refused',
                'error': "Every recipient refused: %s" % "; ".join(parts)}
    except (smtplib.SMTPException, socket.error, OSError) as e:
        answer = {'success': False, 'attempted': True,
                  'error': "%s: %s" % (type(e).__name__, e)}
        reason = _test_failure_reason(e)
        if reason:
            answer['reason'] = reason
        return answer
    finally:
        password = ''
        if server is not None:
            try:
                server.quit()
            except Exception:
                pass

    accepted = [r for r in [recipient] if r not in (refused or {})]
    if not accepted:
        return {'success': False, 'attempted': True,
                'error': "No recipient was accepted by %s" % settings['host']}

    result = {
        'success': True,
        'attempted': True,
        'accepted': accepted,
        'provider_message_id': message_id,
        'detail': "Message accepted by %s for %s"
                  % (settings['host'], ", ".join(accepted)),
    }
    if refused:
        result['refused'] = dict(
            (address, "%s %s" % (answer[0], answer[1]))
            for address, answer in refused.items())
    return result


def test_channel(channel_id, login='', language=None, recipient=None):
    """Send a real test message through a channel."""
    cfg = _config()
    database = ReflexDatabase()
    channel = database.get_channel(channel_id, login=_login(login))
    if not channel:
        return {'success': False, 'attempted': False,
                'error': "Unknown notification channel"}

    channel_type = channel.get('channel_type')
    if channel_type != 'email':
        return {'success': False, 'attempted': False,
                'error': "The '%s' channel type is not implemented in this "
                         "version: only email is delivered" % channel_type}

    address, refusal = _test_recipient_refusal(recipient)
    if refusal:
        return refusal

    settings = _channel_settings(channel)
    result = _send_test_email(cfg, channel, settings, address, language)

    try:
        database.add_notification_history(
            channel_id=channel.get('id'),
            recipients=address,
            status='sent' if result.get('success') else 'failed',
            error_message=result.get('error'),
            attempt_count=1,
            accepted_at=datetime.now() if result.get('success') else None,
            provider_message_id=result.get('provider_message_id'))
    except Exception as e:
        logger.warning("Plugin reflex: test sending could not be traced: "
                       "%s" % e)

    return result


# =============================================================================
# Notification rules
# =============================================================================
def get_notification_rules(login=''):
    """Notification rules, with the channel and probe labels joined."""
    return ReflexDatabase().get_notification_rules(login=_login(login))


def create_notification_rule(login, rule):
    """Create a notification rule."""
    return ReflexDatabase().create_notification_rule(rule, login=_login(login))


def update_notification_rule(rule_id, rule, login=''):
    """Update a notification rule."""
    return ReflexDatabase().update_notification_rule(rule_id, rule,
                                                     login=_login(login))


def delete_notification_rule(rule_id, login=''):
    """Delete a notification rule."""
    return ReflexDatabase().delete_notification_rule(rule_id,
                                                     login=_login(login))



# =============================================================================
# Console address
# =============================================================================
def get_console_url():
    """Address at which this console is reached, as the notifications use it."""
    return ReflexDatabase().console_url()


def set_console_url(login, url):
    """Record the address at which this console is reached, or clear it."""
    return ReflexDatabase().set_console_url(_login(login), url)


# =============================================================================
# Retention
# =============================================================================
def get_retention_settings(login=''):
    """The retention horizons in force, in days, for the whole instance."""
    return ReflexDatabase().get_retention_settings(_login(login))


def set_retention_settings(login, values):
    """Record the retention horizons, for the whole instance."""
    return ReflexDatabase().set_retention_settings(_login(login), values)
