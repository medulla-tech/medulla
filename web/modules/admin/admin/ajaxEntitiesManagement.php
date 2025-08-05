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
require_once("modules/xmppmaster/includes/html.inc.php");
?>

<style>
    #container>form>table>thead td:first-child span {
        display: block;
        text-align: left;
        padding-left: 0 !important;
        margin-left: 0 !important;
    }

    #container>form>table>thead td:last-child span {
        display: block;
        text-align: right;
        padding-right: 50px;
    }
</style>

<?php
list($list, $values) = getEntitiesSelectableElements();
$titles = array_values($list);

$types = [
    "École",
    "Entreprise",
    "Collectivité"
];

$usersCount = [
    "5 utilisateurs",
    "12 utilisateurs",
    "3 utilisateurs"
];

$created = [
    "2024-01-15",
    "2023-11-03",
    "2025-02-28"
];

$edit = new ActionItem(_("Edit"), "editEntities", "edit", "", "admin", "admin");
$add = new ActionItem(_("Add"), "editEntities", "add", "", "admin", "admin");
$view = new ActionItem(_("View"), "manageentity", "display", "", "admin", "admin");
$download = new ActionItem(_("Download"), "manageentity", "down", "", "admin", "admin");

$params = [];

for ($i = 0; $i < count($titles); $i++) {
    $editAction[] = $edit;
    $addAction[] = $add;
    $viewAction[] = $view;
    $downloadAction[] = $download;

    $params[] = [
        'entity_id' => array_keys($values)[$i],
        'entity_name' => $titles[$i],
    ];
}

$filter = "";

$n = new OptimizedListInfos($titles, "Liste des entités");
$n->setNavBar(new AjaxNavBar("10", $filter));
$n->setCssClass("package");
$n->disableFirstColumnActionLink();

$n->addExtraInfo($types, "Type");
$n->addExtraInfo($usersCount, "Utilisateurs");
$n->addExtraInfo($created, "Créée le");

$n->addActionItemArray($editAction);
$n->addActionItemArray($addAction);
$n->addActionItemArray($viewAction);
$n->addActionItemArray($downloadAction);
$n->setParamInfo($params);
$n->display();
?>
<script>
jQuery(document).ready(function($) {
    $('li.edit a, li.add a').on('click', function(e) {
        const $link = $(this);
        let href = $link.attr('href');

        if (href.includes('mode=')) return;

        let mode = '';
        if ($link.closest('li').hasClass('edit')) {
            mode = 'edit';
        } else if ($link.closest('li').hasClass('add')) {
            mode = 'add';
        }

        const separator = href.includes('?') ? '&' : '?';
        href += separator + 'mode=' + mode;

        window.location.href = href;
        e.preventDefault();
    });
});
</script>