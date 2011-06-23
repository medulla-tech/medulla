<?php
/*
 * (c) 2007-2008 Mandriva, http://www.mandriva.com/
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

class RenderedImage extends HtmlElement {

    function RenderedImage($url, $alt = '', $style = '') {
        $this->url = $url;
        $this->alt = $alt;
        $this->style = $style;
    }

    function display() {
        print '<img src="' . $this->url . '" alt="'.$this->alt.'" style="'.$this->style.'"/>';
    }
}

class RenderedLink extends HtmlElement {
    function RenderedLink($link, $content) {
        $this->link = $link;
        $this->content = $content;
    }

    function display() {
        print '<a href="'.$this->link.'">'.$this->content.'</a>';
    }
}

/**
 * Define a class that render a widget with a calendar integrated for the inventory parts
 * It has a checkbox to filter the softwares
 * It saves the date set in a session to remember it when changing the page
 */
class AjaxFilterInventory extends AjaxFilter {

    function AjaxFilterInventory($url, $divid = "container", $params = array(), $formid = "") {
        $this->AjaxFilter($url, $divid, $params, $formid);
        // Get the date saved in the session
        if(isset($_SESSION['__inventoryDate']))
            $defaultDate = $_SESSION['__inventoryDate'];
        // Or put the default string "Date" in the field
        else
            $defaultDate = _T("Date");

        // Save the part to later know if we are in the Software page ($params['part'] is changed by the AjaxFilter class)
        $this->part = $params['part'];
        // Add a calendar at the default date (from the session or "Date"
        $this->date = new LogDynamicDateTpl("date", $defaultDate, false);
    }

    function setsearchbar($url){
        $this->urlsearch=$url;
    }

    function display(){

?>
<form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;">
    <div id="loader">
        <img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/>
    </div>
    <div id="searchSpan<?php echo $this->formid ?>" class="searchboxlog">
        <span class="searchfieldfilter">
<?php
        $this->date->setSize(15);
        $this->date->display(array("update_search"=>True));

        // Display the checkbox to allow to filter the softwares
        if($this->part == 'Software') {
            $checkbox = new CheckboxTpl("software_filter");
            $checkbox->display(array("value"=>"checked"));
            echo "Filter softwares";
        }
?>

        <span class="searchtools">
            <span id="searchfilter">
                <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" /> <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param<?php echo $this->formid ?>" onkeyup="pushSearch<?php echo $this->formid ?>(); return false;" />
                <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
                onclick="document.getElementById('param<?php echo $this->formid ?>').value =''; pushSearch<?php echo $this->formid ?>(); return false;" />
                </span>
            </span>
            <img src="img/common/reload.png" style="vertical-align: middle; margin-left: 10px; margin-right: 10px;" onclick="pushSearch(); return false;" title="<?php echo _("Refresh") ?>" />
        </span>&nbsp;
        </span>
    </div>
    <script type="text/javascript">

<?
if(!$this->formid) {
?>
        document.getElementById('param<?php echo $this->formid ?>').focus();
<?
}
if(isset($this->storedfilter)) {
?>
        document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
<?
}
?>


        var refreshtimer<?php echo $this->formid ?> = null;
        var refreshparamtimer<?php echo $this->formid ?> = null;
        var refreshdelay<?php echo $this->formid ?> = <?php echo  $this->refresh ?>;
        // Get the state of the software_value checkbox
        var software_filter = "";
        if(document.Form<?php echo $this->formid ?>.software_filter != undefined){
            software_filter = document.Form<?php echo $this->formid ?>.software_filter.checked;
        }

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
        updateSearch<?php echo $this->formid ?> = function() {
            new Ajax.Updater('<?php echo  $this->divid; ?>',
            '<?php echo  $this->url; ?>filter='+document.Form<?php echo $this->formid ?>.param.value+'&date='+document.Form<?php echo $this->formid ?>.date.value+'<?php echo $this->params ?>&software_filter='+software_filter,
            { asynchronous:true, evalScripts: true}
            );

<?
if ($this->refresh) {
?>
            //refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", refreshdelay<?php echo $this->formid ?>)
<?
}
?>
        }

        /**
         * Update div when clicking previous / next
         */
            updateSearchParam<?php echo $this->formid ?> = function(filter, start, end) {
            clearTimers<?php echo $this->formid ?>();
            new Ajax.Updater('<?php echo  $this->divid; ?>','<?php echo  $this->url; ?>filter='+filter+'&start='+start+'&end='+end+'&date='+document.Form<?php echo $this->formid ?>.date.value+'<?php echo  $this->params ?>&software_filter='+software_filter, { asynchronous:true, evalScripts: true});

<?
if ($this->refresh) {
?>
            refreshparamtimer<?php echo $this->formid ?> = setTimeout("updateSearchParam<?php echo $this->formid ?>('"+filter+"',"+start+","+end+")", refreshdelay<?php echo $this->formid ?>);
<?
}
?>
        }

        /**
         * wait 500ms and update search
         */
        pushSearch<?php echo $this->formid ?> = function() {
            clearTimers<?php echo $this->formid ?>();
            refreshtimer<?php echo $this->formid ?> = setTimeout("updateSearch<?php echo $this->formid ?>()", 500);
            // Refresh the state of the software_filter checkbox
            if(document.Form<?php echo $this->formid ?>.software_filter != undefined) {
                software_filter = document.Form<?php echo $this->formid ?>.software_filter.checked;
            }
        }

        pushSearch<?php echo $this->formid ?>();

    </script>

</form>
<?
          }
}

?>

