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
<h2>Restore files</h2>
<!-- <p>You are about to restore the files directly on the target computer. Your can change to Restore directory below or keep the original folder. In the last case, new files will be overwritten.</p>
<input type="radio" name="restoredir_" value="/" id="to_original"> Restore to original folder<br/>
<input type="radio" name="restoredir_" value="/" id="to_original"> Restore to alternative folder<br/> -->
<!-- <input type="text"  name="restoredir_" id="restoredir_" value="/"  /><br/> -->
<input type="button" value="To original folder (overwrite)" class="btnPrimary" onclick="$('restorefiles').action='main.php?module=backuppc&submod=backuppc&action=restoreToHost';$('restoredir').value='/';$('restorefiles').submit();" />
<input type="button" value="To alternative folder" class="btnPrimary" onclick="$('restorefiles').action='main.php?module=backuppc&submod=backuppc&action=restoreToHost';$('restoredir').value='/Restore_<?php print(date('Y-m-d')); ?>/';$('restorefiles').submit();" />
