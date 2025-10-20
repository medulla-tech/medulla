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
 * file ajaxTools.php
 */

function linkToRemote($obj,$id,$url,$options = null) {

    $arrOpt = array();
    $arrOpt[] = "evalScript: true";
    $arrOpt[] = "asynchronous: true";
    if ($options !=null) {
        foreach ($options  as $key => $option) {
            $arrOpt[]= "$key: $option";
        }
    }

    $javaopt = '{'.implode(',',$arrOpt).'}';

    $javascriptcode = "jQuery('#$id').load('$url',$javaopt); return false;";


    echo "<a href=\"#\" onClick=\"$javascriptcode\">";
    echo "$obj</a>";
}

function print_ajax_nav($curstart,
                        $curend,
                        $items,
                        $filter)
{
  $_GET["action"] = "index";
  global $conf;

  $max = $conf["global"]["maxperpage"];
  $encitems = urlencode(base64_encode(serialize($items)));

  echo '<form method="post" action="' . $PHP_SELF . '">';
  echo "<ul class=\"navList\">\n";

  if ($curstart == 0)
    {
      echo "<li class=\"previousListInactive\">"._("Previous")."</li>\n";
    }
  else
    {
      $start = $curstart - $max;
      $end = $curstart - 1;
      echo "<li class=\"previousList\"><a href=\"#\" onClick=\"updateSearchParam('$filter','$start','$end'); return false\";>"._("Previous")."</a></li>\n";
    }

  if (is_countable($items) && ($curend + 1) >= safeCount($items))
    {
      echo "<li class=\"nextListInactive\">"._("Next")."</li>\n";
    }
  else
    {
      $start = $curend + 1;
      $end = $curend + $max;


      echo "<li class=\"nextList\"><a href=\"#\" onClick=\"updateSearchParam('$filter','$start','$end'); return false\";>"._("Next")."</a></li>\n";
    }

  echo "</ul>\n";
}

function displayInputLiveSearch($action) {


if (strstr($action,'?')===False) {
    $action = $action ."?ajax=1";
}

?>

<form name="Form" id="Form" action="#" onSubmit="return false;">

    <div id="searchSpan" class="searchbox">
        <div id="searchBest">
            <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onKeyUp="pushSearch(); return false;">
            <button type="button" class="search-clear" aria-label="Clear search"
            onclick="document.getElementById('param').value =''; pushSearch(); return false;"></button>
            </span>
        </div>
    </div>

    <script type="text/javascript">
        jQuery('#param').focus();


                /**
        * update div with user
        */
        function updateSearch() {
            launch--;

            if (launch==0) {
                jQuery("#container").load('<?php echo  $action ?>&filter='+encodeURIComponent(document.Form.param.value));
            }
        }

        /**
        * provide navigation in ajax for user
        */

        function updateSearchParam(filter, start, end) {
            jQuery("#container").load('<?php echo  $action ?>&filter='+encodeURIComponent(filter)+'&start='+start+'&end='+end);
        }

        /**
        * wait 500ms and update search
        */

        function pushSearch() {
            launch++;
            setTimeout("updateSearch()",500);
        }

    </script>

</form>

<?php

}

?>
