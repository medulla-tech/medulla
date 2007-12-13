<?

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 *
 * $Id: general.php 26 2007-10-17 14:48:41Z nrueff $
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

require('modules/msc/includes/qactions.inc.php');
require('modules/msc/includes/mirror_api.php');

function action($action, $cible) {
    $script_list = msc_script_list_file();
    if (array_key_exists($action, $script_list)) {
        require("modules/msc/includes/actions.inc.php");
        $id_command = add_command_quick(
            $script_list[$action]["command"],
            $cible,
            $script_list[$action]["title".$current_lang]);
        dispatch_all_commands();
        // if machine 
        $id_command_on_host = get_id_command_on_host($id_command);

        header("Location: ".urlStrRedirect("base/computers/msctabs", array('tab'=>'tablogs', 'name'=>$_GET['name'], 'coh_id'=>$id_command_on_host)));
        //elseif groupe 
    }
}


$machine = getMachine(array('hostname'=>$_GET['name'])); // should be changed in uuid
if ($machine->hostname != $_GET['name']) {
    $msc_host = new RenderedMSCHostDontExists($_GET['name']);
    $msc_host->headerDisplay();
} else {
    if ($_POST['launchAction']) {
        action($_POST['launchAction'], $_GET['name']);
    }

    // Display the actions list
    $label = new RenderedLabel(3, sprintf(_T('Quick action on %s'), $machine->hostname));
    $label->display();

    $msc_actions = new RenderedMSCActions(msc_script_list_file());
    $msc_actions->display();
                
    require("modules/msc/includes/package_api.php");
    $label = new RenderedLabel(3, sprintf(_T('These packages can by installed on %s'), $machine->hostname));
    $label->display();

    
    $a_packages = array();
    $a_pversions = array();
    $a_css = array();
    $params = array();
    foreach (getAllPackages() as $package) {
        $a_packages[] = $package->label;
        $a_pversions[] = $package->version;
        $params[] = array('pid'=>$package->id, 'name'=>$machine->hostname, 'from'=>'base|computers|msctabs|tablogs');
        $a_css[] = 'primary_list';
    }
    
    //#################
    // local packages : should change the display style, not display new tables
    //#################
    $mirrors = getSubPackageMirror(&$machine);
    
    foreach ($mirrors as $mirror) {
        foreach (getAllMirrorPackages($mirror) as $package) {
            $a_packages[] = $package->label;
            $a_pversions[] = $package->version;
            $params[] = array('pid'=>$package->id, 'name'=>$machine->hostname, 'from'=>'base|computers|msctabs|tablogs');
            $a_css[] = 'secondary_list';
        }
    }
    
    $n = new ListInfos($a_packages, _T("Package"));
    $n->addExtraInfo($a_pversions, _T("Version"));
    $n->setCssClasses($a_css);
    $n->setParamInfo($params);
    
    $n->addActionItem(new ActionPopupItem(_T("Launch", "msc"),"start_tele_diff", "start", "msc", "base", "computers"));
    $n->addActionItem(new ActionPopupItem(_T("Details", "msc"),"package_detail", "detail", "msc", "base", "computers"));
    
    $n->drawTable(0);
       
}

?>
<style>
.primary_list { }
.secondary_list {
    background-color: #e1e5e6 !important;
}
li.detail a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/info.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>


