<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: infoPackage.inc.php 8 2006-11-13 11:08:22Z cedric $
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

require("localSidebar.php");
require("graph/navbar.inc.php");
require("modules/msc/includes/mimetypes.inc.php ");

$p = new PageGenerator(_T("Explorer"));
$p->setSideMenu($sidemenu);
$p->display(); 


/*
 * Define the current directory
 */
if ($_GET["pwd"] == "") {
        if ( $_COOKIE["pwd"] != "" ) {
                $current_directory = $_COOKIE["pwd"];
        } else {
                $current_directory = "/";
        }
} else {
        $current_directory = $_GET["pwd"];
        $current_directory = clean_path($current_directory);
        setcookie("pwd", $current_directory);
}

/*
 * Handle user action
 */
if ( $_GET["go_to_directory"] != "" ) {
        $current_directory .= "/" .$_GET["go_to_directory"];
        $current_directory = clean_path($current_directory);
        setcookie("pwd", $current_directory);
}


/*
 * Initialise some variable                                                                   
 */
$success_message = "";
$error_message = "";

/**                                                                                           
 * Load mimetypes
 */
$exticonsfile = EXTICONSFILE;

$mime_type_icons_data = array();
$mime_types_data = array();

MSC_load_mime_types($exticonsfile, $mime_type_icons_data, $mime_types_data);
        
/*              
 * explorer active ?
 */             
if ($config['explorer'] == 0) {
        $template = new MSC_Tmpl(array("dis" => "dis.tpl" ));
        $template->header_param = array("msc explorer", $text{'explorer_title'});
        $template->pparse("out", "dis", "dis");
        exit;
}

/*
 * Open the session
 */

include("modules/msc/includes/open_session.inc.php"); // set $session instance




?>

