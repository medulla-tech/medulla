<?php
/*
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 *
 */
// modules/admin/admin/manage_entity.php
require("localSidebar.php");
require("graph/navbar.inc.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/updates/includes/updates.inc.php");


generateEntityPage(_T("Manage Updates Lists", 'updates'),
                            "ajaxUpdatesListWin",
                            $sidemenu);
?>
<script type="text/javascript">
document.addEventListener('click', function(event) {
    var link = event.target.closest('a[href]');
    if (!link) return;

    var requestUrl = new URL(link.href, window.location.href);
    if (requestUrl.searchParams.get('module') !== 'updates'
        || requestUrl.searchParams.get('submod') !== 'updates'
        || !['blackUnban', 'grayEnable'].includes(requestUrl.searchParams.get('action'))) {
        return;
    }

    event.preventDefault();
    postAction(link.href);
}, true);
</script>

