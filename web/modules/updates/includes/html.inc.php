<?php
// SPDX-FileCopyrightText: 2024 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2026 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/includes/html.inc.php

require_once("modules/updates/includes/xmlrpc.php");
require_once("modules/xmppmaster/includes/xmlrpc.php");
require_once("modules/medulla_server/includes/utilities.php");
require_once("modules/medulla_server/includes/locations_xmlrpc.inc.php");

/* ===== Composants ===== */

/**
 * Filter and pagination of a list view, read from the request.
 *
 * @return array [filter, start, maxperpage]
 */
function updatesListParams()
{
    global $conf;
    $filter = isset($_GET['filter']) ? trim((string) $_GET['filter']) : "";
    $start = (isset($_GET['start']) && is_numeric($_GET['start'])) ? max(0, (int) $_GET['start']) : 0;
    $maxperpage = (isset($_GET['maxperpage']) && is_numeric($_GET['maxperpage']) && (int) $_GET['maxperpage'] > 0)
        ? (int) $_GET['maxperpage']
        : (int) $conf["global"]["maxperpage"];
    return array($filter, $start, $maxperpage);
}

/**
 * Tabs of the current page the user may see; a missing or hidden requested tab
 * falls back on the first visible one in $_GET['tab'].
 *
 * @param array $tabs tab id => array(label, file)
 * @return array Visible tabs, same shape
 */
function updatesVisibleTabs($tabs)
{
    $visible = array();
    foreach ($tabs as $tabId => $tab) {
        if (hasCorrectTabAcl($_GET["module"], $_GET["submod"], $_GET["action"], $tabId)) {
            $visible[$tabId] = $tab;
        }
    }
    if (!empty($visible) && (!isset($_GET["tab"]) || !isset($visible[$_GET["tab"]]))) {
        $_GET["tab"] = array_key_first($visible);
    }
    return $visible;
}

/**
 * Page with tabs.
 *
 * @param array $tabs   tab id => array(label, file), from updatesVisibleTabs()
 * @param array $params URL parameters of the tabs
 */
function updatesTabbedPage($tabs, $params = array())
{
    $p = new TabbedPageGenerator();
    foreach ($tabs as $tabId => $tab) {
        $p->addTab($tabId, $tab['label'], "", $tab['file'], $params);
    }
    $p->display();
}

/**
 * Error code of an XML-RPC answer.
 *
 * @param mixed  $result
 * @param string $default Value when the answer carries no usable code
 * @return string
 */
function updatesResultError($result, $default = '')
{
    return is_array($result) && is_scalar($result['error'] ?? null) ? trim((string) $result['error']) : $default;
}

/**
 * Whether a jid received from the request is usable.
 *
 * @param string $jid
 * @return bool
 */
function updatesJidValid($jid)
{
    return $jid !== '' && strlen($jid) <= 255 && !preg_match('/\s/', $jid);
}

/**
 * Popup with a message and a cancel button.
 *
 * @param string $title
 * @param string $text HTML
 */
function updatesMessagePopup($title, $text)
{
    $f = new PopupForm($title);
    $f->addText($text);
    $f->addCancelButton("bback");
    $f->display();
}

/**
 * Confirmation popup.
 *
 * @param string $title
 * @param string ...$texts HTML
 */
