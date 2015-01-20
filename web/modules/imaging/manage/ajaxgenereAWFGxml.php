<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
    require("../../../includes/config.inc.php");
    require("../../../includes/session.inc.php");
    require("../../../includes/PageGenerator.php");
    require("../includes/includes.php");
    require("../includes/xmlrpc.inc.php");
    require("../includes/logs.inc.php");
  ?>
<?php
        $dom = new DomDocument;
        $dom->preserveWhiteSpace = FALSE;
        $dom->loadXML($_POST['data']);
        $dom->formatOutput = true;
        $t=$dom->saveXML();
        if( ! xmlrpc_Windows_Answer_File_Generator($t,$_POST['titre'])){
            echo "0";
        }
        else{
            echo "1";
        }
?>