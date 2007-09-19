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

require_once("modules/msc/includes/tmpl.inc.php"); /**< Use MSC_Tmpl class */
require_once("modules/msc/includes/debug.inc.php"); /**< Use Debug function */

/*
 * Initialise template engine
 */
$template = new MSC_Tmpl(array("connection_error_page" => "connection_error_page.tpl" ));

$template->header_param = array("msc connection_error", $text{'home_title'});

$template->set_var("MAC", $session->mac);
$template->set_var("IP", $session->ip);
$template->set_var("HOSTNAME",$session->hostname);

if ($session->ping_error) {
	$template->set_var("PING", $text{"failed"});
	$template->set_var("TEST_SSH", $text{"not_tested"});
	$template->set_var("TEST_AUTOFS", $text{"not_tested"});
	$template->set_var("SSH_COMMAND", "");
	$template->set_var("SSH_RETURN_VAL", "");
	$template->set_var("SSH_OUTPUT", "");
	
} else {
	$template->set_var("PING", $text{"success"});
	if ($session->error_ssh_failed) {
		$template->set_var("TEST_SSH", $text{"failed"});
		$template->set_var("TEST_AUTOFS", $text{"not_tested"});
	} else {
		$template->set_var("TEST_SSH", $text{"success"});
	
		if ($session->error_autofs_failed) $template->set_var("TEST_AUTOFS", $text{"failed"});
		else $template->set_var("TEST_AUTOFS", $text{"success"});
	}


	$template->set_var("SSH_COMMAND",$session->ssh_test_command);
	$template->set_var("SSH_RETURN_VAL","'".$session->ssh_return_var."'");
	$output = "";
	if(count($session->ssh_array_output)>0) {
		$separator="";
		if (is_array($session->ssh_array_output)) {
			foreach($session->ssh_array_output as $line) {
				$output.=$separator.$line;
				$separator="<br />";
			}
		} else {
			$output = $session->ssh_array_output;
		}
	} else $output="";
	$template->set_var("SSH_OUTPUT",$output);
}


/*
 * Display
 */
$template->pparse("out", "connection_error_page", "connection_error_page");
?>
