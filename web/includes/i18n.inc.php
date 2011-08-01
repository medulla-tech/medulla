<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2008 Mandriva, http://www.mandriva.com
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
?>
<?php

/**
 * provide internationalization for the whole program
 */



if (!function_exists('_T')) {
    /**
    * alias for dgettext
    * if domain not specify, use $_GET['module'] instead
    **/
    function _T($var,$domain = null) {
        if (($domain == null) && !empty($_GET['module'])) {
            $domain = $_GET['module'];
        }
        return dgettext($domain,$var);
    }

    /**
     * return supported locales as an array
     */
    function getArrLocale() {
        $res = array("C" => _("english"),
                     "da_DK" => _("danish"),
                     "de_DE" => _("german"),
                     "es_ES" => _("spanish"),
                     "fr_FR" => _("french"),
                     "it_IT" => _("italian"),
                     "nb_NO" => _("norwegian"),
                     "pl_PL" => _("polish"),
                     "pt_BR" => _("brazilian"),
                     "ru_RU" => _("russian"));
        return $res;
    }

    /**
     * Link a supported locale to a supported locale string sent by a browser
     * via HTTP_ACCEPT_LANGUAGE
     */
    function getArrLocaleShort() {
        return array("en" => "C",
                     "da" => "da_DK",
                     "de" => "de_DE",
                     "es" => "es_ES",
                     "fr" => "fr_FR",
                     "it" => "it_IT",
                     "nb" => "nb_NO",
                     "no" => "nb_NO",
                     "pl" => "pl_PL",
                     "pt-br" => "pt_BR",
                     "ru" => "ru_RU");
    }
}


/* Set language to use in the interface */
if (!isset($_SESSION['lang'])) {
    if (!isset($_COOKIE['lang'])) {
        /*
          If no cookie with the previously used language is found,
          auto-detect it
        */
        $browserLanguage = explode(',',$_SERVER['HTTP_ACCEPT_LANGUAGE']);
        $browserLanguage = strtolower(rtrim($browserLanguage[0]));
        $localeShort = getArrLocaleShort();
        $found = isset($localeShort[$browserLanguage]);
        if (!$found) {
            /* Keep only the two first letters of a language, and try to match
               again. */
            $browserLanguage = strtolower(substr($browserLanguage,0,2));
            $found = isset($localeShort[$browserLanguage]);
        }
        if ($found) {
            $_SESSION["lang"] = $localeShort[$browserLanguage];
        } else {
            $_SESSION['lang'] = 'C';
        }
    } else {
        $_SESSION['lang'] = $_COOKIE['lang'];        
    }
}

if ($_SESSION["lang"] == "C") {
    setlocale(LC_ALL, $_SESSION['lang']);
} else {
    setlocale(LC_ALL, $_SESSION['lang'] . ".UTF-8");
}

if (empty($_SESSION["supportModList"])) { //if supportModList not available
					      //ex: not logged
	$_SESSION["supportModList"] = array();
}

foreach ($_SESSION["supportModList"] as $mod) { //bind all supported mod list for
                                                //dgettext function and _T() alias
    bindtextdomain ($mod, dirname(__FILE__)."/../modules/$mod/locale");
}

textdomain ("base"); //define default domain for gettext and _() alias

?>
