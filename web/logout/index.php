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
 *
 */
//to have the same path as all other scripts...
chdir ('../');

require("includes/config.inc.php");
require("includes/session.inc.php");
require("includes/acl.inc.php");
require("includes/i18n.inc.php");
require("includes/PageGenerator.php");
require("modules/base/includes/edit.inc.php");

$root = $conf["global"]["root"];

if (isset($_POST["delog"])) {
    // redirect to the treatment of OIDC disconnection
    if (isset($_SESSION['selectedProvider'])) {
        header("Location: " . $root . "providers.php?signout=1");
        exit;
    }

    $_SESSION = array();
    if (isset($_COOKIE[session_name()])) {
        setcookie(session_name(), '', time()-42000, '/');
    }
    session_destroy();
    header("Location: " . $root . "index.php");
    exit;
}

?>
<h2><?php echo  _("Logout") ?></h2>
<hr style="color: #ccc;background-color: #ccc;height: 1px;border: 0 none;" />

<p><?php echo  _("Your session will be closed") ?></p>
<br>

<form method="post" action="logout/index.php">
<input type="submit" name="delog" class="btnPrimary btn-no-marge" value="<?php echo  _("Logout") ?>" />
</form>
