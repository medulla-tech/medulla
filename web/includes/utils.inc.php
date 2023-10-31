<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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

/* Returns the first logo found in img/logo */
function getMMCLogo()
{
    $basedir = "img/logo/";
    $logos = scandir($basedir);
    // remove . and .. entries
    $logos = array_slice($logos, 2);
    if (!is_file($basedir . $logos[0])) {
        return false;
    }
    return $basedir . $logos[0];
}

function _startsWith($haystack, $needle)
{
    return !strncmp($haystack, $needle, strlen($needle));
}

function startsWith($haystack, $needle)
{
    if (is_array($needle)) {
        foreach($needle as $item) {
            if (_startsWith($haystack, $item)) {
                return true;
            }
        }
        return false;
    }
    return _startsWith($haystack, $needle);
}

function endsWith($haystack, $needle)
{
    $length = strlen($needle);
    if ($length == 0) {
        return true;
    }

    return (substr($haystack, -$length) === $needle);
}

function safeCount($toCount)
{
    if (is_countable($toCount)) {
        return count($toCount);
    } elseif (is_string($toCount)) {
        return strlen($toCount);
    } else {
        return 0;
    }
}
