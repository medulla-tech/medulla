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

require("graph/navbar.inc.php");

function display_page($page,$submod,$mod) {
    if ($page->getDescription() && $page->isVisible()) {
        $url = urlStr($mod->getName()."/".$submod->getName()."/".$page->_action);
        if (hasCorrectAcl($mod->getName(),$submod->getName(),$page->_action)) {
            echo "<li><a href=\"$url\">".$page->getDescription()."</a></li>";
        } else {
            echo "<li style=\"color: #BBB;\">".$page->getDescription()."</li>";
        }
    }
}

function display_submod($submod,$mod) {
    if (!$submod->hasVisible()) {
        return;
    }
    echo '<div class="submod">';
    ?> <img src="<?php echo  $submod->_img ?>_select.png" alt="" style="float:right;" /><?php
    /*if (!$submod->_visibility) { //if submod not visible
        return;
    }*/
    echo '<h3>';
    $url = urlStr($submod->_defaultpage);
    echo "<a style=\"text-decoration: none;\" href=\"$url\">".$submod->getDescription()."</a><br/>";
    echo "</h3>";
    print "<ul>";
    foreach ($submod->getPages() as $page) {
        display_page($page,$submod,$mod);
    }
    print "</ul>";
    echo '</div>';
}

$i = 1;

function display_mod($mod) {
    if (!$mod->hasVisible()) {
        return;
    }

    global $i;
?>
    <div class="column" id="col<?php echo $i; ?>" style="width:250px;">
                <div id="<?php echo $mod->getName(); ?>" class="portlet">
                    <div class="portlet-header"><?php echo $mod->getDescription(); ?></div>
                    <div class="portlet-content">
    <?php foreach (getSorted($mod->getSubmodules()) as $submod) {
    ?>
        
                    <?php display_submod($submod,$mod); $i++; ?>
    <?php
    }
    ?>
            </div>
        </div>
    </div>
<?php
}

$MMCApp =& MMCApp::getInstance();
$modules = getSorted($MMCApp->getModules());
$nb_modules = count($modules);

$p = new PageGenerator(_("Home"));
$p->display();

?>
    <div id="home">
        <?php
        foreach($modules as $key => $mod) {
            display_mod($mod);
        }
        ?>
    </div>
    <div class="clearer"></div>
</div>


<style>
.column { width: 230px; float: left; padding-bottom: 100px; }
.portlet { margin: 0 1em 1em 0; border:1px solid #333; -moz-border-radius: 5px; border-radius: 5px; }
.portlet-header { margin: 0.3em; padding-bottom: 4px; padding-left: 0.2em; font-size:14px; background:#324C96; color:#fff; padding:5px; -moz-border-radius: 5px; border-radius: 5px; cursor:move; }
.portlet-header .ui-icon { float: right; }
.portlet-content { padding: 0.4em; }
.ui-sortable-placeholder { border: 2px dotted #324C96; visibility: visible !important; height: 50px !important; }
.ui-sortable-placeholder * { visibility: hidden; }
</style>


<script type="text/javascript">
// function that writes the list order to a cookie
function saveOrder() {
    jQuery(".column script").remove();
    jQuery(".column").each(function(index, value){
        var colid = value.id;
        var cookieName = "home-cookie-" + colid;
        // Get the order for this column.
        var order = jQuery('#' + colid).sortable("toArray");
        // For each portlet in the column
        for ( var i = 0, n = order.length; i < n; i++ ) {
            // Determine if it is 'opened' or 'closed'
            var v = jQuery('#' + order[i] ).find('.portlet-content').is(':visible');
            // Modify the array we're saving to indicate what's open and
            //  what's not.
            order[i] = order[i] + ":" + v;
        }
        jQuery.cookie(cookieName, order, { path: "/", expiry: new Date(2012, 1, 1)});
    });
}

// function that restores the list order from a cookie
function restoreOrder() {
    jQuery(".column").each(function(index, value) {
        var colid = value.id;
        var cookieName = "home-cookie-" + colid
        var cookie = jQuery.cookie(cookieName);
        if ( cookie == null ) { return; }
        var IDs = cookie.split(",");
        for (var i = 0, n = IDs.length; i < n; i++ ) {
            var toks = IDs[i].split(":");
            if ( toks.length != 2 ) {
                continue;
            }
            var portletID = toks[0];
            var visible = toks[1]
            var portlet = jQuery(".column")
                .find('#' + portletID)
                .appendTo(jQuery('#' + colid));
            if (visible === 'false') {
                portlet.find(".ui-icon").toggleClass("ui-icon-minus");
                portlet.find(".ui-icon").toggleClass("ui-icon-plus");
                portlet.find(".portlet-content").hide();
            }
        }
    });
} 

jQuery(document).ready( function () {
    jQuery(".column").sortable({
        connectWith: ['.column'],
        stop: function(event,ui) { ui.item.css('opacity',1);saveOrder(); },
        sort: function(event,ui) { ui.item.css('opacity',0.7); }
    }); 

    jQuery(".portlet")
        .addClass("ui-widget ui-widget-content")
        .addClass("ui-helper-clearfix ui-corner-all")
        .find(".portlet-header")
        .addClass("ui-widget-header ui-corner-all")
        .prepend('<span class="ui-icon ui-icon-minus"></span>')
        .end()
        .find(".portlet-content");

    restoreOrder();

    jQuery(".portlet-header .ui-icon").click(function() {
        jQuery(this).toggleClass("ui-icon-minus");
        jQuery(this).toggleClass("ui-icon-plus");
        jQuery(this).parents(".portlet:first").find(".portlet-content").toggle();
        saveOrder(); // This is important
    });
    jQuery(".portlet-header .ui-icon").hover(
        function() {jQuery(this).addClass("ui-icon-hover"); },
        function() {jQuery(this).removeClass('ui-icon-hover'); }
    );
});  
</script>