function updatesConfirmPopup($title, ...$texts)
{
    $f = new PopupForm($title);
    foreach ($texts as $text) {
        $f->addText($text);
    }
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

/**
 * Popup d'une lecture impossible.
 *
 * @param string $title Titre de la popup
 */
function updatesReadFailedPopup($title)
{
    updatesMessagePopup($title, htmlspecialchars(_T("Read failed", "updates"), ENT_QUOTES, 'UTF-8'));
}

/**
 * Popup d'une action impossible sur une entite que l'utilisateur ne voit pas.
 *
 * @param string $title Titre de la popup
 */
function updatesUnknownEntityPopup($title)
{
    updatesMessagePopup($title, _T("Unknown entity.", "updates"));
}

/**
 * Popup of an unknown or refused group.
 *
 * @param string $title
 */
function updatesUnknownGroupPopup($title)
{
    updatesMessagePopup($title, _T("Unknown group.", "updates"));
}

/* ===== Module ===== */

/**
 * Numero du KB (chiffres seuls) ou chaine vide si la valeur n'est pas un KB.
 */
function updatesKbNumber($value)
{
    $value = trim((string) $value);
    if (strncasecmp($value, 'KB', 2) === 0) {
        $value = substr($value, 2);
    }
    return ($value !== '' && ctype_digit($value)) ? $value : '';
}

/**
 * Cellule KB : lien vers l'article Microsoft, ou tiret.
 */
function updatesKbCell($value, $icon = '')
{
    $number = updatesKbNumber($value);
    if ($number === '') {
        $cell = '<span class="cell-empty">-</span>';
    } else {
        $url = 'https://support.microsoft.com/help/' . $number;
        $tooltip = _T("Open the Microsoft article", "updates");
        $cell = '<a href="' . htmlspecialchars($url, ENT_QUOTES, 'UTF-8') . '"'
            . ' target="_blank" rel="noopener noreferrer"'
            . ' title="' . htmlspecialchars($tooltip, ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars('KB' . $number, ENT_QUOTES, 'UTF-8') . '</a>';
    }
    return ($icon !== '') ? '<span class="updates-nowrap">' . $cell . $icon . '</span>' : $cell;
}

/**
 * Cellule titre echappee, sans le "(KBnnnn)" de la ligne.
 */
function updatesTitleCell($title, $kb, $tooltip = '')
{
    $title = (string) $title;
    $number = updatesKbNumber($kb);
    if ($number !== '') {
        $title = str_ireplace('(KB' . $number . ')', '', $title);
        $title = implode(' ', array_filter(explode(' ', $title), 'strlen'));
    }
    $safe = htmlspecialchars($title, ENT_QUOTES, 'UTF-8');
    $titleAttr = ($tooltip !== '') ? $safe . "\n" . htmlspecialchars($tooltip, ENT_QUOTES, 'UTF-8') : $safe;
    return '<span class="cell-text" title="' . $titleAttr . '">' . $safe . '</span>';
}

/**
 * Nom court d'une mise a jour pour les popups et les messages : KBnnnn, sinon
 * le titre sans "(KBnnnn)" ni numero de build final entre parentheses.
 *
 * @return string Texte non echappe
 */
function updatesUpdateLabel($title, $kb)
{
    $number = updatesKbNumber($kb);
    if ($number !== '') {
        return 'KB' . $number;
    }
    $title = trim((string) $title);
    $open = stripos($title, '(KB');
    $close = ($open !== false) ? strpos($title, ')', $open) : false;
    if ($close !== false && updatesKbNumber(substr($title, $open + 1, $close - $open - 1)) !== '') {
        $title = trim(substr($title, 0, $open) . substr($title, $close + 1));
    }
    $open = strrpos($title, '(');
    if ($open !== false && substr($title, -1) === ')') {
        $build = str_replace('.', '', substr($title, $open + 1, -1));
        if ($build !== '' && ctype_digit($build)) {
            $title = rtrim(substr($title, 0, $open));
        }
    }
    return implode(' ', array_filter(explode(' ', $title), 'strlen'));
}

/**
 * Phrase de popup ou de message : les valeurs sont echappees, le gras vient
 * de la chaine traduite.
 *
 * @param string $format Chaine traduite
 * @return string HTML
 */
function updatesActionText($format, ...$values)
{
    foreach ($values as $i => $value) {
        $values[$i] = is_int($value) ? $value : htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
    }
    return vsprintf($format, $values);
}

/**
 * Libelle traduit d'une classification ou d'une severite du catalogue Microsoft, echappe.
 */
function updatesCatalogLabel($value)
{
    return htmlspecialchars(updatesCatalogText($value), ENT_QUOTES, 'UTF-8');
}

/**
 * Libelle traduit d'une classification ou d'une severite du catalogue Microsoft, non echappe.
 */
function updatesCatalogText($value)
{
    static $labels = null;
    if ($labels === null) {
        $labels = [
            'Critical Updates'   => _T("Critical Updates", "updates"),
            'Security Updates'   => _T("Security Updates", "updates"),
            'Definition Updates' => _T("Definition Updates", "updates"),
            'Service Packs'      => _T("Service Packs", "updates"),
            'Update Rollups'     => _T("Update Rollups", "updates"),
            'Updates'            => _T("Updates", "updates"),
            'Feature Packs'      => _T("Feature Packs", "updates"),
            'Tools'              => _T("Tools", "updates"),
            'Drivers'            => _T("Drivers", "updates"),
            'Upgrades'           => _T("Upgrades", "updates"),
            'Critical'           => _T("Critical", "updates"),
            'Important'          => _T("Important", "updates"),
            'Moderate'           => _T("Moderate", "updates"),
            'Low'                => _T("Low", "updates"),
        ];
    }
    $value = trim((string) $value);
    return $labels[$value] ?? $value;
}

/**
 * Entite demandee par le parametre location, si l'utilisateur la voit.
 *
 * @return array|null Entree de getUserLocations(), null pour toutes les entites
 */
function updatesSelectedEntity()
{
    return updatesEntityByUuid($_GET['location'] ?? '');
}

/**
 * Retient l'entite choisie, relue par les pages a entite unique
 * (updatesWinProductsEntity). « Toutes mes entites » (switch sans location) est
 * retenu aussi. Le choix ne vaut que tant que la page precedente etait dans le
 * module.
 */
function updatesRememberEntity()
{
    if (isset($_GET['location'])) {
        if (updatesEntityByUuid($_GET['location'])) {
            $_SESSION['updates_entity'] = $_GET['location'];
        }
        return;
    }
    if (!empty($_GET['switch'])) {
        $_SESSION['updates_entity'] = '';
        return;
    }
    $referer = parse_url((string) ($_SERVER['HTTP_REFERER'] ?? ''));
    $query = array();
    parse_str((string) ($referer['query'] ?? ''), $query);
    $sameHost = isset($referer['host'])
        && strcasecmp($referer['host'], (string) parse_url('http://' . ($_SERVER['HTTP_HOST'] ?? ''), PHP_URL_HOST)) === 0;
    if (!$sameHost || ($query['module'] ?? null) !== 'updates') {
        unset($_SESSION['updates_entity']);
    }
}

/**
 * Entree de getUserLocations() d'un UUID, si l'utilisateur voit l'entite.
 *
 * @param mixed $uuid UUIDn
 * @return array|null
 */
function updatesEntityByUuid($uuid)
{
    if (!is_string($uuid) || !preg_match('/^UUID\d+$/', $uuid)) {
        return null;
    }
    foreach (getUserLocations() as $location) {
        if (($location['uuid'] ?? null) === $uuid) {
            return $location;
        }
    }
    return null;
}

/**
 * Identifiant GLPI d'une entree de getUserLocations().
 *
 * @param array $entity
 * @return int
 */
function updatesEntityId($entity)
{
    return intval(substr((string) $entity['uuid'], 4));
}

/**
 * Nom affiche d'une entree de getUserLocations().
 *
 * @param array $entity
 * @return string
 */
function updatesEntityName($entity)
{
    return (string) ($entity['completename'] ?? $entity['name'] ?? $entity['uuid']);
}

/**
 * Reponse de lecture inexploitable : le backend a intercepte une erreur.
 *
 * @param mixed $result Reponse XML-RPC
 * @return bool
 */
function updatesReadFailed($result)
{
    return !is_array($result) || !empty($result['error']);
}

/**
 * Etat d'une lecture impossible : ni vide ni a jour, on ne sait pas.
 */
function updatesReadFailedBox()
{
    EmptyStateBox::show(_T("Read failed", "updates"));
}

/**
 * Vue AJAX refusee sans l'ACL de sa page (les vues AJAX n'ont pas d'ACL propre) ;
 * affiche alors l'etat de refus.
 *
 * @param string $page  Page qui porte la vue
 * @param string $tabId Onglet de la page, "" sans ACL d'onglet
 * @return bool
 */
function updatesAjaxDenied($page, $tabId = '')
{
    if (hasCorrectAcl("updates", "updates", $page)
        && ($tabId === '' || hasCorrectTabAcl("updates", "updates", $page, $tabId))) {
        return false;
    }
    EmptyStateBox::show(_T("You are not allowed to see this list.", "updates"));
    return true;
}

/**
 * Selecteur d'entite ; le choix recharge la page avec le parametre location.
 *
 * @param array|null $entity   Entite choisie (updatesSelectedEntity)
 * @param bool       $allowAll Offer the "All my entities" choice
 * @param string     $aside    HTML shown right of the list (updatesWinInheritanceLine)
 */
function updatesEntitySelect($entity, $allowAll = true, $aside = '')
{
    echo '<div class="entity-filter">';
    echo '<label for="entity-filter">' . htmlspecialchars(_T("Entity", "updates")) . ':</label>';
    updatesEntitySelectField($entity, $allowAll, $aside);
    echo '</div>';
}

/**
 * Liste deroulante d'entite seule, sans libelle ; sans attribut name, elle
 * n'est jamais soumise avec un formulaire englobant.
 *
 * @param array|null $entity   Entite choisie (updatesSelectedEntity)
 * @param bool       $allowAll Offer the "All my entities" choice
 * @param string     $aside    HTML shown right of the list (updatesWinInheritanceLine)
 */
function updatesEntitySelectField($entity, $allowAll = true, $aside = '')
{
    list($labels, $values) = getEntitiesSelectableElements();
    $current = $entity ? $entity['uuid'] : '';
    $options = '';
    if ($allowAll) {
        $options = '<option value=""' . ($current === '' ? ' selected' : '') . '>'
            . htmlspecialchars(_T("All my entities", "updates")) . '</option>';
    }
    foreach ($values as $uuid => $value) {
        $options .= '<option value="' . htmlspecialchars($value) . '"' . ($value === $current ? ' selected' : '') . '>'
            . htmlspecialchars($labels[$uuid]) . '</option>';
    }
    echo '<select id="entity-filter" onchange="updatesApplyLocation(this.value)">' . $options . '</select>';
    if ($aside !== '') {
        echo '<span class="updates-entity-inheritance">' . $aside . '</span>';
    }
    ?>
    <script>
    function updatesApplyLocation(value) {
        var url = new URL(window.location.href);
        url.searchParams.set('switch', '1');
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
 * Libelle traduit d'un etat de deploiement, echappe ; un etat inconnu
 * s'affiche tel quel.
 *
 * @param string $state Etat brut (ex. ABORT ON TIMEOUT)
 * @return string HTML
 */
function updatesDeployStateLabel($state)
{
    static $labels = null;
    if ($labels === null) {
        $labels = array(
            'DEPLOYMENT SUCCESS'                        => _T("Deployment Success", "updates"),
            'DEPLOYMENT PARTIAL SUCCESS'                => _T("Deployment Partial Success", "updates"),
            'UNINSTALL SUCCESS'                         => _T("Uninstall Success", "updates"),
            'DEPLOYMENT START'                          => _T("Deployment start", "updates"),
            'DEPLOYMENT PENDING (REBOOT/SHUTDOWN/...)'  => _T("Deployment Pending", "updates"),
            'DEPLOYMENT DELAYED'                        => _T("Deployment Delayed", "updates"),
            'DEPLOYMENT SPOOLED'                        => _T("Deployment Spooled", "updates"),
            'DEPLOYMENT SYNCTHING'                      => _T("Deployment Syncthing", "updates"),
            'DEPLOY TASK SCHEDULED'                     => _T("Deploy Task Scheduled", "updates"),
            'WAITING MACHINE ONLINE'                    => _T("Waiting Machine Online", "updates"),
            'RESTART DEPLOY'                            => _T("Restart Deploy", "updates"),
            'ABORT ON TIMEOUT'                          => _T("Abort On Timeout", "updates"),
            'ABORT MISSING AGENT'                       => _T("Abort Missing Agent", "updates"),
            'ABORT INCONSISTENT GLPI INFORMATION'       => _T("Abort inconsistent GLPI Information", "updates"),
            'ABORT RELAY DOWN'                          => _T("Abort Relay Down", "updates"),
            'ABORT ALTERNATIVE RELAYS DOWN'             => _T("Abort Alternative relay down", "updates"),
            'ABORT INFO RELAY MISSING'                  => _T("Abort Info Relay Missing", "updates"),
            'ABORT PACKAGE IDENTIFIER MISSING'          => _T("Abort Package Identifier Missing", "updates"),
            'ABORT PACKAGE NAME MISSING'                => _T("Abort Package Name Missing", "updates"),
            'ABORT PACKAGE VERSION MISSING'             => _T("Abort Package Version Missing", "updates"),
            'ABORT PACKAGE WORKFLOW ERROR'              => _T("Abort Package Workflow Error", "updates"),
            'ABORT PACKAGE EXECUTION ERROR'             => _T("Abort Package Execution Error", "updates"),
            'ABORT PACKAGE EXECUTION CANCELLED'         => _T("Abort Package Execution Cancelled", "updates"),
            'ABORT DESCRIPTOR MISSING'                  => _T("Abort Descriptor Missing", "updates"),
            'ABORT MACHINE DISAPPEARED'                 => _T("Abort Machine Disappeared", "updates"),
            'ABORT DEPLOYMENT CANCELLED BY USER'        => _T("Abort Deployment Cancelled By User", "updates"),
            'ABORT DUPLICATE MACHINES'                  => _T("Abort Duplicate Machines", "updates"),
            'ABORT HASH INVALID'                        => _T("Abort Hash Invalid", "updates"),
            'ABORT MISSING DEPENDENCY'                  => _T("Abort Missing Dependency", "updates"),
            'ERROR UNKNOWN ERROR'                       => _T("Error Unknown Error", "updates"),
            'ERROR HASH MISSING'                        => _T("Error Hash Missing", "updates"),
            'ERROR TRANSFER FAILED'                     => _T("Error Transfer Failed", "updates"),
        );
    }
    $state = (string) $state;
    $label = $labels[strtoupper(trim($state))] ?? $state;
    return htmlspecialchars($label, ENT_QUOTES, 'UTF-8');
}

/**
 * Badge d'etat d'un deploiement.
 *
 * @param string $state
 * @param mixed  $failure Cause de l'echec, disk_full seul est connu
 * @return string HTML
 */
function updatesDeployStateBadge($state, $failure = '')
{
    $state = (string) $state;
    if (preg_match('#success#i', $state)) {
        $class = 'status-badge-success';
    } elseif (preg_match('#^abort#i', $state)) {
        $class = 'status-badge-abort';
    } elseif (preg_match('#^error#i', $state)) {
        $class = 'status-badge-error';
    } elseif (preg_match('#pending#i', $state)) {
        $class = 'status-badge-pending';
    } elseif (preg_match('#start#i', $state)) {
        $class = 'status-badge-start';
    } else {
        $class = 'status-badge-other';
    }
    $failed = ($class === 'status-badge-abort' || $class === 'status-badge-error');
    $tooltip = ($failed && $failure === 'disk_full')
        ? ' updates-tooltip" aria-label="' . htmlspecialchars(_T("Not enough free space on the machine", "updates"), ENT_QUOTES, 'UTF-8')
        : '';
    return '<span class="status-badge ' . $class . $tooltip . '">' . updatesDeployStateLabel($state) . '</span>';
}

/**
 * Parametres de la page de journal d'un deploiement : ses valeurs scalaires ou
 * nulles, sous leurs noms (viewlogs fait un extract de $_GET).
 *
 * @param array $deployment
 * @return array
 */
function updatesDeployLogParams($deployment)
{
    return array_filter($deployment, function ($value) {
        return $value === null || is_scalar($value);
    });
}

/**
 * Etat vide d'une liste de machines, neutre quand une recherche est active.
 *
 * @param OptimizedListInfos $list
 * @param string             $search      Recherche de la liste
 * @param string             $title       Titre sans recherche
 * @param string             $description Description sans recherche
 */
function updatesMachinesEmptyState($list, $search, $title, $description = '')
{
    if (trim((string) $search) !== '') {
        $list->setEmptyState(_T("No machines found", "updates"), _T("No machine matches the search.", "updates"));
    } else {
        $list->setEmptyState($title, $description);
    }
}

/**
 * Fait du compteur d'une carte le lien qui cree, apres confirmation, un groupe
 * des machines qu'elle compte. Sans machine ou sans le droit de creer un groupe,
 * le compteur reste un simple chiffre.
 *
 * @param array      $options      Options de StatCards::addCard, completees
 * @param string     $screen       Ecran (updatesGroupScreens)
 * @param string     $tabId        Onglet de l'ecran
 * @param string     $category     Carte de l'ecran
 * @param array|null $entity       Entite de l'onglet, null pour toutes
 * @param int        $count        Valeur de la carte
 * @param string     $distribution Distribution Linux de l'ecran, "" pour toutes
 */
function updatesGroupCardLink(&$options, $screen, $tabId, $category, $entity, $count, $distribution = '')
{
    $count = intval($count);
    if ($count <= 0 || !hasCorrectAcl("base", "computers", "computersgroupcreator")) {
        return;
    }
    $group = array(
        'screen'   => $screen,
        'tab'      => $tabId,
        'category' => $category,
    );
    if ($entity) {
        $group['location'] = $entity['uuid'];
    }
    if ($distribution !== '') {
        $group['distribution'] = $distribution;
    }
    $onclick = "PopupWindow(event, " . json_encode(urlStrRedirect("updates/updates/ajaxUpdateCreateGroup", $group)) . ", 400); return false;";
    $options['link_html'] = '<a href="#" onclick="' . htmlspecialchars($onclick, ENT_QUOTES, 'UTF-8') . '">' . $count . '</a>';
}

/**
 * Ecrans dont les cartes proposent de creer un groupe.
 *
 * @return array ecran => array(page : page et ACL d'onglet, tabs, categories)
 */
function updatesGroupScreens()
{
    return array(
        'upgrade' => array('page' => "MajorEntitiesList", 'tabs' => updatesUpgradeTabs(),
                           'categories' => updatesUpgradeGroupCategories()),
        'status'  => array('page' => "EntityComplianceos", 'tabs' => updatesStatusTabs(),
                           'categories' => updatesStatusGroupCategories()),
    );
}

/**
 * Carte demandee pour creer un groupe : ecran, onglet visible par l'utilisateur,
 * categorie et distribution Linux, tous sur liste fermee.
 *
 * @return array|null array(screen, system, category, distribution, what, tabLabel, categoryLabel, back)
 */
function updatesGroupRequest()
{
    $screenId = is_string($_GET['screen'] ?? null) ? $_GET['screen'] : '';
    $tabId = is_string($_GET['tab'] ?? null) ? $_GET['tab'] : '';
    $category = is_string($_GET['category'] ?? null) ? $_GET['category'] : '';
    $screens = updatesGroupScreens();
    if (!isset($screens[$screenId])) {
        return null;
    }
    $tabs = $screens[$screenId]['tabs'];
    $categories = $screens[$screenId]['categories'];
    $page = $screens[$screenId]['page'];
    if (!isset($tabs[$tabId], $categories[$category])
        || !hasCorrectTabAcl("updates", "updates", $page, $tabId)) {
        return null;
    }
    $entity = updatesSelectedEntity();
    $back = array('tab' => $tabId);
    if ($entity) {
        $back['location'] = $entity['uuid'];
    }
    $distribution = '';
    if ($screenId === 'status' && $tabs[$tabId]['system'] === 'linux' && is_string($_GET['distribution'] ?? null)) {
        $distribution = $_GET['distribution'];
    }
    if ($distribution !== '') {
        if (!isset(updatesLinuxDistributions($entity)[$distribution])) {
            return null;
        }
        $back['distribution'] = $distribution;
    }
    return array('screen' => $screenId, 'system' => $tabs[$tabId]['system'], 'category' => $category,
                 'distribution' => $distribution, 'what' => $categories[$category]['what'],
                 'tabLabel' => $tabs[$tabId]['label'], 'categoryLabel' => $categories[$category]['label'],
                 'back' => urlStrRedirect("updates/updates/" . $page, $back));
}

/**
 * Machines de la carte demandee, lues comme son compteur.
 *
 * @param array|null $entity Entite de la carte, null pour toutes
 * @return array array(machines {uuid: {hostname, uuid}}, message d'erreur ou null)
 */
function updatesGroupMachines($entity)
{
    $machines = array();
    $request = updatesGroupRequest();
    if ($request !== null) {
        $location = $entity ? array(updatesEntityId($entity)) : array();
        $result = ($request['screen'] === 'status')
            ? xmlrpc_get_windows_machines($location, 0, -1, "", $request['system'], $request['distribution'], $request['category'])
            : xmlrpc_get_upgrade_machine_list($location, 0, -1, "", $request['category'], $request['system']);
        if (updatesReadFailed($result)) {
            return array(array(), _T("Read failed", "updates"));
        }
        foreach ((is_array($result) && is_array($result['rows'] ?? null)) ? $result['rows'] : array() as $row) {
            $uuid = is_array($row) ? trim((string) ($row['glpi_uuid'] ?? '')) : '';
            if ($uuid !== '') {
                $machines[$uuid] = array('hostname' => (string) ($row['hostname'] ?? ''), 'uuid' => $uuid);
            }
        }
    }
    if (empty($machines)) {
        return array(array(), _T("No machine matches these criteria.", "updates"));
    }
    return array($machines, null);
}

/**
 * Lien vers la page de detail Windows d'une machine.
 *
 * @param string $name Nom affiche
 * @param mixed  $jid  JID de la machine ; vide = sans lien
 * @param array|null $entity Entite de la liste d'origine, pour le retour de la fiche
 * @return string HTML
 */
function updatesMachineLink($name, $jid, $entity = null)
{
    $safe = htmlspecialchars((string) $name);
    $jid = trim((string) $jid);
    if ($jid === '' || !hasCorrectAcl("updates", "updates", "detailsMachineWin")) {
        return $safe;
    }
    $params = array('jid' => $jid);
    if ($entity) {
        $params['location'] = $entity['uuid'];
    }
    return '<a href="' . htmlspecialchars(urlStrRedirect("updates/updates/detailsMachineWin", $params)) . '">' . $safe . '</a>';
}

/**
 * Onglets d'une page par systeme, dans l'ordre d'affichage.
 * Les identifiants servent aux ACL d'onglet : ne pas les renommer.
 *
 * @param string $folder Dossier de la page sous modules/updates/updates
 * @return array id d'onglet => array(label, file, system)
 */
function updatesSystemTabs($folder)
{
    return array(
        'tabwin' => array('label' => _T("Windows", "updates"), 'system' => 'windows',
                          'file' => "modules/updates/updates/" . $folder . "/osWindows.php"),
        'tablinux' => array('label' => _T("Linux", "updates"), 'system' => 'linux',
                            'file' => "modules/updates/updates/" . $folder . "/osLinux.php"),
    );
}

/**
 * Onglets de la page des mises a niveau.
 *
 * @return array id d'onglet => array(label, file, system)
 */
function updatesUpgradeTabs()
{
    return updatesSystemTabs("major");
}

/**
 * Onglet de mise a niveau demande par le parametre tab, Windows par defaut.
 *
 * @return string Identifiant d'onglet (updatesUpgradeTabs)
 */
function updatesUpgradeRequestTab()
{
    $tabId = is_string($_GET['tab'] ?? null) ? $_GET['tab'] : '';
    return isset(updatesUpgradeTabs()[$tabId]) ? $tabId : 'tabwin';
}

/**
 * Onglets de la page de l'etat des mises a jour.
 *
 * @return array id d'onglet => array(label, file, system)
 */
function updatesStatusTabs()
{
    return updatesSystemTabs("entity");
}

/**
 * Cartes de l'etat des mises a jour qui proposent de creer un groupe : la cle
 * est un filtre de get_windows_machines.
 *
 * @return array cle => array(label de la carte, what : ce qui suit « N machines »)
 */
function updatesStatusGroupCategories()
{
    return array(
        'to_update' => array('label' => _T("Machines to update", "updates"),
                             'what' => _T("to update", "updates")),
        'critical'  => array('label' => _T("Critical machines", "updates"),
                             'what' => _T("with a critical update missing", "updates")),
        'reboot_pending' => array('label' => _T("Reboot pending", "updates"),
                                  'what' => _T("waiting for a restart", "updates")),
    );
}

/**
 * Linux distributions reported in an entity (all visible ones when null), fetched once per request.
 *
 * @param array|null $entity Entry of getUserLocations()
 * @return array|null distribution => label, null when the answer is unusable
 */
function updatesLinuxDistributions($entity)
{
    static $cache = array();
    $key = $entity ? (string) updatesEntityId($entity) : '';
    if (array_key_exists($key, $cache)) {
        return $cache[$key];
    }
    $result = xmlrpc_get_linux_distributions($entity ? array(updatesEntityId($entity)) : array());
    if (updatesReadFailed($result)) {
        return $cache[$key] = null;
    }
    $distributions = array();
    foreach ($result as $row) {
        $id = is_array($row) && is_scalar($row['distribution'] ?? null) ? trim((string) $row['distribution']) : '';
        if ($id === '') {
            continue;
        }
        $label = is_scalar($row['label'] ?? null) ? trim((string) $row['label']) : '';
        $distributions[$id] = ($label !== '') ? $label : $id;
    }
    return $cache[$key] = $distributions;
}

/**
 * System of a status tab or of its machines list: "linux", else "windows".
 *
 * @param mixed $value
 * @return string
 */
function updatesStatusSystem($value)
{
    return ($value === 'linux') ? 'linux' : 'windows';
}

/**
 * Linux distribution filter of the machines list, "" for all.
 *
 * @param mixed $value
 * @return string
 */
function updatesStatusDistribution($value)
{
    return (is_string($value) && preg_match('/^[A-Za-z0-9._+-]{1,64}$/', $value)) ? $value : '';
}

/**
 * Filter of the bar that reloads the page with its URL parameter.
 *
 * @param string $param    URL parameter, also the id of the list
 * @param string $label
 * @param array  $options  value => label, "" removes the parameter
 * @param string $selected
 */
function updatesParamSelect($param, $label, $options, $selected)
{
    $labels = array();
    $values = array();
    foreach ($options as $value => $text) {
        $labels[] = htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
        $values[] = htmlspecialchars((string) $value, ENT_QUOTES, 'UTF-8');
    }
    $id = $param . '-filter';
    $select = new SelectItem($id, 'updatesApplyParam');
    $select->setJsFuncParams(array("'" . $param . "'", 'this.value'));
    $select->setElements($labels);
    $select->setElementsVal($values);
    $select->setSelected(htmlspecialchars($selected, ENT_QUOTES, 'UTF-8'));
    echo '<div class="entity-filter">';
    echo '<label for="' . $id . '">' . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . ':</label>';
    $select->display();
    echo '</div>';
    ?>
    <script>
    function updatesApplyParam(param, value) {
        var url = new URL(window.location.href);
        if (value) {
            url.searchParams.set(param, value);
        } else {
            url.searchParams.delete(param);
        }
        window.location.href = url.toString();
    }
    </script>
    <?php
}

/**
 * Distribution selector; the choice reloads the page with the distribution parameter.
 *
 * @param array  $distributions distribution => label (updatesLinuxDistributions)
 * @param string $selected      "" for all
 */
function updatesDistributionSelect($distributions, $selected)
{
    updatesParamSelect('distribution', _T("Distribution", "updates"),
                       array('' => _T("All distributions", "updates")) + $distributions, $selected);
}

/**
 * Distributions of an entity and the one requested in the URL, kept only when
 * the entity reports it.
 *
 * @param array|null $entity Entry of getUserLocations()
 * @return array array(distributions or null when unreadable, selected distribution or "")
 */
function updatesLinuxDistributionFilter($entity)
{
    $distributions = updatesLinuxDistributions($entity);
    $requested = updatesStatusDistribution($_GET['distribution'] ?? '');
    $distribution = ($distributions === null || isset($distributions[$requested])) ? $requested : '';
    return array($distributions, $distribution);
}

/**
 * Body of a tab of the Update status page: counters, filters and machines list.
 *
 * @param string $system "windows" or "linux"
 */
function updatesStatusTab($system)
{
    $system = updatesStatusSystem($system);
    $linux = ($system === 'linux');
    $entity = updatesSelectedEntity();
    $scope = $entity ? array(updatesEntityId($entity)) : array();

    $distributions = array();
    $distribution = '';
    if ($linux) {
        list($distributions, $distribution) = updatesLinuxDistributionFilter($entity);
    }

    $summary = xmlrpc_get_windows_summary($scope, $system, $distribution);
    if (updatesReadFailed($summary)) {
        updatesReadFailedBox();
    } else {
        $machines = (int) updatesWinNumber($summary['machines'] ?? null);
        $noReport = (int) updatesWinNumber($summary['no_report'] ?? null);
        $cards = new StatCards();
        $conformity = ($machines > 0) ? updatesWinNumber($summary['conformity'] ?? null) : null;
        $cards->addCard(($conformity !== null) ? min($conformity, 100) . ' %' : '-', _T("Compliance", "updates"),
                        ($conformity === null) ? 'neutral' : (($conformity >= 100) ? 'low' : 'medium'),
                        array('title' => _T("Share of evaluated machines with no missing update.", "updates")));
        $tabId = $linux ? 'tablinux' : 'tabwin';
        $groupCards = updatesStatusGroupCategories();
        $toUpdate = (int) updatesWinNumber($summary['to_update'] ?? null);
        $options = array('total' => $machines,
                         'title' => _T("Machines missing at least one update.", "updates"));
        updatesGroupCardLink($options, 'status', $tabId, 'to_update', $entity, $toUpdate, $distribution);
        $cards->addCard($toUpdate, $groupCards['to_update']['label'], 'neutral', $options);
        $critical = (int) updatesWinNumber($summary['critical'] ?? null);
        $options = array('title' => $linux
                         ? _T("Machines missing an update rated Critical by the distribution.", "updates")
                         : _T("Machines missing a critical update or one that fixes an exploited flaw.", "updates"));
        updatesGroupCardLink($options, 'status', $tabId, 'critical', $entity, $critical, $distribution);
        $cards->addCard($critical, $groupCards['critical']['label'], ($critical > 0) ? 'critical' : 'neutral', $options);
        $notEvaluated = (int) updatesWinNumber($summary['not_evaluated'] ?? null);
        $cards->addCard($notEvaluated, _T("Not evaluated", "updates"), ($notEvaluated > 0) ? 'medium' : 'neutral',
                        array('title' => $linux
                              ? _T("Machines with no recent report.", "updates")
                              : _T("Machines with no recent report, or whose entity tracks no product.", "updates")));
        $rebootPending = (int) updatesWinNumber($summary['reboot_pending'] ?? null);
        $options = array();
        updatesGroupCardLink($options, 'status', $tabId, 'reboot_pending', $entity, $rebootPending, $distribution);
        $cards->addCard($rebootPending, $groupCards['reboot_pending']['label'], 'neutral', $options);
        if ($noReport > 0) {
            $cards->addCard($noReport, _T("No report", "updates"), 'neutral',
                            array('title' => _T("Machines known to Medulla whose agent has never sent an updates report.", "updates")));
        }
        $cards->display();
    }

    if (!$linux && $entity && updatesWinTrackedProducts(updatesEntityId($entity)) === 0) {
        updatesWinNoProductNotice(updatesEntityId($entity));
    }

    $params = $entity ? array('location' => $entity['uuid']) : array();
    if ($linux) {
        $params['system'] = $system;
        if ($distribution !== '') {
            $params['distribution'] = $distribution;
        }
    }
    echo '<div class="ajax-section updates-entity-section">';
    updatesEntitySelect($entity);
    if ($linux && $distributions !== null) {
        updatesDistributionSelect($distributions, $distribution);
    }
    $ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMachinesListWin"), "container", $params);
    $ajax->display();
    $ajax->displayDivToUpdate();
    echo '</div>';
}

/**
 * Categories de mise a niveau, dans l'ordre d'affichage.
 *
 * @return array cle backend => array(label, badge : variante updatesWinBadge)
 */
function updatesUpgradeCategories()
{
    return array(
        'ready'         => array('label' => _T("To upgrade", "updates"), 'badge' => 'info'),
        'in_progress'   => array('label' => _T("In progress", "updates"), 'badge' => 'progress'),
        'reboot_pending' => array('label' => _T("Reboot pending", "updates"), 'badge' => 'reboot'),
        'not_eligible' => array('label' => _T("Not eligible", "updates"), 'badge' => 'none'),
        'no_report'     => array('label' => _T("Waiting for the report", "updates"), 'badge' => 'none'),
        'undetermined'  => array('label' => _T("Undetermined", "updates"), 'badge' => 'none'),
        'up_to_date'    => array('label' => _T("Up to date", "updates"), 'badge' => 'low'),
        'not_concerned' => array('label' => _T("Not concerned", "updates"), 'badge' => 'none'),
    );
}

/**
 * Cartes de mise a niveau qui proposent de creer un groupe : la cle est un
 * filtre de get_upgrade_machine_list.
 *
 * @return array cle => array(label de la carte, what : ce qui suit « N machines »)
 */
function updatesUpgradeGroupCategories()
{
    return array(
        'ready'           => array('label' => _T("To upgrade", "updates"),
                                   'what' => _T("to upgrade", "updates")),
        'reboot_pending'  => array('label' => _T("Reboot pending", "updates"),
                                   'what' => _T("waiting for a restart", "updates")),
    );
}

/**
 * Une mise a niveau peut etre lancee depuis cette categorie.
 *
 * @param string $category
 * @return bool
 */
function updatesUpgradeLaunchable($category)
{
    return $category === 'ready';
}

/**
 * Pourquoi la mise a niveau de la ligne ne peut pas etre abandonnee (regle de
 * updates.cancel_upgrade), vide quand elle peut l'etre.
 *
 * @param array  $row    Ligne de get_upgrade_machine_list
 * @param string $system "windows" or "linux"
 * @return string '', not_launched, step_running ou reboot_pending
 */
function updatesUpgradeCancelRefusal($row, $system)
{
    if (trim((string) ($row['launched_at'] ?? '')) === '') {
        return 'not_launched';
    }
    if (updatesWinTriState($row['step_running'] ?? null) === true) {
        return 'step_running';
    }
    if ($system !== 'linux' && ($row['category'] ?? '') === 'reboot_pending') {
        return 'reboot_pending';
    }
    return '';
}

/**
 * Compteurs de mise a niveau, lus une seule fois par requete et par entite.
 *
 * @param array|null $entity Entite choisie, null pour toutes
 * @param string     $tabId  Onglet (updatesUpgradeTabs)
 * @return array|null {total, categories: {cle: nombre}, reboot_pending}, null si la reponse est inexploitable
 */
function updatesUpgradeSummary($entity, $tabId = 'tabwin')
{
    static $cache = array();
    $entityId = $entity ? updatesEntityId($entity) : null;
    $key = $tabId . ':' . ($entityId ?? 'all');
    if (!array_key_exists($key, $cache)) {
        $summary = xmlrpc_get_upgrade_summary(($entityId !== null) ? array($entityId) : array(),
                                              updatesUpgradeTabs()[$tabId]['system'] ?? 'windows');
        if (updatesReadFailed($summary) || !isset($summary['total']) || !is_array($summary['categories'] ?? null)) {
            $cache[$key] = null;
        } else {
            $counts = array();
            foreach (updatesUpgradeCategories() as $category => $unused) {
                $counts[$category] = (int) updatesWinNumber($summary['categories'][$category] ?? null);
            }
            $cache[$key] = array('total' => (int) updatesWinNumber($summary['total']), 'categories' => $counts,
                                 'reboot_pending' => (int) updatesWinNumber($summary['reboot_pending'] ?? null));
        }
    }
    return $cache[$key];
}

/**
 * URL de la page des mises a niveau.
 *
 * @param array|null $entity Entite choisie, null pour toutes
 * @param string     $tabId  Onglet (updatesUpgradeTabs)
 * @return string URL non echappee
 */
function updatesUpgradeUrl($entity, $tabId = 'tabwin')
{
    $params = array('tab' => $tabId);
    if ($entity) {
        $params['location'] = $entity['uuid'];
    }
    return urlStrRedirect("updates/updates/MajorEntitiesList", $params);
}

/**
 * Libelles des prerequis et des raisons d'une mise a niveau, table unique.
 *
 * @return array code => libelle
 */
function updatesUpgradeReasonLabels()
{
    return array(
        'cpu'           => _T("Processor", "updates"),
        'ram'           => _T("Memory", "updates"),
        'disk'          => _T("Storage", "updates"),
        'secure_boot'   => _T("Firmware", "updates"),
        'tpm'           => _T("TPM 2.0", "updates"),
        'graphics'      => _T("Graphics card", "updates"),
        'display'       => _T("Display", "updates"),
        'firmware'      => _T("Firmware", "updates"),
        'server'        => _T("Windows Server", "updates"),
        'ltsc'          => _T("LTSC edition", "updates"),
        'backports'     => _T("Backports repository to remove", "updates"),
        'held_packages' => _T("Held packages", "updates"),
        'dpkg_audit'    => _T("Packages to repair", "updates"),
        'disk_boot'     => _T("/boot too small or too full", "updates"),
        'disk_root'     => _T("Not enough free space on /", "updates"),
        'disk_var'      => _T("Not enough free space on /var", "updates"),
        'distro_info'   => _T("List of system versions missing", "updates"),
        'release_upgrader' => _T("Upgrade tool missing", "updates"),
        'distribution'  => _T("Distribution not supported yet", "updates"),
    );
}

/**
 * Raisons de non-eligibilite, separees par des virgules, traduites ; un code
 * inconnu n'est jamais affiche tel quel.
 *
 * @param mixed $reason
 * @return string Texte non echappe
 */
function updatesUpgradeReasonsText($reason)
{
    $labels = updatesUpgradeReasonLabels();
    $texts = array();
    foreach (explode(',', is_scalar($reason) ? (string) $reason : '') as $code) {
        $code = strtolower(trim($code));
        if ($code !== '') {
            $texts[] = $labels[$code] ?? _T("Other reason", "updates");
        }
    }
    return implode(', ', array_unique($texts));
}

/**
 * Cause de l'arret d'une mise a niveau (run_error), traduite d'apres ses codes :
 * « etape: cause », release etant l'etape Linux a reprendre.
 *
 * @param mixed $runError
 * @return string Texte non echappe, vide sans erreur
 */
function updatesUpgradeRunErrorText($runError)
{
    $error = is_scalar($runError) ? trim((string) $runError) : '';
    if ($error === '') {
        return '';
    }
    $cause = preg_replace('/^[^:\s]+:\s*/', '', $error);
    $causes = array(
        'no catalog update'          => _T("No update in the catalog for this step", "updates"),
        'no report from the machine' => _T("No report from the machine after the step", "updates"),
        'restart still pending'      => _T("Restart still pending after the step", "updates"),
        'machine unchanged'          => _T("Machine unchanged after the step", "updates"),
        'disk_full'                  => _T("Not enough free space on the machine", "updates"),
        'stopped'                    => _T("Upgrade stopped before any change, see the deployment log", "updates"),
    );
    $text = _T("The last attempt failed", "updates");
    if (strpos($cause, 'abandoned by ') === 0) {
        $text = sprintf(_T("Abandoned by %s", "updates"), substr($cause, strlen('abandoned by ')));
    } else {
        foreach ($causes as $code => $label) {
            if (strpos($cause, $code) === 0) {
                $text = $label;
                break;
            }
        }
    }
    return (strpos($error, 'release:') === 0)
        ? sprintf(_T("%s: %s", "updates"), _T("Upgrade to resume", "updates"), $text)
        : $text;
}

/**
 * Cellule Etat : badge de la categorie ; les raisons de non-eligibilite ou de non-prise en charge,
 * ou l'attente du redemarrage, en infobulle.
 *
 * @param array $row Ligne de xmlrpc_get_upgrade_machine_list
 * @return string HTML
 */
function updatesUpgradeStateCell($row)
{
    $categories = updatesUpgradeCategories();
    $category = (string) ($row['category'] ?? '');
    if (!isset($categories[$category])) {
        $category = 'undetermined';
    }
    if ($category === 'no_report' && trim((string) ($row['received_at'] ?? '')) === '') {
        return updatesWinBadge(_T("No report received", "updates"), 'none');
    }
    $tooltip = '';
    if ($category === 'not_eligible' || $category === 'not_concerned') {
        $tooltip = updatesUpgradeReasonsText($row['reason'] ?? '');
    }
    if ($category !== 'in_progress' && $category !== 'reboot_pending') {
        $runError = updatesUpgradeRunErrorText($row['run_error'] ?? '');
        if ($runError !== '') {
            $tooltip = ($tooltip !== '') ? $tooltip . ' - ' . $runError : $runError;
        }
    }
    $variant = ($tooltip !== '') ? 'upgrade-' . str_replace('_', '-', $category) : $categories[$category]['badge'];
    $label = ($category === 'reboot_pending' && updatesWinTriState($row['restart_requested'] ?? null) === true)
        ? _T("Restart requested", "updates") : $categories[$category]['label'];
    return updatesWinBadge($label, $variant, '', $tooltip);
}

/**
 * Cartes de la page des mises a niveau, sur le modele de la page d'etat des
 * mises a jour : conformite, a mettre a niveau, redemarrage en attente.
 *
 * @param array|null $entity Entite choisie, null pour toutes
 * @param string     $tabId  Onglet (updatesUpgradeTabs)
 */
function updatesUpgradeCards($entity, $tabId = 'tabwin')
{
    $summary = updatesUpgradeSummary($entity, $tabId);
    if ($summary === null) {
        updatesReadFailedBox();
        return;
    }
    $categories = $summary['categories'];
    $concerned = max(0, $summary['total'] - $categories['not_concerned']);
    $cards = new StatCards();
    if ($concerned > 0) {
        $conformity = (int) round(100 * $categories['up_to_date'] / $concerned);
        $cards->addCard(min($conformity, 100) . ' %', _T("Compliance", "updates"),
                        ($conformity >= 100) ? 'low' : 'medium');
    } else {
        $cards->addCard('-', _T("Compliance", "updates"), 'neutral');
    }
    $counts = array('ready' => $categories['ready'], 'reboot_pending' => $summary['reboot_pending']);
    foreach (updatesUpgradeGroupCategories() as $key => $card) {
        $options = ($key === 'ready') ? array('total' => $concerned) : array();
        updatesGroupCardLink($options, 'upgrade', $tabId, $key, $entity, $counts[$key]);
        $cards->addCard($counts[$key], $card['label'], 'neutral', $options);
    }
    $cards->display();
}

/**
 * Contenu d'un onglet de la page des mises a niveau : cartes, selecteur
 * d'entite, puis liste des machines avec recherche et pagination.
 *
 * @param string $tabId Identifiant d'onglet (updatesUpgradeTabs)
 */
function updatesUpgradeTab($tabId)
{
    if (!isset(updatesUpgradeTabs()[$tabId])) {
        return;
    }
    $entity = updatesSelectedEntity();
    updatesUpgradeCards($entity, $tabId);
    $params = array('tab' => $tabId);
    if ($entity) {
        $params['location'] = $entity['uuid'];
    }
    echo '<div class="ajax-section updates-entity-section">';
    updatesEntitySelect($entity);
    $ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxMajorTabMachines"), "EntityCompliancediv", $params);
    $ajax->display();
    $ajax->displayDivToUpdate();
    echo '</div>';
}

/**
 * Droit de lancer une mise a niveau : voir l'onglet du systeme sur la page et
 * deployer des mises a jour.
 *
 * @param string $tabId Onglet (updatesUpgradeTabs)
 * @return bool
 */
function updatesUpgradeCanLaunch($tabId = 'tabwin')
{
    return isset(updatesUpgradeTabs()[$tabId])
        && updatesWinCanDeploy()
        && hasCorrectAcl("updates", "updates", "MajorEntitiesList")
        && hasCorrectTabAcl("updates", "updates", "MajorEntitiesList", $tabId);
}

/**
 * Ligne de mise a niveau d'une machine, relue cote serveur.
 *
 * @param array  $entity   Entite de la machine
 * @param string $tabId    Onglet (updatesUpgradeTabs)
 * @param string $hostname Nom de la machine, restreint la lecture
 * @param string $field    Champ identifiant : glpi_uuid ou jid
 * @param string $value    Valeur attendue
 * @param bool   $failed   Rempli : la lecture a echoue
 * @return array|null
 */
function updatesUpgradeRow($entity, $tabId, $hostname, $field, $value, &$failed = null)
{
    $result = xmlrpc_get_upgrade_machine_list(array(updatesEntityId($entity)), 0, -1, $hostname, "",
                                              updatesUpgradeTabs()[$tabId]['system']);
    $failed = updatesReadFailed($result);
    foreach ((is_array($result) && is_array($result['rows'] ?? null)) ? $result['rows'] : array() as $candidate) {
        if (is_array($candidate) && ($candidate[$field] ?? null) === $value) {
            return $candidate;
        }
    }
    return null;
}

/**
 * Popup qui lance la mise a niveau d'une machine apres confirmation.
 * Parametres : entity (UUIDn, entite du lancement), uuid (machine GLPI),
 * hostname, tab (onglet d'origine) ; location pour revenir a la liste.
 */
function updatesUpgradePopup()
{
    $title = _T("Upgrade machine", "updates");
    $tabId = updatesUpgradeRequestTab();
    $entity = updatesUpgradeCanLaunch($tabId) ? updatesEntityByUuid($_GET['entity'] ?? '') : null;
    if (!$entity) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $glpiUuid = is_string($_GET['uuid'] ?? null) ? trim($_GET['uuid']) : '';
    $hostname = is_string($_GET['hostname'] ?? null) ? trim($_GET['hostname']) : '';
    $back = updatesUpgradeUrl(updatesSelectedEntity(), $tabId);
    $row = null;
    $readFailed = false;
    if (preg_match('/^UUID\d+$/', $glpiUuid)) {
        $row = updatesUpgradeRow($entity, $tabId, $hostname, 'glpi_uuid', $glpiUuid, $readFailed);
    }
    if ($row !== null && trim((string) ($row['hostname'] ?? '')) !== '') {
        $hostname = trim((string) $row['hostname']);
    }

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $name = ($hostname !== '') ? $hostname : $glpiUuid;
        $launched = 0;
        $error = $readFailed ? 'internal_error' : '';
        if ($row !== null && updatesUpgradeLaunchable((string) ($row['category'] ?? ''))) {
            $result = xmlrpc_launch_upgrades(updatesEntityId($entity), array($glpiUuid));
            if (is_array($result)) {
                $launched = (int) updatesWinNumber($result['launched'] ?? null);
                $error = is_scalar($result['error'] ?? null) ? trim((string) $result['error']) : '';
            } else {
                $error = 'internal_error';
            }
        }
        if ($launched > 0) {
            new NotifyWidgetSuccess(updatesActionText(_T("Upgrade of <b>%s</b> launched.", "updates"), $name));
        } else {
            $reason = updatesWinDeployErrorText($error, '');
            if ($reason === '') {
                $reason = _T("the machine is no longer ready to be upgraded", "updates");
            }
            new NotifyWidgetFailure(updatesActionText(_T("Upgrade of <b>%s</b> refused: %s.", "updates"), $name, $reason));
        }
        header('Location: ' . $back);
        exit;
    }

    if ($readFailed) {
        updatesReadFailedPopup($title);
        return;
    }
    $f = new PopupForm($title);
    if ($row === null || !updatesUpgradeLaunchable((string) ($row['category'] ?? ''))) {
        $f->addText(_T("This machine cannot be upgraded right now.", "updates"));
        $f->addCancelButton("bback");
        $f->display();
        return;
    }
    $target = is_scalar($row['target_release'] ?? null) ? trim((string) $row['target_release']) : '';
    $f->addText(($target !== '')
        ? updatesActionText(_T("Upgrade <b>%s</b> to <b>%s</b>?", "updates"), $hostname, $target)
        : updatesActionText(_T("Upgrade <b>%s</b>?", "updates"), $hostname));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

/**
 * Popup qui abandonne la mise a niveau en cours d'une machine apres confirmation.
 * Parametres : entity (UUIDn), jid, hostname, tab (onglet d'origine) ; location
 * pour revenir a la liste.
 */
function updatesUpgradeCancelPopup()
{
    $title = _T("Abandon", "updates");
    $tabId = updatesUpgradeRequestTab();
    $entity = updatesUpgradeCanLaunch($tabId) ? updatesEntityByUuid($_GET['entity'] ?? '') : null;
    $jid = is_string($_GET['jid'] ?? null) ? trim($_GET['jid']) : '';
    if (!$entity || !updatesJidValid($jid)) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $hostname = is_string($_GET['hostname'] ?? null) ? trim($_GET['hostname']) : '';
    $back = updatesUpgradeUrl(updatesSelectedEntity(), $tabId);
    $readFailed = false;
    $row = updatesUpgradeRow($entity, $tabId, $hostname, 'jid', $jid, $readFailed);
    $refusal = ($row !== null) ? updatesUpgradeCancelRefusal($row, updatesUpgradeTabs()[$tabId]['system']) : 'not_launched';
    $cancellable = ($refusal === '');
    $name = ($row !== null && trim((string) ($row['hostname'] ?? '')) !== '') ? trim((string) $row['hostname']) : $jid;

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $error = $readFailed ? 'internal_error' : $refusal;
        if ($cancellable) {
            $result = xmlrpc_cancel_upgrade($jid);
            $error = updatesResultError($result, 'internal_error');
        }
        if ($error === '') {
            new NotifyWidgetSuccess(updatesActionText(_T("Upgrade of <b>%s</b> abandoned.", "updates"), $name));
        } else {
            $reason = updatesWinDeployErrorText($error, '');
            if ($reason === '') {
                $reason = updatesWinDeployErrorText('internal_error', '');
            }
            new NotifyWidgetFailure(($error === 'step_running' || $error === 'reboot_pending')
                ? htmlspecialchars($reason, ENT_QUOTES, 'UTF-8')
                : updatesActionText(_T("Upgrade of <b>%s</b> not abandoned: %s.", "updates"), $name, $reason));
        }
        header('Location: ' . $back);
        exit;
    }

    if ($readFailed) {
        updatesReadFailedPopup($title);
        return;
    }
    $f = new PopupForm($title);
    if ($cancellable) {
        $f->addText(updatesActionText(_T("Abandon the upgrade of <b>%s</b>?", "updates"), $name));
        $f->addValidateButton("bconfirm");
    } elseif ($refusal === 'step_running' || $refusal === 'reboot_pending') {
        $f->addText(htmlspecialchars(updatesWinDeployErrorText($refusal, ''), ENT_QUOTES, 'UTF-8'));
    } else {
        $f->addText(_T("This upgrade is no longer in progress.", "updates"));
    }
    $f->addCancelButton("bback");
    $f->display();
}

/**
 * Restart action of a list row, greyed with its reason when not possible.
 *
 * @param array $params from (major ou list) et parametres de retour
 * @param bool  $waiting The machine waits for a restart
 * @param bool  $online
 * @param bool  $requested A restart was already sent and no report came since
 * @return ActionItem
 */
function updatesRestartAction($params, $waiting, $online, $requested = false)
{
    if (!updatesWinCanDeploy()) {
        $blocker = _T("Restart", "updates");
    } elseif (!$waiting) {
        $blocker = _T("No restart pending", "updates");
    } elseif ($requested) {
        $blocker = _T("Restart already requested", "updates");
    } elseif (!$online) {
        $blocker = _T("Machine offline", "updates");
    } else {
        $action = new ActionPopupItem(htmlspecialchars(_T("Restart", "updates"), ENT_QUOTES, 'UTF-8'),
                                      "restartMachine", "restart", "", "updates", "updates", null, 500);
        $action->staticParams = $params;
        return $action;
    }
    $item = new EmptyActionItem(htmlspecialchars($blocker, ENT_QUOTES, 'UTF-8'));
    $item->setClassCss('restart');
    return $item;
}

/**
 * Popup qui redemarre une machine en attente de redemarrage apres confirmation,
 * comme l'action rapide de xmppmaster. Parametres : jid, from (major, list ou
 * details), tab, location, distribution pour revenir a la page d'origine.
 */
function updatesRestartPopup()
{
    $title = _T("Restart", "updates");
    $jid = is_string($_GET['jid'] ?? null) ? trim($_GET['jid']) : '';
    if (!updatesWinCanDeploy() || !updatesJidValid($jid)) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $machine = xmlrpc_get_windows_machine($jid);
    $readFailed = is_array($machine) && updatesReadFailed($machine);
    if ($readFailed || !is_array($machine) || empty($machine)) {
        $machine = null;
    }
    $entityId = $machine ? updatesWinNumber($machine['entity_id'] ?? null) : null;
    if (!$readFailed && ($entityId === null || !updatesEntityByUuid('UUID' . $entityId))) {
        updatesUnknownEntityPopup($title);
        return;
    }

    $listEntity = updatesSelectedEntity();
    $from = $_GET['from'] ?? '';
    if ($from === 'major') {
        $back = updatesUpgradeUrl($listEntity, updatesUpgradeRequestTab());
    } else {
        $backParams = ($from === 'list') ? array() : array('jid' => $jid);
        if ($listEntity) {
            $backParams['location'] = $listEntity['uuid'];
        }
        if ($from === 'list') {
            if (($_GET['tab'] ?? '') === 'tablinux') {
                $backParams['tab'] = 'tablinux';
            }
            $distribution = updatesStatusDistribution($_GET['distribution'] ?? '');
            if ($distribution !== '') {
                $backParams['distribution'] = $distribution;
            }
        }
        $back = urlStrRedirect(($from === 'list') ? "updates/updates/EntityComplianceos" : "updates/updates/detailsMachineWin",
                               $backParams);
    }

    $online = $machine && updatesWinTriState($machine['online'] ?? null) === true;
    $signals = ($machine && is_array($machine['signals'] ?? null)) ? array_map('strval', $machine['signals']) : array();
    $waiting = in_array('reboot_pending', $signals, true) && updatesWinTriState($machine['running'] ?? null) !== true;
    $requested = $machine && updatesWinTriState($machine['restart_requested'] ?? null) === true;
    $hostname = $machine ? trim((string) ($machine['hostname'] ?? '')) : '';
    $name = ($hostname !== '') ? $hostname : $jid;

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $refusals = array(
            'not_waiting'       => _T("This machine is no longer waiting for a restart.", "updates"),
            'offline'           => _T("Machine offline", "updates"),
            'already_requested' => _T("Restart already requested", "updates"),
        );
        $result = $readFailed ? null : xmlrpc_restart_machine($jid);
        $reason = (is_array($result) && is_scalar($result['reason'] ?? null)) ? (string) $result['reason'] : '';
        if (is_array($result) && ($result['sent'] ?? false) === true) {
            new NotifyWidgetSuccess(updatesActionText(_T("Restart of <b>%s</b> sent.", "updates"), $name));
        } elseif (isset($refusals[$reason])) {
            new NotifyWidgetFailure(htmlspecialchars($refusals[$reason], ENT_QUOTES, 'UTF-8'));
        } else {
            new NotifyWidgetFailure(updatesActionText(_T("Restart of <b>%s</b> not sent.", "updates"), $name));
        }
        header('Location: ' . $back);
        exit;
    }

    if ($readFailed) {
        updatesReadFailedPopup($title);
    } elseif (!$waiting) {
        updatesMessagePopup($title, htmlspecialchars(_T("This machine is no longer waiting for a restart.", "updates"), ENT_QUOTES, 'UTF-8'));
    } elseif ($requested) {
        updatesMessagePopup($title, htmlspecialchars(_T("Restart already requested", "updates"), ENT_QUOTES, 'UTF-8'));
    } elseif (!$online) {
        updatesMessagePopup($title, htmlspecialchars(_T("Machine offline", "updates"), ENT_QUOTES, 'UTF-8'));
    } else {
        updatesConfirmPopup($title, updatesActionText(_T("Restart <b>%s</b>?", "updates"), $name));
    }
}

/**
 * Non-negative integer from the Windows backend, or null when absent
 * (null, "" or -1 when XML-RPC cannot carry None).
 *
 * @param mixed $value
 * @return int|null
 */
function updatesWinNumber($value)
{
    if (is_bool($value) || !is_numeric($value) || (int) $value < 0) {
        return null;
    }
    return (int) $value;
}

/**
 * Tri-state value from the Windows backend: true, false, or null when unknown.
 *
 * @param mixed $value
 * @return bool|null
 */
function updatesWinTriState($value)
{
    if ($value === true || $value === 1 || $value === '1') {
        return true;
    }
    if ($value === false || $value === 0 || $value === '0') {
        return false;
    }
    return null;
}

/**
 * Counter cell: muted at zero, highlighted when positive if a style is given.
 *
 * @param mixed  $value
 * @param string $highlight critical or empty
 * @return string HTML
 */
function updatesWinCount($value, $highlight = '')
{
    $count = updatesWinNumber($value);
    if ($count === null) {
        return '<span class="cell-empty">-</span>';
    }
    if ($count === 0) {
        return '<span class="updates-count-zero">0</span>';
    }
    if ($highlight !== '') {
        return '<span class="updates-count-' . htmlspecialchars($highlight) . '">' . $count . '</span>';
    }
    return (string) $count;
}

/**
 * Badge with a theme colour.
 *
 * @param string $text    Unescaped text
 * @param string $variant critical, high, medium, low or none
 * @param string $title   Optional unescaped tooltip
 * @param string $tooltip Optional unescaped text of a jQuery UI tooltip (updatesWinTooltips)
 * @return string HTML
 */
function updatesWinBadge($text, $variant, $title = '', $tooltip = '')
{
    $titleAttr = ($title !== '') ? ' title="' . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '"' : '';
    $tooltipClass = ($tooltip !== '') ? ' updates-tooltip' : '';
    $tooltipAttr = ($tooltip !== '') ? ' aria-label="' . htmlspecialchars($tooltip, ENT_QUOTES, 'UTF-8') . '"' : '';
    return '<span class="updates-badge updates-badge-' . htmlspecialchars($variant) . $tooltipClass . '"' . $titleAttr . $tooltipAttr . '>'
        . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') . '</span>';
}

/**
 * Last report date, plain text.
 *
 * @param mixed $receivedAt "YYYY-MM-DD HH:MM" or empty
 * @return string HTML
 */
function updatesWinReportDate($receivedAt)
{
    $date = is_string($receivedAt) ? trim($receivedAt) : '';
    return ($date !== '') ? '<span class="updates-nowrap">' . htmlspecialchars($date, ENT_QUOTES, 'UTF-8') . '</span>' : '<span class="cell-empty">-</span>';
}

/**
 * Status cell of a Windows machine: one badge for the exception, a dash otherwise.
 *
 * @param mixed $unsupported
 * @param mixed $evaluated
 * @param mixed $untracked Windows version not tracked by the entity
 * @param mixed $rebootPending Windows waits for a restart
 * @param string $system "windows" or "linux"
 * @param mixed $missing Number of missing updates
 * @param mixed $searchFailed The last search failed: the machine cannot be called up to date
 * @param mixed $updating An update deployment holds the machine or its command is waiting
 * @param mixed $restartRequested A restart was sent and no report came since
 * @return string HTML
 */
function updatesWinMachineStatus($unsupported, $evaluated, $untracked = null, $rebootPending = null, $system = 'windows', $missing = null, $searchFailed = null, $updating = null, $restartRequested = null)
{
    if (updatesWinTriState($searchFailed) === true) {
        return updatesWinBadge(_T("Search failed", "updates"), 'untracked',
            _T("The last search for updates failed.", "updates"));
    }
    if (updatesWinTriState($evaluated) !== true) {
        return updatesWinBadge(_T("No recent report", "updates"), 'none');
    }
    if (updatesWinTriState($updating) === true) {
        return updatesWinBadge(_T("In progress", "updates"), 'progress');
    }
    if (updatesWinTriState($rebootPending) === true && updatesWinTriState($restartRequested) === true) {
        return updatesWinBadge(_T("Restart requested", "updates"), 'reboot');
    }
    if (updatesWinTriState($rebootPending) === true) {
        return updatesWinBadge(_T("Reboot pending", "updates"), 'reboot', ($system === 'linux')
            ? _T("Updates are installed but the machine is waiting for a restart.", "updates")
            : _T("Updates are installed but Windows is waiting for a restart.", "updates"));
    }
    if (updatesWinTriState($unsupported) === true) {
        return updatesWinBadge(_T("Out of support", "updates"), 'unsupported',
            _T("Windows 10 without an ESU license no longer receives security updates.", "updates"));
    }
    if (updatesWinTriState($untracked) === true) {
        return updatesWinBadge(_T("Version not tracked", "updates"), 'untracked',
            _T("This entity does not track this Windows version: its updates are not evaluated.", "updates"));
    }
    if ((int) updatesWinNumber($missing) > 0) {
        return updatesWinBadge(_T("To update", "updates"), 'info');
    }
    return updatesWinBadge(_T("Up to date", "updates"), 'low');
}

/**
 * Severity of a Microsoft update as a badge; unknown values shown as text.
 *
 * @param mixed $severity Critical, Important, Moderate, Low
 * @return string HTML
 */
function updatesWinSeverityCell($severity)
{
    $variants = array('Critical' => 'critical', 'Important' => 'high', 'Moderate' => 'medium', 'Low' => 'low');
    $value = trim((string) $severity);
    if ($value === '') {
        return '<span class="cell-empty">-</span>';
    }
    if (!isset($variants[$value])) {
        return htmlspecialchars($value, ENT_QUOTES, 'UTF-8');
    }
    return '<span class="updates-badge updates-badge-' . $variants[$value] . '">' . updatesCatalogLabel($value) . '</span>';
}

/**
 * Risk cell of an update: one badge, "Exploited" when a flaw is exploited, else the severity.
 *
 * @param mixed $severity  Critical, Important, Moderate, Low
 * @param mixed $exploited
 * @return string HTML
 */
function updatesWinRiskCell($severity, $exploited)
{
    $severity = trim((string) $severity);
    if (updatesWinTriState($exploited) === true) {
        $title = ($severity !== '')
            ? sprintf(_T("Microsoft severity: %s", "updates"), html_entity_decode(updatesCatalogLabel($severity), ENT_QUOTES, 'UTF-8'))
            : '';
        return '<span class="updates-risk">' . updatesWinBadge(_T("Exploited", "updates"), 'critical', $title) . '</span>';
    }
    if ($severity === '') {
        return '<span class="cell-empty">-</span>';
    }
    return '<span class="updates-risk">' . updatesWinSeverityCell($severity) . '</span>';
}

/**
 * Offer of a Windows update line; missing or unknown means main.
 *
 * @param array $row Update line
 * @return string main, optional or esu
 */
function updatesWinOffer($row)
{
    $offer = $row['offer'] ?? '';
    return in_array($offer, array('optional', 'esu'), true) ? $offer : 'main';
}

/**
 * Info icon of a Windows update line, next to its KB; empty for a main update.
 *
 * @param array $row Update line
 * @return string HTML
 */
function updatesWinOfferIcon($row)
{
    switch (updatesWinOffer($row)) {
        case 'optional':
            $text = _T("Optional", "updates");
            break;
        case 'esu':
            $text = _T("ESU license required", "updates");
            break;
        default:
            return '';
    }
    $safe = htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    return '<span class="updates-offer-icon" aria-label="' . $safe . '"></span>';
}

/**
 * Tooltip of the offer icons and badges of a list, to call after each ajax rendering.
 * jQuery UI closes it when the list reloads and removes its element.
 */
function updatesWinTooltips()
{
    echo '<script type="text/javascript">
jQuery(function () {
    if (!(jQuery.ui && jQuery.ui.tooltip)) {
        return;
    }
    jQuery(".updates-offer-icon, .updates-tooltip").tooltip({
        items: ".updates-offer-icon, .updates-tooltip",
        show: {duration: 100},
        hide: {duration: 100},
        position: {my: "center top+8", at: "center bottom", collision: "flipfit flipfit"},
        content: function () {
            return jQuery("<span>").text(jQuery(this).attr("aria-label"));
        }
    });
});
</script>';
}

/**
 * Update lines of one section of the Windows machine page.
 *
 * @param array  $updates Update lines
 * @param string $section missing (offers main and esu) or optional
 * @return array
 */
function updatesWinSectionRows($updates, $section)
{
    return array_values(array_filter($updates, function ($row) use ($section) {
        return (updatesWinOffer($row) === 'optional') === ($section === 'optional');
    }));
}

/**
 * Single search of a machine page: it reloads every list, each one keeps its own pagination.
 * AjaxFilter drives one container only, so its updateSearch is replaced after display.
 *
 * @param string $jid      Machine JID
 * @param array  $sections Sections listed on the page, each with its div
 */
function updatesMachineSearch($jid, $sections)
{
    $url = urlStrRedirect("updates/updates/ajaxMachineUpdatesListWin", array('jid' => $jid));
    $ajax = new AjaxFilter($url, "updates-machine-" . $sections[0], array('section' => $sections[0]));
    $ajax->display();
    $flags = JSON_HEX_TAG | JSON_HEX_AMP | JSON_HEX_APOS | JSON_HEX_QUOT;
    echo '<script type="text/javascript">
(function () {
    var url = ' . json_encode($url, $flags) . ';
    var sections = ' . json_encode(array_values($sections), $flags) . ';
    function load(section, filter, start, end) {
        var target = url + "&section=" + section + "&filter=" + encodeURIComponent(filter);
        if (start !== undefined) {
            target += "&start=" + start + "&end=" + end;
        }
        jQuery.ajax({url: target, type: "get", success: function (data) {
            jQuery("#updates-machine-" + section).html(data);
        }});
    }
    jQuery.each(sections, function (index, section) {
        window["updateSearchParam" + section] = function (filter, start, end) {
            load(section, filter, start, end);
        };
    });
    jQuery(function () {
        jQuery.each(sections.slice(1), function (index, section) {
            load(section, document.Form.param.value);
        });
    });
    window.updateSearch = function () {
        jQuery.each(sections, function (index, section) {
            load(section, document.Form.param.value);
        });
    };
})();
</script>';
}

/**
 * Section title and container of a list loaded by updatesMachineSearch.
 *
 * @param string $title   Unescaped title
 * @param string $section Section name
 */
function updatesMachineSection($title, $section)
{
    $element = new SpanElement(htmlspecialchars($title, ENT_QUOTES, 'UTF-8'), "section-title");
    $element->display();
    echo '<div id="updates-machine-' . htmlspecialchars($section, ENT_QUOTES, 'UTF-8') . '" class="updates-machine-list"></div>';
}

/**
 * Greyed deploy action of an update that needs an ESU license.
 *
 * @return ActionItem
 */
function updatesWinEsuAction()
{
    return updatesWinDeployAction(_T("ESU license required", "updates"));
}

/**
 * Windows Update state of a machine, most telling fact first.
 *
 * @param mixed $state {automatic_updates, service_state, wsus_server, paused_until} or null
 * @return string|null HTML, null when unknown
 */
function updatesWinUpdateState($state)
{
    if (!is_array($state)) {
        return null;
    }
    $text = function ($key) use ($state) {
        return is_scalar($state[$key] ?? null) ? trim((string) $state[$key]) : '';
    };
    if ($text('service_state') === 'disabled') {
        return htmlspecialchars(_T("disabled", "updates"), ENT_QUOTES, 'UTF-8');
    }
    if ($text('wsus_server') !== '') {
        return htmlspecialchars(sprintf(_T("WSUS (%s)", "updates"), $text('wsus_server')), ENT_QUOTES, 'UTF-8');
    }
    $paused = ($text('paused_until') !== '') ? strtotime($text('paused_until')) : false;
    if ($paused !== false) {
        return htmlspecialchars(sprintf(_T("paused until %s", "updates"), date('d/m/Y', $paused)), ENT_QUOTES, 'UTF-8');
    }
    $labels = array(
        'not_configured' => _T("automatic", "updates"),
        'disabled'       => _T("disabled by policy", "updates"),
        'notify'         => _T("notification only", "updates"),
        'auto_download'  => _T("automatic download, manual installation", "updates"),
        'scheduled'      => _T("scheduled installation", "updates"),
    );
    $mode = $text('automatic_updates');
    return isset($labels[$mode]) ? htmlspecialchars($labels[$mode], ENT_QUOTES, 'UTF-8') : null;
}

/**
 * Automatic updates of a Linux machine: "on (tool)", or "off" in bold.
 *
 * @param mixed $state {tool, automatic_updates: "enabled"|"disabled"|null} or null
 * @return string|null HTML, null when unknown
 */
function updatesLinuxAutoUpdatesState($state)
{
    if (!is_array($state)) {
        return null;
    }
    $mode = is_scalar($state['automatic_updates'] ?? null) ? trim((string) $state['automatic_updates']) : '';
    $tool = is_scalar($state['tool'] ?? null) ? trim((string) $state['tool']) : '';
    if ($mode === 'disabled') {
        return '<strong>' . htmlspecialchars(_T("off", "updates"), ENT_QUOTES, 'UTF-8') . '</strong>';
    }
    if ($mode !== 'enabled') {
        return null;
    }
    $text = ($tool !== '') ? sprintf(_T("on (%s)", "updates"), $tool) : _T("on", "updates");
    return htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
}

/**
 * Escaped text cell, a dash when empty.
 *
 * @param mixed $value
 * @return string HTML
 */
function updatesLinuxTextCell($value)
{
    $text = is_scalar($value) ? trim((string) $value) : '';
    return ($text !== '') ? htmlspecialchars($text, ENT_QUOTES, 'UTF-8') : '<span class="cell-empty">-</span>';
}

/**
 * Positive number in the user's locale: "4", "15,6"; null when not measured.
 *
 * @param mixed $value
 * @return string|null
 */
function updatesWinDecimal($value)
{
    if (is_bool($value) || !is_numeric($value) || (float) $value <= 0) {
        return null;
    }
    $value = (float) $value;
    if (floor($value) == $value) {
        return (string) (int) $value;
    }
    $locale = localeconv();
    $point = !empty($locale['decimal_point']) ? $locale['decimal_point'] : '.';
    return number_format($value, 1, $point, '');
}

/**
 * Size cell of an update: MB below 1 GB, else GB with one decimal; a dash when unknown.
 *
 * @param mixed $size Bytes: int, string or float depending on the XML-RPC transport
 * @return string HTML
 */
function updatesSizeCell($size)
{
    $bytes = updatesWinNumber($size);
    if (!$bytes) {
        return '<span class="cell-empty">-</span>';
    }
    $megabytes = max(1, (int) round($bytes / 1048576));
    if ($megabytes < 1024) {
        $text = sprintf(_T("%s MB", "updates"), $megabytes);
    } else {
        $locale = localeconv();
        $point = !empty($locale['decimal_point']) ? $locale['decimal_point'] : '.';
        $text = sprintf(_T("%s GB", "updates"), number_format($bytes / 1073741824, 1, $point, ''));
    }
    return htmlspecialchars(str_replace(' ', "\u{00A0}", $text), ENT_QUOTES, 'UTF-8');
}

/**
 * Readable values of the Windows requirements measured on the machine.
 *
 * @param array $criteria Values measured on the machine
 * @return array criterion code => unescaped text, '' when not measured
 */
function updatesWinRequirementValues($criteria)
{
    $text = function ($key) use ($criteria) {
        return is_scalar($criteria[$key] ?? null) && $criteria[$key] !== false ? trim((string) $criteria[$key]) : '';
    };
    $values = array();

    $values['cpu'] = $text('cpu');

    $ram = updatesWinDecimal($criteria['ram_gb'] ?? null);
    $values['ram'] = ($ram !== null) ? sprintf(_T("%s GB", "updates"), $ram) : '';

    $disk = updatesWinDecimal($criteria['disk_size_gb'] ?? null);
    $values['disk'] = ($disk !== null) ? sprintf(_T("%s GB", "updates"), $disk) : '';

    $firmware = strtolower($text('firmware'));
    if ($firmware === 'bios') {
        $values['secure_boot'] = _T("Legacy BIOS", "updates");
    } elseif ($firmware === 'uefi' || ($firmware === '' && strtolower($text('secure_boot')) === 'enabled')) {
        $values['secure_boot'] = 'UEFI';
    } else {
        $values['secure_boot'] = '';
    }

    $tpm = $text('tpm');
    $values['tpm'] = (strtolower($tpm) === 'none') ? _T("absent", "updates") : $tpm;

    $graphics = is_array($criteria['graphics'] ?? null) ? $criteria['graphics'] : array();
    $parts = array();
    $directx = updatesWinDecimal($graphics['directx'] ?? null);
    if ($directx !== null) {
        $parts[] = 'DirectX ' . $directx;
    }
    $wddm = is_scalar($graphics['wddm'] ?? null) && $graphics['wddm'] !== false ? trim((string) $graphics['wddm']) : '';
    if ($wddm !== '') {
        $parts[] = 'WDDM ' . $wddm;
    }
    $values['graphics'] = implode(', ', $parts);

    $display = is_array($criteria['display'] ?? null) ? $criteria['display'] : array();
    $parts = array();
    $width = updatesWinNumber($display['width'] ?? null);
    $height = updatesWinNumber($display['height'] ?? null);
    if ($width && $height) {
        $parts[] = $width . ' × ' . $height;
    }
    $diagonal = updatesWinDecimal($display['diagonal_inches'] ?? null);
    if ($diagonal !== null) {
        $parts[] = sprintf(_T("%s inches", "updates"), $diagonal);
    }
    $values['display'] = implode(', ', $parts);

    return $values;
}

/**
 * Eligibility cell of an upgrade row: verdict as text, one line per requirement
 * in its HTML tooltip (mydata, see ajaxMajorTabMachines.php). Graphics card and
 * display only when they block the upgrade.
 *
 * @param array $row Upgrade row: target_release, windows11 {eligible, blockers, source, criteria}
 * @return string HTML
 */
function updatesUpgradeEligibilityCell($row)
{
    $empty = '<span class="cell-empty">-</span>';
    $windows11 = $row['windows11'] ?? null;
    if (trim((string) ($row['target_release'] ?? '')) === '' || !is_array($windows11) || empty($windows11)) {
        return $empty;
    }
    $blockers = array();
    foreach (is_array($windows11['blockers'] ?? null) ? $windows11['blockers'] : array() as $code) {
        if (is_scalar($code) && trim((string) $code) !== '') {
            $blockers[] = strtolower(trim((string) $code));
        }
    }
    // Microsoft asks for a UEFI firmware able to run Secure Boot: one line for both
    if (in_array('firmware', $blockers, true)) {
        $blockers[] = 'secure_boot';
    }
    $values = updatesWinRequirementValues(is_array($windows11['criteria'] ?? null) ? $windows11['criteria'] : array());
    $eligible = updatesWinTriState($windows11['eligible'] ?? null);
    if ($eligible === null && empty($blockers) && implode('', $values) === '') {
        return $empty;
    }
    if ($eligible === true) {
        $verdict = _T("Eligible", "updates");
    } elseif ($eligible === false) {
        $verdict = _T("Not eligible", "updates");
    } else {
        $verdict = _T("Indeterminate", "updates");
    }

    $windowsVerdict = (($windows11['source'] ?? '') === 'windows');
    $labels = array_intersect_key(updatesUpgradeReasonLabels(),
                                  array_flip(array('cpu', 'ram', 'disk', 'secure_boot', 'tpm', 'graphics', 'display')));
    $lines = '';
    foreach ($labels as $code => $label) {
        $blocking = in_array($code, $blockers, true);
        if (!$blocking && ($code === 'graphics' || $code === 'display')) {
            continue;
        }
        $value = $values[$code];
        if ($blocking) {
            $dot = 'ko';
            $text = ($value !== '') ? $value : _T("not measured", "updates");
        } elseif ($windowsVerdict) {
            if ($value === '') {
                continue;
            }
            $dot = 'ok';
            $text = $value;
        } elseif ($value === '') {
            $dot = 'none';
            $text = _T("not measured", "updates");
        } elseif ($code === 'cpu') {
            $dot = 'none';
            $text = $value . ' (' . _T("not verified", "updates") . ')';
        } else {
            $dot = 'ok';
            $text = $value;
        }
        $lines .= '<tr><td><span class="updates-req-dot updates-req-dot-' . $dot . '"></span>'
            . htmlspecialchars($label, ENT_QUOTES, 'UTF-8') . '</td><td>'
            . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') . '</td></tr>';
    }
    if ($lines === '') {
        return '<span class="cell-text">' . htmlspecialchars($verdict, ENT_QUOTES, 'UTF-8') . '</span>';
    }
    $tooltip = '<table class="ttable updates-req-tt">' . $lines . '</table>';
    return '<span class="cell-text updates-cell-help updates-eligibility" mydata="' . htmlspecialchars($tooltip, ENT_QUOTES, 'UTF-8') . '">'
        . htmlspecialchars($verdict, ENT_QUOTES, 'UTF-8') . '</span>';
}

/**
 * Every Windows entity row, fetched once per request.
 *
 * @return array|null Rows keyed by GLPI id, null when the answer is unusable
 */
function updatesWinEntityRows()
{
    static $rows = false;
    if ($rows !== false) {
        return $rows;
    }
    $result = xmlrpc_get_windows_entities();
    if (updatesReadFailed($result) || !is_array($result['rows'] ?? null)) {
        $rows = null;
        return $rows;
    }
    $rows = array();
    foreach ($result['rows'] as $row) {
        $id = is_array($row) ? updatesWinNumber($row['entity_id'] ?? null) : null;
        if ($id !== null) {
            $rows[$id] = $row;
        }
    }
    return $rows;
}

/**
 * Number of Windows products tracked by an entity, null when unknown.
 *
 * @param int $entityId
 * @return int|null
 */
function updatesWinTrackedProducts($entityId)
{
    $rows = updatesWinEntityRows();
    if ($rows === null || !isset($rows[(int) $entityId])) {
        return null;
    }
    return updatesWinNumber($rows[(int) $entityId]['tracked_products'] ?? null);
}

/**
 * Trackable versions of a Windows product; a single "" entry for a product without versions.
 *
 * @param array $product Row of xmlrpc_get_windows_products()
 * @return array[] {name, tracked}
 */
function updatesWinProductReleases($product)
{
    $releases = array();
    foreach ((array) ($product['releases'] ?? array()) as $release) {
        if (!is_array($release) || !is_scalar($release['name'] ?? null)) {
            continue;
        }
        $name = trim((string) $release['name']);
        if ($name !== '' && !isset($releases[$name])) {
            $releases[$name] = array('name' => $name,
                                     'tracked' => updatesWinTriState($release['tracked'] ?? null) === true);
        }
    }
    if (empty($releases)) {
        return array(array('name' => '', 'tracked' => updatesWinTriState($product['tracked'] ?? null) === true));
    }
    return array_values($releases);
}

/**
 * Entity of a single-entity page: the requested one, else the remembered one, else the first visible.
 *
 * @return array|null Entry of getUserLocations()
 */
function updatesWinProductsEntity()
{
    $entity = updatesSelectedEntity() ?? updatesEntityByUuid($_SESSION['updates_entity'] ?? '');
    if ($entity) {
        return $entity;
    }
    $locations = getUserLocations();
    return (is_array($locations) && !empty($locations)) ? reset($locations) : null;
}

/**
 * Link to the tracked Windows products of an entity, or plain text without the ACL.
 *
 * @param int    $entityId
 * @param string $text  Unescaped text
 * @param string $class CSS class of the link
 * @return string HTML
 */
function updatesWinProductsLink($entityId, $text, $class = '')
{
    $html = htmlspecialchars($text, ENT_QUOTES, 'UTF-8');
    if (!hasCorrectAcl("updates", "updates", "products")) {
        return ($class !== '') ? '<span class="' . htmlspecialchars($class) . '">' . $html . '</span>' : $html;
    }
    $url = urlStrRedirect("updates/updates/products", array('location' => 'UUID' . intval($entityId)));
    $classAttr = ($class !== '') ? ' class="' . htmlspecialchars($class) . '"' : '';
    return '<a' . $classAttr . ' href="' . htmlspecialchars($url, ENT_QUOTES, 'UTF-8') . '">' . $html . '</a>';
}

/**
 * Tabs of the tracked products page.
 *
 * @return array tab id => array(label, file)
 */
function updatesProductsTabs()
{
    return array(
        'tabwin' => array('label' => _T("Windows", "updates"),
                          'file' => "modules/updates/updates/products/windowsProducts.php"),
        'tablinux' => array('label' => _T("Linux", "updates"),
                            'file' => "modules/updates/updates/products/linuxReleases.php"),
    );
}

/**
 * End of a tracked products form: token and button under the last column.
 *
 * @param string $button Name of the submit button
 */
function updatesTrackedFormEnd($button)
{
    echo '<input type="hidden" name="auth_token" value="' . htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8') . '">';
    echo '<div class="approval-form-actions">';
    echo '<input class="btnPrimary" type="submit" name="' . htmlspecialchars($button, ENT_QUOTES, 'UTF-8') . '" value="' . htmlspecialchars(_T("Apply", "updates"), ENT_QUOTES, 'UTF-8') . '">';
    echo '</div>';
    echo '</form>';
    ?>
    <script>
    (function() {
        var col = document.querySelector('.approval-form table.listinfos thead th:last-child');
        var btn = document.querySelector('.approval-form-actions');
        if (col && btn) {
            var r = col.getBoundingClientRect();
            var f = btn.closest('form').getBoundingClientRect();
            btn.style.marginLeft = (r.left - f.left) + 'px';
            btn.style.width = r.width + 'px';
        }
    })();

    (function() {
        var form = document.querySelector('.approval-form');
        if (!form) { return; }

        function boxes(selector) {
            return Array.prototype.slice.call(form.querySelectorAll(selector));
        }

        function setState(master, items) {
            var checked = items.filter(function(b) { return b.checked; }).length;
            master.checked = (items.length > 0 && checked === items.length);
            master.indeterminate = (checked > 0 && checked < items.length);
        }

        function refresh() {
            boxes('input.family-check-all').forEach(function(master) {
                setState(master, boxes('input.product-check[data-family="' + master.dataset.family + '"]'));
            });
        }

        form.addEventListener('change', function(e) {
            var target = e.target;
            if (target.classList.contains('family-check-all')) {
                boxes('input.product-check[data-family="' + target.dataset.family + '"]').forEach(function(b) {
                    b.checked = target.checked;
                });
            }
            refresh();
        });
        refresh();
    })();
    </script>
    <?php
}

/**
 * Display name of a Linux distribution, the value itself when it has none.
 *
 * @param string $distribution
 * @return string Unescaped text
 */
function updatesLinuxDistributionName($distribution)
{
    $names = array(
        'debian' => 'Debian',
        'ubuntu' => 'Ubuntu',
        'almalinux' => 'AlmaLinux',
        'rocky' => 'Rocky Linux',
        'rockylinux' => 'Rocky Linux',
    );
    return $names[strtolower((string) $distribution)] ?? (string) $distribution;
}

/**
 * Notice shown when an entity tracks no Windows product.
 *
 * @param int $entityId
 */
function updatesWinNoProductNotice($entityId)
{
    $msg = htmlspecialchars(_T("No product is tracked for this entity: nothing is evaluated.", "updates"), ENT_QUOTES, 'UTF-8')
        . ' ' . updatesWinProductsLink($entityId, _T("Tracked products", "updates"));
    $notice = new Message($msg, "warning");
    $notice->display();
}

/**
 * Approval states offered by the status filter of the Approval page.
 *
 * @param string $system "windows" or "linux"
 * @return array status => label
 */
function updatesApprovalStatuses($system = 'windows')
{
    $statuses = array('pending' => _T("Pending", "updates"), 'approved' => _T("Approved", "updates"));
    if ($system !== 'linux') {
        $statuses['declined'] = _T("Declined", "updates");
    }
    return $statuses;
}

/**
 * Approval state from a request, pending when unknown to the system.
 *
 * @param mixed  $value
 * @param string $system "windows" or "linux"
 * @return string
 */
function updatesApprovalStatus($value, $system = 'windows')
{
    return (is_string($value) && isset(updatesApprovalStatuses($system)[$value])) ? $value : 'pending';
}

/**
 * Page whose ACL allows moving an update to a state.
 *
 * @param string $status approved, declined or pending
 * @return string|null
 */
function updatesApprovalActionPage($status)
{
    $pages = array('approved' => 'grayApprove', 'declined' => 'banUpdate', 'pending' => 'whiteUnlist');
    return $pages[$status] ?? null;
}

/**
 * Update id from a request, or null when malformed.
 *
 * @param mixed $value
 * @return string|null
 */
function updatesApprovalId($value)
{
    if (!is_scalar($value) || is_bool($value)) {
        return null;
    }
    $value = trim((string) $value);
    return ($value !== '' && strlen($value) <= 128 && preg_match('/^[A-Za-z0-9._-]+$/', $value)) ? $value : null;
}

/**
 * URL of a tab of the Approval page for an entity and a state.
 *
 * @param array|null $entity Entry of getUserLocations()
 * @param string     $status
 * @param string     $system       "windows" or "linux"
 * @param string     $distribution Linux distribution, "" for all
 * @return string
 */
function updatesApprovalUrl($entity, $status, $system = 'windows', $distribution = '')
{
    $params = array('tab' => ($system === 'linux') ? 'tablinux' : 'tabwin',
                    'status' => updatesApprovalStatus($status, $system));
    if ($entity) {
        $params['location'] = $entity['uuid'];
    }
    if ($system === 'linux' && $distribution !== '') {
        $params['distribution'] = $distribution;
    }
    return urlStrRedirect("updates/updates/updatesListWin", $params);
}

/**
 * Title cell of the approval list: the tooltip tells whether a rule approved
 * the update, otherwise who decided and when.
 *
 * @param mixed  $title
 * @param mixed  $kb
 * @param string $status    pending, approved or declined
 * @param bool   $byRule
 * @param mixed  $decidedBy
 * @param mixed  $decidedAt "YYYY-MM-DD HH:MM" or empty
 * @return string HTML
 */
function updatesApprovalTitleCell($title, $kb, $status, $byRule, $decidedBy, $decidedAt)
{
    if ($byRule) {
        return updatesTitleCell($title, $kb, _T("Approved by an automatic rule", "updates"));
    }
    $tooltip = '';
    $author = trim((string) $decidedBy);
    if ($author !== '' && ($status === 'approved' || $status === 'declined')) {
        $date = '';
        if (preg_match('/^(\d{4})-(\d{2})-(\d{2}) (\d{2}:\d{2})/', trim((string) $decidedAt), $m)) {
            $date = $m[3] . '/' . $m[2] . '/' . $m[1] . ' ' . $m[4];
        }
        if ($status === 'approved') {
            $tooltip = ($date !== '') ? sprintf(_T("Approved by %s on %s", "updates"), $author, $date)
                                      : sprintf(_T("Approved by %s", "updates"), $author);
        } else {
            $tooltip = ($date !== '') ? sprintf(_T("Declined by %s on %s", "updates"), $author, $date)
                                      : sprintf(_T("Declined by %s", "updates"), $author);
        }
    }
    return updatesTitleCell($title, $kb, $tooltip);
}

/**
 * Approval counters of an entity, with the origin of the Linux rules,
 * fetched once per request and per system.
 *
 * @param mixed  $entityId
 * @param string $system       "windows" or "linux"
 * @param string $distribution Linux distribution, "" for all
 * @return array|null Answer of get_windows_approvals, first row only
 */
function updatesApprovalsSummary($entityId, $system, $distribution = '')
{
    static $cache = array();
    $key = $system . ':' . $entityId . ':' . $distribution;
    if (!array_key_exists($key, $cache)) {
        $result = xmlrpc_get_windows_approvals($entityId, 'pending', 0, 1, "", $system, $distribution);
        $cache[$key] = updatesReadFailed($result) ? null : $result;
    }
    return $cache[$key];
}

/**
 * Status links of the Approval page, each state with its count; the current
 * one is shown without a link.
 *
 * @param array|null $entity       Entry of getUserLocations()
 * @param array|null $summary      Answer of updatesApprovalsSummary()
 * @param string     $system       "windows" or "linux"
 * @param string     $selected
 * @param string     $distribution Linux distribution, "" for all
 */
function updatesStatusLinks($entity, $summary, $system, $selected, $distribution = '')
{
    $counts = is_array($summary['counts'] ?? null) ? $summary['counts'] : null;
    $links = array();
    foreach (updatesApprovalStatuses($system) as $status => $label) {
        $count = ($counts !== null) ? updatesWinNumber($counts[$status] ?? null) : null;
        $text = htmlspecialchars(($count !== null) ? $label . ' (' . $count . ')' : $label, ENT_QUOTES, 'UTF-8');
        $links[] = ($status === $selected)
            ? '<strong class="updates-status-current">' . $text . '</strong>'
            : '<a href="' . htmlspecialchars(updatesApprovalUrl($entity, $status, $system, $distribution), ENT_QUOTES, 'UTF-8') . '">' . $text . '</a>';
    }
    echo '<div class="updates-status-links">'
        . implode('<span class="updates-status-sep">&middot;</span>', $links) . '</div>';
}

/**
 * Right of the entity selector on the Linux approval tab: where the automatic
 * approval rules come from, and the link to edit them.
 *
 * @param array $entity    Entry of getUserLocations()
 * @param mixed $rulesFrom rules_from of get_windows_approvals
 * @return string HTML
 */
function updatesLinuxRulesLine($entity, $rulesFrom)
{
    $rules = updatesWinInheritedEntity($rulesFrom);
    if ($rules === null) {
        $html = htmlspecialchars(_T("No automatic approval rule", "updates"), ENT_QUOTES, 'UTF-8');
    } elseif ($rules['id'] !== updatesEntityId($entity)) {
        $html = updatesWinBadge(sprintf(_T("Inherited from %s", "updates"), $rules['name']), 'none');
    } else {
        $html = updatesWinBadge(_T("Own setting", "updates"), 'none');
    }
    if (hasCorrectAcl("updates", "updates", "automation")
        && hasCorrectTabAcl("updates", "updates", "automation", "tablinux")) {
        $url = urlStrRedirect("updates/updates/automation", array('tab' => 'tablinux', 'location' => $entity['uuid']));
        $html .= ' <a href="' . htmlspecialchars($url, ENT_QUOTES, 'UTF-8') . '">'
            . htmlspecialchars(_T("Automatic approval", "updates"), ENT_QUOTES, 'UTF-8') . '</a>';
    }
    return $html;
}

/**
 * Popup moving one update to an approval state.
 *
 * @param string $status approved, declined or pending
 */
function updatesApprovalPopup($status)
{
    $texts = array(
        'approved' => array(
            'title'    => _T("Approve", "updates"),
            'question' => _T("Approve <b>%s</b> for entity <b>%s</b>?", "updates"),
            'note'     => _T("It can then be deployed to the machines of this entity.", "updates"),
            'success'  => _T("<b>%s</b> approved for entity <b>%s</b>.", "updates"),
            'failure'  => _T("<b>%s</b> could not be approved for entity <b>%s</b>.", "updates"),
        ),
        'declined' => array(
            'title'    => _T("Decline", "updates"),
            'question' => _T("Decline <b>%s</b> for entity <b>%s</b>?", "updates"),
            'note'     => _T("It cannot be deployed to the machines of this entity.", "updates"),
            'success'  => _T("<b>%s</b> declined for entity <b>%s</b>.", "updates"),
            'failure'  => _T("<b>%s</b> could not be declined for entity <b>%s</b>.", "updates"),
        ),
        'pending' => array(
            'title'    => _T("Back to pending", "updates"),
            'question' => _T("Move <b>%s</b> back to pending for entity <b>%s</b>?", "updates"),
            'note'     => '',
            'success'  => _T("<b>%s</b> moved back to pending for entity <b>%s</b>.", "updates"),
            'failure'  => _T("<b>%s</b> could not be moved back to pending for entity <b>%s</b>.", "updates"),
        ),
    );
    if (!isset($texts[$status])) {
        return;
    }
    $text = $texts[$status];
    $entity = updatesEntityByUuid($_GET['location'] ?? '');
    $updateId = updatesApprovalId($_GET['updateid'] ?? null);
    if (!$entity || $updateId === null) {
        updatesUnknownEntityPopup($text['title']);
        return;
    }
    $entityName = updatesEntityName($entity);
    $label = updatesUpdateLabel($_GET['title'] ?? '', $_GET['kb'] ?? '');
    if ($label === '') {
        $label = $updateId;
    }
    $from = $_GET['from'] ?? '';
    $backStatus = updatesApprovalStatus($from);

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_set_windows_approval(updatesEntityId($entity), array($updateId), $status);
        if ($result === true) {
            new NotifyWidgetSuccess(updatesActionText($text['success'], $label, $entityName));
        } else {
            new NotifyWidgetFailure(updatesActionText($text['failure'], $label, $entityName));
        }
        header('Location: ' . updatesApprovalUrl($entity, $backStatus));
        exit;
    }

    $f = new PopupForm($text['title']);
    $f->addText(updatesActionText($text['question'], $label, $entityName));
    if ($text['note'] !== '') {
        $f->addText('<em>' . htmlspecialchars($text['note'], ENT_QUOTES, 'UTF-8') . '</em>');
    }
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

/**
 * Whether the user may deploy Windows updates: same right as approving them.
 *
 * @return bool
 */
function updatesWinCanDeploy()
{
    return hasCorrectAcl("updates", "updates", "grayApprove");
}

/**
 * Reason why a Windows update cannot be deployed, empty when its package is ready.
 *
 * @param mixed $state ready, building, failed, unsupported or empty
 * @param mixed $error
 * @return string Unescaped sentence
 */
function updatesWinPackageBlocker($state, $error)
{
    $state = is_string($state) ? trim($state) : '';
    $error = is_scalar($error) ? trim((string) $error) : '';
    switch ($state) {
        case 'ready':
            return '';
        case 'building':
            return _T("Package being prepared", "updates");
        case 'failed':
            return ($error !== '') ? sprintf(_T("Package failed: %s", "updates"), $error) : _T("Package failed", "updates");
        case 'unsupported':
            return ($error !== '') ? sprintf(_T("Cannot be deployed automatically: %s", "updates"), $error)
                                   : _T("Cannot be deployed automatically", "updates");
    }
    return _T("No package available", "updates");
}

/**
 * Deploy action of a list row, greyed with its reason when not possible.
 *
 * @param string $blocker Unescaped reason, empty when the update can be deployed
 * @return ActionItem
 */
function updatesWinDeployAction($blocker)
{
    if (!updatesWinCanDeploy()) {
        $blocker = _T("Deploy", "updates");
    }
    if ($blocker !== '') {
        $item = new EmptyActionItem(htmlspecialchars($blocker, ENT_QUOTES, 'UTF-8'));
        $item->setClassCss('install');
        return $item;
    }
    return new ActionPopupItem(htmlspecialchars(_T("Deploy", "updates")), "deployWinUpdate", "install", "", "updates", "updates");
}

/**
 * Reason of a refused deployment, from the backend error code.
 *
 * @param string $code
 * @param mixed  $packageError Detail of a failed or unsupported package
 * @return string Unescaped sentence, empty for an unknown code
 */
function updatesWinDeployErrorText($code, $packageError)
{
    switch ($code) {
        case 'package_failed':
            return updatesWinPackageBlocker('failed', $packageError);
        case 'package_unsupported':
            return updatesWinPackageBlocker('unsupported', $packageError);
        case 'package_building':
            return updatesWinPackageBlocker('building', '');
    }
    $texts = array(
        'entity_refused'       => _T("entity not allowed", "updates"),
        'unknown_update'       => _T("unknown update", "updates"),
        'unknown_group'        => _T("unknown group", "updates"),
        'not_approved'         => _T("not approved for this entity", "updates"),
        'package_missing'      => _T("no package available", "updates"),
        'package_unregistered' => _T("package not registered", "updates"),
        'machine_not_targeted' => _T("this machine does not need it", "updates"),
        'internal_error'       => _T("internal error", "updates"),
        'not_launched'         => _T("it is no longer in progress", "updates"),
        'forbidden'            => _T("not allowed", "updates"),
        'step_running'         => _T("A step is running on this machine: wait for it to finish.", "updates"),
        'reboot_pending'       => _T("Preparation done: the upgrade will apply at the restart", "updates"),
        'esu_required'         => _T("ESU license required", "updates"),
    );
    return $texts[$code] ?? '';
}

/**
 * Reason why a machine was left out of a deployment.
 *
 * @param mixed $code
 * @return string Unescaped text, empty for an unknown code
 */
function updatesWinSkipReasonText($code)
{
    $texts = array(
        'unknown_machine'    => _T("unknown machine", "updates"),
        'already_deploying'  => _T("already being deployed", "updates"),
        'awaiting_report'    => _T("installed, waiting for the next report", "updates"),
        'deployment_running' => _T("another deployment in progress", "updates"),
        'upgrade_running'    => _T("upgrade in progress", "updates"),
        'upgrade_to_resume'  => _T("Upgrade to resume", "updates"),
        'creation_failed'    => _T("creation failed", "updates"),
        'not_approved'       => _T("not approved for its entity", "updates"),
        'package_not_ready'  => _T("package not ready", "updates"),
        'entity_refused'     => _T("entity not allowed", "updates"),
        'esu_required'       => _T("ESU license required", "updates"),
        'reboot_pending'     => _T("Reboot pending", "updates"),
    );
    return is_string($code) ? ($texts[$code] ?? '') : '';
}

/**
 * Notification of a deployment result: machines reached, then the skipped ones with their reason.
 *
 * @param array $result {created, skipped: [{jid, hostname, reason}]}
 */
function updatesWinDeployNotify($result)
{
    $created = updatesWinNumber($result['created'] ?? null) ?? 0;
    $skipped = array();
    foreach ((is_array($result['skipped'] ?? null) ? $result['skipped'] : array()) as $entry) {
        if (!is_array($entry)) {
            continue;
        }
        $host = trim((string) ($entry['hostname'] ?? ''));
        if ($host === '') {
            $host = trim((string) ($entry['jid'] ?? ''));
        }
        $reason = updatesWinSkipReasonText($entry['reason'] ?? '');
        $skipped[] = ($reason !== '') ? $host . ' (' . $reason . ')' : $host;
    }
    if ($created === 1) {
        $message = htmlspecialchars(_T("Deployment created on 1 machine.", "updates"), ENT_QUOTES, 'UTF-8');
    } elseif ($created > 1) {
        $message = updatesActionText(_T("Deployment created on %d machines.", "updates"), $created);
    } else {
        $message = htmlspecialchars(_T("No deployment created.", "updates"), ENT_QUOTES, 'UTF-8');
    }
    if (!empty($skipped)) {
        $message .= '<br>' . updatesActionText(_T("Skipped: %s", "updates"), implode(', ', $skipped));
    }
    if ($created > 0) {
        new NotifyWidgetSuccess($message);
    } else {
        new NotifyWidgetFailure($message);
    }
}

/**
 * Machine named by a popup: the hostname it received, else its jid.
 *
 * @param string $jid
 * @return string
 */
function updatesPopupMachine($jid)
{
    $hostname = is_string($_GET['hostname'] ?? null) ? trim($_GET['hostname']) : '';
    return ($hostname !== '') ? $hostname : $jid;
}

/**
 * Popup deploying one Windows update to the machines of an entity that miss
 * it, or to one machine when a jid is given.
 */
function updatesWinDeployPopup()
{
    $title = _T("Deploy", "updates");
    $entity = updatesEntityByUuid($_GET['location'] ?? '');
    $updateId = updatesApprovalId($_GET['updateid'] ?? null);
    if (!updatesWinCanDeploy() || !$entity || $updateId === null) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $jid = is_string($_GET['jid'] ?? null) ? trim($_GET['jid']) : '';
    if ($jid !== '' && !updatesJidValid($jid)) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $entityName = updatesEntityName($entity);
    $label = updatesUpdateLabel($_GET['title'] ?? '', $_GET['kb'] ?? '');
    if ($label === '') {
        $label = $updateId;
    }
    $back = ($jid !== '')
        ? urlStrRedirect("updates/updates/detailsMachineWin", array('jid' => $jid))
        : updatesApprovalUrl($entity, 'approved');

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_deploy_windows_update($updateId, updatesEntityId($entity), $jid);
        $error = updatesResultError($result);
        if (!is_array($result) || $error !== '') {
            $reason = updatesWinDeployErrorText($error, $result['package_error'] ?? '');
            $message = ($reason !== '')
                ? updatesActionText(_T("<b>%s</b> could not be deployed: %s", "updates"), $label, $reason)
                : updatesActionText(_T("<b>%s</b> could not be deployed.", "updates"), $label);
            new NotifyWidgetFailure($message);
            header('Location: ' . $back);
            exit;
        }
        updatesWinDeployNotify($result);
        header('Location: ' . $back);
        exit;
    }

    if ($jid !== '') {
        $question = updatesActionText(_T("Deploy <b>%s</b> on <b>%s</b>?", "updates"), $label, updatesPopupMachine($jid));
    } else {
        $count = updatesWinNumber($_GET['machines'] ?? null);
        if ($count === 1) {
            $question = updatesActionText(_T("Deploy <b>%s</b> to the machine of entity <b>%s</b> that needs it?", "updates"), $label, $entityName);
        } elseif ($count !== null && $count > 1) {
            $question = updatesActionText(_T("Deploy <b>%s</b> to the %d machines of entity <b>%s</b> that need it?", "updates"), $label, $count, $entityName);
        } else {
            $question = updatesActionText(_T("Deploy <b>%s</b> to the machines of entity <b>%s</b> that need it?", "updates"), $label, $entityName);
        }
    }
    updatesConfirmPopup($title, $question);
}

/**
 * Parameters of the popup deploying the approved missing packages of a Linux machine.
 *
 * @param string $jid
 * @param string $hostname
 * @param int    $count Approved packages among the missing ones
 * @return array
 */
function updatesLinuxDeployParams($jid, $hostname, $count)
{
    return array('os' => 'linux', 'jid' => $jid, 'hostname' => $hostname, 'count' => $count);
}

/**
 * Button opening a deployment popup.
 *
 * @param string $url
 * @param string $label HTML
 * @return string HTML
 */
function updatesDeployPopupButton($url, $label)
{
    $onclick = "PopupWindow(event, " . json_encode($url) . ", 400); return false;";
    return '<div class="updates-machine-actions"><button type="button" class="btnPrimary" onclick="'
        . htmlspecialchars($onclick, ENT_QUOTES, 'UTF-8') . '">' . $label . '</button></div>';
}

/**
 * Button of a Linux machine sheet deploying its approved missing packages.
 *
 * @param string $jid
 * @param string $hostname
 * @param int    $count Approved packages among the missing ones
 * @param bool   $running A deployment holds the machine: button greyed out
 * @return string HTML, empty without the deploy right or approved package
 */
function updatesLinuxDeployButton($jid, $hostname, $count, $running = false)
{
    if ($count <= 0 || !updatesWinCanDeploy()) {
        return '';
    }
    if ($running) {
        return '<div class="updates-machine-actions"><button type="button" class="btnPrimary" disabled>'
            . htmlspecialchars(_T("Deployment in progress", "updates"), ENT_QUOTES, 'UTF-8') . '</button></div>';
    }
    return updatesDeployPopupButton(
        urlStrRedirect("updates/updates/deployWinUpdate", updatesLinuxDeployParams($jid, $hostname, $count)),
        updatesActionText(_T("Deploy the approved updates (%d)", "updates"), intval($count)));
}

/**
 * Popup deploying to one Linux machine its missing packages approved for its
 * entity, or only the package of the row it was opened from. Back to the machine
 * sheet, or to the Update status list with from=list (location, distribution).
 */
function updatesLinuxDeployPopup()
{
    $title = _T("Deploy", "updates");
    $jid = is_string($_GET['jid'] ?? null) ? trim($_GET['jid']) : '';
    if (!updatesWinCanDeploy() || !updatesJidValid($jid)) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $hostname = is_string($_GET['hostname'] ?? null) ? trim($_GET['hostname']) : '';
    $package = is_string($_GET['package'] ?? null) ? trim($_GET['package']) : '';
    if (strlen($package) > 255 || preg_match('/[\s[:cntrl:]]/', $package)) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $back = urlStrRedirect("updates/updates/detailsMachineWin", array('jid' => $jid));
    if (($_GET['from'] ?? '') === 'list') {
        $listParams = array('tab' => 'tablinux');
        $listEntity = updatesSelectedEntity();
        if ($listEntity) {
            $listParams['location'] = $listEntity['uuid'];
        }
        $distribution = updatesStatusDistribution($_GET['distribution'] ?? '');
        if ($distribution !== '') {
            $listParams['distribution'] = $distribution;
        }
        $back = urlStrRedirect("updates/updates/EntityComplianceos", $listParams);
    }

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_deploy_linux_updates($jid, $package);
        $error = updatesResultError($result);
        if ($package !== '' && (!is_array($result) || $error !== '')) {
            $reason = updatesWinDeployErrorText($error, '');
            new NotifyWidgetFailure(($reason !== '')
                ? updatesActionText(_T("<b>%s</b> could not be deployed: %s", "updates"), $package, $reason)
                : updatesActionText(_T("<b>%s</b> could not be deployed.", "updates"), $package));
            header('Location: ' . $back);
            exit;
        }
        if (!is_array($result) || $error !== '') {
            $texts = array(
                'not_approved'         => _T("no package approved for this entity", "updates"),
                'machine_not_targeted' => _T("no package missing on this machine", "updates"),
            );
            $reason = $texts[$error] ?? updatesWinDeployErrorText($error, '');
            $message = ($reason !== '')
                ? updatesActionText(_T("The updates could not be deployed: %s", "updates"), $reason)
                : htmlspecialchars(_T("The updates could not be deployed.", "updates"), ENT_QUOTES, 'UTF-8');
            new NotifyWidgetFailure($message);
            header('Location: ' . $back);
            exit;
        }
        $packages = updatesWinNumber($result['packages'] ?? null) ?? 0;
        if ((updatesWinNumber($result['created'] ?? null) ?? 0) > 0 && $packages > 0) {
            new NotifyWidgetSuccess(($packages === 1)
                ? htmlspecialchars(_T("Deployment launched for 1 package.", "updates"), ENT_QUOTES, 'UTF-8')
                : updatesActionText(_T("Deployment launched for %d packages.", "updates"), $packages));
        } else {
            updatesWinDeployNotify($result);
        }
        header('Location: ' . $back);
        exit;
    }

    $host = ($hostname !== '') ? $hostname : $jid;
    $count = updatesWinNumber($_GET['count'] ?? null);
    if ($package !== '') {
        $question = updatesActionText(_T("Deploy <b>%s</b> on <b>%s</b>?", "updates"), $package, $host);
    } elseif ($count === 1) {
        $question = updatesActionText(_T("Deploy the approved update on <b>%s</b>?", "updates"), $host);
    } elseif ($count !== null && $count > 1) {
        $question = updatesActionText(_T("Deploy the %d approved updates on <b>%s</b>?", "updates"), $count, $host);
    } else {
        $question = updatesActionText(_T("Deploy the approved updates on <b>%s</b>?", "updates"), $host);
    }
    updatesConfirmPopup($title, $question);
}

