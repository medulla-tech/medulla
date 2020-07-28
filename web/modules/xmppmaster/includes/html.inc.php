<?php
/*
 * (c) 2015-2019 Siveo, http://www.siveo.net
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

 /*
  * This class add the elements to manage the refresh in the page
  */
class RefreshButton{
  protected $minimum;
  protected $refreshtime;
  protected $module;
  protected $submodule;
  protected $action;
  protected $target;
  protected $time;

  function __construct($target = "", $minimum = 1){
    /*
     * Called to instanciate new object
     * params :
     *  $target: string of the page name which needs to be refresh
     *  $minimum: int of the minimum (in min.) to set the time input
     * 1 sec = 1000 ms
     * 1 min = 60 sec = 60 000 ms
     */

     $this->module = htmlentities($_GET['module']);
     $this->submodule = htmlentities($_GET['submod']);
     $this->action = htmlentities($_GET['action']);

     $this->target = ($target == "") ? $this->action : $target;

     $this->minimum = (int)$minimum;
     // The refresh time is set by the GET variable, or the SESSION variable or the minimum (by default 5 min)
     $this->refreshtime = isset($_GET['refreshtime']) ? $_GET['refreshtime'] :( isset($_SESSION['refreshtime']) ? $_SESSION['refreshtime'] : 5*60000);
     if ($this->refreshtime < $this->minimum) $this->refreshtime = $this->minimum*60000;
     $_SESSION['refreshtime'] = $this->refreshtime;

     $this->time = $this->refreshtime/60000;
  }

  //Some getters and setters
  function refreshtime(){return $this->refreshtime;}

  function setRefreshtime($newtime){
    /*
     * setRefreshtime is a setter for the refreshtime attribute
     * param:
     *  int $newtime in minutes.
     */

    $newtime = (int)$newtime;
    if($newtime < $this->minimum)
      $newtime = $this->minimum;
    else
      $this->refreshtime = $newtime*60000;
      $this->time = $this->refreshtime/60000;
  }
  function time(){return $this->time;}
  function target(){return $this->target;}

  //The display function displays the buttons and add the js script which manage the refresh
  function display(){
    echo '<button class="btn btn-small btn-primary" id="bt1" type="button">'._T("Refresh","xmppmaster").'</button>';
    echo '<button class="btn btn-small btn-primary" id="bt" type="button">'._T("Change refresh","xmppmaster").'</button>';
    echo '<input  id="nbs" style="width:40px" type="number" min="'.($this->minimum).'" max="500" step="2" value="'.$this->time.'" required> min';
    ?>
    <script type="text/javascript">
    jQuery('document').ready(function() {
        jQuery('#bt').click(function() {
            var query = document.location.href ;
            var searchParam = query.match("&refreshtime=([0-9]*)");
            var num = jQuery('#nbs').val() * 60000;
            if(searchParam){
              query = query.replace(searchParam[0], "&refreshtime=" + num)
            }
            else{
              query = query + "&refreshtime=" + num;
            }
            window.location.href = query;
        });
        jQuery('#bt1').click(function() {
            location.reload()
        });
    });
    </script>
    <?php
  }

}

class CheckActionItem extends ActionItem{
  function CheckActionItem($title, $class, $disabled, $value, $paramString, $action, $submod, $module){
    $this->title = $title;
    $this->class = $class;
    $this->disabled = $disabled;
    $this->value = $value;
    $this->action = $action;
    $this->submod = $submod;
    $this->module = $module;
    $this->paramString = $paramString;
  }

  function display($param, $extraParams = []){
    $disabledstr = ($this->disabled) ? 'disabled' : '';
    $valuestr = ($this->value == 1) ? 'checked' : '';

    echo '<li style="width:10px;position=relative" class="'.$this->class.'" onclick="switchvalue(this)">';
    echo '<input type="checkbox" title="'.$this->title.'" '.$disabledstr.' '.$valuestr.'>';
        echo '<input type="hidden" value="'.$extraParams['jid'].'" '.$disabledstr.' '.$valuestr.'>';
    echo '</li>';

    ?>
    <script>
    function switchvalue(element){
      datas = {'switch': <?php echo $this->value;?>, 'jid' : ''}
      if(jQuery(jQuery(element).find('input')[0]).is(":checked")){
        datas['switch'] = 1;
        datas['jid'] = jQuery(jQuery(element).find('input')[1]).val()
      }
      else{
        datas['switch'] = 0;
        datas['jid'] = jQuery(jQuery(element).find('input')[1]).val()
      }
      jQuery("#switchresult").load("modules/xmppmaster/xmppmaster/relays/ajaxchangerelay.php", datas);

    }

    </script>
  <?php }
}
?>
