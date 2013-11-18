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

    var $cols;
    var $widths;

    function multicol() {
        $this->cols = array();
        $this->widths = array();
        $this->paddings = array();
    }

    function add($col, $width = 0, $padding = 0, $arrParam = array()) {
        $this->cols[] = $col;
        $this->widths[] = $width;
        $this->paddings[] = $padding;
        $this->arrParams[] = $arrParam;
        return $this;
    }

    function display($arrParam = array()) {
        if (count($this->cols) == 0)
            return;

        // Table
        print '<table style="border:0"><tr>';

        // Display all columns
        for ($i = 0; $i < count($this->cols); $i++) {

            $col = $this->cols[$i];
            $width = is_int($this->widths[$i]) ? $this->widths[$i] . 'px' : $this->widths[$i];
            $padding = is_int($this->paddings[$i]) ? $this->paddings[$i] . 'px' : $this->paddings[$i];

            print "<td style=\"border:0;width:$width;padding:$padding\">";
            $col->display($this->arrParams[$i]);
            print '</td>';
        }

        print '</tr></table>';
        return $this;
    }

}

class raphaelPie extends HtmlElement {

    public $id;
    public $title = 'Example title';
    public $data = array();
    public $labels = array();
    public $colors = array();
    public $links = array();

    function __construct($id) {
        $this->id = $id;
        //$this->colors = array("#000", "#73d216", "#ef2929", "#003399");
    }

    function display($arrParam = array()) {


        $_data = json_encode($this->data);
        $_labels = json_encode($this->labels);
        $_colors = json_encode($this->colors);
        $_links = json_encode($this->links);


        echo <<< SPACE
        <div id="$this->id" style="height:250px;"></div>
        <script type="text/javascript">
        var    r = Raphael("$this->id"),
                radius = 70,
                margin = 10,
                x = 100,
                y = 100;


        var data = $_data,
            //createGroupText = $createGroupText,
            legend = $_labels,
            colors = $_colors,
            href = $_links,
            title = '$this->title';

        /*r.text(5, y - radius - 10, title)
         .attr({ font: "12px sans-serif" })
         .attr({ "text-anchor": "start" });*/
        data = getPercentageData(data);
        pie = r.piechart(x, y, radius, data,
                   {colors: colors, legendpos: "east", 'legend': legend})
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

        r.setSize(300, (radius * 1 + margin) + 100);
        // Legend
        /*jQuery('#$this->id').append('<ul></ul>');
        for (var i = 0; i < legend.length; i++) {
            jQuery('#$this->id ul').append(
                '<li style="color: ' + colors[i]  + '"><span style="color: #000">' + legend[i]
                + '<a href="' + href[i] + '"><img title="' +
                '" style="height: 10px; padding-left: 3px;" src="img/machines/icn_machinesList.gif" /></a></span></li>'
            );
        }*/
        </script>
SPACE;
    }

}

?>