/**
 * Uninstall action of a machine history row, greyed when the update cannot be removed.
 *
 * @param bool $removable
 * @param bool $running A deployment holds the machine: greyed with this reason
 * @return ActionItem
 */
function updatesWinUninstallAction($removable, $running)
{
    if (!$removable) {
        return new EmptyActionItem1(htmlspecialchars(_T("Uninstall", "updates"), ENT_QUOTES, 'UTF-8'), "uninstallWinUpdate", "convergenceunin");
    }
    if ($running) {
        $item = new EmptyActionItem(htmlspecialchars(_T("Deployment in progress", "updates"), ENT_QUOTES, 'UTF-8'));
        $item->setClassCss('convergenceunin');
        return $item;
    }
    return new ActionPopupItem(htmlspecialchars(_T("Uninstall", "updates"), ENT_QUOTES, 'UTF-8'), "uninstallWinUpdate", "convergenceunin", "", "updates", "updates");
}

/**
 * Popup removing an installed Windows update from one machine.
 */
function updatesWinUninstallPopup()
{
    $title = _T("Uninstall", "updates");
    $kb = updatesWinNumber($_GET['kb'] ?? null);
    $jid = is_string($_GET['jid'] ?? null) ? trim($_GET['jid']) : '';
    if (!$kb || !updatesJidValid($jid)) {
        updatesUnknownEntityPopup($title);
        return;
    }
    $label = 'KB' . $kb;
    $back = urlStrRedirect("updates/updates/detailsMachineWin", array('jid' => $jid));

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_uninstall_windows_update($kb, $jid);
        $error = updatesResultError($result);
        if (!is_array($result) || $error !== '') {
            if ($error === 'machine_not_targeted') {
                $message = htmlspecialchars(_T("This update is no longer installed on this machine.", "updates"), ENT_QUOTES, 'UTF-8');
            } else {
                $reason = updatesWinDeployErrorText($error, $result['package_error'] ?? '');
                $message = ($reason !== '')
                    ? updatesActionText(_T("<b>%s</b> could not be uninstalled: %s", "updates"), $label, $reason)
                    : updatesActionText(_T("<b>%s</b> could not be uninstalled.", "updates"), $label);
            }
            new NotifyWidgetFailure($message);
            header('Location: ' . $back);
            exit;
        }
        if ((updatesWinNumber($result['created'] ?? null) ?? 0) > 0) {
            new NotifyWidgetSuccess(updatesActionText(_T("Uninstallation of %s launched.", "updates"), $label));
        } else {
            updatesWinDeployNotify($result);
        }
        header('Location: ' . $back);
        exit;
    }

    $texts = array(updatesActionText(_T("Uninstall <b>%s</b> from <b>%s</b>? The machine will need a restart.", "updates"),
                                     $label, updatesPopupMachine($jid)));
    if (($_GET['reinstalled'] ?? '') === '1') {
        $texts[] = htmlspecialchars(_T("This update stays approved: it will be installed again by the next automatic deployment.", "updates"), ENT_QUOTES, 'UTF-8');
    }
    updatesConfirmPopup($title, ...$texts);
}

