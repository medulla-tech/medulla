<?php
/*
 * (c) 2016-2023 Siveo, http://www.siveo.net
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

/**
 * Entity selector of the profile list; the choice reloads the page with the
 * location parameter.
 *
 * @param string $current "UUIDn" of the chosen entity, "" for all of them
 */
function kioskEntityFilter($current)
{
    $options = '<option value=""' . ($current === '' ? ' selected' : '') . '>'
        . htmlspecialchars(_T("All my entities", "kiosk"), ENT_QUOTES, 'UTF-8') . '</option>';
    foreach (kioskEntities() as $id => $name) {
        $uuid = 'UUID' . $id;
        $options .= '<option value="' . $uuid . '"' . ($uuid === $current ? ' selected' : '') . '>'
            . htmlspecialchars($name, ENT_QUOTES, 'UTF-8') . '</option>';
    }
    echo '<div class="entity-filter">';
    echo '<label for="entity-filter">' . htmlspecialchars(_T("Entity", "kiosk"), ENT_QUOTES, 'UTF-8') . ':</label>';
    echo '<select id="entity-filter" onchange="kioskApplyLocation(this.value)">' . $options . '</select>';
    echo '</div>';
    ?>
    <script>
    function kioskApplyLocation(value) {
        var url = new URL(window.location.href);
        if (value) {
            url.searchParams.set('location', value);
        } else {
            url.searchParams.delete('location');
        }
        window.location.href = url.toString();
    }
    </script>
    <?php
}

/**
 * Items of a package list.
 *
 * @param array $packages uuid => name
 * @return string
 */
