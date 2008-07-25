<?php
/**
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

function getQueryPossibilities() {
    return myXmlCall("dyngroup.getQueryPossibilities");
}

function getPossiblesModules() {
    return myXmlCall("dyngroup.getPossiblesModules");
}

function getPossiblesCriterionsInMainModule() {
    return myXmlCall("dyngroup.getPossiblesCriterionsInMainModule");
}

function getPossiblesCriterionsInModule($moduleName) {
    return myXmlCall("dyngroup.getPossiblesCriterionsInModule", array($moduleName));
}

function getPossiblesValuesForCriterionInModule($moduleName, $criterion) {
    return myXmlCall("dyngroup.getPossiblesValuesForCriterionInModule", array($moduleName, $criterion));
}

function getPossiblesValuesForCriterionInModuleFuzzy($moduleName, $criterion, $search) {
    return myXmlCall("dyngroup.getPossiblesValuesForCriterionInModuleFuzzy", array(urldecode($moduleName), urldecode($criterion), urldecode($search)));
}

function getPossiblesValuesForCriterionInModuleFuzzyWhere($moduleName, $criterion, $search, $value2) {
    return myXmlCall("dyngroup.getPossiblesValuesForCriterionInModuleFuzzyWhere", array(urldecode($moduleName), urldecode($criterion), urldecode($search), urldecode($value2)));
}

?>
