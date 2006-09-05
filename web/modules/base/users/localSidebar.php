<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?
if ($_SESSION["login"]!='root') {

$sidebar = array("class" => "users",
                 "content" => array(array("id" => "global",
                                    "text" => _("List"),
                                    "link" => "main.php?module=base&submod=users&action=index"),
                              array("id" => "addUser",
                                    "text" => _("Add"),
                                    "link" => "main.php?module=base&submod=users&action=add"),
			      array("id" => "changePasswd",
                                    "text" => _("Change your password"),
                                    "link" => "main.php?module=base&submod=users&action=passwd")));
} else {

$sidebar = array("class" => "users",
                 "content" => array(array("id" => "global",
                                    "text" => _("List"),
                                    "link" => "main.php?module=base&submod=users&action=index"),
                              array("id" => "addUser",
                                    "text" => _("Add"),
                                    "link" => "main.php?module=base&submod=users&action=add"),
			      ));


}
?>
