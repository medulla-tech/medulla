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

require_once('modules/msc/includes/widgets.inc.php');
require_once('modules/msc/includes/utilities.php');
require_once('modules/msc/includes/qactions.inc.php');
require_once('modules/msc/includes/mirror_api.php');
require_once('modules/msc/includes/commands_xmlrpc.inc.php');
require_once('modules/msc/includes/package_api.php');
require_once('modules/msc/includes/scheduler_xmlrpc.php');
require_once('modules/msc/includes/mscoptions_xmlrpc.php');

### Advanced actions handling ###
/* Advanced action: post handling */
if (isset($_GET['badvanced']) and isset($_POST['bconfirm'])) {
    // Vars seeding
    $post = $_POST;
    $from = $post['from'];
    $path =  explode('|', $from);
    $module = $path[0];
    $submod = $path[1];
    $page = $path[2];
    $tab = $path[3];
    $params = array();
    foreach (array('start_script', 'clean_on_success', 'do_wol', 'next_connection_delay','max_connection_attempt', 'do_inventory', 'ltitle', 'parameters', 'papi', 'maxbw', 'deployment_intervals') as $param) {
        $params[$param] = $post[$param];
    }
    $p_api = new ServerAPI();
    $p_api->fromURI($post['papi']);

    foreach (array('start_date', 'end_date') as $param) {
        if ($post[$param] == _T("now", "msc")) {
            $params[$param] = "0000-00-00 00:00:00";
        } elseif ($post[$param] == _T("never", "msc")) {
            $params[$param] = "0000-00-00 00:00:00";
        } else
            $params[$param] = $post[$param];
    }

    $hostname = $post['hostname'];
    $uuid = $post['uuid'];
    $gid = $post['gid'];

    if (isset($_GET['uuid']) && $_GET['uuid']) {
        $machine = getMachine(array('uuid'=>$_GET['uuid']), True);
        if ($machine->uuid == $uuid) { // Action on a single computer
                $cible = array($uuid, $machine->hostname);
        } else { // action on a whole group
                $group = new Group($gid);
                $cible = array_map('onlyValues', $group->getResult(0, -1));
        }
    } else {
        $group = new Group($gid);
        $cible = array_map('onlyValues', $group->getResult(0, -1));
    }

    $pid = $post['pid'];
    $mode = $post['copy_mode'];

    // record new command
    $id = add_command_api($pid, $cible, $params, $p_api, $mode, $gid);
    scheduler_start_all_commands();

    // then redirect to the logs page
    header("Location: " . urlStrRedirect("$module/$submod/$page", array('tab'=>$tab, 'uuid'=>$uuid, 'hostname'=>$hostname, 'gid'=>$gid, 'cmd_id'=>$id)));
}

