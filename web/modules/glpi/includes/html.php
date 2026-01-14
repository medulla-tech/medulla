<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: includes/html.php
 */

class AjaxFilterGlpi extends AjaxFilter {
    function __construct($url, $divid = "container", $params = array(), $formid = "") {
        parent::__construct($url, $divid, $params, $formid);
    }

    function display($arrParam = array()) {
        global $conf;
        $root = $conf["global"]["root"];
        $maxperpage = $conf["global"]["maxperpage"];

?>
<form name="Form<?php echo $this->formid ?>" id="Form<?php echo $this->formid ?>" action="#" onsubmit="return false;">

    <div id="searchSpan<?php echo $this->formid ?>" class="searchbox">

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
    <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
    onclick="document.getElementById('param<?php echo $this->formid ?>').value =''; pushSearch<?php echo $this->formid ?>(); return false;"></button>
    </span>
    <span class="loader" aria-hidden="true"></span>
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
         * Build URL dynamically in JS to avoid duplicate params issue
         */
        updateSearch<?php echo $this->formid ?> = function() {
            clearTimers<?php echo $this->formid ?>();

            // Refresh checkbox/select states
            if(document.Form<?php echo $this->formid ?>.hide_win_updates != undefined) {
                hide_win_updates = document.Form<?php echo $this->formid ?>.hide_win_updates.checked;
            }
            if(document.Form<?php echo $this->formid ?>.history_delta != undefined) {
                history_delta = document.Form<?php echo $this->formid ?>.history_delta.value;
            }

            var searchValue = document.Form<?php echo $this->formid ?>.param.value;

            // Build URL with filter FIRST to ensure it's not overwritten
            var finalUrl = '<?php echo rtrim($this->url, "&"); ?>'
                + '&filter=' + encodeURIComponent(searchValue)
                + '&maxperpage=' + maxperpage
                + '&hide_win_updates=' + hide_win_updates
                + '&history_delta=' + history_delta
                <?php if (isset($this->storedstart) && isset($this->storedend)) { ?>
                + '&start=<?php echo $this->storedstart ?>'
                + '&end=<?php echo $this->storedend ?>'
                <?php } ?>
            ;

            jQuery('#<?php echo $this->divid; ?>').load(finalUrl);

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

            var finalUrl = '<?php echo rtrim($this->url, "&"); ?>'
                + '&filter=' + encodeURIComponent(filter)
                + '&start=' + start
                + '&end=' + end
                + '&maxperpage=' + maxperpage
                + '&hide_win_updates=' + hide_win_updates
                + '&history_delta=' + history_delta;

            jQuery('#<?php echo $this->divid; ?>').load(finalUrl);
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
   function __construct($url, $divid = "container", $paramname = 'location', $params = array()) {
       parent::__construct($url, $divid, $params);
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
       if (safeCount($elt) == 0) {
           $this->location = new NoLocationTpl($this->paramname);
       } else if (safeCount($elt) == 1) {
           $loc = array_values($elt);
           $this->location = new SingleLocationTpl($this->paramname, $loc[0]);
       } else {
           $this->location->setElements($elt);
       }
   }

   function setElementsVal($elt) {
       if (safeCount($elt) >= 1) {
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
           <div id="searchSpan" class="searchbox">
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
               <input type="text" class="searchfieldreal" name="param" id="param" />
                   <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
                        onclick="document.getElementById('param').value = '';
                                pushSearch();
                                return false;"></button>
              </span>
              <button onclick="pushSearch();
                      return false;"><?php echo _T("Search", "glpi");?></button>
              <span class="loader" aria-hidden="true"></span>
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


class AjaxFilterParamssearch extends AjaxFilterLocation {


      function __construct($url, $divid = "container", $paramname = 'entity_search', $params = array()) {
       parent::__construct($url, $divid, $params);

       $this->paramname = $paramname;
       $this->checkbox = array();
       $this->onchange = "pushSearch(); return false;";
       $this->fields = array();

       // initialisation de location avec SelectItem vide
       $this->location = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
   }

   function addCheckbox($checkbox) {
       $checkbox->onchange = $this->onchange;
       $this->checkbox[] = $checkbox;
   }

   function setElements($elt) {
       if (safeCount($elt) == 0) {
           $this->location = new NoLocationTpl($this->paramname);
       } else if (safeCount($elt) == 1) {
           $loc = array_values($elt);
           $this->location = new SingleLocationTpl($this->paramname, $loc[0]);
       } else {
           $this->location->setElements($elt);

           // si aucun élément sélectionné n'a été défini, on prend le premier
           if (!isset($this->location->selected)) {
               $keys = array_keys($elt);
               $this->location->setSelected($keys[0]);
           }
       }
   }

   function setElementsVal($values) {
       if (safeCount($values) >= 1) {
           $this->location->setElementsVal($values);

           // si aucune sélection définie, utiliser la première valeur
           if (!isset($this->location->selected)) {
               $firstVal = reset($values);
               $this->location->setSelected($firstVal);
           }
       }
   }

   function setSelected($elemnt) {
       $this->location->setSelected($elemnt);
   }

    function setfieldsearch($elt){
        if (safeCount($elt) == 0) {
            $this->fields = [ _T('Hide Windows Updates', "glpi") => "allelt"];
        }
        else {
                $this->fields = $elt;
            }
    }

   function display($arrParam = array()) {
       global $conf;
       $root = $conf["global"]["root"];
       ?>
       <form name="Form" id="Form" action="#" onsubmit="return false;">
           <div id="searchSpan" class="searchbox">
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
                     <option value="allchamp">search all fields</option>
                     <?php
                        foreach( $this->fields as $keys => $value){
                            if ($keys == "Hostname " ){
                                echo '<option  selected="selected" value="'.$value.'">'.$keys.'</option>';
                            }
                            else{
                                echo '<option value="'.$value.'">'.$keys.'</option>';
                            }
                        }
                     ?>
                 </select>
               </span>
               <!--<span class="searchfield" onchange="pushSearch(); return false;">
                   <select id="contains">
                     <option value="">All</option>
                     <option value="notcontains">Doesn't contain</option>
                   </select>
               </span>-->
               <span style="width:50px;">
               <input type="text" class="searchfieldreal" name="param" id="param" />
                   <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
                        onclick="document.getElementById('param').value = '';
                                pushSearch();
                                return false;"></button>
              </span>
              <button onclick="pushSearch();
                      return false;"><?php echo _T("Search", "glpi");?></button>
              <span class="loader" aria-hidden="true"></span>
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
                * Fournit la navigation AJAX (pagination) en conservant filtres et cases à cocher.
                *
                * @param {string} filt   Chaîne contenant "filter##location" ou uniquement location
                * @param {number} start  Index de début pour la pagination
                * @param {number} end    Index de fin pour la pagination
                */
                function updateSearchParam(filt, start, end) {
                    // 1. Construction de la chaîne de requête pour les cases à cocher sélectionnées
                    let strCheckbox = "";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox += '&' + jQuery(this).attr('id') + "=true";
                        }
                    });

                    // 2. Découpage du paramètre filt
                    let filter   = "";
                    let location = "";
                    const tableau = filt.split(/##/g);

                    if (tableau.length >= 2) {
                        filter   = tableau[0] || "";
                        location = tableau[1] || "";
                    } else if (tableau.length === 1) {
                        location = tableau[0] || "";
                    }

                    // 3. Valeurs par défaut si vides
                    if (jQuery('#maxperpage').length) {
                        maxperpage = jQuery('#maxperpage').val();
                    }
                    if (!location) {
                        location = jQuery('#<?php echo $this->paramname ?>').val();
                    }
                    if (!filter) {
                        filter = document.Form.param.value;
                    }

                    // 4. Récupération du champ de recherche
                    const field    = jQuery("#field").val();
                    let contains   = "";
                    if (typeof jQuery("#contains").val() !== "undefined") {
                        contains = jQuery("#contains").val();
                    }

                    // 5. Appel AJAX pour mettre à jour les résultats
                    jQuery.ajax({
                        url: '<?php echo $this->url; ?>filter=' +
                            encodeURIComponent(filter) +
                            '<?php echo $this->params ?>' +
                            '&field=' + encodeURIComponent(field) +
                            '&contains=' + encodeURIComponent(contains) +
                            '&location=' + encodeURIComponent(location) +
                            '&start=' + start +
                            '&end=' + end +
                            '&maxperpage=' + encodeURIComponent(maxperpage) +
                            strCheckbox,
                        type: 'GET',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        },
                        error: function(xhr, status, error) {
                            console.error("Erreur AJAX:", status, error);
                        }
                    });
                }


                /**
                * Met à jour la recherche en fonction des paramètres sélectionnés,
                * y compris les cases à cocher et les champs de formulaire.
                */
                function updateSearch() {
                    // 1. Construction de la chaîne de requête pour les cases à cocher sélectionnées
                    let strCheckbox = "";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox += '&' + jQuery(this).attr('id') + "=true";
                        }
                    });

                    // 2. Décrémentation du compteur de lancement (si utilisé pour gérer plusieurs appels)
                    launch--;
                    entity = jQuery('#<?php echo $this->paramname ?>').val();
                    // 3. Exécution de la requête AJAX uniquement si le compteur atteint zéro
                    if (launch === 0) {
                        // Récupération des valeurs des champs de formulaire
                        const field = jQuery("#field").val();
                        let contains = "";
                        if (typeof jQuery("#contains").val() !== "undefined") {
                            contains = jQuery("#contains").val();
                        }
                        // 4. Appel AJAX pour mettre à jour les résultats
                        jQuery.ajax({
                    url: '<?php echo $this->url; ?>filter=' +
                        encodeURIComponent(document.Form.param.value) +
                        '<?php echo $this->params ?>' +
                        '&field=' + encodeURIComponent(field) +
                        '&contains=' + encodeURIComponent(contains) +
                        '&location=' + encodeURIComponent(entity) +
                        '&maxperpage=' + encodeURIComponent(maxperpage) +
                        strCheckbox,
                    type: 'GET',
                    success: function(data) {
                        jQuery("#<?php echo $this->divid; ?>").html(data);
                    }
                });
                    }
                }

               /**
                * wait 500ms and update search
                */

               function pushSearch() {
                   launch++;
                   setTimeout("updateSearch()", 500);
                   //setTimeout("updateSearchParam()", 500);

               }

              pushSearch();
           </script>

       </form>
       <?php
   }

}
?>
