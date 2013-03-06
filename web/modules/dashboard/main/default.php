<?php
/**
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007-2012 Mandriva, http://www.mandriva.com
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
require("modules/dashboard/includes/dashboard-xmlrpc.inc.php");

?>
<script src="jsframework/cookiejar.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.raphael-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.pie-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/g.line-min.js"></script>
<script type="text/javascript" src="jsframework/lib/raphael/utilities.js"></script>
<?php

$d = new Div(array("id" => "dashboard"));
$d->display();

// Search for panels...
foreach(getPanels() as $panelName) {
    $modules = $_SESSION["modulesList"];
    foreach($modules as $module) {
        $basedir = "modules/$module/includes/panels/";
        if (is_dir($basedir)) {
            $h = opendir($basedir);
            while (false !== ($f = readdir($h))) {
                if (substr($f, 0, 1) != ".") {
                    if ($f == $panelName . ".inc.php") {
                        $file = $basedir . $f;
                        include_once($file);
                        if (!isset($options["enable"]))
                            $options["enable"] = True;
                        if (!isset($options["refresh"]))
                            $options["refresh"] = 10;
                        if ($options["enable"]) {
                            $panel = new AjaxPage(urlStrRedirect('dashboard/main/ajaxPanels'), $options["id"], array("file" => urlencode($file)), $options["refresh"]);
                            $panel->class = "panel";
                            $panel->display();
                        }
                    }
                }
            }
        }
    }
}

?>
<script type="text/javascript">
    load = function() {
        try {
            settings = mmcookie.get('dashboard-settings');
            saved_modules = 0;
            for(zone in settings)
                for(module in settings[zone])
                    saved_modules++;
            // if there is more or less modules loaded
            // invalidate the settings
            if (modules.length != saved_modules)
                settings = false;
        }
        catch (err) {
            mmcookie.remove('dashboard-settings');
            settings = false;
        }
        if (!settings) {
            // create default settings
            settings = {};
            // store column info
            for(var c=0; c<cols; c++)
                settings['dashboard-column_'+c] = {};
            // add each module in a column
            for(var m=0, c=0; m<modules.length; m++, c++) {
                settings['dashboard-column_'+c][modules[m].id] = modules[m].id;
                // don't fill the first column
                // base module can be very high
                if (c == cols-1)
                    c = 0;
            }
            // save the settings
            mmcookie.put('dashboard-settings', settings);
        }
        // apply the settings
        zone_no = 0;
        for(zone in settings) {
            // create the columns
            var z = new Element('div', {'class': 'dashboard-column', 'id': 'dashboard-column_'+zone_no});
            // add modules in columns
            for(module in settings[zone])
                z.appendChild(modules.find(function(m) { return m.id == module; }));
            // display the column
            home.appendChild(z);
            zone_no++;
        }
        // add more columns if needed
        if(Object.keys(settings).length < cols) {
            for(var i=Object.keys(settings).length; i<cols; i++) {
                var z = new Element('div', {'class': 'dashboard-column', 'id': 'dashboard-column_'+i});
                home.appendChild(z);
            }
        }
    }

    save = function() {
        new_settings = {};
        sortables.each(function (z) {
            $$('#'+z.id+' .panel').each(function(m) {
                if (!new_settings[z.id])
                    new_settings[z.id] = {};
                new_settings[z.id][m.id] = m.id;
            });
        });
        mmcookie.put('dashboard-settings', new_settings);
    }

    var settings = false;
    var mmcookie = new CookieJar({
        expires: 604800, // one week
        path: '/mmc/'
    });
    var home = $('dashboard');
    var modules = $$('.panel');
    // calculate the number of columns for the screen
    var cols = Math.floor($('dashboard').offsetWidth / 210);
    // load the modules in the columns
    load();
    // make the modules sortable
    var sortables = $$('.dashboard-column');
    sortables.each(function (sortable) {
      Sortable.create(sortable, {
        containment: sortables,
        constraint: false,
        tag: 'div',
        only: 'panel',
        dropOnEmpty: true,
        handle: 'handle',
        hoverclass: 'panel-hover',
        onUpdate: function() {
            save();
        }
      });
      // Wait a little that all panels are loaded
      setTimeout(function() {
          $$('.handle').each(function(m) {
            m.observe("mousedown", function(m) {
                sortables.each(function (s) {
                    s.style.border = "1px solid #ccc";
                    s.style.background = "#FFFAFA";
                });
            });
          });
          $$('.handle').each(function(m) {
            m.observe("mouseup", function(m) {
                sortables.each(function (s) {
                    s.style.border = "1px solid white";
                    s.style.background = "white";
                });
            });
          });
      }, 500);
});
</script>
