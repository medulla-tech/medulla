<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: infoPackage.inc.php 8 2006-11-13 11:08:22Z cedric $
 *
 * This file is part of MMC.
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

require_once("modules/msc/includes/common.inc.php");
require_once("modules/msc/includes/config.inc.php");
require_once("modules/msc/includes/tmpl.inc.php"); /**< Use MSC_Tmpl class */
require_once("modules/msc/includes/debug.inc.php"); /**< Use Debug function */
require_once("modules/msc/includes/ssh.inc.php"); /**< Use MSC_Session class */
require_once("modules/msc/includes/widget.inc.php"); /**< Use MSC_Widget_... functions */
require_once("modules/msc/includes/mimetypes.inc.php"); /**< Use MSC_load_mime_types function */
require_once("modules/msc/includes/tree.inc.php"); /**< Use MSC_Distant_Tree class */
require_once("modules/msc/includes/scheduler.php"); /**< Use MSC_Scheduler class */
require_once("modules/msc/includes/file.inc.php"); /**< Use MSC_File class */
require_once("modules/msc/includes/directory.inc.php"); /**< Use MSC_Directory class */

ob_end_clean();

/*
 * Define the current directory
 */
if ($_GET["repository_pwd"] == "") {
    if ( $_COOKIE["repository_pwd"] != "" ) {
        $current_repository_directory = $_COOKIE["repository_pwd"];
    } else {
        $current_repository_directory = "";
    }
} else {
    $current_repository_directory = $_GET["repository_pwd"];
    $current_repository_directory = clean_path($current_repository_directory);
    setcookie("repository_pwd", $current_repository_directory);
}

/**
 * Load mimetypes
 */
$mime_type_icons_data = array();
$mime_types_data = array();

MSC_load_mime_types(EXTICONSFILE, $mime_type_icons_data, $mime_types_data);

/*
 * handle user action
 */
if ($_GET["download"] != "") {
    /*
     * action = Download one file
     */
    debug(1, sprintf("User action - download this file : %s", clean_path($current_directory . "/" . $_GET["download"])));

    $file = new MSC_File(realpath($repository_home_directory . "/" . $current_repository_directory . "/" . $_GET["download"]));

    $file->download($mime_types_data);
}

?>
