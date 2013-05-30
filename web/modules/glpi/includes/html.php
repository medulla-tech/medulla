<?php
/*
 * (c) 2013 Mandriva, http://www.mandriva.com/
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

class AjaxFilterGlpi extends AjaxFilter {
    function AjaxFilterGlpi($url, $divid = "container", $params = array(), $formid = "") {
        $this->AjaxFilter($url, $divid, $params, $formid);
    }

    function display() {
        global $conf;
        $root = $conf["global"]["root"];
        $maxperpage = $conf["global"]["maxperpage"];

?>
<form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;">

    <div id="loader<?php echo $this->formid ?>">
        <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/>
    </div>
    <div id="searchSpan<?php echo $this->formid ?>" class="searchbox" style="float: right;">

    <?php if($_GET['part'] == 'Softwares') { ?>
    <!-- Hide Windows Updates checkbox -->
    <input checked style="top: 2px; left: 5px; position: relative; float: left" 
        type="checkbox"
        class="searchfieldreal" 
        name="hide_win_updates" 
        id="hide_win_updates<?php echo $this->formid ?>" onchange="pushSearch<?php echo $this->formid ?>(); return false;" />
    <span style="padding: 7px 15px; position: relative; float: left"><?php echo _T('Hide Windows Updates', "glpi")?></span>
    <?php } ?>

    <?php if($_GET['part'] == 'History') { ?>
    <select style="position: relative; float: left" 
        class="searchfieldreal" 
        name="history_delta" 
        id="history_delta<?php echo $this->formid ?>" onchange="pushSearch<?php echo $this->formid ?>(); return false;" >
        <option value="today"><?php echo _T('Today', 'glpi') ?></option>
        <option selected="selected" alue="week"><?php echo _T('Last 7 days', 'glpi') ?></option>
        <option value="month"><?php echo _T('Last 30 days', 'glpi') ?></option>
        <option value="older"><?php echo _T('All', 'glpi') ?></option>
    </select>
    <?php } ?>

    <img src="graph/search.gif" style="position:relative; top: 5px; float: left;" alt="search" />
    <span class="searchfield">
    <input type="text" class="searchfieldreal" name="param" id="param<?php echo $this->formid ?>" onkeyup="pushSearch<?php echo $this->formid ?>(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 4px;"
    onclick="document.getElementById('param<?php echo $this->formid ?>').value =''; pushSearch<?php echo $this->formid ?>(); return false;" />
    </span>
    </div>
    <br /><br /><br />

    <script type="text/javascript">
    <?php if (!in_array($_GET['part'], array('Softwares', 'History'))) echo "$('Form').hide();" ?>
<?php
if(!$this->formid) {
?>
        document.getElementById('param<?php echo $this->formid ?>').focus();
<?php
}
if(isset($this->storedfilter)) {
?>
        document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
<?php
}
?>
        var refreshtimer<?php echo $this->formid ?> = null;
        var refreshparamtimer<?php echo $this->formid ?> = null;
        var refreshdelay<?php echo $this->formid ?> = <?php echo  $this->refresh ?>;
        var maxperpage = <?php echo $maxperpage ?>;

        // Get the state of the hide_win_updates checkbox
        var hide_win_updates = "";
        if(document.Form<?php echo $this->formid ?>.hide_win_updates != undefined){
            hide_win_updates = document.Form<?php echo $this->formid ?>.hide_win_updates.checked;
        }
        // Get the state of the history_delta dropdown
        var history_delta = "";
        if(document.Form<?php echo $this->formid ?>.history_delta != undefined){
            history_delta = document.Form<?php echo $this->formid ?>.history_delta.value;
        }

<?php
if (isset($this->storedmax)) {
?>
        maxperpage = <?php echo $this->storedmax ?>;
<?php
}
?>
        if(document.getElementById('maxperpage') != undefined)
            maxperpage = document.getElementById('maxperpage').value;

        /**
         * Clear the timers set vith setTimeout
         */
        clearTimers<?php echo $this->formid ?> = function() {
            if (refreshtimer<?php echo $this->formid ?> != null) {
                clearTimeout(refreshtimer<?php echo $this->formid ?>);
            }
            if (refreshparamtimer<?php echo $this->formid ?> != null) {
                clearTimeout(refreshparamtimer<?php echo $this->formid ?>);
            }
        }

        /**
         * Update div
         */
        <?php
        $url = $this->url."filter='+document.Form".$this->formid.".param.value+'&maxperpage='+maxperpage+'&hide_win_updates='+hide_win_updates+'&history_delta='+history_delta+'".$this->params;
        if (isset($this->storedstart) && isset($this->storedend)) {
            $url .= "&start=".$this->storedstart."&end=".$this->storedend;
        }
        ?>

        updateSearch<?php echo $this->formid ?> = function() {
            new Ajax.Updater('<?php echo  $this->divid; ?>',
            '<?php echo $url ?>',
            { asynchronous:true, evalScripts: true}
            );

<?php
if ($this->refresh) {
?>
            refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", refreshdelay<?php echo $this->formid ?>)
<?php
}
?>
        }

        /**
         * Update div when clicking previous / next
         */
        updateSearchParam<?php echo $this->formid ?> = function(filter, start, end, max) {
            clearTimers<?php echo $this->formid ?>();
            if(document.getElementById('maxperpage') != undefined)
                maxperpage = document.getElementById('maxperpage').value;

            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+filter+'&start='+start+'&end='+end+'&maxperpage='+maxperpage+'&hide_win_updates='+hide_win_updates+'&history_delta='+history_delta+'<?php echo  $this->params ?>', { asynchronous:true, evalScripts: true});
<?php
if ($this->refresh) {
?>
            refreshparamtimer<?php echo $this->formid ?> = setTimeout("updateSearchParam<?php echo $this->formid ?>('"+filter+"',"+start+","+end+","+maxperpage+")", refreshdelay<?php echo $this->formid ?>);
<?php
}
?>
        }

        /**
         * wait 500ms and update search
         */
        pushSearch<?php echo $this->formid ?> = function() {
            clearTimers<?php echo $this->formid ?>();
            refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", 500);
            // Refresh the state of the hide_win_updates checkbox
            if(document.Form<?php echo $this->formid ?>.hide_win_updates != undefined) {
                hide_win_updates = document.Form<?php echo $this->formid ?>.hide_win_updates.checked;
            }
            // Refresh the state of the history_delta dropdown
            if(document.Form<?php echo $this->formid ?>.history_delta != undefined) {
                history_delta = document.Form<?php echo $this->formid ?>.history_delta.value;
            }
        }

        pushSearch<?php echo $this->formid ?>();

    </script>

</form>
<?php
          }
}

?>
