<?

/**
 * (c) 2010 Mandriva, http://www.mandriva.com
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

require_once("modules/inventory/includes/xmlrpc.php");

require("localSidebar.php");
require("graph/navbar.inc.php");

// Loads all the params to send to the Ajax script from the HTTP parameters
$params = array();
if(isset($_POST['only_new']))
    $params["only_new"] = $_POST['only_new'];
if(isset($_POST['period']))
    $params["period"] = $_POST["period"];


// Create the page with its title and sidemenu
$p = new PageGenerator(_T("Incoming Inventories"));
$p->setSideMenu($sidemenu);

// Create a form with a list of options and a checkbox
$form = new ValidatingForm();
$form->push(new Table());

// The list of options is put in an array, and the listbox is configured with this array
$periodList = array(_T("Last week") => 7, _T("Last month")=>30, _T("Last quarter")=>90, _T("Last semester")=>180, _T("Last year")=>356);
$listbox = new SelectItem("period", "validateForm");
$listbox->setElements(array_keys($periodList));
$listbox->setElementsVal(array_values($periodList));
// Check the value to put by default in the list
if(isset($_POST['period']))
    $listbox->setSelected($_POST['period']);
else
    $listbox->setSelected(7); // must match with the default value in ajaxIncoming.php (7 for a week here)

// Put the element in a Tr elemet to align it
$listboxTr = new TrFormElement(_T("Period"), $listbox);

// Create a checkbox element
$checkbox = new CheckboxTpl("only_new", null, "validateForm");

$checkboxTr = new TrFormElement(_T("Only new computers"), $checkbox,
                                array("tooltip"=>_T("Load only the computers which were new when the inventory was made")));

$form->add($listboxTr);
$form->add($checkboxTr,
           array("value" => isset($_POST["only_new"]) ? "checked" : ""));

$form->pop();
// Display the form
$form->display();

// Create the Ajax filter
$ajax = new AjaxFilter(urlStrRedirect("inventory/inventory/ajaxIncoming"), "container", $params);
// Call this Ajax updater every 10sec
//$ajax->setRefresh(10000);
// Display the AjaxFilter
$ajax->display();

// Display the PageGenerator
$p->display();

// Display the DIV container that will be updated
$ajax->displayDivToUpdate();

// Insert a script to valid the form with javascript on change
?>
<script type="text/javascript">
function validateForm()
{
    document.getElementById("edit").submit();
}
</script>
