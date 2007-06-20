<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php
/* $Id$ */
$root = $conf["global"]["root"];



//generate LMCApp (CSS, etc...)
$LMCApp =& LMCApp::getInstance();
$LMCApp->render();

?>

<div class="clearer"></div>

</div><!-- section -->

<div id="sectionBottomLeft"><div id="sectionBottomRight">
<img src="<?php echo $root; ?>img/common/spacer.gif" alt="" width="1" height="1" />
</div></div>

</div><!-- sectionContainer -->
</div><!-- Content -->

<?php
    $n = new NotifyWidget();
    $n->showJS();
?>

<div id="footer">
LMC Agent

    <a href="#" onclick="showPopupUp(event,'version.php'); return false;">
        <?php  echo $_SESSION["modListVersion"]['ver'] ?>
    </a>

</div>

</div>
<script type="text/javascript">

<!--

function canChangeStyle(elt) {
    if (elt.id=='param') return false;
    if (elt.type=='text') return true;
    if (elt.type=='checkbox') return true;
    if (elt.type=='select') return true;
    if (elt.type=='password') return true;
    return false;
}

function ifocus(e) {
    var elt = Event.element(e);
    if (canChangeStyle(elt)) {
        Element.setStyle(elt, {'border-color': '#EE5010'});
        Element.setStyle(elt, {'background-color': '#FFFFEE'});
    }
}
function iblur(e) {
    var elt = Event.element(e);
    if (canChangeStyle(elt)) {
        Element.setStyle(elt, {'border-color': '#666'})
        Element.setStyle(elt, {'background-color': '#FFF'});
    }
}

function focusStyler(nodes) {
var i = 0;

nodes.each( function(node) {

        Event.observe(node, 'focus', ifocus, false);
        Event.observe(node, 'blur', iblur, false);
        if ((i==0)&&(canChangeStyle(node))) {
            node.focus();
            Element.setStyle(node, {'border-color': '#EE5010'});
            Element.setStyle(node, {'background-color': '#FFFFEE'});
        }

        if (canChangeStyle(node)) {
            i++;
        }
    });
}

var inputList = document.getElementsByTagName('input');
var nodes = $A(inputList);

focusStyler(nodes);

<?
if (isset($_SESSION["doeffect"])) {
    print 'Element.hide("logo");';
    Print 'new Effect.Appear("logo", {duration: 2.0});';
    unset($_SESSION["doeffect"]);
}
?>

//Event.observe(input, 'focus', ifocus, false);
-->

</script>
</body>
</html>

<?php
unset($root);
?>