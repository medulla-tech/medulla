<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

function listPluginsServices() { return xmlCall("services.list_plugins_services"); }
function listOthersServices($filter = "") { return xmlCall("services.list_others_services", array($filter)); }
function startService($service) { return xmlCall("services.start", array($service)); }
function stopService($service) { return xmlCall("services.stop", array($service)); }
function restartService($service) { return xmlCall("services.restart", array($service)); }
function reloadService($service) { return xmlCall("services.reload", array($service)); }
function statusService($service) { return xmlCall("services.status", array($service)); }
function servicesLog($service = "", $filter = "") { return xmlCall("services.log", array($service, $filter)); }
function serverPoweroff() { return xmlCall("services.server_power_off", array()); }
function serverReboot() { return xmlCall("services.server_reboot", array()); }

?>
