<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
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
 * file: token.php
 */
$lang = (string)($_GET['lang'] ?? 'en_US');
if (isset($_GET['lang'])) {
    $_SESSION['lang'] = $lang;
}

/* The different statuses:
   - sent     : email sent (or unknown account → neutral message)
   - invalid  : Invalid/expired link
   - mailfail : Mail sending failure
*/
$status = isset($_GET['status']) ? (string)$_GET['status'] : 'sent';
$view = in_array($status, ['sent','invalid','mailfail'], true) ? $status : 'sent';
?>
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title><?= _("Medulla / Sign-in link"); ?></title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="icon" href="img/common/favicon.ico" />
  <style>
    html,body{height:100%;margin:0;background:#ffffff;font-family:Arial,Helvetica,sans-serif;color:#111827}
    .stage{min-height:100vh;display:grid;place-items:center;padding:24px}
    .panel{transform:translateY(-8vh)}
    .logo{display:block;margin:0 auto 16px auto;height:52px}
    .card{
      width:min(520px,92vw);
      background:#ffffff;border:1px solid #e5e7eb;border-radius:14px;overflow:hidden;
      box-shadow:0 6px 22px rgba(0,0,0,.06), 0 1px 3px rgba(0,0,0,.04);
    }
    .card-h{padding:14px 18px 6px;text-align:center}
    .card-h h1{margin:0;font-size:18px;font-weight:700;color:#005776;letter-spacing:.2px}
    .alert-success{
      margin:14px 18px;padding:14px 16px;border:1px solid #d6e9c6;border-radius:10px;
      background:#dff0d8;color:#468847;line-height:1.6
    }
    .alert-error{
      margin:14px 18px;padding:14px 16px;border:1px solid #f5c2c7;border-radius:10px;
      background:#f8d7da;color:#842029;line-height:1.6
    }
    .note{margin:0 18px 18px;color:#6b7280;font-size:12px}
    .btn{
      display:inline-block;margin:4px 18px 18px;padding:10px 16px;
      text-decoration:none;border-radius:8px;border:1px solid #e5e7eb;color:#005776
    }
    .btn:hover{background:#f8fafc}
  </style>
</head>
<body>
  <div class="stage">
    <div class="panel">
      <img class="logo" src="img/login/medulla.svg" alt="<?= _("Medulla"); ?>">
      <div class="card">

        <?php if ($view === 'sent'): ?>
          <div class="card-h"><h1><?= _("Check your email"); ?></h1></div>
          <div class="alert-success">
            <?= _("If your account was found, we sent a sign-in link and you will receive it shortly."); ?>
            <?= _("The link will expire in"); ?> <strong>5&nbsp;<?= _("minutes"); ?></strong>.
          </div>
          <p class="note">
            <?= _("Remember to check your <em>junk</em> / <em>spam</em> folders."); ?>
          </p>

        <?php elseif ($view === 'invalid'): ?>
          <div class="card-h"><h1><?= _("Link problem"); ?></h1></div>
          <div class="alert-error">
            <?= _("This sign-in link is invalid or has expired."); ?>
            <?= _("Please return to the sign-in page and request a new link."); ?>
          </div>

        <?php else: /* mailfail */ ?>
          <div class="card-h"><h1><?= _("Email not sent"); ?></h1></div>
          <div class="alert-error">
            <?= _("We couldn't send the email. Please try again later or contact your administrator."); ?>
          </div>
        <?php endif; ?>

        <a class="btn" href="index.php?<?= htmlspecialchars('lang='.$lang, ENT_QUOTES, 'UTF-8') ?>">← <?= _("Back to sign-in"); ?></a>
      </div>
    </div>
  </div>
</body>
</html>