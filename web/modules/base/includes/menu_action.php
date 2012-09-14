<?

/**
 * (c) 2012 Mandriva, http://www.mandriva.com
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

$prev_selected = "";

if (isset($_POST['menuAction'])){
    $action = $_POST['menuAction'];
    $paramArray = array('cn' => $_GET['cn'], 'objectUUID' => $_GET['objectUUID']);

    $redirect_url = urlStrRedirect('base/computers/invtabs', $paramArray); 

    if ($action=="vnc_client")
    {
	$quote = "'";
	$args = "'event',".$quote.urlStrRedirect("base/computers/vnc_client", $paramArray)."&mod=".$quote.", '300'";
	$fnc = "PopupWindow(".$args."); return false;";
	echo '<script type="text/javascript">'.$fnc.'</script>'; 
	$prev_selected = $selected;

    }
    else
    {
	header("Location: ".urlStrRedirect('base/computers/'.$action.'tabs', $paramArray));
	exit;    
    }
}
    
$frm = new ValidatingForm();

$listActions = array(_T("Imaging")=>"img",_T("Inventory")=>"inv",_T("Deployment")=>"msc",_T("Remote Control")=>"vnc_client");
$listBox = new SelectItem("menuAction","validateForm");
$listBox->setElements(array_keys($listActions));
$listBox->setElementsVal(array_values($listActions));

if ($prev_selected != "")
    $listBox->setSelected($prev_selected);
elseif(isset($_POST['menuAction']))
    $listBox->setSelected($_POST['menuAction']);
else
    $listBox->setSelected($selected);

$frm->add($listBox);
$frm->pop();
echo '<div style="float: right">';
$frm->display();
echo '</div>';

?>
<script type="text/javascript">
function validateForm()
{
    document.getElementById("edit").submit();
}
</script>

