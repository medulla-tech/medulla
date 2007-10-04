<?php
/*
 * Linbox Rescue Server - Secure Remote Control Module
 * Copyright (C) 2005  Linbox FAS
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, US
 */

/*
 * Get variable are :
 *
 * - edit = file to edit (this doesn't content the path)
 * - pwd = explorer current directory
 * - repository = repository current directory
 * - mac = distant host mac address
 * - content = if file edit formular is submited, this variable content file new data
 */
if ($_POST["return_submit"] != "") {
  if ($_GET["current_tab"] == "explorer") { // no longuer exists
    printf(
      "<html><head><meta http-equiv=\"refresh\" content=\"0;url=".
        urlStr("msc/msc/explorer", array(
              'mac'=>$_GET["mac"],
              'group'=>$_GET["profile"],
              'profile'=>$_GET["group"]
            )
        ).
        "\"></head></html>");
  } elseif ($_GET["current_tab"] == "repository") {
    printf(
      "<html><head><meta http-equiv=\"refresh\" content=\"0;url=".
        urlStr("msc/msc/repository", array(
              'mac'=>$_GET["mac"],
              'group'=>$_GET["profile"],
              'profile'=>$_GET["group"]
            )
        ).
        "\"></head></html>");

  }
  exit();
}

require("localSidebar.php");
require("graph/navbar.inc.php");

$p = new PageGenerator(_T("Edit"));
$p->setSideMenu($sidemenu);
$p->display();

require_once("modules/msc/includes/common.inc.php");
require_once("modules/msc/includes/config.inc.php");
require_once("modules/msc/includes/tmpl.inc.php"); /**< Use MSC_Tmpl class */
require_once("modules/msc/includes/debug.inc.php"); /**< Use Debug function */
require_once("modules/msc/includes/ssh.inc.php"); /**< Use MSC_Session class */
require_once("modules/msc/includes/widget.inc.php"); /**< Use MSC_Widget_... functions */
require_once("modules/msc/includes/mimetypes.inc.php"); /**< Use MSC_load_mime_types function */
require_once("modules/msc/includes/file.inc.php"); /**< Use MSC_Distant_File class */
require_once("modules/msc/includes/clean_path.inc.php"); /**< Use clean_path function */

$OUTPUT_TYPE = "WEB";
//$DEBUG = 0;

/*
 * Initialise webmin
 */

if ($_GET["current_tab"] == "explorer") {
  /*
   * Open the session
   */
  include("modules/msc/includes/open_session.inc.php"); // set $session instance
}
/*
 * Open the file
 */
if ($_GET["current_tab"] == "explorer") {
  $file_to_edit = new MSC_Distant_File($session, $_COOKIE["pwd"] . "/" . $_GET["edit"]);
} elseif ($_GET["current_tab"] == "repository") {
  $file_to_edit = new MSC_File(realpath($repository_home_directory . "/" . $_COOKIE["repository_pwd"] . "/" . $_GET["edit"]));
}

/*
 * handle user action
 */
if ($_POST["edit_save_submit"] != "")
{
  /*
   * Write data to file
   */

  if ($file_to_edit->write_content(stripslashes($_POST["content"]))) {
    // No error
    $success_message = "Le fichier a 退t退 modifi退 avec succ耀s";
  } else {
    // Error
    $error_message = "Erreur lors de l'退criture des donn退es dans le fichier";
  }
} else {
  /*
   * Read data from file
   */

  if ($file_to_edit->get_content()) {
    // No error

  } else {
    // Error
    $error_message = "Erreur de lecture du fichier";
  }
}



/*
 * Initialise template engine
 */
$template = new MSC_Tmpl(array("edit_page" => "edit_page.tpl" ));

$template->header_param = array("msc repository", $text{'editor_title'});

/*
 * Send user interface message to template
 */
if (( $success_message != "" ) || ( $error_message != "" )) {
  if ($success_message != "") {
    MSC_Widget_action_message($template, $success_message, false); // false = error disable
  } else {
    MSC_Widget_action_message($template, $error_message, true); // true = error enable
  }
} else {
  $template->set_var("action_message", "");
}

$script = urlStr("msc/msc/edit", array(
                 'mac'=>$_GET["mac"],
                 'group'=>$_GET["profile"],
                 'profile'=>$_GET["group"],
                ));
$template->set_var("SCRIPT_NAME", $script);

$template->set_var("MAC", urlencode($_GET["mac"]));
$template->set_var("PROFILE", urlencode($_GET["profile"]));
$template->set_var("GROUP", urlencode($_GET["group"]));
$template->set_var("EDIT_FILE", urlencode($_GET["edit"]));
$template->set_var("CURRENT_TAB", $_GET["current_tab"]);


if ($_GET["current_tab"] == "explorer") {
  $template->set_var("COMPLETE_PATH_FILE_TO_EDIT", clean_path($_COOKIE["pwd"] . "/" . $_GET["edit"]));
} elseif ($_GET["current_tab"] == "repository") {
  $template->set_var("COMPLETE_PATH_FILE_TO_EDIT", clean_path($_COOKIE["repository_pwd"] . "/" . $_GET["edit"]));
}

$template->set_var("CONTENT_DATA", $file_to_edit->content);


/*
 * Display
 */
$template->pparse("out", "edit_page", "edit_page");
?>