function kioskPackageItems($packages)
{
    $html = '';
    foreach ($packages as $uuid => $name) {
        $html .= '<li data-draggable="item" data-uuid="' . htmlspecialchars((string) $uuid, ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars((string) $name, ENT_QUOTES, 'UTF-8') . '</li>';
    }
    return $html;
}

/**
 * Form row content written as is.
 */
class KioskHtmlTpl extends AbstractTpl
{
    public $html;
    public $trid;
    public $style;

    public function __construct($html)
    {
        $this->html = $html;
    }

    public function display($arrParam = array())
    {
        echo $this->html;
    }
}

/**
 * Form of the add and edit pages.
 *
 * @param array|null $profile Answer of kiosk.get_profile_by_id, null to create
 */
function kioskProfileForm($profile = null)
{
    $esc = function ($value) {
        return htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
    };
    $editing = is_array($profile);
    $entities = kioskEntities();
    $entityId = ($editing && $profile['entity_id'] !== null && $profile['entity_id'] !== '') ? intval($profile['entity_id']) : null;
    if (!$editing && count($entities) === 1) {
        $entityId = array_key_first($entities);
    }
    $source = $editing ? (string) $profile['source'] : 'entity';

    if (!isset($_SESSION['sharings'])) {
        $_SESSION['sharings'] = xmlrpc_pkgs_search_share(array("login" => $_SESSION["login"]));
    }
    $visible = xmlrpc_get_all_packages($_SESSION['login'], $_SESSION['sharings']['config']['centralizedmultiplesharing'], -1, -1, "");
    $visibleUuids = (is_array($visible) && isset($visible['datas']['uuid'])) ? $visible['datas']['uuid'] : array();

    $chosen = array();
    foreach (($editing ? $profile['packages'] : array()) as $package) {
        if (in_array($package['uuid'], $visibleUuids)) {
            $chosen[$package['uuid']] = $package['name'];
        }
    }
    $available = array();
    foreach ($visibleUuids as $row => $uuid) {
        if (!isset($chosen[$uuid]) && $visible['datas']['associateinventory'][$row] == 1) {
            $available[$uuid] = $visible['datas']['name'][$row];
        }
    }

    $f = new ValidatingForm(array("id" => "profile-form"));
    $f->options["onsubmit"] = "return kioskSubmitProfile();";

    $f->add(new SpanElement(_T("Profile information", "kiosk"), "section-title"));
    $f->push(new Table());
    $f->add(
        new TrFormElement(_T("Profile Name", "kiosk"), new InputTpl("name")),
        array("value" => $editing ? $esc($profile['name']) : "", "required" => true)
    );
    $status = new SelectItem("status");
    $status->setElements(array(_T("Active", "kiosk"), _T("Inactive", "kiosk")));
    $status->setElementsVal(array("1", "0"));
    $f->add(
        new TrFormElement(_T("Profile Status", "kiosk"), $status),
        array("value" => ($editing && !$profile['active']) ? "0" : "1", "required" => true)
    );
    $f->pop();

    $f->add(new SpanElement(_T("Scope", "kiosk"), "section-title"));
    $f->push(new Table());
    $entityLabels = array_map($esc, array_values($entities));
    $entityValues = array_map('strval', array_keys($entities));
    $entityKnown = $entityId !== null && isset($entities[$entityId]);
    if (!$entityKnown) {
        array_unshift($entityLabels, "");
        array_unshift($entityValues, "");
    }
    $entitySelect = new SelectItem("entity_id");
    $entitySelect->setElements($entityLabels);
    $entitySelect->setElementsVal($entityValues);
    $f->add(
        new TrFormElement(_T("Entity", "kiosk"), $entitySelect),
        array("value" => $entityKnown ? (string) $entityId : "", "required" => true)
    );
    $sources = kioskSourceLabels();
    $sourceSelect = new SelectItem("source");
    $sourceSelect->setElements(array_map($esc, array_values($sources)));
    $sourceSelect->setElementsVal(array_keys($sources));
    $f->add(
        new TrFormElement(_T("Restriction", "kiosk"), $sourceSelect),
        array("value" => $source, "required" => true)
    );
    $search = $esc(_T("Search by name ...", "kiosk"));
    $f->add(
        new TrFormElement('<span id="ou-label"></span>', new KioskHtmlTpl(
            '<div id="ou-container" role="group" aria-labelledby="ou-label">
                <div id="ou-box">
                    <div id="ou-tools">
                        <input type="text" id="ouFilter" value="" placeholder="' . $search . '" aria-label="' . $search . '">
                        <button type="button" id="ouToggleAll"></button>
                    </div>
                    <div id="ou-tree"></div>
                </div>
                <div id="ou-users" aria-live="polite"></div>
            </div>'
        ), array("trid" => "ou-row", "style" => "display:none")),
        array("required" => true)
    );
    $f->pop();

    $f->add(new SpanElement(_T("Packages", "kiosk"), "section-title"));
    $f->add(new SpanElement(
        '<div id="packages">
            <div>
                <h3>' . $esc(_T("Available packages", "kiosk")) . '</h3>
                <input type="text" id="availableFilter" value="" placeholder="' . $search . '">
                <ol data-draggable="target" id="available-packages">' . kioskPackageItems($available) . '</ol>
            </div>
            <div>
                <h3>' . $esc(_T("Profile packages", "kiosk")) . '</h3>
                <input type="text" id="profileFilter" value="" placeholder="' . $search . '">
                <ol data-draggable="target" id="profile-packages">' . kioskPackageItems($chosen) . '</ol>
            </div>
        </div>'
    ));

    $f->addValidateButtonWithValue("bvalid", $editing ? _T("Save", "kiosk") : _T("Create", "kiosk"));
    $f->display();

    $config = array(
        "saveUrl" => urlStrRedirect("kiosk/kiosk/" . ($editing ? "ajaxEditProfile" : "ajaxAddProfile")),
        "sourcesUrl" => urlStrRedirect("kiosk/kiosk/ajaxSources"),
        "usersUrl" => urlStrRedirect("kiosk/kiosk/ajaxGetUsersForOu"),
        "listUrl" => urlStrRedirect("kiosk/kiosk/index"),
        "profile" => array(
            "id" => $editing ? intval($profile['id']) : null,
            "entity" => ($editing && $entityId !== null) ? (string) $entityId : null,
            "source" => $editing ? $source : null,
            "ous" => $editing ? array_values($profile['ous']) : array(),
        ),
        "messages" => array(
            "ouRequired" => $esc(_T("Select at least one item of the restriction.", "kiosk")),
            "noValue" => _T("Nothing found on the machines of this entity.", "kiosk"),
            "ouLabel" => _T("OUs concerned", "kiosk"),
            "groupLabel" => _T("Groups concerned", "kiosk"),
            "expandAll" => _T("Expand all", "kiosk"),
            "collapseAll" => _T("Collapse all", "kiosk"),
            "saving" => $esc(_T("Saving the profile may take a few moments.", "kiosk")),
            "failed" => $esc(_T("The profile could not be saved.", "kiosk")),
        ),
    );
    echo '<script>var kioskForm = '
        . json_encode($config, JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT)
        . ';</script>';
    echo '<script src="modules/kiosk/graph/js/packages.js"></script>';
    echo '<script src="modules/kiosk/graph/js/sources.js"></script>';
    echo '<script src="modules/kiosk/graph/js/validate.js"></script>';
}
