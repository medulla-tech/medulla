<?php

/**
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

/* Set PHP assert options values, and add a callback */

assert_options(ASSERT_ACTIVE, 1);
assert_options(ASSERT_WARNING, 1);
assert_options(ASSERT_BAIL, 1);
assert_options(ASSERT_QUIET_EVAL, 1);

/* Callback called when an assert failed */
function mmc_assert_handler($file, $line, $code) {
    echo("<hr>Assertion Failed:
        File '$file'<br />
        Line '$line'<br />
        Code '$code'<br /><hr />");
}

/* Set up the callback */
assert_options(ASSERT_CALLBACK, 'mmc_assert_handler');

?>