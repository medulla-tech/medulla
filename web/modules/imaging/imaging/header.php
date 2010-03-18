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

global $stateid;
global $SYNCHROSTATE_TODO;

if ($stateid == $SYNCHROSTATE_TODO) {
    print "<table><tr><td><font color='red'><b>";
    print _T('This target has been modified, when you are done, please press on "Synchronize" so that modifications are updated on the Imaging server.', 'imaging');
    print "</b></font></td><td>";

    $f = new ValidatingForm();
    $f->addButton("bsync", _T("Synchronize", "imaging"));
    $f->display();
    print "</td></tr></table>";
} elseif (($_GET['tab'] == 'tabbootmenu' || $_GET['tab'] == 'grouptabbootmenu') && isExpertMode()) {
    print "<table><tr><td>";
    print _T('Click on "Force synchronize" if you want to force the synchronization', 'imaging');
    print "</td><td>";
    $f = new ValidatingForm();
    $f->addButton("bsync", _T("Force synchronize", "imaging"));
    $f->display();
    print "</td></tr></table>";
}
?>
