<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
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

<p><?php echo  _("Your session will be closed") ?></p>

<form method="post" action="logout/index.php">
<input type="submit" name="delog" class="btnPrimary" value="<?php echo  _("Logout") ?>" />
</form>
