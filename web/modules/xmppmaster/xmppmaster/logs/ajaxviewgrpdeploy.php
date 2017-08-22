<?php
/**
 * (c) 2017 Siveo, http://http://www.siveo.net
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
 *
 * file ajaxviewgrpdeploy.php
 */

require_once("../../../base/includes/computers.inc.php");
require_once("../../../../includes/config.inc.php");
require_once("../../../../includes/i18n.inc.php");
require_once("../../../../includes/acl.inc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/PageGenerator.php");

require_once("../../includes/xmlrpc.php");

$info = xmlrpc_getdeployfromcommandid($_GET['cmd'], "UUID_NONE");

foreach ($info['objectdeploy'] as $val)
{
   $id  .= $val['inventoryuuid']."@@";
   $sta .=  $val['state']."@@";
}

if($id != $_GET['id']) {
    echo "1";
    exit;
}
else{
    if($sta!= $_GET['sta']) {
        echo "1";
        exit;
    }
}
echo "0";
?>
