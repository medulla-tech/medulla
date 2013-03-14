<?php
/**
 * (c) 2013 Mandriva, http://www.mandriva.com
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

class MultiFileTpl extends AbstractTpl {

    function MultiFileTpl($name) {
        $this->name=$name;
    }

    function display() {
        // FIXME use session or not ?
        $random_dir = "pulse_rdir_" . uniqid();
        $_SESSION['random_dir'] = $random_dir;
        print '<div id="file-uploader">          
                <noscript>                      
                        <p>Please enable JavaScript to use file uploader.</p>
                        <!-- or put a simple form for upload here -->
                </noscript>         
        </div>

        <input id="random_dir" name="random_dir" type="hidden">
        <div id="parentTrigger">
        <div id="triggerUpload">' . _T('Upload Queued Files', "pkgs") . '</div>
        </div>
    
        <script src="modules/pkgs/lib/fileuploader/fileuploader.js" type="text/javascript"></script>
        <link href="modules/pkgs/lib/fileuploader/fileuploader.css" rel="stylesheet" type="text/css">
        <script>
        var box = $(\'p_api\');
        var selectedIndex = box.selectedIndex;
        var selectedPapi = box.options[selectedIndex].value;
        function createUploader(){
            var uploader = new qq.FileUploader({
                element: document.getElementById(\'file-uploader\'),
                action: \'modules/pkgs/lib/fileuploader/fileuploader.php\',
                debug: true,
                multiple: true,
                demoMode: false,
                random_dir: \'' . $random_dir . '\',
                selectedPapi: selectedPapi,
                autoUpload: false,
                uploadButtonText: "' . _T('Click here to select files', "pkgs") . '",
                onComplete: function(id, file, responseJson){
                    // queue
                    if(uploader.getInProgress() > 0){
                        return;
                    }
                    // DEBUG: write action to do when upload complete

                    url = \'' . urlStrRedirect("pkgs/pkgs/ajaxGetSuggestedCommand") . '&papiid=\' + selectedPapi;
                    url += \'&tempdir=' . $random_dir . '\';

                    new Ajax.Request(url, {
                        onSuccess: function(response) {
                            $(\'label\').value = response.headerJSON.label;
                            $(\'version\').value = response.headerJSON.version;
                            $(\'commandcmd\').value = response.headerJSON.commandcmd;
                        }
                    });
                }
            });           
            $(\'triggerUpload\').observe(\'click\', function() {
                uploader.uploadStoredFiles();
            });
        }
        
        createUploader();
    </script>';
    }
}

?>