/**
 * Settings of a sub-entity that can come from an ancestor: page that edits
 * them (its ACL guards the reset), XML-RPC functions and the arguments they
 * take after the entity id.
 *
 * @param string $setting products, linuxreleases, rules, linuxrules or settings
 * @return array|null {page, get, reset, args}
 */
function updatesWinInheritance($setting)
{
    $settings = array(
        'products' => array('page' => 'products', 'tab' => 'tabwin', 'get' => 'xmlrpc_get_windows_products',
                            'reset' => 'xmlrpc_reset_windows_products'),
        'rules'    => array('page' => 'automation', 'tab' => 'tabwin', 'get' => 'xmlrpc_get_windows_approval_rules',
                            'reset' => 'xmlrpc_reset_windows_approval_rules', 'args' => array('windows')),
        'linuxrules' => array('page' => 'automation', 'tab' => 'tablinux', 'get' => 'xmlrpc_get_windows_approval_rules',
                              'reset' => 'xmlrpc_reset_windows_approval_rules', 'args' => array('linux')),
        'linuxreleases' => array('page' => 'products', 'tab' => 'tablinux', 'get' => 'xmlrpc_get_linux_releases',
                                 'reset' => 'xmlrpc_reset_linux_releases'),
        'settings' => array('page' => 'settingsWin', 'get' => 'xmlrpc_get_windows_settings',
                            'reset' => 'xmlrpc_reset_windows_settings'),
    );
    if (!is_string($setting) || !isset($settings[$setting])) {
        return null;
    }
    return $settings[$setting] + array('args' => array());
}

