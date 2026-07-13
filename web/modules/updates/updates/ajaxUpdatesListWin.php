<?php
// SPDX-FileCopyrightText: 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
// SPDX-FileCopyrightText: 2007 Mandriva, http://www.mandriva.com
// SPDX-FileCopyrightText: 2016-2023 Siveo, http://www.siveo.net
// SPDX-FileCopyrightText: 2024-2025 Medulla, http://www.medulla-tech.io
// SPDX-License-Identifier: GPL-3.0-or-later
// file : web/modules/updates/updates/ajaxUpdatesListWin.php


require_once("modules/updates/includes/xmlrpc.php");


// Configuration des trois listes (Grey/White/Black). Centralisée pour éviter les duplications.
$listsConfig = [
    'grey' => [
        'action'    => 'ajaxUpdatesListWinGray',
        'container' => 'containerGray',
        'formid'    => 'formGray',
        'label'     => _T("Grey list (manual updates)", 'updates'),
    ],
    'white' => [
        'action'    => 'ajaxUpdatesListWinWhite',
        'container' => 'containerWhite',
        'formid'    => 'formWhite',
        'label'     => _T("White list (automatic updates)", 'updates'),
    ],
    'black' => [
        'action'    => 'ajaxUpdatesListWinBlack',
        'container' => 'containerBlack',
        'formid'    => 'formBlack',
        'label'     => _T("Black list (banned updates)", 'updates'),
    ],
];

// Mode "section" : rendu de l'AjaxFilter d'une seule liste, déclenché par un click sur l'onglet.
$type = $_GET['type'] ?? null;
if ($type !== null) {
    if (!isset($listsConfig[$type])) {
        return;
    }
    $cfg = $listsConfig[$type];

    // Les params de location sont à plat dans $_GET (jQuery a envoyé l'objet flat).
    // On retire les clés de routing et le type avant de les passer à AjaxFilter.
    $locationParams = $_GET;
    unset($locationParams['type'], $locationParams['module'], $locationParams['submod'], $locationParams['action']);

    $ajax = new AjaxFilter(urlStrRedirect("updates/updates/" . $cfg['action']),
                           $cfg['container'],
                           $locationParams,
                           $cfg['formid']);
    $ajax->display();
    echo '<div id="' . htmlspecialchars($cfg['container'], ENT_QUOTES, 'UTF-8') . '"></div>';
    return;
}

// Mode "shell" : on rend les onglets et un container vide, le contenu est chargé en AJAX au clic.
$selected_location = $_GET['selected_location'] ?? [];
?>
<div class="tabselector">
    <ul>
<?php foreach ($listsConfig as $key => $cfg): ?>
        <li id="updatesTab_<?php echo htmlspecialchars($key, ENT_QUOTES, 'UTF-8'); ?>"<?php echo $key === 'grey' ? ' class="tabactive"' : ''; ?>>
            <a href="#" data-list="<?php echo htmlspecialchars($key, ENT_QUOTES, 'UTF-8'); ?>">
                <?php echo htmlspecialchars($cfg['label'], ENT_QUOTES, 'UTF-8'); ?>
            </a>
        </li>
<?php endforeach; ?>
    </ul>
</div>

<div id="updatesListContainer"></div>

<script type="text/javascript">
(function() {
    var locationParams = <?php echo json_encode($selected_location, JSON_UNESCAPED_SLASHES); ?>;
    var sectionUrl = <?php echo json_encode(urlStrRedirect("updates/updates/ajaxUpdatesListWin")); ?>;

    function loadList(type) {
        document.querySelectorAll('.tabselector li').forEach(function(li) {
            var link = li.querySelector('a[data-list]');
            if (!link) { return; }
            li.classList.toggle('tabactive', link.dataset.list === type);
        });
        var data = Object.assign({}, locationParams || {}, { type: type });
        jQuery.ajax({
            url: sectionUrl,
            type: 'get',
            data: data,
            success: function(html) {
                jQuery('#updatesListContainer').html(html);
            }
        });
    }

    document.querySelectorAll('.tabselector a[data-list]').forEach(function(link) {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            loadList(link.dataset.list);
        });
    });

    loadList('grey');
})();
</script>
