<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
require_once("modules/dyngroup/includes/includes.php");
$groupedit = True;
if (strpos($_GET['action'], 'profile') !== false) {
    $groupedit = False;
}
if ($edition) {
    if ($groupedit) {
        $target = 'computersgroupedit';
    } else {
        $target = 'computersprofileedit';
    }
} else {
    if ($groupedit) {
        $target = 'computersgroupcreator';
    } else {
        $target = 'computersprofilecreator';
    }
}
$subedition = false;
if (strlen($_GET['subedition']) && $_GET['subedition'] == '1') {
    $subedition = true;
}


// getting request and id parameters
$id = idGet();
$imaging_server = quickGet('imaging_server');
$group = new Group($id, true);
$request = quickGet('request');
if ($request == 'stored_in_session') {
    $request = $_SESSION['request'];
    unset($_SESSION['request']);
}
if (strlen($request)) {
    $r = new Request();
    $r->parse($request);
    $request = $r;
} elseif (strlen($id)) {
    $r = new Request();
    $r->parse($group->getRequest());
    $request = $r;
} else {
    $request = new Request();
}

// a part of the request has to be removed
if ($_GET['action'] == 'computersgroupsubedit' || $_GET['action'] == 'computersgroupcreatesubedit') {
    if (strlen(quickGet('sub_id'))) {
        $sub = $request->getSub(quickGet('sub_id'));
        quickSet('req', $sub->module);
        quickSet('add_param', $sub->crit);
        quickSet('value', $sub->val);
        $request->removeSub(quickGet('sub_id'));
    }
}
if ($_GET['action'] == 'computersgroupsubdel' || $_GET['action'] == 'computersgroupcreatesubdel') {
    $request->removeSub(quickGet('sub_id'));
}

// a new part has to be added to the request
// if the part is extended, check the validity of data or parse the date
if (quickGet('req') && quickGet('param')) {
    $correct = true;
    if (quickGet('type_extended')) {
        switch (quickGet('type_extended')) {
            case 'date':
                // Keep only the date in YYYY-mm-dd format
                quickSet('value', substr(quickGet('value'), 0, 10));
                break;
            case 'int':
                // Check if the value of the input is a number
                $correct = preg_match("#^[0-9]+$#", quickGet('value'));
                break;
        }
    }
    if ($correct) {
        $sub = new SubRequest(quickGet('req'), quickGet('param'), quickGet('value'), quickGet('value2'), quickGet('operator'));
        $request->addSub($sub);
    }
}

// select the module in which a part of the request must be launch
//TODO put in class
$modules = getPossiblesModules();

if (count($modules) == 1) {
    quickSet('add_req', $modules[0]);
} else {
    $add_req = quickget('add_req');
    if (!isset($add_req) || count($add_req) == 0 || $add_req == '') {
        $default = getDefaultModule();
        quickSet('add_req', $default);
    }

    print "<table><tr><td style=\"width:300px;border:0\">" . _T("Choose the module you want to query : ", "dyngroup") . "</td>";

    foreach ($modules as $name) {
        if ($name == quickGet('add_req')) {
            print "<td style=\"width:80px;border:0\">$name</td>";
        } else {
            $_SESSION['request'] = $request->toS();
            print "<td style=\"width:80px;border:0\"><a href='" .
                    urlStr("base/computers/$target", array(
                        'add_req' => $name,
                        'request' => 'stored_in_session',
                        'id' => $id,
                        'imaging_server' => $imaging_server
                    )) .
                    "'>$name</a></td>";
        }
    }
    print "<td style=\"border:0\"></td></tr></table>";
}

// criterion selection
//TODO put in class
if (quickGet('add_req')) {
    $criterion = getPossiblesCriterionsInModule(quickGet('add_req'));
    // If there is only one criterion, we display it directly
    if (count($criterion) == 1) {
        quickSet('req', quickGet('add_req'));
        quickSet('add_param', $criterion[0]);
    } else {
        // Display All categories
        $categories = getQueryGroupsForModule(quickGet('add_req'));
        // Title
        print "<table style=\"width:700px;\" cellspacing=0 class=\"listinfos\">";
        // Printing category fields
        foreach ($categories as $category) {
            $cat_label = $category[0];
            $fields = $category[1];
            // Category title
            print "<thead><tr><td style=\"text-transform:uppercase;font-size:0.9em;width:250px;\">" . _T($cat_label, "dyngroup") . "</td><td></td></tr></thead>";
            foreach ($fields as $field) {
                $param_name = $field[0];
                $description = $field[1];
                if ($param_name == quickGet('add_param')) {
                    print "<td>$param_name</td>";
                } else {
                    $_SESSION['request'] = $request->toS();
                    print "<tr><td style=\"padding-left:20px;\"><a href='" .
                            urlStr("base/computers/$target", array(
                                'req' => quickGet('add_req'),
                                'add_param' => $param_name,
                                'request' => 'stored_in_session',
                                'id' => $id,
                                'imaging_server' => $imaging_server
                            )) .
                            "'>" . _T($param_name, 'dyngroup') . "</a></td>" .
                            "<td>" . ($description == '' ? '' : _T($description, 'dyngroup') ) . "</td>" .
                            "</tr>";
                }
            }
        }
        print "</table>";
    }
}

