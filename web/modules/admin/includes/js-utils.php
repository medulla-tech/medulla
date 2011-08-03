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

?>

<script type="text/javascript">

//Global Declarations
var ie = (document.all) ? true : false;


// Hides Elements by object Class
function hideClass(objClass) {
  var elements = (ie) ? document.all : document.getElementsByTagName('*');
  for (i=0; i<elements.length; i++){
    if (elements[i].className == objClass)
      {
	elements[i].style.display = "none";
      }
  }
}

// Show Elements by object Class
function showClass(objClass){
  var elements = (ie) ? document.all : document.getElementsByTagName('*');
  for (i=0; i<elements.length; i++){
    if (elements[i].className == objClass){
      elements[i].style.display = null;
    }
  }
}

// show the element with the class in the selector
// and hide all other elements with class in classList
function hideAndShowElement(selectorId, classList)
{
  var selectedName = this.document.getElementById(selectorId).value + '-show';

  var classArray = classList.split('.');
  for (var i = 0; i < classArray.length; i++)
    {
      if (classArray[i] != '')
	{
	  if (classArray[i] === selectedName)
	    showClass(classArray[i]);
	  else
	    hideClass(classArray[i]);
	}
    }
}

</script>

