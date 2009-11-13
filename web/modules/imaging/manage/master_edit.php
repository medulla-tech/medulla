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

$masters = array(
    array('MDV 2008.0', 'Mandriva 2008 Master', '2009-02-25 17:38', '1GB', true),
    array('MDV 2009.0', 'Mandriva 2009 Master', '2009-02-25 17:38', '1GB', false),
    array('MDV 2010.0', 'Mandriva 2010 Master', '2009-02-25 17:38', '1GB', false),
);

$id = $_GET['itemid'];

if(count($_POST) == 0) {
            
    // get current values
    $label = $masters[$id][0];    
    $desc = $masters[$id][1];
    if($masters[$id][4] == 'yes')
        $in_bootmenu = 'CHECKED';
        
    $p = new PageGenerator(_T("Edit master : ", "imaging").$label);
    $sidemenu->forceActiveItem("master");
    $p->setSideMenu($sidemenu);
    $p->display();
    
    $f = new ValidatingForm();
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Label", "imaging"), new InputTpl("image_label")),
        array("value" => $label)
    );
    $f->add(
        new TrFormElement(_T("Description", "imaging"), new InputTpl("image_description")),
        array("value" => $desc)
    );
    $postInstall = new SelectItem("post_install");
    $postInstall->setElements(
        array("none" => "No post-installation script", "sysprep1" => "Sysprep sur la première partition"));
    $postInstall->setElementsVal(
        array("none" => "none", "sysprep1" => "sysprep1"));
    // set selected
    // ...
    $f->add(
        new TrFormElement(_T("Post-installation script", "imaging"), $postInstall)
    );
    $f->add(
        new TrFormElement(_T("In default bootmenu", "imaging"), 
        new CheckboxTpl("bootmenu")),
        array("value" => $in_bootmenu)
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
    $label = $_POST['image_label'];
    // goto menu boot list
    $str = sprintf(_T("Master <strong>%s</strong> modified with success", "imaging"), $label);
    new NotifyWidgetSuccess($str);
    header("Location: " . urlStrRedirect("imaging/manage/master"));
} 

?>
