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
class ValidateButtonTpl extends HtmlElement {
    var $class = '';
    var $cssClass = 'btn';

    function __construct($id, $value, $class='', $infobulle='', $params = array()) {
        $this->id = $id;
        $this->value = $value;
        $this->class = $class;
        $this->infobulle = $infobulle;
        $this->params = $params;
        $this->style='';
    }

    function setstyle($sty){
        $this->style=$sty;
    }

    function setClass($class) {
        $this->cssClass = $class;
    }

    function display($arrParam = array()) {
        if (isset($this->id,$this->value))
            printf('<input id="%s" title="%s" type="button" value="%s" class="%s %s" />',
                $this->id,
                $this->infobulle,
                $this->value,
                $this->cssClass,
                $this->class);
    }
}
?>
