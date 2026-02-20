<?php
/*
 * (c) 2025 Medulla, http://www.medulla-tech.io
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
 */

require("graph/navbar.inc.php");
require("modules/admin/admin/localSidebar.php");
require_once("modules/admin/includes/xmlrpc.php");
require_once("includes/PageGenerator.php");

// Vue d'ensemble de la configuration :
// - récupère les tables de config,
// - classe les sections par catégories fonctionnelles,
// - génère des liens vers parameterList.php avec contexte (filtres + onglet).

$p = new PageGenerator(_T("Configuration Management", 'admin'));
$p->setSideMenu($sidemenu);
$p->display();

echo '<link rel="stylesheet" href="modules/admin/graph/css/admin.css" type="text/css" media="screen" />';

// Récupérer la liste des tables de configuration
$tables = xmlrpc_get_config_tables();

if (!$tables || !is_array($tables)) {
    echo '<div class="alert alert-warning">' . _T("No configuration tables found", "admin") . '</div>';
    return;
}

$configurationTables = array_values(array_filter(array_unique($tables), function ($table) {
    return is_string($table) && preg_match('/_version$/', $table) !== 1;
}));
sort($configurationTables, SORT_NATURAL | SORT_FLAG_CASE);

// Index pré-calculé pour accélérer la phase de matching :
// - tableSections[table] => liste des sections,
// - tableSectionParams[table][section] => liste des noms de paramètres.
$tableSections = [];
$tableSectionParams = [];

foreach ($configurationTables as $table) {
    $rows = xmlrpc_get_config_data($table);
    $sections = [];
    $sectionParams = [];

    if ($rows && is_array($rows)) {
        foreach ($rows as $row) {
            $sectionName = trim((string)($row['section'] ?? ''));
            $paramName = trim((string)($row['nom'] ?? ''));

            if ($sectionName !== '') {
                $sections[$sectionName] = true;
                if (!isset($sectionParams[$sectionName])) {
                    $sectionParams[$sectionName] = [];
                }
                if ($paramName !== '') {
                    $sectionParams[$sectionName][$paramName] = true;
                }
            }
        }
    }

    $tableSections[$table] = array_keys($sections);
    $tableSectionParams[$table] = [];
    foreach ($sectionParams as $sectionName => $paramsMap) {
        $tableSectionParams[$table][$sectionName] = array_keys($paramsMap);
    }

}

