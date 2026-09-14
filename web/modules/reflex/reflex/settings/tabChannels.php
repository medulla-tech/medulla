<?php
/*
 * (c) 2026 Medulla, http://www.medulla-tech.io
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
 * Reflex Module - Settings Tab: Notification Channels
 */

require_once("modules/reflex/includes/xmlrpc.php");
require_once("modules/reflex/includes/html.inc.php");
?>

<h3><?php echo _T("Notification channels", "reflex"); ?></h3>
<div class="filters-row">
    <div class="filters-left">
        <a class="btnPrimary reflex-action-link reflex-action-create"
           href="<?php echo urlStrRedirect("reflex/reflex/channelEdit"); ?>">
            <?php echo _T("New channel", "reflex"); ?>
        </a>
    </div>
    <div class="search-wrapper">
    <?php
    $ajax = new AjaxFilter(
        urlStrRedirect("reflex/reflex/ajaxChannelsList"),
        "containerReflexChannels",
        array(),
        "searchReflexChannel"
    );
    $ajax->display();
    ?>
    </div>
</div>

<?php
$ajax->displayDivToUpdate();
?>
