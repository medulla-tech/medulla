<?

/*
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
 * along with MMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */

require("localSidebar.php");
require("graph/navbar.inc.php");

$id = $_GET['itemid'];

$menu = array(
    array('Start computer', 'Boot on system hard drive', true, true, true, true),
    array('Create rescue image', 'Backup system hard drive', "", true, "", true),
    array('Create master', 'Backup system hard drive as a master', "", true, "", true)
);

if(count($_POST) == 0) {
            
    // get current values
    $label = $menu[$id][0];
    if($menu[$id][2] == true)
        $is_selected = 'CHECKED';
    if($menu[$id][3] == true)
        $is_displayed = 'CHECKED';
    if($menu[$id][4] == true)
        $is_wol_selected = 'CHECKED';
    if($menu[$id][5] == true)
        $is_wol_displayed = 'CHECKED';
    
    
    $p = new PageGenerator(_T("Edit : ", "imaging").$label);
    $sidemenu->forceActiveItem("bootmenu");
    $p->setSideMenu($sidemenu);
    $p->display();
    
    $f = new ValidatingForm();
    $f->push(new Table());      
    $f->add(
        new TrFormElement(_T("Selected by default", "imaging"), 
        new CheckboxTpl("selected")),
        array("value" => $is_selected)
    );
    $f->add(
        new TrFormElement(_T("Displayed", "imaging"), 
        new CheckboxTpl("displayed")),
        array("value" => $is_displayed)
    );
    $f->add(
        new TrFormElement(_T("Selected by default on WOL", "imaging"), 
        new CheckboxTpl("wol_selected")),
        array("value" => $is_wol_selected)
    );
    $f->add(
        new TrFormElement(_T("Displayed on WOL", "imaging"), 
        new CheckboxTpl("wol_displayed")),
        array("value" => $is_wol_displayed)
    );    
    $f->pop();
    $f->addButton("bvalid", _T("Validate"));
    $f->pop();
    $f->display();
}
else {
    // set new values
    foreach($_POST as $key => $value) {
    
    }
    // goto menu boot list
    header("Location: " . urlStrRedirect("imaging/manage/bootmenu"));
}   


?>
