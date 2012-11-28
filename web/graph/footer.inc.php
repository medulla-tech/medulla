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

$root = $conf["global"]["root"];
//generate MMCApp (CSS, etc...)
$MMCApp =& MMCApp::getInstance();
$MMCApp->render();

?>
            <div class="clearer"></div>
        </div><!-- section -->
    </div><!-- content -->

    <div id="overlay" class="overlay" style="display: none"></div>
    <div id="popup" class="popup" style="display: none;">
        <div style="float:right"><a href="#" onclick="toggleVisibility('popup'); $('overlay').hide(); return false;"><img src="img/common/icn_close.png" alt ="[x]"/></a></div>
        <div id="__popup_container"><?php echo  _("If this phrase does not change, you browser is not supported by the MMC application"); ?></div>
    </div>
<?php
if (isset($_SESSION['notify'])) {
    $n = unserialize($_SESSION['notify']);
    if ($n->strings)
        $n->show();
}
?>
    <div id="footer">
        MMC Agent <a href="#" onclick="showPopupUp(event,'version.php'); return false;"><?php  echo $_SESSION["modListVersion"]['ver'] ?></a>
    </div>
</div><!-- wrapper -->
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

<?php
/*if (isset($_SESSION["doeffect"])) {
    print 'Element.hide("logo");';
    print 'new Effect.Appear("logo", {duration: 2.0});';
    unset($_SESSION["doeffect"]);
}*/
?>

//Event.observe(input, 'focus', ifocus, false);
-->

</script>
</body>
</html>

<?php
unset($root);
?>
