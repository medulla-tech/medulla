# -*- coding: utf-8; -*-
# SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
# SPDX-License-Identifier: GPL-3.0-or-later
"""
Test message of a notification channel.

Copy of the skeleton of pulse_xmpp_master_substitute/lib/plugins/reflex,
which ships in another package: a change of presentation there is to be
carried over here.
"""

import gettext

from datetime import datetime
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate, make_msgid
from html import escape as html_escape

GETTEXT_DOMAIN = "reflex"

# Where the web module of the console compiles its catalogues.
DEFAULT_LOCALE_DIR = "/usr/share/mmc/modules/reflex/locale"

# Colours of the console, as in the substitute: .reflex-badge-info.
TEST_BADGE_COLORS = ("#3b82f6", "#ffffff")

MAIL_FOOTER = ("Automatic message from Medulla Reflex. Do not reply: "
               "notification channels and rules are set in the Medulla "
               "console.")

MAIL_FACT = (
    '<tr>'
    '<td width="140" valign="top" style="width:140px; padding:10px 10px 0 0;'
    ' font-family:Arial,Helvetica,sans-serif; font-size:13px; line-height:18px;'
    ' color:#64748b;">{label}</td>'
    '<td valign="top" style="padding:10px 0 0 0;'
    ' font-family:Arial,Helvetica,sans-serif; font-size:14px; line-height:19px;'
    ' font-weight:bold; color:#1e293b;">{value}</td>'
    '</tr>\n')

MAIL_SUBTITLE = (
    '<tr><td style="padding:0 20px 16px 20px;'
    ' font-family:Arial,Helvetica,sans-serif; font-size:14px; line-height:20px;'
    ' color:#64748b;">{text}</td></tr>\n')

MAIL_MESSAGE = (
    '<tr><td style="padding:0 20px 18px 20px;">\n'
    '<table role="presentation" border="0" cellpadding="0" cellspacing="0"'
    ' width="100%" style="border-collapse:collapse;">\n'
    '<tr>\n'
    '<td width="4" bgcolor="{badge_bg}" style="width:4px;'
    ' background-color:{badge_bg}; font-size:0; line-height:0;">&nbsp;</td>\n'
    '<td bgcolor="#f1f5f9" style="padding:12px 14px; background-color:#f1f5f9;'
    ' font-family:Arial,Helvetica,sans-serif; font-size:15px; line-height:22px;'
    ' color:#1e293b;">{text}</td>\n'
    '</tr>\n</table>\n</td></tr>\n')

MAIL_FACTS = (
    '<tr><td style="padding:4px 20px 18px 20px;">\n'
    '<table role="presentation" border="0" cellpadding="0" cellspacing="0"'
    ' width="100%" style="border-collapse:collapse;'
    ' border-top:1px solid #e2e8f0;">\n'
    '{rows}'
    '</table>\n</td></tr>\n')

