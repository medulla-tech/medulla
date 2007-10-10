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
require_once("modules/msc/includes/tmpl.inc.php");
require_once("modules/msc/includes/path.inc.php");
require_once("modules/msc/includes/system.inc.php");
require_once("modules/msc/includes/ssh.inc.php");
require_once("modules/msc/includes/widget.inc.php");
require_once("modules/msc/includes/scheduler.php");
require_once("modules/msc/includes/functions.php");



$p = new PageGenerator(_T("Commands states"));
$p->setSideMenu($sidemenu);
$p->display(); 

if ($_GET["id_command"]!="") { ############################ id_command
    require("modules/msc/includes/commands.php");
    tmpl_command_detail($_GET);
    //exit;
} elseif ($_GET["id_command_on_host"]!="") { ################################ id_command_on_host
    require("modules/msc/includes/commands.php");
    tmpl_command_on_host_detail($_GET, 'commands_states.cgi');
    //exit;
} else {
    
    if ($_POST["apply_filter_submit"]) {
        $number_command_by_page = $_POST["number_command_by_page"];
        $state_filter = $_POST["state_filter"];
    } else {
        
        if ($_COOKIE["number_command_by_page"]=="") {
            $number_command_by_page = 10;
        } else {
            $number_command_by_page = $_COOKIE["number_command_by_page"];
        }
    }
    
    if ($_GET["page"]!="") {
        $page = $_GET["page"];
    } else {
        if ($_COOKIE["page"]=="") {
            $page = 0;
        } else {
            $page = $_COOKIE["page"];
        }
    }
    $OUTPUT_TYPE = "WEB";
    
    if ($_GET["mac"] == "") { ########################################## GROUP
        $current_mode="group";
        /*
         * Handle action
         */
        if ($_GET["msc_action"]=="play") {
            msc_command_set_play($_GET["id_command_play"]);
        } elseif ($_GET["msc_action"]=="pause") {
            msc_command_set_pause($_GET["id_command_pause"]);
        } elseif ($_GET["msc_action"]=="stop") {
            msc_command_set_stop($_GET["id_command_stop"]);
        }
        
        /*
         * Initialise template engine
         */
        $template = new MSC_Tmpl(array("commands_states_on_group_and_profile_page" => "commands_states_on_group_and_profile_page.tpl" ));
        
        $template->header_param = array("msc commands_states", $text{'explorer_title'});
        
        $script = urlStr("msc/msc/cmd_state", array(
            'mac'=>$_GET["mac"],
            'group'=>$_GET["profile"],
            'profile'=>$_GET["group"],
        ));
        $template->set_var("SCRIPT_NAME", $script);
        $template->set_var("MAC", urlencode($_GET["mac"]));
        $template->set_var("PROFILE", urlencode($_GET["profile"]));
        $template->set_var("GROUP", urlencode($_GET["group"]));
        
        template_set_cmd_by_page(&$template, 'commands_states_on_group_and_profile_page', $number_command_by_page);
        
        /**
         * Set target_filter with profil and group
         */
        $target_filter=$_GET["profile"].":".$_GET["group"]."/";
        
        $template->set_var("GROUP_AND_PROFILE", $target_filter);
        if ($target_filter == ':/') $target_filter = 'all';
        
        $total_commands_number = count_commands_filter($target_filter);
        $number_page = ceil($total_commands_number / $number_command_by_page);
        
        /**
         * Display pages list
         */
                                                                                                       
        if ($number_page > 1) {                                                                        
            if ($page==0) {
                $template->set_block("commands_states_on_group_and_profile_page", "PAGE_PREVIOUS_HIDE", "previous_page");
                $template->set_var("previous_page", "");
            } else {
                $template->set_block("commands_states_on_group_and_profile_page", "PAGE_PREVIOUS_HIDE", "previous_page");
                $template->set_var("PAGE_PREVIOUS", $page - 1);
                $template->parse("previous_page", "PAGE_PREVIOUS_HIDE");
            }
            $template->set_block("commands_states_on_group_and_profile_page", "PAGE_LINK", "page_link");
            $template->set_block("commands_states_on_group_and_profile_page", "PAGE_CURRENT", "page_current");
            $template->set_block("commands_states_on_group_and_profile_page", "LIST_PAGE_COL", "page");
        
            for($p=0;$p<$number_page;$p++) {
                if ($page == $p) {
                    $template->set_var("PAGE_LABEL", $p + 1);
                    $template->parse("page_current", "PAGE_CURRENT");
                    $template->set_var("page_link", "");
                } else {
                    $template->set_var("PAGE_NUMBER", $p);
                    $template->set_var("PAGE_LABEL", $p + 1);
                    $template->parse("page_link", "PAGE_LINK");
                    $template->set_var("page_current", "");
                
                }
                $template->parse("page", "LIST_PAGE_COL", true);
            }
            if ($page==$number_page-1) {
                $template->set_block("commands_states_on_group_and_profile_page", "PAGE_NEXT_HIDE");
                $template->set_var("PAGE_NEXT_HIDE", "");
            } else {
                $template->set_block("commands_states_on_group_and_profile_page", "PAGE_NEXT_HIDE", "next_page");
                $template->set_var("PAGE_NEXT", $page + 1);
                $template->parse("next_page", "PAGE_NEXT_HIDE");
            }
        } else {
            $template->set_block("commands_states_on_group_and_profile_page", "LIST_PAGES", "list_pages");
            $template->set_var("list_pages", "");
        }
        
        /**
         * Display the list of command
         *
         * Use filter information
         */
        $commands_array = command_list_filter($target_filter, $page, $number_command_by_page);
        if (count($commands_array) > 0) {
            /*
             * Hide COMMANDS_STATES_LIST_EMPTY block
             */
            $template->set_block("commands_states_on_group_and_profile_page", "COMMANDS_STATES_LIST_EMPTY");
            $template->set_var("COMMANDS_STATES_LIST_EMPTY", "");
        
            /*
             * Display all rows
             */
            $template->set_block("commands_states_on_group_and_profile_page", "BUTTON_PLAY", "play");
            $template->set_block("commands_states_on_group_and_profile_page", "BUTTON_PAUSE", "pause");
            $template->set_block("commands_states_on_group_and_profile_page", "BUTTON_STOP", "stop");
            $template->set_block("commands_states_on_group_and_profile_page", "COMMANDS_STATES_ROW", "row");
            $row_class = "row-odd";
            foreach($commands_array as $c) {
                $template->set_var("ROW_CLASS", $row_class);
                $template->set_var("ID_COMMAND", $c["id_command"]);
                $template->set_var("NUMBER_OF_HOST", get_number_host_of_command($c["id_command"]));
                $template->set_var("TITLE", $c["title"]);
                if ($c["date_created"] == "0000-00-00 00:00:00") {
                    $template->set_var("DATE_CREATED", "-");
                } else {
                    $template->set_var("DATE_CREATED", $c["date_created_formated"]);
                }
                
                if ($c["start_date"] == "0000-00-00 00:00:00") {
                    $template->set_var("START_DATE", "-");
                } else {
                    $template->set_var("START_DATE", $c["start_date_formated"]);
                }
                
                if ($c["end_date"] == "0000-00-00 00:00:00") {
                    $template->set_var("END_DATE", "-");
                } else {
                    $template->set_var("END_DATE", $c["end_date_formated"]);
                }
                                                          
                $current_state=get_state_of_command($c["id_command"]);            
                $template->set_var("CURRENT_STATES_ICON",state2icon($current_state));
        
                if ($current_state == "?") {
                    $template->set_var("CURRENT_STATES", $text["many_states"]);
                } else {
                    $template->set_var("CURRENT_STATES", $text[$current_state]);
                }
        
                $a_state = state_tmpl($current_state);
                foreach ($a_state as $k => $v) {
                    if ($v == '') {
                        $template->set_var($k, $v);
                    } else {
                        $template->parse($k, $v);
                    }
                }
        
                /* NOT used, this feature will be implemented in next version...
                $template->set_var("NUMBER_ATTEMPT", get_number_attempt_of_command($c["id_command"]));
                */
                $template->parse("row", "COMMANDS_STATES_ROW", true);              
                if ($row_class == "row-odd") $row_class = "row-even";              
                else $row_class = "row-odd";
            }
        } else {
            /*
             * Hide COMMANDS_STATES_LIST block
             */
            $template->set_block("commands_states_on_group_and_profile_page", "COMMANDS_STATES_LIST");
            $template->set_var("COMMANDS_STATES_LIST", "");
        }
        
        /*
         * Display
         */
        $template->set_var('IMAGE_PATH', '/mmc/modules/msc/graph/images/');
        $template->pparse("out", "commands_states_on_group_and_profile_page", "commands_states_on_group_and_profile_page");
        
    } else { ########################################################### HOST
        // include("open_session.inc.php");
        if ($_GET["mac"] != "")
                $session = new MSC_Session($_GET["mac"], "root", false, false);
        
        $hostname = $session->hostname;
        /*
         * Initialise template engine
         */
        $template = new MSC_Tmpl(array("commands_states_on_host_page" => "commands_states_on_host_page.tpl" ));
        
        $template->header_param = array("msc commands_states", $text{'explorer_title'});
    
        $script = urlStr("msc/msc/cmd_state", array(
            'mac'=>$_GET["mac"],
            'group'=>$_GET["profile"],
            'profile'=>$_GET["group"],
        ));
        
        $template->set_var("SCRIPT_NAME", $script);
        $template->set_var("MAC", urlencode($_GET["mac"]));
        $template->set_var("PROFILE", urlencode($_GET["profile"]));
        $template->set_var("GROUP", urlencode($_GET["group"]));
        $template->set_var("WHERE_I_M_CONNECTED_HOSTNAME", $hostname);
        
        /*
         * Handle action
         */
        if ($_GET["msc_action"]=="play") {
            msc_command_set_play($_GET["id_command_play"]);
        } elseif ($_GET["msc_action"]=="pause") {
            msc_command_set_pause($_GET["id_command_pause"]);
        } elseif ($_GET["msc_action"]=="stop") {
            msc_command_set_stop($_GET["id_command_stop"]);
        }                                                                                             
        
        template_set_cmd_by_page(&$template, 'commands_states_on_host_page', $number_command_by_page);
        
        $total_commands_number = count_all_commands_on_host($hostname);
        $number_page = ceil($total_commands_number / $number_command_by_page);
        /**
         * Display pages list
         */
        
        
        if ($number_page > 1) {
            if ($page==0) {
                $template->set_block("commands_states_on_host_page", "PAGE_PREVIOUS_HIDE", "previous_page");
                $template->set_var("previous_page", "");
            } else {
                $template->set_block("commands_states_on_host_page", "PAGE_PREVIOUS_HIDE", "previous_page");
                $template->set_var("PAGE_PREVIOUS", $page - 1);                 
                $template->parse("previous_page", "PAGE_PREVIOUS_HIDE");
            }
        
            $template->set_block("commands_states_on_host_page", "PAGE_LINK", "page_link");
            $template->set_block("commands_states_on_host_page", "PAGE_CURRENT", "page_current");
            $template->set_block("commands_states_on_host_page", "LIST_PAGE_COL", "page");
            for($p=0;$p<$number_page;$p++) {
                if ($page == $p) {
                    $template->set_var("PAGE_LABEL", $p + 1);
                    $template->parse("page_current", "PAGE_CURRENT");
                    $template->set_var("page_link", "");
                } else {
                    $template->set_var("PAGE_NUMBER", $p);
                    $template->set_var("PAGE_LABEL", $p + 1);
                    $template->parse("page_link", "PAGE_LINK");
                    $template->set_var("page_current", "");
        
                }
                $template->parse("page", "LIST_PAGE_COL", true);
            }
            if ($page==$number_page-1) {
                $template->set_block("commands_states_on_host_page", "PAGE_NEXT_HIDE");       
                $template->set_var("PAGE_NEXT_HIDE", "");
            } else {
                $template->set_block("commands_states_on_host_page", "PAGE_NEXT_HIDE", "next_page");
                $template->set_var("PAGE_NEXT", $page + 1);
                $template->parse("next_page", "PAGE_NEXT_HIDE");
            }
        } else {
                $template->set_block("commands_states_on_host_page", "LIST_PAGES", "list_pages");
                $template->set_var("list_pages", "");
        }
        /**
         * Display the list of command
         *
         * Use filter information
         */
        $a_commands = get_all_commands_on_host($hostname, $page, $number_command_by_page);
        
        if (count($a_commands) > 0) {
            /*
             * Hide COMMANDS_STATES_LIST_EMPTY block
             */
            $template->set_block("commands_states_on_host_page", "COMMANDS_STATES_LIST_EMPTY");
            $template->set_var("COMMANDS_STATES_LIST_EMPTY", "");
        
            /*
             * Display all rows
             */
            $template->set_block("commands_states_on_host_page", "BUTTON_PLAY", "play");
            $template->set_block("commands_states_on_host_page", "BUTTON_PAUSE", "pause");
            $template->set_block("commands_states_on_host_page", "BUTTON_STOP", "stop");
            $template->set_block("commands_states_on_host_page", "COMMANDS_STATES_ROW", "row");
            $row_class = "row-odd";
        
            foreach($a_commands as $c) {
                $template->set_var("ROW_CLASS", $row_class);
                $template->set_var("ID_COMMAND", $c["id_command"]);
                $template->set_var("ID_COMMAND_ON_HOST", $c["id_command_on_host"]);
                $template->set_var("TITLE", $c["title"]);
                if ($c["date_created"] == "0000-00-00 00:00:00") {
                    $template->set_var("DATE_CREATED", "-");
                } else {
                    $template->set_var("DATE_CREATED", $c["date_created_formated"]);
                }
                
                if ($c["start_date"] == "0000-00-00 00:00:00") {
                    $template->set_var("START_DATE", "-");
                } else {
                    $template->set_var("START_DATE", $c["start_date_formated"]);
                }                                         
                                                      
                if ($c["end_date"] == "0000-00-00 00:00:00") {
                    $template->set_var("END_DATE", "-");
                } else {
                    $template->set_var("END_DATE", $c["end_date_formated"]);
                }
        
                $current_state=$c["current_state"];
        
                $template->set_var("CURRENT_STATES_ICON",state2icon($current_state));
        
                $a_state = state_tmpl($current_state);
                    foreach ($a_state as $k => $v) {
                        if ($v == '') {
                            $template->set_var($k, $v);
                        } else {
                            $template->parse($k, $v);
                        }
                    }
                    $template->set_var("CURRENT_STATES", $text[$current_state]);
                    /* NOT used, this feature will be implemented in next version...
                    $template->set_var("NUMBER_ATTEMPT", get_number_attempt_of_command($c["id_command"]));
                    */
                    $template->parse("row", "COMMANDS_STATES_ROW", true);
                    if ($row_class == "row-odd") $row_class = "row-even";
                    else $row_class = "row-odd";
            }
        } else {
            /*
             * Hide COMMANDS_STATES_LIST block
             */
            $template->set_block("commands_states_on_host_page", "COMMANDS_STATES_LIST");
            $template->set_var("COMMANDS_STATES_LIST", "");
        }
        
        /*
         * Send standard variable to template
         */
        $template->set_var("SCRIPT_NAME", "commands_states.cgi");
        $template->set_var("MAC", urlencode($_GET['mac']));                                           
        $template->set_var("PROFILE", urlencode($_GET['profile']));
        $template->set_var("GROUP", urlencode($_GET['group']));
        
        
        /*
         * Display
         */
        $template->set_var('IMAGE_PATH', '/mmc/modules/msc/graph/images/');
        $template->pparse("out", "commands_states_on_host_page", "commands_states_on_host_page");
        
    }
}

?>

