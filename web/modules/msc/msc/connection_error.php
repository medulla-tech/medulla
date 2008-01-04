<?php
/*
 * Linbox Rescue Server - Secure Remote Control Module
 * Copyright (C) 2005  Linbox FAS
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of the GNU General Public License
 * as published by the Free Software Foundation; either version 2
 * of the License, or (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, US
 */

require_once("modules/msc/includes/widgets/html.php");

// Display host informations
$label = new RenderedLabel(3, _T('Remote control of :', 'msc'));
$label->display();

$msc_host = new RenderedMSCHost(
    $_GET["mac"],
    $session,
    (MSC_sysPing($session->ip)==0),
    'msc/msc/general'
);
$msc_host->display();

?>