/**
 * Right to edit a setting: the ACL of its page and of its tab, if it has one.
 *
 * @param array $inheritance Answer of updatesWinInheritance()
 * @return bool
 */
function updatesWinInheritanceAllowed($inheritance)
{
    return hasCorrectAcl("updates", "updates", $inheritance['page'])
        && (!isset($inheritance['tab']) || hasCorrectTabAcl("updates", "updates", $inheritance['page'], $inheritance['tab']));
}

/**
 * Entity {id, name} of an inheritance field (parent, inherited_from), or null.
 *
 * @param mixed $value
 * @return array|null {id: int, name: string}
 */
function updatesWinInheritedEntity($value)
{
    if (!is_array($value)) {
        return null;
    }
    $id = updatesWinNumber($value['id'] ?? null);
    if ($id === null) {
        return null;
    }
    return array('id' => $id, 'name' => trim((string) ($value['name'] ?? '')));
}

/**
 * Right of the entity selector: badge of the ancestor the setting comes from, or
 * badge of the own setting followed by the link that takes the setting of the
 * parent again. Empty for the root entity.
 *
 * @param array  $entity  Entry of getUserLocations()
 * @param string $setting products, linuxreleases, rules, linuxrules or settings
 * @param mixed  $result  Answer of the matching get_* call
 * @return string HTML
 */