MAIL_HTML = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
<meta name="viewport" content="width=device-width, initial-scale=1" />
<title>{title}</title>
</head>
<body style="margin:0; padding:0; background-color:#f8fafc;">
<div style="display:none; font-size:1px; color:#f8fafc; line-height:1px; max-height:0; max-width:0; opacity:0; overflow:hidden;">{preheader}</div>
<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse; background-color:#f8fafc;">
<tr>
<td align="center" style="padding:16px 10px;">
<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="600" style="width:100%; max-width:600px; border-collapse:collapse; background-color:#ffffff; border:1px solid #e2e8f0;">
<tr>
<td bgcolor="#25607d" style="padding:14px 20px; background-color:#25607d; font-family:Arial,Helvetica,sans-serif; font-size:15px; font-weight:bold; color:#ffffff;">Medulla Reflex</td>
</tr>
<tr><td style="padding:20px 20px 2px 20px;">
<table role="presentation" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse:collapse;">
<tr>
<td align="left" style="font-family:Arial,Helvetica,sans-serif; font-size:21px; line-height:27px; font-weight:bold; color:#1e293b;">{heading}</td>
<td align="right" valign="middle">
<table role="presentation" border="0" cellpadding="0" cellspacing="0" align="right" style="border-collapse:collapse;">
<tr><td bgcolor="{badge_bg}" style="padding:4px 10px; background-color:{badge_bg}; border-radius:3px; font-family:Arial,Helvetica,sans-serif; font-size:11px; font-weight:bold; color:{badge_fg}; white-space:nowrap;">{badge}</td></tr>
</table>
</td>
</tr>
</table>
</td></tr>
{subtitle}{message}{facts}<tr>
<td bgcolor="#1f2937" style="padding:12px 20px; background-color:#1f2937; font-family:Arial,Helvetica,sans-serif; font-size:12px; line-height:18px; color:#94a3b8;">
{footer}
</td>
</tr>
</table>
</td>
</tr>
</table>
</body>
</html>
"""


def date_display(moment, language):
    """Day first outside English, as the alert mails write it."""
    code = str(language or "").strip().lower()
    english = not code or code == "c" or code.startswith("en")
    return moment.strftime("%Y-%m-%d %H:%M" if english else "%d/%m/%Y %H:%M")


def _html(value):
    return html_escape(str(value if value is not None else ""), quote=True)


def translate(value, language):
    """One string in the given language, the English itself when none holds
    it.
    """
    value = str(value or "")
    code = str(language or "").strip()
    # gettext("") answers the header of the catalogue, not an empty string.
    if not value or not code:
        return value
    try:
        book = gettext.translation(GETTEXT_DOMAIN, DEFAULT_LOCALE_DIR,
                                   languages=[code], fallback=True)
        return book.gettext(value)
    except Exception:
        return value


def test_mail_parts(channel_name, host, language=None):
    """Subject, text half and HTML half of the test message of a channel."""
    def _(value):
        return translate(value, language)

    channel_name = str(channel_name or "").strip()
    host = str(host or "").strip()
    sent_at = date_display(datetime.now(), language)
    intro = _("Test message of this notification channel.")
    proof = _("Receiving this message proves that this channel delivers its "
              "notifications to its mail server.")
    footer = _(MAIL_FOOTER)

    subject = "Medulla Reflex - %s" % _("Test message")

    text = ("%s\n\n"
            "%s: %s\n"
            "%s: %s\n"
            "%s: %s\n\n"
            "%s\n\n"
            "-- \n%s\n"
            % (intro,
               _("Channel"), channel_name,
               _("Mail server"), host,
               _("Sent at"), sent_at,
               proof,
               footer))

    badge_bg, badge_fg = TEST_BADGE_COLORS
    rows = [MAIL_FACT.format(label=_html(_("Mail server")), value=_html(host)),
            MAIL_FACT.format(label=_html(_("Sent at")), value=_html(sent_at))]
    html = MAIL_HTML.format(
        title=_html(subject),
        preheader=_html(proof),
        heading=_html(channel_name) or "&#8212;",
        badge=_html(_("Test").upper()),
        badge_bg=badge_bg,
        badge_fg=badge_fg,
        subtitle=MAIL_SUBTITLE.format(text=_html(intro)),
        message=MAIL_MESSAGE.format(text=_html(proof), badge_bg=badge_bg),
        facts=MAIL_FACTS.format(rows="".join(rows)),
        footer=_html(footer))
    return subject, text, html


def build_test_message(channel_name, settings, recipient, language=None):
    """The test message, ready to hand to smtplib, and its Message-ID."""
    subject, text, html = test_mail_parts(
        channel_name, settings.get('host'), language)
    message = MIMEMultipart('alternative')
    message.attach(MIMEText(text, 'plain', 'utf-8'))
    message.attach(MIMEText(html, 'html', 'utf-8'))
    message['Subject'] = Header(subject, 'utf-8')
    message['From'] = formataddr((str(Header(settings.get('from_name') or '',
                                             'utf-8')),
                                  settings.get('from_address')))
    message['To'] = recipient
    message['Date'] = formatdate(localtime=True)
    message_id = make_msgid()
    message['Message-ID'] = message_id
    return message, message_id
