<?php

/**
 * (c) 2013 Mandriva, http://www.mandriva.com
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */
class MultipleSelect extends SelectItem {

    function setSelected($elemnt) {
        if (isset($this->selected))
            $this->selected[] = $elemnt;
        else
            $this->selected = array($elemnt);
    }

    function content_to_string($paramArray = null) {
        if (!isset($this->elementsVal)) {
            $this->elementsVal = $this->elements;
        }

        // if value... set it
        if (isset($paramArray["value"])) {
            $this->setSelected($paramArray["value"]);
        }
        $ret = '';
        foreach ($this->elements as $key => $item) {
            if (in_array($this->elementsVal[$key], $this->selected)) {
                $selected = 'selected="selected"';
            } else {
                $selected = "";
            }
            $ret .= "\t<option value=\"" . $this->elementsVal[$key] . "\" $selected>$item</option>\n";
        }
        return $ret;
    }

    function to_string($paramArray = null) {
        $ret = "<select multiple=\"true\" ";
        if ($this->style) {
            $ret .= " class=\"" . $this->style . "\"";
        }
        if ($this->jsFunc) {
            $ret .= " onchange=\"" . $this->jsFunc . "(";
            if ($this->jsFuncParams) {
                $ret .= implode(", ", $this->jsFuncParams);
            }
            $ret .= "); return false;\"";
        }
        $ret .= " name=\"" . $this->id . "[]\" id=\"" . $this->id . "\">\n";
        $ret .= $this->content_to_string($paramArray);
        $ret .= "</select>";
        return $ret;
    }

}

class multifieldTpl extends AbstractTpl {

    var $fields;

    function multifieldTpl($fields) {
        $this->fields = $fields;
    }

    function display($arrParam) {

        if (!isset($this->fields))
            return;

        $separator = isset($arrParam['separator']) ? $arrParam['separator'] : ' &nbsp;&nbsp; ';

        for ($i = 0; $i < count($this->fields); $i++) {
            if (count($arrParam[$i])) {
                $this->fields[$i]->display($arrParam[$i]);
            } else {
                $this->fields[$i]->display(array('value' => ''));
            }
            echo $separator;
        }
    }

}

class textTpl extends AbstractTpl {

    function textTpl($text) {
        $this->text = $text;
    }

    function display($arrParam) {
        echo $this->text;
    }

}

class dateInputTpl extends InputTpl {

    function dateInputTpl($name, $regexp='/(0[1-9]|[12][0-9]|3[01])\/(0[1-9]|1[012])\/(\d\d\d\d)/') {
        # TODO: handle localized regexp for date format
        $this->InputTpl($name);
        $this->fieldType = "text";
    }

    function display($arrParam) {
        $arrParam['disabled'] = ' style="width:80px;" ';
        parent::display($arrParam);
    }

}

class periodInputTpl extends multifieldTpl {

    function periodInputTpl($from_txt, $from_id, $to_txt, $to_id) {
        $this->fields = array(
            new textTpl($from_txt),
            new dateInputTpl($from_id),
            new textTpl($to_txt),
            new dateInputTpl($to_id),
            new HiddenTpl($from_id . "_timestamp"),
            new HiddenTpl($to_id . "_timestamp"),
        );

        $months = json_encode(array(_T("January", "report"),
                        _T("February", "report"),
                        _T("March", "report"),
                        _T("April", "report"),
                        _T("May", "report"),
                        _T("June", "report"),
                        _T("July", "report"),
                        _T("August", "report"),
                        _T("September", "report"),
                        _T("October", "report"),
                        _T("November", "report"),
                        _T("December", "report")));
        $monthsShort = json_encode(array(_T("Jan", "report"),
                             _T("Feb", "report"),
                             _T("Mar", "report"),
                             _T("Apr", "report"),
                             _T("May", "report"),
                             _T("Jun", "report"),
                             _T("Jul", "report"),
                             _T("Aug", "report"),
                             _T("Sep", "report"),
                             _T("Oct", "report"),
                             _T("Nov", "report"),
                             _T("Dec", "report")));
        $days = json_encode(array(_T("Sunday", "report"),
                      _T("Monday", "report"),
                      _T("Tuesday", "report"),
                      _T("Wednesday", "report"),
                      _T("Thirsday", "report"),
                      _T("Friday", "report"),
                      _T("Saturday", "report")));
        $daysShort = json_encode(array(_T("Sun", "report"),
                           _T("Mon", "report"),
                           _T("Tue", "report"),
                           _T("Wed", "report"),
                           _T("Thi", "report"),
                           _T("Fri", "report"),
                           _T("Sat", "report")));
        $daysMin = json_encode(array(_T("Su", "report"), _T("Mo", "report"), _T("Tu", "report"),
                         _T("We", "report"), _T("Th", "report"), _T("Fr", "report"),
                         _T("Sa", "report")));
        $weekHeader = json_encode(_T("Wk", "report"));
        $dateFormat = json_encode(_T("yy/mm/dd", "report"));

        echo <<< JQUERY
            <script>
            jQuery(function() {
                jQuery("#$from_id").click(function() {
                    jQuery("#$from_id").datepicker("show");
                });
                jQuery("#$from_id").datepicker({
                    defaultDate: -2,
                    changeMonth: true,
                    showWeek: true,
                    showAnim: 'slideDown',
                    maxDate: -2,
                    monthNames: $months,
                    monthNamesShort: $monthsShort,
                    dayNames: $days,
                    dayNamesShort: $daysShort,
                    dayNamesMin: $daysMin,
                    weekHeader: $weekHeader,
                    dateFormat: $dateFormat,
                    onClose: function( selectedDate ) {
                        toid_minDate = new Date(selectedDate);
                        toid_minDate.setDate(toid_minDate.getDate() + 1);
                        jQuery("#$to_id").datepicker( "option", "minDate", toid_minDate);
                        var timestamp = new Date(selectedDate).valueOf() / 1000;
                        jQuery("input[name=$from_id" + "_timestamp]").val(timestamp);
                    }
                }).datepicker('setDate', '-2');
                jQuery("#$to_id").datepicker({
                    defaultDate: -1,
                    changeMonth: true,
                    showWeek: true,
                    showAnim: 'slideDown',
                    maxDate: -1,
                    monthNames: $months,
                    monthNamesShort: $monthsShort,
                    dayNames: $days,
                    dayNamesShort: $daysShort,
                    dayNamesMin: $daysMin,
                    weekHeader: $weekHeader,
                    dateFormat: $dateFormat,
                    onClose: function( selectedDate ) {
                        var timestamp = new Date(selectedDate).valueOf() / 1000;
                        jQuery("input[name=$to_id" + "_timestamp]").val(timestamp);
                    }
                }).datepicker('setDate', '-1');
            });
            </script>
JQUERY;
    }

