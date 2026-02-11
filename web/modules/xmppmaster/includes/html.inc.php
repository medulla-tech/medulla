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


require_once("modules/xmppmaster/includes/xmlrpc.php");


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
  function __construct($title, $class, $disabled, $value, $paramString, $action, $submod, $module){
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

    echo '<li style="width:10px;position:relative" class="'.$this->class.'" onclick="switchvalue(this)">';
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


class Editor{
  public static $languagesList = [
    "batchfile" =>"Dos Windows",
    "powershell"=> "PowerShell Windows",
    "sh" => "Linux Bash",
    "plain_text" => "Text",
    "python" => "Python",
    "json" => "Json",
    "xml" => "Xml",
    "mysql" => "Mysql",
    "ini" => "Ini file",
    "perl" => "Perl",
    "javascript" =>"Javascript",
    "php" => "Php"
  ];
  public static $themesList = [
    "ambiance" => "ambiance",
    "chaos" => "chaos",
    "chrome" => "chrome",
    "clouds" => "clouds",
    "dawn" => "dawn",
    "dracula" => "dracula",
    "dreamweaver" => "dreamweaver",
    "eclipse" => "eclipse",
    "github" => "github",
    "gob" => "gob",
    "gruvbox" => "gruvbox",
    "idle_fingers" => "idle_fingers",
    "iplastic" => "iplastic",
    "katzenmilch" => "katzenmilch",
    "kr_theme" => "kr_theme",
    "kuroir" => "kuroir",
    "merbivore" => "merbivore",
    "mono_industrial" => "mono_industrial",
    "monokai" => "monokai",
    "pastel_on_dark" => "pastel_on_dark",
    "terminal" => "terminal",
    "textmate" => "textmate",
    "tomorrow" => "tomorrow",
    "tomorrow_night" => "tomorrow_night",
    "tomorrow_night_blue" => "tomorrow_night_blue",
    "tomorrow_night_bright" => "tomorrow_night_bright",
    "tomorrow_night_eighties" => "tomorrow_night_eighties",
    "twilight" => "twilight",
    "vibrant_ink" => "vibrant_ink",
    "xcode" => "xcode",
  ];

  public static $modes = [
    'in' => 'terminal',
    'out' => 'github'
  ];
  //Object options
  protected $m_fileName;
  protected $m_pointedLine;
  protected $m_language;
  protected $m_theme;
  protected $m_mode;
  protected $m_fontSize;

  //html properties
  protected $m_id;
  protected $m_class;
  protected $m_name;
  protected $m_css;
  protected $m_ajax;

  //js scripts launched added when the object is displayed
  protected $m_scripts;

  //editor elements
  protected $m_content = "";

  public function __construct($file, $name, $id="", $css=[], $scripts=[], $mode='out', $language='plain_text'){
    $this->setFileName($file);
    $this->setName($name);
    $this->setId($id);
    $this->setCss($css);
    $this->setScripts($scripts);
    $this->setMode($mode);
    $this->setLanguage($language);
    $this->setPointedLine(1);

    // Defaults value:
    $this->setPointedLine(1);
    $this->setFontSize(13);
    $this->m_content = "";
  }

  //Getters
  public function fileName(){return $this->$m_fileName;}
  public function pointedLine(){return $this->m_pointedLine;}
  public function language(){return $this->m_language;}
  public function theme(){return $this->m_theme;}
  public function mode(){return $this->m_mode;}
  public function fontSize(){return $this->m_fontSize;}
  public function id(){return $this->id;}
  public function cssclass(){return $this->m_class;}
  public function name(){return $this->m_name;}
  public function css(){return $this->m_css;}
  public function scripts(){return $this->m_scripts;}
  public function content(){return $this->m_content;}
  public function ajax(){return $this->m_ajax;}

  //Setters
  public function setFileName($filename){
    if(is_string($filename))
      $this->m_fileName = $filename;
  }
  public function setPointedLine($line){
    $this->m_pointedLine = $line;
  }
  public function setLanguage($language){
    if(isset(Editor::$languagesList[$language])){
      $this->m_language = $language;
    }
    else{
      $this->m_language = 'plain_text';
    }
  }
  public function setTheme($theme){
    if(isset(Editor::$themesList[$theme])){
      $this->m_theme = $theme;
    }
  }

  public function setFontSize($fontSize){
    if(is_int($fontSize)){
      $this->m_fontSize = $fontSize;
    }
    else{
      $this->m_fontSize = 13;
    }
  }

  public function setId($id){
    if(is_string($id)){
      if($id != ""){
        $this->m_id = $id;
      }
      else{
        $this->m_id = $this->m_name;
      }
    }
  }

  /*public function class*/
  public function setName($name){
    if(is_string($name)){
      $this->m_name = $name;
      $this->m_class = $name;
    }
  }
  public function setCss($css){
    if(is_array($css)){
      $this->m_css = $css;
    }
  }
  public function setScripts($scripts){
    if(is_array($scripts)){
      $this->m_scripts = $scripts;
    }
  }

  public function setMode($mode){
    if(isset(Editor::$modes[$mode])){
      $this->m_mode = $mode;
      $this->m_theme = Editor::$modes[$mode];
    }
    else{
      $this->m_mode = "out";
      $this->m_theme = Editor::$modes["out"];
    }
  }

  public function setContent($content){
    $this->m_content = $content;
  }

  public function setAjax($ajax){
    $this->m_ajax = $ajax;
  }

  // Some methods
  public function dir_exists(){
    return xmlrpc_dir_exists(dirname($this->m_fileName));
  }

  public function file_exists(){
    return xmlrpc_file_exists($this->m_fileName);
  }

  public function create_dir(){
    return xmlrpc_create_dir(dirname($this->m_fileName));
  }

  public function create_file(){
    return xmlrpc_create_file($this->m_fileName);
  }


  public function get_content(){
    $content = xmlrpc_get_content($this->m_fileName);
    $this->setContent($content);
    return $content;
  }

  public function display(){?>

  <!--HERE Load js lib like ACE.js-->
  <?php if($this->m_mode == "in"){?>
    <!--HERE Load <link /> css for input editor-->
  <?php }
  else{?>
  <!--HERE Load <link /> css for output editor-->
<?php }?>
  <style>
  .info{
    font-size:1.3em;
    background-color: lightblue;
    padding:10px;
    margin-bottom:5px;
    font-family: arial, serif;
    font-weight: bold;
  }
  </style>

  <div class="<?php echo $this->m_id;?>_result"></div>
<p class="info"><?php echo _T("The file will be automatically saved", "xmppmaster");?></p>
  <div style="display:flex; width:100%;" class="<?php echo $this->m_id;?>_editor">
    <div style="width:100%;">
      <h1><?php echo _T("Edit file: ","xmppmaster").$this->m_fileName;?></h1>
      <textarea class="<?php echo $this->m_class.'_edit';?>" style="width:95%;min-height:50vh;font-size:<?php echo $this->m_fontSize.'pt';?>;"><?php echo $this->m_content;?></textarea>
    </div>
    <!--The second part to create a preview box
    <div style="width:50%">
      <h1>Preview</h1>
      <pre><code class="<?php echo $this->m_class.'_preview';?> language-<?php echo $this->m_language;?>" style="font-size:<?php echo $this->m_fontSize.'pt';?>;"><?php echo $this->m_content;?>
</code></pre>
</div>-->
  </div>


  <script>
  cursor = 0;
  oldCursor = 0;
  text= ""

  preview= ".<?php echo $this->m_class;?>_preview"

  /*
  //Keep this code just in case...
  jQuery("document").ready(function(){
    //jQuery(".<?php echo $this->m_class;?>_edit").hide();
    jQuery(".<?php echo $this->m_class;?>_preview").on("click", function(){

      jQuery(".<?php echo $this->m_class;?>_edit").focus()
      select = window.getSelection()
      cursor = select.anchorOffset
      node = jQuery(select.anchorNode)
      jQuery(select.anchorNode).text();

      hljs.highlightBlock(jQuery(".<?php echo $this->m_class;?>_preview")[0],'  ', false);

    });
  });*/



  jQuery(".<?php echo $this->m_class;?>_edit").bind('keydown keyup click focus', function(){

    cursor = jQuery(this).prop("selectionStart");
    text = jQuery(".<?php echo $this->m_class;?>_edit").val();

    /*
    //Keep this code just in case...
    text_before_cursor = text.slice(0, cursor)
    text_after_cursor = text.slice(cursor, -1)

    jQuery(".<?php echo $this->m_class;?>_preview").html(text_before_cursor+'|'+text_after_cursor)
    hljs.highlightBlock(jQuery(".<?php echo $this->m_class;?>_preview")[0],'  ', false);
    */
  });

  jQuery(".<?php echo $this->m_class;?>_edit").bind("input propertychange", function(){
    value = jQuery(this).val()
    text = value

    cursor = jQuery(this).prop("selectionStart");
    text = jQuery(".<?php echo $this->m_class;?>_edit").val();

    /*
    //Keep this code just in case...
    //text_before_cursor = text.slice(0, cursor)
    //text_after_cursor = text.slice(cursor, -1)

    //jQuery(".<?php echo $this->m_class;?>_preview").html(text_before_cursor+' I '+text_after_cursor)
    //hljs.highlightBlock(jQuery(".<?php echo $this->m_class;?>_preview")[0],'  ', false);
    */
    jQuery(".<?php echo $this->m_class;?>_result").load("<?php echo $this->m_ajax;?>", {"save":true, "path":"<?php echo $this->m_fileName;?>", 'datas': text}, function(result){
    });
  });

  </script>

  <?php }
}
?>
