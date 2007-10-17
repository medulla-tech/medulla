<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

require("localSidebar.php");
require("graph/navbar.inc.php");

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
require_once("modules/msc/includes/scheduler.php"); /**< Use MSC_Directory class */
//require_once("modules/msc/includes/extract_all_files_of_directory.inc.php");

$p = new PageGenerator(_T("Repository"));
$p->setSideMenu($sidemenu);
$p->display(); 

if ($_GET["download"] != "") {
    /*
     * If action is download a file, I must disable DEBUG because I mustn't write something before call header
     */
    $DEBUG = 0;
}

/*
 * Set pwd cookie
 */

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
/*OLIVIERif (array_key_exists("repository", $config)) {
    $repository_home_directory = $config["repository"];
    }*/

if ($_GET["delete_file"] != "") {
    /*
     * action = Delete one file
     */
    $full_path_file_to_delete = realpath($repository_home_directory . "/" . $current_repository_directory . "/" . $_GET["delete_file"]);                                                                                                                                                                        
    debug(1, sprintf("User action - delete this file : %s", $full_path_file_to_delete));

    $file = new MSC_File($full_path_file_to_delete);

    if ($file->remove()) {
        // No error
        $success_message = "File deleted with success";
    } else {
        // Error !
        $error_message = "Error when I delete file";
    } 
} 

if ($_GET["delete_directory"] != "") {
    /*
     * action = Delete one directory
     */
    $full_path_directory_to_delete = clean_path($repository_home_directory . "/" . $current_repository_directory . "/" . $_GET["delete_directory"]);

    debug(1, sprintf("User action - delete this file : %s", $full_path_directory_to_delete));

    $directory = new MSC_Directory($full_path_directory_to_delete);

    if ($directory->delete_directory()) {
        // No error
        $success_message = "Directory deleted with success";
    } else {
        // Error !
        $error_message = "Directory when I delete file";
    }
}

if ( ( $_POST["file_upload_submit"] != "" ) && ( $_GET["process"] == 1 ) ) {
    /*
     * Upload a file
     */
    $full_path_file_to_upload = clean_path($repository_home_directory . "/" . $current_repository_directory . "/" . basename($_FILES["file_to_upload"]["name"]));
    $file = new MSC_File($full_path_file_to_upload);
    if ($file->upload($_FILES["file_to_upload"]["tmp_name"])) {
        // No error
        $success_message = "File : " . $full_path_file_to_create . " uploaded with success";
    } else {
        // Error
        $error_message = "Error cannot upload the file : " . $full_path_file_to_create;
    }
}

if (($_POST["create_file_submit"]!="") && ($_POST["type_file_to_create"] == "file")) {
    /*
     * Create a new file
     */
    $full_path_file_to_create = clean_path($repository_home_directory . "/" . $current_repository_directory . "/" . $_POST["filename_to_create"]);
    $file = new MSC_File($full_path_file_to_create);
    if ($file->create()) {
        // No error
        $success_message = "File : " . $full_path_file_to_create . " created with success";
    } else {
        // Error
        $error_message = "Error cannot create the file : " . $full_path_file_to_create;
    }
}

if (( $_POST["create_file_submit"] != "" ) && ( $_POST["type_file_to_create"] == "directory" )) {
    /*
     * Create a new directory
     */
    $full_path_directory_to_create = clean_path($repository_home_directory . "/" . $current_repository_directory . "/" . $_POST["filename_to_create"]);

    $directory = new MSC_Directory($full_path_directory_to_create);
    if ($directory->make_directory()) {
        // No error
        $success_message = "Directory : " . $full_path_directory_to_create . " created with success";
    } else {
        // Error
        $error_message = "Error cannot create the directory : " . $full_path_directory_to_create;
    }
}


/**
 * Load mimetypes
 */
$exticonsfile = EXTICONSFILE;

$mime_type_icons_data = array();
$mime_types_data = array();

MSC_load_mime_types($exticonsfile, $mime_type_icons_data, $mime_types_data);

include("modules/msc/includes/open_session.inc.php"); // set $session instance

/*
 * Display debug informations
 */
debug(2, sprintf("MAC Address : %s", $_GET['mac']));
debug(2, sprintf("profile : %s", $_GET['profile']));
debug(2, sprintf("group : %s", $_GET['group']));
debug(2, sprintf("IP Address : %s", $session->ip));
debug(2, sprintf("repository_launch_action : %s", $_POST['repository_launch_action']));
debug(2, sprintf("repository_path_destination : %s", $_POST['repository_path_destination']));
debug(2, sprintf("repository_create_directory : %s", $_POST['repository_create_directory']));
debug(2, sprintf("repository_start_script : %s", $_POST['repository_start_script']));
debug(2, sprintf("repository_parameters : %s", $_POST['repository_parameters']));
debug(2, sprintf("repository_delete_file_after_execute_successful : %s", $repository_delete_file_after_execute_successful));

