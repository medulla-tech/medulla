<?php
require_once("../xmlrpc.php");
require_once("../../../../includes/session.inc.php");
require_once("../../../../includes/xmlrpc.inc.php");
?>
<div class="header">
    <h1>Go to package folder</h1>
</div>


<div class="content">
    <div>
        <input type="hidden" name="step" />
        <input type="hidden" name="actionlabel" value="<?php echo (isset($_POST['actionlabel']))? $_POST['actionlabel'] : uniqid(); ?>"/>
        <input type="hidden" name="action" value="action_pwd_package" />


        <?php
        $packageList = xmpp_packages_list();
        $options = "";

        foreach($packageList as $id=>$package)
        {
            if(isset($_POST['packageuuid']) && $_POST['packageuuid'] == $package['uuid'])
            {
                $options .= "<option value='".$package['uuid']."' selected>".$package['name']."</option>";
            }
            else
                $options .= "<option value='".$package['uuid']."'>".$package['name']."</option>";
        }

        if(isset($_POST['packageuuid']))
        {
            echo '<p><input type="checkbox" checked onclick="if(jQuery(this).is(\':checked\')){jQuery(this).next().prop(\'disabled\',false);}else{jQuery(this).next().prop(\'disabled\',true);}" />Package uuid <select name="packageuuid">'.$options.'</select></p>';

        }
        else{
            echo '<p><input type="checkbox" onclick="if(jQuery(this).is(\':checked\')){jQuery(this).next().prop(\'disabled\',false);}else{jQuery(this).next().prop(\'disabled\',true);}" />Package uuid <select disabled name="packageuuid">'.$options.'</select></p>';
        }

        ?>

    </div>

    <input type="button" onclick="jQuery(this).parent().parent('li').detach()" value="Delete" />
</div>
