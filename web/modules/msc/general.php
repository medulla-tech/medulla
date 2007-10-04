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
require("modules/msc/includes/tmpl.inc.php");
require("modules/msc/includes/path.inc.php");
require("modules/msc/includes/system.inc.php");
require("modules/msc/includes/ssh.inc.php");
require("modules/msc/includes/widget.inc.php");

require_once("modules/msc/includes/xmlrpc.php");

$p = new PageGenerator(_T("General informations"));
$p->setSideMenu($sidemenu);
$p->display(); 

if ($_GET['mac'] != '') {
	require("modules/msc/includes/open_session.inc.php");

	/*
	 * Control action
	 */
	if ($_POST["action"] != "") {
		$script_list = msc_script_list_file();
	        if (array_key_exists($_POST["action"], $script_list)) {
			require_once("modules/msc/includes/scheduler.php");
			
			$id_command = scheduler_add_command_quick(
				$script_list[ $_POST["action"] ][ "command" ],
				$session->hostname,
				$script_list[ $_POST["action"] ]["title".$current_lang]);
			scheduler_dispatch_all_commands();
			scheduler_start_all_commands();
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
		}
	}
	
	/*
	 * Initialise template engine
	 */
	$template = new MSC_Tmpl(array("home_page" => "home_one_host_page.tpl" ));

	/*                      
	 * Test ping            
	 */                     
	if (MSC_sysPing($session->ip)==0) {
		// Host reachable
		$host_reachable = true;
	} else {
		// Host not reachable
		$host_reachable = false;
	}

	/*
	 * Display debug informations
	 */
	debug(2, sprintf("MAC Address : %s", $_GET["mac"]));
	debug(2, sprintf("IP Address : %s", $session->ip));
	debug(2, sprintf("Hostname : %s", $session->hostname));
	debug(2, sprintf("Profile name : %s", $session->profile));
	debug(2, sprintf("Group name : %s", $session->group));
	debug(2, sprintf("Operating system : %s", $session->platform));

	/*                      
	 * Transmission des paramètres vers le template
	 */             

	$template->set_var("HOST_INFO_MAC_ADDRESS", $_GET["mac"]);
	$template->set_var("MAC", urlencode($_GET['mac']));
	$template->set_var("HOST_INFO_IP_ADDRESS", $session->ip);
	$template->set_var("HOST_INFO_HOSTNAME", $session->hostname);
	$template->set_var("HOST_INFO_PROFILE", $session->profile);
	$template->set_var("HOST_INFO_GROUP", $session->group);
	$template->set_var("HOST_INFO_OPERATING_SYSTEM", $session->platform);
	if ($host_reachable) {  
		$template->set_var("HOST_INFO_REACHABLE", _("success"));
	} else {                
		$template->set_var("HOST_INFO_REACHABLE", _("failed"));
	}               

	$template->set_var("SCRIPT_PROFILE_URL", urlStr("msc/msc/general", array('profile'=>$session->profile)));
	$template->set_var("SCRIPT_GROUP_URL", urlStr("msc/msc/general", array('group'=>$session->group)));
} else {
	/*
	 * Control action
	 */
	if ($_POST["action"]!="") {
		$script_list = msc_script_list_file();
	        if (array_key_exists($_POST["action"], $script_list)) {
			require_once("modules/msc/includes/scheduler.php");
			
			$id_command = scheduler_add_command_quick(
				$script_list[ $_POST["action"] ][ "command" ],
				$_GET["profile"].":".$_GET["group"]."/",
				$script_list[ $_POST["action"] ]["title".$current_lang]);
			scheduler_dispatch_all_commands();
			scheduler_start_all_commands();
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
		}
	}
			  
	/*
	 * Initialise template engine
	 */ 
	$template = new MSC_Tmpl(array("home_page" => "home_group_and_profile_page.tpl" ));

	/*      
	 * Get host list of group or profile
	 */     
	$path = new MSC_Path($_GET["profile"].":".$_GET["group"]."/");

	$hosts_array = $path->get_hosts_list();


	/*              
	 * Iterate all element of files_array
	 */                     
	$i = 0;         

	if (count($hosts_array)>0) {
		$template->set_block("home_page", "HOSTS_LIST_ROW", "rows");                                               $row_class = "row-odd";
		foreach($hosts_array as $host) {
			$i++;   
			$template->set_var("INDEX", $i);

			$template->set_var("ROW_CLASS", $row_class);

			$template->set_var("HOSTNAME", $host["hostname"]);
			$template->set_var("IP", $host["ip"]);
			$template->set_var("MAC", $host["mac"]);
			$template->set_var("MAC_AND_DOT", urlencode($host["mac"]));
			$template->set_var("LINK", urlStr("msc/msc/general", array('mac'=>$host["mac"])));
      $template->set_var('EXEC_LINK', urlStr("msc/msc/repository", array( 'mac'=>$host["mac"])));
      $template->set_var('INV_LINK', urlStr("lrs-inventory/lrs-inventory/view", array('inventaire'=>$host['hostname'])));
			$template->parse("rows", "HOSTS_LIST_ROW", true);
			/*
			 * Switch the row class
			 */
			if ($row_class == "row-odd") $row_class = "row-even";
			else $row_class = "row-odd";
		}
		$template->set_block("home_page", "HOSTS_LIST_EMPTY");
		$template->set_var("HOSTS_LIST_EMPTY", "");
	} else {
		$template->set_block("home_page", "HOSTS_LIST");                                   
		$template->set_var("HOSTS_LIST", "");                                              
	}
}
	/*      
	 * Display widgets
	 */             
	$template->set_var("PROFILE", $_GET["profile"]);
	$template->set_var("GROUP", $_GET["group"]);
	$template->set_var("SCRIPT_NAME", urlStr("msc/msc/general", array()));


MSC_Widget_standard_host_actions($template, msc_script_list_file());

/*
 * Display
 */
$template->set_var('IMAGE_PATH', '/mmc/modules/msc/graph/images/');
$template->pparse("out", "home_page", "home_page");


?>

