<?php
/**
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

require_once("modules/dyngroup/includes/includes.php");

if ($edition) {
    $target = 'computersgroupedit';
} else {
    $target = 'computersgroupcreator';
}

// getting request and id parameters
$id = idGet();
$group = new Group($id, true);
$request = quickGet('request');
if ($request) {
    $r = new Request();
    $r->parse($request);
    $request = $r;
} elseif ($id) {
   $r = new Request();
   $r->parse($group->getRequest());
   $request = $r;
} else {
    $request = new Request();
}

// a part of the request has to be removed 
if (quickGet('delete')) {
    $request->removeSub(quickGet('delete'));
}

// a new part has to be added to the request
if (quickGet('req') && quickGet('param')) {
    $sub = new SubRequest(quickGet('req'), quickGet('param'), quickGet('value'), quickGet('value2'));
    $request->addSub($sub);
}

// select the module in which a part of the request must be launch
//TODO put in class
$modules = getPossiblesModules();
if (count($modules) == 1) {
    quickSet('add_req', $modules[0]);
} else {
    print "<table><tr><td>"._T("Choose the module you want to query : ", "dyngroup")."</td>";
    
    foreach ($modules as $name) {
        if ($name == quickGet('add_req')) {
            print "<td>$name</td>";
        } else {
            print "<td><a href='".
                urlStr("base/computers/$target", array(
                                                    'add_req'=>$name,
                                                    'request'=>$request->toURL(),
                                                    'id'=>$id
                )).
                "'>$name</a></td>";
        }
    }
    print "</tr></table>";
}

// criterion selection
//TODO put in class
if (quickGet('add_req')) {
    print "<table><tr><td>"._T("Choose your field : ", "dyngroup")."</td>";
    $criterion = getPossiblesCriterionsInModule(quickGet('add_req'));
    foreach ($criterion as $param_name) {
        if ($param_name == quickGet('add_param')) {
            print "<td>$param_name</td>";
        } else {
            print "<td><a href='".
                urlStr("base/computers/$target", array( 'req'=>quickGet('add_req'), 'add_param'=>$param_name, 'request'=>$request->toURL(), 'id'=>$id )).
                "'>$param_name</a></td>";
        }
    }
    print "</tr></table>";
}

// allow to select/write a value for the criterion
//TODO put in class
if (quickGet('add_param')) {
    print "<form action='".  urlStr("base/computers/$target", array()).  "' method='POST'><table>";
    // need to be changed in getCriterionType (we don't use the second part of the array...
    $param = getPossiblesValuesForCriterionInModule(quickGet('req'), quickGet('add_param'));
    if (!is_array($param)) { $param = array($param); }
    print "<tr><td>".quickGet('req')." > ".quickGet('add_param')."</td><td>";
    switch ($param[0]) {
        case 'string':
            print "<input name='value' type='text'></input>";
            print "<input class='btnPrimary' value='"._T("Add", "dyngroup")."' name='Add' type='submit'/>";
            break;
        case 'list':
            $module = clean(quickGet('req'));
            $criterion = clean(quickGet('add_param'));
            include("modules/dyngroup/includes/autocomplete.php");
            $auto = new Autocomplete($module, $criterion);
            $auto->display();
            break;
        case 'double':
            $module = clean(quickGet('req'));
            $criterion = clean(quickGet('add_param'));
            include("modules/dyngroup/includes/double.php");
            $auto = new DoubleAutocomplete($module, $criterion);
            $auto->display();
            break;
        case 'bool':
            print "<select name='value'>";
            print "<option name='True' value='True'>"._T("Yes", "dyngroup")."</option>";
            print "<option name='False' value='False'>"._T("No", "dyngroup")."</option>";
            print "</select>";
            print "<input class='btnPrimary' value='"._T("Add", "dyngroup")."' name='Add' type='submit'/>";
            break;
        case 'true':
            print "<input type='hidden' value='True' name='value'/><input type='text' readonly value='"._T("Yes", "dyngroup")."'/>";
            print "<input class='btnPrimary' value='"._T("Add", "dyngroup")."' name='Add' type='submit'/>";
            break;
    } 
    print "</td><td>";
    print "<input type='hidden' name='req' value='".quickGet('req')."'/>";
    print "<input type='hidden' name='param' value='".quickGet('add_param')."'/>";
    print "<input type='hidden' name='request' value='".$request->toURL()."'/>";
    print "<input type='hidden' name='id' value='$id'/>";
    print "</td></tr>";
    print "</table></form>";
}

// display the request in detail
if (!$request->isEmpty()) {
    print "<hr/>";
    print "<h3>"._T("The request is : ", "dyngroup")."</h3>";
    $request->displayReqListInfos(true, array('id'=>$id, 'target'=>$target));
}

// display action buttons in the bottom
//TODO put in class
if (!$request->isEmpty())  {
    print "<hr/>";
    print "<table>";
    print "<tr><td><a href='".
        urlStr("base/computers/display", array('id'=>$id, 'request'=>$request->toS())).
        "'>"._T("Execute", "dyngroup")."</a></td><td><a href='".
        urlStr("base/computers/save", array('id'=>$id, 'request'=>$request->toS(), 'save_type'=>0)).
        "'>"._T("Save result", "dyngroup")."</a></td><td><a href='".
        urlStr("base/computers/save", array('id'=>$id, 'request'=>$request->toS(), 'save_type'=>1)).
        "'>"._T("Save query", "dyngroup")."</a></td></tr>";
    print "</table>";
}
?>
<style>
li.delete a {
        padding: 3px 0px 5px 20px;
        margin: 0 0px 0 0px;
        background-image: url("modules/msc/graph/images/actions/delete.png");
        background-repeat: no-repeat;
        background-position: left top;
        line-height: 18px;
        text-decoration: none;
        color: #FFF;
}

</style>