if ($DEBUG>3) {
    $i = 0;
    foreach($_POST["filename"] as $item) {
        debug(4, "====");
        debug(4, sprintf("Filename %s = %s", $i, $_POST["filename"][$i]));
        debug(4, sprintf("Select_to_copy %s = %s", $i, $_POST["select_to_copy"][$i]));
        debug(4, sprintf("Select_to_execute %s = %s", $i, $_POST["select_to_execute"][$i]));
        $i++;
    }
}

/*
 * handle user action
 */
if ($_GET["download"] != "") {
    /*
     * action = Download one file
     */
    debug(1, sprintf("User action - download this file : %s", clean_path($current_directory . "/" . $_GET["download"])));

    $file = new MSC_File(realpath($repository_home_directory . "/" . $current_repository_directory . "/" . $_GET["download"]));

    $file->download();
    exit();
}

if ($_POST["repository_launch_action"] != "") {
    /*
     * Add command to scheduler
     */
    if ($current_repository_directory == "") $current_repository_directory = "/";
    $path_source = clean_path("/".$config["repository"]."/".$current_repository_directory);

    $start_file = "";
    $files = array();
    $i = 0;

    foreach($_POST["select_to_copy"] as $i) {
        // push files even if they are directories since they will 
        // be uploaded with a 'scp -r'
        $item = $_POST["filename"][$i];
        array_push($files, $item);
        if ( $_POST["select_to_execute"] == $i ) {
            $start_file = $item;
        }
    }

    //debug(3, sprintf("Select to copy = %s", var_export($files, true)));
    debug(3, sprintf("Select to execute = %s", $start_file));

    $parameters = $_POST['repository_parameters'];

    //$path_destination = $_POST['repository_path_destination'];
    $path_destination = $session->tmp_path;
    if ($session->platform == "Windows") $path_destination = $config['path_destination'];

    $create_directory_enable = $_POST['repository_create_directory'];
    if ($_POST["select_to_execute"]==-1) {
        $start_script_enable = false;
    } else {
        $start_script_enable = $_POST['repository_start_script'];
    }
    $delete_file_after_execute_successful_enable = $_POST['repository_delete_file_after_execute_successful'];
    if ($repository_start_date!="d&egrave;s que possible" && $repository_start_date!="ASAP") {
        list($date, $time) = split(" [^ ]* ", $repository_start_date);
        list($day, $month, $year) = split("-", $date);
        $start_date = $year."-".$month."-".$day." ".$time.":00";
    } else {
        $start_date = "0000-00-00 00:00:00";
    }

    if ($repository_end_date!="aucune" && $repository_end_date!="none") {
        list($date, $time) = split(" [^ ]* ", $repository_end_date);
        list($day, $month, $year) = split("-", $date);
        $end_date = $year."-".$month."-".$day." ".$time.":00";
    } else {
        $end_date = "0000-00-00 00:00:00";
    }


    if ( $_GET["mac"] != "" ) {
        $target = $session->hostname;
    } elseif (( $_GET["profile"] != "" ) || ( $_GET["group"] != "" )) {
        $target = $_GET["profile"] . ":" . $_GET["group"]."/";
    }
    $username = "root";
    $title = $_POST["repository_command_title"];
    if ($_POST["repository_wake_on_lan"] == "1") {
        $wake_on_lan_enable = true;
    } else {
        $wake_on_lan_enable = false;
    }

    if ($_POST["repository_next_connection_delay"] != "") {
        $next_connection_delay = $_POST["repository_next_connection_delay"];
    } else {
        $next_connection_delay = 60;
    }

    if ($_POST["repository_max_connection_attempt"] != "") {
        $max_connection_attempt = $_POST["repository_max_connection_attempt"];
    } else {
        $max_connection_attempt = 3;
    }

    if ($_POST["repository_inventory"] == 1) {
        $start_inventory_enable = true;
    } else {
        $start_inventory_enable = false;
    }
    if (!$_POST["repeat"]) {
        $repeat = 0;
    } else {
        $repeat = intval($_POST["repeat"]);
        if ($start_date == "0000-00-00 00:00:00") $start_date = date("Y-m-d G:i:00");
    }

    $id_command = scheduler_add_command(
        $start_file,
        $parameters,
        $path_destination,
        $path_source,
        $files,
        $target,
        $create_directory_enable,
        $start_script_enable,
        $delete_file_after_execute_successful_enable,
        $start_date,
        $end_date,
        $username,
        $REMOTE_USER."@".$_SERVER['REMOTE_ADDR'],
        $title,
        $wake_on_lan_enable,
        $next_connection_delay,
        $max_connection_attempt,
        $start_inventory_enable,
        $repeat
    );
    /*
     * Dispatch all command
     */
    scheduler_dispatch_all_commands();

    /*
     * Start all command
     */
    scheduler_start_all_commands();

    /*
     * Redirect to command state
     */
    if ($_GET["mac"]!="") {
        // Redirect to command_on_host state page
        $id_command_on_host = scheduler_get_id_command_on_host($id_command);

        print("<html><head><meta http-equiv=\"refresh\" content=\"0;url=" .
            urlStr("msc/msc/cmd_state", array(
                        'mac'=>$_GET["mac"],
                        'group'=>$_GET["profile"],
                        'profile'=>$_GET["group"],
                        'id_command_on_host'=>$id_command_on_host
                    )
            ).
            "\"></head></html>");
        exit();
    } else {
        // Redirect to command state page
        print("<html><head><meta http-equiv=\"refresh\" content=\"0;url=" .
            urlStr("msc/msc/cmd_state", array(
                    'mac'=>$_GET["mac"],
                    'group'=>$_GET["profile"],
                    'profile'=>$_GET["group"],
                    'id_command'=>$id_command
                )
            ).
            "\"></head></html>");
        exit();
    }
}