// allow to select/write a value for the criterion
//TODO put in class
if (quickGet('add_param')) {
    print "<form action = '" . urlStr("base/computers/$target", array()) . "' method = 'POST'><table>";
    print "<input type = 'hidden' name = 'imaging_server' value = '$imaging_server'/>";
    // need to be changed in getCriterionType (we don't use the second part of the array...
    $type = getTypeForCriterionInModule(quickGet('req'), quickGet('add_param'));
    $extended = getExtended(quickGet('req'), quickGet('add_param'));

    print "<tr><td>" . quickGet('req') . " > " . quickGet('add_param') . "</td><td>";
    if (strlen($extended)) {
        // Insert a hidden input which contains the type of data
        print "<input type = 'hidden' name = 'type_extended' value = '" . $extended . "' />";

        // Display an option list to chose the comparison operator
        $operators = array('=', '<', '>', '!=');
        $listbox = new SelectItem("operator");
        $listbox->setElements($operators);
        $listbox->setElementsVal($operators);

        print _T("Comparison operator : ");
        $listbox->display();

        print "</td><td>";

        switch ($extended) {
            // Execute a regexp that checks the right type
            case 'int':
                // Nothing to do for the moment.
                break;
            // Display a calendar widget instead of an input
            case 'date':
                include("modules/base/includes/AjaxFilterLog.inc.php");
                $dateWidget = new LogDynamicDateTpl("value", _("Date"));
                $dateWidget->display();
                print "</td><td>";
                print "<input class = 'btnPrimary' value = '" . _T("Add", "dyngroup") . "' name = 'Add' type = 'submit'/>";
                print "</td><td>";
                break;
        }
    }
    if ($extended != "date") {
        switch ($type) { #$param[0] ) {
            case 'string':
                print "<input name = 'value' type = 'text'></input>";
                print "<input class = 'btnPrimary' value = '" . _T("Add", "dyngroup") . "' name = 'Add' type = 'submit'/>";
                break;
            case 'list':
                $module = clean(quickGet('req'));
                $criterion = clean(quickGet('add_param'));
                include("modules/dyngroup/includes/autocomplete.php");
                $auto = new Autocomplete($module, $criterion, quickGet('value'), $subedition);
                $auto->display();
                break;
            case 'double':
                $module = clean(quickGet('req'));
                $criterion = clean(quickGet('add_param'));
                include("modules/dyngroup/includes/double.php");
                $auto = new DoubleAutocomplete($module, $criterion, quickGet('value'), $subedition);
                $auto->display();
                break;
            case 'halfstatic':
                $module = clean(quickGet('req'));
                $criterion = clean(quickGet('add_param'));
                include("modules/dyngroup/includes/autocomplete.php");
                $auto = new Autocomplete($module, $criterion, quickGet('value'), $subedition);
                $auto->display();
                break;
            case 'bool':
                $b_label = _T("Add", "dyngroup");
                if ($subedition) {
                    $b_label = _T("Modify", "dyngroup");
                }
                print "<select name = 'value'>";
                print "<option name = 'True' value = 'True'>" . _T("Yes", "dyngroup") . "</option>";
                print "<option name = 'False' value = 'False'>" . _T("No", "dyngroup") . "</option>";
                print "</select>";
                print "<input class = 'btnPrimary' value = '" . _T("Add", "dyngroup") . "' name = 'Add' type = 'submit'/>";
                break;
            case 'true':
                print "<input type = 'hidden' value = 'True' name = 'value'/><input type = 'text' readonly value = '" . _T("Yes", "dyngroup") . "'/>";
                print "<input class = 'btnPrimary' value = '" . _T("Add", "dyngroup") . "' name = 'Add' type = 'submit'/>";
                break;
        }
    }
    print "</td><td>";
    print "<input type = 'hidden' name = 'req' value = '" . quickGet('req') . "'/>";
    print "<input type = 'hidden' name = 'param' value = '" . quickGet('add_param') . "'/>";
    print "<input type = 'hidden' name = 'request' value = '" . $request->toURL() . "'/>";
    print "<input type = 'hidden' name = 'id' value = '$id'/>";
    print "</td></tr>";
    print "</table></form>";
}

// display the request in detail
if (!$request->isEmpty()) {
    print "<hr/>";
    print "<h3>" . _T("The request is : ", "dyngroup") . "</h3>";
    if ($edition) {
        $request->displayReqListInfos(true, array('id' => $id, 'gid' => $id, 'target' => $target, 'target_edit' => 'computersgroupsubedit', 'target_del' => 'computersgroupsubdel', 'request' => $request->toS()));
    } else {
        $request->displayReqListInfos(true, array('id' => $id, 'gid' => $id, 'target' => $target, 'target_edit' => 'computersgroupcreatesubedit', 'target_del' => 'computersgroupcreatesubdel', 'request' => $request->toS(), 'tab' => 'tabdyn'));
    }
}

// display action buttons in the bottom
//TODO put in class
if (!$request->isEmpty()) {  # TODO check ACLs....
    print "<hr/>";
    print "<table>";
    print "<tr><td>";
    $b = new Button('base', 'computers', 'creator_step2');
    $_SESSION['request'] = $request->toS();
    $url = urlStr("base/computers/creator_step2", array('id' => $id, 'request' => 'stored_in_session', 'imaging_server' => $imaging_server, 'is_group' => ( $groupedit ? '1' : 0)));
    print $b->getOnClickButton(_T("Go to save step", "dyngroup"), $url);

    print "</td><td>";
    print "</td></tr>";
    print "</table>";
}
?>
<style>
    li.delete a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/delete.png   ");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
    }

</style>