function updatesWinInheritanceLine($entity, $setting, $result)
{
    $inheritance = updatesWinInheritance($setting);
    if (!$entity || $inheritance === null || !is_array($result)) {
        return '';
    }
    $inherited = updatesWinInheritedEntity($result['inherited_from'] ?? null);
    if ($inherited !== null) {
        return updatesWinBadge(sprintf(_T("Inherited from %s", "updates"), $inherited['name']), 'none');
    }
    $parent = updatesWinInheritedEntity($result['parent'] ?? null);
    if ($parent === null || !updatesWinInheritanceAllowed($inheritance)) {
        return '';
    }
    $url = urlStrRedirect("updates/updates/resetWinSetting", array('location' => $entity['uuid'], 'setting' => $setting));
    $onclick = "PopupWindow(event, " . json_encode($url) . ", 400); return false;";
    return updatesWinBadge(_T("Own setting", "updates"), 'none')
        . ' <a href="' . htmlspecialchars($url, ENT_QUOTES, 'UTF-8') . '" onclick="' . htmlspecialchars($onclick, ENT_QUOTES, 'UTF-8') . '">'
        . htmlspecialchars(sprintf(_T("Use the setting of %s", "updates"), $parent['name']), ENT_QUOTES, 'UTF-8')
        . '</a>';
}

