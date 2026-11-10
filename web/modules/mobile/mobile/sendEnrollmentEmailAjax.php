<?php
require_once("modules/mobile/includes/xmlrpc.php");

header('Content-Type: application/json');

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    echo json_encode(['ok' => false, 'error' => 'Invalid request']);
    exit;
}

$email = trim($_POST['email'] ?? '');
$name  = trim($_POST['name'] ?? '');

if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
    echo json_encode(['ok' => false, 'error' => 'Invalid email address']);
    exit;
}

$qr_url = xmlrpc_get_hmdm_config_qr_url();
if (!$qr_url) {
    echo json_encode(['ok' => false, 'error' => 'Could not retrieve QR code']);
    exit;
}

$logo_url  = 'https://medulla-tech.io/wp-content/uploads/2022/11/medulla-logo-head.svg';
$safe_name = htmlspecialchars($name, ENT_QUOTES, 'UTF-8');
$safe_qr   = htmlspecialchars($qr_url, ENT_QUOTES, 'UTF-8');
$subject   = 'Your device enrollment QR code';

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
            <td height="64" valign="middle" style="height:64px;padding:0 24px;">
              <span style="color:#ffffff;font-size:18px;font-weight:bold;line-height:1;">Mobile Device Enrollment</span>
            </td>
            <td height="64" valign="middle" align="right" style="height:64px;padding:0 24px;">
              <img src="{$logo_url}" alt="Medulla" style="display:block;height:auto;max-height:36px;margin:0;border:0;">
            </td>
          </tr>
        </table>
      </td>
    </tr>
    <tr>
      <td style="padding:32px 24px;">
        <p style="margin:0 0 16px;font-size:15px;color:#374151;">Hello,</p>
        <p style="margin:0 0 24px;font-size:15px;color:#374151;">
          Your device <strong>{$safe_name}</strong> has been registered for enrollment.<br>
          Scan the QR code below with your Android device to complete the setup.
        </p>
        <div style="text-align:center;margin:24px 0;">
          <img src="{$safe_qr}" alt="Enrollment QR Code" style="width:250px;height:250px;display:inline-block;border:0;">
        </div>
        <p style="margin:24px 0 0;font-size:13px;color:#6b7280;">
          If you did not expect this message, please ignore it.
        </p>
      </td>
    </tr>
    <tr>
      <td style="background:#f9fafb;padding:16px 24px;text-align:center;font-size:12px;color:#9ca3af;">
        medulla-tech.io
      </td>
    </tr>
  </table>
  </td></tr>
</table>
</body>
</html>
HTML;

$headers = "From: Medulla <no-reply@medulla-tech.io>\r\n" .
           "MIME-Version: 1.0\r\n" .
           "Content-Type: text/html; charset=UTF-8\r\n";

$ok = mail($email, $subject, $html, $headers, '-f no-reply@medulla-tech.io');

echo json_encode(['ok' => $ok, 'error' => $ok ? null : 'mail() returned false']);
exit;
?>
