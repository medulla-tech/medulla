<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
require_once("../../../../includes/i18n.inc.php");

extract($_POST);
/*

descriptor type
  unzip file from python
        descriptor type
        {
            "step" : intnb,
            "action" : "action_unzip_file",
            "filename" : "namefile",
            "pathdirectorytounzip" : "pathdirextract",
            "@resultcommand" : ""
        }
        filename if current directory or pathfilename
        optionnel
            @resultcommand list files
            10@lastlines 10 last lines
            10@firstlines 10 first lines
            succes
            error
            goto
        """
*/

$packageList = xmpp_packages_list();
$optionspackage= "";

foreach($packageList as $id=>$package)
{
   if(isset($packageuuid) && $packageuuid == $package['uuid'])
   {
       $optionspackage .= "<option value='".$package['uuid']."' selected>".$package['name']."</option>";
   }
   else
       $optionspackage .= "<option value='".$package['uuid']."'>".$package['name']."</option>";
}

$waiting =  (isset($waiting))? $waiting : 10;/*
$goto =  (isset($goto))? $goto : "END_SUCCESS";*/


$tableToggle=  "tableToggle".uniqid();
$toggleable =  "toggleable".uniqid();
$idclass =  "#".$tableToggle.' tr.'.$toggleable;
?>
<div class="header">
    <h1><?php echo _T('Unzip File', 'pkgs'); ?></h1>
