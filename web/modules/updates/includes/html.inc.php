<?php
/**
 * (c) 2024 Siveo, http://siveo.net/
 *
 * $Id$
 *
 * This file is part of Management Console (MMC).
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

 function colorconf($conf)
 {
     $colorDisplay = array( "#ff0000","#ff3535","#ff5050","#ff8080","#ffA0A0","#c8ffc8","#97ff97","#64ff64","#2eff2e","#00ff00", "#00ff00");
     return $colorDisplay[intval(($conf - ($conf % 10)) / 10)];
 }
 
?>