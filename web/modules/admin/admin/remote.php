<?php
/*
 * (c) 2021 Siveo, http://www.siveo.net
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

/*
Use this page to access to xmppmaster/xmppmaster/listconffile to generate ACLs for the action
*/
 unset($_GET['module']);
 unset($_GET['submod']);
 unset($_GET['action']);

 header("Location: " . urlStrRedirect("base/computers/vnc_client", $_GET));