</div>
<div class="content">
    <div>
        <input type="hidden" name="action" value="action_unzip_file" />
        <input type="hidden" name="step" />
        <input type="hidden" name="codereturn" value=""/>
    <table id="tableToggle">
        <tr class="toggleable">
            <th width="16%"><?php echo _T('Step label:', 'pkgs'); ?></th>
            <th width="25%">
                <input id="laction" type="text" name="actionlabel" value="<?php echo (isset($actionlabel))? $actionlabel : uniqid(); ?>"/>
            </th>
            <th></th>
            <th></th>
        </tr>

        <tr>
            <th width="16%"><?php echo _T('Zip file:', 'pkgs'); ?></th>
            <th width="25%">
                <input type="text" name="filename" value="<?php echo (isset($filename))? $filename : ""; ?>"/>
            </th>
            <th></th>
            <th></th>
        </tr>

        <?php
            echo '<tr class="toggleable">';
              if(isset($packageuuid))
              {
                  echo '<td width="16%">
                      <input type="checkbox" checked
                          onclick="if(jQuery(this).is(\':checked\')){
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                  }
                                  else{
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                  }" />'._T("Alternate package","pkgs").'
                  </td>
                  <td width="25%">
                      <select name="packageuuid">'.$optionspackage.'</select>
                  </td>';
              }
              else{
                  echo '<td width="16%">
                      <input type="checkbox"
                          onclick="if(jQuery(this).is(\':checked\')){
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                  }
                                  else{
                                      jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                  }" />'._T("Alternate package","pkgs").'
                      </td>
                      <td width="25%">
                          <select disabled name="packageuuid">'.$optionspackage.'</select>
                      </td>';
              }
          echo '
          <td></td><td></td>
              </tr>';
      ?>


         <tr class="toggleable">
            <?php
        $resultlist = array(
                            array('label' => _T('10 first lines of result','pkgs'),'value' => "10@firstlines"),
                            array('label' => _T('20 first lines of result','pkgs'),'value' => "20@firstlines"),
                            array('label' => _T('30 first lines of result','pkgs'),'value' => "30@firstlines"),
                            array('label' => _T('Complete results','pkgs'),'value' => "@resultcommand"),
                            array('label' => _T('10 last lines of result','pkgs'),'value' => "10@lastlines"),
                            array('label' => _T('20 last lines of result','pkgs'),'value' => "20@lastlines"),
                            array('label' => _T('30 last lines of result','pkgs'),'value' => "30@lastlines"),
                            array('label' => _T('20 last lines of result','pkgs'),'value' => "2@lastlines"),
                            array('label' => _T('The last line of result','pkgs'),'value' => "1@lastlines"),
        );
        $posibleresultname = array(
                                    "10@firstlines",
                                    "20@firstlines",
                                    "30@firstlines",
                                    "@resultcommand",
                                    "10@lastlines",
                                    "20@lastlines",
                                    "30@lastlines",
                                    "2@lastlines",
                                    "1@lastlines"
        );
        $options = "";
        $boolselected = false;
        // search in $Post if input result
        foreach($_POST as $key=>$val){
            if (in_array($key, $posibleresultname)){
                $selectresult = $key;
                $boolselected = true;
                break;
            }
        }
        if (!isset($selectresult)){
            $selectresult = "1@lastlines";
        }

        foreach($resultlist as $selectedbyuser)
        {
            if(isset($selectresult) && $selectedbyuser['value'] == $selectresult)
            {
                $options .= "<option value='".$selectedbyuser['value']."' selected>".$selectedbyuser['label']."</option>";
            }
            else
                $options .= "<option value='".$selectedbyuser['value']."'>".$selectedbyuser['label']."</option>";
        }

        if($boolselected)// and $selectresult != "noneresult"
        {
            echo '
            <td>
                <input type="checkbox" checked onclick="if(jQuery(this).is(\':checked\')){
                                                            jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                                        }
                                                        else{
                                                            jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                                        }" />'._T("Return result","pkgs").'
            </td>
            <td>
                <select  onchange="jQuery(this).attr(\'name\',jQuery(this).val());" name="'.$selectresult.'">'.$options.'</select>
            </td>
            <td></td><td></td>
            ';

        }
        else{
            echo '
            <td>
                <input type="checkbox" onclick="if(jQuery(this).is(\':checked\')){
                                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',false);
                                                }
                                                else{
                                                    jQuery(this).closest(\'td\').next().find(\'select\').prop(\'disabled\',true);
                                                }" />Return result
            </td>
            <td>
            <select disabled onchange="jQuery(this).attr(\'name\',jQuery(this).val());"
                name="1@lastlines">'.$options.'</select>
            </td>
            <td></td><td></td>';
        }
        ?>
        </tr>


        <tr class="toggleable">
           <?php
            if(isset($pathdirectorytounzip))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("Unzip to specified folder","pkgs").'
                </td>
                <td>
                    <input " type="text"  value="'.$pathdirectorytounzip.'" name="pathdirectorytounzip"  />
                </td><td></td><td></td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("Unzip to specified folder","pkgs").'
                </td>
                <td>
                    <input type="text" value="" disabled name="pathdirectorytounzip"  />
                </td><td></td><td></td>';
            }
            ?>
        </tr>
         <tr class="toggleable">
        <?php
           if(isset($goto))
            {
                echo '<td width="16%">
                    <input type="checkbox" checked
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                                }" />'._T("Go to step","pkgs").'
                </td>
                <td width="25%">
                    <input type="text"  value="'.$goto.'" name="goto"  />
                </td><td></td><td></td>';
            }
            else{
                echo '<td width="16%">
                    <input type="checkbox"
                        onclick="if(jQuery(this).is(\':checked\')){
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                                }
                                else{
                                    jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                                }" />'._T("Go to step","pkgs").'
                    </td>
                    <td width="25%">
                         <input type="text" disabled value="" name="goto"  />
                    </td><td></td><td></td>';
            }
            ?>
        </tr>



         <tr class="toggleable">
           <?php
            if(isset($success))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("On success go to step","pkgs").'
                </td>
                <td>
                    <input " type="text"  value="'.$success.'" name="success"  />
                </td></td><td></td><td></td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("On success go to step","pkgs").'
                </td>
                <td>
                    <input type="text" value="END_SUCCESS" disabled name="success"  />
                </td></td><td></td><td></td>';
            }
            ?>
        </tr>
         <tr class="toggleable">
            <?php
            if(isset($error))
            {
                echo '
                <td>
                    <input type="checkbox" checked onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("On error go to step","pkgs").'
                </td>
                <td>
                    <input " type="text"  value="'.$error.'" name="error"  />
                </td></td><td></td><td></td>';
            }
            else{
                echo '
                <td>
                    <input type="checkbox"  onclick="
                    if(jQuery(this).is(\':checked\')){
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',false);
                    }
                    else{
                        jQuery(this).closest(\'td\').next().find(\'input\').prop(\'disabled\',true);
                    }" />'._T("On error go to step","pkgs").'
                </td>
                <td>
                    <input type="text" value="END_ERROR" enabled name="error"  />
                </td></td><td></td><td></td>';
            }
            ?>
        </tr>
    </table>
        <!-- Option timeout -->
    </div>
    <input  class="btn btn-primary" type="button" onclick="jQuery(this).parent().parent('li').detach()" value="<?php echo _T("Delete", "pkgs");?>" />
  <input  class="btn btn-primary" id="property" onclick='jQuery(this).parent().find(".toggleable").each(function(){ jQuery(this).toggle()});' type="button" value="<?php echo _T("Options", "pkgs");?>" />
</div>

<script type="text/javascript">
    jQuery(document).ready(function(){
        jQuery("#tableToggle tr.toggleable").hide();
    });
</script>
