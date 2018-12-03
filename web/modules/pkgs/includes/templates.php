<?php
/**
 * (c) 2016 Siveo, http://www.siveo.net/
 *
 * $Id$
 *
 * This file is part of Pulse 2, http://www.siveo.net/
 *
 * Pulse 2 is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * Pulse 2 is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 * You should have received a copy of the GNU General Public License
 * along with Pulse 2; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
 * MA 02110-1301, USA.
 *
 */
?>


<div class="critic-hidden">
    <input type="hidden" name="<?php echo $_POST['option'];?>" value="<?php if(isset($_POST['value'])) echo $_POST['value'];?>"/>
</div>

<div class="mandatory-hidden">
    <input type="hidden" name="<?php echo $_POST['option'];?>" value="<?php if(isset($_POST['value'])) echo $_POST['value'];?>"/>
</div>

<div class="mandatory-text">
    <h4><?php echo $_POST['option'];?></h4>
    <input type="text" name="<?php echo $_POST['option'];?>" onchange="testOptions()" placeholder="<?php echo $_POST['option'];?>"  value="<?php if(isset($_POST['value'])) echo $_POST['value'];?>"/>
</div>

<div class="extra-text">
    <h4><?php echo $_POST['option'];?></h4>

    <a href="#" class="add"><img src="/mmc/modules/pkgs/graph/img/add.png" width="24px" alt="Add to action"/></a>
    <input type="text" name="<?php echo $_POST['option'];?>" onchange="testOptions()" value="<?php if(isset($_POST['value'])) echo $_POST['value'];?>" placeholder="<?php echo $_POST['option'];?>"/>
    <a href="#" class="remove"><img src="/mmc/modules/pkgs/graph/img/remove.png" width="24px" alt="-remove option"/></a>
</div>

<div class="mandatory-number">
    <h4><?php echo $_POST['option'];?></h4>
    <input type="number" name="<?php echo $_POST['option'];?>" onchange="testOptions()" placeholder="<?php echo $_POST['option'];?>"  value="<?php if(isset($_POST['value'])) echo $_POST['value'];?>"/>
</div>

<div class="extra-number">
    <h4><?php echo $_POST['option'];?></h4>

    <a href="#" class="add"><img src="/mmc/modules/pkgs/graph/img/add.png" width="24px" alt="Add to action"/></a>
    <input type="text" name="<?php echo $_POST['option'];?>" onchange="testOptions()" value="<?php if(isset($_POST['value'])) echo $_POST['value'];?>" placeholder="<?php echo $_POST['option'];?>"/>
    <a href="#" class="remove"><img src="/mmc/modules/pkgs/graph/img/remove.png" width="24px" alt="-remove option"/></a>
</div>

<div class="mandatory-select-label">

    <h4><?php echo $_POST['option'];?></h4>
    <select name="<?php echo $_POST['option'].'-label';?>" >
        <?php if(isset($_POST['value']) && $_POST['value'] == "NEXT")
            echo '<option value="NEXT" selected>NEXT</option>';

        else
            echo '<option value="NEXT">NEXT</option>';

        foreach($_POST['labels'] as $id=>$label)
        {
            if(isset($_POST['value']) && $_POST['value'] == $label)
                echo '<option value="'.$label.'" selected>'.$_POST['value'].'</option>';

            else
                echo "<option value='$label' >$label</option>";
        }
        ?>
    </select>
    <input type="hidden" name="<?php echo $_POST['option'];?>" value=" " />
</div>

<div class="extra-select-label">
    <h4><?php echo $_POST['option'];?></h4>

    <select name="<?php echo $_POST['option'].'-label';?>" >
        <?php if(isset($_POST['value']) && $_POST['value'] == "NEXT")
        {
            echo '<option value="NEXT" selected>NEXT</option>';
        }
        else
            echo '<option value="NEXT">NEXT</option>';

        foreach($_POST['labels'] as $id=>$label)
        {
            if(isset($_POST['value']) && $_POST['value'] == $label)
            {
                echo '<option value="'.$label.'" selected>'.$_POST['value'].'>'.$label.'</option>';
            }
            else
                echo "<option value='$label' >$label</option>";
        }
        ?>
    </select>
    <input type="hidden" name="<?php echo $_POST['option'];?>" value=" " />
    <a href="#" class="remove"><img src="/mmc/modules/pkgs/graph/img/remove.png" width="24px" alt="-remove option"/></a>
</div>
