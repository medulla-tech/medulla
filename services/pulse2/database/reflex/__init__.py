# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Data layer of the reflex module.

Shared by the MMC plugin and the master substitute, so that both read the
schema the same way. Visibility, parameter binding, secret ciphering and the
two levels of a condition setting are enforced here and not in the callers.
No condition is evaluated and no message is sent from here.
"""

import base64
import ipaddress
import json
import logging
import os
import re
import time
import unicodedata
from configparser import ConfigParser
from datetime import datetime, timedelta
from urllib.parse import urlsplit

try:
    from Cryptodome.Cipher import AES
    from Cryptodome.Util.Padding import pad, unpad
    CRYPTO_AVAILABLE = True
except ImportError:  # pragma: no cover - depends on the installed packages
    AES = None
    pad = None
    unpad = None
    CRYPTO_AVAILABLE = False

from sqlalchemy import create_engine, MetaData, text
from sqlalchemy.exc import DBAPIError, IntegrityError

from mmc.database.database_helper import DatabaseHelper
from pulse2.database.reflex.schema import (
    Base as ReflexSchemaBase,
    SEVERITIES,
    OPERATORS,
    OPERATING_SYSTEMS,
    USER_VISIBILITIES,
    CATEGORIES,
    VALUE_TYPES,
    TARGET_TYPES,
    ALERT_STATUSES,
    CHANNEL_TYPES,
    CONFIG_CHANGE_SCOPES,
)

logger = logging.getLogger()

# Operators that need a second bound.
RANGE_OPERATORS = ('between', 'outside')
# Operators that compare nothing: no threshold to validate, no point to draw
# on a chart, and no verdict from a single measure.
THRESHOLDLESS_OPERATORS = ('changed',)
# Operators acceptable for each value type.
OPERATORS_BY_VALUE_TYPE = {
    'numeric': ('gt', 'gte', 'lt', 'lte', 'eq', 'ne',
                'between', 'outside', 'changed'),
    'boolean': ('eq', 'ne', 'changed'),
    'text': ('eq', 'ne', 'changed'),
}

# Ordering of severities, from the least to the most serious.
SEVERITY_RANK = {'info': 1, 'medium': 2, 'high': 3, 'critical': 4}

# Silence beyond which a machine is called silent when nothing else can date
# it: no cadence is known for it and no caller named a threshold.
DEFAULT_SILENT_AFTER_SECONDS = 3600

# Largest selection accepted in one assign_probe_bulk call.
MAX_BULK_ASSIGNMENTS = 200

# Copies of one probe the module is willing to tell apart, on probe_key as on
# the label, so two copies never read alike in the console.
MAX_PROBE_COPIES = 50

# A personal probe is a command the agent runs; the first line it prints is
# the measure. The Unix command serves Linux and macOS alike.
SCRIPT_COMMAND_MAX_LENGTH = 4000
SCRIPT_COLLECTORS = (
    ('command_unix', 'linux', 'script.sh'),
    ('command_unix', 'darwin', 'script.sh'),
    ('command_windows', 'windows', 'script.powershell'),
)
SCRIPT_COMMAND_FIELDS = ('command_unix', 'command_windows')
# probe_key of a scripted probe is generated, under a prefix the shipped
# catalog never uses: the schema upserts its probes on probe_key, and a
# personal probe must never be taken for one of them.
SCRIPT_PROBE_KEY_PREFIX = 'custom_'
SCRIPT_METRIC_KEY_PREFIX = 'script.'
# Width of probe_measures.detail.
MEASURE_DETAIL_MAX_LENGTH = 512

# Window read by the aggregates that answer "does this machine still measure,
# and what?": the machine list.
MACHINE_ACTIVITY_WINDOW_SECONDS = 86400

# Gap between the timestamp a machine writes on a measure and the one the
# server stamps when it arrives, beyond which the clock of the machine is said
# to be off.
CLOCK_DRIFT_TOLERANCE_SECONDS = 180

# Reports a machine may skip before what it last said stops being taken for
# what it is doing now.
SILENCE_MISSED_REPORTS = 3

# Added on top of the missed reports whatever the cadence.
SILENCE_GRACE_SECONDS = 120

# Spread of the report of one probe, used to read back every measure of its
# last batch.
MEASURE_BATCH_WINDOW_SECONDS = 120

# Points a chart is served at most.
MEASURE_POINTS_CEILING = 20000

# Points a curve is reduced to when the window holds more measures than it can
# be served raw.
MEASURE_AGGREGATE_POINTS = 1500

# Longest window a chart may ask for in hours.
MEASURE_WINDOW_MAX_HOURS = 720

# Presence events read for one machine over one period.
PRESENCE_EVENTS_MAX = 2000

# Difference tolerated between the interval separating two presence events and
# the duration the master measured for the state that ended.
PRESENCE_GAP_TOLERANCE_SECONDS = 120

# Rows deleted per statement by purge_old_data, and number of statements it
# allows itself per table and per pass.
PURGE_BATCH_SIZE = 20000
PURGE_MAX_BATCHES = 200

# Sending attempts returned for one alert.
NOTIFICATION_TRACE_LIMIT = 200

# Keys refused in notification_channels.config_json: a secret belongs to the
# local configuration file, never to the database.
SECRET_LIKE_KEYS = ('password', 'passwd', 'pwd', 'secret', 'token', 'api_key',
                    'apikey', 'access_key', 'private_key', 'bearer',
                    'credential', 'credentials', 'auth')

# Lifetime of the cache holding the entities a login reaches, in seconds.
ENTITY_CACHE_TTL_SECONDS = 30

# Logins kept in that cache before it is dropped whole.
ENTITY_CACHE_MAX_LOGINS = 500


# Columns of a condition an estate may override, in the order the statements
# read them.
CONDITION_OVERRIDE_FIELDS = ('threshold_value', 'threshold_value2',
                             'threshold_text', 'duration_seconds',
                             'severity', 'message_template', 'enabled')


# Columns where an alert freezes the condition that actually fired, and the key
# each one carries once read as a condition.
ALERT_FREEZE_FIELDS = (('operator_at_trigger', 'operator'),
                       ('threshold_value_at_trigger', 'threshold_value'),
                       ('threshold_value2_at_trigger', 'threshold_value2'),
                       ('threshold_text_at_trigger', 'threshold_text'),
                       ('duration_seconds_at_trigger', 'duration_seconds'))


# Length of the AES-256 key expected in [main] keyAES32.
AES_KEY_LENGTH = 32


# From the narrowest target to the widest, used to break a tie between two
# assignments that reach the same machine at the same cadence.
TARGET_SPECIFICITY = {'machine': 0, 'group': 1, 'entity': 2}


# What became of the target of a placement, carried by every row that names one
# under `target_state`.
TARGET_STATE_OK = 'ok'
TARGET_STATE_OUT_OF_SCOPE = 'out_of_scope'
TARGET_STATE_DELETED = 'deleted'


# Written to alerts.resolved_reason when the resolution comes from a gesture of
# the operator and not from a measure back under the threshold.
ALERT_RESOLVED_BY_EXCLUSION = "probe_excluded"
ALERT_RESOLVED_BY_UNASSIGN = "probe_unassigned"
ALERT_RESOLVED_BY_SCOPE = "probe_out_of_scope"
# Spelled as the substitute spells it when its sweep finds an alert whose
# condition no longer exists: the same event closed by another path.
ALERT_RESOLVED_BY_CONDITION_REMOVED = "condition_removed"
ALERT_RESOLVED_BY_CONDITION_CHANGE = "condition_changed"
ALERT_RESOLVED_BY_CONDITION_DISABLE = "condition_disabled"
# Written by the substitute, never by this module: a more serious condition
# of the same probe opened its alert on the same machine and instance, and one
# alert per machine, probe and instance stands, the most serious.
ALERT_RESOLVED_BY_SUPERSEDE = "superseded"


# Statuses an alert carries while the problem it names is still there.
ALERT_STATUS_OPEN = 'open'
ALERT_STATUS_ACK = 'ack'
ALERT_ACTIVE_STATUSES = (ALERT_STATUS_OPEN, ALERT_STATUS_ACK)

# Value get_alerts accepts to ask for that scope in one word.
ALERT_STATUS_ACTIVE = 'active'

# Orders get_alerts accepts.
ALERT_SORT_SEVERITY = 'severity'
ALERT_SORT_RECENT = 'recent'


class ConditionTrust(object):
    """How far the condition shown on an alert can be attributed to it."""

    # The condition displayed is the one that fired, proven: the alert froze
    # its operator, its thresholds and its duration at insert, and they come
    # back as condition_at_trigger.
    CERTIFIED = 'certified'

    # No proof either way.
    UNVERIFIED = 'unverified'

    # Proven to have moved since the alert opened.
    CHANGED = 'changed'

    # Worse than changed: the value that raised the alert does not satisfy the
    # condition displayed.
    CONTRADICTED = 'contradicted'

    # The condition was deleted since.
    GONE = 'gone'


class ConditionEvidence(object):
    """What was actually observed, under the status ConditionTrust carries."""

    # alerts.severity is written once, at insert, from the effective severity
    # of the condition -- see apply_condition in the master substitute.
    SEVERITY_MOVED = 'severity_moved'

    # The customized_at of the estate that sets this machine is later than
    # alerts.opened_at: somebody posed an override after this alert was raised.
    CUSTOMIZED_AFTER_OPEN = 'customized_after_open'

    # The value frozen in value_at_trigger does not satisfy the condition as it
    # reads today.
    TRIGGER_VALUE_UNSATISFIED = 'trigger_value_unsatisfied'

    # The condition is turned off today, and only an enabled condition raises
    # anything: the substitute reads it as it applies to this machine.
    CONDITION_DISABLED_NOW = 'condition_disabled_now'

    # The condition frozen on the alert and the condition of today do not say
    # the same thing: a threshold, a bound, an operator or a duration was
    # moved.
    CONDITION_MOVED = 'condition_moved'

    # The condition row is gone, and the alert still carries what it was.
    CONDITION_DELETED_NOW = 'condition_deleted_now'

    # probes.updated_at is later than alerts.opened_at.
    PROBE_EDITED_AFTER_OPEN = 'probe_edited_after_open'


# What still concludes on an alert that froze its condition.
CERTIFIED_PROOFS = (ConditionEvidence.CONDITION_MOVED,
                    ConditionEvidence.CONDITION_DELETED_NOW,
                    ConditionEvidence.SEVERITY_MOVED,
                    ConditionEvidence.CONDITION_DISABLED_NOW)


# Date formats accepted on a period bound, the most precise first.
PERIOD_FORMATS = ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S",
                  "%Y-%m-%d %H:%M", "%Y-%m-%dT%H:%M")
PERIOD_DATE_FORMAT = "%Y-%m-%d"


# Cadence the substitute falls back on for a probe declaring none, and the
# bound of one statement reading alerts or measures by identifier.
SUBSTITUTE_DEFAULT_INTERVAL_SECONDS = 300
IDS_PER_STATEMENT = 1000


# ---------------------------------------------------------------------------
# Operating settings
# ---------------------------------------------------------------------------

# Lifetime of the settings cache, in seconds.
SETTINGS_CACHE_TTL_SECONDS = 30


# Address at which this console is reached from a browser, up to and not
# including main.php.
CONSOLE_URL_SETTING = 'console.base_url'

# Route of the alert page of the console, appended to that address.
CONSOLE_ALERTS_PATH = 'mmc/main.php?module=reflex&submod=reflex&action=alerts'

# Longest address accepted, the width of settings.value.
CONSOLE_URL_MAX_LENGTH = 512

# Characters refused in a console address on top of the parsing below.
CONSOLE_URL_FORBIDDEN_CHARS = '"\'<>`\\{}|^ \t\r\n'

# Settings a deployment may legitimately leave empty.
OPTIONAL_SETTINGS = (CONSOLE_URL_SETTING,)


# Retention horizons the console may change, field name -> (setting key,
# lowest, highest), in days. They hold for the whole instance.
RETENTION_SETTINGS = (
    ('measures_days', 'retention.measures_days', 1, 365),
    ('alerts_resolved_days', 'retention.alerts_resolved_days', 7, 3650),
    ('notification_history_days', 'retention.notification_history_days',
     7, 3650),
)


# Where the public name of this server is read when the setting above is empty.
MMC_INI_PATH = '/etc/mmc/mmc.ini'
MMC_INI_PATHS = (MMC_INI_PATH, MMC_INI_PATH + '.local')
MMC_INI_SERVER_SECTION = 'server_01'
MMC_INI_SERVER_NAME_KEY = 'description'

# Scheme given to a derived address.
CONSOLE_URL_DERIVED_SCHEME = 'https'

# Names that are not an address of this server as somebody else reaches it.
CONSOLE_HOST_REFUSED_NAMES = ('localhost', 'localhost.localdomain',
                              'localdomain', 'local')

# A hostname and nothing else.
CONSOLE_HOST_ALLOWED_RE = re.compile(r'^[A-Za-z0-9]([A-Za-z0-9._-]*[A-Za-z0-9])?$')


class RefusalReason(object):
    """Stable keys naming the rule a refused value broke."""

    PAYLOAD_MALFORMED = 'payload_malformed'

    # Enumerations.
    VALUE_TYPE_UNKNOWN = 'value_type_unknown'
    OPERATOR_UNKNOWN = 'operator_unknown'
    OPERATOR_NOT_APPLICABLE = 'operator_not_applicable'
    SEVERITY_UNKNOWN = 'severity_unknown'
    CATEGORY_UNKNOWN = 'category_unknown'
    CHANNEL_TYPE_UNKNOWN = 'channel_type_unknown'
    TARGET_TYPE_UNKNOWN = 'target_type_unknown'
    SCOPE_UNKNOWN = 'scope_unknown'

    # Numbers.
    VALUE_NOT_NUMERIC = 'value_not_numeric'
    THRESHOLD_NOT_WHOLE = 'threshold_not_whole'
    DURATION_NEGATIVE = 'duration_negative'

    # Thresholds against the operator and the value type.
    THRESHOLD_REQUIRED = 'threshold_required'
    THRESHOLD_NOT_ALLOWED = 'threshold_not_allowed'
    THRESHOLD_TEXT_REQUIRED = 'threshold_text_required'
    THRESHOLD_TEXT_NOT_ALLOWED = 'threshold_text_not_allowed'
    THRESHOLD_BOOLEAN_EXPECTED = 'threshold_boolean_expected'
    SECOND_BOUND_NOT_ALLOWED = 'second_bound_not_allowed'
    RANGE_BOUNDS_REQUIRED = 'range_bounds_required'
    RANGE_BOUNDS_ORDER = 'range_bounds_order'

    # Text fields, whatever the payload they belong to.
    FIELD_REQUIRED = 'field_required'
    FIELD_TOO_LONG = 'field_too_long'
    # The value does not have the shape the field accepts: a probe key with a
    # capital in it, a machine target that is not a machines_id.
    FIELD_FORMAT_INVALID = 'field_format_invalid'
    # A count of seconds or of minutes that has to be strictly above zero.
    VALUE_NOT_POSITIVE = 'value_not_positive'
    # A whole number was expected, or one inside the bounds of its setting.
    VALUE_NOT_INTEGER = 'value_not_integer'
    VALUE_OUT_OF_RANGE = 'value_out_of_range'

    # Overrides.
    FIELD_NOT_OVERRIDABLE = 'field_not_overridable'

    # Who is writing, and what the object already holds.
    LOGIN_REQUIRED = 'login_required'
    NAME_ALREADY_USED = 'name_already_used'
    LIMIT_REACHED = 'limit_reached'

    # The name of a probe.
    LABEL_ALREADY_USED = 'label_already_used'
    LABEL_RESERVED = 'label_reserved'

    # Scope of a probe.
    SCOPE_RESERVED = 'scope_reserved'
    ENTITY_FORBIDDEN = 'entity_forbidden'
    # What a placement was asked to act upon stands outside the estate the
    # caller reaches: another client's machine, entity or group.
    TARGET_FORBIDDEN = 'target_forbidden'
    # What a placement acts upon no longer exists at all, see
    # TARGET_STATE_DELETED. Not a right: the placement stands, its target is
    # gone, and the only gesture left on it is to take it off.
    TARGET_DELETED = 'target_deleted'

    # What a notification rule points at.
    CHANNEL_UNKNOWN = 'channel_unknown'
    PROBE_UNKNOWN = 'probe_unknown'

    # Channels.
    CONFIG_JSON_INVALID = 'config_json_invalid'
    CONFIG_JSON_SECRET = 'config_json_secret'
    # One or more recipient addresses are not mail addresses; `details` lists
    # them as they were typed.
    EMAIL_INVALID = 'email_invalid'
    # No usable keyAES32, so a channel password can be neither ciphered nor
    # read back.
    SECRET_KEY_UNUSABLE = 'secret_key_unusable'
    # A channel test is sent to one address typed for the test, and none was.
    TEST_RECIPIENT_REQUIRED = 'test_recipient_required'
    # Several addresses were typed for a test that is sent to one only.
    TEST_RECIPIENT_SINGLE = 'test_recipient_single'


class ReflexValidationError(ValueError):
    """Raised when a payload does not match the schema contract."""

    def __init__(self, message, field=None, reason=None, details=None):
        ValueError.__init__(self, message)
        self.field = field
        self.reason = reason or ''
        self.details = list(details or [])


class ReflexSecretError(ReflexValidationError):
    """Raised when a channel secret cannot be ciphered or read back."""
    pass


class ReflexSettingsError(Exception):
    """Raised when an operating setting cannot be read from the database."""
    pass


# Why a refused write answers a structure and not False.
REFUSAL_MISSING = 'missing'      # the object is gone, or was never visible
REFUSAL_FORBIDDEN = 'forbidden'  # the caller may not write this
REFUSAL_READONLY = 'readonly'    # shipped by the product, not editable
REFUSAL_INVALID = 'invalid'      # the payload does not hold together
REFUSAL_FAILED = 'failed'        # the statement itself failed

# Largest cadence probe_assignments.interval_seconds, a signed int, can hold.
MAX_INTERVAL_SECONDS = 2 ** 31 - 1


def refused(code, message, field=None, condition=0, reason='',
            details=None):
    """Answer of a write that did not happen, with the reason it did not."""
    return {
        'success': False,
        'code': code,
        'reason': reason or '',
        'error': message,
        'field': field or '',
        'condition': _to_int(condition, 0),
        'details': [str(item) for item in (details or [])],
    }


PROBE_OUT_OF_REACH = "This probe does not exist, or it is not visible to you"
CHANNEL_GONE = "This channel does not exist any more"
RULE_GONE = "This rule does not exist any more"
ASSIGNMENT_GONE = "This assignment does not exist any more"
ASSIGNMENT_PROBE_HIDDEN = ("This assignment does not exist, or its probe is "
                           "not visible to you")
NO_ASSIGNMENT_NAMED = "No assignment was named"


def _reachable(access):
    """Whether the object an access answers for exists and is readable."""
    return bool(access['exists'] and access['visible'])


def refused_from(error, code=REFUSAL_INVALID, condition=0):
    """The same answer, built from a ReflexValidationError."""
    return refused(code, str(error), error.field, condition,
                   error.reason, error.details)


def check_aes_key(key):
    """Return the key as bytes, or say precisely what is wrong with it."""
    if not CRYPTO_AVAILABLE:
        raise ReflexSecretError(
            "The pycryptodome library is missing: channel secrets cannot be "
            "ciphered")
    key = key or ''
    if isinstance(key, bytes):
        raw = key
    else:
        raw = str(key).encode('utf-8')
    if not raw:
        raise ReflexSecretError(
            "No encryption key: set keyAES32 in the [main] section of "
            "reflex.ini.local before recording a channel secret")
    if len(raw) != AES_KEY_LENGTH:
        raise ReflexSecretError(
            "The keyAES32 encryption key must be exactly %d characters, the "
            "one configured holds %d" % (AES_KEY_LENGTH, len(raw)))
    return raw


def encrypt_secret(plaintext, key):
    """Cipher a channel secret, AES-256-CBC, random IV prefixed, base64."""
    raw_key = check_aes_key(key)
    if plaintext is None:
        return None
    if not isinstance(plaintext, bytes):
        plaintext = str(plaintext).encode('utf-8')
    if not plaintext:
        return None
    iv = os.urandom(16)
    cipher = AES.new(raw_key, AES.MODE_CBC, iv)
    encrypted = cipher.encrypt(pad(plaintext, AES.block_size))
    return base64.b64encode(iv + encrypted).decode('utf-8')


def decrypt_secret(ciphertext, key):
    """Read a channel secret back."""
    # NULL, empty string or anything else empty: there is no secret to read.
    if not ciphertext:
        return ''
    raw_key = check_aes_key(key)
    try:
        blob = base64.b64decode(ciphertext)
    except Exception:
        raise ReflexSecretError(
            "Unreadable secret: the stored value is not valid base64")
    if len(blob) <= 16 or (len(blob) - 16) % AES.block_size != 0:
        raise ReflexSecretError(
            "Unreadable secret: the stored value has an unexpected length")
    try:
        cipher = AES.new(raw_key, AES.MODE_CBC, blob[:16])
        return unpad(cipher.decrypt(blob[16:]), AES.block_size).decode('utf-8')
    except Exception:
        # Nothing of the value is reported, only the likely cause.
        raise ReflexSecretError(
            "Unreadable secret: has the keyAES32 encryption key changed?")


def _to_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _login(value):
    """Normalise the login carried by every call that depends on rights."""
    return str(value or '').strip()


def _to_float(value, field=None):
    """Read a number the console sent, or None when it sent none."""
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        return 1.0 if value else None
    if isinstance(value, str):
        value = value.strip().replace(',', '.')
        if not value:
            return None
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ReflexValidationError("A numeric value is expected", field,
                                   RefusalReason.VALUE_NOT_NUMERIC)


def _to_whole(value, field=None):
    """Read a threshold the console sent: a whole number, or None."""
    number = _to_float(value, field)
    if number is None:
        return None
    if not number.is_integer():
        raise ReflexValidationError("A threshold must be a whole number",
                                    field,
                                    RefusalReason.THRESHOLD_NOT_WHOLE)
    return number


def _positive_seconds(value, field):
    """Read a count of seconds the console sent: a whole number above zero."""
    if isinstance(value, bool):
        raise ReflexValidationError("A whole number of seconds is expected",
                                    field, RefusalReason.VALUE_NOT_INTEGER)
    number = _to_float(value, field)
    if number is None:
        raise ReflexValidationError("Field %s is required" % field, field,
                                    RefusalReason.FIELD_REQUIRED)
    if not number.is_integer():
        raise ReflexValidationError("A whole number of seconds is expected",
                                    field, RefusalReason.VALUE_NOT_INTEGER)
    if number <= 0:
        raise ReflexValidationError("A cadence is strictly above zero",
                                    field, RefusalReason.VALUE_NOT_POSITIVE)
    if number > MAX_INTERVAL_SECONDS:
        raise ReflexValidationError(
            "A cadence is at most %d seconds" % MAX_INTERVAL_SECONDS, field,
            RefusalReason.VALUE_OUT_OF_RANGE)
    return int(number)


def _to_bool_int(value):
    if isinstance(value, bool):
        return 1 if value else 0
    if isinstance(value, str):
        return 1 if value.strip().lower() in ('1', 'true', 'yes', 'on') else 0
    return 1 if _to_int(value, 0) else 0


def _clean_str(value, maxlen, field, required=False):
    """Normalise a text field and refuse what the column cannot hold."""
    if value is None:
        value = ''
    value = str(value).strip()
    if not value:
        if required:
            raise ReflexValidationError("Field %s is required" % field,
                                        field, RefusalReason.FIELD_REQUIRED)
        return None
    if len(value) > maxlen:
        raise ReflexValidationError(
            "Field %s is longer than %d characters" % (field, maxlen), field,
            RefusalReason.FIELD_TOO_LONG)
    return value


def _clean_command(value, field):
    """Normalise the command of a scripted probe, '' when there is none."""
    if value is None:
        return ''
    if not isinstance(value, str):
        raise ReflexValidationError("Field %s must be a text" % field, field,
                                    RefusalReason.FIELD_FORMAT_INVALID)
    value = value.strip()
    if '\x00' in value:
        raise ReflexValidationError("Field %s holds a NUL byte" % field,
                                    field, RefusalReason.FIELD_FORMAT_INVALID)
    if len(value) > SCRIPT_COMMAND_MAX_LENGTH:
        raise ReflexValidationError(
            "Field %s is longer than %d characters"
            % (field, SCRIPT_COMMAND_MAX_LENGTH), field,
            RefusalReason.FIELD_TOO_LONG)
    return value


# Said once per process: a base without probe_shipped_labels answers the
# same way at every probe written, and one line says it.
_SHIPPED_LABELS_SAID = False


def _drop_latin_accents(value):
    """`value` with the accents of its Latin letters removed."""
    out = []
    latin_base = False
    for char in unicodedata.normalize('NFD', value):
        if unicodedata.combining(char):
            if latin_base:
                continue
            out.append(char)
            continue
        latin_base = 'LATIN' in unicodedata.name(char, '')
        out.append(char)
    return unicodedata.normalize('NFC', ''.join(out))


def fold_label(value):
    """The form two probe names are compared under."""
    return _drop_latin_accents(' '.join(str(value or '').split()).casefold())


def shipped_label_index(engine):
    """Folded names of the shipped probes, by probe_key, read from the base."""
    global _SHIPPED_LABELS_SAID
    index = {}
    try:
        with engine.connect() as connection:
            for row in _rows(connection.execute(text(
                    "SELECT probe_key, label FROM probe_shipped_labels"))):
                folded = fold_label(row.get('label'))
                if not folded:
                    continue
                index.setdefault(str(row.get('probe_key') or ''),
                                 set()).add(folded)
    except Exception as error:
        if not _SHIPPED_LABELS_SAID:
            _SHIPPED_LABELS_SAID = True
            logger.warning(
                "Reflex: probe_shipped_labels unreadable (%s). Probe names "
                "are compared on the stored wording alone until the base is "
                "migrated" % error)
        return None
    return index


def script_key_base(label):
    """probe_key stem of a scripted probe, read from its label."""
    folded = unicodedata.normalize('NFKD', str(label or ''))
    folded = folded.encode('ascii', 'ignore').decode('ascii').lower()
    stem = re.sub(r'[^a-z0-9]+', '_', folded).strip('_')[:60].strip('_')
    return SCRIPT_PROBE_KEY_PREFIX + (stem or 'probe')


def script_collector_rows(commands):
    """probe_collectors rows of a scripted probe, and its os_support."""
    rows = []
    for field, os_name, collector in SCRIPT_COLLECTORS:
        command = commands.get(field) or ''
        if command:
            rows.append({'os': os_name, 'collector': collector,
                         'params_json': json.dumps({'command': command})})
    return rows, normalise_os_support([row['os'] for row in rows])


def attach_measure_detail(measures):
    """Give every measure sent to the console its `detail`, '' when none."""
    for measure in measures or []:
        measure['detail'] = str(measure.get('detail') or '')
    return measures


def _measure_detail(value):
    """All or nothing: a detail wider than its column is not stored.

    A detail is read whole by the console, a JSON object as much as a
    sentence; cut in the middle it would read as corrupt.
    """
    if value is None:
        return None
    value = str(value).strip()
    if not value or len(value) > MEASURE_DETAIL_MAX_LENGTH:
        return None
    return value


def _truncate_str(value, maxlen):
    """Fit a trace into its column instead of refusing the whole row."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None
    return value[:maxlen]


def _serialise(value):
    """Make a database value transportable over XML-RPC."""
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    try:
        from decimal import Decimal
        if isinstance(value, Decimal):
            return float(value)
    except ImportError:
        pass
    return value


def _read_moment(value):
    """Read back a timestamp this module serialised, or None."""
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    value = str(value).strip()
    if not value:
        return None
    for fmt in PERIOD_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def _rows(result):
    """Turn a result set into a list of serialisable dicts."""
    keys = list(result.keys())
    out = []
    for row in result:
        out.append(dict((k, _serialise(v)) for k, v in zip(keys, row)))
    return out


def _one(result):
    rows = _rows(result)
    return rows[0] if rows else None


def _placeholders(prefix, values):
    """Expand a list of values into bound placeholders."""
    names = []
    params = {}
    for index, value in enumerate(values):
        name = "%s%d" % (prefix, index)
        names.append(":" + name)
        params[name] = value
    return ", ".join(names), params


def _mark_config_change(session, scope_type, scope_ids=None):
    """Queue the machines a gesture changes the configuration of."""
    if scope_type not in CONFIG_CHANGE_SCOPES:
        raise ValueError("Unknown configuration change scope: %s" % scope_type)
    if scope_type == 'all':
        ids = [None]
    else:
        if scope_ids is None or isinstance(scope_ids, (str, int)):
            scope_ids = [scope_ids]
        ids = []
        for raw in scope_ids:
            value = _to_int(raw, -1)
            if value >= 0 and value not in ids:
                ids.append(value)
    if not ids:
        return 0
    rows = []
    params = {'scope_type': scope_type}
    for index, value in enumerate(ids):
        rows.append("(:scope_type, :scope%d, NOW())" % index)
        params['scope%d' % index] = value
    session.execute(text(
        "INSERT INTO probe_config_changes (scope_type, scope_id, created_at) "
        "VALUES " + ", ".join(rows)), params)
    return len(ids)


def _mark_target_changes(session, targets):
    """Queue the targets of placements, as (target_type, target_id) pairs."""
    by_type = {}
    for target_type, target_id in targets:
        by_type.setdefault(target_type, []).append(target_id)
    return sum(_mark_config_change(session, target_type, ids)
               for target_type, ids in sorted(by_type.items()))


def parse_id_list(raw):
    """Accept a list, a tuple or a comma separated string of identifiers."""
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        candidates = list(raw)
    else:
        candidates = str(raw).split(',')
    out = []
    for item in candidates:
        value = _to_int(str(item).strip(), 0)
        if value > 0 and value not in out:
            out.append(value)
    return out


def parse_entity_list(raw):
    """Accept a list, a tuple or a comma separated string of entity ids."""
    if raw is None:
        return []
    if isinstance(raw, (list, tuple, set)):
        candidates = list(raw)
    else:
        candidates = str(raw).split(',')
    out = []
    for item in candidates:
        value = _to_int(str(item).strip(), -1)
        if value >= 0 and str(value) not in out:
            out.append(str(value))
    return out


def parse_period_bound(value, end_of_day=False):
    """Read one end of a period, or None when none was given."""
    if value is None:
        return None
    value = str(value).strip()
    if not value:
        return None

    for fmt in PERIOD_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    try:
        moment = datetime.strptime(value, PERIOD_DATE_FORMAT)
    except ValueError:
        raise ReflexValidationError(
            "A period bound is written YYYY-MM-DD or YYYY-MM-DD HH:MM:SS")
    if end_of_day:
        return moment.replace(hour=23, minute=59, second=59)
    return moment


def measure_window(days=7, hours=None):
    """Period a machine page asks for, as a duration."""
    hours = None if isinstance(hours, bool) else _to_int(hours, 0)
    if hours and 0 < hours <= MEASURE_WINDOW_MAX_HOURS:
        return timedelta(hours=hours)
    days = _to_int(days, 7)
    if days <= 0:
        days = 7
    return timedelta(days=min(days, 365))


def presence_segments(events, start, end, current_state=None):
    """Turn the presence events of a machine into the strip of its states."""
    segments = []
    state = None
    cursor = None
    for event in events:
        moment = event.get('moment')
        if moment is None:
            continue
        online = 1 if event.get('online') else 0
        if state is not None and cursor is not None:
            opened = cursor
            held = _to_int(event.get('held'), 0)
            if held > 0:
                accounted = moment - timedelta(seconds=held)
                if accounted > opened + timedelta(
                        seconds=PRESENCE_GAP_TOLERANCE_SECONDS):
                    opened = accounted
            if moment > opened:
                segments.append({'from': opened, 'to': moment,
                                 'online': state})
        state = online
        cursor = moment
    if (state is not None and cursor is not None and end > cursor
            and current_state is not None and current_state == state):
        segments.append({'from': cursor, 'to': end, 'online': state})

    kept = []
    for segment in segments:
        opened = max(segment['from'], start)
        closed = min(segment['to'], end)
        if closed <= opened:
            continue
        if (kept and kept[-1]['online'] == segment['online']
                and kept[-1]['to'] >= opened):
            kept[-1]['to'] = max(kept[-1]['to'], closed)
            continue
        kept.append({'from': opened, 'to': closed,
                     'online': segment['online']})
    return kept


def normalise_os_support(raw):
    """Keep only the operating systems the schema knows, in a stable order."""
    if isinstance(raw, (list, tuple)):
        candidates = list(raw)
    else:
        candidates = str(raw or '').split(',')
    selected = set()
    for item in candidates:
        item = str(item).strip().lower()
        if item in OPERATING_SYSTEMS:
            selected.add(item)
    if not selected:
        raise ReflexValidationError(
            "os_support must list at least one of: %s"
            % ", ".join(OPERATING_SYSTEMS),
            'os_support', RefusalReason.FIELD_REQUIRED)
    return ",".join([os_name for os_name in OPERATING_SYSTEMS
                     if os_name in selected])


def normalise_target_type(target_type):
    """Normalise the scope of an assignment to what the column accepts."""
    value = str(target_type or '').strip().lower()
    if value not in TARGET_TYPES:
        raise ReflexValidationError("Unknown target type: %s" % value,
                                    'target_type',
                                    RefusalReason.TARGET_TYPE_UNKNOWN)
    return value


def normalise_target_id(target_type, target_id):
    """Normalise one target identifier, for an already normalised type."""
    value = _clean_str(target_id, 255, 'target_id', required=True)
    number = _to_int(value, -1) if value.isdigit() else -1
    if number < 0:
        raise ReflexValidationError(
            "A target of type %s is named by its identifier: %s"
            % (target_type, value),
            'target_id', RefusalReason.FIELD_FORMAT_INVALID)
    return str(number)


def probe_visible_sql(entity_ids=None):
    """WHERE fragment selecting the probes a login may read."""
    clauses = ["p.visibility = 'global'",
               "(p.owner_login IS NOT NULL AND p.owner_login = :login)"]
    params = {}
    ids = parse_entity_list(entity_ids)
    if ids:
        fragment, params = _placeholders('vis', ids)
        clauses.append("(p.visibility = 'entity' AND p.entity_id IN (%s))"
                       % fragment)
    return "(" + " OR ".join(clauses) + ")", params


def channel_visible_sql(entity_ids=None):
    """WHERE fragment selecting the notification channels a login may read."""
    ids = parse_entity_list(entity_ids)
    if not ids:
        return "0", {}
    fragment, params = _placeholders('cvis', ids)
    return "(c.entity_id IN (%s))" % fragment, params


def membership_reach_sql(readable=True):
    """Placements on a group or an entity, resolved to the machines they
    reach.
    """
    if not readable:
        return ("SELECT CAST(NULL AS UNSIGNED) AS assignment_id, "
                "       CAST(NULL AS UNSIGNED) AS machines_id FROM DUAL WHERE 0")
    return ("SELECT rpa.id AS assignment_id, rxm.id AS machines_id "
            "  FROM probe_assignments rpa "
            "  JOIN dyngroup.Results rr "
            "    ON rr.FK_groups = CAST(rpa.target_id AS UNSIGNED) "
            "  JOIN dyngroup.Machines rdm ON rdm.id = rr.FK_machines "
            "  JOIN xmppmaster.machines rxm "
            "    ON rxm.uuid_inventorymachine = rdm.uuid "
            " WHERE rpa.target_type = 'group' "
            "   AND rr.FK_groups > 0 "
            "   AND rpa.target_id = CAST(rr.FK_groups AS CHAR) "
            "UNION "
            "SELECT rpa.id, rxm.id "
            "  FROM probe_assignments rpa "
            "  JOIN xmppmaster.glpi_entity re "
            "    ON re.glpi_id = CAST(rpa.target_id AS UNSIGNED) "
            "  JOIN xmppmaster.machines rxm ON rxm.glpi_entity_id = re.id "
            " WHERE rpa.target_type = 'entity' "
            # No lower bound on glpi_id: 0 is the root entity, not an absence.
            "   AND rpa.target_id <> '' "
            "   AND rpa.target_id = CAST(re.glpi_id AS CHAR)")


