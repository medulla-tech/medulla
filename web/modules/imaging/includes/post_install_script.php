<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2010 Mandriva, http://www.mandriva.com
 *
 * $Id$
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

function get_post_install_scripts($f, $post_install_scripts, $post_installs) {
    $already_orders = array();
    $elt = array("id_None" => _T("Not selected", "imaging"));
    $elt_values = array("id_None"=> "None");
    $h_pis = array();
    foreach ($post_install_scripts as $lpis) {
        $h_pis[$lpis['imaging_uuid']] = $lpis;
        $already_orders[$lpis['order']] = True;
    }
    $i = 0;
    foreach ($post_installs as $pis) {
        $elt["id_".$i] = "$i";
        $elt_values["id_".$i] = "$i";
        $i += 1;
    }
    $a_label = array();
    $a_desc = array();
    $a_order = array();
    $a_pis_id = array();
    foreach ($post_installs as $pis) {
        $a_pis_id[] = "order_".$pis['imaging_uuid'];
        $a_label[] = $pis['default_name'];
        $a_desc[] = $pis['default_desc'];

        $order = new MySelectItem("order_".$pis['imaging_uuid'], "exclusive_orders");

        $order = new MySelectItem("order_".$pis['imaging_uuid'], "exclusive_orders");
        $order->setJsFuncParams(array('this'));
        $order->setElements($elt);
        $order->setElementsVal($elt_values);
        if (array_key_exists($pis['imaging_uuid'], $h_pis)) {
            $order->setSelected($h_pis[$pis['imaging_uuid']]['order']);
        } else {
            $order->setSelected("None");
        }
        $a_order[] = $order;
    }
    $l = new MyListInfos($a_label, _T("Name", "imaging"));
    $l->setPostInstallCount(count($post_installs));
    $l->addExtraInfo($a_desc, _T("Description", "imaging"));
    $l->addExtraInfo($a_order, _T("Order", "imaging"));

    $l->disableFirstColumnActionLink();
    $l->setRowsPerPage(count($post_installs));

    $f->add($l);

    print_exclusive_orders_js($a_pis_id);
    return $f;
}
function print_exclusive_orders_js($a_pis_id) {
?>
    <script type='text/javascript'>
    <!--
        function exclusive_orders(self_element) {
            var all_selects = ['<?php echo  implode("', '", $a_pis_id);  ?>'];
            for (var i = 0; i < all_selects.length; i++) {
                var sel = all_selects[i];
                var elem = document.getElementById(sel);
                if (self_element.name != elem.name) {
                    if (self_element.value == elem.value && self_element.value != 'None') {
                        self_element.value = "None";
                        alert("<?php echo  _T("This value is already taken, please only put one element for each order.", "imaging"); ?>");
                        break;
                    } else if (self_element.value == 'None') {
                        break;
                    }
                }
            }
        }
    -->
    </script>
<?php
}

global $conf;
class MyListInfos extends ListInfos {
    function setPostInstallCount($value) {
        $this->post_install_count = $value;
    }

    function display() {
        if (isset($this->post_install_count)) {
            $maxperpage = $conf["global"]["maxperpage"];
            $conf["global"]["maxperpage"] = $this->post_install_count;
        }

        $ret = $this->drawTable(0);

        $conf["global"]["maxperpage"] = $maxperpage;
        return $ret;
    }
}

class MySelectItem extends SelectItem {
    function __toString() {
        return $this->to_string();
    }
}

?>

