<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2009 Mandriva, http://www.mandriva.com
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

function __web_def_in_session($option) {
    if (!isset($_SESSION["imaging.".$option])) {
        $_SESSION["imaging.".$option] = xmlCall("imaging.get_web_def_" . $option);
    }
    return $_SESSION["imaging.".$option];
}

function web_def_date_fmt() {
    return __web_def_in_session("date_fmt");
}


function web_def_image_hidden() {
    #return __web_def_in_session("image_hidden");
}

function web_def_image_hidden_WOL() {
    #return __web_def_in_session("image_hidden_WOL");
}

function web_def_image_default() {
    #return __web_def_in_session("image_default");
}

function web_def_image_default_WOL() {
    #return __web_def_in_session("image_default_WOL");
}

function web_def_service_hidden() {
    #return __web_def_in_session("service_hidden");
}

function web_def_service_hidden_WOL() {
    #return __web_def_in_session("service_hidden_WOL");
}

function web_def_service_default() {
    #return __web_def_in_session("service_default");
}

function web_def_service_default_WOL() {
    #return __web_def_in_session("service_default_WOL");
}

?>