/* Advanced action: form display */
if (isset($_GET['badvanced']) and !isset($_POST['bconfirm'])) {
    // Vars seeding
    $from = $_GET['from'];
    $hostname = $_GET['hostname'];
    $uuid = $_GET['uuid'];
    $gid = $_GET['gid'];
    $pid = $_GET['pid'];
    $p_api = new ServerAPI();
    $p_api->fromURI($_GET["papi"]);
    $name = getPackageLabel($p_api, $_GET['pid']);

    if (isset($_GET['uuid']) && $_GET['uuid']) {
        $machine = getMachine(array('uuid'=>$_GET['uuid']), True);
        // top label
        if ($machine->uuid == $_GET['uuid']) { // Action on a single computer
                $hostname = $machine->hostname;
                $label = new RenderedLabel(3, sprintf(_T('Advanced launch action "%s" on "%s"', 'msc'), $name, $machine->hostname));
        } else { // action on a whole group
                $group = new Group($_GET['gid'], true);
                $label = new RenderedLabel(3, sprintf(_T('Advanced launch action "%s" on "%s"', 'msc'), $name, $group->getName()));
        }
    } else {
        $group = new Group($_GET['gid'], true);
        $label = new RenderedLabel(3, sprintf(_T('Advanced launch action "%s" on "%s"', 'msc'), $name, $group->getName()));
    }
    $label->display();

    // form design
    $f = new Form();
    $f->push(new Table());
    $f->add(new HiddenTpl("uuid"),  array("value" => $uuid,         "hide" => True));
    $f->add(new HiddenTpl("papi"),  array("value" => $_GET["papi"], "hide" => True));
    $f->add(new HiddenTpl("name"),  array("value" => $hostname,     "hide" => True));
    $f->add(new HiddenTpl("from"),  array("value" => $from,         "hide" => True));
    $f->add(new HiddenTpl("pid"),   array("value" => $pid,          "hide" => True));
    $f->add(new HiddenTpl("gid"),   array("value" => $gid,          "hide" => True));
    $f->add(new TrFormElement(_T('Command title', 'msc'),                               new InputTpl('ltitle')), array("value" => $name));
    $f->add(new TrFormElement(_T('Wake on lan', 'msc'),                                 new CheckboxTpl("do_wol")), array("value" => $_GET['do_wol'] == 'on' ? 'checked' : ''));
    $f->add(new TrFormElement(_T('Start inventory', 'msc'),                             new CheckboxTpl("do_inventory")), array("value" => $_GET['do_inventory'] == 'on' ? 'checked' : ''));
    $f->add(new TrFormElement(_T('Start the script', 'msc'),                            new CheckboxTpl("start_script")), array("value" => 'checked'));
    $f->add(new TrFormElement(_T('Delete files after a successful execution', 'msc'),   new CheckboxTpl("clean_on_success")), array("value" => 'checked'));
    $f->add(new TrFormElement(_T('Delay betwen connections (minuts)', 'msc'),           new InputTpl("next_connection_delay")), array("value" => $_GET['next_connection_delay']));
    $f->add(new TrFormElement(_T('Maximum number of connection attempt', 'msc'),        new InputTpl("max_connection_attempt")), array("value" => $_GET['max_connection_attempt']));
    $f->add(new TrFormElement(_T('Command parameters', 'msc'),                          new InputTpl('parameters')), array("value" => ''));
    $f->add(new TrFormElement(_T('Start date', 'msc'),                                  new DynamicDateTpl('start_date')), array('ask_for_now' => 1));
    $f->add(new TrFormElement(_T('End date', 'msc'),                                    new DynamicDateTpl('end_date')), array('ask_for_never' => 1));
    $f->add(new TrFormElement(_T('Deployment interval', 'msc'),                         new InputTpl('deployment_intervals')), array("value" => $_GET['deployment_intervals']));
    $f->add(new TrFormElement(_T('Max bandwidth (b/s)', 'msc'),                         new NumericInputTpl('maxbw')), array("value" => web_def_maxbw()));
    $rb = new RadioTpl("copy_mode");
    $rb->setChoices(array(_T('push', 'msc'), _T('push / pull', 'msc')));
    $rb->setvalues(array('push', 'push_pull'));
    $rb->setSelected($_GET['copy_mode']);
    $f->add(new TrFormElement(_T('Copy Mode', 'msc'), $rb));

    $f->pop();
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();

}
### /Advanced actions handling ###

/* single target: form display */
if (!isset($_GET['badvanced']) && $_GET['uuid'] && !isset($_POST['launchAction'])) {
    $machine = getMachine(array('uuid'=>$_GET['uuid']), True);
    if ($machine->uuid != $_GET['uuid']) { // Not matching computer found, show error
        $msc_host = new RenderedMSCHostDontExists($_GET['hostname']);
        $msc_host->headerDisplay();
    } else { // We found a matching computer, display QActions and available packages
        $machine = getMachine(array('uuid'=>$_GET['uuid']), $ping = False);
        $msc_host = new RenderedMSCHost($machine);
        $msc_host->ajaxDisplay();

        $msc_actions = new RenderedMSCActions(msc_script_list_file(), $machine->hostname, array('uuid'=>$_GET['uuid']));
        $msc_actions->display();

        $ajax = new AjaxFilter("modules/msc/msc/ajaxPackageFilter.php?uuid=".$machine->uuid."&hostname=".$machine->hostname);
        $ajax->display();
        $ajax->displayDivToUpdate();
    }
}

/* group display */
if (!isset($_GET['badvanced']) && isset($_GET['gid']) && !isset($_POST['launchAction']) && !isset($_GET['uuid'])) {
    $group = new Group($_GET['gid'], true);
    // Display the actions list
    $msc_actions = new RenderedMSCActions(msc_script_list_file(), $group->getName(), array("gid"=>$_GET['gid']));
    $msc_actions->display();

    $ajax = new AjaxFilter("modules/msc/msc/ajaxPackageFilter.php", "container", array("gid"=>$_GET['gid']));
    $ajax->display();
    print "<br/>";
    $ajax->displayDivToUpdate();
}


?>
<style>
.primary_list { }
.secondary_list {
    background-color: #e1e5e6 !important;
}

</style>
