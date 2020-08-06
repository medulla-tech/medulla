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

    function display($arrParam = array()) {
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
        <option selected="selected" value="week"><?php echo _T('Last 7 days', 'glpi') ?></option>
        <option value="month"><?php echo _T('Last 30 days', 'glpi') ?></option>
        <option value="older"><?php echo _T('All', 'glpi') ?></option>
    </select>
    <?php } ?>

    <span class="searchfield">
    <input type="text" class="searchfieldreal" name="param" id="param<?php echo $this->formid ?>" onkeyup="pushSearch<?php echo $this->formid ?>(); return false;" />
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 4px;"
    onclick="document.getElementById('param<?php echo $this->formid ?>').value =''; pushSearch<?php echo $this->formid ?>(); return false;" />
    </span>
    </div>
    <br /><br /><br />

    <script type="text/javascript">
    <?php if (!in_array($_GET['part'], array('Softwares', 'History'))) echo "jQuery('#Form').hide();" ?>
<?php
if(!$this->formid) {
?>
        jQuery('#param<?php echo $this->formid ?>').focus();
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
        $url = $this->url."filter='+encodeURIComponent(document.Form".$this->formid.".param.value)+'&maxperpage='+maxperpage+'&hide_win_updates='+hide_win_updates+'&history_delta='+history_delta+'".$this->params;
        if (isset($this->storedstart) && isset($this->storedend)) {
            $url .= "&start=".$this->storedstart."&end=".$this->storedend;
        }
        ?>

        updateSearch<?php echo $this->formid ?> = function() {
            jQuery('#<?php echo  $this->divid; ?>').load('<?php echo $url ?>');

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

            jQuery('#<?php echo  $this->divid; ?>').load('<?php echo  $this->url; ?>filter='+filter+'&start='+start+'&end='+end+'&maxperpage='+maxperpage+'&hide_win_updates='+hide_win_updates+'&history_delta='+history_delta+'<?php echo  $this->params ?>');
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

 class AjaxFilterParams extends AjaxFilterLocation {
   /*
   Like AjaxFilterGlpi, this object create a search bar with this fileds:
    - entities selectbox
    - peripherals field selectbox
    - value field
   */
   function AjaxFilterParams($url, $divid = "container", $paramname = 'location', $params = array()) {
       $this->AjaxFilter($url, $divid, $params);
       $this->location = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
       $this->paramname = $paramname;
       $this->checkbox=array();
       $this->onchange="pushSearch(); return false;";
   }
   function addCheckbox($checkbox)
   {
       $checkbox->onchange=$this->onchange;
       $this->checkbox[]=$checkbox;
   }
   function setElements($elt) {
       if (count($elt) == 0) {
           $this->location = new NoLocationTpl($this->paramname);
       } else if (count($elt) == 1) {
           $loc = array_values($elt);
           $this->location = new SingleLocationTpl($this->paramname, $loc[0]);
       } else {
           $this->location->setElements($elt);
       }
   }

   function setElementsVal($elt) {
       if (count($elt) >= 1) {
           $this->location->setElementsVal($elt);
       }
   }

   function setSelected($elemnt) {
       $this->location->setSelected($elemnt);
   }

   function display($arrParam = array()) {
       global $conf;
       $root = $conf["global"]["root"];
       ?>
       <form name="Form" id="Form" action="#" onsubmit="return false;">
           <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>
           <div id="searchSpan" class="searchbox" style="float: right;">
           <div id="searchBest">
               <?php foreach ($this->checkbox as $checkbox)
                   {
                       $checkbox->display();
                   }
                   ?>
               <span class="searchfield">
                   <?php
                   $this->location->display();
                   ?>
               </span>
               <span class="searchfield" onchange="pushSearch(); return false;">
                 <select id="field">
                     <option value="">Displayed fields</option>
                     <option value="peripherals">Peripheral Details</option>
                 </select>
               </span>
               <!--<span class="searchfield" onchange="pushSearch(); return false;">
                   <select id="contains">
                     <option value="">All</option>
                     <option value="notcontains">Doesn't contain</option>
                   </select>
               </span>-->
               <span style="width:50px;">
               <input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch();
                       return false;" />
                   <img class="searchfield" src="graph/croix.gif" alt="suppression" style="position:relative;"
                        onclick="document.getElementById('param').value = '';
                                pushSearch();
                                return false;" />
              </span>
           </div>
           </div>

           <script type="text/javascript">
               jQuery('#param').focus();
               jQuery("#searchBest").width(jQuery("#searchBest").width()+20);
               if(!(navigator.userAgent.toLowerCase().indexOf('chrome') > -1)) {
                   jQuery("#searchBest").width(jQuery("#searchBest").width()+20);
               }

       <?php
       if (isset($this->storedfilter)) {
           ?>
                   document.Form.param.value = "<?php echo $this->storedfilter ?>";
           <?php
       }
       ?>
               var maxperpage = <?php echo $conf["global"]["maxperpage"] ?>;
               if (jQuery('#maxperpage').length)
                   maxperpage = jQuery('#maxperpage').val();

               /**
                * update div with user
                */
               function updateSearch() {
                   /*add checkbox param*/
                   var strCheckbox ="";
                   jQuery(".checkboxsearch").each(function() {
                       if (jQuery(this).is(":checked")) {
                           strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                       }
                   });
                   launch--;
                   if (launch == 0) {
                     var field = "";
                     field = jQuery("#field").val();
                     var contains = "";
                     if(typeof(jQuery("#contains").val())!= "undefined")
                      contains = jQuery("#contains").val();
                       jQuery.ajax({
                           'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(document.Form.param.value) + '<?php echo $this->params ?>&field='+field+'&contains='+contains+'&<?php echo $this->paramname ?>=' + document.Form.<?php echo $this->paramname ?>.value + '&maxperpage=' + maxperpage +strCheckbox,
                           type: 'get',
                           success: function(data) {
                               jQuery("#<?php echo $this->divid; ?>").html(data);
                           }
                       });
                   }
               }

               /**
                * provide navigation in ajax for user
                */

               function updateSearchParam(filt, start, end) {
                   /*add checkbox param*/
                   var strCheckbox ="";
                   jQuery(".checkboxsearch").each(function() {
                       if (jQuery(this).is(":checked")) {
                           strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                       }
                   });
                   var reg = new RegExp("##", "g");
                   var tableau = filt.split(reg);
                   var location = "";
                   var filter = "";
                   var reg1 = new RegExp(tableau[0] + "##", "g");
                   if (filt.match(reg1)) {
                       if (tableau[0] != undefined) {
                           filter = tableau[0];
                       }
                       if (tableau[1] != undefined) {
                           location = tableau[1];
                       }
                   } else if (tableau.length == 1) {
                       if (tableau[0] != undefined) {
                           location = tableau[0];
                       }
                   }
                   if (jQuery('#maxperpage').length)
                       maxperpage = jQuery('#maxperpage').val();
                   if (!location)
                       location = document.Form.<?php echo $this->paramname ?>.value;
                   if (!filter)
                       filter = document.Form.param.value;

                   jQuery.ajax({
                       'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(filter) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + location + '&start=' + start + '&end=' + end + '&maxperpage=' + maxperpage +strCheckbox,
                       type: 'get',
                       success: function(data) {
                           jQuery("#<?php echo $this->divid; ?>").html(data);
                       }
                   });

               }

               /**
                * wait 500ms and update search
                */

               function pushSearch() {
                   launch++;
                   setTimeout("updateSearch()", 500);
               }

               pushSearch();
           </script>

       </form>
       <?php
   }

}

?>
