<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?

function printSidebarCss($submod,$action) {
    echo "#sidebar ul.$submod li#$action a {\n"; 
    echo "        background-color: #FFF;\n";
    echo "        color: #666;\n";
    echo "        border-right: 1px solid #FFF;\n";
    echo "}\n";
    echo "\n";
    echo "#sidebar ul.$submod li#$action a:hover {\n"; 
    echo "        color: #666;\n";
    echo "}\n";
}

function printNavbarCss ($module)
{
    $css = "modules/" . $_GET["module"] ."/graph/" . $_GET["submod"] . "/index.css";
    if (file_exists($css) && $_GET["module"] != "base" && $_GET["module"] != "samba") include($css);
    else {
        echo "#navbar ul li#$module { width: 70px; }\n";

        echo "#navbar ul li#$module a {\n";
        echo "	border-top: 2px solid #D8D8D7;\n";
        echo "	border-left: 1px solid #B2B2B2;\n";
        echo "	border-right: 1px solid #B2B2B2;\n";
        echo "	color: #EE5010;\n";
        echo "	background-color: #F2F2F2;\n";
        echo "	padding-top: 48px;\n";
        echo "  background-position: 50% -132px;\n";
        echo "	}\n\n";
        
        echo "#navbar ul li#$module a:hover {\n";
        echo " color: #999;\n";
        echo " background-position: 50% -132px;}\n";
    }
}

printNavbarCss($_GET["module"]);
printNavbarCss($_GET["submod"]);

?>