def machine_scope_sql(entity_ids, machine_ref, readable=True, prefix='mscope'):
    """WHERE fragment keeping a machine inside the estate a login reaches."""
    ids = parse_entity_list(entity_ids)
    if not readable or not ids:
        return "0", {}
    # Bound as numbers: parse_entity_list answers strings, the spelling
    # probes.entity_id and probe_assignments.target_id store, and the column
    # compared here is the integer glpi_entity.glpi_id.
    fragment, params = _placeholders(prefix, [int(value) for value in ids])
    return ("EXISTS (SELECT 1 FROM xmppmaster.machines sm "
            "          JOIN xmppmaster.glpi_entity se "
            "            ON se.id = sm.glpi_entity_id "
            "         WHERE sm.id = " + machine_ref +
            "           AND se.glpi_id IN (" + fragment + "))"), params


def machine_target_clauses(machines_id, group_ids=None, entity_ids=None,
                           machine_column=None, reach_sql=None):
    """SQL selecting the assignments that reach one machine."""
    if machine_column is not None:
        if group_ids or entity_ids:
            raise ValueError("memberships belong to one machine")
        params = {}
        fragment = ("((pa.target_type = 'machine' "
                    "AND pa.target_id = CAST(%s AS CHAR))" % machine_column)
        if reach_sql:
            fragment += (" OR (pa.target_type IN ('group', 'entity') "
                         "AND EXISTS (SELECT 1 FROM (" + reach_sql + ") rc "
                         "WHERE rc.assignment_id = pa.id "
                         "AND rc.machines_id = " + machine_column + "))")
        return fragment + ")", params
    machines_id = _to_int(machines_id, 0)
    params = {'machines_id': machines_id, 'machines_text': str(machines_id)}
    clauses = ["(pa.target_type = 'machine' AND pa.target_id = :machines_text)"]

    # The two target types below are literals of ours, never caller input; the
    # identifiers they are compared to stay bound placeholders.
    for target_type, prefix, raw_ids in (('group', 'grp', group_ids),
                                         ('entity', 'ent', entity_ids)):
        # Entities are read with their own parser: 0 is the root entity of GLPI
        # and the only one an estate that never split has, so it must survive
        # here, where parse_id_list drops it as it drops a group 0 that cannot
        # exist.
        if target_type == 'entity':
            ids = parse_entity_list(raw_ids)
        else:
            ids = [str(value) for value in parse_id_list(raw_ids)]
        if not ids:
            continue
        fragment, id_params = _placeholders(prefix, ids)
        params.update(id_params)
        clauses.append("(pa.target_type = '%s' AND pa.target_id IN (%s))"
                       % (target_type, fragment))
    return "(" + " OR ".join(clauses) + ")", params


def group_shared_sql(group_ref):
    """WHERE fragment keeping the groups of dyngroup a login is given."""
    return ("(EXISTS (SELECT 1 FROM dyngroup.Groups dg "
            "           JOIN dyngroup.Users du ON du.id = dg.FK_users "
            "          WHERE dg.id = " + group_ref +
            "            AND du.login = :login) "
            " OR EXISTS (SELECT 1 FROM dyngroup.ShareGroup ds "
            "              JOIN dyngroup.Users dsu ON dsu.id = ds.FK_users "
            "             WHERE ds.FK_groups = " + group_ref +
            "               AND dsu.type = 0 "
            "               AND dsu.login = :login))")


def assignment_visible_sql(entity_ids, readable=True, groups_readable=True,
                           prefix='avis'):
    """WHERE fragment keeping the placements a login may read."""
    machine_sql, params = machine_scope_sql(
        entity_ids, "CAST(pa.target_id AS UNSIGNED)", readable=readable,
        prefix=prefix + 'm')

    clauses = [
        "(pa.created_by IS NOT NULL AND pa.created_by = :login)",
        "(pa.target_type = 'machine' AND " + machine_sql + ")",
    ]

    ids = parse_entity_list(entity_ids)
    if ids:
        fragment, entity_params = _placeholders(prefix + 'e', ids)
        params.update(entity_params)
        clauses.append("(pa.target_type = 'entity' AND pa.target_id IN (%s))"
                       % fragment)

    if groups_readable:
        # target_id is compared as a number here and not as text: it names
        # dyngroup.Groups.id, an integer column.
        clauses.append(
            "(pa.target_type = 'group' AND "
            + group_shared_sql("CAST(pa.target_id AS UNSIGNED)") + ")")

    return "(" + " OR ".join(clauses) + ")", params


def assignment_reaches_estate_sql(entity_ids):
    """WHERE fragment keeping the placements that reach a machine of an
    estate.
    """
    params = {}

    def reached(machine_ref, key):
        scope_sql, scope_params = machine_scope_sql(
            entity_ids, machine_ref, prefix='reach' + key)
        params.update(scope_params)
        return (scope_sql +
                " AND NOT EXISTS (SELECT 1 FROM probe_exclusions rpx "
                "                  WHERE rpx.probe_id = pa.probe_id "
                "                    AND rpx.machines_id = " + machine_ref + ")")

    machine_sql = reached("CAST(pa.target_id AS UNSIGNED)", 'm')
    member_sql = reached('rrc.machines_id', 'g')
    return ("((pa.target_type = 'machine' AND " + machine_sql + ") "
            " OR (pa.target_type IN ('group', 'entity') "
            "     AND EXISTS (SELECT 1 FROM (" + membership_reach_sql() + ") rrc "
            "                  WHERE rrc.assignment_id = pa.id "
            "                    AND " + member_sql + ")))"), params


def probe_measured_sql():
    """1 when a probe is measured by an agent, 0 when the server decides it."""
    return ("EXISTS (SELECT 1 FROM probe_collectors pcol "
            "         WHERE pcol.probe_id = p.id)")


def machine_os_sql(machine_ref):
    """Operating system of a machine, spelled as probe_collectors.os does."""
    return ("(SELECT CASE "
            "          WHEN LOCATE('windows', LOWER(xos.platform)) > 0 "
            "               THEN 'windows' "
            "          WHEN LOCATE('darwin', LOWER(xos.platform)) > 0 "
            "               OR LOCATE('mac', LOWER(xos.platform)) > 0 "
            "               THEN 'darwin' "
            "          WHEN LOCATE('linux', LOWER(xos.platform)) > 0 "
            "               THEN 'linux' "
            "          ELSE NULL END "
            "   FROM xmppmaster.machines xos "
            "  WHERE xos.id = " + machine_ref + ")")


def probe_distributable_sql(os_expr, alias='p'):
    """1 when the agent of a machine can be asked to measure a probe."""
    return ("EXISTS (SELECT 1 FROM probe_collectors pcol "
            "         WHERE pcol.probe_id = %(p)s.id "
            "           AND pcol.enabled = 1 "
            "           AND pcol.os = COALESCE(%(os)s, pcol.os))"
            % {'p': alias or 'p', 'os': os_expr})


def machine_placements_sql(target_fragment, visible_sql, machine_ref):
    """FROM and WHERE of the probes placed on a machine, as a reader sees
    them.
    """
    return ("  FROM probe_assignments pa "
            "  JOIN probes p ON p.id = pa.probe_id "
            "  LEFT JOIN probe_exclusions px ON px.probe_id = p.id "
            "        AND px.machines_id = " + machine_ref +
            " WHERE " + target_fragment +
            "   AND " + visible_sql)


def placed_probes_count_sql(target_fragment, visible_sql, machine_ref):
    """Number of probes placed on a machine and not excepted there."""
    return ("(SELECT COUNT(DISTINCT pa.probe_id)"
            + machine_placements_sql(target_fragment, visible_sql, machine_ref)
            + " AND px.id IS NULL)")


def placed_cadence_sql(target_fragment, visible_sql, machine_ref):
    """Cadence a machine owes a report at, read on its placements."""
    return ("(SELECT MIN(pa.interval_seconds)"
            + machine_placements_sql(target_fragment, visible_sql, machine_ref)
            + " AND p.enabled = 1 AND px.id IS NULL"
            " AND " + probe_measured_sql() +
            " AND pa.interval_seconds > 0)")


def probe_last_received_sql(machine_ref):
    """Last received_at of one probe on one machine, without a time bound.

    ORDER BY and LIMIT rather than MAX: correlated, MAX walks the whole
    history of the probe in the index.
    """
    return ("(SELECT lm.received_at FROM probe_measures lm "
            "  WHERE lm.machines_id = " + machine_ref +
            "    AND lm.probe_id = p.id"
            "  ORDER BY lm.received_at DESC LIMIT 1)")


def machine_last_received_sql(visible_sql, machine_ref):
    """Last report of a machine over the probes a reader sees, however old."""
    return ("(SELECT " + probe_last_received_sql(machine_ref) +
            " AS last_received "
            "   FROM probes p WHERE " + visible_sql +
            "    AND " + probe_measured_sql() +
            "  ORDER BY last_received DESC LIMIT 1)")


def config_stale_sql(target_fragment, machine_ref, os_readable=True):
    """1 when a change reaching a machine is not distributed to it yet."""
    machine_os = machine_os_sql(machine_ref) if os_readable else 'NULL'
    sent_at = ("(SELECT pac.sent_at FROM probe_agent_config pac "
               "  WHERE pac.machines_id = " + machine_ref + ")")
    effective = ("(SELECT COUNT(DISTINCT pa.probe_id) "
                 "   FROM probe_assignments pa "
                 "   JOIN probes ap ON ap.id = pa.probe_id "
                 "  WHERE ap.enabled = 1 "
                 "    AND " + probe_distributable_sql(machine_os, 'ap') +
                 "    AND " + target_fragment +
                 "    AND NOT EXISTS (SELECT 1 FROM probe_exclusions px2 "
                 "                     WHERE px2.probe_id = pa.probe_id "
                 "                       AND px2.machines_id = "
                 + machine_ref + "))")
    return ("(CASE WHEN " + sent_at + " IS NULL "
            "      THEN CASE WHEN " + effective + " > 0 THEN 1 ELSE 0 END "
            "      WHEN (SELECT MAX(pa.created_at) FROM probe_assignments pa "
            "             WHERE " + target_fragment + ") > " + sent_at +
            "      THEN 1 "
            "      WHEN (SELECT MAX(px.created_at) FROM probe_exclusions px "
            "             WHERE px.machines_id = " + machine_ref + ") > "
            + sent_at +
            "      THEN 1 "
            "      WHEN " + effective + " <> COALESCE("
            "           (SELECT pac.probe_count FROM probe_agent_config pac "
            "             WHERE pac.machines_id = " + machine_ref + "), 0) "
            "      THEN 1 "
            "      ELSE 0 END)")


def collapse_assignments(rows):
    """One line per probe out of the assignments that reach a machine."""
    best = {}
    order = []
    for row in rows:
        probe_id = _to_int(row.get('probe_id'), 0)
        if probe_id not in best:
            best[probe_id] = dict(row)
            best[probe_id]['origins'] = []
            order.append(probe_id)
        kept = best[probe_id]
        target_type = str(row.get('target_type') or '')
        if target_type and target_type not in kept['origins']:
            kept['origins'].append(target_type)
        if _governs(row, kept):
            origins = kept['origins']
            best[probe_id] = dict(row)
            best[probe_id]['origins'] = origins
    return [best[probe_id] for probe_id in order]


def _governs(candidate, current):
    """Tell whether an assignment rules over another one for a machine."""
    def rank(row):
        return (_to_int(row.get('interval_seconds'), 0) or 2 ** 31,
                TARGET_SPECIFICITY.get(str(row.get('target_type') or ''), 9),
                _to_int(row.get('assignment_id'), 0))
    return rank(candidate) < rank(current)


# Where a probe is actually placed, as three figures the console turns into a
# sentence in its own language.
ASSIGNMENT_SUMMARY_FIELDS = ('assigned_machines', 'assigned_groups',
                             'assigned_entities')

# Target type of an assignment to the field that counts it.
ASSIGNMENT_SUMMARY_BY_TARGET = {'machine': 'assigned_machines',
                                'group': 'assigned_groups',
                                'entity': 'assigned_entities'}


def summarise_assignments(rows):
    """Count the assignments of a probe, by target type."""
    summary = dict((field, 0) for field in ASSIGNMENT_SUMMARY_FIELDS)
    for row in rows or []:
        field = ASSIGNMENT_SUMMARY_BY_TARGET.get(
            str(row.get('target_type') or ''))
        if field is not None:
            summary[field] += 1
    return summary


def drop_deleted_targets(rows):
    """The placements whose target still exists, the others being gone."""
    return [row for row in rows or []
            if str(row.get('target_state') or '') != TARGET_STATE_DELETED]


def silence_after_seconds(interval_seconds, fallback_seconds):
    """How long a report may be missing before it stops describing the
    present.
    """
    interval = _to_int(interval_seconds, 0)
    if interval > 0:
        return SILENCE_MISSED_REPORTS * interval + SILENCE_GRACE_SECONDS
    return max(_to_int(fallback_seconds, 0), 1)


def condition_override_join_sql(param, override_alias='pco',
                                entity_ref=None):
    """LEFT JOIN bringing the settings of one estate over a condition."""
    reference = entity_ref if entity_ref else (":" + str(param))
    return (" LEFT JOIN probe_condition_overrides " + override_alias +
            " ON " + override_alias + ".condition_id = pc.id "
            " AND " + override_alias + ".entity_id = " + reference + " ")


def condition_field_sql(field, alias='pc', override_alias=None):
    """Effective value of one condition field, at the level that supplies it.
    """
    if not override_alias:
        return "%s.default_%s" % (alias, field)
    return "COALESCE(%s.%s, %s.default_%s)" % (override_alias, field,
                                               alias, field)


def condition_effective_sql(alias='pc', override_alias=None):
    """SELECT fragment reading a condition as it actually applies."""
    return ", ".join(
        "%s AS %s" % (condition_field_sql(field, alias, override_alias), field)
        for field in CONDITION_OVERRIDE_FIELDS)


def condition_default_sql():
    """SELECT fragment reading what the product ships for a condition."""
    return ", ".join("pc.default_%s" % field
                     for field in CONDITION_OVERRIDE_FIELDS)


def condition_customized_sql(override_alias=None):
    """SELECT fragment telling whether the condition the reader sees was
    moved.
    """
    if not override_alias:
        return "0"
    return ("CASE WHEN "
            + " OR ".join("%s.%s IS NOT NULL" % (override_alias, field)
                          for field in CONDITION_OVERRIDE_FIELDS)
            + " THEN 1 ELSE 0 END")


def condition_trace_sql(field, override_alias=None):
    """Who moved the condition the reader sees, and when."""
    if not override_alias:
        return "NULL"
    return "%s.%s" % (override_alias, field)


def severity_rank_sql(alias='a'):
    """Rank of alias.severity, 1 for the mildest up to the most serious."""
    return "FIELD(%s.severity, %s)" % (
        alias, ", ".join("'%s'" % severity for severity in SEVERITIES))


def alert_order_sql(sort):
    """ORDER BY expression of get_alerts for `sort`, total and stable."""
    recent = "a.opened_at DESC, a.id DESC"
    if str(sort or '').strip().lower() == ALERT_SORT_RECENT:
        return recent + " "
    return "%s DESC, %s " % (severity_rank_sql('a'), recent)


def alert_active_sql(alias='a'):
    """WHERE fragment selecting the alerts that still stand."""
    prefix = ("%s." % alias) if alias else ""
    return "%sstatus IN (%s)" % (
        prefix, ", ".join("'%s'" % status for status in ALERT_ACTIVE_STATUSES))


def measure_instance(measure, value_type=None):
    """What a measure was taken on, None when the probe reports one value."""
    value_type = str(value_type if value_type is not None
                     else measure.get('value_type') or 'numeric').strip().lower()
    if value_type == 'text':
        # A text probe reporting several instances would have nowhere to put
        # their names, and nothing here could tell them apart.
        return None
    value_text = measure.get('value_text')
    if value_text is None:
        return None
    value_text = str(value_text).strip()
    return value_text or None


def alert_instance(alert):
    """What one alert was raised on, None when the probe reports one value."""
    return measure_instance({'value_text': alert.get('value_text_at_trigger')},
                            alert.get('value_type'))


def annotate_alert_instances(rows):
    """Give every alert row the instance it was raised on, and drop the rest.
    """
    for row in rows or []:
        row['instance'] = alert_instance(row) or ''
        row.pop('value_type', None)
    return rows


# Whether anybody was told about an alert, read off notification_history.
NOTIFICATION_STATE_SENT = 'sent'
NOTIFICATION_STATE_PENDING = 'pending'
NOTIFICATION_STATE_FAILED = 'failed'
NOTIFICATION_STATE_NONE = 'none'


def notification_state(lines):
    """State and reason of the notification of one alert."""
    sent = pending = failed = False
    reasons = {}
    for line in lines:
        status = str(line.get('status') or '')
        if status == 'sent':
            sent = True
        elif status == 'pending' or (status == 'failed'
                                     and _to_int(line.get('retrying'), 0)):
            pending = True
        elif status == 'failed':
            failed = True
        elif status == 'skipped':
            key = str(line.get('skip_reason') or '')
            count, last = reasons.get(key, (0, 0))
            reasons[key] = (count + _to_int(line.get('line_count'), 0),
                            max(last, _to_int(line.get('last_id'), 0)))
    if sent:
        return NOTIFICATION_STATE_SENT, ''
    if pending:
        return NOTIFICATION_STATE_PENDING, ''
    if failed:
        return NOTIFICATION_STATE_FAILED, ''
    if not reasons:
        return NOTIFICATION_STATE_NONE, ''
    return NOTIFICATION_STATE_NONE, max(reasons.items(),
                                        key=lambda item: item[1])[0]


def retention_days(value):
    """A retention sent by the console as an int, None when it is not one."""
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return value
    if isinstance(value, str) and re.match(r'^\s*[-+]?\d+\s*$', value):
        return int(value)
    return None


def condition_holds_now(condition, value_num, value_text):
    """Whether one measure, read alone, satisfies one condition."""
    operator = str(condition.get('operator') or '').strip().lower()
    if not operator or operator in THRESHOLDLESS_OPERATORS:
        return None

    try:
        threshold = _to_float(condition.get('threshold_value'))
        threshold2 = _to_float(condition.get('threshold_value2'))
    except ReflexValidationError:
        # A threshold the column holds but no number can read decides nothing.
        return None
    threshold_text = condition.get('threshold_text')

    if operator in ('eq', 'ne') and threshold_text not in (None, ''):
        if value_text is None:
            return None
        equal = str(value_text).strip() == str(threshold_text).strip()
        return equal if operator == 'eq' else not equal

    try:
        value_num = _to_float(value_num)
    except ReflexValidationError:
        return None
    if value_num is None:
        return None

    if operator in RANGE_OPERATORS:
        if threshold is None or threshold2 is None:
            return None
        if operator == 'between':
            return threshold <= value_num <= threshold2
        return value_num < threshold or value_num > threshold2

    # A comparison without a bound is false and not unknown, exactly as the
    # substitute reads it: such a row should not exist, validate_condition
    # refuses it, and if one ever did no alert would come from it either.
    if operator == 'gt':
        return threshold is not None and value_num > threshold
    if operator == 'gte':
        return threshold is not None and value_num >= threshold
    if operator == 'lt':
        return threshold is not None and value_num < threshold
    if operator == 'lte':
        return threshold is not None and value_num <= threshold
    if operator == 'eq':
        return threshold is not None and value_num == threshold
    if operator == 'ne':
        return threshold is not None and value_num != threshold
    return None


def alert_frozen_condition(alert):
    """The condition an alert froze when it was raised, {} when it froze none.
    """
    alert = alert or {}
    operator = str(alert.get('operator_at_trigger') or '').strip().lower()
    if not operator:
        return {}
    frozen = dict((key, alert.get(column))
                  for column, key in ALERT_FREEZE_FIELDS)
    frozen['operator'] = operator
    frozen['severity'] = str(alert.get('severity') or '').strip().lower()
    return frozen


def _same_setting(left, right):
    """Whether two settings of a condition say the same thing."""
    left_absent = left is None or str(left).strip() == ''
    right_absent = right is None or str(right).strip() == ''
    if left_absent or right_absent:
        return left_absent and right_absent
    try:
        return float(_to_float(left)) == float(_to_float(right))
    except (ReflexValidationError, TypeError, ValueError):
        return str(left).strip().lower() == str(right).strip().lower()


def condition_moved_fields(frozen, condition):
    """Settings of a condition that read differently today than when it fired.
    """
    if not frozen or not condition:
        return []
    return [key for _column, key in ALERT_FREEZE_FIELDS
            if not _same_setting(frozen.get(key), condition.get(key))]


def alert_condition_trust(alert, condition, value_type=None,
                          probe_updated_at=None, frozen=None):
    """Whether the condition shown next to an alert may be taken for its
    cause.
    """
    alert = alert or {}
    condition = condition or {}
    frozen = frozen or {}

    severity_at_trigger = str(alert.get('severity') or '').strip().lower()
    trust = {
        'status': ConditionTrust.GONE,
        'certified': 0,
        'condition_frozen': 1 if frozen else 0,
        'condition_moved_fields': [],
        'changed_since_opened': 0,
        'evidence': [],
        'severity_at_trigger': severity_at_trigger,
        'severity_now': '',
        'severity_moved': 0,
        'trigger_value_holds_now': None,
        'customized_at': '',
        'customized_by': '',
    }
    # Nothing to show as the cause and nothing to qualify: the condition row is
    # gone and the alert froze none.
    if not condition and not frozen:
        return trust

    trust['status'] = ConditionTrust.CERTIFIED if frozen \
        else ConditionTrust.UNVERIFIED
    trust['certified'] = 1 if frozen else 0
    trust['customized_at'] = condition.get('customized_at') or ''
    trust['customized_by'] = condition.get('customized_by') or ''

    evidence = []
    severity_now = str(condition.get('severity') or '').strip().lower()
    trust['severity_now'] = severity_now
    if severity_now and severity_at_trigger and severity_now != severity_at_trigger:
        trust['severity_moved'] = 1
        evidence.append(ConditionEvidence.SEVERITY_MOVED)

    # The rule of alert_instance, applied here rather than restated: on a
    # numeric or a boolean probe value_text_at_trigger names a mount point
    # and comparing a threshold to it would compare a threshold to "/home".
    value_text = None
    if str(value_type or '').strip().lower() == 'text':
        value_text = alert.get('value_text_at_trigger')
    holds = condition_holds_now(condition, alert.get('value_at_trigger'),
                                value_text)
    # 1, 0 or None, the shape every tri-state of this module travels in -- see
    # the `breaching` key of the machine sheet.
    trust['trigger_value_holds_now'] = None if holds is None else \
        (1 if holds else 0)
    if holds is False:
        evidence.append(ConditionEvidence.TRIGGER_VALUE_UNSATISFIED)

    if 'enabled' in condition and not _to_int(condition.get('enabled'), 0):
        evidence.append(ConditionEvidence.CONDITION_DISABLED_NOW)

    opened_at = _read_moment(alert.get('opened_at'))
    customized_at = _read_moment(condition.get('customized_at'))
    if opened_at is not None and customized_at is not None \
            and customized_at > opened_at:
        evidence.append(ConditionEvidence.CUSTOMIZED_AFTER_OPEN)

    probe_updated_at = _read_moment(probe_updated_at)
    if opened_at is not None and probe_updated_at is not None \
            and probe_updated_at > opened_at:
        evidence.append(ConditionEvidence.PROBE_EDITED_AFTER_OPEN)

    # Only an alert that froze its condition has two settings to compare;
    # condition_moved_fields answers nothing on the others rather than report
    # every column as moved, and the deletion of a condition nobody can show
    # is already the whole answer -- the GONE status above.
    moved = condition_moved_fields(frozen, condition)
    trust['condition_moved_fields'] = moved
    if moved:
        evidence.append(ConditionEvidence.CONDITION_MOVED)
    if frozen and not condition:
        evidence.append(ConditionEvidence.CONDITION_DELETED_NOW)

    trust['evidence'] = evidence
    if frozen:
        # Nothing downgrades a certified alert: what is displayed as its cause
        # IS the condition that fired, whatever became of the row since.
        proven = [key for key in evidence if key in CERTIFIED_PROOFS]
    else:
        proven = [key for key in evidence
                  if key != ConditionEvidence.PROBE_EDITED_AFTER_OPEN]
        if ConditionEvidence.TRIGGER_VALUE_UNSATISFIED in evidence:
            # Named apart from a plain change: a severity that moved still
            # leaves a readable explanation, a threshold the triggering value
            # does not cross leaves a contradiction on screen.
            trust['status'] = ConditionTrust.CONTRADICTED
        elif proven:
            trust['status'] = ConditionTrust.CHANGED
    trust['changed_since_opened'] = 1 if proven else 0
    return trust


def validate_condition(condition, value_type):
    """Check a condition against the value type of its probe."""
    if not isinstance(condition, dict):
        raise ReflexValidationError("A condition must be a structure", None,
                                    RefusalReason.PAYLOAD_MALFORMED)

    value_type = str(value_type or 'numeric').lower()
    if value_type not in VALUE_TYPES:
        raise ReflexValidationError("Unknown value type: %s" % value_type,
                                    'value_type',
                                    RefusalReason.VALUE_TYPE_UNKNOWN)

    operator = str(condition.get('operator', '')).strip().lower()
    if operator not in OPERATORS:
        raise ReflexValidationError("Unknown operator: %s" % operator,
                                    'operator',
                                    RefusalReason.OPERATOR_UNKNOWN)
    if operator not in OPERATORS_BY_VALUE_TYPE[value_type]:
        raise ReflexValidationError(
            "Operator %s is not applicable to a %s probe" % (operator, value_type),
            'operator', RefusalReason.OPERATOR_NOT_APPLICABLE)

    severity = str(condition.get('severity', 'medium')).strip().lower()
    if severity not in SEVERITIES:
        raise ReflexValidationError("Unknown severity: %s" % severity,
                                    'severity',
                                    RefusalReason.SEVERITY_UNKNOWN)

    duration = _to_int(condition.get('duration_seconds', 0), -1)
    if duration < 0:
        raise ReflexValidationError("The duration must not be negative",
                                    'duration_seconds',
                                    RefusalReason.DURATION_NEGATIVE)

    threshold_value = _to_whole(condition.get('threshold_value'),
                                'threshold_value')
    threshold_value2 = _to_whole(condition.get('threshold_value2'),
                                 'threshold_value2')
    threshold_text = _clean_str(condition.get('threshold_text'), 255,
                                'threshold_text')

    # A second bound only means something for a range.
    if operator not in RANGE_OPERATORS and threshold_value2 is not None:
        raise ReflexValidationError(
            "A second bound is only accepted by the between and outside operators",
            'threshold_value2', RefusalReason.SECOND_BOUND_NOT_ALLOWED)

    if operator in RANGE_OPERATORS:
        if threshold_value is None or threshold_value2 is None:
            raise ReflexValidationError(
                "The %s operator needs both bounds" % operator,
                'threshold_value' if threshold_value is None
                else 'threshold_value2',
                RefusalReason.RANGE_BOUNDS_REQUIRED)
        if threshold_value2 <= threshold_value:
            raise ReflexValidationError(
                "The upper bound must be greater than the lower one",
                'threshold_value2', RefusalReason.RANGE_BOUNDS_ORDER)
        if threshold_text is not None:
            raise ReflexValidationError(
                "A range compares numbers, not text", 'threshold_text',
                RefusalReason.THRESHOLD_TEXT_NOT_ALLOWED)
    elif operator in THRESHOLDLESS_OPERATORS:
        # A change is observed, it is not compared to anything.
        if threshold_value is not None or threshold_text is not None:
            raise ReflexValidationError(
                "The %s operator takes no threshold" % operator,
                'threshold_value' if threshold_value is not None
                else 'threshold_text',
                RefusalReason.THRESHOLD_NOT_ALLOWED)
    else:
        if value_type == 'text':
            if threshold_text is None:
                raise ReflexValidationError(
                    "A text probe is compared to a text threshold",
                    'threshold_text', RefusalReason.THRESHOLD_TEXT_REQUIRED)
            threshold_value = None
        elif value_type == 'boolean':
            if threshold_text is not None:
                raise ReflexValidationError(
                    "A boolean probe is compared to 0 or 1", 'threshold_text',
                    RefusalReason.THRESHOLD_BOOLEAN_EXPECTED)
            if threshold_value is None or threshold_value not in (0.0, 1.0):
                raise ReflexValidationError(
                    "A boolean threshold is 0 or 1", 'threshold_value',
                    RefusalReason.THRESHOLD_BOOLEAN_EXPECTED)
        else:
            if threshold_value is None:
                raise ReflexValidationError(
                    "A numeric probe needs a numeric threshold",
                    'threshold_value', RefusalReason.THRESHOLD_REQUIRED)
            threshold_text = None

    return {
        'operator': operator,
        'threshold_value': threshold_value,
        'threshold_value2': threshold_value2,
        'threshold_text': threshold_text,
        'duration_seconds': duration,
        'severity': severity,
        'message_template': _clean_str(condition.get('message_template'), 512,
                                       'message_template'),
        'enabled': _to_bool_int(condition.get('enabled', 1)),
        'display_order': _to_int(condition.get('display_order', 0), 0),
    }


def validate_condition_set(conditions, value_type):
    """Check a whole set of conditions against the value type of its probe."""
    if conditions is None:
        conditions = []
    if isinstance(conditions, dict):
        conditions = [conditions]
    if not isinstance(conditions, (list, tuple)):
        raise ReflexValidationError("The conditions must be a list", None,
                                    RefusalReason.PAYLOAD_MALFORMED)

    prepared = []
    for index, condition in enumerate(conditions):
        try:
            clean = validate_condition(condition, value_type)
        except ReflexValidationError as e:
            e.condition = index + 1
            raise
        # Order is rewritten so the unique key never collides on a payload
        # that repeats a rank.
        clean['display_order'] = (index + 1) * 10
        clean['condition_id'] = _to_int(condition.get('id'), 0)
        prepared.append(clean)
    return prepared


def validate_condition_override(row, overrides, value_type):
    """Check an override against the condition it modifies."""
    if overrides is None:
        overrides = {}
    # An override carrying nothing is the reset, and a caller that spells an
    # empty structure as an empty list is spelling that same nothing: PHP has
    # one array type and its XML-RPC bridge writes an empty one as <array>,
    # never as <struct>.
    if isinstance(overrides, (list, tuple)) and not overrides:
        overrides = {}
    if not isinstance(overrides, dict):
        raise ReflexValidationError("An override must be a structure", None,
                                    RefusalReason.PAYLOAD_MALFORMED)

    unknown = [str(key) for key in overrides
               if key not in CONDITION_OVERRIDE_FIELDS]
    if unknown:
        raise ReflexValidationError(
            "These fields cannot be overridden: %s" % ", ".join(sorted(unknown)),
            sorted(unknown)[0], RefusalReason.FIELD_NOT_OVERRIDABLE)

    # operator and display_order are read from the row: they are not
    # overridable, and the coherence of the thresholds is judged against them.
    candidate = {'operator': row.get('operator'),
                 'display_order': row.get('display_order')}
    for field in CONDITION_OVERRIDE_FIELDS:
        candidate[field] = (overrides[field] if field in overrides
                            else row.get('default_%s' % field))

    clean = validate_condition(candidate, value_type)
    return dict((field, clean[field] if field in overrides else None)
                for field in CONDITION_OVERRIDE_FIELDS)


RECIPIENT_ADDRESS_RE = re.compile(r'^[^@\s,;]+@[^@\s,;]+\.[^@\s,;]+$')
RECIPIENT_ADDRESS_MAX_LENGTH = 254
RECIPIENTS_SPLIT_RE = re.compile(r'[,;\r\n]+')
# The senders split on commas and semicolons only, never on line breaks.
RECIPIENTS_SEPARATOR = ', '
# Recipient keys a channel config used to carry.
CHANNEL_RECIPIENT_KEYS = ('recipients', 'to')


def normalise_recipients(raw, field='recipients'):
    """Recipient addresses of a rule, checked and normalised."""
    if raw is None:
        return ''
    pieces = raw if isinstance(raw, (list, tuple)) else [raw]
    kept, seen, invalid = [], set(), []
    for piece in pieces:
        for address in RECIPIENTS_SPLIT_RE.split(str(piece)):
            address = address.strip()
            if not address:
                continue
            if (len(address) > RECIPIENT_ADDRESS_MAX_LENGTH
                    or not RECIPIENT_ADDRESS_RE.match(address)):
                if address not in invalid:
                    invalid.append(address)
                continue
            if address.lower() in seen:
                continue
            seen.add(address.lower())
            kept.append(address)
    if invalid:
        raise ReflexValidationError(
            "Invalid recipient address: %s" % ", ".join(invalid), field,
            RefusalReason.EMAIL_INVALID, details=invalid)
    return RECIPIENTS_SEPARATOR.join(kept)


def validate_config_json(raw):
    """Accept a JSON object of non sensitive parameters, or nothing."""
    if raw is None:
        return None
    if isinstance(raw, dict):
        parsed = raw
    else:
        raw = str(raw).strip()
        if not raw:
            return None
        try:
            parsed = json.loads(raw)
        except ValueError:
            raise ReflexValidationError(
                "The channel parameters must be valid JSON", 'config_json',
                RefusalReason.CONFIG_JSON_INVALID)
    if not isinstance(parsed, dict):
        raise ReflexValidationError(
            "The channel parameters must be a JSON object", 'config_json',
            RefusalReason.CONFIG_JSON_INVALID)
    for key in parsed:
        lowered = str(key).lower()
        for forbidden in SECRET_LIKE_KEYS:
            if forbidden in lowered:
                raise ReflexValidationError(
                    "The parameter '%s' looks like a secret: send it as "
                    "smtp_password, it will be ciphered" % key, 'config_json',
                    RefusalReason.CONFIG_JSON_SECRET)
    for key in CHANNEL_RECIPIENT_KEYS:
        parsed.pop(key, None)
    return json.dumps(parsed, sort_keys=True)


def channel_config_for_reading(raw):
    """config_json of a stored channel, without the recipient keys."""
    if not raw:
        return raw
    try:
        parsed = json.loads(raw)
    except (TypeError, ValueError):
        return raw
    if not isinstance(parsed, dict):
        return raw
    if not any(key in parsed for key in CHANNEL_RECIPIENT_KEYS):
        return raw
    for key in CHANNEL_RECIPIENT_KEYS:
        parsed.pop(key, None)
    return json.dumps(parsed, sort_keys=True)


def coerce_setting(raw, value_type):
    """Turn a stored setting into the type it declares."""
    if raw is None:
        return None
    if value_type == 'int':
        try:
            return int(str(raw).strip())
        except (TypeError, ValueError):
            return None
    if value_type == 'bool':
        if isinstance(raw, bool):
            return raw
        spelling = str(raw).strip().lower()
        if spelling in ('1', 'true', 'yes', 'on'):
            return True
        if spelling in ('0', 'false', 'no', 'off'):
            return False
        return None
    value = str(raw).strip()
    return value or None


def readable_console_url(raw):
    """The console address as it may be written into a link, '' when there is
    none that may.
    """
    value = ('' if raw is None else str(raw)).strip()
    if not value or len(value) > CONSOLE_URL_MAX_LENGTH:
        return ''
    if any(char in value for char in CONSOLE_URL_FORBIDDEN_CHARS):
        return ''
    if any(ord(char) < 0x20 or ord(char) == 0x7f for char in value):
        return ''
    try:
        parts = urlsplit(value)
        # urlsplit parses the port only when the port is read: a host written
        # "server:notaport" splits perfectly until somebody looks at it, and
        # looking at it here is the check.
        parts.port
    except ValueError:
        return ''
    if parts.scheme not in ('http', 'https'):
        return ''
    if not parts.netloc or '@' in parts.netloc:
        return ''
    if parts.query or parts.fragment:
        return ''
    return value.rstrip('/')


def publishable_console_host(raw):
    """The value as a host somebody else may reach, '' when it is not one."""
    value = ('' if raw is None else str(raw)).strip().rstrip('.')
    if not value or len(value) > CONSOLE_URL_MAX_LENGTH:
        return ''
    if not CONSOLE_HOST_ALLOWED_RE.match(value):
        return ''
    if value.lower() in CONSOLE_HOST_REFUSED_NAMES:
        return ''

    try:
        address = ipaddress.ip_address(value)
    except ValueError:
        address = None
    if address is not None:
        if (address.is_loopback or address.is_unspecified
                or address.is_link_local or address.is_multicast
                or address.is_reserved):
            return ''
        return value

    if '.' not in value:
        return ''
    # An empty label -- "srv..example" -- or one that starts or ends with a
    # dash is not a name; the regexp above only guards the ends of the whole
    # string.
    for label in value.split('.'):
        if not label or label.startswith('-') or label.endswith('-'):
            return ''
    return value


