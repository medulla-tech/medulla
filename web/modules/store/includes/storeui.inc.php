<?php
/*
 * (c) 2024-2026 Medulla, http://www.medulla-tech.io
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
 * Store - helpers UI partages (labels/badges OS, regroupement par produit).
 */

if (!function_exists('store_os_label')) {

    function store_os_label($os)
    {
        switch (strtolower($os)) {
            case 'win': return 'Windows';
            case 'linux': return 'Linux';
            case 'mac': return 'macOS';
            default: return $os !== '' ? ucfirst($os) : '';
        }
    }

    function store_os_badge($os, $href = null)
    {
        $os = strtolower($os);
        $map = array('win' => 'win', 'windows' => 'win', 'linux' => 'linux', 'mac' => 'mac', 'macos' => 'mac');
        $label = store_os_label($os);
        if (!isset($map[$os])) {
            return '<span style="font-size:11px;color:#888;">' . htmlspecialchars($label) . '</span>';
        }
        $img = '<img src="modules/store/graph/img/os/' . $map[$os] . '.svg" width="18" height="18" '
             . 'title="' . htmlspecialchars($label) . '" alt="' . htmlspecialchars($label) . '" '
             . 'style="vertical-align:middle;margin:0 3px;opacity:.7;"/>';
        if ($href !== null && $href !== '') {
            return '<a href="' . htmlspecialchars($href) . '" title="' . htmlspecialchars(_T('Deploy', 'store') . ' ' . $label)
                 . '" style="text-decoration:none;">' . $img . '</a>';
        }
        return $img;
    }

    function store_os_badges($osArr, $allOs, $hrefs = array())
    {
        $present = array_map('strtolower', $osArr);
        $out = '';
        foreach ($allOs as $o) {
            if (in_array($o, $present)) {
                $out .= store_os_badge($o, isset($hrefs[$o]) ? $hrefs[$o] : null);
            } else {
                $out .= '<span style="display:inline-block;width:24px;"></span>';
            }
        }
        return $out !== '' ? $out : '-';
    }

    function store_group_by_product($builds, $subscribedIds = array())
    {
        $products = array();
        foreach ($builds as $b) {
            $key = $b['name'];
            if (!isset($products[$key])) {
                $products[$key] = array(
                    'name'       => $b['name'],
                    'vendor'     => $b['vendor'] ?? '',
                    'category'   => $b['category'] ?? '',
                    'short_desc' => $b['short_desc'] ?? '',
                    'os'         => array(),
                    'build_ids'  => array(),
                    'versions'   => array(),
                    'uuids'      => array(),
                    'subscribed' => 0,
                    'deployed'   => false,
                    'builds'     => array(),
                );
            }
            $os = strtolower($b['os'] ?? '');
            if ($os !== '' && !in_array($os, $products[$key]['os'])) { $products[$key]['os'][] = $os; }
            $products[$key]['build_ids'][] = intval($b['id']);
            if (!empty($b['version']))      { $products[$key]['versions'][$os] = $b['version']; }
            if (!empty($b['package_uuid'])) { $products[$key]['uuids'][$os] = $b['package_uuid']; }
            if (in_array($b['id'], $subscribedIds)) { $products[$key]['subscribed']++; }
            if (!empty($b['deployed_at']))  { $products[$key]['deployed'] = true; }
            $products[$key]['builds'][] = $b;
        }
        return array_values($products);
    }

    function store_catalog_os($products)
    {
        $canonical = array('win', 'linux', 'mac');
        $out = array();
        foreach ($canonical as $o) {
            foreach ($products as $p) {
                if (in_array($o, $p['os'])) { $out[] = $o; break; }
            }
        }
        foreach ($products as $p) {
            foreach ($p['os'] as $o) {
                if (!in_array($o, $out)) { $out[] = $o; }
            }
        }
        return $out;
    }

    function store_product_version($prod)
    {
        $uniq = array_values(array_unique(array_values($prod['versions'])));
        if (count($uniq) === 1) {
            return '<span style="background:#e9ecef;padding:2px 8px;border-radius:4px;font-family:monospace;font-size:12px;">'
                 . htmlspecialchars($uniq[0]) . '</span>';
        }
        return '-';
    }

    // Icone d'action standard (td.action) mais qui ouvre une popup JS au lieu de naviguer.
    class StoreDeployAction extends ActionItem
    {
        public function displayWithRight($param, $extraParams = array())
        {
            $name = isset($extraParams['name']) ? $extraParams['name'] : '';
            $options = isset($extraParams['options']) ? $extraParams['options'] : '[]';
            echo '<li class="' . $this->classCss . '">'
               . '<a title="' . htmlspecialchars($this->desc, ENT_QUOTES) . '" href="#" onclick="storeOpenDeploy(this); return false;"'
               . ' data-name="' . htmlspecialchars($name, ENT_QUOTES) . '"'
               . ' data-options="' . htmlspecialchars($options, ENT_QUOTES) . '">&nbsp;</a></li>';
        }
    }

    class StoreUnsubAction extends ActionItem
    {
        public function displayWithRight($param, $extraParams = array())
        {
            $ids = isset($extraParams['ids']) ? $extraParams['ids'] : '';
            echo '<li class="' . $this->classCss . '">'
               . '<a title="' . htmlspecialchars($this->desc, ENT_QUOTES) . '" href="#" onclick="storeUnsubscribe(this); return false;"'
               . ' style="background-image:url(\'img/actions/remove.svg\');"'
               . ' data-ids="' . htmlspecialchars($ids, ENT_QUOTES) . '">&nbsp;</a></li>';
        }
    }
}
?>