    function display($arrParam) {
        /*
         * Set default values for this class
         * $from_id_timestamp is set by default to now() - 2 days
         * $to_id_timestamp is set by default to yesterday
         *
         * We need for these 2 values timestamp at 00:00:00
         */

        $from_ts = time() - 86400 * 2;
        $to_ts = time() - 86400;

        // Getting timestamp for these 2 values at 00:00:00
        $from_id_timestamp = mktime(0, 0, 0, date('m', $from_ts), date('d', $from_ts), date('Y', $from_ts));
        $to_id_timestamp = mktime(0, 0, 0, date('m', $to_ts), date('d', $to_ts), date('Y', $to_ts));
        $arrParam = array(
            array(), // from_txt
            array(), // from_id
            array(), // to_txt
            array(), // to_id
            array('value' => $from_id_timestamp, 'hide' => True),
            array('value' => $to_id_timestamp, 'hide' => True),
        );
        parent::display($arrParam);
    }

}

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

class ReportSVG extends HtmlElement {
    /*
     * Instanciate ReportSVG
     *
     * @param $indicator: indicator of svg file
     * @type $indicator: str
     *
     * @param $params: params to get svg file from python files:
     *      array(
     *      'mmc plugin name',
     *      'report class name',
     *      'method class to get svg file',
     *      'some args'
     *      )
     *  @type $params: array
     *
     *  @return: SpanElement with SVG graphic
     */

    function ReportSVG($indicator, $params) {
        $_SESSION['svg_files'][$indicator] = $params;
        $_SESSION['svg_files'][$indicator][4]['render'] = 'png';
        $this->mmc_plugin = $params[0];
        $this->class = $params[1];
        $this->method = $params[2];
        $this->args = $params[3];
        $this->kargs = $params[4];
        $this->indicator = $indicator;
    }

    function display($arrParam = array()) {
        $svg = get_report_datas($this->mmc_plugin, $this->class, $this->method, $this->args, $this->kargs);
        $result = new SpanElement($svg . '<br /><a href="' . urlStrRedirect("report/report/get_file", array('type' => 'svg', 'svg' => $this->indicator)) . '">' . 'Download me !' . '</a>');
        print $result->display();
    }

}

class ValueCheckboxTpl extends CheckboxTpl {
    /*
     * With this class, we can set values to checkboxes
     * Example:
     *   foreach ($sections as $section) {
     *       $f->add(new TrFormElement(
     *           $section['title'], new ValueCheckboxTpl("selected_sections[]")), array("value" => $section['name'])
     *       );
     *   }
     *
     * $_POST['selected_sections'] will be an array with checked checkboxes
     */

    function display($arrParam = array()) {
        if (empty($arrParam))
            $arrParam = $this->options;
        if (!isset($arrParam['extraArg'])) {
            $arrParam["extraArg"] = '';
        }
        print '<input value=' . $arrParam["value"] . ' name="' . $this->name . '" id="' . $this->name . '" type="checkbox" class="checkbox" ' . $arrParam["extraArg"];
        if ($this->jsFunc) {
            print " onchange=\"" . $this->jsFunc . "(); return false;\"";
        }
        print ' />';
        if (isset($this->rightlabel))
            print $this->rightlabel . "\n<br/>\n";
    }

}

?>