/*
 * Make Tree directory
 */

debug(1, "Make tree repository directory");
$tree_directory = new MSC_Tree(mscGetRepositoryPath(), $current_repository_directory);

/*
 * Make file list directory
 */
debug(1, "Make file list repository directory");
$list_directory = new MSC_Directory(realpath(join('/', array(mscGetRepositoryPath(), $current_repository_directory))));

/*
 * Initialise template engine
 */
$template = new MSC_Tmpl(array("repository_page" => "repository.tpl" ));

$template->header_param = array("msc repository", $text{'repository_title'});

$script = urlStr("msc/msc/edit", array(
    'mac'=>$_GET["mac"],
    'group'=>$_GET["profile"],
    'profile'=>$_GET["group"],
));
$template->set_var("EDIT_SCRIPT_NAME", $script);

$script = urlStr("msc/msc/download", array(
    'mac'=>$_GET["mac"],
    'group'=>$_GET["profile"],
    'profile'=>$_GET["group"],
));
$template->set_var("DOWNLOAD_SCRIPT_NAME", $script);

$script = urlStr("msc/msc/repository", array(
    'mac'=>$_GET["mac"],
    'group'=>$_GET["profile"],
    'profile'=>$_GET["group"],
));                                                                                                                                                                                                                                                                                                                                                                            
$template->set_var("SCRIPT_NAME", $script);

$template->set_var("MAC", urlencode($_GET['mac']));
$template->set_var("PROFILE", urlencode($_GET['profile']));
$template->set_var("GROUP", urlencode($_GET['group']));
$template->set_var("CURRENT_TAB", "repository");

/*if ($_GET["mac"] != "") {
    MSC_Widget_where_I_m_connected($template, $session->hostname, $session->ip, $session->profile, $session->group, "where_I_m_connected");
} else {
    MSC_Widget_where_I_m_connected_group_and_profile($template, $_GET["group"], $_GET["profile"], "where_I_m_connected");
}*/

if ($current_repository_directory == "") $current_repository_directory = "/";
$template->set_var("CURRENT_DIRECTORY_PATH", $current_repository_directory);

MSC_Widget_Tree_Directory(
    $template,
    $tree_directory->tree,
    "$script&repository_pwd="
);

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

/*
 * Send file list directory to template
 */
$array_files = $list_directory->array_files; /* List of file and directory */
if (count($array_files) > 0) {
    MSC_Widget_File_List_Directory($template, $array_files, false);
    $template->set_block("repository_page", "FILE_LIST_DIRECTORY_EMPTY", "file_list_directory_empty");
    $template->set_var("file_list_directory_empty", "");
} else {
    $template->set_var("file_list_directory", "");
}

/* */

MSC_Widget_standard_file_list_directory_actions($template, $current_repository_directory);

if ($_GET["mac"] != "") {
    MSC_Widget_repository_actions($template, $config, $session->hostname);
} else {
    MSC_Widget_repository_actions($template, $config, "", $_GET["profile"], $_GET["group"]);
}
$template->set_var("OS", $session->platform);

/*
 * Transmission des param?tres vers le template
 */

/*
 * Display
 */
$template->set_var('IMAGE_PATH', '/mmc/modules/msc/graph/images/');
$template->set_var('JAVASCRIPT_PATH', '/mmc/modules/msc/graph/js/');
$template->set_var('CSS_PATH', '/mmc/modules/msc/graph/css/');
$template->pparse("out", "repository_page", "repository_page");

?>
