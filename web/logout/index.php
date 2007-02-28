<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php
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
    $_SESSION = array();
    if (isset($_COOKIE[session_name()])) {
        setcookie(session_name(), '', time()-42000, '/');
    }
    session_destroy();
    header("Location: " . $root . "index.php");
    exit;
}

?>
<h2><?= _("Logout") ?></h2>

<p><?= _("Your session will be closed") ?></p>

<form method="post" action="logout/index.php">
<input type="submit" name="delog" class="btnPrimary" value="<?= _("logout") ?>" />
</form>