// Taxonomie métier : chaque entrée contient des patterns regex.
// match_on_params=true active également le matching sur le nom du paramètre (colonne `nom`).
$categories = [
    [
        'id' => 'auth',
        'label' => 'Authentification',
        'entries' => [
            [
                'label' => 'LDAP',
                'patterns' => ['/ldap/i'],
            ],
            [
                'label' => 'AD',
                'patterns' => ['/(^|_)ad(_|$)/i', '/active.?directory/i'],
            ],
        ],
    ],
    [
        'id' => 'itsm',
        'label' => 'ITSM',
        'entries' => [
            [
                'label' => 'GLPI',
                'patterns' => ['/glpi/i'],
                'exclude' => ['grafana', 'provisioning_glpi', 'syncthing'],
            ],
            [
                'label' => 'ITSMNG',
                'patterns' => ['/itsmng/i', '/itsm/i'],
            ],
            [
                'label' => 'Autre',
                'patterns' => ['/itsm/i', '/servicedesk/i', '/ticket/i'],
            ],
        ],
    ],
    [
        'id' => 'security',
        'label' => 'Sécurité',
        'entries' => [
            [
                'label' => 'Certificat SSL',
                'patterns' => ['/ssl/i', '/cert/i', '/tls/i'],
                'match_on_params' => true,
            ],
            [
                'label' => 'Clé AES',
                'patterns' => ['/aes/i', '/crypto/i'],
                'match_on_params' => true,
            ],
            [
                'label' => 'Module Security',
                'patterns' => ['/^security_conf$/i', '/security/i'],
            ],
        ],
    ],
    [
        'id' => 'db-management',
        'label' => 'BDD Medulla - Management',
        'entries' => [
            [
                'label' => 'Rights Management',
                'patterns' => ['/rights?/i', '/acl/i', '/profile/i'],
            ],
            [
                'label' => 'Web Interface management (mmc.ini)',
                'patterns' => ['/mmc/i', '/web/i', '/interface/i'],
            ],
            [
                'label' => 'Par USER (Widget)',
                'patterns' => ['/user/i', '/widget/i'],
            ],
            [
                'label' => 'Par Profil ACL (gestion/users)',
                'patterns' => ['/acl/i'],
                'match_on_params' => true,
            ],
            [
                'label' => 'Gestion des profils GLPI',
                'patterns' => ['/provisioning_glpi/i'],
            ],
        ],
    ],
    [
        'id' => 'network',
        'label' => 'Network',
        'entries' => [
            [
                'label' => 'Wake on Lan Port',
                'patterns' => ['/wakeonlan/i'],
            ],
            [
                'label' => 'Cible (Relay ARS / sous-réseau / LAN / VLAN)',
                'patterns' => ['/relay/i', '/subnet/i', '/lan/i', '/vlan/i'],
            ],
            [
                'label' => 'Géoloc',
                'patterns' => ['/geo/i', '/location/i'],
            ],
        ],
    ],
    [
        'id' => 'ops-integrations',
        'label' => 'Intégrations & opérations',
        'entries' => [
            [
                'label' => 'Syncthing (serveur d’annonce)',
                'patterns' => ['/syncthing/i'],
            ],
            [
                'label' => 'Prise en main distante (Guacamole / Rustdesk)',
                'patterns' => ['/guacamole/i', '/rustdesk/i', '/remote/i'],
            ],
            [
                'label' => 'Monitoring (Grafana / autre)',
                'patterns' => ['/grafana/i', '/monitor/i'],
            ],
            [
                'label' => 'Mastering',
                'patterns' => ['/master/i', '/package.?server/i'],
                'exclude' => ['xmpp'],
            ],
            [
                'label' => 'Kiosk',
                'patterns' => ['/kiosk/i'],
            ],
            [
                'label' => 'MSC',
                'patterns' => ['/msc/i', '/deploy/i'],
            ],
            [
                'label' => 'CVE',
                'patterns' => ['/cve/i'],
                'match_on_params' => true,
            ],
            [
                'label' => 'MDM',
                'patterns' => ['/mobile/i'],
            ],
            [
                'label' => 'XMPP',
                'patterns' => ['/xmpp/i'],
                'exclude' => ['grafana_api', 'syncthing'],
            ],
            [
                'label' => 'LOG',
                'patterns' => ['/log/i', '/debug/i'],
                'match_on_params' => true,
            ],
            [
                'label' => 'Schedule Task',
                'patterns' => ['/schedul/i', '/task/i', '/cron/i', '/update/i'],
            ],
            [
                'label' => 'Config sauvegarde et restauration',
                'patterns' => ['/backup/i', '/restore/i', '/urbackup/i'],
            ],
            [
                'label' => 'Sauvegarde/Restauration Medulla Admin (Dump)',
                'patterns' => ['/dump/i', '/admin.?backup/i'],
            ],
        ],
    ],
    [
        'id' => 'others',
        'label' => 'Autres',
        'entries' => [
            [
                'label' => 'Dyngroup',
                'patterns' => ['/dyngroup/i'],
            ],
            [
                'label' => 'Medulla Server',
                'patterns' => ['/^base_conf$/i', '/medulla/i', '/mmc/i', '/server/i'],
            ],
            [
                'label' => 'Pkgs',
                'patterns' => ['/^pkgs_conf$/i', '/pkgs?/i'],
            ],
            [
                'label' => 'Imaging',
                'patterns' => ['/^imaging_conf$/i', '/imaging/i'],
            ],
        ],
    ],
];

$activeTab = isset($_GET['tab']) ? preg_replace('/[^a-zA-Z0-9_-]/', '', $_GET['tab']) : null;

$btn = new Button();

echo '<div class="container-fluid admin-config">';
echo '<h3 class="admin-config-title">Configuration globale Medulla</h3>';

echo '<div class="admin-config-tabs" role="tablist" aria-label="Catégories de configuration">';
foreach ($categories as $index => $category) {
    $isActive = ($activeTab !== null) ? ($activeTab === $category['id']) : ($index === 0);
    $activeClass = $isActive ? ' is-active' : '';
    echo '<button type="button" class="admin-config-tab' . $activeClass . '" data-tab="' . htmlspecialchars($category['id']) . '">'
        . htmlspecialchars($category['label'])
        . '</button>';
}
echo '</div>';

