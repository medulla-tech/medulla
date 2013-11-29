<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com/
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
require('modules/msc/includes/scheduler_xmlrpc.php');
require('modules/msc/includes/commands_xmlrpc.inc.php');

if (isset($_POST["bconfirm"])) {
    /* Form handling */
    $from = $_POST['from'];
    $path = explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];
    $url = array();
    foreach (array('name', 'from', 'uuid', 'gid', 'bundle_id', 'hostname') as $post) {
        $url[$post] = $_POST[$post];
    }
    $url['tab'] = $tab;
    if (isset($tab)) {
        $url['tab'] = $tab;
    }

    if (strlen($_POST['bundle_id'])) {
        $bundle_id = $_POST['bundle_id'];
        if (strlen($_POST['gid'])) {
            if (!strlen($_POST["coh_id"]) and !strlen($_POST["cmd_id"])) {
                stop_bundle($bundle_id);

                header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'gid'=>$gid)));
                exit;
            } elseif (strlen($_POST["cmd_id"]) and !strlen($_POST["coh_id"])) {
                $cmd_id = $_POST["cmd_id"];
                stop_command($cmd_id);
                header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'gid'=>$gid, 'bundle_id'=>$bundle_id)));
                exit;
            } else {
                $coh_id = $_POST["coh_id"];
                $cmd_id = $_POST["cmd_id"];
                stop_command_on_host($coh_id);
                header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'gid'=>$gid, 'bundle_id'=>$bundle_id, 'cmd_id'=>$cmd_id)));
                exit;
            }
        } elseif (strlen($_POST["uuid"])) {
            $hostname = $_POST["hostname"];
            $uuid = $_POST["uuid"];
            if (!strlen($_POST["coh_id"]) and !strlen($_POST["cmd_id"])) {
                stop_bundle($bundle_id);
                header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$hostname)));
                exit;
            } else {
                $coh_id = $_POST["coh_id"];
                stop_command_on_host($coh_id);
                header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$hostname)));
                exit;
            }
        }
    } else {
        if (strlen($_POST['gid']) && !strlen($_POST["coh_id"])) {
            /* The stop command must be done on a group of computers */
            $cmd_id = $_POST["cmd_id"];
            $gid = $_POST["gid"];
            stop_command($cmd_id);
            header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'gid'=>$gid)));
            exit;
        } else if (strlen($_POST['gid'])) {
            /* The stop command is done on a commands_on_host for a group of
              computers */
            $coh_id = $_POST["coh_id"];
            $cmd_id = $_POST["cmd_id"];
            $gid = $_POST["gid"];
            stop_command_on_host($coh_id);
            header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'cmd_id'=>$cmd_id, 'gid'=>$gid)));
            exit;
        } else {
            $hostname = $_POST["hostname"];
            $uuid = $_POST["uuid"];
            $coh_id = $_POST["coh_id"];
            stop_command_on_host($coh_id);
            header("Location: " . urlStrRedirect("$module/$submod/$page", $url)); #array('tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$hostname)));
            exit;
        }
    }
} else {
    /* Form displaying */
    $from = $_GET['from'];
    $hostname = $_GET["hostname"];
    $groupname = $_GET["groupname"];
    $uuid = $_GET["uuid"];
    $cmd_id = $_GET["cmd_id"];
    $coh_id = $_GET["coh_id"];
    $gid = $_GET["gid"];
    $bundle_id = $_GET['bundle_id'];
    $cmd = command_detail($cmd_id);
    $name = $cmd['title'];
    if (!$name && $_GET['title']) {
        $name = $_GET['title'];
    }

    $action_type = _T('action', 'msc');
    if (strlen($bundle_id)) {
        $action_type = _T('bundle', 'msc');
    }
    if (strlen($gid) && !strlen($coh_id)) {
        $title = sprintf(_T("Stop %s %s on this group", 'msc'), $action_type, $name);
    } else {
        $title = sprintf(_T("Stop %s %s on host %s", 'msc'), $action_type, $name, $hostname);
    }
    $f = new PopupForm($title, 'stopPopupForm');
    $f->add(new HiddenTpl("name"), array("value" => $hostname, "hide" => True));
    $f->add(new HiddenTpl("from"), array("value" => $from, "hide" => True));
    $f->add(new HiddenTpl("cmd_id"), array("value" => $cmd_id, "hide" => True));
    $f->add(new HiddenTpl("coh_id"), array("value" => $coh_id, "hide" => True));
    $f->add(new HiddenTpl("uuid"), array("value" => $uuid, "hide" => True));
    $f->add(new HiddenTpl("gid"), array("value" => $gid, "hide" => True));
    $f->add(new HiddenTpl("bundle_id"), array("value" => $bundle_id, "hide" => True));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
    #DEBUG print "u:$uuid - g:$gid || b:$bundle_id - c:$cmd_id - h:$coh_id";
}
?>
<script type="text/javascript">
    jQuery(function() {
        var $ = jQuery;
        $('form#stopPopupForm').submit(function() {
            $.ajax($(this).attr('action'), {
                type: $(this).attr('method'),
                data: $(this).serialize() + '&bconfirm=1'
            }).success(function() {
                window.location.reload();
            });
            return false;
        });
    })
</script>