<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: magiclink.inc.php
 */
require_once("/usr/share/mmc/includes/xmlrpc.inc.php");
require_once("includes/config.inc.php");

$login = trim((string)($_POST['username'] ?? ''));
$lang  = (string)($_POST['lang'] ?? $_SESSION['lang'] ?? 'en_US');

// Check that the account exists
$ret = xmlCall("base.checkExists", $login);

if ($ret) {
    if (!filter_var($login, FILTER_VALIDATE_EMAIL)) {
        $q = http_build_query(['status' => 'mailfail', 'lang' => $lang]);
        header("Location: token.php?{$q}");
        exit;
    }

    $lang       = (string)($_POST['lang'] ?? $_SESSION['lang'] ?? 'en_US');
    $token      = get_token($login);
    $scheme     = $_SESSION['XMLRPC_agent']['scheme'];
    $hostname   = $_SESSION['XMLRPC_server_description'];

    $baseUrl    = $scheme . '://' . $hostname . '/mmc/';
    $query      = http_build_query(['token' => $token, 'lang' => $lang]);
    $url        = $baseUrl . '?' . $query;

    $to         = $login;
    $logoUrl    = 'https://medulla-tech.io/wp-content/uploads/2022/11/medulla-logo-head.svg';

    $subject    = _("Your Medulla sign-in");
    $heading    = _("Secure sign-in");
    $hello      = _("Hello,");
    $pInline    = _("Click the button below to sign in. This link expires in") . " <strong>5&nbsp;"._("minutes")."</strong>.";
    $cta        = _("Open magic link");
    $altLink    = _("If the button doesn’t work, copy and paste this link:");
    $ignore     = _("If you didn’t request this, please ignore this message.");
    $brandFoot  = "medulla-tech.io";

    $html = <<<HTML
    <!doctype html>
    <html lang="en">
    <body style="margin:0;padding:0;background:#ffffff;font-family:Arial,Helvetica,sans-serif;">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0" style="padding:24px 0;background:#ffffff;">
        <tr><td align="center">
        <table role="presentation" width="560" cellpadding="0" cellspacing="0" style="background:#ffffff;border:1px solid #e5e7eb;border-radius:12px;overflow:hidden;">
            <tr>
            <td style="background:#25607D;">
                <table role="presentation" width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td height="64" valign="middle" style="height:64px;padding:0 24px;white-space:nowrap;">
                    <span style="color:#ffffff;font-size:18px;font-weight:bold;line-height:1;display:inline-block;">{$heading}</span>
                    </td>
                    <td height="64" valign="middle" align="right" style="height:64px;padding:0 24px;">
                    <img src="{$logoUrl}" alt="Medulla" style="display:block;height:auto;max-height:36px;margin:0;border:0;outline:none;">
                    </td>
                </tr>
                </table>
            </td>
            </tr>

            <tr>
            <td style="padding:20px 24px;color:#111827;font-size:14px;line-height:1.6;">
                {$hello}
                <p style="margin:12px 0 0;">{$pInline}</p>
            </td>
            </tr>

            <tr>
            <td align="center" style="padding:6px 24px 20px;">
                <a href="{$url}" style="display:inline-block;text-decoration:none;padding:12px 22px;border-radius:8px;background:#25607D;color:#ffffff;font-weight:600;">{$cta}</a>
            </td>
            </tr>

            <tr>
            <td style="padding:0 24px 20px;color:#6b7280;font-size:12px;line-height:1.6;border-top:3px solid #8CB63C;">
                {$altLink}<br>
                <span style="word-break:break-all;color:#17A4CC;">{$url}</span>
            </td>
            </tr>

            <tr>
            <td style="padding:0 24px 20px;color:#6b7280;font-size:12px;">{$ignore}</td>
            </tr>
        </table>
        <div style="color:#9ca3af;font-size:12px;padding:12px;">© {$brandFoot}</div>
        </td></tr>
    </table>
    </body>
    </html>
    HTML;

    $headers =
        "From: Medulla <noreply@medulla-tech.io>\r\n" .
        "MIME-Version: 1.0\r\n" .
        "Content-Type: text/html; charset=UTF-8\r\n";

    $ok     = mail($to, $subject, $html, $headers, '-f noreply@medulla-tech.io');
    $status = $ok ? 'sent' : 'mailfail';

} else {
    // Account not found
    $status = 'sent';
}

$query = http_build_query(['status' => $status, 'lang' => $lang]);
session_unset();
session_destroy();
header('Location: token.php?' . $query);
exit;