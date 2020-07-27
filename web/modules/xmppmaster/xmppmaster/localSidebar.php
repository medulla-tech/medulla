<?
/*
 *  (c) 2016 - 1017 siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of MMC, http://www.siveo.net
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

if (isExpertMode()){
    $sidemenu->addSideMenuItem(
        new SideMenuItem(_T("Wake on LAN","xmppmaster"), "xmppmaster", "xmppmaster", "wakeonlan")
    );

    $sidemenu->addSideMenuItem(
        new SideMenuItem(_T("List of Relays","xmppmaster"), "xmppmaster", "xmppmaster", "xmppRelaysList")
    );
}



$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("List of Uninventoried Machines","xmppmaster"), "base", "computers", "xmppMachinesList")
);

$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Custom Quick Actions","xmppmaster"), "xmppmaster", "xmppmaster", "customQA")
);
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Quick Action results","xmppmaster"), "xmppmaster", "xmppmaster", "ActionQuickGroup")
);

$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("File Manager","xmppmaster"), "xmppmaster", "xmppmaster", "filesmanagers")
);

//topology
$sidemenu->addSideMenuItem(
    new SideMenuItem(_T("Machines Topology","xmppmaster"), "xmppmaster", "xmppmaster", "topology")
);
?>
