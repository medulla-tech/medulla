<?php

/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
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

class multicol extends HtmlElement {

    public $cols;
    public $widths;
    public $valigns;

    function multicol() {
        $this->cols = array();
        $this->widths = array();
        $this->paddings = array();
    }

    function add($col, $params = array(), $arrParam = array()) {
        $this->cols[] = $col;
        $def_params = array(
            'padding' => '0',
            'valign' => 'middle',
            'width' => 'auto'
        );
        $params = array_merge($def_params, $params);
        $this->widths[] = $params['width'];
        $this->paddings[] = $params['padding'];
        $this->valigns[] = $params['valign'];
        $this->arrParams[] = $arrParam;
        return $this;
    }

    function display($arrParam = array()) {
        /* print '<table style="border:0"><tr><td>';
          $col = $this->cols[0];
          $col->display();
          print '</td></tr></table>';
          return; */
        if (count($this->cols) == 0)
            return;

        // Table
        print '<table style="border:0"><tr>';

        // Display all columns
        for ($i = 0; $i < count($this->cols); $i++) {

            $col = $this->cols[$i];
            $width = is_int($this->widths[$i]) ? $this->widths[$i] . 'px' : $this->widths[$i];
            $padding = is_int($this->paddings[$i]) ? $this->paddings[$i] . 'px' : $this->paddings[$i];
            $valign = $this->valigns[$i];

            print "<td style=\"border:0;width:$width;padding:$padding;vertical-align:$valign\">";
            $col->display();
            print '</td>';
        }

        print '</tr></table>';
        return $this;
    }

}

class raphaelPie extends HtmlElement {

    public $id;
    public $title = 'Example title';
    public $legendpos = 'east';
    public $data_array = array();

    function __construct($id) {
        $this->id = $id;
        //$this->colors = array("#000", "#73d216", "#ef2929", "#003399");
    }

    function addData($value, $label, $color, $href = '#') {
        $this->data_array[] = array(
            'value' => $value,
            'label' => $label,
            'color' => $color,
            'href' => $href
        );
        return $this;
    }

    function display($arrParam = array()) {

        function cmp_value($a, $b) {
            if ($a['value'] == $b['value'])
                return 0;
            return ($a['value'] > $b['value']) ? -1 : 1;
        }

        function extract_col(&$item, $key, $col) {
            $item = $item[$col];
        }

        function extract_value($item) {
            return $item['value'];
        }

        // Removing null values
        $this->data_array = array_filter($this->data_array, 'extract_value');
        // Sorting data_array
        usort($this->data_array, 'cmp_value');

        $_data = $this->data_array;
        $_labels = $this->data_array;
        $_colors = $this->data_array;
        $_links = $this->data_array;

        // Extacting cols
        array_walk($_data, 'extract_col', 'value');
        array_walk($_labels, 'extract_col', 'label');
        array_walk($_colors, 'extract_col', 'color');
        array_walk($_links, 'extract_col', 'href');

        // Ensure data are ints
        $_data = array_map('intval', $_data);

        $_data = json_encode(array_values($_data));
        $_labels = json_encode(array_values($_labels));
        $_colors = json_encode(array_values($_colors));
        $_links = json_encode(array_values($_links));

        echo <<< SPACE
        <div id="$this->id" style="height:250px;"></div>
        <script type="text/javascript">
        var    r = Raphael("$this->id"),
                radius = 70,
                margin = 10,
                x = 100,
                y = 100;


        var data = $_data,
            legend = $_labels,
            colors = $_colors,
            href = $_links,
            title = '$this->title';

        /*r.text(5, y - radius - 10, title)
         .attr({ font: "12px sans-serif" })
         .attr({ "text-anchor": "start" });*/
        pie = r.piechart(x, y, radius, data,
                   {
                       colors: colors,
                        legendpos: "$this->legendpos",
                        'legend': legend,
                        strokewidth : 1.5
                    })
         .hover(function () {
            this.sector.stop();
            this.sector.animate({ transform: 's1.1 1.1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

            if (this.label) {
                this.label[0].stop();
                this.label[0].attr({ r: 7.5 });
                this.label[1].attr({ "font-weight": 800 });
            }
         }, function () {
            this.sector.animate({ transform: 's1 1 ' + this.cx + ' ' + this.cy }, 800, "elastic");

            if (this.label) {
                this.label[0].animate({ r: 5 }, 500, "bounce");
                this.label[1].attr({ "font-weight": 400 });
            }
         });

        y += (radius * 2) + margin + 5;

        r.setSize(200, (radius * 1 + margin) + 200);
        // Legend
        /*jQuery('#$this->id').append('<ul></ul>');
        for (var i = 0; i < legend.length; i++) {
            jQuery('#$this->id ul').append(
                '<li style="color: ' + colors[i]  + '"><span style="color: #000">' + legend[i]
                + '<a href="' + href[i] + '"><img title="' +
                '" style="height: 10px; padding-left: 3px;" src="img/other/machine_down.svg" /></a></span></li>'
            );
        }*/
        </script>
SPACE;
    }

}
?>