/**
 * Popup that drops the own setting of a sub-entity, which then takes the
 * setting of its parent again.
 */
function updatesWinResetPopup()
{
    $setting = $_GET['setting'] ?? '';
    $inheritance = updatesWinInheritance($setting);
    $entity = updatesEntityByUuid($_GET['location'] ?? '');
    if ($inheritance === null || !$entity || !updatesWinInheritanceAllowed($inheritance)) {
        updatesUnknownEntityPopup(_T("Use the setting of the parent entity", "updates"));
        return;
    }
    $entityId = updatesEntityId($entity);
    $entityName = updatesEntityName($entity);
    $backParams = array('location' => $entity['uuid']);
    if (isset($inheritance['tab'])) {
        $backParams['tab'] = $inheritance['tab'];
    }
    $back = urlStrRedirect("updates/updates/" . $inheritance['page'], $backParams);
    $args = array_merge(array($entityId), $inheritance['args']);
    $result = call_user_func_array($inheritance['get'], $args);
    $parent = is_array($result) ? updatesWinInheritedEntity($result['parent'] ?? null) : null;
    $parentName = ($parent !== null) ? $parent['name'] : '';

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        if ($parent !== null && call_user_func_array($inheritance['reset'], $args) === true) {
            new NotifyWidgetSuccess(updatesActionText(_T("Entity <b>%s</b> now uses the setting of <b>%s</b>.", "updates"), $entityName, $parentName));
        } else {
            new NotifyWidgetFailure(updatesActionText(_T("Entity <b>%s</b> could not take the setting of its parent again.", "updates"), $entityName));
        }
        header('Location: ' . $back);
        exit;
    }

    if (updatesReadFailed($result)) {
        updatesReadFailedPopup(_T("Use the setting of the parent entity", "updates"));
        return;
    }
    if ($parent === null) {
        updatesUnknownEntityPopup(_T("Use the setting of the parent entity", "updates"));
        return;
    }
    updatesConfirmPopup(htmlspecialchars(sprintf(_T("Use the setting of %s", "updates"), $parentName), ENT_QUOTES, 'UTF-8'),
                        updatesActionText(_T("The settings of %s will be replaced by those of %s.", "updates"), $entityName, $parentName));
}

/**
 * Systems of the automatic approval page: inheritance setting and whether the
 * rules carry a severity.
 *
 * @return array system => {setting, severity}
 */
function updatesApprovalSystems()
{
    return array(
        'windows' => array('setting' => 'rules', 'severity' => true),
        'linux'   => array('setting' => 'linuxrules', 'severity' => false),
    );
}

/**
 * Automatic approval rules of an entity for one system.
 *
 * @param string $system windows or linux
 * @param mixed  $result Filled with the answer of get_windows_approval_rules
 * @return array [{classification, severity, enabled}]
 */
function updatesApprovalRules($entityId, $system, &$result = null)
{
    $result = xmlrpc_get_windows_approval_rules($entityId, $system);
    $rules = array();
    if (is_array($result) && is_array($result['rules'] ?? null)) {
        foreach ($result['rules'] as $rule) {
            if (!is_array($rule)) {
                continue;
            }
            $rules[] = array(
                'classification' => trim((string) ($rule['classification'] ?? '')),
                'severity' => trim((string) ($rule['severity'] ?? '')),
                'enabled' => !empty($rule['enabled']),
            );
        }
    }
    return $rules;
}

/**
 * Indexes of the rules ticked in the posted form, in rule order.
 *
 * @param array $rules Answer of updatesApprovalRules()
 * @return int[]
 */
function updatesApprovalRulesPosted($rules)
{
    $ticked = array();
    foreach ((array) ($_POST['check'] ?? array()) as $value) {
        if (is_string($value) && ctype_digit($value) && isset($rules[(int) $value])) {
            $ticked[(int) $value] = true;
        }
    }
    $indexes = array_keys($ticked);
    sort($indexes);
    return $indexes;
}

/**
 * Save the posted rules of one system. Inherited rules left as they are stay
 * inherited: nothing is written for them.
 *
 * @param string $system windows or linux
 * @return bool
 */
function updatesApprovalRulesSave($entityId, $system)
{
    $result = null;
    $rules = updatesApprovalRules($entityId, $system, $result);
    if (updatesReadFailed($result) || empty($rules)) {
        return false;
    }
    $posted = updatesApprovalRulesPosted($rules);
    $current = array_keys(array_filter($rules, function ($rule) { return $rule['enabled']; }));
    if (updatesWinInheritedEntity($result['inherited_from'] ?? null) !== null && $posted === $current) {
        return true;
    }
    $enabled = array();
    foreach ($posted as $index) {
        $enabled[] = array('classification' => $rules[$index]['classification'],
                           'severity' => $rules[$index]['severity']);
    }
    return (xmlrpc_set_windows_approval_rules($entityId, $enabled, $system) === true);
}

/**
 * Grid of the automatic approval rules of one system, a checkbox per rule.
 *
 * @param array $rules    Answer of updatesApprovalRules()
 * @param bool  $severity Show the severity column
 */
function updatesApprovalRulesGrid($rules, $severity)
{
    $severityLabels = array();
    $classificationLabels = array();
    $checks = array();
    foreach ($rules as $index => $rule) {
        $severityLabels[] = ($rule['severity'] === '')
            ? htmlspecialchars(_T("All severities", "updates"), ENT_QUOTES, 'UTF-8')
            : updatesCatalogLabel($rule['severity']);
        $classificationLabels[] = updatesCatalogLabel($rule['classification']);
        $checks[] = sprintf(
            '<input type="checkbox" name="check[]" value="%d"%s>',
            $index,
            $rule['enabled'] ? ' checked' : ''
        );
    }
    if ($severity) {
        $n = new ListInfos($severityLabels, _T("Update Severity", "updates"));
        $n->addExtraInfoRaw($classificationLabels, _T("Update Classification", "updates"));
    } else {
        $n = new ListInfos($classificationLabels, _T("Update Classification", "updates"));
    }
    $n->addExtraInfoCenteredRaw(
        $checks,
        htmlspecialchars(_T("Automatic approval", "updates"), ENT_QUOTES, 'UTF-8')
            . ' <input type="checkbox" class="approval-check-all">'
    );
    $n->setNavBar = "";
    $n->start = 0;
    $n->end = count($rules) - 1;
    $n->disableFirstColumnActionLink();
    $n->display(0, 0);
}

/**
 * Onglets de la page d'approbation automatique.
 *
 * @return array id d'onglet => array(label, file, system)
 */
function updatesAutomationTabs()
{
    return updatesSystemTabs("automation");
}

/**
 * Body of a tab of the automatic approval page: entity, inheritance and the
 * rules of one system, saved on their own.
 *
 * @param string $system windows or linux
 */
function updatesAutomationTab($system)
{
    $systems = updatesApprovalSystems();
    $tabId = null;
    foreach (updatesAutomationTabs() as $id => $tab) {
        if ($tab['system'] === $system) {
            $tabId = $id;
        }
    }
    if (!isset($systems[$system]) || $tabId === null) {
        return;
    }
    $systemConf = $systems[$system];

    $entity = updatesWinProductsEntity();
    if (!$entity) {
        EmptyStateBox::show(_T("No entity available for this user.", "updates"));
        return;
    }
    $entityId = updatesEntityId($entity);
    $pageUrl = urlStrRedirect("updates/updates/automation", array('tab' => $tabId, 'location' => $entity['uuid']));

    if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['bsaverules'])) {
        verifyCSRFToken($_POST);
        if (updatesApprovalRulesSave($entityId, $system)) {
            new NotifyWidgetSuccess(_T("Rules saved.", "updates"));
        } else {
            new NotifyWidgetFailure(_T("Save failed.", "updates"));
        }
        header("Location: " . $pageUrl);
        exit;
    }

    $result = null;
    $rules = updatesApprovalRules($entityId, $system, $result);
    echo '<div class="updates-entity-section">';
    updatesEntitySelect($entity, false, updatesWinInheritanceLine($entity, $systemConf['setting'], $result));
    echo '</div>';
    if (updatesReadFailed($result)) {
        updatesReadFailedBox();
        return;
    }
    if (empty($rules)) {
        EmptyStateBox::show(_T("No rule available", "updates"));
        return;
    }

    echo '<form method="post" action="' . htmlspecialchars($pageUrl, ENT_QUOTES, 'UTF-8') . '" class="approval-form approval-rules">';
    $noteText = ($system === 'linux')
        ? _T("Approved packages go out on their own to the Linux machines during the time range of the automatic deployment.", "updates")
        : _T("Updates matching a ticked line are approved automatically for this entity, unless declined.", "updates");
    $note = new ParaElement(htmlspecialchars($noteText, ENT_QUOTES, 'UTF-8'), "updates-entity-scope");
    $note->display();
    updatesApprovalRulesGrid($rules, $systemConf['severity']);
    echo '<input type="hidden" name="auth_token" value="' . htmlspecialchars($_SESSION['auth_token'] ?? '', ENT_QUOTES, 'UTF-8') . '">';
    echo '<div class="approval-form-actions">';
    echo '<input class="btnPrimary" type="submit" name="bsaverules" value="' . htmlspecialchars(_T("Apply", "updates"), ENT_QUOTES, 'UTF-8') . '">';
    echo '</div>';
    echo '</form>';
    ?>
    <script>
    (function() {
        var masters = document.querySelectorAll('.approval-form table.listinfos input.approval-check-all');
        Array.prototype.forEach.call(masters, function(master) {
            var table = master.closest('table');
            var boxes = Array.prototype.slice.call(
                table.querySelectorAll('tbody input[type=checkbox]')
            );
            if (!boxes.length) { return; }

            function refreshMaster() {
                var checked = boxes.filter(function(b) { return b.checked; }).length;
                master.checked = (checked === boxes.length);
                master.indeterminate = (checked > 0 && checked < boxes.length);
            }

            master.addEventListener('click', function() {
                boxes.forEach(function(b) { b.checked = master.checked; });
                master.indeterminate = false;
            });
            boxes.forEach(function(b) { b.addEventListener('change', refreshMaster); });
            refreshMaster();
        });
    })();
    </script>
    <?php
}

/**
 * Time of day "HH:MM", or null when malformed.
 *
 * @param mixed $value
 * @return string|null
 */
function updatesWinTimeValue($value)
{
    $value = is_string($value) ? trim($value) : '';
    return preg_match('/^([01][0-9]|2[0-3]):[0-5][0-9]$/', $value) ? $value : null;
}

