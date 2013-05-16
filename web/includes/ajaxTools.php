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
<?php

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

    $javascriptcode = "new Ajax.Updater('$id','$url',$javaopt); return false;";


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

  if (($curend + 1) >= count($items))
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

    <div id="loader"><img id="loadimg" src="<?php echo $root; ?>img/common/loader.gif" alt="loader" class="loader"/></div>

    <div id="searchSpan" class="searchbox" style="float: right;">
    <img src="graph/search.gif" style="position:relative; top: 2px; float: left;" alt="search" /> <span class="searchfield"><input type="text" class="searchfieldreal" name="param" id="param" onKeyUp="pushSearch(); return false;">
    <img src="graph/croix.gif" alt="suppression" style="position:relative; top : 3px;"
    onClick="document.getElementById('param').value =''; pushSearch(); return false;">
    </span>
    </div>

    <script type="text/javascript">
        document.getElementById('param').focus();


                /**
        * update div with user
        */
        function updateSearch() {
            launch--;

                if (launch==0) {
                    new Ajax.Updater('container','<?php echo  $action ?>&filter='+document.Form.param.value, { asynchronous:true, evalScripts: true});
                }
            }

        /**
        * provide navigation in ajax for user
        */

        function updateSearchParam(filter, start, end) {
            new Ajax.Updater('container','<?php echo  $action ?>&filter='+filter+'&start='+start+'&end='+end, { asynchronous:true, evalScripts: true});
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
