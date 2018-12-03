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
<h2><?php print _T('Restore files','backuppc'); ?></h2>
<h3><?php print _T('Host','backuppc'); ?></h3>
<select id="restorehosts">
	<?php
		foreach($_SESSION['backup_hosts'] as $host=>$cn)
		{
			echo '<option id="'.strtoupper($host).'" value="'.strtolower($host).'">'.$cn.'</option>';
		}
	?>
</select>
<h3><?php print _T('Destination Folder','backuppc'); ?></h3>
<input name="restoreto" id="restoreto" type="text" value="<?php echo $_GET['sharename'] ?>" />
<input id="btnRestoreDirect3" type="button" value="<?php print _T('Restore','backuppc'); ?>" class="btnPrimary" />

<script type="text/javascript">

jQuery(function(){

//Extract first information send : initial host
tabl = jQuery('#restorefiles').serializeArray();
host = tabl[0];
//modify "selected" attr when id = initial host
jQuery("#"+host.value).attr('selected','selected');

    jQuery('input#btnRestoreDirect3').click(function(){
			  jQuery('#sharedest').val('/');
			  jQuery('#dir').val('/');
			  var restoreto = jQuery('input#restoreto').val();
			  jQuery('#restoredir').val(restoreto);
        form = jQuery('#restorefiles').serializeArray();

        // Test if no checkbox is checked
        if (jQuery('input[type=checkbox]:checked').length == 0)
            {
                alert('You must select at least on file.');
                return;
            }

        //Add hostdest to the queue
        form.push({
				name : 'hostdest',
				value : jQuery('#restorehosts').val()
        });
        form = jQuery.param(form);

        jQuery.ajax({
            type: "POST",
            url: "<?php  echo 'main.php?module=backuppc&submod=backuppc&action=restoreToHost'; ?>",
            data: form,

            success: function(data){
                jQuery('html').append(data);
                setTimeout("refresh();",3000);
        }
        });
        return false;
    });

});

</script>