/**
 * Group of the gid request parameter, if the user sees it.
 *
 * @return array|null {id, name}
 */
function updatesWinRequestGroup()
{
    $gid = is_string($_GET['gid'] ?? null) ? trim($_GET['gid']) : '';
    if ($gid === '' || !ctype_digit($gid) || intval($gid) <= 0) {
        return null;
    }
    require_once("modules/dyngroup/includes/dyngroup.php");
    $group = new Group(intval($gid), true, true);
    if (!$group->exists) {
        return null;
    }
    return array('id' => intval($gid), 'name' => (string) $group->getName());
}

/**
 * URL of the updates page of a group.
 *
 * @param int $gid
 * @return string
 */
function updatesWinGroupUrl($gid)
{
    return urlStrRedirect("updates/updates/deployWinGroup", array('gid' => intval($gid)));
}

/**
 * Deploy action of a group row, greyed when no machine can receive the update.
 *
 * @param int|null $eligible
 * @return ActionItem
 */
function updatesWinGroupDeployAction($eligible)
{
    if ($eligible === null || $eligible === 0) {
        $item = new EmptyActionItem(htmlspecialchars(_T("No eligible machine", "updates"), ENT_QUOTES, 'UTF-8'));
        $item->setClassCss('install');
        return $item;
    }
    return new ActionPopupItem(htmlspecialchars(_T("Deploy", "updates")), "deployWinGroupUpdate", "install", "", "updates", "updates");
}

/**
 * Popup deploying one Windows update to the eligible machines of a group.
 */
function updatesWinGroupDeployPopup()
{
    $title = _T("Deploy", "updates");
    $group = hasCorrectAcl("updates", "updates", "deployWinGroup") ? updatesWinRequestGroup() : null;
    $updateId = updatesApprovalId($_GET['updateid'] ?? null);
    if (!$group || $updateId === null) {
        updatesUnknownGroupPopup($title);
        return;
    }
    $label = updatesUpdateLabel($_GET['title'] ?? '', $_GET['kb'] ?? '');
    if ($label === '') {
        $label = $updateId;
    }
    $back = updatesWinGroupUrl($group['id']);

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_deploy_windows_update_group($updateId, $group['id']);
        $error = updatesResultError($result);
        if (!is_array($result) || $error !== '') {
            $reason = updatesWinDeployErrorText($error, $result['package_error'] ?? '');
            $message = ($reason !== '')
                ? updatesActionText(_T("<b>%s</b> could not be deployed: %s", "updates"), $label, $reason)
                : updatesActionText(_T("<b>%s</b> could not be deployed.", "updates"), $label);
            new NotifyWidgetFailure($message);
        } else {
            updatesWinDeployNotify($result);
        }
        header('Location: ' . $back);
        exit;
    }

    $count = updatesWinNumber($_GET['eligible'] ?? null);
    if ($count === 1) {
        $question = updatesActionText(_T("Deploy <b>%s</b> to the eligible machine of group <b>%s</b>?", "updates"), $label, $group['name']);
    } elseif ($count !== null && $count > 1) {
        $question = updatesActionText(_T("Deploy <b>%s</b> to the %d eligible machines of group <b>%s</b>?", "updates"), $label, $count, $group['name']);
    } else {
        $question = updatesActionText(_T("Deploy <b>%s</b> to the eligible machines of group <b>%s</b>?", "updates"), $label, $group['name']);
    }
    updatesConfirmPopup($title, $question);
}

/**
 * Linux part of the updates page of a group: the deploy button when a machine
 * can receive its approved packages, and the list of these packages.
 *
 * @param int   $gid
 * @param array $summary {machines, eligible, packages}
 */
function updatesLinuxGroupSummary($gid, $summary)
{
    $eligible = updatesWinNumber($summary['eligible'] ?? null) ?? 0;
    echo '<div class="updates-group-linux">';
    if ((updatesWinNumber($summary['packages'] ?? null) ?? 0) > 0) {
        if ($eligible === 0) {
            echo '<p class="updates-machine-none">' . htmlspecialchars(_T("No eligible machine", "updates"), ENT_QUOTES, 'UTF-8') . '</p>';
        } elseif (updatesWinCanDeploy()) {
            echo updatesDeployPopupButton(
                urlStrRedirect("updates/updates/deployWinGroupUpdate", array('os' => 'linux', 'gid' => intval($gid))),
                htmlspecialchars(_T("Deploy the approved packages", "updates"), ENT_QUOTES, 'UTF-8'));
        }
        $ajax = new AjaxFilter(urlStrRedirect("updates/updates/ajaxDeployWinGroup"), "linuxPackages",
                               array('gid' => intval($gid), 'os' => 'linux'), "LinuxPackages");
        $ajax->display();
        $ajax->displayDivToUpdate();
    } else {
        EmptyStateBox::show(_T("No approved package", "updates"));
    }
    echo '</div>';
}

/**
 * Popup deploying to the Linux machines of a group their approved packages.
 */
function updatesLinuxGroupDeployPopup()
{
    $title = _T("Deploy", "updates");
    $group = (hasCorrectAcl("updates", "updates", "deployWinGroup") && updatesWinCanDeploy()) ? updatesWinRequestGroup() : null;
    if (!$group) {
        updatesUnknownGroupPopup($title);
        return;
    }
    $f = new PopupForm($title);

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_deploy_linux_group($group['id']);
        $error = updatesResultError($result);
        if (!is_array($result) || $error !== '') {
            $reason = updatesWinDeployErrorText($error, '');
            new NotifyWidgetFailure(($reason !== '')
                ? updatesActionText(_T("The updates could not be deployed: %s", "updates"), $reason)
                : htmlspecialchars(_T("The updates could not be deployed.", "updates"), ENT_QUOTES, 'UTF-8'));
        } else {
            updatesWinDeployNotify(array('created' => $result['deployed'] ?? null, 'skipped' => $result['skipped'] ?? null));
        }
        header('Location: ' . updatesWinGroupUrl($group['id']));
        exit;
    }

    $summary = xmlrpc_get_linux_group_summary($group['id']);
    if (updatesReadFailed($summary)) {
        updatesReadFailedPopup($title);
        return;
    }
    $eligible = updatesWinNumber($summary['eligible'] ?? null) ?? 0;
    if ($eligible === 0) {
        $f->addText(htmlspecialchars(_T("No eligible machine", "updates"), ENT_QUOTES, 'UTF-8'));
        $f->addButton("bback", htmlspecialchars(_T("Close", "base"), ENT_QUOTES, 'UTF-8'), "btnSecondary", "onclick=\"closePopup(); return false;\"");
        $f->display();
        return;
    }
    $f->addText(($eligible === 1)
        ? updatesActionText(_T("Deploy the approved packages to 1 Linux machine of group <b>%s</b>?", "updates"), $group['name'])
        : updatesActionText(_T("Deploy the approved packages to %d Linux machines of group <b>%s</b>?", "updates"), $eligible, $group['name']));
    $f->addText(updatesActionText(_T("Approved packages, all machines combined: %d", "updates"),
                                  updatesWinNumber($summary['packages'] ?? null) ?? 0));
    $f->addValidateButton("bconfirm");
    $f->addCancelButton("bback");
    $f->display();
}

/**
 * Page of the group list to come back to after the upgrade popup.
 *
 * @return string
 */
function updatesUpgradeGroupBackUrl()
{
    $referer = is_string($_SERVER['HTTP_REFERER'] ?? null) ? $_SERVER['HTTP_REFERER'] : '';
    $page = (strpos($referer, 'action=listFavourite') !== false) ? "listFavourite" : "list";
    return urlStrRedirect("base/computers/" . $page);
}

/**
 * Systems whose upgrade tab the user may see.
 *
 * @return string[] "windows", "linux"
 */
function updatesUpgradeGroupSystems()
{
    $systems = array();
    foreach (updatesUpgradeTabs() as $tabId => $tab) {
        if (hasCorrectTabAcl("updates", "updates", "MajorEntitiesList", $tabId)) {
            $systems[] = $tab['system'];
        }
    }
    return $systems;
}

/**
 * Popup upgrading the machines of a group after confirmation, on the systems
 * the user may upgrade.
 */
function updatesUpgradeGroupPopup()
{
    $title = _T("Upgrade this group", "updates");
    $group = hasCorrectAcl("updates", "updates", "upgradeWinGroup") ? updatesWinRequestGroup() : null;
    if (!$group) {
        updatesUnknownGroupPopup($title);
        return;
    }
    $f = new PopupForm($title);

    if (isset($_POST['bconfirm'])) {
        verifyCSRFToken($_POST);
        $result = xmlrpc_launch_upgrade_group($group['id'], updatesUpgradeGroupSystems());
        $launched = is_array($result) ? (int) updatesWinNumber($result['launched'] ?? null) : 0;
        $error = (is_array($result) && is_scalar($result['error'] ?? '')) ? trim((string) ($result['error'] ?? '')) : 'internal_error';
        if ($launched > 0) {
            new NotifyWidgetSuccess(($launched === 1)
                ? htmlspecialchars(_T("Upgrade launched on 1 machine.", "updates"), ENT_QUOTES, 'UTF-8')
                : updatesActionText(_T("Upgrade launched on %s machines.", "updates"), $launched));
        } elseif ($error === 'unknown_group') {
            new NotifyWidgetFailure(htmlspecialchars(_T("Unknown group.", "updates"), ENT_QUOTES, 'UTF-8'));
        } elseif ($error !== '') {
            new NotifyWidgetFailure(htmlspecialchars(_T("The upgrade could not be launched.", "updates"), ENT_QUOTES, 'UTF-8'));
        } else {
            new NotifyWidgetFailure(htmlspecialchars(_T("No machine of this group needs an upgrade.", "updates"), ENT_QUOTES, 'UTF-8'));
        }
        header('Location: ' . updatesUpgradeGroupBackUrl());
        exit;
    }

    $preview = xmlrpc_get_upgrade_group_preview($group['id'], updatesUpgradeGroupSystems());
    $error = updatesResultError($preview);
    if (!is_array($preview) || $error !== '') {
        $f->addText(($error === 'unknown_group')
            ? _T("Unknown group.", "updates")
            : htmlspecialchars(_T("Read failed", "updates"), ENT_QUOTES, 'UTF-8'));
        $f->addCancelButton("bback");
        $f->display();
        return;
    }

    $categories = updatesUpgradeCategories();
    $skipped = array();
    foreach ((is_array($preview['skipped'] ?? null) ? $preview['skipped'] : array()) as $category => $count) {
        $count = (int) updatesWinNumber($count);
        if ($count > 0) {
            $category = isset($categories[$category]) ? $category : 'undetermined';
            $skipped[$category] = ($skipped[$category] ?? 0) + $count;
        }
    }
    $skippedLines = array();
    foreach ($categories as $category => $info) {
        if (isset($skipped[$category])) {
            $skippedLines[] = updatesActionText(_T("%s: %s", "updates"), $info['label'], $skipped[$category]);
        }
    }
    $refused = (int) updatesWinNumber($preview['system_refused'] ?? null);
    if ($refused > 0) {
        $skippedLines[] = updatesActionText(_T("%s: %s", "updates"), _T("System not allowed", "updates"), $refused);
    }

    $launch = (int) updatesWinNumber($preview['launch'] ?? null);
    if ($launch === 0) {
        if ($refused === 0) {
            $f->addText(_T("No machine of this group needs an upgrade.", "updates"));
        }
    } else {
        foreach ((is_array($preview['targets'] ?? null) ? $preview['targets'] : array()) as $target => $count) {
            $count = (int) updatesWinNumber($count);
            if ($count > 0) {
                $target = trim((string) $target);
                $label = ($target !== '') ? $target : $categories['undetermined']['label'];
                $label = htmlspecialchars($label, ENT_QUOTES, 'UTF-8');
                $f->addText(($count === 1)
                    ? sprintf(_T("1 machine will be upgraded to %s", "updates"), $label)
                    : sprintf(_T("%s machines will be upgraded to %s", "updates"), '<b>' . $count . '</b>', $label));
            }
        }
    }
    if (!empty($skippedLines)) {
        $f->addText(htmlspecialchars(_T("Left out:", "updates"), ENT_QUOTES, 'UTF-8') . '<br>' . implode('<br>', $skippedLines));
    }
    if ($launch === 0) {
        $f->addButton("bback", htmlspecialchars(_T("Close", "base"), ENT_QUOTES, 'UTF-8'), "btnSecondary", "onclick=\"closePopup(); return false;\"");
    } else {
        $f->addValidateButton("bconfirm");
        $f->addCancelButton("bback");
    }
    $f->display();
}

/**
 * Etat de la copie du catalogue des mises a jour, lu une seule fois par requete.
 *
 * @return array "state", "cause", "last_success_at"
 */
function updatesReplicationState()
{
    static $replication = null;
    if ($replication === null) {
        $raw = xmlrpc_get_replication_state();
        $raw = is_array($raw) ? $raw : array();
        $replication = array(
            'state'           => is_string($raw['state'] ?? null) ? $raw['state'] : '',
            'cause'           => is_string($raw['cause'] ?? null) ? $raw['cause'] : '',
            'last_success_at' => is_string($raw['last_success_at'] ?? null) ? trim($raw['last_success_at']) : '',
        );
    }
    return $replication;
}

/**
 * Module ouvert : le catalogue a ete recu (a jour ou non).
 */
function updatesModuleOpen()
{
    return in_array(updatesReplicationState()['state'], array('ok', 'stale'), true);
}

/**
 * Cause d'echec en clair, jamais le texte brut du backend.
 */
function updatesReplicationCause($cause)
{
    if ($cause === 'unreachable') {
        return _T("catalog server unreachable", "updates");
    }
    if ($cause === 'clock') {
        return _T("server clock out of sync", "updates");
    }
    return _T("replication error", "updates");
}

/**
 * "YYYY-mm-dd HH:MM:SS" vers "d/m/Y H:i", chaine vide si illisible.
 */
function updatesReplicationDate($value)
{
    $date = ($value !== '') ? DateTime::createFromFormat('Y-m-d H:i:s', $value) : false;
    return $date ? $date->format('d/m/Y H:i') : '';
}

/**
 * Bloc affiche a la place d'une page quand le module est ferme.
 */
function updatesClosedBox()
{
    $replication = updatesReplicationState();
    switch ($replication['state']) {
        case 'not_configured':
        case 'denied':
            ContractRequiredBox::show();
            break;
        case 'first_copy':
            EmptyStateBox::show(_T("First copy of the updates catalog in progress", "updates"),
                                _T("The module opens once the catalog has been received.", "updates"));
            break;
        default:
            EmptyStateBox::show(_T("Updates catalog never received", "updates"),
                                sprintf(_T("Last attempt: %s.", "updates"), updatesReplicationCause($replication['cause'])));
    }
}

/**
 * Page complete du module ferme : titre, menu, bloc.
 */
function updatesClosedPage($title, $sidemenu)
{
    $p = new PageGenerator($title);
    $p->setSideMenu($sidemenu);
    $p->display();
    updatesClosedBox();
}

/**
 * Paragraphe "catalogue non actualise" quand la derniere actualisation a echoue.
 */
function updatesStaleNotice()
{
    $replication = updatesReplicationState();
    if ($replication['state'] !== 'stale') {
        return;
    }
    $cause = updatesReplicationCause($replication['cause']);
    $date = updatesReplicationDate($replication['last_success_at']);
    $text = ($date !== '')
        ? sprintf(_T("Updates catalog not updated since %s: %s.", "updates"), $date, $cause)
        : sprintf(_T("Updates catalog not updated: %s.", "updates"), $cause);
    echo '<p class="updates-stale-notice"><strong>' . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') . '</strong></p>';
}

/**
 * Section "Catalogue des mises a jour" en lecture seule, hors de tout formulaire.
 */
function updatesCatalogSection()
{
    $replication = updatesReplicationState();
    $date = updatesReplicationDate($replication['last_success_at']);
    if ($date === '') {
        return;
    }
    if ($replication['state'] === 'stale') {
        $text = sprintf(_T("%s, failing since: %s", "updates"), $date, updatesReplicationCause($replication['cause']));
        $value = '<strong>' . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') . '</strong>';
    } else {
        $value = htmlspecialchars($date, ENT_QUOTES, 'UTF-8');
    }
    $section = new Div();
    $section->add(new SpanElement(htmlspecialchars(_T("Updates catalog", "updates"), ENT_QUOTES, 'UTF-8'), "section-title"));
    $section->push(new Table());
    $section->add(new TrFormElement(_T("Last update", "updates"), new UpdatesTextTpl()),
                  array("value" => $value));
    $section->pop();
    $section->display();
}

/**
 * Valeur affichee telle quelle (deja echappee), sans champ de formulaire.
 */
class UpdatesTextTpl extends AbstractTpl
{
    public function display($arrParam = array())
    {
        print $arrParam['value'] ?? '';
    }

    public function displayRo($arrParam)
    {
        $this->display($arrParam);
    }

    public function displayHide($arrParam)
    {
        $this->display($arrParam);
    }
}

/**
 * Selecteur d'entite en ligne de formulaire (TrFormElement).
 * $arrParam : "entity" (updatesSelectedEntity), "allowAll", "aside" (HTML).
 */
class UpdatesEntitySelectTpl extends AbstractTpl
{
    public function display($arrParam = array())
    {
        updatesEntitySelectField($arrParam['entity'] ?? null, $arrParam['allowAll'] ?? false, $arrParam['aside'] ?? '');
    }
}

/**
 * Plage horaire sur une ligne : deux InputTpl separes par « De » / « à ».
 * $arrParam : "start", "end" (deja echappes), "placeholder".
 */
class UpdatesTimeRangeTpl extends AbstractTpl
{
    private $startTpl;
    private $endTpl;

    public function __construct(InputTpl $startTpl, InputTpl $endTpl)
    {
        $this->startTpl = $startTpl;
        $this->endTpl = $endTpl;
    }

    public function display($arrParam = array())
    {
        $placeholder = $arrParam['placeholder'] ?? '';
        print '<span class="updates-time-range-word updates-time-range-word-first">' . htmlspecialchars(_T("From", "updates"), ENT_QUOTES, 'UTF-8') . '</span>';
        $this->startTpl->display(array("value" => $arrParam['start'] ?? '', "placeholder" => $placeholder));
        print '<span class="updates-time-range-word">' . htmlspecialchars(_T("to", "updates"), ENT_QUOTES, 'UTF-8') . '</span>';
        $this->endTpl->display(array("value" => $arrParam['end'] ?? '', "placeholder" => $placeholder));
    }
}