echo '<div class="admin-config-panels">';
foreach ($categories as $index => $category) {
    $isActivePanel = ($activeTab !== null) ? ($activeTab === $category['id']) : ($index === 0);
    echo '<section class="admin-config-panel' . ($isActivePanel ? ' is-active' : '') . '" data-panel="' . htmlspecialchars($category['id']) . '"'
        . ($isActivePanel ? '' : ' hidden')
        . '>';

    foreach ($category['entries'] as $entry) {
        // Une cible = combinaison (table, section) qui match au moins un pattern de l'entrée.
        $matchedTargets = [];

        foreach ($tableSections as $table => $sections) {
            if (!empty($sections)) {
                foreach ($sections as $sectionName) {
                    $sectionParamNames = $tableSectionParams[$table][$sectionName] ?? [];
                    $allowParamMatch = !empty($entry['match_on_params']);

                    foreach ($entry['patterns'] as $pattern) {
                        // Match de base : nom de section ou nom de table.
                        $matchesPattern = preg_match($pattern, $sectionName) === 1 || preg_match($pattern, $table) === 1;

                        // Match étendu : nom de paramètre (si explicitement activé).
                        if (!$matchesPattern && $allowParamMatch && !empty($sectionParamNames)) {
                            foreach ($sectionParamNames as $paramName) {
                                if (preg_match($pattern, $paramName) === 1) {
                                    $matchesPattern = true;
                                    break;
                                }
                            }
                        }

                        if ($matchesPattern) {
                            // Exclusions locales à l'entrée (uniquement pour l'affichage de cette liste).
                            $skip = false;
                            if (!empty($entry['exclude']) && is_array($entry['exclude'])) {
                                foreach ($entry['exclude'] as $kw) {
                                    $kw = trim((string)$kw);
                                    if ($kw === '') continue;
                                    if (stripos($table, $kw) !== false || stripos($sectionName, $kw) !== false) {
                                        $skip = true;
                                        break;
                                    }
                                    foreach ($sectionParamNames as $paramName) {
                                        if (stripos($paramName, $kw) !== false) {
                                            $skip = true;
                                            break;
                                        }
                                    }
                                    if ($skip) {
                                        $skip = true;
                                        break;
                                    }
                                }
                            }
                            if ($skip) { 
                                break; 
                                } // ne pas ajouter cette section à cette catégorie

                            $matchedTargets[] = [
                                'table' => $table,
                                'section' => $sectionName,
                            ];
                            break;
                        }
                    }
                }
                continue;
            }

            foreach ($entry['patterns'] as $pattern) {
                if (preg_match($pattern, $table) === 1) {
                    // Cas sans section : matching direct au niveau table, avec exclusions applicables.
                    $skipTable = false;
                    if (!empty($entry['exclude']) && is_array($entry['exclude'])) {
                        foreach ($entry['exclude'] as $kw) {
                            $kw = trim((string)$kw);
                            if ($kw === '') continue;
                            if (stripos($table, $kw) !== false) { $skipTable = true; break; }
                        }
                    }
                    if ($skipTable) { continue; }

                    $matchedTargets[] = [
                        'table' => $table,
                        'section' => '',
                    ];
                    break;
                }
            }
        }

        echo '<details class="admin-config-dropdown">';
        echo '<summary>' . htmlspecialchars($entry['label']) . '</summary>';
        echo '<div class="admin-config-dropdown-content">';

        if (!empty($matchedTargets)) {
            echo '<div class="admin-config-actions">';
            foreach ($matchedTargets as $target) {
                $table = $target['table'];
                $sectionName = $target['section'];
                $pluginName = str_replace('_conf', '', $table);
                $label = ucfirst($pluginName);
                $editParams = ['table' => $table];
                if ($sectionName !== '') {
                    $editParams['section'] = $sectionName;
                }

                if (!empty($entry['patterns']) && is_array($entry['patterns'])) {
                    // Les patterns sont encodés pour être transmis à la liste AJAX
                    // et conserver le périmètre d'affichage côté écran de détail.
                    $patternsJson = json_encode(array_values($entry['patterns']));
                    if ($patternsJson !== false) {
                        $encodedPatterns = rtrim(strtr(base64_encode($patternsJson), '+/', '-_'), '=');
                        if ($encodedPatterns !== '') {
                            $editParams['entry_patterns'] = $encodedPatterns;
                        }
                    }
                }

                // Mémorise l'onglet source pour restaurer l'état au retour.
                $editParams['back_tab'] = $category['id'];

                $editUrl = urlStrRedirect("admin/admin/parameterList", $editParams);
                $buttonLabel = $sectionName !== ''
                    ? sprintf('%s / %s', $label, $sectionName)
                    : sprintf('%s (%s)', $label, $table);
                $buttonText = htmlspecialchars($buttonLabel, ENT_QUOTES);
                echo '<div class="admin-config-action">' . $btn->getOnClickButton($buttonText, $editUrl) . '</div>';
            }
            echo '</div>';
        } else {
            echo '<p class="admin-config-placeholder">Aucune section associée pour le moment.</p>';
        }

        echo '</div>';
        echo '</details>';
    }

    echo '</section>';
}
echo '</div>';

echo '</div>';
?>
<script>
document.addEventListener("DOMContentLoaded", function () {
    const tabs = document.querySelectorAll(".admin-config-tab");
    const panels = document.querySelectorAll(".admin-config-panel");

    tabs.forEach(function (tab) {
        tab.addEventListener("click", function () {
            const target = tab.getAttribute("data-tab");

            tabs.forEach(function (item) {
                item.classList.remove("is-active");
            });
            tab.classList.add("is-active");

            panels.forEach(function (panel) {
                const isTarget = panel.getAttribute("data-panel") === target;
                panel.hidden = !isTarget;
                panel.classList.toggle("is-active", isTarget);
            });

            const url = new URL(window.location);
            url.searchParams.set('tab', target);
            history.replaceState(null, '', url.toString());
        });
    });
});
</script>