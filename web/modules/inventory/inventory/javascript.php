<?

/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id: infoPackage.inc.php 8 2006-11-13 11:08:22Z cedric $
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

/**
 * provide navigation in ajax for user
 */

?>

<script type="text/javascript">
/**
 * update div with user
 */
function updateSearchMachine(display, label, filter) {
	launch--;

	if (launch==0) {
	        if (document.inventoryForm.param.value == null || document.inventoryForm.param.value == '') {
		  document.inventoryForm.param.value = filter;
		}
		new Ajax.Updater('inventoryContainer','main.php?module=inventory&submod=inventory&action=ajaxFilter&display='+display+'&label='+label+'&filter='+document.inventoryForm.param.value, { asynchronous:true, evalScripts: true});
	}
}

    
function updateSearchMachineParam(filter, start, end, display, label) {

	new Ajax.Updater('inventoryContainer','main.php?module=inventory&submod=inventory&action=ajaxFilter&display='+display+'&label='+label+'&filter='+filter+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true} );

}

function pushSearchMachine(display, label, filter) {
	launch++;
	setTimeout("updateSearchMachine('"+display+"', '"+label+"', '"+filter+"')",500);
}

</script>

<div id="inventoryContainer">
</div>

