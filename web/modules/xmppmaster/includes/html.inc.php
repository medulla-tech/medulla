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
  protected $target;
  protected $time;

  function __construct($target, $minimum = 20){
    /*
     * Called to instanciate new object
     * params :
     *  $target: string of the page name which needs to be refresh
     *  $minimum: int of the minimum (in sec.) to set the time input
     */

    $this->target = $target;
    $this->minimum = (int)$minimum;

    // The refresh time is set by the GET variable, or the SESSION variable or the minimum
    $this->refreshtime = isset($_GET['refreshtimeaudit']) ? $_GET['refreshtimeaudit'] :( isset($_SESSION['refreshtimeaudit']) ? $_SESSION['refreshtimeaudit'] : $this->minimum*1000);
    if ($this->refreshtime < $this->minimum) $this->refreshtime = $this->minimum;
    $_SESSION['refreshtimeaudit'] = $this->refreshtime;

    $this->time = $this->refreshtime/1000;
  }

  //Some getters and setters
  function refreshtime(){return $this->refreshtime;}
  function setRefreshtime($newtime){
    $newtime = (int)$newtime;
    if($newtime == 0)
      $newtime = 20000;
    $this->refreshtime = $newtime;
  }
  function time(){return $this->time;}
  function target(){return $this->target;}

  //The display function displays the buttons and add the js script which manage the refresh
  function display(){
    echo '<button class="btn btn-small btn-primary" id="bt1" type="button">refresh</button>';
    echo '<button class="btn btn-small btn-primary" id="bt" type="button">change refresh</button>';
    echo '<input  id="nbs" style="width:40px" type="number" min="'.($this->minimum).'" max="120" step="2" value="'.$this->time.'" required>';
    ?>
    <script type="text/javascript">
    jQuery('document').ready(function() {
        jQuery( "#nbs" ).change(function() {
            jQuery('#refreshtimeaudit').val(jQuery('#nbs').val() * 1000);
        });

        jQuery('#bt').click(function() {
            var query = document.location.href.replace(document.location.search,"") + "?module=xmppmaster&submod=xmppmaster&action=<?php echo $this->target;?>";
            var num = jQuery('#nbs').val() * 1000;
            query = query + "&refreshtimeaudit=" + num;
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
?>