def mmc_ini_server_name():
    """[server_01] description of mmc.ini, '' when there is nothing usable."""
    try:
        parser = ConfigParser()
        if not parser.read(list(MMC_INI_PATHS)):
            return ''
        return (parser.get(MMC_INI_SERVER_SECTION, MMC_INI_SERVER_NAME_KEY,
                           fallback='') or '').strip()
    except Exception as e:
        logger.debug("Reflex: %s could not be read for the console address "
                     "(%s)" % (MMC_INI_PATH, e))
        return ''


def derive_console_url():
    """Console address deduced from mmc.ini, '' when nothing usable comes out.
    """
    host = publishable_console_host(mmc_ini_server_name())
    if not host:
        return ''
    return readable_console_url('%s://%s'
                                % (CONSOLE_URL_DERIVED_SCHEME, host))


class _GlpiConnection(DatabaseHelper):
    """Connection path of GLPI, built the way every plugin of Medulla builds
    it.
    """
    my_name = "Glpi"


class ReflexDatabase(DatabaseHelper):
    """Singleton class to query the reflex database."""
    is_activated = False
    session = None
    # Settings cache, class level like the singleton itself: the console API
    # and the master substitute running in the same process read the same
    # values, and refresh them at most once every SETTINGS_CACHE_TTL_SECONDS.
    _settings_cache = None
    _settings_cache_at = 0.0
    # Address deduced from mmc.ini, cached on the same clock and the same
    # lifetime as the settings above: this value is read on every notification,
    # and opening /etc/mmc/mmc.ini each time a mail goes out is not a price a
    # supervision module pays for a link.
    _derived_url = None
    _derived_url_at = 0.0
    # How the entities of a login are resolved, and the cache of the answers.
    _entity_resolver = None
    _entity_cache = {}

    def db_check(self):
        self.my_name = "reflex"
        self.configfile = "reflex.ini"
        return DatabaseHelper.db_check(self)

    def activate(self, config):
        """Open the connection to the reflex database."""
        if ReflexDatabase.is_activated:
            return True
        self.config = config
        self.db = create_engine(
            self.makeConnectionPath(),
            pool_recycle=self.config.dbpoolrecycle,
            pool_size=self.config.dbpoolsize
        )
        if not self.db_check():
            return False
        self.metadata = MetaData(self.db)

        # The tables are created by the SQL scripts of contrib/reflex/sql.
        ReflexSchemaBase.metadata.bind = self.db

        if not self.initMappersCatchException():
            self.session = None
            return False
        ReflexDatabase.is_activated = True

        # The operating settings have no second source: without them nothing
        # knows at which cadence to schedule, how long to keep a measure or
        # whether to notify.
        try:
            settings = self._read_settings_at_activation()
        except ReflexSettingsError:
            ReflexDatabase.is_activated = False
            return False
        if not settings:
            ReflexDatabase.is_activated = False
            return False

        logger.debug("Reflex database connected, %d settings read"
                     % len(settings))
        return True

    @DatabaseHelper._sessionm
    def _read_settings_at_activation(self, session):
        """First read of the settings, which decides the activation."""
        return self._read_settings(session)

    def initMappers(self):
        """Mappers are declarative, nothing to build at runtime."""
        return

    def getDbConnection(self):
        NB_DB_CONN_TRY = 2
        ret = None
        for _ in range(NB_DB_CONN_TRY):
            try:
                ret = self.db.connect()
            except DBAPIError as e:
                logger.error(e)
            except Exception as e:
                logger.error(e)
            if ret:
                break
        if not ret:
            raise Exception("Database reflex connection error")
        return ret

    # =========================================================================
    # Operating settings
    # =========================================================================
    def _read_settings(self, session):
        """Read the settings table and refresh the cache."""
        rows = {}
        try:
            for row in _rows(session.execute(text(
                    "SELECT setting_key, default_value, value, value_type, "
                    "       exposed, updated_by, updated_at "
                    "  FROM settings ORDER BY setting_key"))):
                key = str(row.get('setting_key') or '').strip()
                if key:
                    rows[key] = row
        except Exception as e:
            ReflexDatabase._settings_cache = {}
            ReflexDatabase._settings_cache_at = time.time()
            logger.error(
                "Reflex: the settings table cannot be read (%s). The module "
                "has no operating settings and will not work: replay "
                "services/contrib/reflex/sql on the reflex database." % e)
            try:
                session.rollback()
            except Exception:
                pass
            raise ReflexSettingsError(
                "The reflex settings table cannot be read: %s" % e)

        ReflexDatabase._settings_cache = rows
        ReflexDatabase._settings_cache_at = time.time()
        if not rows:
            logger.error(
                "Reflex: the settings table is empty. The module has no "
                "operating settings and will not work: replay "
                "services/contrib/reflex/sql on the reflex database.")
        return rows

    @DatabaseHelper._sessionm
    def _refresh_settings(self, session):
        """Refresh the cache on a session of its own."""
        return self._read_settings(session)

    def _settings_rows(self, session=None):
        """Settings table as stored, from the cache while it is fresh."""
        cached = ReflexDatabase._settings_cache
        if (cached is not None
                and (time.time() - ReflexDatabase._settings_cache_at)
                < SETTINGS_CACHE_TTL_SECONDS):
            return cached
        if session is not None:
            return self._read_settings(session)
        if not ReflexDatabase.is_activated:
            raise ReflexSettingsError(
                "The reflex database is not connected, settings unreadable")
        return self._refresh_settings()

    def setting(self, key, session=None):
        """Effective value of one operating setting, already typed."""
        row = self._settings_rows(session=session).get(key)
        if row is None:
            raise ReflexSettingsError(
                "Setting '%s' is absent from the settings table: replay "
                "services/contrib/reflex/sql on the reflex database" % key)

        value_type = str(row.get('value_type') or 'string')
        raw = row.get('value')
        if raw is None or str(raw).strip() == '':
            raw = row.get('default_value')

        value = coerce_setting(raw, value_type)
        if value is None:
            if key in OPTIONAL_SETTINGS and value_type == 'string':
                # Empty is a state of its own for these and not an unreadable
                # value, see OPTIONAL_SETTINGS. Restricted to text settings:
                # an empty count of days would still be a table to repair.
                return ''
            raise ReflexSettingsError(
                "Setting '%s' holds '%s', which is not of type %s"
                % (key, raw, value_type))
        return value

    def _derived_console_url(self):
        """Address deduced from mmc.ini, '' when there is none, served from
        the cache while it is fresh.
        """
        cached = ReflexDatabase._derived_url
        if (cached is not None
                and (time.time() - ReflexDatabase._derived_url_at)
                < SETTINGS_CACHE_TTL_SECONDS):
            return cached
        try:
            url = derive_console_url()
        except Exception as e:
            logger.debug("Reflex: the console address could not be deduced "
                         "(%s)" % e)
            url = ''
        ReflexDatabase._derived_url = url
        ReflexDatabase._derived_url_at = time.time()
        return url

    def console_url(self, session=None):
        """Public address of this console, '' when none is usable."""
        try:
            raw = self.setting(CONSOLE_URL_SETTING, session=session)
        except ReflexSettingsError:
            # Also the answer on an instance whose schema predates the key.
            raw = ''
        # Validated on every read and not only when it is saved: a row put in
        # the database by hand went through no form, see readable_console_url.
        url = readable_console_url(raw)
        if url:
            return url
        return self._derived_console_url()

    def console_alerts_url(self, session=None):
        """Link to the alert page of the console, '' when there is no address.
        """
        base = self.console_url(session=session)
        return ("%s/%s" % (base, CONSOLE_ALERTS_PATH)) if base else ''

    @DatabaseHelper._sessionm
    def set_console_url(self, session, login, url):
        """Record the address at which this console is reached, or clear it.

        Returns True, or the structure built by `refused`.
        """
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A write is traced on its caller: no login was "
                           "sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)

        sent = '' if url is None else str(url).strip()
        value = readable_console_url(sent)
        if sent and not value:
            return refused(REFUSAL_INVALID,
                           "The console address must be an http or https URL "
                           "carrying a host, without credentials, query "
                           "string nor fragment", 'console_url',
                           reason=RefusalReason.FIELD_FORMAT_INVALID)

        # Read before the write rather than trusted to rowcount: MySQL counts
        # the rows it changed and not the ones it matched, so saving the same
        # address twice would answer "this setting does not exist".
        known = _one(session.execute(text(
            "SELECT setting_key FROM settings WHERE setting_key = :key"),
            {'key': CONSOLE_URL_SETTING}))
        if known is None:
            return refused(REFUSAL_MISSING,
                           "Setting '%s' is absent from the settings table: "
                           "replay services/contrib/reflex/sql on the reflex "
                           "database" % CONSOLE_URL_SETTING)
        try:
            session.execute(text(
                "UPDATE settings SET value = :value, updated_by = :login, "
                "       updated_at = NOW() "
                " WHERE setting_key = :key"),
                {'value': value or None,
                 'login': _truncate_str(login, 255),
                 'key': CONSOLE_URL_SETTING})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: the console address could not be saved: %s"
                         % e)
            return refused(REFUSAL_FAILED,
                           "The console address could not be saved")
        # The cache would go on serving the old address for up to
        # SETTINGS_CACHE_TTL_SECONDS, and a page that saves a setting is a page
        # that displays it back.
        ReflexDatabase._settings_cache_at = 0.0
        logger.info("Reflex: console address set to '%s' by '%s'"
                    % (value or '(none)', login))
        return True

    def get_retention_settings(self, login=''):
        """The three retention horizons in force, in days."""
        return dict((field, self.setting(key))
                    for field, key, low, high in RETENTION_SETTINGS)

    @DatabaseHelper._sessionm
    def set_retention_settings(self, session, login, values):
        """Record the retention horizons, for the whole instance."""
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A write is traced on its caller: no login was "
                           "sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        if not isinstance(values, dict):
            return refused(REFUSAL_INVALID,
                           "The retention settings must be sent as a "
                           "structure", reason=RefusalReason.PAYLOAD_MALFORMED)

        wanted = []
        for field, key, low, high in RETENTION_SETTINGS:
            if field not in values:
                continue
            days = retention_days(values[field])
            if days is None:
                return refused(REFUSAL_INVALID,
                               "%s must be a whole number of days" % field,
                               field, reason=RefusalReason.VALUE_NOT_INTEGER)
            if not low <= days <= high:
                return refused(REFUSAL_INVALID,
                               "%s must be between %d and %d days"
                               % (field, low, high), field,
                               reason=RefusalReason.VALUE_OUT_OF_RANGE)
            wanted.append((key, days))
        if not wanted:
            return refused(REFUSAL_INVALID,
                           "No retention setting was sent",
                           reason=RefusalReason.PAYLOAD_MALFORMED)

        keys, params = _placeholders('key', [key for key, days in wanted])
        shipped = dict(
            (row.get('setting_key'), row.get('default_value'))
            for row in _rows(session.execute(text(
                "SELECT setting_key, default_value FROM settings "
                " WHERE setting_key IN (" + keys + ")"), params)))
        for key, days in wanted:
            if key not in shipped:
                return refused(REFUSAL_MISSING,
                               "Setting '%s' is absent from the settings "
                               "table: replay services/contrib/reflex/sql on "
                               "the reflex database" % key)
        try:
            for key, days in wanted:
                default = _to_int(shipped[key], None)
                session.execute(text(
                    "UPDATE settings SET value = :value, updated_by = :login, "
                    "       updated_at = NOW() "
                    " WHERE setting_key = :key"),
                    {'value': None if days == default else str(days),
                     'login': _truncate_str(login, 255),
                     'key': key})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: the retention settings could not be saved: "
                         "%s" % e)
            return refused(REFUSAL_FAILED,
                           "The retention settings could not be saved")
        ReflexDatabase._settings_cache_at = 0.0
        logger.info("Reflex: retention set to %s by '%s'"
                    % (", ".join("%s=%d" % item for item in wanted), login))
        return True

    # =========================================================================
    # Activation test
    # =========================================================================
    @DatabaseHelper._sessionm
    def tests(self, session):
        """Check that the database answers and carries the mapped schema.

        The tables expected are the ones schema.py maps, never a second list,
        and the catalog is only checked for not being empty: shipping one
        more probe must not turn the module red.
        """
        result = {
            'ok': False,
            'database': 'reflex',
            'version': None,
            'builtin_probes': 0,
            'schema_complete': False,
            'error': None,
        }
        try:
            result['version'] = session.execute(
                text("SELECT Number FROM version LIMIT 1")).scalar()
            result['builtin_probes'] = _to_int(session.execute(
                text("SELECT COUNT(*) FROM probes WHERE is_builtin = 1")).scalar(), 0)
            expected_tables = sorted(ReflexSchemaBase.metadata.tables)
            fragment, params = _placeholders('table', expected_tables)
            present = set()
            for row in _rows(session.execute(text(
                    "SELECT TABLE_NAME FROM information_schema.TABLES "
                    " WHERE TABLE_SCHEMA = DATABASE() "
                    "   AND TABLE_NAME IN (" + fragment + ")"), params)):
                present.add(str(row.get('TABLE_NAME')).lower())
            missing = [table for table in expected_tables
                       if table not in present]
            result['schema_complete'] = not missing
            if missing:
                result['error'] = "Missing tables: %s" % ", ".join(missing)
            elif not result['builtin_probes']:
                result['error'] = "The shipped probe catalog is empty"
            result['ok'] = bool(result['schema_complete']
                                and result['builtin_probes'])
        except Exception as e:
            logger.error("Reflex tests failed: %s" % e)
            result['error'] = str(e)
        return result

    # =========================================================================
    # Visibility and permissions
    # =========================================================================
    def set_entity_resolver(self, resolver):
        """Declare how the entities a login reaches are obtained."""
        ReflexDatabase._entity_resolver = resolver
        ReflexDatabase._entity_cache = {}

    def entities_for_login(self, login):
        """Entities a login reaches, as strings, cached for a short while."""
        login = _login(login)
        if not login or ReflexDatabase._entity_resolver is None:
            return []
        cached = ReflexDatabase._entity_cache.get(login)
        if cached is not None and (time.time() - cached[0]) < ENTITY_CACHE_TTL_SECONDS:
            return cached[1]
        try:
            entities = parse_entity_list(
                ReflexDatabase._entity_resolver(login))
        except Exception as e:
            logger.error("Reflex: the entities of login '%s' cannot be "
                         "resolved (%s); only the shipped probes and his own "
                         "are shown" % (login, e))
            entities = []
        if len(ReflexDatabase._entity_cache) >= ENTITY_CACHE_MAX_LOGINS:
            ReflexDatabase._entity_cache = {}
        ReflexDatabase._entity_cache[login] = (time.time(), entities)
        return entities

    def _visible_clause(self, login):
        """Visibility fragment and its parameters, for one login."""
        login = str(login or '')
        fragment, params = probe_visible_sql(self.entities_for_login(login))
        params['login'] = login
        return fragment, params

    def _machine_scope_clause(self, login, machine_ref, readable=True,
                              prefix='mscope'):
        """Machine scope fragment and its parameters, for one login."""
        return machine_scope_sql(self.entities_for_login(str(login or '')),
                                 machine_ref, readable=readable, prefix=prefix)

    def _machines_by_entity_sql(self, login, readable=True, extra_column=''):
        """The machines a login reaches, counted by estate, in one statement.
        """
        scope_sql, params = self._machine_scope_clause(login, 'm.id',
                                                       readable=readable)
        return ("SELECT e.glpi_id AS entity_id, "
                "       COUNT(*) AS machines_count"
                + ((", " + extra_column) if extra_column else " ") +
                "  FROM xmppmaster.machines m "
                "  JOIN xmppmaster.glpi_entity e "
                "    ON e.id = m.glpi_entity_id "
                " WHERE " + scope_sql +
                " GROUP BY e.glpi_id"), params

    def _machines_counted_by_entity(self, session, login):
        """How many machines a login reaches in each estate, {} when unknown.
        """
        if not str(login or '').strip():
            return {}
        if not self._memberships_readable(session):
            return {}
        sql, params = self._machines_by_entity_sql(login)
        try:
            rows = _rows(session.execute(text(sql), params))
        except Exception as e:
            session.rollback()
            logger.error("Reflex: the machines of '%s' cannot be counted by "
                         "entity (%s)" % (login, e))
            return {}
        return dict((str(_to_int(row.get('entity_id'), 0)),
                     _to_int(row.get('machines_count'), 0)) for row in rows)

    def _assignment_scope_clause(self, login, readable=True,
                                 groups_readable=True, prefix='avis'):
        """Placement scope fragment and its parameters, for one login."""
        login = str(login or '')
        fragment, params = assignment_visible_sql(
            self.entities_for_login(login), readable=readable,
            groups_readable=groups_readable, prefix=prefix)
        params['login'] = login
        return fragment, params

    def _assignment_scope(self, session, login):
        """Placement scope of a login, with what each of its terms needs read.
        """
        return self._assignment_scope_clause(
            login, readable=self._memberships_readable(session),
            groups_readable=self._group_sharing_readable(session))

    def _mark_readable_assignments(self, session, login, rows):
        """Flag the placements a login reads, and blank the login of the
        others.
        """
        ids = sorted(set(_to_int(row.get('assignment_id'), 0)
                         for row in rows))
        ids = [value for value in ids if value > 0]
        readable = set()
        if ids:
            scope_sql, params = self._assignment_scope(session, login)
            fragment, id_params = _placeholders('mask', ids)
            params.update(id_params)
            readable = set(_to_int(row.get('id'), 0) for row in _rows(
                session.execute(text(
                    "SELECT pa.id FROM probe_assignments pa "
                    " WHERE pa.id IN (" + fragment + ") "
                    "   AND " + scope_sql), params)))
        for row in rows:
            visible = _to_int(row.get('assignment_id'), 0) in readable
            row['assignment_visible'] = 1 if visible else 0
            if not visible:
                row['created_by'] = ''
        return rows

    def _machine_target_states(self, session, login, machine_ids,
                               readable=True):
        """State of each machine a placement names, in one statement."""
        states = {}
        if not readable:
            return states
        ids = sorted(set(machine_ids))
        if not ids:
            return states
        fragment, params = _placeholders('tsm', ids)
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'mx.id', readable=readable, prefix='tsms')
        params.update(scope_params)
        for row in _rows(session.execute(text(
                "SELECT mx.id AS id, (" + scope_sql + ") AS in_scope "
                "  FROM xmppmaster.machines mx "
                " WHERE mx.id IN (" + fragment + ")"), params)):
            states[_to_int(row.get('id'), 0)] = (
                TARGET_STATE_OK if _to_int(row.get('in_scope'), 0)
                else TARGET_STATE_OUT_OF_SCOPE)
        for machine_id in ids:
            states.setdefault(machine_id, TARGET_STATE_DELETED)
        return states

    def _group_target_states(self, session, login, group_ids,
                             groups_readable=True):
        """State of each group a placement names, in one statement."""
        states = {}
        if not groups_readable:
            return states
        ids = sorted(set(group_ids))
        if not ids:
            return states
        fragment, params = _placeholders('tsg', ids)
        params['login'] = str(login or '')
        for row in _rows(session.execute(text(
                "SELECT dgx.id AS id, "
                "       (" + group_shared_sql('dgx.id') + ") AS in_scope "
                "  FROM dyngroup.Groups dgx "
                " WHERE dgx.id IN (" + fragment + ")"), params)):
            states[_to_int(row.get('id'), 0)] = (
                TARGET_STATE_OK if _to_int(row.get('in_scope'), 0)
                else TARGET_STATE_OUT_OF_SCOPE)
        for group_id in ids:
            states.setdefault(group_id, TARGET_STATE_DELETED)
        return states

    def _entity_target_states(self, login, entity_ids):
        """State of each entity a placement names, in one statement on GLPI."""
        states = {}
        ids = sorted(set(entity_ids))
        if not ids:
            return states
        reached = set(parse_entity_list(self.entities_for_login(login)))
        for entity_id in ids:
            states[entity_id] = (TARGET_STATE_OK if str(entity_id) in reached
                                 else TARGET_STATE_OUT_OF_SCOPE)
        try:
            engine, _profiles = self._glpi_access()
            if engine is None:
                return states
            fragment, params = _placeholders('tse', ids)
            with engine.connect() as connection:
                known = set(_to_int(row.get('id'), -1) for row in _rows(
                    connection.execute(text(
                        "SELECT id FROM glpi_entities "
                        " WHERE id IN (" + fragment + ")"), params)))
        except Exception as e:
            if not ReflexDatabase._glpi_unreadable_logged:
                logger.error("Reflex: the entities cannot be read in glpi "
                             "(%s); a placement on an entity keeps the state "
                             "its scope gives" % e)
                ReflexDatabase._glpi_unreadable_logged = True
            return states
        for entity_id in ids:
            if entity_id not in known:
                states[entity_id] = TARGET_STATE_DELETED
        return states

    def _mark_target_states(self, session, login, rows,
                            readable=None, groups_readable=None, known=None):
        """Tell what became of the target of every placement of a list."""
        rows = rows or []
        if readable is None:
            readable = self._memberships_readable(session)
        if groups_readable is None:
            groups_readable = self._group_sharing_readable(session)
        settled = dict(known or {})
        wanted = {'machine': set(), 'group': set(), 'entity': set()}
        keys = []
        for row in rows:
            target_type = str(row.get('target_type') or '')
            if target_type not in wanted:
                keys.append(None)
                continue
            key = (target_type, str(row.get('target_id') or ''))
            if key in settled:
                keys.append(key)
                continue
            # An identifier no row can carry is settled without asking: a
            # machine and a group are numbered from one, an entity from zero,
            # the root one of GLPI.
            floor = 0 if target_type == 'entity' else 1
            value = _to_int(key[1], floor - 1)
            if value < floor:
                settled[key] = TARGET_STATE_DELETED
                keys.append(key)
                continue
            # Asked and answered as a number: a row spelling its identifier
            # any other way reads the same answer rather than none.
            keys.append((target_type, str(value)))
            wanted[target_type].add(value)
        for target_type, states in (
                ('machine', self._machine_target_states(
                    session, login, wanted['machine'], readable=readable)),
                ('group', self._group_target_states(
                    session, login, wanted['group'],
                    groups_readable=groups_readable)),
                ('entity', self._entity_target_states(login,
                                                      wanted['entity']))):
            for value, state in states.items():
                settled[(target_type, str(value))] = state
        for row, key in zip(rows, keys):
            # Nothing was read about that target: the state stays the one the
            # scope of the reader gives, which is what the console showed
            # before this field existed.
            row['target_state'] = (
                TARGET_STATE_OK if key is None
                else settled.get(key, TARGET_STATE_OUT_OF_SCOPE))
        return rows

    def _machine_in_scope(self, session, login, machines_id, readable=None):
        """Whether one machine stands in the estate a login reaches."""
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return False
        if readable is None:
            readable = self._memberships_readable(session)
        scope_sql, params = self._machine_scope_clause(
            login, ':machines_id', readable=readable)
        params['machines_id'] = machines_id
        return bool(_to_int(session.execute(
            text("SELECT " + scope_sql), params).scalar(), 0))

    def _group_in_scope(self, session, login, group_id, groups_readable=None):
        """Whether dyngroup gives one group to a login."""
        group_id = _to_int(group_id, 0)
        if groups_readable is None:
            groups_readable = self._group_sharing_readable(session)
        if group_id <= 0 or not groups_readable:
            return False
        return bool(_to_int(session.execute(
            text("SELECT " + group_shared_sql(':group_id')),
            {'group_id': group_id, 'login': str(login or '')}).scalar(), 0))

    def _target_in_scope(self, session, login, target_type, target_id,
                         readable=None, groups_readable=None):
        """Whether a login may place a probe on a target."""
        if target_type == 'machine':
            return self._machine_in_scope(session, login, target_id,
                                          readable=readable)
        if target_type == 'entity':
            return str(target_id) in self.entities_for_login(login)
        if target_type == 'group':
            return self._group_in_scope(session, login, target_id,
                                        groups_readable=groups_readable)
        return False

    # =========================================================================
    # The estate, read in GLPI
    # =========================================================================
    _glpi_engine = None
    _glpi_profiles = None
    _glpi_unreadable_logged = False

    @classmethod
    def _glpi_access(cls):
        """The GLPI connection and the profiles that carry an estate there."""
        if cls._glpi_engine is not None:
            return cls._glpi_engine, cls._glpi_profiles
        from mmc.plugins.glpi.config import GlpiConfig
        from mmc.plugins.glpi.database import Glpi
        glpi = Glpi()
        if getattr(glpi, 'is_activated', False):
            cls._glpi_profiles = list(glpi.config.activeProfiles)
            cls._glpi_engine = glpi.database.db
            return cls._glpi_engine, cls._glpi_profiles
        config = GlpiConfig("glpi")
        if getattr(config, 'disable', 0):
            return None, None
        holder = _GlpiConnection()
        holder.config = config
        cls._glpi_profiles = list(config.activeProfiles)
        cls._glpi_engine = create_engine(holder.makeConnectionPath(),
                                         pool_recycle=config.dbpoolrecycle,
                                         pool_size=config.dbpoolsize)
        return cls._glpi_engine, cls._glpi_profiles

    # =========================================================================
    # Condition settings, per estate
    # =========================================================================
    def _setting_entities(self, login):
        """Entities a login may choose to read and set the conditions of."""
        login = _login(login)
        if not login:
            return []
        return self.entities_for_login(login)

    def _reader_entity(self, login):
        """The entity read and set when none is chosen, None when there is
        none.
        """
        entities = self._setting_entities(login)
        if not entities:
            return None
        return str(min(int(entity) for entity in entities))

    def _chosen_entity(self, login, entity_id):
        """The entity a caller names, None when the login may not set it."""
        wanted = '' if entity_id is None else str(entity_id).strip()
        if not wanted:
            return self._reader_entity(login)
        if not wanted.isdigit():
            return None
        wanted = str(int(wanted))
        for entity in self._setting_entities(login):
            if str(_to_int(entity, -1)) == wanted:
                return wanted
        return None

    def _machine_entity(self, session, machines_id):
        """Estate one machine belongs to, as GLPI spells it, None if unknown.
        """
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return None
        try:
            entity = session.execute(text(
                "SELECT e.glpi_id FROM xmppmaster.machines m "
                "  JOIN xmppmaster.glpi_entity e ON e.id = m.glpi_entity_id "
                " WHERE m.id = :machines_id"),
                {'machines_id': machines_id}).scalar()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: the entity of machine %s cannot be read "
                         "(%s); its conditions are read on the shipped values"
                         % (machines_id, e))
            return None
        # Zero is the root entity of GLPI, not an absence.
        return None if entity is None else str(_to_int(entity, 0))

    def _condition_scope(self, entity_id):
        """What a statement needs to read a condition for one estate."""
        if entity_id is None:
            return {'alias': None, 'join': '', 'params': {}}
        return {'alias': 'coent',
                'join': condition_override_join_sql('coent',
                                                    override_alias='coent'),
                'params': {'coent': str(entity_id)}}

    # =========================================================================
    # Machine memberships
    # =========================================================================
    _memberships_unreadable_logged = False

    def _memberships_readable(self, session):
        """Whether dyngroup and xmppmaster can be read from this connection."""
        try:
            session.execute(text(
                "SELECT 1 FROM dyngroup.Results, dyngroup.Machines, "
                "       xmppmaster.machines, xmppmaster.glpi_entity LIMIT 0"))
        except Exception as e:
            session.rollback()
            if not ReflexDatabase._memberships_unreadable_logged:
                logger.error("Reflex: dyngroup or xmppmaster unreadable, the "
                             "probes placed on a group or an entity are not "
                             "counted on the machines (%s)" % e)
                ReflexDatabase._memberships_unreadable_logged = True
            return False
        ReflexDatabase._memberships_unreadable_logged = False
        return True

    _group_sharing_unreadable_logged = False

    def _group_sharing_readable(self, session):
        """Whether the tables dyngroup shares a group in can be read."""
        try:
            session.execute(text(
                "SELECT 1 FROM dyngroup.Groups, dyngroup.Users, "
                "       dyngroup.ShareGroup LIMIT 0"))
        except Exception as e:
            session.rollback()
            if not ReflexDatabase._group_sharing_unreadable_logged:
                logger.error("Reflex: the groups of dyngroup cannot be read, "
                             "a probe placed on a group is only listed to "
                             "whoever placed it (%s)" % e)
                ReflexDatabase._group_sharing_unreadable_logged = True
            return False
        ReflexDatabase._group_sharing_unreadable_logged = False
        return True

    def _machine_memberships(self, session, machines_id, readable):
        """Groups and entities of one machine that carry a placement."""
        group_ids = []
        entity_ids = []
        if not readable:
            return group_ids, entity_ids
        rows = _rows(session.execute(text(
            "SELECT DISTINCT pa.target_type, pa.target_id "
            "  FROM probe_assignments pa "
            "  JOIN (" + membership_reach_sql() + ") rc "
            "    ON rc.assignment_id = pa.id "
            " WHERE rc.machines_id = :machines_id"),
            {'machines_id': _to_int(machines_id, 0)}))
        for row in rows:
            if row.get('target_type') == 'group':
                group_ids.append(row.get('target_id'))
            elif row.get('target_type') == 'entity':
                entity_ids.append(row.get('target_id'))
        return group_ids, entity_ids

    _presence_unreadable_logged = False

    def _machines_presence(self, session, machines_ids):
        """Whether the agent of each machine is connected, by machines_id."""
        ids = [_to_int(machines_id, 0) for machines_id in (machines_ids or [])]
        ids = [machines_id for machines_id in ids if machines_id > 0]
        if not ids:
            return {}
        fragment, params = _placeholders('presence', ids)
        try:
            rows = _rows(session.execute(text(
                "SELECT id, enabled FROM xmppmaster.machines "
                " WHERE id IN (" + fragment + ")"), params))
        except Exception as e:
            session.rollback()
            if not ReflexDatabase._presence_unreadable_logged:
                logger.error("Reflex: xmppmaster unreadable, the connection "
                             "state of the agents is not shown on the "
                             "machines (%s)" % e)
                ReflexDatabase._presence_unreadable_logged = True
            return None
        ReflexDatabase._presence_unreadable_logged = False
        presence = dict((machines_id, 0) for machines_id in ids)
        for row in rows:
            presence[_to_int(row.get('id'), 0)] = (
                1 if _to_int(row.get('enabled'), 0) == 1 else 0)
        return presence

    _machine_os_unreadable_logged = False

    def _machine_os(self, session, machines_id):
        """System of one machine, '' when it cannot be told."""
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return ''
        try:
            value = session.execute(text(
                "SELECT " + machine_os_sql(':machines_id') + " AS machine_os"),
                {'machines_id': machines_id}).scalar()
        except Exception as e:
            session.rollback()
            if not ReflexDatabase._machine_os_unreadable_logged:
                logger.error("Reflex: xmppmaster unreadable, the system of "
                             "the machines is unknown and their configuration "
                             "carries every measurable probe (%s)" % e)
                ReflexDatabase._machine_os_unreadable_logged = True
            return ''
        ReflexDatabase._machine_os_unreadable_logged = False
        value = str(value or '').strip().lower()
        return value if value in OPERATING_SYSTEMS else ''

    def _probe_access(self, session, login, probe_id):
        """Return what a login may do with a probe."""
        login = str(login or '')
        probe_id = _to_int(probe_id, 0)
        access = {
            'exists': False,
            'visible': False,
            'can_write': False,
            'is_owner': False,
            'is_builtin': False,
            'probe': None,
            'permission': None,
        }
        if probe_id <= 0:
            return access

        row = _one(session.execute(text(
            "SELECT p.* FROM probes p WHERE p.id = :probe_id"),
            {'probe_id': probe_id}))
        if row is None:
            return access

        access['exists'] = True
        access['probe'] = row
        access['is_builtin'] = bool(_to_int(row.get('is_builtin'), 0))
        owner = row.get('owner_login')
        access['is_owner'] = bool(login) and owner is not None and owner == login
        visibility = row.get('visibility')
        # Read through the same normalisation as the resolved list, so that
        # an entity written 0 or 03 is compared as the resolver spells it.
        in_entity = (visibility == 'entity'
                     and str(_to_int(row.get('entity_id'), -1))
                     in self.entities_for_login(login))

        access['visible'] = (visibility == 'global' or access['is_owner']
                             or in_entity)
        if access['is_owner']:
            access['permission'] = 'rw'
        elif access['visible']:
            access['permission'] = 'r'

        # A probe shipped with the product is nobody's to modify: a variant is
        # obtained by duplicating it.
        access['can_write'] = not access['is_builtin'] and access['is_owner']
        return access

    # =========================================================================
    # Probes
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_probes(self, session, login, start=0, limit=20, filter_str='',
                   scope='all', entity_id=''):
        """Paginated list of the probes a login may see, for one entity."""
        login = str(login or '')
        start = max(_to_int(start, 0), 0)
        limit = _to_int(limit, 20)
        if limit <= 0:
            limit = 20
        scope = str(scope or 'all').lower()

        setting_entity = self._chosen_entity(login, entity_id)
        if setting_entity is None:
            setting_entity = self._reader_entity(login)

        visible_sql, params = self._visible_clause(login)
        clauses = [visible_sql]
        if setting_entity is None:
            clauses.append("p.visibility <> 'entity'")
        else:
            clauses.append("p.visibility <> 'entity' "
                           "OR p.entity_id = :list_entity")
            params['list_entity'] = setting_entity

        if scope == 'mine':
            clauses.append("p.owner_login IS NOT NULL AND p.owner_login = :login")
        elif scope == 'entity':
            clauses.append("p.visibility = 'entity'")
        elif scope == 'catalog':
            clauses.append("p.visibility = 'global'")

        filter_str = str(filter_str or '').strip()
        if filter_str:
            clauses.append("(p.label LIKE :filter OR p.probe_key LIKE :filter "
                           "OR p.metric_key LIKE :filter OR p.category LIKE :filter)")
            params['filter'] = "%%%s%%" % filter_str

        where = " WHERE " + " AND ".join(["(" + clause + ")" for clause in clauses])

        total = _to_int(session.execute(
            text("SELECT COUNT(*) FROM probes p" + where), params).scalar(), 0)
        # Same WHERE as the list, visibility included: counted on every probe
        # it would tell a reader that a colleague keeps a private one.
        has_personal = total > 0 and bool(_to_int(session.execute(text(
            "SELECT EXISTS (SELECT 1 FROM probes p" + where +
            " AND COALESCE(p.is_builtin, 0) = 0)"), params).scalar(), 0))

        params['limit'] = limit
        params['start'] = start
        rows = _rows(session.execute(text(
            "SELECT p.id, p.probe_key, p.label, p.description, p.category, "
            "       p.probe_type, p.metric_key, p.unit, p.value_type, "
            "       p.os_support, p.min_interval_seconds, "
            "       p.default_interval_seconds, p.is_builtin, p.visibility, "
            "       p.entity_id, "
            "       p.owner_login, p.enabled, p.created_at, p.updated_at, "
            "       CASE WHEN p.owner_login IS NOT NULL AND p.owner_login = :login "
            "            THEN 'rw' ELSE 'r' END AS permission, "
            "       (SELECT COUNT(*) FROM probe_conditions pc "
            "         WHERE pc.probe_id = p.id) AS conditions_count "
            "  FROM probes p " + where +
            # Alphabetical, and nothing else.
            " ORDER BY p.label ASC, p.id ASC "
            " LIMIT :limit OFFSET :start"), params))

        probe_ids = [_to_int(row.get('id'), 0) for row in rows]
        placements = self._page_assignment_counts(session, login, probe_ids)
        conditions = self._page_conditions(session, probe_ids, setting_entity)
        cadences = self._page_cadences(session, login, probe_ids)
        for row, probe_id in zip(rows, probe_ids):
            row.update(placements[probe_id])
            row['conditions'] = conditions.get(probe_id, [])
            row['cadences'] = cadences.get(probe_id, [])

        return {'total': total, 'data': rows,
                'has_personal': bool(has_personal),
                'setting_entity_id': setting_entity}

    def _page_assignment_counts(self, session, login, probe_ids):
        """Where each probe of a page is placed, as the sheet counts it."""
        counts = dict((probe_id,
                       dict(summarise_assignments([]), assignments_count=0))
                      for probe_id in probe_ids)
        wanted = [probe_id for probe_id in probe_ids if probe_id > 0]
        if not wanted:
            return counts
        # What the scope is built on is what the states are read on: asked
        # twice, the same page could keep a placement its own figures no
        # longer count.
        readable = self._memberships_readable(session)
        groups_readable = self._group_sharing_readable(session)
        scope_sql, params = self._assignment_scope_clause(
            login, readable=readable, groups_readable=groups_readable,
            prefix='lasg')
        fragment, id_params = _placeholders('lprb', wanted)
        params.update(id_params)
        rows = _rows(session.execute(text(
            "SELECT pa.probe_id, pa.target_type, pa.target_id "
            "  FROM probe_assignments pa "
            " WHERE pa.probe_id IN (" + fragment + ") "
            "   AND " + scope_sql), params))
        grouped = {}
        for row in drop_deleted_targets(
                self._mark_target_states(session, login, rows,
                                         readable=readable,
                                         groups_readable=groups_readable)):
            grouped.setdefault(_to_int(row.get('probe_id'), 0), []).append(row)
        for probe_id, placements in grouped.items():
            if probe_id in counts:
                counts[probe_id] = dict(summarise_assignments(placements),
                                        assignments_count=len(placements))
        return counts

    def _page_conditions(self, session, probe_ids, entity_id):
        """Conditions of a page of probes as they apply to one entity."""
        if not probe_ids:
            return {}
        scope = self._condition_scope(entity_id)
        fragment, params = _placeholders('lcond', probe_ids)
        params.update(scope['params'])
        fields = ('threshold_value', 'threshold_value2', 'threshold_text',
                  'duration_seconds', 'severity', 'enabled')
        rows = _rows(session.execute(text(
            "SELECT pc.id, pc.probe_id, pc.operator, "
            + ", ".join("%s AS %s" % (condition_field_sql(
                field, 'pc', scope['alias']), field) for field in fields) +
            ", " + condition_customized_sql(scope['alias']) +
            " AS is_customized "
            "  FROM probe_conditions pc " + scope['join'] +
            " WHERE pc.probe_id IN (" + fragment + ") "
            " ORDER BY pc.probe_id ASC, pc.display_order ASC, pc.id ASC"),
            params))
        grouped = {}
        for row in rows:
            probe_id = _to_int(row.pop('probe_id'), 0)
            row['is_customized'] = _to_int(row.get('is_customized'), 0)
            grouped.setdefault(probe_id, []).append(row)
        return grouped

    _cadences_unreadable_logged = False

    def _page_cadences(self, session, login, probe_ids):
        """Cadences a page of probes is measured at on the park of a reader."""
        entity_ids = self.entities_for_login(login)
        if not probe_ids or not entity_ids:
            return {}
        readable = self._memberships_readable(session)
        if not readable:
            return {}
        reach_sql, params = assignment_reaches_estate_sql(entity_ids)
        fragment, id_params = _placeholders('lcad', probe_ids)
        params.update(id_params)
        try:
            rows = _rows(session.execute(text(
                "SELECT DISTINCT pa.probe_id, pa.interval_seconds "
                "  FROM probe_assignments pa "
                " WHERE pa.probe_id IN (" + fragment + ") "
                "   AND pa.interval_seconds > 0 "
                "   AND " + reach_sql +
                " ORDER BY pa.probe_id ASC, pa.interval_seconds ASC"), params))
        except Exception as e:
            session.rollback()
            if not ReflexDatabase._cadences_unreadable_logged:
                logger.error("Reflex: the cadences of the probes cannot be "
                             "read on the machines of an entity (%s)" % e)
                ReflexDatabase._cadences_unreadable_logged = True
            return {}
        ReflexDatabase._cadences_unreadable_logged = False
        grouped = {}
        for row in rows:
            interval = _to_int(row.get('interval_seconds'), 0)
            cadences = grouped.setdefault(_to_int(row.get('probe_id'), 0), [])
            if interval not in cadences:
                cadences.append(interval)
        for cadences in grouped.values():
            cadences.sort()
        return grouped

    @DatabaseHelper._sessionm
    def get_probe(self, session, login, probe_id, entity_id=''):
        """Probe with its conditions and its assignments."""
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return {}

        probe = dict(access['probe'])
        commands = dict((field, '') for field in SCRIPT_COMMAND_FIELDS)
        if probe.get('probe_type') == 'script':
            commands = self._script_commands(session, probe_id)
        probe.update(commands)
        probe['permission'] = access['permission']
        probe['can_write'] = access['can_write']
        probe['is_owner'] = access['is_owner']

        probe_id = _to_int(probe_id, 0)
        # Three readings of the same rows, and they answer three different
        # questions: what applies today, what the product ships, and whether
        # somebody moved it.
        setting_entity = self._chosen_entity(login, entity_id)
        if setting_entity is None:
            setting_entity = self._reader_entity(login)
        scope = self._condition_scope(setting_entity)
        params = dict(scope['params'], probe_id=probe_id)
        conditions = _rows(session.execute(text(
            "SELECT pc.id, pc.probe_id, pc.operator, pc.display_order, "
            "       " + condition_effective_sql('pc', scope['alias']) + ", "
            "       " + condition_default_sql() + ", "
            "       " + condition_trace_sql('customized_by', scope['alias'])
            + " AS customized_by, "
            "       " + condition_trace_sql('customized_at', scope['alias'])
            + " AS customized_at, "
            "       " + condition_customized_sql(scope['alias'])
            + " AS is_customized "
            "  FROM probe_conditions pc " + scope['join'] +
            " WHERE pc.probe_id = :probe_id "
            " ORDER BY pc.display_order ASC, pc.id ASC"), params))

        # The probe stays public, what the other clients did with it does
        # not, see assignment_visible_sql.
        scope_sql, params = self._assignment_scope(session, login)
        params['probe_id'] = probe_id
        assignments = _rows(session.execute(text(
            "SELECT pa.id, pa.probe_id, pa.target_type, pa.target_id, "
            "       pa.interval_seconds, pa.created_by, pa.language, "
            "       pa.created_at "
            "  FROM probe_assignments pa WHERE pa.probe_id = :probe_id "
            "   AND " + scope_sql +
            " ORDER BY pa.target_type ASC, pa.id ASC"), params))
        # A placement read is not a target that still exists: its author reads
        # his own whatever it names, and an agent reinscribed leaves the
        # identifier of a machine that is gone.
        self._mark_target_states(session, login, assignments)
        assignments = drop_deleted_targets(assignments)

        # A probe carries the same fields whether it comes from the list or
        # from the detail: the console builds the placement sentence the same
        # way on both pages.
        probe.update(summarise_assignments(assignments))

        return {
            'probe': probe,
            'conditions': conditions,
            'assignments': assignments,
            'setting_entity_id': setting_entity,
            'reader_entities_count': len(self.entities_for_login(login)),
        }

    @DatabaseHelper._sessionm
    def get_probe_entity_settings(self, session, login, probe_id):
        """What this probe does, and what was set on it, in each estate."""
        login = _login(login)
        probe_id = _to_int(probe_id, 0)
        if not login or probe_id <= 0:
            return {}
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return {}

        entities = self._setting_entities(login)
        reader_entity = self._reader_entity(login)
        answer = {'probe_id': probe_id,
                  'reader_entity_id': reader_entity or '',
                  'unreadable': 0,
                  'data': []}
        if not entities:
            return answer

        # --- the machines of the reader, counted by estate in one pass ------
        counted = {}
        readable = self._memberships_readable(session)
        if not readable:
            answer['unreadable'] = 1
        else:
            # Counted on what reaches the machine and not on the placements the
            # reader is shown: this figure answers what his own park measures,
            # which is a fact about his machines and not a gesture of somebody.
            target_sql, params = machine_target_clauses(
                None, machine_column='m.id',
                reach_sql=membership_reach_sql(readable))
            params['probe_id'] = probe_id
            measured_sql = ("SUM(CASE WHEN EXISTS ("
                            "      SELECT 1 FROM probe_assignments pa "
                            "       WHERE pa.probe_id = :probe_id "
                            "         AND " + target_sql + ") "
                            "     AND NOT EXISTS ("
                            "      SELECT 1 FROM probe_exclusions px "
                            "       WHERE px.probe_id = :probe_id "
                            "         AND px.machines_id = m.id) "
                            "    THEN 1 ELSE 0 END) AS measured_count ")
            count_sql, scope_params = self._machines_by_entity_sql(
                login, readable=readable, extra_column=measured_sql)
            params.update(scope_params)
            try:
                for row in _rows(session.execute(text(count_sql), params)):
                    counted[str(_to_int(row.get('entity_id'), 0))] = row
            except Exception as e:
                # The settings are still worth answering: they live in this
                # database and none of them depends on a machine being counted.
                session.rollback()
                logger.error("Reflex: the machines of probe %s cannot be "
                             "counted by entity (%s); the estates are "
                             "answered without their figures"
                             % (probe_id, e))
                counted = {}
                answer['unreadable'] = 1

        # --- the conditions of every estate, in one reading -----------------
        # One statement rather than one per estate: the entities are handed
        # to the database as a relation and the override of each is brought
        # by the ordinary join, so these rows are the very rows get_probe
        # answers, entity by entity, and cannot drift from them.
        params = {'probe_id': probe_id}
        selects = []
        for index, entity in enumerate(entities):
            key = 'coent%d' % index
            params[key] = str(entity)
            selects.append("SELECT :%s AS entity_id" % key)
        override = 'pco'
        conditions = {}
        customized = {}
        for row in _rows(session.execute(text(
                "SELECT ents.entity_id AS setting_entity_id, "
                "       pc.id, pc.probe_id, pc.operator, pc.display_order, "
                "       " + condition_effective_sql('pc', override) + ", "
                "       " + condition_default_sql() + ", "
                "       " + condition_trace_sql('customized_by', override)
                + " AS customized_by, "
                "       " + condition_trace_sql('customized_at', override)
                + " AS customized_at, "
                "       " + condition_customized_sql(override)
                + " AS is_customized "
                "  FROM probe_conditions pc "
                "  CROSS JOIN (" + " UNION ALL ".join(selects) + ") ents "
                + condition_override_join_sql(None, override_alias=override,
                                              entity_ref='ents.entity_id') +
                " WHERE pc.probe_id = :probe_id "
                " ORDER BY pc.display_order ASC, pc.id ASC"), params)):
            entity = str(row.pop('setting_entity_id'))
            row['is_customized'] = _to_int(row.get('is_customized'), 0)
            conditions.setdefault(entity, []).append(row)
            if row['is_customized']:
                customized[entity] = 1

        # Sorted on the identifier, the only order this layer holds: the
        # console names its estates and sorts them on the names, which it
        # reads from GLPI and this module never sees.
        data = []
        for entity in sorted(entities, key=lambda value: _to_int(value, 0)):
            figures = counted.get(entity) or {}
            machines = _to_int(figures.get('machines_count'), 0)
            adapted = customized.get(entity, 0)
            if not machines and not adapted and entity != reader_entity:
                continue
            data.append({
                'entity_id': entity,
                'machines_count': machines,
                'measured_count': _to_int(figures.get('measured_count'), 0),
                'is_customized': adapted,
                'conditions': conditions.get(entity, []),
            })
        answer['data'] = data
        return answer

    @DatabaseHelper._sessionm
    def get_probe_collectors(self, session, probe_id, login=None):
        """Collection methods of a probe, one row per operating system."""
        probe_id = _to_int(probe_id, 0)
        if probe_id <= 0:
            return {'total': 0, 'data': []}
        if login is not None:
            access = self._probe_access(session, login, probe_id)
            if not access['visible']:
                return {'total': 0, 'data': []}
        rows = _rows(session.execute(text(
            "SELECT id, probe_id, os, collector, params_json, "
            "       implementation_note, requires, enabled "
            "  FROM probe_collectors WHERE probe_id = :probe_id "
            " ORDER BY FIELD(os, 'windows', 'linux', 'darwin')"),
            {'probe_id': probe_id}))
        return {'total': len(rows), 'data': rows}

    def _resolve_scope(self, login, probe, source=None):
        """Decide the scope of a personal probe and the entity it is scoped
        to.
        """
        source = source or {}
        requested = str(probe.get('visibility',
                                  source.get('visibility', 'entity'))
                        or 'entity').strip().lower()
        if requested == 'global':
            raise ReflexValidationError(
                "The global scope is reserved for the probes shipped with "
                "the product", 'visibility', RefusalReason.SCOPE_RESERVED)
        if requested not in USER_VISIBILITIES:
            raise ReflexValidationError("Unknown scope: %s" % requested,
                                        'visibility',
                                        RefusalReason.SCOPE_UNKNOWN)
        if requested == 'private':
            return {'visibility': 'private', 'entity_id': None}

        entities = self.entities_for_login(login)
        current = source.get('entity_id')
        current = str(current) if current is not None else None
        raw = probe.get('entity_id', current)
        # An absent entity and an empty one say the same thing, and a payload
        # that carries the key with nothing in it must not drop the entity a
        # probe already has.
        if raw is None or not str(raw).strip():
            raw = current
        # Zero is the root entity of GLPI, not an absent value: an estate
        # that never split holds nothing else.
        asked = _to_int(str(raw).strip(), -1) if raw is not None else -1
        asked = str(asked) if asked >= 0 else ''

        if asked:
            # Keeping the entity a probe already carries is not a scope
            # change: an owner who has left that entity would otherwise be
            # unable to save a label he is still allowed to edit.
            if asked not in entities and asked != current:
                raise ReflexValidationError(
                    "You have no access to entity %s" % asked, 'entity_id',
                    RefusalReason.ENTITY_FORBIDDEN)
            return {'visibility': 'entity', 'entity_id': asked}

        if len(entities) == 1:
            return {'visibility': 'entity', 'entity_id': entities[0]}
        if not entities:
            # No estate to scope to: the probe is kept for its owner alone
            # rather than written with an entity nobody chose.
            logger.warning(
                "Reflex: login '%s' reaches no entity, the probe stays private"
                % login)
            return {'visibility': 'private', 'entity_id': None}
        raise ReflexValidationError(
            "An entity scoped probe must state which entity it belongs to",
            'entity_id', RefusalReason.FIELD_REQUIRED)

    def _label_conflict(self, session, label, scope, exclude_id=0,
                        kept_label=None):
        """Say whether a probe name is already taken, and under which rule."""
        wanted = fold_label(label)
        if not wanted:
            return ''
        kept = fold_label(kept_label)
        exclude_id = _to_int(exclude_id, 0)
        clauses = ["p.visibility = 'global'"]
        params = {}
        if scope.get('visibility') == 'entity':
            # Read through the same normalisation as _probe_access, so an
            # entity written 0 or 03 by hand is compared as the resolver spells
            # it.
            clauses.append("(p.visibility = 'entity' "
                           " AND CAST(p.entity_id AS SIGNED) = :entity)")
            params['entity'] = _to_int(scope.get('entity_id'), -1)
        else:
            owner = str(scope.get('owner_login') or '')
            if not owner:
                return ''
            clauses.append("(p.visibility = 'private' "
                           " AND p.owner_login = :owner)")
            params['owner'] = owner
        conflict = ''
        shipped = None
        looked = False
        for row in _rows(session.execute(text(
                "SELECT p.id, p.probe_key, p.label, p.visibility FROM probes p "
                " WHERE (" + " OR ".join(clauses) + ")"), params)):
            if _to_int(row.get('id'), 0) == exclude_id:
                continue
            if row.get('visibility') == 'global':
                # A shipped name is held in every wording it is read under, see
                # shipped_label_index.
                if wanted == kept:
                    continue
                if not looked:
                    # Read once for the whole comparison, not once per row of
                    # the catalog.
                    looked = True
                    shipped = shipped_label_index(self.db)
                forms = set(shipped.get(str(row.get('probe_key') or ''), ())
                            if shipped else ())
                forms.add(fold_label(row.get('label')))
                if wanted not in forms:
                    continue
                # The stronger rule wins when both match: the catalog holds the
                # name for everybody, and no rename in the entity frees it.
                return RefusalReason.LABEL_RESERVED
            if fold_label(row.get('label')) != wanted:
                continue
            conflict = RefusalReason.LABEL_ALREADY_USED
        return conflict

    def _check_label_free(self, session, label, scope, exclude_id=0,
                          kept_label=None):
        """Refuse a probe name already borne where the probe is going to live.
        """
        reason = self._label_conflict(session, label, scope, exclude_id,
                                      kept_label)
        if reason == RefusalReason.LABEL_RESERVED:
            raise ReflexValidationError(
                "A probe shipped with the product is named '%s'. The catalog "
                "is read by everybody, so that name is not available to "
                "anyone" % label, 'label', reason)
        if reason == RefusalReason.LABEL_ALREADY_USED:
            if scope.get('visibility') == 'entity':
                raise ReflexValidationError(
                    "A probe of your entity is already named '%s'" % label,
                    'label', reason)
            raise ReflexValidationError(
                "One of your own probes is already named '%s'" % label,
                'label', reason)

    def _validate_probe_payload(self, probe, partial_source=None, login=None,
                                scripted=True, session=None, probe_id=0):
        """Normalise a probe payload coming from the console."""
        if not isinstance(probe, dict):
            raise ReflexValidationError("A probe must be a structure", None,
                                        RefusalReason.PAYLOAD_MALFORMED)
        source = partial_source or {}

        category = str(probe.get('category', source.get('category', 'system'))
                       or 'system').strip().lower()
        if category not in CATEGORIES:
            raise ReflexValidationError("Unknown category: %s" % category,
                                        'category',
                                        RefusalReason.CATEGORY_UNKNOWN)

        value_type = str(probe.get('value_type',
                                   source.get('value_type', 'numeric'))
                         or 'numeric').strip().lower()
        if value_type not in VALUE_TYPES:
            raise ReflexValidationError("Unknown value type: %s" % value_type,
                                        'value_type',
                                        RefusalReason.VALUE_TYPE_UNKNOWN)

        label = _clean_str(probe.get('label', source.get('label')), 255,
                           'label', required=True)
        description = _clean_str(probe.get('description',
                                           source.get('description')),
                                 65535, 'description')
        unit = _clean_str(probe.get('unit', source.get('unit')), 32, 'unit')

        commands = {}
        if scripted:
            for field in SCRIPT_COMMAND_FIELDS:
                commands[field] = _clean_command(
                    probe.get(field, source.get(field)), field)
            if not any(commands.values()):
                raise ReflexValidationError(
                    "A probe runs a command: give the command for Linux and "
                    "macOS, the one for Windows, or both", 'command_unix',
                    RefusalReason.FIELD_REQUIRED)

        scope = self._resolve_scope(login, probe, source)
        # Judged once the scope is settled, because the scope decides who reads
        # the name and therefore whom it has to be unique for.
        if session is not None:
            self._check_label_free(session, label,
                                   dict(scope, owner_login=login),
                                   exclude_id=probe_id,
                                   kept_label=source.get('label'))

        # A probe declares its own floor, and nothing above it applies.
        if scripted:
            # The floor and the default cadence of a scripted probe are the
            # schema's: creation leaves both columns out of the INSERT for
            # their DEFAULT to apply, an edit writes back what the row holds.
            min_interval = _to_int(source.get('min_interval_seconds'), 0)
            default_interval = _to_int(
                source.get('default_interval_seconds'), 0)
        else:
            min_interval = _to_int(
                probe.get('min_interval_seconds',
                          source.get('min_interval_seconds', 300)), 300)
            if min_interval <= 0:
                raise ReflexValidationError(
                    "min_interval_seconds must be a positive number of "
                    "seconds", 'min_interval_seconds',
                    RefusalReason.VALUE_NOT_POSITIVE)
            default_interval = _to_int(
                probe.get('default_interval_seconds',
                          source.get('default_interval_seconds',
                                     min_interval)),
                min_interval)
            if default_interval < min_interval:
                default_interval = min_interval

        values = {
            'label': label,
            'description': description,
            'category': category,
            'unit': unit,
            'value_type': value_type,
            'min_interval_seconds': min_interval,
            'default_interval_seconds': default_interval,
            'visibility': scope['visibility'],
            'entity_id': scope['entity_id'],
            'enabled': _to_bool_int(probe.get('enabled', source.get('enabled', 1))),
        }
        if scripted:
            rows, os_support = script_collector_rows(commands)
            values['os_support'] = os_support
            values['collectors'] = rows
        else:
            values['probe_key'] = source.get('probe_key')
            values['metric_key'] = source.get('metric_key')
            values['os_support'] = source.get('os_support')
        return values

    def _script_keys(self, session, label):
        """probe_key and metric_key of a new scripted probe."""
        base = script_key_base(label)[:120]
        candidate = base
        rank = 1
        while _to_int(session.execute(
                text("SELECT COUNT(*) FROM probes WHERE probe_key = :probe_key"),
                {'probe_key': candidate}).scalar(), 0):
            rank += 1
            if rank > MAX_PROBE_COPIES:
                candidate = "%s_%s" % (base[:111], os.urandom(4).hex())
                break
            candidate = "%s_%d" % (base, rank)
        return candidate, SCRIPT_METRIC_KEY_PREFIX + candidate

    def _script_commands(self, session, probe_id):
        """Commands of a scripted probe, read back from its collectors."""
        commands = dict((field, '') for field in SCRIPT_COMMAND_FIELDS)
        by_collector = {}
        for row in _rows(session.execute(text(
                "SELECT os, collector, params_json FROM probe_collectors "
                " WHERE probe_id = :probe_id"),
                {'probe_id': _to_int(probe_id, 0)})):
            by_collector[(row.get('os'), row.get('collector'))] = \
                row.get('params_json')
        for field, os_name, collector in SCRIPT_COLLECTORS:
            if commands[field]:
                continue
            raw = by_collector.get((os_name, collector))
            if not raw:
                continue
            try:
                command = json.loads(raw).get('command')
            except (ValueError, TypeError, AttributeError):
                command = None
            if isinstance(command, str):
                commands[field] = command
        return commands

    def _write_script_collectors(self, session, probe_id, rows):
        """Replace the collectors of a scripted probe, without committing."""
        session.execute(text(
            "DELETE FROM probe_collectors WHERE probe_id = :probe_id"),
            {'probe_id': probe_id})
        for row in rows:
            session.execute(text(
                "INSERT INTO probe_collectors (probe_id, os, collector, "
                "  params_json, implementation_note, requires, enabled) "
                "VALUES (:probe_id, :os, :collector, :params_json, NULL, "
                "  NULL, 1)"), dict(row, probe_id=probe_id))

    @DatabaseHelper._sessionm
    def create_probe(self, session, login, probe):
        """Create a scripted probe owned by the caller."""
        login = _login(login)
        if not login:
            logger.warning("Reflex: probe creation refused, no login")
            return refused(REFUSAL_FORBIDDEN,
                           "A probe is created by somebody: no login was sent",
                           'login', reason=RefusalReason.LOGIN_REQUIRED)
        try:
            values = self._validate_probe_payload(probe, login=login,
                                                  session=session)
        except ReflexValidationError as e:
            logger.warning("Reflex: invalid probe payload: %s" % e)
            return refused_from(e)

        try:
            conditions = validate_condition_set(probe.get('conditions'),
                                                values['value_type'])
        except ReflexValidationError as e:
            rank = getattr(e, 'condition', 0)
            logger.warning("Reflex: probe creation refused, condition %d: %s"
                           % (rank, e))
            return refused_from(e, condition=rank)

        collectors = values.pop('collectors')
        values['owner_login'] = login
        try:
            values['probe_key'], values['metric_key'] = self._script_keys(
                session, values['label'])
            result = session.execute(text(
                # min_interval_seconds and default_interval_seconds are
                # left to the DEFAULT the schema gives them.
                "INSERT INTO probes (probe_key, label, description, category, "
                "  probe_type, metric_key, unit, value_type, os_support, "
                "  is_builtin, visibility, entity_id, owner_login, enabled, "
                "  created_at, updated_at) "
                "VALUES (:probe_key, :label, :description, :category, "
                "  'script', :metric_key, :unit, :value_type, :os_support, "
                "  0, :visibility, :entity_id, :owner_login, :enabled, "
                "  NOW(), NOW())"), values)
            probe_id = _to_int(result.lastrowid, 0)
            if not probe_id:
                probe_id = _to_int(session.execute(
                    text("SELECT id FROM probes WHERE probe_key = :probe_key"),
                    {'probe_key': values['probe_key']}).scalar(), 0)
            if not probe_id:
                session.rollback()
                return refused(REFUSAL_FAILED,
                               "The probe was written but its identifier "
                               "could not be read back")
            self._write_script_collectors(session, probe_id, collectors)
            for clean in conditions:
                session.execute(text(
                    "INSERT INTO probe_conditions (probe_id, operator, "
                    "  default_threshold_value, default_threshold_value2, "
                    "  default_threshold_text, default_duration_seconds, "
                    "  default_severity, default_message_template, "
                    "  default_enabled, display_order) "
                    "VALUES (:probe_id, :operator, :threshold_value, "
                    "  :threshold_value2, :threshold_text, :duration_seconds, "
                    "  :severity, :message_template, :enabled, "
                    "  :display_order)"), dict(clean, probe_id=probe_id))
            session.commit()
        except IntegrityError:
            session.rollback()
            logger.warning("Reflex: probe key '%s' already exists"
                           % values.get('probe_key'))
            return refused(REFUSAL_FAILED,
                           "The probe could not be created, another one was "
                           "being created under the same name: try again")
        except Exception as e:
            session.rollback()
            logger.error("Reflex: probe creation failed: %s" % e)
            return refused(REFUSAL_FAILED, "The probe could not be created")
        return probe_id

    @DatabaseHelper._sessionm
    def update_probe(self, session, login, probe_id, probe):
        """Update a probe the caller owns."""
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)
        if access['is_builtin']:
            logger.warning("Reflex: probe %s is built-in and cannot be modified"
                           % probe_id)
            return refused(REFUSAL_READONLY,
                           "A shipped probe is read only: duplicate it to "
                           "obtain an editable variant")
        if not access['can_write']:
            logger.warning("Reflex: login '%s' has no write access on probe %s"
                           % (login, probe_id))
            return refused(REFUSAL_FORBIDDEN,
                           "Only the owner of this probe may change its "
                           "definition: duplicate it to obtain a variant of "
                           "your own")

        source = dict(access['probe'])
        scripted = source.get('probe_type') == 'script'
        if scripted:
            source.update(self._script_commands(session, probe_id))
        try:
            values = self._validate_probe_payload(
                probe, partial_source=source, login=login, scripted=scripted,
                session=session, probe_id=probe_id)
        except ReflexValidationError as e:
            logger.warning("Reflex: invalid probe payload: %s" % e)
            return refused_from(e)

        # Judged against the value type this payload settles, and before the
        # first write: a set refused must refuse the edit whole.
        prepared = None
        if probe.get('conditions') is not None:
            try:
                prepared = validate_condition_set(probe['conditions'],
                                                  values['value_type'])
            except ReflexValidationError as e:
                rank = getattr(e, 'condition', 0)
                logger.warning("Reflex: probe %s update refused, condition "
                               "%d: %s" % (_to_int(probe_id, 0), rank, e))
                return refused_from(e, condition=rank)

        # A condition requalified from one value type to another is not the
        # same condition: watching a number pass 85 and watching a state turn
        # true are two watches, and the identifier the console sent back names
        # the first.
        if prepared and values['value_type'] != source.get('value_type'):
            for clean in prepared:
                clean['condition_id'] = 0

        # The switch is left alone, whatever the payload carries: a probe keeps
        # its state of service across an edit of its definition.
        values.pop('enabled', None)

        collectors = values.pop('collectors', None)
        values['probe_id'] = _to_int(probe_id, 0)
        distributed = any(
            values.get(field) != source.get(field)
            for field in ('label', 'unit', 'value_type', 'os_support'))
        if collectors is not None and not distributed:
            current = sorted(
                (row.get('os'), row.get('collector'), row.get('params_json'),
                 row.get('requires'), _to_int(row.get('enabled'), 0))
                for row in _rows(session.execute(text(
                    "SELECT os, collector, params_json, requires, enabled "
                    "  FROM probe_collectors WHERE probe_id = :probe_id"),
                    {'probe_id': values['probe_id']})))
            distributed = current != sorted(
                (row['os'], row['collector'], row['params_json'], None, 1)
                for row in collectors)
        resolved = 0
        try:
            if prepared is not None and not self._lock_editable_probe(
                    session, values['probe_id']):
                session.rollback()
                return refused(REFUSAL_READONLY,
                               "A shipped probe is read only: duplicate it to "
                               "obtain an editable variant")
            session.execute(text(
                "UPDATE probes SET label = :label, "
                "  description = :description, category = :category, "
                "  unit = :unit, "
                "  value_type = :value_type, os_support = :os_support, "
                "  min_interval_seconds = :min_interval_seconds, "
                "  default_interval_seconds = :default_interval_seconds, "
                "  visibility = :visibility, entity_id = :entity_id, "
                "  updated_at = NOW() "
                " WHERE id = :probe_id AND is_builtin = 0"), values)
            if collectors is not None:
                self._write_script_collectors(session, values['probe_id'],
                                              collectors)
            if prepared is not None:
                resolved = self._replace_probe_conditions(
                    session, values['probe_id'], prepared)
            if distributed:
                _mark_config_change(session, 'probe', values['probe_id'])
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: probe update failed: %s" % e)
            return refused(REFUSAL_FAILED, "The probe could not be updated")
        if resolved:
            logger.info("Reflex: probe %s edited by '%s', %d alert(s) "
                        "resolved with their removed condition"
                        % (values['probe_id'], login, resolved))
        return True

    @DatabaseHelper._sessionm
    def delete_probe(self, session, login, probe_id):
        """Delete a probe. Owner only, and never a built-in one.

        Returns True, or the structure built by `refused`.
        """
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)
        if access['is_builtin']:
            logger.warning("Reflex: probe %s is built-in and cannot be deleted"
                           % probe_id)
            return refused(REFUSAL_READONLY,
                           "A shipped probe cannot be deleted: turn it off if "
                           "it does not suit this estate")
        if not access['is_owner']:
            logger.warning("Reflex: login '%s' does not own probe %s"
                           % (login, probe_id))
            return refused(REFUSAL_FORBIDDEN,
                           "Only the owner of this probe may delete it")
        try:
            _mark_target_changes(session, [
                (row.get('target_type'), row.get('target_id'))
                for row in _rows(session.execute(text(
                    "SELECT target_type, target_id FROM probe_assignments "
                    " WHERE probe_id = :probe_id"),
                    {'probe_id': _to_int(probe_id, 0)}))])
            _mark_config_change(session, 'probe', probe_id)
            # Conditions, collectors, assignments and alerts follow through
            # the foreign keys declared by the schema.
            session.execute(
                text("DELETE FROM probes WHERE id = :probe_id AND is_builtin = 0"),
                {'probe_id': _to_int(probe_id, 0)})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: probe deletion failed: %s" % e)
            return refused(REFUSAL_FAILED, "The probe could not be deleted")
        return True

    def _free_copy_label(self, session, base, scope):
        """A name for a copy that no probe of its scope already bears."""
        rank = 1
        while rank <= MAX_PROBE_COPIES:
            suffix = '' if rank <= 1 else " (%d)" % rank
            # Truncated so the suffix still fits in the column, exactly as the
            # single name was truncated before it was numbered.
            candidate = base[:255 - len(suffix)] + suffix
            if not self._label_conflict(session, candidate, scope):
                return candidate
            rank += 1
        return None

    @DatabaseHelper._sessionm
    def duplicate_probe(self, session, login, probe_id, label=None,
                        entity_id=None):
        """Copy a visible probe into a probe owned by the caller."""
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A copy belongs to somebody: no login was sent",
                           'login', reason=RefusalReason.LOGIN_REQUIRED)
        try:
            label = _clean_str(label, 255, 'label')
        except ReflexValidationError as e:
            logger.warning("Reflex: invalid label for the copy: %s" % e)
            return refused_from(e)
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)

        source = access['probe']
        try:
            # Tested against the empty value and not on truth: entity 0 is
            # the root entity of GLPI, which a truth test would read as an
            # entity nobody asked for.
            asked = str(entity_id).strip() if entity_id is not None else ''
            scope = self._resolve_scope(login, {'entity_id': asked}
                                        if asked else {})
        except ReflexValidationError as e:
            logger.info("Reflex: the copy of probe %s stays private (%s)"
                        % (_to_int(probe_id, 0), e))
            scope = {'visibility': 'private', 'entity_id': None}
        # Settled before the name, which is now judged inside that scope.
        scope = dict(scope, owner_login=login)

        # Truncated so that the longest suffix the loop can append still
        # fits in the column.
        base_key = str(source.get('probe_key') or 'probe')[:118]
        new_key = "%s_copy" % base_key
        rank = 1
        while _to_int(session.execute(
                text("SELECT COUNT(*) FROM probes WHERE probe_key = :probe_key"),
                {'probe_key': new_key}).scalar(), 0):
            rank += 1
            if rank > MAX_PROBE_COPIES:
                logger.warning("Reflex: too many copies of probe '%s'" % base_key)
                return refused(REFUSAL_INVALID,
                               "This probe already has %d copies: rename or "
                               "delete some before making another"
                               % MAX_PROBE_COPIES,
                               reason=RefusalReason.LIMIT_REACHED)
            new_key = "%s_copy%d" % (base_key, rank)

        label = self._free_copy_label(
            session, label or "%s (copy)" % (source.get('label') or ''),
            scope)
        if label is None:
            logger.warning("Reflex: no free name left for a copy of probe %s"
                           % _to_int(probe_id, 0))
            return refused(REFUSAL_INVALID,
                           "No name is left for a copy of this probe: rename "
                           "or delete some of the %d existing ones"
                           % MAX_PROBE_COPIES, 'label',
                           reason=RefusalReason.LIMIT_REACHED)
        params = {
            'probe_key': new_key,
            'probe_type': ('script' if source.get('probe_type') == 'script'
                           else 'builtin'),
            'label': label,
            'description': source.get('description'),
            'category': source.get('category'),
            'metric_key': (SCRIPT_METRIC_KEY_PREFIX + new_key
                           if source.get('probe_type') == 'script'
                           else source.get('metric_key')),
            'unit': source.get('unit'),
            'value_type': source.get('value_type'),
            'plottable': _to_int(source.get('plottable'), 1),
            'os_support': source.get('os_support'),
            'min_interval_seconds': _to_int(source.get('min_interval_seconds'), 300),
            'default_interval_seconds': _to_int(
                source.get('default_interval_seconds'), 300),
            'owner_login': login,
            'enabled': _to_int(source.get('enabled'), 1),
            'source_id': _to_int(probe_id, 0),
            'visibility': scope['visibility'],
            'entity_id': scope['entity_id'],
        }
        try:
            result = session.execute(text(
                "INSERT INTO probes (probe_key, label, description, category, "
                "  probe_type, metric_key, unit, value_type, plottable, "
                "  os_support, "
                "  min_interval_seconds, default_interval_seconds, is_builtin, "
                "  visibility, entity_id, owner_login, enabled, created_at, "
                "  updated_at) "
                "VALUES (:probe_key, :label, :description, :category, "
                "  :probe_type, :metric_key, :unit, :value_type, :plottable, "
                "  :os_support, "
                "  :min_interval_seconds, :default_interval_seconds, 0, "
                "  :visibility, :entity_id, :owner_login, :enabled, NOW(), "
                "  NOW())"), params)
            new_id = _to_int(result.lastrowid, 0)
            if not new_id:
                new_id = _to_int(session.execute(
                    text("SELECT id FROM probes WHERE probe_key = :probe_key"),
                    {'probe_key': new_key}).scalar(), 0)
            if not new_id:
                session.rollback()
                return refused(REFUSAL_FAILED,
                               "The copy was written but its identifier could "
                               "not be read back")

            # The copy is a personal probe, so what it inherits is what the
            # source condition applies today, override included, flattened into
            # its own definition.
            scope = self._condition_scope(self._reader_entity(login))
            session.execute(text(
                "INSERT INTO probe_conditions (probe_id, operator, "
                "  default_threshold_value, default_threshold_value2, "
                "  default_threshold_text, default_duration_seconds, "
                "  default_severity, default_message_template, "
                "  default_enabled, display_order) "
                "SELECT :new_id, pc.operator, " +
                ", ".join(condition_field_sql(field, 'pc', scope['alias'])
                          for field in CONDITION_OVERRIDE_FIELDS) +
                ", pc.display_order "
                "  FROM probe_conditions pc " + scope['join'] +
                " WHERE pc.probe_id = :source_id"),
                dict(scope['params'], new_id=new_id,
                     source_id=params['source_id']))

            session.execute(text(
                "INSERT INTO probe_collectors (probe_id, os, collector, "
                "  params_json, implementation_note, requires, enabled) "
                "SELECT :new_id, os, collector, params_json, "
                "  implementation_note, requires, enabled "
                "  FROM probe_collectors WHERE probe_id = :source_id"),
                {'new_id': new_id, 'source_id': params['source_id']})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: probe duplication failed: %s" % e)
            return refused(REFUSAL_FAILED, "The probe could not be duplicated")
        return new_id

    @DatabaseHelper._sessionm
    def set_probe_visibility(self, session, login, probe_id, visibility,
                             entity_id=None):
        """Change the scope of a probe. Owner only.

        Returns True, or the structure built by `refused`.
        """
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)
        if access['is_builtin']:
            logger.warning("Reflex: the scope of built-in probe %s is read only"
                           % probe_id)
            return refused(REFUSAL_READONLY,
                           "A shipped probe is readable by everyone: its "
                           "scope is not editable")
        if not access['is_owner']:
            logger.warning("Reflex: login '%s' cannot change the scope of probe %s"
                           % (login, probe_id))
            return refused(REFUSAL_FORBIDDEN,
                           "Only the owner of this probe may change who reads "
                           "it")
        try:
            scope = self._resolve_scope(
                login, {'visibility': visibility, 'entity_id': entity_id},
                source=access['probe'])
            # Publishing a draft is the fourth way a name lands in an estate,
            # and the only one that moves an unchanged name: refused here too,
            # or a name refused at creation would be obtained by creating the
            # probe private and publishing it afterwards.
            self._check_label_free(session, access['probe'].get('label'),
                                   dict(scope, owner_login=login),
                                   exclude_id=probe_id,
                                   kept_label=access['probe'].get('label'))
        except ReflexValidationError as e:
            logger.warning("Reflex: scope refused on probe %s: %s"
                           % (_to_int(probe_id, 0), e))
            return refused_from(e)
        try:
            session.execute(text(
                "UPDATE probes SET visibility = :visibility, "
                "  entity_id = :entity_id, updated_at = NOW() "
                " WHERE id = :probe_id AND is_builtin = 0"),
                {'visibility': scope['visibility'],
                 'entity_id': scope['entity_id'],
                 'probe_id': _to_int(probe_id, 0)})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: scope update failed: %s" % e)
            return refused(REFUSAL_FAILED, "The scope could not be changed")
        return True

    # =========================================================================
    # Operating right on a probe and on its conditions
    # =========================================================================
    def _may_operate(self, access):
        """Tell whether a caller may adapt the conditions of a probe.

        A shipped probe is adapted by every estate, each for itself: an
        override is written per entity and reaches nobody else.
        """
        if not access['exists']:
            return False
        if access['is_builtin']:
            return True
        return bool(access['can_write'])

    # =========================================================================
    # Probe conditions
    # =========================================================================
    def _lock_editable_probe(self, session, probe_id):
        """Lock a probe and answer whether it is still an editable one."""
        return session.execute(text(
            "SELECT id FROM probes "
            " WHERE id = :probe_id AND is_builtin = 0 FOR UPDATE"),
            {'probe_id': _to_int(probe_id, 0)}).first() is not None

    def _replace_probe_conditions(self, session, probe_id, prepared):
        """Bring the conditions of a probe to `prepared`, without committing.

        Returns the number of alerts closed that way.
        """
        probe_id = _to_int(probe_id, 0)
        for clean in prepared:
            clean['probe_id'] = probe_id
        resolved = 0
        existing = set(
            _to_int(row[0], 0) for row in session.execute(text(
                "SELECT id FROM probe_conditions "
                " WHERE probe_id = :probe_id FOR UPDATE"),
                {'probe_id': probe_id}))

        kept = set()
        for clean in prepared:
            if clean['condition_id'] in existing and \
                    clean['condition_id'] not in kept:
                kept.add(clean['condition_id'])
            else:
                clean['condition_id'] = 0

        removed = sorted(existing - kept)
        if removed:
            fragment, params = _placeholders('removed', removed)
            params['probe_id'] = probe_id
            params['reason'] = ALERT_RESOLVED_BY_CONDITION_REMOVED
            resolved = _to_int(session.execute(text(
                "UPDATE alerts SET status = 'resolved', "
                "       resolved_at = NOW(), resolved_reason = :reason "
                " WHERE probe_id = :probe_id "
                "   AND condition_id IN (" + fragment + ") "
                "   AND " + alert_active_sql('')), params).rowcount, 0)
            session.execute(text(
                "DELETE FROM probe_conditions "
                " WHERE probe_id = :probe_id "
                "   AND id IN (" + fragment + ")"), params)

        if kept:
            # uk_probe_order refuses two rows of a probe on one rank, even for
            # the time of a statement: an exchange of two ranks would collide
            # on the first update.
            fragment, params = _placeholders('kept', sorted(kept))
            params['probe_id'] = probe_id
            session.execute(text(
                "UPDATE probe_conditions SET display_order = -id "
                " WHERE probe_id = :probe_id "
                "   AND id IN (" + fragment + ")"), params)

        for clean in prepared:
            # The definition of the owner is what the probe ships: a probe
            # one wrote oneself has nothing above it to override.
            if clean['condition_id']:
                session.execute(text(
                    "UPDATE probe_conditions "
                    "   SET operator = :operator, "
                    "       default_threshold_value = :threshold_value, "
                    "       default_threshold_value2 = :threshold_value2, "
                    "       default_threshold_text = :threshold_text, "
                    "       default_duration_seconds = :duration_seconds, "
                    "       default_severity = :severity, "
                    "       default_message_template = :message_template, "
                    "       default_enabled = :enabled, "
                    "       display_order = :display_order "
                    " WHERE id = :condition_id AND probe_id = :probe_id"),
                    clean)
                continue
            session.execute(text(
                "INSERT INTO probe_conditions (probe_id, operator, "
                "  default_threshold_value, default_threshold_value2, "
                "  default_threshold_text, default_duration_seconds, "
                "  default_severity, default_message_template, "
                "  default_enabled, display_order) "
                "VALUES (:probe_id, :operator, :threshold_value, "
                "  :threshold_value2, :threshold_text, :duration_seconds, "
                "  :severity, :message_template, :enabled, :display_order)"),
                clean)
        return resolved

    @DatabaseHelper._sessionm
    def set_probe_conditions(self, session, login, probe_id, conditions):
        """Bring the conditions of a probe to the complete set sent."""
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)
        if access['is_builtin']:
            logger.warning("Reflex: conditions of built-in probe %s are read only"
                           % probe_id)
            return refused(REFUSAL_READONLY,
                           "The conditions of a shipped probe are read only: "
                           "duplicate the probe to obtain an editable variant")
        if not access['can_write']:
            logger.warning("Reflex: login '%s' has no write access on probe %s"
                           % (login, probe_id))
            return refused(REFUSAL_FORBIDDEN,
                           "Only the owner of this probe may change its "
                           "conditions: duplicate it to obtain a variant of "
                           "your own")

        value_type = access['probe'].get('value_type', 'numeric')
        try:
            prepared = validate_condition_set(conditions, value_type)
        except ReflexValidationError as e:
            rank = getattr(e, 'condition', 0)
            logger.warning("Reflex: probe %s, condition %d refused: %s"
                           % (_to_int(probe_id, 0), rank, e))
            return refused_from(e, condition=rank)

        probe_id = _to_int(probe_id, 0)
        resolved = 0
        try:
            if not self._lock_editable_probe(session, probe_id):
                session.rollback()
                return refused(REFUSAL_READONLY,
                               "The conditions of a shipped probe are read "
                               "only: duplicate the probe to obtain an "
                               "editable variant")
            resolved = self._replace_probe_conditions(session, probe_id,
                                                      prepared)
            session.execute(
                text("UPDATE probes SET updated_at = NOW() WHERE id = :probe_id"),
                {'probe_id': probe_id})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: conditions update failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The conditions could not be written")
        if resolved:
            logger.info("Reflex: conditions of probe %s rewritten by '%s', %d "
                        "alert(s) resolved with their removed condition"
                        % (probe_id, login, resolved))
        return True

    def _condition_for_override(self, session, condition_id):
        """Read a condition and the probe it hangs on, in one statement."""
        condition_id = _to_int(condition_id, 0)
        if condition_id <= 0:
            return None
        return _one(session.execute(text(
            "SELECT pc.*, p.value_type FROM probe_conditions pc "
            "  JOIN probes p ON p.id = pc.probe_id "
            " WHERE pc.id = :condition_id"), {'condition_id': condition_id}))

    def _write_entity_override(self, session, condition_id, entity, values,
                               login):
        """Write, or remove, the setting of one condition for one entity."""
        params = {'condition_id': condition_id, 'entity_id': str(entity)}
        session.execute(text(
            "DELETE FROM probe_condition_overrides "
            " WHERE condition_id = :condition_id "
            "   AND entity_id = :entity_id"), params)
        if not any(values[field] is not None
                   for field in CONDITION_OVERRIDE_FIELDS):
            return
        params.update({'customized_by': login,
                       'customized_at': datetime.now()})
        params.update(dict((field, values[field])
                           for field in CONDITION_OVERRIDE_FIELDS))
        session.execute(text(
            "INSERT INTO probe_condition_overrides "
            "  (condition_id, entity_id, "
            + ", ".join(CONDITION_OVERRIDE_FIELDS) +
            ", customized_by, customized_at) "
            "VALUES (:condition_id, :entity_id, "
            + ", ".join(":%s" % field for field in CONDITION_OVERRIDE_FIELDS) +
            ", :customized_by, :customized_at)"), params)

    def _override_entity(self, login, condition_id, entity_id, gesture):
        """The entity a set or a reset writes, or the refusal to answer.

        Returns (entity, None) or (None, refusal).
        """
        entity = self._chosen_entity(login, entity_id)
        if entity is not None:
            return entity, None
        wanted = '' if entity_id is None else str(entity_id).strip()
        if wanted:
            logger.warning("Reflex: login '%s' cannot %s condition %s for "
                           "entity %s, outside his estate"
                           % (login, gesture, condition_id, wanted))
            return None, refused(REFUSAL_FORBIDDEN,
                                 "This entity is outside your estate, its "
                                 "conditions cannot be adapted")
        logger.warning("Reflex: login '%s' reaches no entity, condition %s "
                       "not changed" % (login, condition_id))
        return None, refused(REFUSAL_FORBIDDEN,
                             "Your estate cannot be resolved, the condition "
                             "cannot be adapted for it")

    @DatabaseHelper._sessionm
    def set_condition_override(self, session, login, condition_id, overrides,
                               entity_id=''):
        """Set what the caller chose for one condition, for one entity."""
        login = _login(login)
        row = self._condition_for_override(session, condition_id)
        if row is None:
            return refused(REFUSAL_MISSING,
                           "This condition does not exist any more")

        access = self._probe_access(session, login, row.get('probe_id'))
        if not self._may_operate(access):
            logger.warning("Reflex: login '%s' cannot set condition %s"
                           % (login, condition_id))
            return refused(REFUSAL_FORBIDDEN,
                           "You may not adapt the conditions of this probe")

        entity, refusal = self._override_entity(login, condition_id,
                                                entity_id, 'set')
        if refusal is not None:
            return refusal

        try:
            values = validate_condition_override(row, overrides,
                                                 row.get('value_type'))
        except ReflexValidationError as e:
            logger.warning("Reflex: condition %s override refused: %s"
                           % (_to_int(condition_id, 0), e))
            return refused_from(e)

        condition_id = _to_int(condition_id, 0)
        try:
            self._write_entity_override(session, condition_id, entity,
                                        values, login)
            session.execute(text(
                "UPDATE probes SET updated_at = NOW() WHERE id = :probe_id"),
                {'probe_id': _to_int(row.get('probe_id'), 0)})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: condition override failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The adaptation could not be written")
        self._close_overridden_alerts(session, condition_id, entity)
        return True

    @DatabaseHelper._sessionm
    def reset_condition_override(self, session, login, condition_id,
                                 entity_id=''):
        """Give a condition back to what the product ships, for one entity.

        Returns True, or the structure built by `refused`.
        """
        login = _login(login)
        row = self._condition_for_override(session, condition_id)
        if row is None:
            return refused(REFUSAL_MISSING,
                           "This condition does not exist any more")

        access = self._probe_access(session, login, row.get('probe_id'))
        if not self._may_operate(access):
            logger.warning("Reflex: login '%s' cannot reset condition %s"
                           % (login, condition_id))
            return refused(REFUSAL_FORBIDDEN,
                           "You may not adapt the conditions of this probe")

        entity, refusal = self._override_entity(login, condition_id,
                                                entity_id, 'reset')
        if refusal is not None:
            return refusal

        condition_id = _to_int(condition_id, 0)
        try:
            # A setting made of nothing is the removal of the row, which is
            # what giving an estate back to the shipped values means.
            self._write_entity_override(
                session, condition_id, entity,
                dict((field, None) for field in CONDITION_OVERRIDE_FIELDS),
                login)
            session.execute(text(
                "UPDATE probes SET updated_at = NOW() WHERE id = :probe_id"),
                {'probe_id': _to_int(row.get('probe_id'), 0)})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: condition reset failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The shipped values could not be restored")
        self._close_overridden_alerts(session, condition_id, entity)
        return True

    def _probe_cadence(self, session, probe_id):
        """Cadence the substitute judges a probe on, as its probe_interval."""
        row = _one(session.execute(text(
            "SELECT MAX(a.interval_seconds) AS assigned, "
            "       MAX(p.default_interval_seconds) AS declared "
            "  FROM probes p "
            "  LEFT JOIN probe_assignments a ON a.probe_id = p.id "
            " WHERE p.id = :probe_id"), {'probe_id': probe_id})) or {}
        interval = _to_int(row.get('assigned'), 0)
        if interval <= 0:
            interval = _to_int(row.get('declared'), 0)
        return interval if interval > 0 else SUBSTITUTE_DEFAULT_INTERVAL_SECONDS

    def _close_overridden_alerts(self, session, condition_id, entity):
        """Close the alerts of one entity its new setting certainly rejects."""
        try:
            scope = self._condition_scope(entity)
            alias = scope['alias']
            moved = " AND ".join(
                "a.%s <=> %s" % (frozen, "pc.operator" if key == 'operator'
                                 else condition_field_sql(key, 'pc', alias))
                for frozen, key in ALERT_FREEZE_FIELDS)
            params = dict(scope['params'])
            params.update({'condition_id': condition_id,
                           'entity': str(entity)})
            alerts = _rows(session.execute(text(
                "SELECT a.id, a.machines_id, a.probe_id, pc.operator, "
                + condition_effective_sql('pc', alias) +
                "  FROM alerts a "
                "  JOIN probe_conditions pc ON pc.id = a.condition_id "
                "  JOIN probes p ON p.id = a.probe_id AND p.enabled <> 0 "
                "  JOIN xmppmaster.machines xm ON xm.id = a.machines_id "
                "  JOIN xmppmaster.glpi_entity xe "
                "    ON xe.id = xm.glpi_entity_id "
                + scope['join'] +
                " WHERE a.condition_id = :condition_id "
                "   AND " + alert_active_sql('a') +
                "   AND CAST(xe.glpi_id AS CHAR) = :entity "
                "   AND (" + condition_field_sql('enabled', 'pc', alias) +
                " = 0 OR (a.operator_at_trigger IS NOT NULL "
                "         AND NOT (" + moved + ")))"), params))
            if not alerts:
                return 0

            condition = alerts[0]
            closing = []
            if not _to_int(condition.get('enabled'), 0):
                reason = ALERT_RESOLVED_BY_CONDITION_DISABLE
                closing = [row['id'] for row in alerts]
            elif (str(condition.get('operator') or '').strip().lower()
                  not in THRESHOLDLESS_OPERATORS):
                reason = ALERT_RESOLVED_BY_CONDITION_CHANGE
                probe_id = _to_int(condition.get('probe_id'), 0)
                span = (_to_int(condition.get('duration_seconds'), 0)
                        + self._probe_cadence(session, probe_id) + 1)
                # received_at is stamped by the database: the window is cut
                # on its clock, never on the one of this process.
                now = _read_moment(session.execute(
                    text("SELECT NOW()")).scalar())
                if now is None:
                    raise ValueError("the clock of the database cannot be read")
                since = now - timedelta(seconds=span + 1)
                machines = sorted(set(_to_int(row['machines_id'], 0)
                                      for row in alerts))
                measures = {}
                for start in range(0, len(machines), IDS_PER_STATEMENT):
                    fragment, measure_params = _placeholders(
                        'mid', machines[start:start + IDS_PER_STATEMENT])
                    measure_params.update({'probe_id': probe_id,
                                           'since': since})
                    for measure in _rows(session.execute(text(
                            "SELECT machines_id, value_num, value_text, status "
                            "  FROM probe_measures "
                            " WHERE probe_id = :probe_id "
                            "   AND received_at >= :since "
                            "   AND machines_id IN (" + fragment + ") "
                            " ORDER BY machines_id ASC, received_at DESC"),
                            measure_params)):
                        measures.setdefault(
                            _to_int(measure['machines_id'], 0),
                            []).append(measure)
                for row in alerts:
                    decided = False
                    stands = False
                    for measure in measures.get(
                            _to_int(row['machines_id'], 0), []):
                        if str(measure.get('status') or 'ok') == 'unavailable':
                            continue
                        holds = condition_holds_now(
                            condition, measure.get('value_num'),
                            measure.get('value_text'))
                        if holds:
                            stands = True
                            break
                        if holds is False:
                            decided = True
                    if decided and not stands:
                        closing.append(row['id'])
            if not closing:
                return 0

            closed = 0
            for start in range(0, len(closing), IDS_PER_STATEMENT):
                fragment, close_params = _placeholders(
                    'alert', closing[start:start + IDS_PER_STATEMENT])
                close_params['reason'] = reason
                result = session.execute(text(
                    "UPDATE alerts SET status = 'resolved', "
                    "       resolved_at = NOW(), resolved_reason = :reason "
                    " WHERE id IN (" + fragment + ") "
                    "   AND " + alert_active_sql('')), close_params)
                closed += _to_int(result.rowcount, 0)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: alerts of condition %s for entity %s left "
                         "to the sweep, closing failed: %s"
                         % (condition_id, entity, e))
            return 0
        if closed:
            logger.info("Reflex: %d alert(s) of condition %s closed for "
                        "entity %s, reason %s"
                        % (closed, condition_id, entity, reason))
        return closed

    # =========================================================================
    # Probe assignments
    # =========================================================================
    def _clamped_interval(self, access, interval_seconds):
        """Cadence actually written, never below the floor of the probe."""
        floor = max(_to_int(access['probe'].get('min_interval_seconds'), 0), 1)
        interval = _to_int(interval_seconds, 0)
        if interval < floor:
            logger.info("Reflex: interval %s raised to the floor %s for probe %s"
                        % (interval, floor, access['probe'].get('id')))
            interval = floor
        return interval

    def _write_assignments(self, session, login, probe_id, target_type,
                           target_ids, interval, language=None):
        """Create or refresh the assignments of one probe on given targets."""
        probe_id = _to_int(probe_id, 0)
        language = language or None
        existing = {}
        # The identifiers come from the caller: they are expanded into
        # generated placeholders, so the statement stays ours.
        fragment, params = _placeholders('target', target_ids)
        params['probe_id'] = probe_id
        params['target_type'] = target_type
        changed = []
        for row in _rows(session.execute(text(
                "SELECT id, target_id, interval_seconds FROM probe_assignments "
                " WHERE probe_id = :probe_id "
                "   AND target_type = :target_type "
                "   AND target_id IN (" + fragment + ")"), params)):
            key = str(row.get('target_id') or '')
            existing[key] = _to_int(row.get('id'), 0)
            if _to_int(row.get('interval_seconds'), 0) != interval:
                changed.append(key)

        if existing:
            # An assignment already placed keeps its row and takes the new
            # cadence: the caller asked for a state, not for a second row.
            fragment, params = _placeholders('row', list(existing.values()))
            params['interval_seconds'] = interval
            language_set = ""
            if language is not None:
                language_set = ", language = :language"
                params['language'] = language
            session.execute(text(
                "UPDATE probe_assignments "
                "   SET interval_seconds = :interval_seconds" + language_set +
                " WHERE id IN (" + fragment + ")"), params)

        assignment_ids = []
        for target_id in target_ids:
            key = str(target_id or '')
            if key in existing:
                assignment_ids.append(existing[key])
                continue
            result = session.execute(text(
                "INSERT INTO probe_assignments (probe_id, target_type, "
                "  target_id, interval_seconds, created_by, language, "
                "  created_at) "
                "VALUES (:probe_id, :target_type, :target_id, "
                "  :interval_seconds, :created_by, :language, NOW())"),
                {'probe_id': probe_id, 'target_type': target_type,
                 'target_id': target_id, 'interval_seconds': interval,
                 'created_by': login, 'language': language})
            assignment_ids.append(_to_int(result.lastrowid, 0) or 1)
            changed.append(key)
        _mark_config_change(session, target_type, changed)
        return assignment_ids

    @DatabaseHelper._sessionm
    def assign_probe(self, session, login, probe_id, target_type, target_id,
                     interval_seconds, language=None):
        """Place a probe on a target at a given cadence."""
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A placement is recorded against somebody: no "
                           "login was sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)

        if str(target_type or '').strip().lower() == 'all':
            target_type = 'entity'
            target_ids = list(self.entities_for_login(login))
            if not target_ids:
                logger.warning("Reflex: login '%s' places probe %s on the "
                               "whole park and reaches no entity"
                               % (login, probe_id))
                return refused(REFUSAL_FORBIDDEN,
                               "The estate you reach cannot be resolved, so "
                               "there is no park to place this probe on",
                               'target_id',
                               reason=RefusalReason.TARGET_FORBIDDEN)
        else:
            try:
                target_type = normalise_target_type(target_type)
                target_ids = [normalise_target_id(target_type, target_id)]
            except ReflexValidationError as e:
                logger.warning("Reflex: %s" % e)
                return refused_from(e)

        # Every target is judged, the expanded ones included: they come from
        # the estate of the caller, and the rule that says so is asked here
        # rather than trusted.
        for candidate in target_ids:
            if self._target_in_scope(session, login, target_type, candidate):
                continue
            logger.warning("Reflex: login '%s' cannot place probe %s on %s "
                           "target '%s'"
                           % (login, probe_id, target_type, candidate))
            return refused(REFUSAL_FORBIDDEN,
                           "This target is outside the estate you reach",
                           'target_id',
                           reason=RefusalReason.TARGET_FORBIDDEN)

        interval = self._clamped_interval(access, interval_seconds)

        try:
            assignment_ids = self._write_assignments(
                session, login, probe_id, target_type, target_ids, interval,
                language)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: probe assignment failed: %s" % e)
            return refused(REFUSAL_FAILED, "The probe could not be placed")
        if not assignment_ids:
            return refused(REFUSAL_FAILED,
                           "The placement was written but its identifier "
                           "could not be read back")
        # One integer answered whatever the number of rows written: the one
        # the caller is standing in front of, his own entity, or the first.
        reader = self._reader_entity(login)
        for candidate, assignment_id in zip(target_ids, assignment_ids):
            if target_type == 'entity' and str(candidate) == str(reader):
                return assignment_id
        return assignment_ids[0]

    @DatabaseHelper._sessionm
    def assign_probe_bulk(self, session, login, probe_id, target_type,
                          target_ids, interval_seconds, language=None):
        """Place a probe on a selection of targets in a single gesture."""
        outcome = {'success': True, 'assigned': 0, 'rejected': 0}
        login = _login(login)

        def batch_refused(code, message, field=None, reason='', asked=0):
            """Refusal of a whole batch, counters included."""
            answer = refused(code, message, field, reason=reason)
            answer['assigned'] = 0
            answer['rejected'] = _to_int(asked, 0)
            return answer

        if target_ids is None:
            candidates = []
        elif isinstance(target_ids, (list, tuple, set)):
            candidates = list(target_ids)
        elif isinstance(target_ids, (str, bytes)):
            candidates = str(target_ids).split(',')
        else:
            candidates = [target_ids]
        if not candidates:
            return batch_refused(REFUSAL_INVALID,
                                 "No target was sent", 'target_ids',
                                 RefusalReason.FIELD_REQUIRED, 0)

        outcome['rejected'] = len(candidates)
        if not login:
            return batch_refused(REFUSAL_FORBIDDEN,
                                 "A placement is recorded against somebody: "
                                 "no login was sent", 'login',
                                 RefusalReason.LOGIN_REQUIRED, len(candidates))

        if len(candidates) > MAX_BULK_ASSIGNMENTS:
            logger.warning(
                "Reflex: batch of %d targets refused for probe %s, the limit "
                "is %d" % (len(candidates), probe_id, MAX_BULK_ASSIGNMENTS))
            return batch_refused(
                REFUSAL_INVALID,
                "A batch places at most %d targets at a time, %d were sent"
                % (MAX_BULK_ASSIGNMENTS, len(candidates)), 'target_ids',
                RefusalReason.LIMIT_REACHED, len(candidates))

        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            logger.warning("Reflex: login '%s' cannot place probe %s on %d "
                           "targets" % (login, probe_id, len(candidates)))
            return batch_refused(REFUSAL_MISSING,
                                 PROBE_OUT_OF_REACH, None, '',
                                 len(candidates))

        try:
            target_type = normalise_target_type(target_type)
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return batch_refused(REFUSAL_INVALID, str(e),
                                 getattr(e, 'field', None),
                                 getattr(e, 'reason', ''), len(candidates))

        # A bad identifier costs its own line and nothing else: the rest of
        # the selection is placed, and the count says how many were dropped.
        accepted = []
        seen = set()
        for candidate in candidates:
            try:
                target_id = normalise_target_id(target_type, candidate)
            except ReflexValidationError:
                continue
            key = str(target_id or '')
            if key in seen:
                continue
            seen.add(key)
            accepted.append(target_id)
        if not accepted:
            logger.warning("Reflex: no usable target among the %d sent for "
                           "probe %s" % (len(candidates), probe_id))
            return batch_refused(
                REFUSAL_INVALID,
                "None of the %d identifiers sent names a usable target"
                % len(candidates), 'target_ids',
                RefusalReason.FIELD_FORMAT_INVALID, len(candidates))

        # One target outside the estate refuses the batch whole: the console
        # only offers targets the caller reaches, so a selection holding one
        # was not built by it.
        readable = self._memberships_readable(session)
        groups_readable = self._group_sharing_readable(session)
        for target_id in accepted:
            if self._target_in_scope(session, login, target_type, target_id,
                                     readable=readable,
                                     groups_readable=groups_readable):
                continue
            logger.warning("Reflex: login '%s' cannot place probe %s on %s "
                           "target '%s'"
                           % (login, probe_id, target_type, target_id))
            return batch_refused(
                REFUSAL_FORBIDDEN,
                "This selection holds a target outside the estate you reach",
                'target_ids', RefusalReason.TARGET_FORBIDDEN, len(candidates))

        interval = self._clamped_interval(access, interval_seconds)

        try:
            assignment_ids = self._write_assignments(
                session, login, probe_id, target_type, accepted, interval,
                language)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: batch probe assignment failed: %s" % e)
            return batch_refused(REFUSAL_FAILED,
                                 "The probe could not be placed on this "
                                 "selection", None, '', len(candidates))

        outcome['assigned'] = len(assignment_ids)
        outcome['rejected'] = len(candidates) - outcome['assigned']
        logger.info("Reflex: probe %s placed on %d %s target(s) by '%s', "
                    "%d identifier(s) rejected"
                    % (_to_int(probe_id, 0), outcome['assigned'], target_type,
                       login, outcome['rejected']))
        return outcome

    # =========================================================================
    # Alerts left without measures
    # =========================================================================
    # An alert closes when a measure comes back under the threshold.
    def _resolve_alerts_on_machine(self, session, probe_id, machines_id,
                                   reason):
        """Close the still open alerts of one probe on one machine."""
        probe_id = _to_int(probe_id, 0)
        machines_id = _to_int(machines_id, 0)
        if probe_id <= 0 or machines_id <= 0:
            return 0
        result = session.execute(text(
            "UPDATE alerts SET status = 'resolved', resolved_at = NOW(), "
            "       resolved_reason = :reason "
            " WHERE probe_id = :probe_id AND machines_id = :machines_id "
            "   AND " + alert_active_sql('')),
            {'probe_id': probe_id, 'machines_id': machines_id,
             'reason': reason})
        return _to_int(result.rowcount, 0)

    def _resolve_alerts_off_coverage(self, session, machines_id, probe_ids):
        """Close the alerts of one machine on probes that no longer reach it.
        """
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return 0
        params = {'machines_id': machines_id,
                  'reason': ALERT_RESOLVED_BY_SCOPE}
        clauses = ["machines_id = :machines_id", alert_active_sql('')]
        kept = [_to_int(value, 0) for value in probe_ids or []]
        kept = [value for value in kept if value > 0]
        if kept:
            # The identifiers come from the coverage just built; they are
            # bound all the same.
            fragment, id_params = _placeholders('kept', kept)
            params.update(id_params)
            clauses.append("probe_id NOT IN (" + fragment + ")")
        result = session.execute(text(
            "UPDATE alerts SET status = 'resolved', resolved_at = NOW(), "
            "       resolved_reason = :reason "
            " WHERE " + " AND ".join(clauses)), params)
        return _to_int(result.rowcount, 0)

    def _resolve_alerts_after_unassign(self, session, probe_id, removed_ids,
                                       readable):
        """Close the alerts the removal of assignments leaves without
        measures.
        """
        probe_id = _to_int(probe_id, 0)
        removed = [value for value in (_to_int(raw, 0)
                                       for raw in removed_ids or [])
                   if value > 0]
        if probe_id <= 0 or not removed:
            return 0

        # Most removals leave no alert behind: answered by one indexed read,
        # without resolving any membership.
        if session.execute(text(
                "SELECT 1 FROM alerts "
                " WHERE probe_id = :probe_id AND " + alert_active_sql('') +
                " LIMIT 1"), {'probe_id': probe_id}).first() is None:
            return 0

        reach_sql = None
        if readable:
            reach_sql = membership_reach_sql()
        elif session.execute(text(
                "SELECT 1 FROM probe_assignments "
                " WHERE probe_id = :probe_id "
                "   AND target_type IN ('group', 'entity') LIMIT 1"),
                {'probe_id': probe_id}).first() is not None:
            logger.warning(
                "Reflex: alerts of probe %s left open after the removal of "
                "assignment(s) %s, the machines of its groups and entities "
                "cannot be read" % (probe_id, removed))
            return 0

        target_sql, target_params = machine_target_clauses(
            None, machine_column='alerts.machines_id', reach_sql=reach_sql)
        removed_fragment, params = _placeholders('removed', removed)
        params.update(target_params)
        params['probe_id'] = probe_id
        params['reason'] = ALERT_RESOLVED_BY_UNASSIGN
        result = session.execute(text(
            "UPDATE alerts SET status = 'resolved', resolved_at = NOW(), "
            "       resolved_reason = :reason "
            " WHERE probe_id = :probe_id AND " + alert_active_sql('') +
            "   AND EXISTS (SELECT 1 FROM probe_assignments pa "
            "                WHERE pa.probe_id = :probe_id "
            "                  AND pa.id IN (" + removed_fragment + ") "
            "                  AND " + target_sql + ") "
            "   AND (EXISTS (SELECT 1 FROM probe_exclusions px "
            "                 WHERE px.probe_id = :probe_id "
            "                   AND px.machines_id = alerts.machines_id) "
            "        OR NOT EXISTS (SELECT 1 FROM probe_assignments pa "
            "                WHERE pa.probe_id = :probe_id "
            "                  AND pa.id NOT IN (" + removed_fragment + ") "
            "                  AND " + target_sql + "))"), params)
        return _to_int(result.rowcount, 0)

    @DatabaseHelper._sessionm
    def unassign_probe(self, session, login, assignment_id):
        """Remove an assignment.

        Returns True, or the structure built by `refused`.
        """
        login = _login(login)
        assignment_id = _to_int(assignment_id, 0)
        if assignment_id <= 0:
            return refused(REFUSAL_INVALID, NO_ASSIGNMENT_NAMED,
                           'assignment_id',
                           reason=RefusalReason.FIELD_REQUIRED)

        scope_sql, params = self._assignment_scope(session, login)
        params['assignment_id'] = assignment_id
        row = _one(session.execute(text(
            "SELECT pa.id, pa.probe_id, pa.target_type, pa.target_id "
            "  FROM probe_assignments pa "
            "  JOIN probes p ON p.id = pa.probe_id "
            " WHERE pa.id = :assignment_id AND " + scope_sql), params))
        if row is None:
            return refused(REFUSAL_MISSING, ASSIGNMENT_GONE)

        access = self._probe_access(session, login, row.get('probe_id'))
        if not access['visible']:
            return refused(REFUSAL_MISSING, ASSIGNMENT_PROBE_HIDDEN)
        readable = self._memberships_readable(session)
        try:
            resolved = self._resolve_alerts_after_unassign(
                session, row.get('probe_id'), [assignment_id], readable)
            session.execute(
                text("DELETE FROM probe_assignments WHERE id = :assignment_id"),
                {'assignment_id': assignment_id})
            _mark_config_change(session, row.get('target_type'),
                                row.get('target_id'))
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: assignment removal failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The placement could not be removed")
        if resolved:
            logger.info("Reflex: assignment %s removed by '%s', %d alert(s) "
                        "resolved for lack of measures"
                        % (assignment_id, login, resolved))
        return True

    @DatabaseHelper._sessionm
    def update_assignment_interval(self, session, login, assignment_id,
                                   interval_seconds):
        """Change the cadence of one placement, and nothing else.

        Returns True, or the structure built by `refused`.
        """
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A change is checked against somebody: no login "
                           "was sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        assignment_id = _to_int(assignment_id, 0)
        if assignment_id <= 0:
            return refused(REFUSAL_INVALID, NO_ASSIGNMENT_NAMED,
                           'assignment_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        try:
            asked = _positive_seconds(interval_seconds, 'interval_seconds')
        except ReflexValidationError as e:
            return refused_from(e)

        scope_sql, params = self._assignment_scope(session, login)
        params['assignment_id'] = assignment_id
        row = _one(session.execute(text(
            "SELECT pa.id, pa.probe_id, pa.target_type, "
            "       pa.target_id, pa.interval_seconds "
            "  FROM probe_assignments pa "
            " WHERE pa.id = :assignment_id AND " + scope_sql), params))
        if row is None:
            return refused(REFUSAL_MISSING, ASSIGNMENT_GONE)

        access = self._probe_access(session, login, row.get('probe_id'))
        if not access['visible']:
            return refused(REFUSAL_MISSING, ASSIGNMENT_PROBE_HIDDEN)
        # A cadence is how often something is measured, so it is only asked of
        # a target that still exists.
        state = self._mark_target_states(session, login, [dict(row)])[0]
        if state.get('target_state') == TARGET_STATE_DELETED:
            return refused(REFUSAL_MISSING,
                           "The target of this placement no longer exists",
                           'target_id',
                           reason=RefusalReason.TARGET_DELETED)
        interval = self._clamped_interval(access, asked)
        if interval == _to_int(row.get('interval_seconds'), 0):
            return True
        try:
            result = session.execute(text(
                "UPDATE probe_assignments SET interval_seconds = :interval "
                " WHERE id = :assignment_id AND interval_seconds <> :interval"),
                {'interval': interval, 'assignment_id': assignment_id})
            if not _to_int(result.rowcount, 0):
                session.rollback()
                gone = session.execute(text(
                    "SELECT COUNT(*) FROM probe_assignments "
                    " WHERE id = :assignment_id"),
                    {'assignment_id': assignment_id}).scalar()
                if not _to_int(gone, 0):
                    return refused(REFUSAL_MISSING, ASSIGNMENT_GONE)
                return True
            _mark_config_change(session, row.get('target_type'),
                                row.get('target_id'))
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: cadence change of assignment %s failed: %s"
                         % (assignment_id, e))
            return refused(REFUSAL_FAILED,
                           "The cadence of the placement could not be changed")
        return True

    @DatabaseHelper._sessionm
    def unassign_probes_bulk(self, session, login, assignment_ids):
        """Remove several assignments at once. Returns the number removed."""
        login = _login(login)
        ids = parse_id_list(assignment_ids)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A removal is checked against somebody: no login "
                           "was sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        if not ids:
            return refused(REFUSAL_INVALID, NO_ASSIGNMENT_NAMED,
                           'assignment_ids',
                           reason=RefusalReason.FIELD_REQUIRED)

        scope_sql, params = self._assignment_scope(session, login)
        fragment, id_params = _placeholders('assignment', ids)
        params.update(id_params)
        rows = _rows(session.execute(text(
            "SELECT pa.id, pa.probe_id, pa.target_type, "
            "       pa.target_id "
            "  FROM probe_assignments pa "
            "  JOIN probes p ON p.id = pa.probe_id "
            " WHERE pa.id IN (" + fragment + ") AND " + scope_sql), params))

        accesses = {}
        removable = []
        for row in rows:
            probe_id = _to_int(row.get('probe_id'), 0)
            if probe_id not in accesses:
                accesses[probe_id] = self._probe_access(session, login, probe_id)
            # A placement on a probe the caller cannot read is left where it
            # is, like one outside his estate: unassign_probe answers missing
            # on it, so here it is simply not counted.
            if not accesses[probe_id]['visible']:
                logger.warning("Reflex: login '%s' cannot remove assignment %s"
                               % (login, row.get('id')))
                continue
            removable.append(row)
        if not removable:
            # The identifiers matched nothing readable: the selection is
            # stale, not forbidden, and answering zero is the honest count.
            return 0

        removed_by_probe = {}
        for row in removable:
            removed_by_probe.setdefault(_to_int(row.get('probe_id'), 0),
                                        []).append(_to_int(row.get('id'), 0))
        readable = self._memberships_readable(session)
        try:
            resolved = 0
            for probe_id, removed_ids in sorted(removed_by_probe.items()):
                resolved += self._resolve_alerts_after_unassign(
                    session, probe_id, removed_ids, readable)
            fragment, params = _placeholders(
                'removed', [_to_int(row.get('id'), 0) for row in removable])
            session.execute(text(
                "DELETE FROM probe_assignments WHERE id IN (" + fragment + ")"),
                params)
            _mark_target_changes(session, [
                (row.get('target_type'), row.get('target_id'))
                for row in removable])
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: bulk assignment removal failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The selected placements could not be removed")
        if resolved:
            logger.info("Reflex: %d assignment(s) removed by '%s', %d alert(s) "
                        "resolved for lack of measures"
                        % (len(removable), login, resolved))
        return len(removable)

    # =========================================================================
    # Probe exclusions
    # =========================================================================
    # A probe placed on all the machines, on a group or on an entity stores no
    # row per machine: that link is computed when the configuration of an agent
    # is built.
    @DatabaseHelper._sessionm
    def exclude_probe_on_machine(self, session, login, probe_id, machines_id,
                                 hostname='', reason=''):
        """Take a probe off one machine without touching its assignments.

        Returns True, or the structure built by `refused`.
        """
        login = _login(login)
        machines_id = _to_int(machines_id, 0)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "An exception is recorded against somebody: no "
                           "login was sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        if machines_id <= 0:
            return refused(REFUSAL_INVALID, "No machine was named",
                           'machines_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            logger.warning("Reflex: login '%s' cannot except probe %s on "
                           "machine %s" % (login, probe_id, machines_id))
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)
        if not self._machine_in_scope(session, login, machines_id):
            logger.warning("Reflex: login '%s' cannot except probe %s on "
                           "machine %s, which is outside his estate"
                           % (login, probe_id, machines_id))
            return refused(REFUSAL_MISSING,
                           "This machine does not exist, or it is not visible "
                           "to you")

        try:
            params = {
                'probe_id': _to_int(probe_id, 0),
                'machines_id': machines_id,
                'hostname': _clean_str(hostname, 255, 'hostname') or '',
                'reason': _clean_str(reason, 255, 'reason'),
                'created_by': login,
            }
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return refused_from(e)

        try:
            already = session.execute(text(
                "SELECT 1 FROM probe_exclusions "
                " WHERE probe_id = :probe_id AND machines_id = :machines_id"),
                params).first() is not None
            session.execute(text(
                "INSERT INTO probe_exclusions (probe_id, machines_id, "
                "  hostname, reason, created_by, created_at) "
                "VALUES (:probe_id, :machines_id, :hostname, :reason, "
                "  :created_by, NOW()) "
                "ON DUPLICATE KEY UPDATE hostname = VALUES(hostname), "
                "  reason = VALUES(reason), created_by = VALUES(created_by), "
                "  created_at = NOW()"), params)
            resolved = self._resolve_alerts_on_machine(
                session, params['probe_id'], machines_id,
                ALERT_RESOLVED_BY_EXCLUSION)
            if not already:
                _mark_config_change(session, 'machine', machines_id)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: probe exception failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The probe could not be excepted on this machine")
        logger.info("Reflex: probe %s excepted on machine %s by '%s', "
                    "%d alert(s) resolved"
                    % (params['probe_id'], machines_id, login, resolved))
        return True

    @DatabaseHelper._sessionm
    def include_probe_on_machine(self, session, login, probe_id, machines_id):
        """Lift the exception of a probe on one machine."""
        login = _login(login)
        machines_id = _to_int(machines_id, 0)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "An exception is lifted by somebody: no login was "
                           "sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        if machines_id <= 0:
            return refused(REFUSAL_INVALID, "No machine was named",
                           'machines_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            logger.warning("Reflex: login '%s' cannot lift the exception of "
                           "probe %s on machine %s"
                           % (login, probe_id, machines_id))
            return refused(REFUSAL_MISSING, PROBE_OUT_OF_REACH)
        # Same estate rule as the gesture this one undoes: lifting an
        # exception puts a machine back under measurement.
        if not self._machine_in_scope(session, login, machines_id):
            logger.warning("Reflex: login '%s' cannot lift the exception of "
                           "probe %s on machine %s, which is outside his "
                           "estate" % (login, probe_id, machines_id))
            return refused(REFUSAL_MISSING,
                           "This machine does not exist, or it is not visible "
                           "to you")

        try:
            result = session.execute(text(
                "DELETE FROM probe_exclusions "
                " WHERE probe_id = :probe_id AND machines_id = :machines_id"),
                {'probe_id': _to_int(probe_id, 0), 'machines_id': machines_id})
            if _to_int(result.rowcount, 0) > 0:
                _mark_config_change(session, 'machine', machines_id)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: lifting a probe exception failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The exception could not be lifted")
        if _to_int(result.rowcount, 0) <= 0:
            return refused(REFUSAL_MISSING,
                           "This machine is not excepted from this probe")
        return True

    @DatabaseHelper._sessionm
    def get_probe_exclusions(self, session, login, probe_id):
        """Machines excepted from a probe, inside the estate of the reader."""
        login = str(login or '')
        access = self._probe_access(session, login, probe_id)
        if not _reachable(access):
            return []
        scope_sql, params = self._machine_scope_clause(
            login, 'px.machines_id',
            readable=self._memberships_readable(session))
        params['probe_id'] = _to_int(probe_id, 0)
        return _rows(session.execute(text(
            "SELECT px.id, px.probe_id, px.machines_id, px.hostname, "
            "       px.reason, px.created_by, px.created_at "
            "  FROM probe_exclusions px WHERE px.probe_id = :probe_id "
            "   AND " + scope_sql +
            " ORDER BY px.hostname ASC, px.machines_id ASC"), params))

    # =========================================================================
    # Alerts
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_alerts(self, session, login, start=0, limit=20, filter_str='',
                   severity='', status=ALERT_STATUS_ACTIVE,
                   opened_from='', opened_to='', sort=ALERT_SORT_SEVERITY,
                   probe_id=0):
        """Paginated list of the alerts raised by probes the caller may see."""
        login = str(login or '')
        start = max(_to_int(start, 0), 0)
        limit = _to_int(limit, 20)
        if limit <= 0:
            limit = 20
        nothing = {'total': 0, 'data': [], 'has_instance': False}

        visible_sql, params = self._visible_clause(login)
        readable = self._memberships_readable(session)
        # Correlated EXISTS posed in the WHERE: one pass, no statement per row,
        # and the pagination still cuts the filtered result.
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'a.machines_id', readable=readable)
        params.update(scope_params)
        clauses = [visible_sql, scope_sql]

        try:
            period_from = parse_period_bound(opened_from)
            period_to = parse_period_bound(opened_to, end_of_day=True)
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return nothing
        if period_from is not None:
            clauses.append("a.opened_at >= :opened_from")
            params['opened_from'] = period_from
        if period_to is not None:
            clauses.append("a.opened_at <= :opened_to")
            params['opened_to'] = period_to

        status = str(status or '').strip().lower()
        if status == ALERT_STATUS_ACTIVE:
            clauses.append(alert_active_sql())
        elif status:
            if status not in ALERT_STATUSES:
                logger.warning("Reflex: unknown alert status '%s'" % status)
                return nothing
            clauses.append("a.status = :status")
            params['status'] = status

        severity = str(severity or '').strip().lower()
        if severity:
            if severity not in SEVERITIES:
                logger.warning("Reflex: unknown severity '%s'" % severity)
                return nothing
            clauses.append("a.severity = :severity")
            params['severity'] = severity

        probe_id = _to_int(probe_id, 0)
        if probe_id > 0:
            clauses.append("a.probe_id = :probe_id")
            params['probe_id'] = probe_id

        filter_str = str(filter_str or '').strip()
        if filter_str:
            clauses.append("(a.hostname LIKE :filter OR a.message LIKE :filter "
                           "OR p.label LIKE :filter)")
            params['filter'] = "%%%s%%" % filter_str

        where = " WHERE " + " AND ".join(["(" + clause + ")" for clause in clauses])
        source = " FROM alerts a JOIN probes p ON p.id = a.probe_id"
        joined = source + where
        if readable:
            entity_column = "ae.glpi_id AS entity_id"
            entity_join = (" LEFT JOIN xmppmaster.machines am "
                           "   ON am.id = a.machines_id "
                           " LEFT JOIN xmppmaster.glpi_entity ae "
                           "   ON ae.id = am.glpi_entity_id")
        else:
            entity_column = "NULL AS entity_id"
            entity_join = ""

        total = _to_int(session.execute(
            text("SELECT COUNT(*)" + joined), params).scalar(), 0)

        # Over the whole filtered result, from the same FROM and WHERE: a
        # column that comes and goes from one page to the next says nothing.
        has_instance = total > 0 and self._alerts_have_instance(
            session, joined, params)

        params['limit'] = limit
        params['start'] = start
        rows = _rows(session.execute(text(
            "SELECT a.id, a.probe_id, a.condition_id, a.machines_id, "
            "       a.uuid_inventorymachine, a.hostname, a.severity, a.status, "
            "       a.value_at_trigger, a.value_text_at_trigger, "
            "       a.detail_at_trigger, a.message, "
            "       a.opened_at, a.last_seen_at, a.occurrence_count, "
            "       a.ack_user, a.ack_at, a.ack_comment, a.resolved_at, "
            "       a.resolved_reason, "
            # Read to resolve `instance` below, and not returned: the rule
            # stays on this side.
            "       p.value_type, "
            "       p.label AS probe_label, p.metric_key, p.unit, "
            "       " + entity_column
            + source + entity_join + where +
            " ORDER BY " + alert_order_sql(sort) +
            " LIMIT :limit OFFSET :start"), params))
        for row in rows:
            entity = row.get('entity_id')
            row['entity_id'] = None if entity is None else str(_to_int(entity, 0))
            # '' and never None, as get_alert renders it.
            row['detail_at_trigger'] = str(row.get('detail_at_trigger') or '')
        self._annotate_notification_states(session, rows)

        return {'total': total, 'data': annotate_alert_instances(rows),
                'has_instance': bool(has_instance)}

    def _annotate_notification_states(self, session, rows):
        """Give every alert row `notification_state` and
        `notification_reason`.
        """
        ids = sorted(set(_to_int(row.get('id'), 0) for row in rows) - {0})
        summary = {}
        if ids:
            fragment, params = _placeholders('nh_alert', ids)
            for line in _rows(session.execute(text(
                    "SELECT alert_id, status, skip_reason, "
                    "       (next_retry_at IS NOT NULL) AS retrying, "
                    "       COUNT(*) AS line_count, MAX(id) AS last_id "
                    "  FROM notification_history "
                    " WHERE alert_id IN (" + fragment + ") "
                    " GROUP BY alert_id, status, skip_reason, retrying"),
                    params)):
                summary.setdefault(_to_int(line.get('alert_id'), 0),
                                   []).append(line)
        for row in rows:
            state, reason = notification_state(
                summary.get(_to_int(row.get('id'), 0), []))
            row['notification_state'] = state
            row['notification_reason'] = reason

    def _alerts_have_instance(self, session, joined, params):
        """Whether an alert of a filtered result was raised on an instance."""
        batch = 50
        offset = 0
        while True:
            candidates = _rows(session.execute(text(
                "SELECT a.value_text_at_trigger, p.value_type" + joined +
                " AND a.value_text_at_trigger IS NOT NULL "
                " AND TRIM(a.value_text_at_trigger) <> '' "
                " AND p.value_type <> 'text' "
                " ORDER BY a.id ASC LIMIT :instance_batch OFFSET :instance_offset"),
                dict(params, instance_batch=batch, instance_offset=offset)))
            if any(alert_instance(row) for row in candidates):
                return True
            if len(candidates) < batch:
                return False
            offset += batch

    @DatabaseHelper._sessionm
    def get_alert(self, session, login, alert_id):
        """Everything there is to read about one alert."""
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "A read is filtered on its caller: no login was "
                           "sent", 'login',
                           reason=RefusalReason.LOGIN_REQUIRED)
        alert_id = _to_int(alert_id, 0)
        if alert_id <= 0:
            return refused(REFUSAL_INVALID, "No alert was named", 'alert_id',
                           reason=RefusalReason.FIELD_REQUIRED)

        visible_sql, params = self._visible_clause(login)
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'a.machines_id',
            readable=self._memberships_readable(session))
        params.update(scope_params)
        params['alert_id'] = alert_id
        alert = _one(session.execute(text(
            "SELECT a.id, a.probe_id, a.condition_id, a.machines_id, "
            "       a.uuid_inventorymachine, a.hostname, a.severity, a.status, "
            "       a.value_at_trigger, a.value_text_at_trigger, "
            # What the measure that triggered carried, frozen with it: the
            # current detail of the probe names another instance already.
            "       a.detail_at_trigger, a.message, "
            "       a.opened_at, a.last_seen_at, a.occurrence_count, "
            "       a.ack_user, a.ack_at, a.ack_comment, a.resolved_at, "
            "       a.resolved_reason, "
            # The condition this alert froze when it was raised.
            "       a.operator_at_trigger, a.threshold_value_at_trigger, "
            "       a.threshold_value2_at_trigger, "
            "       a.threshold_text_at_trigger, "
            "       a.duration_seconds_at_trigger, "
            # Read to resolve `instance` below, and taken back out by
            # annotate_alert_instances: the rule stays on this side.
            "       p.value_type, "
            # Last edit of the probe, read for condition_trust and taken back
            # out with it: the alert row keeps the keys get_alerts returns.
            "       p.updated_at AS probe_updated_at, "
            "       p.probe_key, p.label AS probe_label, p.metric_key, p.unit "
            "  FROM alerts a JOIN probes p ON p.id = a.probe_id "
            " WHERE a.id = :alert_id AND " + visible_sql
            + " AND " + scope_sql), params))
        if alert is None:
            return refused(REFUSAL_MISSING,
                           "This alert does not exist, or it is not visible "
                           "to you")
        # '' and never None, as attach_measure_detail does for a measure: an
        # alert opened before the column existed reads as one without detail.
        alert['detail_at_trigger'] = str(alert.get('detail_at_trigger') or '')
        # Both are read to decide, never returned: value_type would be the raw
        # material to redo the instance rule in the page, and probe_updated_at
        # an evidence without the reading that qualifies it.
        value_type = alert.get('value_type')
        probe_updated_at = alert.pop('probe_updated_at', None)
        # Assembled before the raw columns leave the row, and severity is read
        # from the same row: what comes back is a condition readable on its
        # own. Empty on an alert opened before those columns were filled.
        frozen = alert_frozen_condition(alert)
        for column, _key in ALERT_FREEZE_FIELDS:
            alert.pop(column, None)
        annotate_alert_instances([alert])

        # The condition is read on its own rather than joined.
        condition = {}
        condition_id = _to_int(alert.get('condition_id'), 0)
        if condition_id > 0:
            # The estate of the machine the alert stands on, not that of the
            # reader: what is compared with the frozen condition, and shown as
            # the condition of today, is the one that actually decides here.
            scope = self._condition_scope(
                self._machine_entity(session, alert.get('machines_id')))
            condition = _one(session.execute(text(
                "SELECT pc.id, pc.probe_id, pc.operator, pc.display_order, "
                "       " + condition_effective_sql('pc', scope['alias']) + ", "
                "       " + condition_default_sql() + ", "
                "       " + condition_trace_sql('customized_by', scope['alias'])
                + " AS customized_by, "
                "       " + condition_trace_sql('customized_at', scope['alias'])
                + " AS customized_at, "
                "       " + condition_customized_sql(scope['alias'])
                + " AS is_customized "
                "  FROM probe_conditions pc " + scope['join'] +
                " WHERE pc.id = :condition_id"),
                dict(scope['params'], condition_id=condition_id))) or {}

        return {
            'alert': alert,
            'condition': condition,
            'condition_at_trigger': frozen,
            'condition_trust': alert_condition_trust(
                alert, condition, value_type=value_type,
                probe_updated_at=probe_updated_at, frozen=frozen),
            'notifications': self._alert_notifications(session, alert_id),
            'skipped': self._alert_skipped_notifications(session, alert_id),
        }

    def _alert_notifications(self, session, alert_id):
        """Sending attempts traced for one alert, oldest first."""
        rows = _rows(session.execute(text(
            "SELECT h.id, h.channel_id, h.rule_id, h.recipients, h.status, "
            "       h.skip_reason, "
            "       h.error_message, h.attempt_count, h.next_retry_at, "
            "       h.accepted_at, h.provider_message_id, h.is_escalation, "
            "       h.created_at, h.sent_at, "
            "       c.name AS channel_name, c.channel_type, "
            "       c.enabled AS channel_enabled, "
            "       r.min_severity AS rule_min_severity, "
            "       r.enabled AS rule_enabled, "
            "       rp.label AS rule_probe_label "
            "  FROM notification_history h "
            "  LEFT JOIN notification_channels c ON c.id = h.channel_id "
            "  LEFT JOIN notification_rules r ON r.id = h.rule_id "
            "  LEFT JOIN probes rp ON rp.id = r.probe_id "
            " WHERE h.alert_id = :alert_id AND h.status <> 'skipped' "
            " ORDER BY h.created_at ASC, h.id ASC LIMIT :limit"),
            {'alert_id': _to_int(alert_id, 0),
             'limit': NOTIFICATION_TRACE_LIMIT}))
        # A rule without a probe concerns every probe.
        for row in rows:
            row['rule_all_probes'] = 1 if row.get('rule_probe_label') is None \
                else 0
        return rows

    def _alert_skipped_notifications(self, session, alert_id):
        """Sendings that did not happen for one alert, grouped by reason."""
        rows = _rows(session.execute(text(
            "SELECT h.channel_id, h.rule_id, h.skip_reason, "
            "       COUNT(*) AS occurrence_count, "
            "       MAX(h.attempt_count) AS attempt_count, "
            "       MIN(h.created_at) AS first_at, "
            "       MAX(h.created_at) AS last_at, "
            "       c.name AS channel_name, c.channel_type, "
            "       c.enabled AS channel_enabled "
            "  FROM notification_history h "
            "  LEFT JOIN notification_channels c ON c.id = h.channel_id "
            " WHERE h.alert_id = :alert_id AND h.status = 'skipped' "
            " GROUP BY h.channel_id, h.rule_id, h.skip_reason, c.name, "
            "          c.channel_type, c.enabled "
            " ORDER BY MAX(h.created_at) DESC"),
            {'alert_id': _to_int(alert_id, 0)}))
        for row in rows:
            row['attempt_count'] = _to_int(row.get('attempt_count'), 0)
        return rows

    @DatabaseHelper._sessionm
    def ack_alert(self, session, login, alert_id, comment=''):
        """Acknowledge one open alert."""
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "An acknowledgement is signed: no login was sent",
                           'login', reason=RefusalReason.LOGIN_REQUIRED)
        alert_id = _to_int(alert_id, 0)
        if alert_id <= 0:
            return refused(REFUSAL_INVALID, "No alert was named", 'alert_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        try:
            comment = _clean_str(comment, 512, 'ack_comment')
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return refused_from(e)
        visible_sql, params = self._visible_clause(login)
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'a.machines_id',
            readable=self._memberships_readable(session))
        params.update(scope_params)
        params.update({'comment': comment, 'alert_id': alert_id})
        try:
            result = session.execute(text(
                "UPDATE alerts a JOIN probes p ON p.id = a.probe_id "
                "   SET a.status = 'ack', a.ack_user = :login, "
                "       a.ack_at = NOW(), a.ack_comment = :comment "
                " WHERE a.id = :alert_id AND a.status = 'open' AND "
                + visible_sql + " AND " + scope_sql), params)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: alert acknowledgement failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The alert could not be acknowledged")
        if _to_int(result.rowcount, 0) <= 0:
            return refused(REFUSAL_MISSING,
                           "This alert is not open any more, or it is not "
                           "visible to you")
        return True

    @DatabaseHelper._sessionm
    def ack_alerts_bulk(self, session, login, alert_ids, comment=''):
        """Acknowledge several alerts at once. Returns the number
        acknowledged.
        """
        login = _login(login)
        if not login:
            return refused(REFUSAL_FORBIDDEN,
                           "An acknowledgement is signed: no login was sent",
                           'login', reason=RefusalReason.LOGIN_REQUIRED)
        ids = parse_id_list(alert_ids)
        if not ids:
            return refused(REFUSAL_INVALID, "No alert was named", 'alert_ids',
                           reason=RefusalReason.FIELD_REQUIRED)
        try:
            comment = _clean_str(comment, 512, 'ack_comment')
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return refused_from(e)

        # Identifiers are expanded into generated placeholders: the list comes
        # from the caller, the statement does not.
        fragment, params = _placeholders('alert', ids)
        visible_sql, visible_params = self._visible_clause(login)
        params.update(visible_params)
        # Same estate rule as the single acknowledgement: a selection cannot
        # reach further than what a click reaches.
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'a.machines_id',
            readable=self._memberships_readable(session))
        params.update(scope_params)
        params['comment'] = comment
        try:
            result = session.execute(text(
                "UPDATE alerts a JOIN probes p ON p.id = a.probe_id "
                "   SET a.status = 'ack', a.ack_user = :login, "
                "       a.ack_at = NOW(), a.ack_comment = :comment "
                " WHERE a.id IN (" + fragment + ") AND a.status = 'open' AND "
                + visible_sql + " AND " + scope_sql), params)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: bulk acknowledgement failed: %s" % e)
            return refused(REFUSAL_FAILED,
                           "The selected alerts could not be acknowledged")
        return _to_int(result.rowcount, 0)

    # =========================================================================
    # Machines
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_machines_status(self, session, login, start=0, limit=20,
                            filter_str=''):
        """Supervision state of the machines, one row per machine."""
        login = str(login or '')
        start = max(_to_int(start, 0), 0)
        limit = _to_int(limit, 20)
        if limit <= 0:
            limit = 20

        # One check for both readings of xmppmaster: the memberships of a
        # placement and the system of a machine come from the same database.
        memberships_readable = self._memberships_readable(session)
        reach_sql = membership_reach_sql(memberships_readable)
        fallback_silence = DEFAULT_SILENT_AFTER_SECONDS
        now = datetime.now()
        visible_sql, params = self._visible_clause(login)
        params['since'] = now - timedelta(
            seconds=MACHINE_ACTIVITY_WINDOW_SECONDS)
        params['now'] = now

        # Machines known either because a configuration was distributed to them
        # or because they reported at least one measure.
        reached_sql = ""
        if memberships_readable:
            reached_target_sql, reached_params = machine_target_clauses(
                None, machine_column='nm.id', reach_sql=reach_sql)
            params.update(reached_params)
            reached_scope_sql, reached_scope_params = (
                self._machine_scope_clause(login, 'nm.id', prefix='rscope'))
            params.update(reached_scope_params)
            reached_sql = (
                "        UNION "
                "        SELECT nm.id FROM xmppmaster.machines nm "
                "         WHERE nm.agenttype = 'machine' "
                "           AND " + reached_scope_sql +
                "           AND EXISTS (SELECT 1"
                + machine_placements_sql(reached_target_sql, visible_sql,
                                         'nm.id') +
                "                          AND px.id IS NULL) ")
        machines_sql = (
            "  FROM (SELECT machines_id FROM probe_agent_config "
            "        UNION "
            "        SELECT machines_id FROM probe_measures GROUP BY machines_id "
            + reached_sql +
            "       ) mach "
            "  LEFT JOIN probe_agent_config ac ON ac.machines_id = mach.machines_id ")

        # Who may be told that a machine exists is decided on the machine and
        # not on the probes: this page holds one row per machine, and a catalog
        # probe is visible to everybody.
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'mach.machines_id', readable=memberships_readable)
        params.update(scope_params)

        # Name the machine is sorted and filtered on: the one its configuration
        # was sent under, otherwise the last one it reported over the window,
        # otherwise the one xmppmaster knows it by.
        known_hostname_sql = (
            "(SELECT hm.hostname FROM xmppmaster.machines hm "
            "  WHERE hm.id = mach.machines_id), "
            if memberships_readable else "")
        hostname_sql = (
            "COALESCE(ac.hostname, "
            "         (SELECT MAX(wm.hostname) "
            "            FROM probes p "
            "            JOIN probe_measures wm ON wm.probe_id = p.id "
            "           WHERE wm.machines_id = mach.machines_id "
            "             AND wm.received_at >= :since "
            "             AND " + visible_sql + "), "
            + known_hostname_sql + "'')")
        filter_str = str(filter_str or '').strip()
        where_clause = " WHERE " + scope_sql + " "
        if filter_str:
            where_clause += " AND " + hostname_sql + " LIKE :filter "
            params['filter'] = "%%%s%%" % filter_str

        alerts_sql = (
            "  LEFT JOIN (SELECT a.machines_id, "
            "                    SUM(CASE WHEN a.severity = 'critical' THEN 1 ELSE 0 END) AS critical, "
            "                    SUM(CASE WHEN a.severity = 'high' THEN 1 ELSE 0 END) AS high, "
            "                    SUM(CASE WHEN a.severity = 'medium' THEN 1 ELSE 0 END) AS medium, "
            "                    SUM(CASE WHEN a.severity = 'info' THEN 1 ELSE 0 END) AS info "
            "               FROM alerts a "
            "               JOIN probes p ON p.id = a.probe_id "
            "              WHERE " + alert_active_sql() +
            "                AND " + visible_sql +
            "              GROUP BY a.machines_id) al "
            "    ON al.machines_id = mach.machines_id ")

        # Placements and pending changes read with the expressions the machine
        # sheet reads for one machine, memberships included, for the rows of
        # the page only, computed once the page is cut: in the select list of
        # the paginated statement they were evaluated for every machine before
        # the sort.
        page_target_sql, page_target_params = machine_target_clauses(
            None, machine_column='page.machines_id', reach_sql=reach_sql)
        params.update(page_target_params)
        page_placed = placed_probes_count_sql(page_target_sql, visible_sql,
                                              'page.machines_id')
        page_stale = config_stale_sql(page_target_sql, 'page.machines_id',
                                      os_readable=memberships_readable)
        # Cadence read on the placements, as the machine sheet reads it: taken
        # from the measures of the window, it vanished with them and a machine
        # quiet for a day lost the very cadence its silence is judged on.
        page_cadence = placed_cadence_sql(page_target_sql, visible_sql,
                                          'page.machines_id')
        page_last = machine_last_received_sql(visible_sql, 'page.machines_id')
        probe_last = probe_last_received_sql('page.machines_id')
        # Clock gap of the last report, used only for a machine heard of
        # nothing over the window, whose window bounds are empty.
        page_last_drift = (
            "(SELECT (SELECT TIMESTAMPDIFF(SECOND, lm.collected_at, "
            "                              lm.received_at) "
            "           FROM probe_measures lm "
            "          WHERE lm.machines_id = page.machines_id "
            "            AND lm.probe_id = p.id "
            "          ORDER BY lm.received_at DESC, lm.id DESC LIMIT 1) "
            "   FROM probes p WHERE " + visible_sql +
            "  ORDER BY " + probe_last + " DESC LIMIT 1)")

        # Neither the sort nor the filter reads the activity of the window,
        # so the count does not compute it.
        total = _to_int(session.execute(text(
            "SELECT COUNT(*) FROM (SELECT mach.machines_id" + machines_sql
            + where_clause + ") counted"), params).scalar(), 0)

        params['limit'] = limit
        params['start'] = start
        rows = _rows(session.execute(text(
            # Answered by the server clock, the one that stamped received_at,
            # so a machine whose clock drifts is not called silent for that.
            "SELECT dated.*, "
            "       TIMESTAMPDIFF(SECOND, dated.last_measure_at, :now) "
            "           AS silence_seconds "
            "  FROM (SELECT page.*, "
            "       " + page_placed + " AS probes_placed_count, "
            "       " + page_stale + " AS config_stale, "
            "       " + page_cadence + " AS expected_interval, "
            "       " + page_last + " AS last_measure_at, "
            "       " + page_last_drift + " AS last_drift, "
            "       EXISTS (SELECT 1 FROM probe_measures em "
            "                WHERE em.machines_id = page.machines_id) "
            "           AS measured "
            "  FROM (SELECT mach.machines_id, "
            "       " + hostname_sql + " AS hostname, "
            "       COALESCE(al.critical, 0) AS critical, "
            "       COALESCE(al.high, 0) AS high, "
            "       COALESCE(al.medium, 0) AS medium, "
            "       COALESCE(al.info, 0) AS info, "
            "       ac.sent_version, ac.sent_at, "
            "       ac.acked_version, ac.acked_at, "
            "       COALESCE(ac.probe_count, 0) AS probe_count, "
            "       ac.last_error, ac.updated_at"
            + machines_sql + alerts_sql + where_clause +
            " ORDER BY hostname ASC, mach.machines_id ASC "
            " LIMIT :limit OFFSET :start) page) dated "
            " ORDER BY dated.hostname ASC, dated.machines_id ASC"), params))

        # The measures of the window are read for the rows of the page only,
        # once it is cut: neither the sort nor the filter depends on them.
        page_ids = [_to_int(row.get('machines_id'), 0) for row in rows]
        activity = self._machines_activity(
            session, page_ids,
            visible_sql, params, reach_sql, fallback_silence)
        # Connection state of the agents, one statement for the page, see
        # _machines_presence. None when xmppmaster cannot be read.
        presence = self._machines_presence(session, page_ids)

        for row in rows:
            for key in ('machines_id', 'probes_placed_count', 'config_stale',
                        'probe_count', 'critical', 'high', 'medium', 'info'):
                row[key] = _to_int(row.get(key), 0)
            # A machine says nothing either because its agent is stopped or
            # because the machine is off: only its connection tells them
            # apart, and reading it used to mean leaving this page.
            row['agent_online'] = (None if presence is None
                                   else presence.get(row['machines_id'], 0))
            stats = activity.get(row['machines_id']) or {}
            for key in ('probes_count', 'probes_silent', 'probes_unwatched'):
                row[key] = _to_int(stats.get(key), 0)
            heard_in_window = 1 if stats else 0
            behind = _to_int(stats.get('drift_behind'), 0)
            ahead = _to_int(stats.get('drift_ahead'), 0)
            drift = behind if abs(behind) >= abs(ahead) else ahead
            last_drift = row.pop('last_drift', None)
            if not heard_in_window:
                # Nothing over the window: the gap of the last report, NULL
                # for a machine that never reported.
                drift = _to_int(last_drift, 0)
            row['clock_drift_seconds'] = drift
            row['clock_drift'] = (
                1 if abs(drift) >= CLOCK_DRIFT_TOLERANCE_SECONDS else 0)

            expected = _to_int(row.pop('expected_interval', None), 0)
            row['expected_interval_seconds'] = expected
            # Says what the threshold rests on, so a console can tell an
            # estate wide default apart from a cadence read on the placement.
            row['cadence_source'] = 'assignment' if expected > 0 else 'default'
            threshold = silence_after_seconds(expected, fallback_silence)
            row['silent_after_seconds'] = threshold
            silence = row.get('silence_seconds')
            silence = None if silence is None else _to_int(silence, 0)
            row['silence_seconds'] = silence
            # What is actually reporting: neither the probes that went quiet
            # nor the ones nobody asks anything of any more.
            row['probes_reporting_count'] = max(
                row['probes_count'] - row['probes_silent']
                - row['probes_unwatched'], 0)

            row['config_acked'] = 1 if row.get('acked_version') else 0
            measured = _to_int(row.pop('measured', None), 0)
            if row['probe_count'] == 0 and row.get('sent_version'):
                # A configuration went out asking for nothing: every probe
                # placed here is turned off or excepted.
                row['silent'] = 0
                row['reporting_state'] = 'unwatched'
            elif not measured:
                # Reached and never heard of, whether its configuration was
                # received or not: the machine is owed a look.
                row['silent'] = 1
                row['reporting_state'] = 'never'
            elif silence is None:
                # Nothing ever heard.
                row['silent'] = 1 if row.get('sent_version') else 0
                row['reporting_state'] = ('silent' if row['silent']
                                          else 'unknown')
            elif silence > threshold:
                row['silent'] = 1
                row['reporting_state'] = 'silent'
            else:
                # The machine still speaks; one of its probes may have
                # stopped, which is a different sentence and not a quiet one.
                row['silent'] = 0
                row['reporting_state'] = ('partial' if row['probes_silent']
                                          else 'reporting')

        return {'total': total, 'data': rows}

    def _machines_activity(self, session, machines_ids, visible_sql, params,
                           reach_sql, fallback_silence):
        """Activity of some machines over the window, keyed by machines_id."""
        if not machines_ids:
            return {}
        params = dict(params)
        # Only the probes an agent measures: a probe the server evaluates owes
        # no report, so it is neither counted, nor called silent, nor allowed
        # to make a machine look partially quiet. See probe_measured_sql.
        probe_ids = [_to_int(row.get('id'), 0)
                     for row in _rows(session.execute(text(
                         "SELECT p.id FROM probes p WHERE " + visible_sql +
                         "   AND " + probe_measured_sql()), params))]
        if not probe_ids:
            return {}
        machine_list, machine_params = _placeholders('actm', machines_ids)
        probe_list, probe_params = _placeholders('actp', probe_ids)
        params.update(machine_params)
        params.update(probe_params)
        params['missed'] = SILENCE_MISSED_REPORTS
        params['grace'] = SILENCE_GRACE_SECONDS
        params['fallback_silence'] = fallback_silence
        # Cadence this machine is asked to hold for this probe: the machine
        # by name, its groups and its entities, the shortest of them, as the
        # agent is configured.
        expected_interval = "cm.interval_seconds"

        # Silence allowed for one probe.
        probe_silence = ("COALESCE(:missed * " + expected_interval
                         + " + :grace, :fallback_silence)")
        # Whether the probe is still placed on this machine, read on the
        # assignments and never on what was measured: a probe taken off
        # yesterday keeps its measures of the day, and counting them made the
        # machine owe a report nobody asks of it any more.
        probe_placed = "(cm.probe_id IS NOT NULL)"
        # A probe no longer placed, turned off or excepted on this machine is
        # asked for nothing.
        probe_in_service = "(p.enabled = 1 AND px.id IS NULL)"
        probe_watched = "(" + probe_placed + " AND " + probe_in_service + ")"

        rows = _rows(session.execute(text(
            "SELECT pp.machines_id, "
            "       SUM(CASE WHEN " + probe_placed +
            "                THEN 1 ELSE 0 END) AS probes_count, "
            # Signed gap between the two clocks, kept as its two bounds: the
            # widest of them is picked by the caller, whichever way the clock
            # is off.
            "       MAX(pp.drift_behind) AS drift_behind, "
            "       MIN(pp.drift_ahead) AS drift_ahead, "
            # Each probe against its own cadence: a probe placed at the hour
            # is not late because the one placed at the minute stopped.
            "       SUM(CASE WHEN " + probe_watched +
            "                 AND TIMESTAMPDIFF(SECOND, "
            "                     pp.last_received, :now) > " + probe_silence +
            "                THEN 1 ELSE 0 END) AS probes_silent, "
            # Placed but asked for nothing: turned off or excepted.
            "       SUM(CASE WHEN " + probe_placed +
            "                 AND NOT " + probe_in_service +
            "                THEN 1 ELSE 0 END) AS probes_unwatched "
            # One row per probe and per machine before rolling up to the
            # machine: the freshness of a probe cannot be read off a figure
            # already merged with the other probes.
            "  FROM (SELECT pm.machines_id, pm.probe_id, "
            "               MAX(pm.received_at) AS last_received, "
            "               MAX(TIMESTAMPDIFF(SECOND, pm.collected_at, "
            "                   pm.received_at)) AS drift_behind, "
            "               MIN(TIMESTAMPDIFF(SECOND, pm.collected_at, "
            "                   pm.received_at)) AS drift_ahead "
            # The probes are joined once the rows are rolled up and not
            # here: joined to the measures, they hand the optimizer a lookup
            # by probe on idx_probe_time that reads the whole history of
            # every probe instead of the ranges below.
            "          FROM probe_measures pm "
            "         WHERE pm.machines_id IN (" + machine_list + ") "
            "           AND pm.probe_id IN (" + probe_list + ") "
            "           AND pm.received_at >= :since "
            "         GROUP BY pm.machines_id, pm.probe_id) pp "
            "  JOIN probes p ON p.id = pp.probe_id "
            # Placements naming the machine, directly or through a group or an
            # entity, one row per probe and machine.
            "  LEFT JOIN (SELECT sp.probe_id, sp.machines_id, "
            "                    MIN(sp.interval_seconds) AS interval_seconds "
            "               FROM (SELECT spa.probe_id, "
            "                            CAST(spa.target_id AS UNSIGNED) "
            "                                AS machines_id, "
            "                            spa.interval_seconds "
            "                       FROM probe_assignments spa "
            "                      WHERE spa.target_type = 'machine' "
            "                        AND spa.target_id = CAST(CAST("
            "                            spa.target_id AS UNSIGNED) AS CHAR) "
            "                     UNION ALL "
            "                     SELECT spa.probe_id, rc.machines_id, "
            "                            spa.interval_seconds "
            "                       FROM probe_assignments spa "
            "                       JOIN (" + reach_sql + ") rc "
            "                         ON rc.assignment_id = spa.id"
            "                    ) sp "
            "              GROUP BY sp.probe_id, sp.machines_id) cm "
            "         ON cm.probe_id = pp.probe_id "
            "        AND cm.machines_id = pp.machines_id "
            # (probe_id, machines_id) is the unique key of probe_exclusions.
            "  LEFT JOIN probe_exclusions px "
            "         ON px.probe_id = pp.probe_id "
            "        AND px.machines_id = pp.machines_id "
            " WHERE " + visible_sql +
            " GROUP BY pp.machines_id"), params))
        return dict((_to_int(row.get('machines_id'), 0), row) for row in rows)

    @staticmethod
    def _empty_machine_detail(machines_id):
        """A sheet holding nothing, with the keys of a real one."""
        return {
            'machines_id': _to_int(machines_id, 0),
            'probes': [],
            'last_measures': [],
            'open_alerts': [],
            'agent_config': {'config_stale': 0},
            'agent_online': None,
            'reporting': {'state': 'unknown', 'silent': 0,
                          'silence_seconds': None,
                          'expected_interval_seconds': 0,
                          'silent_after_seconds': 0,
                          'cadence_source': 'default',
                          'probes_total': 0, 'probes_reporting': 0,
                          'probes_silent': 0, 'probes_never': 0,
                          'probes_unwatched': 0, 'probes_server_evaluated': 0},
        }

    @DatabaseHelper._sessionm
    def get_machine_detail(self, session, login, machines_id):
        """Supervision of one machine: probes, last measures and open alerts.
        """
        login = str(login or '')
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return self._empty_machine_detail(0)
        # Two lists of entities meet here and must not be confused: the ones
        # the machine belongs to, used to know what the agent measures, and
        # the ones the reader reaches, used to know what he may see.
        memberships_readable = self._memberships_readable(session)
        # Read before anything else: whether this machine may be described at
        # all is not a question about the probes placed on it.
        if not self._machine_in_scope(session, login, machines_id,
                                      readable=memberships_readable):
            return self._empty_machine_detail(machines_id)
        fallback_silence = DEFAULT_SILENT_AFTER_SECONDS
        group_ids, entity_ids = self._machine_memberships(
            session, machines_id, memberships_readable)
        visible_sql, params = self._visible_clause(login)
        params['machines_id'] = machines_id
        params['now'] = datetime.now()
        # NULL when the system cannot be told, and told apart below: an
        # unknown system is not a system a probe does not cover.
        params['machine_os'] = (self._machine_os(session, machines_id) or None
                                if memberships_readable else None)

        # Same target clauses as the configuration built for the agent.
        target_fragment, target_params = machine_target_clauses(
            machines_id, group_ids=group_ids, entity_ids=entity_ids)
        probes = collapse_assignments(_rows(session.execute(text(
            "SELECT p.id AS probe_id, p.probe_key, p.label, p.category, "
            "       p.metric_key, p.unit, p.value_type, p.probe_type, "
            # Property of the probe as it is shipped: a probe whose curve
            # teaches nothing is read as a value, whatever the period.
            "       p.plottable, "
            "       pa.id AS assignment_id, p.owner_login, pa.created_by, "
            "       pa.interval_seconds, pa.target_type, pa.target_id, "
            # The operating switch is the one of the probe and nothing else:
            # an assignment carries no state of its own.
            "       p.enabled AS probe_enabled, "
            "       p.enabled AS enabled, "
            "       (px.id IS NOT NULL) AS excluded, "
            # What the agent of this machine has to run for that probe, as
            # get_probe_config_for_machine reads it.
            "       (" + probe_distributable_sql(':machine_os') + ") "
            "           AS agent_measurable, "
            # Measured by the agent or decided by the server: nothing below
            # dates a probe of the second kind, see probe_measured_sql.
            "       (NOT " + probe_measured_sql() + ") AS server_evaluated, "
            "       px.reason AS exclusion_reason, "
            "       px.created_by AS exclusion_by, "
            "       px.created_at AS exclusion_at "
            + machine_placements_sql(target_fragment, visible_sql,
                                     ':machines_id') +
            " ORDER BY p.label ASC"),
            dict(params, **target_params))))
        for probe in probes:
            probe['excluded'] = _to_int(probe.get('excluded'), 0)
            probe['server_evaluated'] = _to_int(probe.get('server_evaluated'),
                                                0)
            probe['agent_measurable'] = (
                None if params['machine_os'] is None
                else _to_int(probe.get('agent_measurable'), 0))
            probe['plottable'] = _to_int(probe.get('plottable'), 1)
        # The placements are listed as the agent measures them, so one of them
        # can be a gesture of another estate -- a group of another client the
        # machine belongs to.
        self._mark_readable_assignments(session, login, probes)
        # The target of the placement shown, and what became of it.
        self._mark_target_states(
            session, login, probes, readable=memberships_readable,
            known={('machine', str(machines_id)): TARGET_STATE_OK})

        # Latest measure per probe and per instance, obtained in one statement.
        placed_ids = [_to_int(probe.get('probe_id'), 0) for probe in probes
                      if _to_int(probe.get('server_evaluated'), 0) == 0]
        placed_ids = [probe_id for probe_id in placed_ids if probe_id > 0]
        params['batch_window'] = MEASURE_BATCH_WINDOW_SECONDS
        batches = []
        if placed_ids:
            placed_fragment, placed_params = _placeholders('placed',
                                                           placed_ids)
            batches = [row for row in _rows(session.execute(text(
                "SELECT latest.probe_id, "
                "       DATE_SUB(latest.last_received, "
                "                INTERVAL :batch_window SECOND) AS batch_start "
                "  FROM (SELECT p.id AS probe_id, "
                "               " + probe_last_received_sql(':machines_id') +
                "                   AS last_received "
                "          FROM probes p "
                "         WHERE p.id IN (" + placed_fragment + ")) latest "
                " WHERE latest.last_received IS NOT NULL"),
                dict(params, **placed_params)))]
        last_measures = []
        if batches:
            batch_params = dict(params)
            batch_clauses = []
            for index, batch in enumerate(batches):
                batch_clauses.append(
                    "(pm.probe_id = :batch_probe%d "
                    "AND pm.received_at >= :batch_start%d)" % (index, index))
                batch_params['batch_probe%d' % index] = _to_int(
                    batch.get('probe_id'), 0)
                batch_params['batch_start%d' % index] = batch.get('batch_start')
            last_measures = _rows(session.execute(text(
                "SELECT pm.id, pm.machines_id, pm.uuid_inventorymachine, "
                "       pm.hostname, pm.probe_id, pm.metric_key, pm.value_num, "
                "       pm.value_text, pm.unit, pm.status, pm.detail, "
                "       pm.collected_at, "
                # Age answered by the server clock, the one that stamped
                # received_at: a machine whose clock drifts must not have its
                # values dated old, nor fresh, for that reason.
                "       TIMESTAMPDIFF(SECOND, pm.received_at, :now) "
                "           AS age_seconds, "
                "       pm.received_at, p.label AS probe_label, p.value_type, "
                "       p.probe_type "
                "  FROM probe_measures pm "
                "  JOIN probes p ON p.id = pm.probe_id "
                " WHERE pm.machines_id = :machines_id "
                "   AND (" + " OR ".join(batch_clauses) + ") "
                "   AND " + visible_sql +
                " ORDER BY p.label ASC, pm.value_text ASC, "
                "          pm.received_at DESC, pm.id DESC"), batch_params))

        # One row per (probe, instance), the freshest of each.
        deduplicated = []
        seen_instances = set()
        for measure in last_measures:
            key = (_to_int(measure.get('probe_id'), 0),
                   measure_instance(measure))
            if key in seen_instances:
                continue
            seen_instances.add(key)
            deduplicated.append(measure)
        last_measures = deduplicated
        attach_measure_detail(last_measures)

        open_alerts = _rows(session.execute(text(
            "SELECT a.id, a.probe_id, a.condition_id, a.machines_id, "
            "       a.hostname, a.severity, "
            "       a.status, a.value_at_trigger, a.value_text_at_trigger, "
            "       a.message, a.opened_at, a.last_seen_at, "
            "       a.occurrence_count, a.ack_user, a.ack_at, a.ack_comment, "
            "       a.resolved_at, a.resolved_reason, "
            # As in get_alerts: read to resolve `instance`, not returned.
            "       p.value_type, "
            "       p.label AS probe_label, p.unit "
            "  FROM alerts a "
            "  JOIN probes p ON p.id = a.probe_id "
            " WHERE a.machines_id = :machines_id "
            "   AND " + alert_active_sql() + " AND " + visible_sql +
            " ORDER BY FIELD(a.severity, 'info', 'medium', 'high', 'critical') DESC, "
            "          a.last_seen_at DESC"), params))
        # Same key and same rule as the alert list: the sheet and the list
        # must not describe one alert differently.
        annotate_alert_instances(open_alerts)

        # Dated before the conditions are judged: a verdict built on a value
        # nobody refreshed has to be able to say so.
        reporting = self._annotate_freshness(probes, last_measures,
                                             fallback_silence)

        self._annotate_probe_conditions(session, machines_id, probes,
                                        last_measures, open_alerts)

        agent_config = _one(session.execute(text(
            "SELECT machines_id, hostname, sent_version, sent_at, "
            "       acked_version, acked_at, probe_count, last_error, "
            "       updated_at "
            "  FROM probe_agent_config WHERE machines_id = :machines_id"),
            {'machines_id': machines_id})) or {}

        # The machine list reads the same expression for every machine it
        # shows, see config_stale_sql.
        settled = _one(session.execute(text(
            "SELECT " + config_stale_sql(target_fragment, ':machines_id',
                                         os_readable=memberships_readable)
            + " AS config_stale, "
            + placed_cadence_sql(target_fragment, visible_sql,
                                 ':machines_id') + " AS watched_cadence"),
            dict(params, **target_params))) or {}
        agent_config['config_stale'] = 1 if _to_int(
            settled.get('config_stale'), 0) else 0

        if reporting['state'] == 'unheard':
            # Nothing was ever heard from this machine, and whether that is a
            # silence depends on what is actually asked of it.
            if settled.get('watched_cadence') is None:
                reporting['state'] = 'unwatched'
            elif agent_config.get('sent_version'):
                reporting['state'] = 'silent'
            else:
                reporting['state'] = 'unknown'
            reporting['silent'] = 1 if reporting['state'] == 'silent' else 0

        # Same key and same rule as the machine list, read with the same
        # statement on one identifier: a sheet and a list disagreeing on
        # whether an agent is connected would be worse than neither showing it.
        presence = self._machines_presence(session, [machines_id])
        return {
            'machines_id': machines_id,
            'probes': probes,
            'last_measures': last_measures,
            'open_alerts': open_alerts,
            'agent_config': agent_config,
            'agent_online': (None if presence is None
                             else presence.get(machines_id, 0)),
            'reporting': reporting,
        }

    def _annotate_freshness(self, probes, last_measures, fallback_seconds):
        """Date what the machine sheet shows against the cadence it is placed
        at.
        """
        intervals = {}
        watched = {}
        server_side = {}
        for probe in probes or []:
            probe_id = _to_int(probe.get('probe_id'), 0)
            intervals[probe_id] = _to_int(probe.get('interval_seconds'), 0)
            server_side[probe_id] = (
                _to_int(probe.get('server_evaluated'), 0) == 1)
            watched[probe_id] = (
                _to_int(probe.get('probe_enabled'), 0) == 1
                and _to_int(probe.get('excluded'), 0) == 0
                and not server_side[probe_id])

        freshest = {}
        for measure in last_measures or []:
            probe_id = _to_int(measure.get('probe_id'), 0)
            interval = intervals.get(probe_id, 0)
            threshold = silence_after_seconds(interval, fallback_seconds)
            age = measure.get('age_seconds')
            age = None if age is None else _to_int(age, 0)
            measure['age_seconds'] = age
            measure['expected_interval_seconds'] = interval
            measure['silent_after_seconds'] = threshold
            # Instance by instance: a volume that stopped being reported is
            # stale on its own row while the others of the same probe are not.
            if age is None or not watched.get(probe_id, True):
                measure['stale'] = None
            else:
                measure['stale'] = 1 if age > threshold else 0
            if age is not None and (probe_id not in freshest
                                    or age < freshest[probe_id]):
                freshest[probe_id] = age

        summary = {'reporting': 0, 'silent': 0, 'never': 0, 'unwatched': 0,
                   'server': 0}
        machine_age = None
        machine_interval = 0
        watched_any = False
        for probe in probes or []:
            probe_id = _to_int(probe.get('probe_id'), 0)
            interval = intervals.get(probe_id, 0)
            threshold = silence_after_seconds(interval, fallback_seconds)
            age = freshest.get(probe_id)
            probe['expected_interval_seconds'] = interval
            probe['silent_after_seconds'] = threshold
            probe['measure_age_seconds'] = age
            if server_side.get(probe_id, False):
                # No collector, so no report to wait for: it owes nothing and
                # says nothing about the freshness of this machine.
                state = 'server'
            elif not watched.get(probe_id, True):
                state = 'unwatched'
            elif age is None:
                state = 'never'
            elif age > threshold:
                state = 'silent'
            else:
                state = 'reporting'
            probe['reporting_state'] = state
            probe['measure_stale'] = {'silent': 1, 'reporting': 0}.get(state)
            summary[state] += 1
            if state in ('unwatched', 'server'):
                # Nothing is asked of it, so it owes no report and its last
                # value must not drag the machine towards a silence verdict.
                continue
            watched_any = True
            # The machine owes a report as often as its fastest watched probe:
            # that is the cadence its own silence is judged against.
            if interval > 0:
                machine_interval = (interval if machine_interval == 0
                                    else min(machine_interval, interval))
            if age is not None and (machine_age is None or age < machine_age):
                machine_age = age

        threshold = silence_after_seconds(machine_interval, fallback_seconds)
        if probes and not watched_any:
            # Nothing measured is asked of this machine: every probe placed on
            # it is turned off, excepted, or evaluated by the server.
            state = 'unwatched'
        elif machine_age is None:
            state = 'unheard'
        elif machine_age > threshold:
            state = 'silent'
        elif summary['silent']:
            # It still speaks, but not about everything it was asked to.
            state = 'partial'
        else:
            state = 'reporting'
        return {
            'state': state,
            'silent': 1 if state == 'silent' else 0,
            'silence_seconds': machine_age,
            'expected_interval_seconds': machine_interval,
            'silent_after_seconds': threshold,
            'cadence_source': ('assignment' if machine_interval > 0
                               else 'default'),
            # probes_total counts what is placed here, the probes the server
            # evaluates included: they are placed.
            'probes_total': len(probes or []),
            'probes_reporting': summary['reporting'],
            'probes_silent': summary['silent'],
            'probes_never': summary['never'],
            'probes_unwatched': summary['unwatched'],
            'probes_server_evaluated': summary['server'],
        }

    def _annotate_probe_conditions(self, session, machines_id, probes,
                                   last_measures, open_alerts):
        """Hang the effective conditions on the probes of a machine sheet."""
        probe_ids = []
        for probe in probes:
            probe_id = _to_int(probe.get('probe_id'), 0)
            if probe_id > 0 and probe_id not in probe_ids:
                probe_ids.append(probe_id)

        conditions_by_probe = {}
        if probe_ids:
            # The estate of this machine: the sheet must judge its values
            # against the thresholds that actually raise alerts on it.
            scope = self._condition_scope(
                self._machine_entity(session, machines_id))
            fragment, params = _placeholders('cprobe', probe_ids)
            params.update(scope['params'])
            for condition in _rows(session.execute(text(
                    "SELECT pc.id, pc.probe_id, pc.operator, "
                    "       pc.display_order, "
                    "       " + condition_effective_sql('pc', scope['alias']) +
                    "  FROM probe_conditions pc " + scope['join'] +
                    " WHERE pc.probe_id IN (" + fragment + ") "
                    " ORDER BY pc.probe_id ASC, pc.display_order ASC, "
                    "          pc.id ASC"), params)):
                conditions_by_probe.setdefault(
                    _to_int(condition.get('probe_id'), 0), []).append(condition)

        # Every measure of a probe, not one of them: what the sheet shows is
        # one row per instance and what is judged must be the same set.
        measures_by_probe = {}
        for measure in last_measures or []:
            measures_by_probe.setdefault(
                _to_int(measure.get('probe_id'), 0), []).append(measure)

        alerted_probes = set()
        alerted_conditions = set()
        # Most serious standing alert per probe and instance, the instance
        # read by the same rule as the measures ('' on a single value probe).
        worst_alert_rank = {}
        for alert in open_alerts or []:
            alert_probe_id = _to_int(alert.get('probe_id'), 0)
            alerted_probes.add(alert_probe_id)
            condition_id = _to_int(alert.get('condition_id'), 0)
            if condition_id > 0:
                alerted_conditions.add(condition_id)
            key = (alert_probe_id, str(alert.get('instance') or ''))
            worst_alert_rank[key] = max(
                worst_alert_rank.get(key, 0),
                SEVERITY_RANK.get(
                    str(alert.get('severity') or '').strip().lower(), 0))

        for probe in probes:
            probe_id = _to_int(probe.get('probe_id'), 0)
            conditions = conditions_by_probe.get(probe_id, [])

            # A probe turned off or excepted here is not measured, so no
            # condition of it is watched: saying it is satisfied would claim a
            # surveillance that does not run.
            server_evaluated = _to_int(probe.get('server_evaluated'), 0) == 1
            watched = (_to_int(probe.get('probe_enabled'), 0) == 1
                       and _to_int(probe.get('excluded'), 0) == 0
                       and not server_evaluated)
            usable = [measure
                      for measure in measures_by_probe.get(probe_id, [])
                      if str(measure.get('status') or 'ok') != 'unavailable']
            # Every value read below is older than what the cadence of this
            # probe promises.
            evidence_stale = 1 if (usable and all(
                _to_int(measure.get('stale'), 0) == 1
                for measure in usable)) else 0

            active = 0
            breaching = 0
            unknown = 0
            severity_rank = 0
            for condition in conditions:
                condition['enabled'] = _to_int(condition.get('enabled'), 0)
                condition['duration_seconds'] = _to_int(
                    condition.get('duration_seconds'), 0)
                condition['alert_open'] = (
                    1 if _to_int(condition.get('id'), 0) in alerted_conditions
                    else 0)

                condition['breaching_instances'] = []
                condition['evidence_stale'] = 0
                condition['superseded'] = 0
                if not condition['enabled']:
                    # Disabled: it raises nothing, it is not read either.
                    condition['breaching'] = None
                    continue
                active += 1
                if not watched or not usable:
                    condition['breaching'] = None
                    if not server_evaluated:
                        unknown += 1
                    continue

                crossed = []
                compared = 0
                holds_any = False
                for measure in usable:
                    holds = condition_holds_now(condition,
                                                measure.get('value_num'),
                                                measure.get('value_text'))
                    if holds is None:
                        continue
                    compared += 1
                    if not holds:
                        continue
                    holds_any = True
                    # A probe reporting a single value has no instance to
                    # name: the crossing is the probe itself.
                    instance = measure_instance(measure)
                    if instance is not None:
                        crossed.append(instance)

                if not compared:
                    # Nothing could be compared at all.
                    condition['breaching'] = None
                    unknown += 1
                    continue
                condition['breaching'] = 1 if holds_any else 0
                condition['breaching_instances'] = crossed
                condition['evidence_stale'] = evidence_stale
                if holds_any and not condition['alert_open']:
                    rank = SEVERITY_RANK.get(
                        str(condition.get('severity') or '').strip().lower(),
                        0)
                    if all(worst_alert_rank.get((probe_id, instance), 0) > rank
                           for instance in (crossed or [''])):
                        condition['superseded'] = 1
                        condition['alert_open'] = 1
                if holds_any:
                    breaching = 1
                    severity_rank = max(severity_rank, SEVERITY_RANK.get(
                        str(condition.get('severity') or '').strip().lower(),
                        0))

            probe['conditions'] = conditions
            probe['breaching'] = breaching
            probe['evidence_stale'] = evidence_stale
            probe['alert_open'] = 1 if probe_id in alerted_probes else 0
            probe['breaching_severity'] = ''
            for severity, rank in SEVERITY_RANK.items():
                if rank == severity_rank:
                    probe['breaching_severity'] = severity
                    break

            if not active:
                probe['conditions_state'] = 'none'
            elif server_evaluated:
                # Its verdict is the alert the server raises or does not raise;
                # there is nothing on this sheet to read it from, and calling
                # it undecided would state an ignorance that is not one.
                probe['conditions_state'] = 'server'
            elif breaching:
                probe['conditions_state'] = 'breaching'
            elif unknown:
                probe['conditions_state'] = 'unknown'
            else:
                probe['conditions_state'] = 'satisfied'

    @DatabaseHelper._sessionm
    def get_agent_config(self, session, machines_id, login=''):
        """Probe configuration distributed to the agent of a machine."""
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return {}
        scope_sql, params = self._machine_scope_clause(
            login, ':machines_id',
            readable=self._memberships_readable(session))
        params['machines_id'] = machines_id
        return _one(session.execute(text(
            "SELECT id, machines_id, hostname, sent_version, sent_at, "
            "       acked_version, acked_at, probe_count, last_error, "
            "       updated_at "
            "  FROM probe_agent_config WHERE machines_id = :machines_id "
            "   AND " + scope_sql), params)) or {}

    # =========================================================================
    # Measures
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_measures_timeseries(self, session, login, machines_id, probe_id,
                                days=7, max_points=5000, hours=None):
        """Measures of one probe on one machine over a period."""
        # Nothing to draw and nothing to say about how it was drawn: the empty
        # answer carries the same keys as a full one, so that a console never
        # has to test for their presence before reading them.
        empty = {'total': 0, 'data': [], 'series_keys': [],
                 'truncated': False, 'aggregated': 0, 'bucket_seconds': 0,
                 'points': 0,
                 # The probe is named by nothing here: a value type left
                 # empty is what tells a refusal apart from a numeric probe
                 # that has no point over the period.
                 'probe_id': 0, 'probe_label': '', 'metric_key': '',
                 'unit': '', 'value_type': ''}

        machines_id = _to_int(machines_id, 0)
        probe_id = _to_int(probe_id, 0)
        if machines_id <= 0 or probe_id <= 0:
            return dict(empty)

        access = self._probe_access(session, login, probe_id)
        if not access['visible']:
            return dict(empty)

        # Before the measures are read: the estate of the reader decides
        # whether this machine may be described at all.
        if not self._machine_in_scope(session, login, machines_id):
            return dict(empty)

        # The same period the presence strip of the machine is read over, see
        # measure_window: the two are driven by one selector on the page.
        window = measure_window(days, hours)
        max_points = min(max(_to_int(max_points, 5000), 1),
                         MEASURE_POINTS_CEILING)
        since = datetime.now() - window

        params = {'machines_id': machines_id, 'probe_id': probe_id,
                  'since': since,
                  'batch_window': MEASURE_BATCH_WINDOW_SECONDS}
        # Two figures, one statement: how many points the window holds, and how
        # many curves they make.
        counts = _one(session.execute(text(
            "SELECT (SELECT COUNT(*) FROM probe_measures "
            "         WHERE machines_id = :machines_id "
            "           AND probe_id = :probe_id "
            "           AND received_at >= :since) AS total, "
            "       (SELECT COUNT(DISTINCT value_text) FROM probe_measures "
            "         WHERE machines_id = :machines_id "
            "           AND probe_id = :probe_id "
            "           AND received_at >= "
            "               (SELECT DATE_SUB(MAX(received_at), "
            "                                INTERVAL :batch_window SECOND) "
            "                  FROM probe_measures "
            "                 WHERE machines_id = :machines_id "
            "                   AND probe_id = :probe_id)) AS instances"),
            params)) or {}
        total = _to_int(counts.get('total'), 0)

        probe = access['probe'] or {}
        # A text probe holds its value in value_text: telling curves apart on
        # it would draw one per distinct status, and a status is not a curve.
        named = str(probe.get('value_type')
                    or 'numeric').strip().lower() != 'text'
        # COUNT(DISTINCT) ignores NULL, so a probe reporting a single value
        # answers zero here and is served exactly as it always was.
        instances = _to_int(counts.get('instances'), 0) if named else 0

        # The budget of points is per curve: a machine with three volumes must
        # be served the same period as a machine with one, not a third of it.
        curves = max(instances, 1)
        # Past that budget the window is reduced instead of being cut, which
        # is what makes a week end where the operator asked it to end.
        aggregated = named and total > max_points * curves
        bucket_seconds = 0

        if aggregated:
            target = min(MEASURE_AGGREGATE_POINTS, max_points)
            window_seconds = int(window.total_seconds())
            # Ceiling division: the intervals must cover the window whole, one
            # second short and the end of the period falls outside them.
            bucket_seconds = max(-(-window_seconds // target), 1)
            params['bucket'] = bucket_seconds
            # One interval per curve, plus the partial one the window edge cuts
            # and one of margin, so that a complete answer never comes back
            # sitting exactly on its own limit and reading as cut.
            params['limit'] = min((target + 2) * curves,
                                  MEASURE_POINTS_CEILING)
            # Intervals anchored on the epoch and not on :since, so their
            # boundaries do not move between two refreshes of the same chart: a
            # point that shifted by a few seconds every minute would read as a
            # measurement that never settles.
            rows = _rows(session.execute(text(
                "SELECT MIN(collected_at) AS collected_at, "
                "       MIN(received_at) AS received_at, "
                "       MAX(received_at) AS received_until, "
                "       ROUND(AVG(value_num), 6) AS value_num, "
                "       MIN(value_num) AS value_min, "
                "       MAX(value_num) AS value_max, "
                "       COUNT(*) AS sample_count, "
                "       value_text, MAX(unit) AS unit, "
                "       MAX(status) AS status "
                "  FROM probe_measures "
                " WHERE machines_id = :machines_id AND probe_id = :probe_id "
                "   AND received_at >= :since "
                " GROUP BY value_text, "
                "          FLOOR(UNIX_TIMESTAMP(received_at) / :bucket) "
                " ORDER BY MIN(received_at) DESC "
                " LIMIT :limit"), params))
        else:
            params['limit'] = min(max_points * curves,
                                  MEASURE_POINTS_CEILING)
            # Read from the end of the window backwards.
            rows = _rows(session.execute(text(
                "SELECT collected_at, received_at, value_num, value_text, "
                "       unit, status, detail "
                "  FROM probe_measures "
                " WHERE machines_id = :machines_id AND probe_id = :probe_id "
                "   AND received_at >= :since "
                " ORDER BY received_at DESC "
                " LIMIT :limit"), params))
        # Both statements read backwards, the console reads forwards.
        rows.reverse()
        attach_measure_detail(rows)

        # The curves, in a stable order so the legend does not move from one
        # refresh to the next.
        series_keys = []
        if named:
            series_keys = sorted(set(
                str(row.get('value_text')) for row in rows
                if row.get('value_text') is not None))

        # What is missing, and it is never the recent end.
        if aggregated:
            truncated = len(rows) >= params['limit']
        else:
            truncated = total > len(rows)

        threshold = self._probe_reference_threshold(session, probe_id,
                                                    machines_id)
        answer = {
            'total': total,
            'data': rows,
            'truncated': truncated,
            # 1: every point is an interval, not a measure.
            'aggregated': 1 if aggregated else 0,
            # Width of an interval in seconds, 0 when nothing was reduced.
            'bucket_seconds': bucket_seconds,
            'points': len(rows),
            'probe_id': probe_id,
            # Text and never NULL, as the empty answer spells them: unit is a
            # nullable column, and a key that changes type between two answers
            # is read wrong once.
            'probe_label': str(probe.get('label') or ''),
            'metric_key': str(probe.get('metric_key') or ''),
            'unit': str(probe.get('unit') or ''),
            'value_type': str(probe.get('value_type') or ''),
            # Empty: one curve, drawn from data as before.
            'series_keys': series_keys,
        }
        # A probe whose conditions carry no plottable threshold simply comes
        # back without these keys: the console draws no line, which is the
        # honest rendering of "nothing is compared on this axis".
        answer.update(threshold)
        return answer

    def _probe_reference_threshold(self, session, probe_id, machines_id=None):
        """Threshold the chart of a probe draws as a reference line."""
        scope = self._condition_scope(self._machine_entity(session, machines_id))
        operator_sql, params = _placeholders('unplottable', THRESHOLDLESS_OPERATORS)
        params['probe_id'] = probe_id
        params.update(scope['params'])
        threshold = condition_field_sql('threshold_value', 'pc', scope['alias'])
        row = _one(session.execute(text(
            "SELECT " + threshold + " AS threshold_value, "
            "       " + condition_field_sql('severity', 'pc', scope['alias'])
            + " AS severity, "
            "       pc.operator "
            "  FROM probe_conditions pc " + scope['join'] +
            " WHERE pc.probe_id = :probe_id "
            "   AND " + condition_field_sql('enabled', 'pc', scope['alias'])
            + " = 1 "
            "   AND " + threshold + " IS NOT NULL "
            "   AND pc.operator NOT IN (" + operator_sql + ") "
            " ORDER BY pc.display_order ASC, pc.id ASC "
            " LIMIT 1"), params))
        if not row:
            return {}

        try:
            threshold_value = float(row.get('threshold_value'))
        except (TypeError, ValueError):
            return {}

        severity = str(row.get('severity') or '').strip().lower()
        return {
            'threshold_value': threshold_value,
            # The severity colours the line: a critical probe must not be read
            # as an informative one.
            'threshold_severity': severity if severity in SEVERITIES else '',
            'threshold_operator': str(row.get('operator') or ''),
        }

    # =========================================================================
    # Agent presence
    # =========================================================================
    _presence_history_unreadable_logged = False

    @DatabaseHelper._sessionm
    def get_agent_presence(self, session, login, machines_id, days=7,
                           hours=None):
        """When the agent of one machine was connected over a period."""
        end = datetime.now()
        window = measure_window(days, hours)
        start = end - window
        answer = {
            'data': [],
            'from': _serialise(start),
            'to': _serialise(end),
            'known_from': None,
            'unavailable': 0,
            'refused': 0,
        }
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return answer
        # Folded into the dive that reads the JID: the guard costs no statement
        # of its own, and an xmppmaster that cannot be read falls in the except
        # below, which answers `unavailable` rather than an empty strip.
        scope_sql, scope_params = self._machine_scope_clause(login, 'm.id')

        # The bare JID is the exact predicate, the prefix is what lets the
        # index on the JID be ranged instead of scanned: it may match wider --
        # a hostname holding an underscore makes it a wildcard -- and the
        # equality on the bare JID removes whatever it took in excess.
        jid_sql = ("(um.jid = :jid_bare "
                   " OR (um.jid LIKE :jid_prefix "
                   "     AND SUBSTRING_INDEX(um.jid, '/', 1) = :jid_bare))")
        try:
            machine = _one(session.execute(text(
                "SELECT m.jid, m.enabled, "
                # Whether anything at all was ever recorded, for any machine.
                "       (SELECT 1 FROM xmppmaster.uptime_machine LIMIT 1) "
                "           AS recorded "
                "  FROM xmppmaster.machines m "
                " WHERE m.id = :machines_id AND " + scope_sql),
                dict(scope_params, machines_id=machines_id)))
            if machine is None:
                # xmppmaster answered, and no machine of this identifier stands
                # in the estate of the reader: none was ever registered under
                # it, or it belongs to another client.
                ReflexDatabase._presence_history_unreadable_logged = False
                return answer
            bare = str(machine.get('jid') or '').strip().split('/')[0]
            if not bare:
                return answer
            rows = _rows(session.execute(text(
                # The state holding when the period opens is carried by the
                # last event before it, which is why it is read: without it a
                # machine connected for three weeks would show a strip
                # starting at its last reconnection and nothing before, when
                # what is true is that it was connected the whole time.
                "(SELECT um.id, um.date AS moment, um.status, um.updowntime "
                "   FROM xmppmaster.uptime_machine um "
                "  WHERE " + jid_sql + " AND um.date < :since "
                "  ORDER BY um.date DESC, um.id DESC LIMIT 1) "
                "UNION ALL "
                # Read from the end of the period backwards: what a ceiling
                # cuts on a flapping machine must be the oldest part of the
                # strip, never the end the operator came to see.
                "(SELECT um.id, um.date, um.status, um.updowntime "
                "   FROM xmppmaster.uptime_machine um "
                "  WHERE " + jid_sql +
                "    AND um.date >= :since AND um.date <= :until "
                "  ORDER BY um.date DESC, um.id DESC LIMIT :limit)"),
                {'jid_bare': bare, 'jid_prefix': bare + '/%',
                 'since': start, 'until': end,
                 'limit': PRESENCE_EVENTS_MAX}))
        except Exception as e:
            session.rollback()
            if not ReflexDatabase._presence_history_unreadable_logged:
                logger.error("Reflex: xmppmaster unreadable, the presence of "
                             "the agents is not shown on the machine sheets "
                             "(%s)" % e)
                ReflexDatabase._presence_history_unreadable_logged = True
            answer['unavailable'] = 1
            return answer
        ReflexDatabase._presence_history_unreadable_logged = False

        events = []
        for row in rows:
            moment = _read_moment(row.get('moment'))
            if moment is None:
                continue
            events.append({
                'moment': moment,
                'id': _to_int(row.get('id'), 0),
                'online': 1 if _to_int(row.get('status'), 0) else 0,
                # Duration the master measured for the state that ended here.
                'held': _to_int(row.get('updowntime'), 0),
            })
        events.sort(key=lambda event: (event['moment'], event['id']))
        inside = [event for event in events if event['moment'] >= start]
        if len(inside) >= PRESENCE_EVENTS_MAX:
            # The oldest part of the period was cut.
            events = inside

        # What the sheet reads as the connection dot of this machine, from the
        # column _machines_presence reads: the strip and the dot above it
        # cannot disagree about the state the machine is in now.
        current = 1 if _to_int(machine.get('enabled'), 0) == 1 else 0

        if events:
            segments = presence_segments(events, start, end, current)
        elif _to_int(machine.get('recorded'), 0) == 1:
            # No event at all, neither in the period nor before it, on a master
            # that does record them: this machine has not changed state over
            # the whole history kept -- a machine connected and left alone
            # writes one row the day it registers, and the purge takes that row
            # after four weeks.
            segments = [{'from': start, 'to': end, 'online': current}]
        else:
            # Nothing was ever recorded, for any machine.
            segments = []

        answer['data'] = [{'from': _serialise(segment['from']),
                           'to': _serialise(segment['to']),
                           'online': segment['online']}
                          for segment in segments]
        answer['known_from'] = (answer['data'][0]['from']
                                if answer['data'] else None)
        return answer

    # =========================================================================
    # Dashboard
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_dashboard_summary(self, session, login=''):
        """Figures of the supervision dashboard."""
        login = str(login or '')
        visible_sql, params = self._visible_clause(login)
        # Read once for the whole call: the alerts and the counted
        # configurations are all restricted on the same estate.
        memberships_readable = self._memberships_readable(session)

        # An alert names a machine, so counting them is naming how many
        # incidents an estate carries: the count follows the machine and not
        # the probe, exactly as the list does.
        alert_scope_sql, alert_scope_params = self._machine_scope_clause(
            login, 'a.machines_id', readable=memberships_readable,
            prefix='ascope')
        params.update(alert_scope_params)
        alert_where = (" WHERE " + alert_active_sql() + " AND " + visible_sql
                       + " AND " + alert_scope_sql)

        by_severity = {'info': 0, 'medium': 0, 'high': 0, 'critical': 0}
        ack_by_severity = {'info': 0, 'medium': 0, 'high': 0, 'critical': 0}
        rows = _rows(session.execute(text(
            "SELECT a.severity, a.status, COUNT(*) AS total "
            "  FROM alerts a JOIN probes p ON p.id = a.probe_id "
            + alert_where +
            " GROUP BY a.severity, a.status"), params))
        for row in rows:
            severity = row.get('severity')
            if severity not in by_severity:
                continue
            total = _to_int(row.get('total'), 0)
            by_severity[severity] += total
            if row.get('status') == ALERT_STATUS_ACK:
                ack_by_severity[severity] += total

        # A machine is taken in hand once none of its standing alerts is still
        # open: counted the other way round, a machine carrying one handled
        # alert and one nobody has seen would read as handled.
        impacted_params = dict(params)
        impacted_params['status_open'] = ALERT_STATUS_OPEN
        impacted = _one(session.execute(text(
            "SELECT COUNT(DISTINCT a.machines_id) AS impacted, "
            "       COUNT(DISTINCT CASE WHEN a.status = :status_open "
            "                           THEN a.machines_id END) AS unhandled "
            "  FROM alerts a JOIN probes p ON p.id = a.probe_id "
            + alert_where),
            impacted_params)) or {}
        machines_impacted = _to_int(impacted.get('impacted'), 0)
        machines_impacted_ack = machines_impacted - _to_int(
            impacted.get('unhandled'), 0)

        top_probes = _rows(session.execute(text(
            "SELECT a.probe_id, p.label, COUNT(*) AS alert_count, "
            "       MAX(FIELD(a.severity, 'info', 'medium', 'high', 'critical')) "
            "         AS severity_rank "
            "  FROM alerts a JOIN probes p ON p.id = a.probe_id "
            + alert_where +
            " GROUP BY a.probe_id, p.label "
            " ORDER BY alert_count DESC "
            " LIMIT 10"), params))
        rank_to_severity = {1: 'info', 2: 'medium', 3: 'high', 4: 'critical'}
        for row in top_probes:
            row['alert_count'] = _to_int(row.get('alert_count'), 0)
            row['severity'] = rank_to_severity.get(
                _to_int(row.pop('severity_rank', 0), 0), 'info')

        # One row per machine: the estate of the reader decides it, see
        # machine_scope_sql.
        scope_sql, scope_params = self._machine_scope_clause(
            login, 'ac.machines_id', readable=memberships_readable)

        probes_total = _to_int(session.execute(text(
            "SELECT COUNT(*) FROM probes p WHERE " + visible_sql),
            params).scalar(), 0)
        machines_supervised = _to_int(session.execute(text(
            "SELECT COUNT(*) FROM probe_agent_config ac "
            " WHERE " + scope_sql), scope_params).scalar(), 0)
        config_drift = _to_int(session.execute(text(
            "SELECT COUNT(*) FROM probe_agent_config ac "
            " WHERE ac.sent_version IS NOT NULL "
            "   AND (ac.acked_version IS NULL "
            "        OR ac.acked_version <> ac.sent_version) "
            "   AND " + scope_sql), scope_params).scalar(), 0)

        return {
            'alerts_by_severity': by_severity,
            # Key kept as it is read by the console; it counts the alerts
            # that stand, acknowledged ones included.
            'alerts_open_total': sum(by_severity.values()),
            'alerts_ack_total': sum(ack_by_severity.values()),
            'alerts_ack_by_severity': ack_by_severity,
            'machines_impacted': machines_impacted,
            'machines_impacted_ack': machines_impacted_ack,
            'machines_supervised': machines_supervised,
            'config_drift': config_drift,
            'probes_total': probes_total,
            'top_probes': top_probes,
        }

    # =========================================================================
    # Notification channels
    # =========================================================================
    # Columns a channel is read through, everywhere.
    CHANNEL_COLUMNS = (
        "c.id, c.name, c.entity_id, c.channel_type, c.config_json, "
        "c.enabled, c.created_by, c.created_at, c.updated_at, "
        "CASE WHEN c.secret_encrypted IS NULL OR c.secret_encrypted = '' "
        "     THEN 0 ELSE 1 END AS secret_configured")

    def _channel_visible_clause(self, login):
        """Visibility fragment and its parameters, for one login."""
        login = _login(login)
        if not login:
            # Closed, as channel_visible_sql closes on an estate that resolves
            # to nothing: a caller naming nobody reads nobody's channels.
            return "0", {}
        return channel_visible_sql(self.entities_for_login(login))

    def _channel_access(self, session, login, channel_id):
        """Return whether a login may read and manage one channel."""
        access = {'exists': False, 'visible': False, 'channel': None}
        channel_id = _to_int(channel_id, 0)
        if channel_id <= 0:
            return access
        fragment, params = self._channel_visible_clause(login)
        params['channel_id'] = channel_id
        row = _one(session.execute(text(
            "SELECT " + self.CHANNEL_COLUMNS + ", "
            "       CASE WHEN " + fragment + " THEN 1 ELSE 0 END AS visible "
            "  FROM notification_channels c WHERE c.id = :channel_id"),
            params))
        if row is None:
            return access
        access['exists'] = True
        access['visible'] = bool(_to_int(row.pop('visible', 0), 0))
        access['channel'] = row
        return access

    def _channel_entity_from_payload(self, channel, login='', source=None):
        """Entity a channel is written under."""
        source = source or {}
        current = source.get('entity_id')
        current = str(current) if current is not None else None
        raw = channel.get('entity_id', current)
        if raw is None or not str(raw).strip():
            if current is not None:
                return current
            raise ReflexValidationError(
                "A channel belongs to an entity, and none was named",
                'entity_id', RefusalReason.FIELD_REQUIRED)
        asked = _to_int(str(raw).strip(), -1)
        if asked < 0:
            raise ReflexValidationError(
                "Entity identifier not readable: %s" % raw, 'entity_id',
                RefusalReason.FIELD_FORMAT_INVALID)
        asked = str(asked)
        # Keeping the entity a channel already carries is not a scope change.
        if asked == current:
            return asked
        if asked not in self.entities_for_login(login):
            raise ReflexValidationError(
                "You have no access to entity %s" % asked, 'entity_id',
                RefusalReason.ENTITY_FORBIDDEN)
        return asked

    @DatabaseHelper._sessionm
    def get_channels(self, session, start=0, limit=0, include_disabled=True,
                     login=''):
        """Notification channels, never their secret."""
        fragment, params = self._channel_visible_clause(login)
        clauses = [fragment]
        if not include_disabled:
            clauses.append("c.enabled = 1")
        sql = ("SELECT " + self.CHANNEL_COLUMNS +
               "  FROM notification_channels c "
               " WHERE " + " AND ".join(clauses) +
               " ORDER BY c.name ASC")
        limit = _to_int(limit, 0)
        if limit > 0:
            sql += " LIMIT :limit OFFSET :start"
            params['limit'] = limit
            params['start'] = max(_to_int(start, 0), 0)
        rows = _rows(session.execute(text(sql), params))
        for row in rows:
            row['config_json'] = channel_config_for_reading(
                row.get('config_json'))
        return rows

    @DatabaseHelper._sessionm
    def get_channel(self, session, channel_id, login=''):
        """One channel, by id, without its secret."""
        access = self._channel_access(session, login, channel_id)
        if not _reachable(access):
            return {}
        channel = access['channel']
        channel['config_json'] = channel_config_for_reading(
            channel.get('config_json'))
        return channel

    @DatabaseHelper._sessionm
    def get_channel_secret(self, session, channel_id, aes_key):
        """Read back the secret of a channel, for a sending only."""
        channel_id = _to_int(channel_id, 0)
        if channel_id <= 0:
            return ''
        stored = session.execute(text(
            "SELECT secret_encrypted FROM notification_channels "
            " WHERE id = :channel_id"), {'channel_id': channel_id}).scalar()
        return decrypt_secret(stored, aes_key)

    def _validate_channel_payload(self, channel, login=''):
        """Normalise a channel payload, secret excluded."""
        if not isinstance(channel, dict):
            raise ReflexValidationError("A channel must be a structure", None,
                                        RefusalReason.PAYLOAD_MALFORMED)
        channel_type = str(channel.get('channel_type', 'email')
                           or 'email').strip().lower()
        if channel_type not in CHANNEL_TYPES:
            raise ReflexValidationError(
                "Unknown channel type: %s" % channel_type, 'channel_type',
                RefusalReason.CHANNEL_TYPE_UNKNOWN)
        created_by = _clean_str(channel.get('created_by') or login, 255,
                                'created_by') or 'unknown'
        return {
            'name': _clean_str(channel.get('name'), 255, 'name', required=True),
            'channel_type': channel_type,
            # The guard on secret looking keys stays: config_json is returned
            # to the console, a password has nothing to do in it.
            'config_json': validate_config_json(channel.get('config_json')),
            'enabled': _to_bool_int(channel.get('enabled', 1)),
            'created_by': created_by,
        }

    def _channel_secret_from_payload(self, channel, aes_key):
        """Decide what happens to the secret of a channel on a write."""
        if _to_bool_int(channel.get('clear_secret', 0)):
            if channel.get('smtp_password'):
                logger.info("Reflex: channel secret cleared, the password sent "
                            "along is ignored")
            return ('clear', None)
        plaintext = channel.get('smtp_password')
        if plaintext is None or str(plaintext) == '':
            return ('keep', None)
        return ('set', encrypt_secret(plaintext, aes_key))

    def _channel_write(self, channel, login, aes_key, source=None):
        """Columns and secret gesture of a channel write, else a refusal.

        Returns (values, action, ciphered, None) or (None, None, None,
        refusal).
        """
        try:
            values = self._validate_channel_payload(channel, login=login)
            values['entity_id'] = self._channel_entity_from_payload(
                channel, login=login, source=source)
            action, ciphered = self._channel_secret_from_payload(channel,
                                                                 aes_key)
        except ReflexSecretError as e:
            logger.error("Reflex: channel secret refused: %s" % e)
            return None, None, None, refused(
                REFUSAL_FAILED, str(e), 'smtp_password',
                reason=RefusalReason.SECRET_KEY_UNUSABLE)
        except ReflexValidationError as e:
            logger.warning("Reflex: invalid channel payload: %s" % e)
            return None, None, None, refused_from(e)
        return values, action, ciphered, None

    def _channel_name_taken(self, values):
        """The refusal a channel name already borne in that estate answers."""
        logger.warning("Reflex: entity %s already has a channel named '%s'"
                       % (values['entity_id'], values['name']))
        return refused(REFUSAL_INVALID,
                       "A channel of your entity is already named '%s'"
                       % values['name'],
                       'name', reason=RefusalReason.NAME_ALREADY_USED)

    @DatabaseHelper._sessionm
    def create_channel(self, session, channel, login='', aes_key=''):
        """Create a notification channel."""
        values, action, ciphered, refusal = self._channel_write(
            channel, login, aes_key)
        if refusal:
            return refusal
        values['secret_encrypted'] = ciphered if action == 'set' else None
        try:
            result = session.execute(text(
                "INSERT INTO notification_channels (name, entity_id, "
                "  channel_type, config_json, secret_encrypted, enabled, "
                "  created_by, created_at, updated_at) "
                "VALUES (:name, :entity_id, :channel_type, :config_json, "
                "  :secret_encrypted, :enabled, :created_by, NOW(), NOW())"),
                values)
            session.commit()
        except IntegrityError:
            # uk_entity_name: the homonym is a channel of the same entity,
            # never one belonging to another client.
            session.rollback()
            return self._channel_name_taken(values)
        except Exception as e:
            session.rollback()
            logger.error("Reflex: channel creation failed: %s" % e)
            return refused(REFUSAL_FAILED, "The channel could not be created")
        channel_id = _to_int(result.lastrowid, 0)
        if not channel_id:
            return refused(REFUSAL_FAILED,
                           "The channel was written but its identifier could "
                           "not be read back")
        return channel_id

    @DatabaseHelper._sessionm
    def update_channel(self, session, channel_id, channel, login='',
                       aes_key=''):
        """Update a notification channel."""
        channel_id = _to_int(channel_id, 0)
        if channel_id <= 0:
            return refused(REFUSAL_INVALID, "No channel was named",
                           'channel_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        access = self._channel_access(session, login, channel_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, CHANNEL_GONE)
        values, action, ciphered, refusal = self._channel_write(
            channel, login, aes_key, source=access['channel'])
        if refusal:
            return refusal

        secret_fragment = ""
        if action == 'set':
            secret_fragment = " secret_encrypted = :secret_encrypted,"
            values['secret_encrypted'] = ciphered
        elif action == 'clear':
            secret_fragment = " secret_encrypted = NULL,"

        values['channel_id'] = channel_id
        try:
            session.execute(text(
                "UPDATE notification_channels "
                "   SET name = :name, entity_id = :entity_id, "
                "       channel_type = :channel_type, "
                "       config_json = :config_json,"
                + secret_fragment +
                "       enabled = :enabled, updated_at = NOW() "
                " WHERE id = :channel_id"), values)
            session.commit()
        except IntegrityError:
            session.rollback()
            return self._channel_name_taken(values)
        except Exception as e:
            session.rollback()
            logger.error("Reflex: channel update failed: %s" % e)
            return refused(REFUSAL_FAILED, "The channel could not be updated")
        return True

    @DatabaseHelper._sessionm
    def delete_channel(self, session, channel_id, login=''):
        """Delete a channel. Its rules follow through the foreign key.

        Returns True, or the structure built by `refused`.
        """
        channel_id = _to_int(channel_id, 0)
        if channel_id <= 0:
            return refused(REFUSAL_INVALID, "No channel was named",
                           'channel_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        access = self._channel_access(session, login, channel_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, CHANNEL_GONE)
        try:
            result = session.execute(
                text("DELETE FROM notification_channels WHERE id = :channel_id"),
                {'channel_id': channel_id})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: channel deletion failed: %s" % e)
            return refused(REFUSAL_FAILED, "The channel could not be deleted")
        if _to_int(result.rowcount, 0) <= 0:
            return refused(REFUSAL_MISSING, CHANNEL_GONE)
        return True

    # =========================================================================
    # Notification rules
    # =========================================================================
    def _rule_access(self, session, login, rule_id):
        """Whether a login may read and manage one notification rule."""
        access = {'exists': False, 'visible': False, 'rule': None}
        rule_id = _to_int(rule_id, 0)
        if rule_id <= 0:
            return access
        fragment, params = self._channel_visible_clause(login)
        params['rule_id'] = rule_id
        row = _one(session.execute(text(
            "SELECT r.id, r.channel_id, r.probe_id, r.created_by, "
            "       c.entity_id AS channel_entity_id, "
            "       CASE WHEN " + fragment + " THEN 1 ELSE 0 END AS visible "
            "  FROM notification_rules r "
            "  JOIN notification_channels c ON c.id = r.channel_id "
            " WHERE r.id = :rule_id"), params))
        if row is None:
            return access
        access['exists'] = True
        access['visible'] = bool(_to_int(row.pop('visible', 0), 0))
        access['rule'] = row
        return access

    @DatabaseHelper._sessionm
    def get_notification_rules(self, session, start=0, limit=0, login=''):
        """Notification rules, with the channel and probe labels joined."""
        fragment, params = self._channel_visible_clause(login)
        sql = ("SELECT r.id, r.channel_id, r.probe_id, r.min_severity, "
               "       r.recipients, r.target_filter, r.cooldown_minutes, "
               "       r.escalation_minutes, r.enabled, r.created_by, "
               "       r.created_at, c.name AS channel_name, "
               "       c.channel_type, c.enabled AS channel_enabled, "
               "       c.entity_id AS channel_entity_id, "
               "       p.label AS probe_label "
               "  FROM notification_rules r "
               "  JOIN notification_channels c ON c.id = r.channel_id "
               "  LEFT JOIN probes p ON p.id = r.probe_id "
               " WHERE " + fragment +
               " ORDER BY c.name ASC, r.id ASC")
        limit = _to_int(limit, 0)
        if limit > 0:
            sql += " LIMIT :limit OFFSET :start"
            params['limit'] = limit
            params['start'] = max(_to_int(start, 0), 0)
        return self._mark_rules_reaching_nothing(
            session, login, _rows(session.execute(text(sql), params)))

    def _mark_rules_reaching_nothing(self, session, login, rows):
        """Flag the rules whose channel sits in an estate without machines."""
        rows = rows or []
        if not rows:
            return rows
        counted = self._machines_counted_by_entity(session, login)
        reached = set(entity for entity, count in counted.items() if count > 0)
        for row in rows:
            entity = str(row.get('channel_entity_id') or '').strip()
            row['reaches_nothing'] = (
                1 if reached and entity.isdigit()
                and str(int(entity)) not in reached else 0)
        return rows

    def _validate_rule_payload(self, session, rule, login=''):
        if not isinstance(rule, dict):
            raise ReflexValidationError("A rule must be a structure", None,
                                        RefusalReason.PAYLOAD_MALFORMED)

        channel_id = _to_int(rule.get('channel_id'), 0)
        if channel_id <= 0:
            raise ReflexValidationError("A rule needs a notification channel",
                                        'channel_id',
                                        RefusalReason.FIELD_REQUIRED)
        # A channel of another client is unknown here, in those words and with
        # that reason: a rule is never pointed at a channel its author cannot
        # read, and the refusal does not confirm that the identifier exists.
        fragment, params = self._channel_visible_clause(login)
        params['channel_id'] = channel_id
        if not _to_int(session.execute(
                text("SELECT COUNT(*) FROM notification_channels c "
                     " WHERE c.id = :channel_id AND " + fragment),
                params).scalar(), 0):
            raise ReflexValidationError("Unknown notification channel",
                                        'channel_id',
                                        RefusalReason.CHANNEL_UNKNOWN)

        probe_id = _to_int(rule.get('probe_id'), 0)
        if probe_id <= 0:
            probe_id = None
        else:
            # Read on the visibility and not on the existence, for the reason
            # the channel is read on it: a rule is never pointed at a probe
            # its author cannot read, and naming one would put its label on
            # the rule list.
            visible_sql, probe_params = self._visible_clause(login)
            probe_params['probe_id'] = probe_id
            if not _to_int(session.execute(
                    text("SELECT COUNT(*) FROM probes p "
                         " WHERE p.id = :probe_id AND " + visible_sql),
                    probe_params).scalar(), 0):
                raise ReflexValidationError("Unknown probe", 'probe_id',
                                            RefusalReason.PROBE_UNKNOWN)

        # The form always sends a severity and an anti repetition, so these are
        # the values of a payload that did not come from it.
        default_severity = 'high'
        default_cooldown = 60

        min_severity = str(rule.get('min_severity', default_severity)
                           or default_severity).strip().lower()
        if min_severity not in SEVERITIES:
            raise ReflexValidationError("Unknown severity: %s" % min_severity,
                                        'min_severity',
                                        RefusalReason.SEVERITY_UNKNOWN)

        cooldown = _to_int(rule.get('cooldown_minutes', default_cooldown),
                           default_cooldown)
        if cooldown < 0:
            raise ReflexValidationError("The cooldown must not be negative",
                                        'cooldown_minutes',
                                        RefusalReason.DURATION_NEGATIVE)

        escalation = rule.get('escalation_minutes')
        if escalation in (None, '', 0, '0'):
            escalation = None
        else:
            escalation = _to_int(escalation, 0)
            if escalation <= 0:
                raise ReflexValidationError(
                    "The escalation delay must be a positive number of minutes",
                    'escalation_minutes', RefusalReason.VALUE_NOT_POSITIVE)

        return {
            'channel_id': channel_id,
            'probe_id': probe_id,
            'min_severity': min_severity,
            'recipients': _clean_str(
                normalise_recipients(rule.get('recipients')),
                65535, 'recipients', required=True),
            'target_filter': _clean_str(rule.get('target_filter'), 255,
                                        'target_filter'),
            'cooldown_minutes': cooldown,
            'escalation_minutes': escalation,
            'enabled': _to_bool_int(rule.get('enabled', 1)),
            'created_by': _clean_str(rule.get('created_by') or login, 255,
                                     'created_by') or 'unknown',
        }

    @DatabaseHelper._sessionm
    def create_notification_rule(self, session, rule, login=''):
        """Create a notification rule."""
        try:
            values = self._validate_rule_payload(session, rule, login=login)
        except ReflexValidationError as e:
            logger.warning("Reflex: invalid rule payload: %s" % e)
            return refused_from(e)
        try:
            result = session.execute(text(
                "INSERT INTO notification_rules (channel_id, probe_id, "
                "  min_severity, recipients, target_filter, cooldown_minutes, "
                "  escalation_minutes, enabled, created_by, created_at) "
                "VALUES (:channel_id, :probe_id, :min_severity, :recipients, "
                "  :target_filter, :cooldown_minutes, :escalation_minutes, "
                "  :enabled, :created_by, NOW())"), values)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: rule creation failed: %s" % e)
            return refused(REFUSAL_FAILED, "The rule could not be created")
        rule_id = _to_int(result.lastrowid, 0)
        if not rule_id:
            return refused(REFUSAL_FAILED,
                           "The rule was written but its identifier could not "
                           "be read back")
        return rule_id

    @DatabaseHelper._sessionm
    def update_notification_rule(self, session, rule_id, rule, login=''):
        """Update a notification rule.

        Returns True, or the structure built by `refused`.
        """
        rule_id = _to_int(rule_id, 0)
        if rule_id <= 0:
            return refused(REFUSAL_INVALID, "No rule was named", 'rule_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        access = self._rule_access(session, login, rule_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, RULE_GONE)
        try:
            values = self._validate_rule_payload(session, rule, login=login)
        except ReflexValidationError as e:
            logger.warning("Reflex: invalid rule payload: %s" % e)
            return refused_from(e)
        values['rule_id'] = rule_id
        try:
            session.execute(text(
                "UPDATE notification_rules "
                "   SET channel_id = :channel_id, probe_id = :probe_id, "
                "       min_severity = :min_severity, recipients = :recipients, "
                "       target_filter = :target_filter, "
                "       cooldown_minutes = :cooldown_minutes, "
                "       escalation_minutes = :escalation_minutes, "
                "       enabled = :enabled "
                " WHERE id = :rule_id"), values)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: rule update failed: %s" % e)
            return refused(REFUSAL_FAILED, "The rule could not be updated")
        return True

    @DatabaseHelper._sessionm
    def delete_notification_rule(self, session, rule_id, login=''):
        """Delete a notification rule.

        Returns True, or the structure built by `refused`.
        """
        rule_id = _to_int(rule_id, 0)
        if rule_id <= 0:
            return refused(REFUSAL_INVALID, "No rule was named", 'rule_id',
                           reason=RefusalReason.FIELD_REQUIRED)
        access = self._rule_access(session, login, rule_id)
        if not _reachable(access):
            return refused(REFUSAL_MISSING, RULE_GONE)
        try:
            result = session.execute(
                text("DELETE FROM notification_rules WHERE id = :rule_id"),
                {'rule_id': rule_id})
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: rule deletion failed: %s" % e)
            return refused(REFUSAL_FAILED, "The rule could not be deleted")
        if _to_int(result.rowcount, 0) <= 0:
            return refused(REFUSAL_MISSING, RULE_GONE)
        return True

    # =========================================================================
    # Operations shared with the master substitute
    # =========================================================================
    @DatabaseHelper._sessionm
    def get_probe_config_for_machine(self, session, machines_id, group_ids=None,
                                     entity_ids=None):
        """Probes applicable to a machine, with their collection methods."""
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return []

        target_fragment, params = machine_target_clauses(
            machines_id, group_ids=group_ids, entity_ids=entity_ids)
        params['machine_os'] = self._machine_os(session, machines_id) or None

        # A probe placed widely leaves no row per machine, so an exception is
        # the only way to take it off one machine.
        probes = _rows(session.execute(text(
            "SELECT p.id AS probe_id, p.probe_key, p.label, p.metric_key, "
            "       p.unit, p.value_type, p.os_support, "
            # Whether this agent has anything to run for that probe.
            "       (" + probe_distributable_sql(':machine_os') + ") "
            "           AS agent_measurable, "
            "       MIN(pa.interval_seconds) AS interval_seconds "
            "  FROM probe_assignments pa "
            "  JOIN probes p ON p.id = pa.probe_id "
            # A probe turned off is distributed to nobody: that switch is the
            # only one, and it is actionable on the shipped probes too.
            " WHERE p.enabled = 1 "
            "   AND " + target_fragment +
            "   AND NOT EXISTS (SELECT 1 FROM probe_exclusions px "
            "                    WHERE px.probe_id = p.id "
            "                      AND px.machines_id = :machines_id) "
            " GROUP BY p.id, p.probe_key, p.label, p.metric_key, p.unit, "
            "          p.value_type, p.os_support "
            " ORDER BY p.probe_key ASC"), params))

        # Read after the coverage, never before, as on the removal path.
        try:
            resolved = self._resolve_alerts_off_coverage(
                session, machines_id,
                [_to_int(row.get('probe_id'), 0) for row in probes])
            # Committed even when it closed nothing: the statement takes its
            # locks whether it matches or not, and this runs for every machine
            # of the estate on every round of the sweep.
            session.commit()
            if resolved:
                logger.info("Reflex: %d alert(s) of machine %s resolved, "
                            "their probe no longer reaches it"
                            % (resolved, machines_id))
        except Exception as e:
            session.rollback()
            logger.error("Reflex: alerts of machine %s left open, their "
                         "resolution failed: %s" % (machines_id, e))

        # The coverage above has done its work on the alerts.
        kept, dropped = [], []
        for row in probes:
            measurable = _to_int(row.pop('agent_measurable', 0), 0)
            (kept if measurable else dropped).append(row)
        probes = kept
        if dropped:
            logger.debug(
                "Reflex: machine %s, %d probe(s) placed but not distributed, "
                "no collector for its system: %s"
                % (machines_id, len(dropped),
                   ", ".join(str(row.get('probe_key')) for row in dropped)))

        if not probes:
            return []

        # Collectors fetched for the whole set in one statement.
        fragment, collector_params = _placeholders(
            'probe', [_to_int(row.get('probe_id'), 0) for row in probes])
        collectors = _rows(session.execute(text(
            "SELECT probe_id, os, collector, params_json, requires, enabled "
            "  FROM probe_collectors "
            " WHERE enabled = 1 AND probe_id IN (" + fragment + ")"),
            collector_params))

        by_probe = {}
        for collector in collectors:
            by_probe.setdefault(_to_int(collector.get('probe_id'), 0), []) \
                    .append(collector)
        for probe in probes:
            probe['collectors'] = by_probe.get(_to_int(probe.get('probe_id'), 0),
                                               [])
        return probes

    @DatabaseHelper._sessionm
    def set_agent_config_sent(self, session, machines_id, hostname,
                              sent_version, probe_count=0):
        """Record the configuration version distributed to an agent."""
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return False
        try:
            params = {
                'machines_id': machines_id,
                'hostname': _clean_str(hostname, 255, 'hostname') or '',
                'sent_version': _clean_str(sent_version, 64, 'sent_version'),
                'probe_count': _to_int(probe_count, 0),
            }
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return False
        try:
            session.execute(text(
                "INSERT INTO probe_agent_config (machines_id, hostname, "
                "  sent_version, sent_at, probe_count) "
                "VALUES (:machines_id, :hostname, :sent_version, NOW(), "
                "  :probe_count) "
                "ON DUPLICATE KEY UPDATE hostname = VALUES(hostname), "
                "  sent_version = VALUES(sent_version), sent_at = NOW(), "
                "  probe_count = VALUES(probe_count)"), params)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: agent configuration update failed: %s" % e)
            return False
        return True

    @DatabaseHelper._sessionm
    def set_agent_config_acked(self, session, machines_id, acked_version,
                               last_error=None):
        """Record the configuration version an agent declares to apply."""
        machines_id = _to_int(machines_id, 0)
        if machines_id <= 0:
            return False
        try:
            params = {
                'machines_id': machines_id,
                'acked_version': _clean_str(acked_version, 64, 'acked_version'),
                'last_error': _clean_str(last_error, 512, 'last_error'),
            }
        except ReflexValidationError as e:
            logger.warning("Reflex: %s" % e)
            return False
        try:
            result = session.execute(text(
                "UPDATE probe_agent_config "
                "   SET acked_version = :acked_version, acked_at = NOW(), "
                "       last_error = :last_error "
                " WHERE machines_id = :machines_id"), params)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: agent acknowledgement failed: %s" % e)
            return False
        return _to_int(result.rowcount, 0) > 0

    @DatabaseHelper._sessionm
    def record_measures(self, session, measures):
        """Store measures reported by an agent."""
        if isinstance(measures, dict):
            measures = [measures]
        if not measures:
            return 0

        prepared = []
        for measure in measures:
            if not isinstance(measure, dict):
                continue
            try:
                machines_id = _to_int(measure.get('machines_id'), 0)
                probe_id = _to_int(measure.get('probe_id'), 0)
                if machines_id <= 0 or probe_id <= 0:
                    raise ReflexValidationError(
                        "A measure needs a machine and a probe")
                status = str(measure.get('status', 'ok') or 'ok').lower()
                if status not in ('ok', 'warning', 'error', 'unavailable'):
                    raise ReflexValidationError("Unknown measure status: %s"
                                                % status)
                collected_at = measure.get('collected_at')
                if isinstance(collected_at, datetime):
                    collected_at = collected_at.strftime("%Y-%m-%d %H:%M:%S")
                collected_at = _clean_str(collected_at, 19, 'collected_at')
                prepared.append({
                    'machines_id': machines_id,
                    'uuid_inventorymachine': _clean_str(
                        measure.get('uuid_inventorymachine'), 45,
                        'uuid_inventorymachine'),
                    'hostname': _clean_str(measure.get('hostname'), 255,
                                           'hostname') or '',
                    'probe_id': probe_id,
                    'metric_key': _clean_str(measure.get('metric_key'), 128,
                                             'metric_key', required=True),
                    'value_num': _to_float(measure.get('value_num')),
                    'value_text': _clean_str(measure.get('value_text'), 512,
                                             'value_text'),
                    'unit': _clean_str(measure.get('unit'), 32, 'unit'),
                    'status': status,
                    'detail': _measure_detail(measure.get('detail')),
                    'collected_at': collected_at,
                })
            except ReflexValidationError as e:
                logger.warning("Reflex: measure dropped: %s" % e)
        if not prepared:
            return 0

        try:
            # collected_at comes from the machine and is stored as reported;
            # received_at is the server clock and is the only timestamp any
            # freshness or retention question is allowed to read.
            session.execute(text(
                "INSERT INTO probe_measures (machines_id, "
                "  uuid_inventorymachine, hostname, probe_id, metric_key, "
                "  value_num, value_text, unit, status, detail, collected_at, "
                "  received_at) "
                "VALUES (:machines_id, :uuid_inventorymachine, :hostname, "
                "  :probe_id, :metric_key, :value_num, :value_text, :unit, "
                "  :status, :detail, COALESCE(:collected_at, NOW(3)), NOW(3))"),
                prepared)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: measures could not be stored: %s" % e)
            return 0
        return len(prepared)

    @DatabaseHelper._sessionm
    def add_notification_history(self, session, alert_id=None, channel_id=None,
                                 rule_id=None, recipients=None,
                                 status='pending', skip_reason=None,
                                 error_message=None, attempt_count=0,
                                 accepted_at=None, provider_message_id=None,
                                 is_escalation=0):
        """Trace a sending attempt."""
        status = str(status or 'pending').lower()
        if status not in ('pending', 'sent', 'failed', 'skipped'):
            logger.warning("Reflex: unknown notification status '%s'" % status)
            return 0
        # Every text is truncated and none is validated: see _truncate_str.
        params = {
            'alert_id': _to_int(alert_id, 0) or None,
            'channel_id': _to_int(channel_id, 0) or None,
            'rule_id': _to_int(rule_id, 0) or None,
            'recipients': _truncate_str(recipients, 65535),
            'status': status,
            'skip_reason': _truncate_str(skip_reason, 255),
            'error_message': _truncate_str(error_message, 512),
            'attempt_count': _to_int(attempt_count, 0),
            'accepted_at': accepted_at,
            'provider_message_id': _truncate_str(provider_message_id, 255),
            'is_escalation': _to_bool_int(is_escalation),
        }
        try:
            result = session.execute(text(
                "INSERT INTO notification_history (alert_id, channel_id, "
                "  rule_id, recipients, status, skip_reason, error_message, "
                "  attempt_count, accepted_at, provider_message_id, "
                "  is_escalation, created_at, sent_at) "
                "VALUES (:alert_id, :channel_id, :rule_id, :recipients, "
                "  :status, :skip_reason, :error_message, :attempt_count, "
                "  :accepted_at, :provider_message_id, :is_escalation, NOW(), "
                "  CASE WHEN :status = 'sent' THEN NOW() ELSE NULL END)"),
                params)
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error("Reflex: notification history write failed: %s" % e)
            return 0
        return _to_int(result.lastrowid, 0)

    def _purge_in_batches(self, session, sql, cutoff, label):
        """Run one delete statement in bounded batches, one commit each.

        Returns the number of rows removed and whether the cap was hit.
        """
        deleted = 0
        params = {'cutoff': cutoff, 'batch': PURGE_BATCH_SIZE}
        for _ in range(PURGE_MAX_BATCHES):
            removed = _to_int(session.execute(text(sql), params).rowcount, 0)
            # Committed batch by batch: an interruption keeps what has already
            # been removed instead of replaying it the next night.
            session.commit()
            deleted += removed
            if removed < PURGE_BATCH_SIZE:
                return deleted, False
        logger.warning(
            "Reflex: purge of %s stopped after %d batches of %d rows, older "
            "rows remain and will be taken by the next pass"
            % (label, PURGE_MAX_BATCHES, PURGE_BATCH_SIZE))
        return deleted, True

    @DatabaseHelper._sessionm
    def purge_old_data(self, session, measures_days=None,
                       alerts_resolved_days=None,
                       notification_history_days=None):
        """Apply the retention policy of the settings table."""
        if measures_days is None:
            measures_days = self.setting('retention.measures_days',
                                         session=session)
        if alerts_resolved_days is None:
            alerts_resolved_days = self.setting(
                'retention.alerts_resolved_days', session=session)
        if notification_history_days is None:
            notification_history_days = self.setting(
                'retention.notification_history_days', session=session)

        purged = {'measures': 0, 'alerts': 0, 'notification_history': 0,
                  'truncated': []}
        now = datetime.now()
        plan = (
            ('measures', _to_int(measures_days, 30),
             "DELETE FROM probe_measures WHERE received_at < :cutoff "
             " ORDER BY received_at ASC LIMIT :batch"),
            ('alerts', _to_int(alerts_resolved_days, 365),
             "DELETE FROM alerts WHERE status = 'resolved' "
             "   AND resolved_at IS NOT NULL AND resolved_at < :cutoff "
             " ORDER BY resolved_at ASC LIMIT :batch"),
            ('notification_history', _to_int(notification_history_days, 90),
             "DELETE FROM notification_history WHERE created_at < :cutoff "
             " ORDER BY created_at ASC LIMIT :batch"),
        )
        for label, days, sql in plan:
            # A horizon of zero disables the purge of that table, as it did
            # before: nothing is removed and no cutoff is computed.
            if days <= 0:
                continue
            try:
                removed, truncated = self._purge_in_batches(
                    session, sql, now - timedelta(days=days), label)
            except Exception as e:
                session.rollback()
                logger.error("Reflex: purge of %s failed: %s" % (label, e))
                continue
            purged[label] = removed
            if truncated:
                purged['truncated'].append(label)
        return purged
