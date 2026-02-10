<?php
/*
 * (c) 2004-2007 Linbox / Free&ALter Soft, http://linbox.com
 * (c) 2007 Mandriva, http://www.mandriva.com
 * (c) 2016-2023 Siveo, http://www.siveo.net
 * (c) 2024-2025 Medulla, http://www.medulla-tech.io
 *
 * $Id$
 *
 * This file is part of MMC, http://www.medulla-tech.io
 *
 * MMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 3 of the License, or
 * any later version.
 *
 * MMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with MMC; If not, see <http://www.gnu.org/licenses/>.
 * file: PageGenerator.php
 */
require("FormGenerator.php");
require_once("utils.inc.php");


function generateSplashScreen(
    string $imageUrl,
    int $appearAnimTime = 500,
    int $disappearDelay = 3000,
    int $disappearAnimTime = 800,
    string $containerId = 'splash-container',
    string $additionalCss = '',
    string $focusId = '' // <-- ID de l'élément à focus après splash
): void {
    $appearMs = max(0, (int)$appearAnimTime);
    $disappearDelayMs = max(0, (int)$disappearDelay);
    $disappearMs = max(0, (int)$disappearAnimTime);

    $css = "
        <style>
            #$containerId {
                position: fixed;
                inset: 0;
                display: flex;
                align-items: center;
                justify-content: center;
                background: rgba(0,0,0,0.85);
                opacity: 1;
                z-index: 2147483647;
                overflow: hidden;
                transition: opacity {$disappearMs}ms ease-in-out;
                $additionalCss
            }
            #$containerId.fade-out { opacity: 0; }
            #$containerId .splash-image {
                width: 50vw;
                max-width: 90%;
                height: auto;
                opacity: 0;
                transform: scale(0.92);
                transition: opacity {$appearMs}ms ease-in-out, transform {$appearMs}ms ease-in-out;
                border-radius: 6px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }
            #$containerId .splash-image.visible { opacity: 1; transform: scale(1); }
            #$containerId .splash-image.hide { opacity: 0; transform: scale(0.6); }
        </style>
    ";

    $html = "
        <div id='$containerId' role='presentation' aria-hidden='true'>
            <img class='splash-image' src='$imageUrl' alt='Image de présentation'>
        </div>
    ";

    $js = "
        <script>
            (function() {
                const appearMs = {$appearMs};
                const disappearDelayMs = {$disappearDelayMs};
                const disappearMs = {$disappearMs};

                const container = document.getElementById('{$containerId}');
                if (!container) return;
                const img = container.querySelector('.splash-image');
                if (!img) return;

                // apparition
                requestAnimationFrame(() => {
                    requestAnimationFrame(() => img.classList.add('visible'));
                });

                // disparition
                setTimeout(() => {
                    img.style.transitionDuration = disappearMs + 'ms, ' + disappearMs + 'ms';
                    img.classList.remove('visible');
                    requestAnimationFrame(() => {
                        img.classList.add('hide');
                        container.classList.add('fade-out');
                    });

                    setTimeout(() => {
                        container.remove();

                        // focus sur l'élément si ID fourni et présent
                        if ('{$focusId}') {
                            const el = document.getElementById('{$focusId}');
                            if (el) el.focus();
                        }

                    }, disappearMs + 50);

                }, disappearDelayMs);
            })();
        </script>
    ";

    echo $css . $html . $js;
}
/**
 * Generates a unique ID for auto-generation in JavaScript or other similar contexts.
 * The ID is incremented each time the function is called, ensuring uniqueness.
 * This ID can be used to generate dynamic HTML elements, such as form fields, with unique IDs.
 */
function getUniqId()
{
    global $__uniqID;
    $__uniqID++;
    return $__uniqID;
}

/**
 * This function allows for echoing objects and strings using the same function, similar to "echo" in PHP5.
 */
function echo_obj($obj) {
    // Check if the variable is an object and convert it to a string
    if (is_object($obj)) {
        // Convert the object to a string and replace new lines with <br> tags for formatting purposes
        echo nl2br(strval($obj));
    } elseif (is_bool($obj)) {
        // Display an image of 'yes.svg' if the boolean is true, otherwise leave the output blank
        echo $obj ? '<img src="img/other/yes.svg" alt="yes" width="25" height="25" />' : '';
    } else {
        // Print the given string with new lines replaced by <br> tags for formatting purposes
        echo nl2br($obj);
    }
}

/**
 * debug print
 */
function debug($obj, $return = false)
{
    // Define a string to hold the output in a preformatted style with Courier font and bold text
    $s = '<pre style="font-family:Courier, monospace; font-weight:bold ">';

    // Print the given object in a readable format using print_r()
    $s .= print_r($obj, true);

    // Close the preformatted string and output it
    $s .= '</pre>';

    // If the return variable is set to true, return the debug output instead of printing it
    if ($return) {
        // Return the generated debug output as a string
        return $s;
    } else {
        // Otherwise, print the debug output directly to the screen
        print $s;
    }
}

/**
 * class for action encapsulation
 * Abstract class for the moment
 * @see EditInPlace
 */
class ActionEncapsulator
{
    public function __construct()
    {

    }

    public function __toString()
    {
        return "default action encapsulator";
    }

}

/**
 * AutoGenerate an EditInPlace text
 * based on scriptaculous javascript
 */
class EditInPlace extends ActionEncapsulator
{
    public $origText;
    public $url;
    public $param;

    public function __construct($origText, $url, $param)
    {
        $this->origText = $origText;
        $this->url = $url;
        $this->param = $param;
    }

    public function __toString()
    {

        $param = array();

        foreach ($this->param as $key => $value) {
            $param[] = "$key=$value";
        }

        $urlparam = implode("&", $param);

        if ($this->origText == '') {
            $this->origText = "n/a";
        }

        $idx = getUniqId();

        $str = '';
        $str .= "<span id=\"id$idx\" class=\"editinplace\">" . $this->origText . "</span>";


        /* $str .= '<script type="text/javascript">';
          $str .= "     new Ajax.InPlaceEditor($('id$idx'),'".$this->url."', {\n
          okButton: true, cancelLink: true, cancelText : '"._('Cancel')."',
          highlightcolor : '#FF9966',
          ajaxOptions: {method: 'get' },\n
          callback: function(form,value) {\n
          return '$urlparam&value='+value\n
          }\n
          });\n
          </script>\n"; ===> CLASS NOT USED */
        return $str;
    }

}

/**
 *  class for action in various application
 */
class ActionItem
{
    /**
    *  Constructor
    * @param $desc         description
    * @param $action       string include in the url
    * @param $classCss     class for CSS like "supprimer" or other class define in the CSS global.css
    * @param $paramString  add "&$param=" at the very end of the url
    * @param $module       module name
    * @param $submod       submodule name
    * @param $tab          optional tab
    * @param $mod          optional mod flag
    * @param $staticParams tableau associatif de paramètres GET statiques ajoutés à l'URL
    */
    public $desc;
    public $action;
    public $classCss;
    public $paramString;
    public $module;
    public $submod;
    public $mod;
    public $path;
    public $tab;
    public $staticParams; // pour les paramètres fixes ajoutés

    /**
     *  Constructor
     * @param $desc description
     * @param $action string include in the url
     * @param $classCss class for CSS like "supprimer" or other class define
     *    in the CSS global.css
     * @param $paramString add "&$param=" at the very end of the url
     */
    public function __construct(
        $desc,
        $action,
        $classCss,
        $paramString,
        $module = null,
        $submod = null,
        $tab = null,
        $mod = false,
        $staticParams = null
    ) {
        $this->desc        = $desc;
        $this->action      = $action;
        $this->classCss    = $classCss;
        $this->paramString = $paramString;
        $this->module      = $module ?? $_GET["module"];
        $this->submod      = $submod ?? $_GET["submod"];
        $this->tab         = $tab;
        $this->mod         = $mod;
        $this->path        = $this->module . "/" . $this->submod . "/" . $this->action;
        if ($this->tab != null) {
            $this->path .= "/" . $this->tab;
        }
        $this->staticParams = is_array($staticParams) ? $staticParams : array();
    }

    /**
     *  display a link for the action
     *  @param add &$this->param=$param at the very end of the url
     *  display "displayWithRight" if you have correct right
     */
    public function display($param, $extraParams = array())
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            $this->displayWithRight($param, $extraParams);
        } else {
            $this->displayWithNoRight($param, $extraParams);
        }
    }

    /**
     * display function if you have correct right on this action
     */
    public function displayWithRight($param, $extraParams = array())
    {
        /* add special param for actionItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        echo "<li class=\"" . $this->classCss . "\">";
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($extraParams);
        }
        echo "<a title=\"" . $this->desc . "\" href=\"" . urlStr($this->path) . $urlChunk . "\">&nbsp;</a>";
        echo "</li>";
    }

    /**
     * display function if you don't have the right for this action
     */
    public function displayWithNoRight($param, $extraParams = array())
    {
        echo "<li class=\"" . $this->classCss . " inactive\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" onclick='return false;'>&nbsp;</a>";
        echo "</li>";
    }

    /**
     * transform $obj param in link for this action
     */
    public function encapsulate($obj, $extraParams = array())
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            if (is_array($extraParams) & !empty($extraParams)) {
                $urlChunk = $this->buildUrlChunk($extraParams);
            } else {
                $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($obj);
            }
            $str = "<a title=\"" . $this->desc . "\" href=\"main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "\">";
            $str .= trim($obj);
            $str .= "</a>";
            return $str;
        } else {
            $str = "<a title=\"" . $this->desc . "\" href=\"#\">";
            $str .= "$obj";
            $str .= " </a>";
            return $str;
        }
    }

    /**
    * Construit une chaîne de paramètres GET à partir d'un tableau associatif.
    * ------------------------------------------------------------------------
    * - Les paramètres "statiques" définis dans $this->staticParams sont
    *   fusionnés avec les paramètres passés en argument ($arr).
    * - En cas de clé en doublon, ce sont les valeurs de $arr (dynamiques)
    *   qui prennent le dessus.
    * - Chaque clé/valeur est automatiquement encodée pour être conforme à l'URL.
    *
    * @param array $arr Tableau associatif de paramètres dynamiques
    *                   (clé => valeur) à ajouter à l'URL.
    *
    * @return string Chaîne formatée de type "&amp;key=value&amp;key2=value2"
    *
    * Exemple :
    *   $this->staticParams = array('entity' => 1, 'restreint' => 1);
    *   $arr = array('login' => 'root', 'restreint' => 2);
    *
    *   Résultat :
    *   "&amp;entity=1&amp;restreint=2&amp;login=root"
    */
    public function buildUrlChunk($arr)
    {
        // S'assurer que $arr est bien un tableau
        if (!is_array($arr)) {
            $arr = [];
        }

        // S'assurer que staticParams est bien un tableau
        $static = is_array($this->staticParams) ? $this->staticParams : [];

        // Fusion des paramètres fixes + dynamiques
        $merged = array_merge($static, $arr);

        $urlChunk = "";
        foreach ($merged as $option => $value) {
            $urlChunk .= "&amp;" . $option . "=" . urlencode($value);
        }
        return $urlChunk;
    }


    /**
     * display help (not use for the moment)
     */
    public function strHelp()
    {
        $str = "";
        $str .= "<li class=\"" . $this->classCss . "\">";
        $str .= "<a title=\"" . $this->desc . "\" href=\"#\">";
        $str .= " </a>" . $this->desc . "</li>";
        return $str;
    }
    /**
    * Génère plusieurs liens pour la même action, à partir d'une liste de valeurs
    *
    * @param array $paramsList  tableau de valeurs pour le paramètre principal
    *                           Exemple : ['root', 'kjf', 'admin']
    * @param array $extraParams tableau associatif commun de paramètres supplémentaires
    *                           Exemple : ['restreint' => 1, 'entity' => 1]
    */
    public function displayMulti($paramsList, $extraParams = array())
    {
        if (!is_array($paramsList)) {
            return; // sécurité : on attend bien un tableau
        }

        foreach ($paramsList as $param) {
            // On appelle simplement display() pour chaque valeur
            $this->display($param, $extraParams);
        }
    }
    /**
    * Variante de displayWithRight qui ajoute toujours le paramètre principal
    * et préserve les paramètres additionnels (restreint, entity, etc.)
    * Sans modifier la méthode d'origine.
    */
    public function displayWithRightFull($param, $extraParams = array())
    {
        // On force $extraParams à être un tableau
        if (!is_array($extraParams)) {
            $extraParams = array();
        }

        // Ajouter 'mod' seulement s'il n'existe pas déjà
        if (!array_key_exists('mod', $extraParams)) {
            $extraParams['mod'] = $this->mod;
        }

        // Toujours inclure le paramètre principal (id, login, etc.)
        $extraParams[$this->paramString] = $param;

        // Construction de l'URL
        $urlChunk = $this->buildUrlChunk($extraParams);

        // Affichage du lien
        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"" . urlStr($this->path) . $urlChunk . "\">&nbsp;</a>";
        echo "</li>";
    }
}



class ActionAjaxPopupItem extends ActionItem
{
    private $message;
    private $width;

    public function __construct(
        $desc,
        $action,
        $classCss,
        $paramString,
        $message,
        $module = null,
        $submod = null,
        $tab = null,
        $width = 400,
        $mod = false
    ) {
        parent::__construct($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        $this->message = $message;
        $this->width   = $width;
    }

    /**
     * Affiche le lien texte déclenchant la popup AJAX.
     */
    public function encapsulate($obj, $extraParams = array())
    {
        if (is_array($extraParams) && !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($obj);
        }

        // Construit l’URL AJAX dynamique
        $ajaxUrl = "main.php?module=" . $this->module;
        if (!empty($this->submod)) {
            $ajaxUrl .= "&amp;submod=" . $this->submod;
        }
        if (!empty($this->tab)) {
            $ajaxUrl .= "&amp;tab=" . $this->tab;
        }
        $ajaxUrl .= "&amp;action=" . $this->action . $urlChunk;

        $popupId = "popup_" . uniqid();

        // Lien HTML cliquable
        $str  = "<a href=\"#\" class=\"" . htmlspecialchars($this->classCss) . "\" ";
        $str .= "title=\"" . htmlspecialchars($this->desc) . "\" ";
        $str .= "onclick=\"openAjaxPopup_{$popupId}(); return false;\">";
        $str .= htmlspecialchars($obj);
        $str .= "</a>";

        // Intègre le JavaScript directement (comme SimpleNavBar)
        $str .= $this->buildPopupScript($popupId, $ajaxUrl, $this->message, $this->width);

        return $str;
    }

    /**
     * Génère le JavaScript intégré pour cette instance.
     */
    private function buildPopupScript($popupId, $ajaxUrl, $message, $width)
    {
        ob_start(); ?>
        <script type="text/javascript">
            function openAjaxPopup_<?php echo $popupId; ?>() {
                // Supprime l’ancienne popup s’il y en a une
                jQuery('#<?php echo $popupId; ?>').remove();

                // Crée la popup en jQuery
                const popup = jQuery('<div>', { id: '<?php echo $popupId; ?>' })
                    .css({
                        position: 'fixed',
                        top: '50%',
                        left: '50%',
                        transform: 'translate(-50%, -50%)',
                        width: '<?php echo $width; ?>px',
                        background: '#fff',
                        border: '1px solid #999',
                        padding: '20px',
                        zIndex: 9999,
                        boxShadow: '0 0 15px rgba(0,0,0,0.3)',
                        borderRadius: '8px',
                        textAlign: 'center'
                    })
                    .html(`
                        <div style="font-weight:bold;margin-bottom:10px;"><?php echo addslashes($message); ?></div>
                        <button onclick="confirmAjaxAction_<?php echo $popupId; ?>()">Oui</button>
                        <button onclick="closeAjaxPopup_<?php echo $popupId; ?>()">Non</button>
                        <div id="<?php echo $popupId; ?>_result" style="margin-top:15px;font-size:0.9em;color:#333;"></div>
                    `);

                jQuery('body').append(popup);
            }

            function closeAjaxPopup_<?php echo $popupId; ?>() {
                jQuery('#<?php echo $popupId; ?>').remove();
            }

            function confirmAjaxAction_<?php echo $popupId; ?>() {
                const resultDiv = jQuery('#<?php echo $popupId; ?>_result');
                resultDiv.html('Exécution en cours...');

                jQuery.ajax({
                    url: '<?php echo $ajaxUrl; ?>'.replace(/&amp;/g, '&'),
                    method: 'GET',
                    headers: { 'X-Requested-With': 'XMLHttpRequest' },
                    success: function (data) {
                        resultDiv.html('<b>Résultat :</b><br>' + data);
                    },
                    error: function (xhr, status, error) {
                        resultDiv.html('Erreur : ' + error);
                    }
                });
            }
        </script>
        <?php
        return ob_get_clean();
    }
}

class ActionAjaxPopup extends ActionItem
{
    private $_confirmMessage = '';
    private $_width = 400;
    private $_replaceContent = true;

    public function __construct(
        $desc,
        $action,
        $classCss,
        $paramString,
        $confirmMessage,
        $module = null,
        $submod = null,
        $tab = null,
        $width = 400,
        $mod = false,
        $replace_content = true
    ) {
        parent::__construct($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        $this->_confirmMessage = $confirmMessage;
        $this->_width = $width;
        $this->_replaceContent = $replace_content;
    }

    public function render($text, $extraParams = array(), $title = '', $hoverClass = '')
    {
        if (is_string($extraParams) && !empty($extraParams)) {
            $urlChunk = $extraParams;
        } elseif (is_array($extraParams) && !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&" . $this->paramString . "=" . rawurlencode($text);
        }

        $decodedUrlChunk = html_entity_decode($urlChunk, ENT_QUOTES, 'UTF-8');
        $targetUrl = "main.php?module=" . $this->module .
                    "&submod=" . $this->submod .
                    "&action=" . $this->action;
        if (!empty($this->tab)) {
            $targetUrl .= "&tab=" . $this->tab;
        }
        $targetUrl .= $decodedUrlChunk;
        $targetUrlJs = htmlspecialchars($targetUrl, ENT_QUOTES, 'UTF-8');
        $confirmMessageJs = htmlspecialchars($this->_confirmMessage, ENT_QUOTES, 'UTF-8');

        if (empty($title)) {
            $title = $text;
        }
        $titleAttr = ' title="' . htmlspecialchars($title, ENT_QUOTES, 'UTF-8') . '"';
        $allClasses = trim($this->classCss . ' ' . $hoverClass);

        $html = '<a href="#" class="' . $allClasses . '"' . $titleAttr . '
                    onclick="return ActionAjaxPopup_showPopup(\'' . $confirmMessageJs . '\', \'' . $targetUrlJs . '\', ' . $this->_width . ', ' . ($this->_replaceContent ? 'true' : 'false') . ');">'
                    . htmlspecialchars($text, ENT_QUOTES, 'UTF-8') .
                '</a>';

        static $jsIncluded = false;
        if (!$jsIncluded) {
            ob_start();
            $this->printJavascript();
            $html .= ob_get_clean();
            $jsIncluded = true;
        }

        return $html;
    }

    private function printJavascript()
    {
        ?>
        <script type="text/javascript">
        function ActionAjaxPopup_showPopup(message, targetUrl, width, replaceContent) {
            // Si pas de message de confirmation, on fait un autoload dans la popup
            if (message === '') {
                if (!jQuery('#actionConfirmPopup').length) {
                    jQuery('body').append('<div id="actionConfirmPopup" class="action-popup" style="display:none; padding:10px; background:#fff; border:1px solid #666; border-radius:6px; box-shadow:0 0 10px #000; position:fixed; z-index:10000;"></div>');
                }
                var $popup = jQuery('#actionConfirmPopup');
                $popup.html('<em>Chargement...</em>').css({
                    width: width + 'px',
                    top: '20%',
                    left: '50%',
                    transform: 'translateX(-50%)'
                }).fadeIn(200);

                jQuery.ajax({
                    url: targetUrl,
                    type: 'GET',
                    success: function(data) {
                        if (replaceContent) {
                            // Remplace le contenu du div de la popup
                            $popup.html(data);
                        } else {
                            // Affiche le résultat dans la popup (comportement par défaut)
                            $popup.html(data);
                        }
                        $popup.append('<div style="text-align:center; margin-top:10px;"><button id="popupClose">Fermer</button></div>');
                        jQuery('#popupClose').on('click', function() {
                            $popup.fadeOut(200);
                        });
                    },
                    error: function(xhr) {
                        $popup.html('<span style="color:red;">Erreur AJAX : ' + xhr.status + '</span>');
                    }
                });
                return false;
            }

            // Comportement classique avec confirmation
            if (!jQuery('#actionConfirmPopup').length) {
                jQuery('body').append('<div id="actionConfirmPopup" class="action-popup" style="display:none; padding:10px; background:#fff; border:1px solid #666; border-radius:6px; box-shadow:0 0 10px #000; position:fixed; z-index:10000;"></div>');
            }
            var $popup = jQuery('#actionConfirmPopup');
            var html = '<div class="popup-message" style="margin-bottom:10px;">' + message + '</div>' +
                       '<div class="popup-buttons" style="text-align:center;">' +
                       '<button id="popupYes" style="margin-right:10px;">Oui</button>' +
                       '<button id="popupNo">Non</button>' +
                       '</div>' +
                       '<div id="popupResult" style="margin-top:10px; display:none;"></div>';
            $popup.html(html);
            $popup.css({
                width: width + 'px',
                top: '20%',
                left: '50%',
                transform: 'translateX(-50%)'
            }).fadeIn(200);

            jQuery('#popupNo').on('click', function() {
                $popup.fadeOut(200);
            });

            jQuery('#popupYes').on('click', function() {
                jQuery('#popupResult').html('<em>Chargement...</em>').show();
                jQuery.ajax({
                    url: targetUrl,
                    type: 'GET',
                    success: function(data) {
                        if (replaceContent) {
                            // Remplace le contenu du div de la popup
                            $popup.html(data);
                        } else {
                            // Affiche le résultat dans la popup (comportement par défaut)
                            jQuery('#popupResult').html(data).show();
                        }
                        if (!jQuery('#popupClose').length) {
                            $popup.append('<div style="text-align:center; margin-top:10px;"><button id="popupClose">Fermer</button></div>');
                            jQuery('#popupClose').on('click', function() {
                                $popup.fadeOut(200);
                            });
                        }
                    },
                    error: function(xhr) {
                        jQuery('#popupResult').html('<span style="color:red;">Erreur AJAX : ' + xhr.status + '</span>').show();
                    }
                });
            });

            return false;
        }
        </script>
        <?php
    }
}


/**
 * display action in a JavaScript popup
 *
 * @see ActionItem
 * @see showPopup (js)
 */
class ActionPopupItem extends ActionItem
{
    private $_displayType = 0;
    public $width;
    public function __construct($desc, $action, $classCss, $paramString, $module = null, $submod = null, $tab = null, $width = 300, $mod = false)
    {
        parent::__construct($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        $this->setWidth($width);
    }

    /**
     * Set the JavaScript popup width.
     * The default width value is 300px.
     */
    public function setWidth($width)
    {
        $this->width = $width;
    }

    public function displayType($type)
    {
        $this->_displayType = $type;
    }

    public function displayWithRight($param, $extraParams = array())
    {
        /* Add special param for actionPopupItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($param);
        }

        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "\"";
        echo " onclick=\"PopupWindow(event,'main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "', " . $this->width . "); return false;\">&nbsp;</a>";
        echo "</li>";
    }

    public function encapsulate($obj, $extraParams = array())
    {
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($obj);
        }
        $str = "<a title=\"" . $this->desc . "\" href=\"main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "\" ";
        $str .= "  onclick=\"showPopup(event,'main.php?module=" . $this->module . "&amp;submod=" . $this->submod . "&amp;action=" . $this->action . $urlChunk . "', " . $this->width . "); return false;\">";
        $str .= "$obj";
        $str .= " </a>";
        return $str;
    }

}

/**
 * display confirm box before redirecting to action link
 *
 * @see ActionItem
 * @see showPopup (js)
 */
class ActionConfirmItem extends ActionItem
{
    public $_displayType = 0;
    public $_confirmMessage = '';

    public function __construct($desc, $action, $classCss, $paramString, $module = null, $submod = null, $confirmMessage, $tab = null, $width = 300, $mod = false)
    {
        parent::__construct($desc, $action, $classCss, $paramString, $module, $submod, $tab, $mod);
        //$this->setWidth($width);
        $this->_confirmMessage = $confirmMessage;
    }

    public function displayWithRight($param, $extraParams = array())
    {
        /* Add special param for actionPopupItem */
        if (is_array($extraParams)) {
            $extraParams['mod'] = $this->mod;
        }
        if (is_array($extraParams) & !empty($extraParams)) {
            $urlChunk = $this->buildUrlChunk($extraParams);
        } else {
            $urlChunk = "&amp;" . $this->paramString . "=" . rawurlencode($param);
        }
        $confirmMessageJs = htmlspecialchars(
            json_encode($this->_confirmMessage, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT),
            ENT_QUOTES,
            'UTF-8'
        );

        $decodedUrlChunk = html_entity_decode($urlChunk, ENT_QUOTES, 'UTF-8');
        $targetUrl = "main.php?module=" . $this->module . "&submod=" . $this->submod . "&action=" . $this->action . $decodedUrlChunk;
        $targetUrlJs = htmlspecialchars(
            json_encode($targetUrl, JSON_HEX_TAG | JSON_HEX_APOS | JSON_HEX_AMP | JSON_HEX_QUOT),
            ENT_QUOTES,
            'UTF-8'
        );

        echo "<li class=\"" . $this->classCss . "\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" ";
        echo " onclick=\"displayConfirmationPopup(" . $confirmMessageJs . ", " . $targetUrlJs . "); return false;\" ";
        echo ">&nbsp;</a>";
        echo "</li>";
    }
}

class EmptyActionItem extends ActionItem
{
    public function __construct($desc = "")
    {
        $this->classCss = 'empty';
        $this->desc = $desc;
    }

    public function display($param = null, $extraParams = array())
    {
        echo "<li class=\"" . $this->classCss . " inactive\">";
        echo "<a title=\"" . $this->desc . "\" href=\"#\" ";
        echo "onclick=\"return false;\">&nbsp;</a>";
        print "</li>";
    }
    public function setClassCss($name)
    {
        $this->classCss = $name;
    }
    public function setDescription($name)
    {
        $this->desc = $name;
    }

}



class ConvertCouleur
{
    private $predefinedColors = [
        'aliceblue' => 'rgb(240, 248, 255)',
        'antiquewhite' => 'rgb(250, 235, 215)',
        'aqua' => 'rgb(0, 255, 255)',
        'aquamarine' => 'rgb(127, 255, 212)',
        'azure' => 'rgb(240, 255, 255)',
        'beige' => 'rgb(245, 245, 220)',
        'bisque' => 'rgb(255, 228, 196)',
        'black' => 'rgb(0, 0, 0)',
        'blanchedalmond' => 'rgb(255, 235, 205)',
        'blue' => 'rgb(0, 0, 255)',
        'blueviolet' => 'rgb(138, 43, 226)',
        'brown' => 'rgb(165, 42, 42)',
        'burlywood' => 'rgb(222, 184, 135)',
        'cadetblue' => 'rgb(95, 158, 160)',
        'chartreuse' => 'rgb(127, 255, 0)',
        'chocolate' => 'rgb(210, 105, 30)',
        'coral' => 'rgb(255, 127, 80)',
        'cornflowerblue' => 'rgb(100, 149, 237)',
        'cornsilk' => 'rgb(255, 248, 220)',
        'crimson' => 'rgb(220, 20, 60)',
        'cyan' => 'rgb(0, 255, 255)',
        'darkblue' => 'rgb(0, 0, 139)',
        'darkcyan' => 'rgb(0, 139, 139)',
        'darkgoldenrod' => 'rgb(184, 134, 11)',
        'darkgray' => 'rgb(169, 169, 169)',
        'darkgreen' => 'rgb(0, 100, 0)',
        'darkgrey' => 'rgb(169, 169, 169)',
        'darkkhaki' => 'rgb(189, 183, 107)',
        'darkmagenta' => 'rgb(139, 0, 139)',
        'darkolivegreen' => 'rgb(85, 107, 47)',
        'darkorange' => 'rgb(255, 140, 0)',
        'darkorchid' => 'rgb(153, 50, 204)',
        'darkred' => 'rgb(139, 0, 0)',
        'darksalmon' => 'rgb(233, 150, 122)',
        'darkseagreen' => 'rgb(143, 188, 143)',
        'darkslateblue' => 'rgb(72, 61, 139)',
        'darkslategray' => 'rgb(47, 79, 79)',
        'darkslategrey' => 'rgb(47, 79, 79)',
        'darkturquoise' => 'rgb(0, 206, 209)',
        'darkviolet' => 'rgb(148, 0, 211)',
        'deeppink' => 'rgb(255, 20, 147)',
        'deepskyblue' => 'rgb(0, 191, 255)',
        'dimgray' => 'rgb(105, 105, 105)',
        'dimgrey' => 'rgb(105, 105, 105)',
        'dodgerblue' => 'rgb(30, 144, 255)',
        'firebrick' => 'rgb(178, 34, 34)',
        'floralwhite' => 'rgb(255, 250, 240)',
        'forestgreen' => 'rgb(34, 139, 34)',
        'fuchsia' => 'rgb(255, 0, 255)',
        'gainsboro' => 'rgb(220, 220, 220)',
        'ghostwhite' => 'rgb(248, 248, 255)',
        'gold' => 'rgb(255, 215, 0)',
        'goldenrod' => 'rgb(218, 165, 32)',
        'gray' => 'rgb(128, 128, 128)',
        'green' => 'rgb(0, 128, 0)',
        'greenyellow' => 'rgb(173, 255, 47)',
        'grey' => 'rgb(128, 128, 128)',
        'honeydew' => 'rgb(240, 255, 240)',
        'hotpink' => 'rgb(255, 105, 180)',
        'indianred' => 'rgb(205, 92, 92)',
        'indigo' => 'rgb(75, 0, 130)',
        'ivory' => 'rgb(255, 255, 240)',
        'khaki' => 'rgb(240, 230, 140)',
        'lavender' => 'rgb(230, 230, 250)',
        'lavenderblush' => 'rgb(255, 240, 245)',
        'lawngreen' => 'rgb(124, 252, 0)',
        'lemonchiffon' => 'rgb(255, 250, 205)',
        'lightblue' => 'rgb(173, 216, 230)',
        'lightcoral' => 'rgb(240, 128, 128)',
        'lightcyan' => 'rgb(224, 255, 255)',
        'lightgoldenrodyellow' => 'rgb(250, 250, 210)',
        'lightgray' => 'rgb(211, 211, 211)',
        'lightgreen' => 'rgb(144, 238, 144)',
        'lightgrey' => 'rgb(211, 211, 211)',
        'lightpink' => 'rgb(255, 182, 193)',
        'lightsalmon' => 'rgb(255, 160, 122)',
        'lightseagreen' => 'rgb(32, 178, 170)',
        'lightskyblue' => 'rgb(135, 206, 250)',
        'lightslategray' => 'rgb(119, 136, 153)',
        'lightslategrey' => 'rgb(119, 136, 153)',
        'lightsteelblue' => 'rgb(176, 196, 222)',
        'lightyellow' => 'rgb(255, 255, 224)',
        'lime' => 'rgb(0, 255, 0)',
        'limegreen' => 'rgb(50, 205, 50)',
        'linen' => 'rgb(250, 240, 230)',
        'magenta' => 'rgb(255, 0, 255)',
        'maroon' => 'rgb(128, 0, 0)',
        'mediumaquamarine' => 'rgb(102, 205, 170)',
        'mediumblue' => 'rgb(0, 0, 205)',
        'mediumorchid' => 'rgb(186, 85, 211)',
        'mediumpurple' => 'rgb(147, 112, 219)',
        'mediumseagreen' => 'rgb(60, 179, 113)',
        'mediumslateblue' => 'rgb(123, 104, 238)',
        'mediumspringgreen' => 'rgb(0, 250, 154)',
        'mediumturquoise' => 'rgb(72, 209, 204)',
        'mediumvioletred' => 'rgb(199, 21, 133)',
        'midnightblue' => 'rgb(25, 25, 112)',
        'mintcream' => 'rgb(245, 255, 250)',
        'mistyrose' => 'rgb(255, 228, 225)',
        'moccasin' => 'rgb(255, 228, 181)',
        'navajowhite' => 'rgb(255, 222, 173)',
        'navy' => 'rgb(0, 0, 128)',
        'oldlace' => 'rgb(253, 245, 230)',
        'olive' => 'rgb(128, 128, 0)',
        'olivedrab' => 'rgb(107, 142, 35)',
        'orange' => 'rgb(255, 165, 0)',
        'orangered' => 'rgb(255, 69, 0)',
        'orchid' => 'rgb(218, 112, 214)',
        'palegoldenrod' => 'rgb(238, 232, 170)',
        'palegreen' => 'rgb(152, 251, 152)',
        'paleturquoise' => 'rgb(175, 238, 238)',
        'palevioletred' => 'rgb(219, 112, 147)',
        'papayawhip' => 'rgb(255, 239, 213)',
        'peachpuff' => 'rgb(255, 218, 185)',
        'peru' => 'rgb(205, 133, 63)',
        'pink' => 'rgb(255, 192, 203)',
        'plum' => 'rgb(221, 160, 221)',
        'powderblue' => 'rgb(176, 224, 230)',
        'purple' => 'rgb(128, 0, 128)',
        'rebeccapurple' => 'rgb(102, 51, 153)',
        'red' => 'rgb(255, 0, 0)',
        'rosybrown' => 'rgb(188, 143, 143)',
        'royalblue' => 'rgb(65, 105, 225)',
        'saddlebrown' => 'rgb(139, 69, 19)',
        'salmon' => 'rgb(250, 128, 114)',
        'sandybrown' => 'rgb(244, 164, 96)',
        'seagreen' => 'rgb(46, 139, 87)',
        'seashell' => 'rgb(255, 245, 238)',
        'sienna' => 'rgb(160, 82, 45)',
        'silver' => 'rgb(192, 192, 192)',
        'skyblue' => 'rgb(135, 206, 235)',
        'slateblue' => 'rgb(106, 90, 205)',
        'slategray' => 'rgb(112, 128, 144)',
        'slategrey' => 'rgb(112, 128, 144)',
        'snow' => 'rgb(255, 250, 250)',
        'springgreen' => 'rgb(0, 255, 127)',
        'steelblue' => 'rgb(70, 130, 180)',
        'tan' => 'rgb(210, 180, 140)',
        'teal' => 'rgb(0, 128, 128)',
        'thistle' => 'rgb(216, 191, 216)',
        'tomato' => 'rgb(255, 99, 71)',
        'turquoise' => 'rgb(64, 224, 208)',
        'violet' => 'rgb(238, 130, 238)',
        'wheat' => 'rgb(245, 222, 179)',
        'white' => 'rgb(255, 255, 255)',
        'whitesmoke' => 'rgb(245, 245, 245)',
        'yellow' => 'rgb(255, 255, 0)',
        'yellowgreen' => 'rgb(154, 205, 50)'
    ];

    public function convert($color)
    {
        // Vérifie si la couleur est déjà au format rgb ou rgba
        if (preg_match('/^rgb\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3})\)$/', $color, $matches)) {
            return "rgb({$matches[1]}, {$matches[2]}, {$matches[3]})";
        } elseif (preg_match('/^rgba\((\d{1,3}),\s*(\d{1,3}),\s*(\d{1,3}),\s*([\d.]+)\)$/', $color, $matches)) {
            return "rgba({$matches[1]}, {$matches[2]}, {$matches[3]}, {$matches[4]})";
        }

        // Vérifie si la couleur est au format hexadécimal
        if (strpos($color, '#') === 0) {
            $hex = ltrim($color, '#');
            $alpha = (strlen($hex) == 8) ? true : false;

            $r = hexdec(substr($hex, 0, 2));
            $g = hexdec(substr($hex, 2, 2));
            $b = hexdec(substr($hex, 4, 2));

            if ($alpha) {
                $a = round(hexdec(substr($hex, 6, 2)) / 255, 2);
                return "rgba($r, $g, $b, $a)";
            } else {
                return "rgb($r, $g, $b)";
            }
        }

        // Si c'est un nom de couleur, indiquer qu'il faut convertir
        if (array_key_exists(strtolower($color), $this->predefinedColors)) {
            return "La couleur '$color' doit être convertie en rgb.";
        }

        return "Format non reconnu.";
    }
}


/**
 *  class who maintain array presentation of information
 */
class ListInfos extends HtmlElement
{
    public $arrInfo; /*     * < main list */
    // public $extraInfo;
    public $paramInfo;
    public $name;
    public $arrAction; /*     * < list of possible action */
    public $end;
    public $start;
    public $description; /*     * < list of description (not an obligation) */
    public $col_width; /*     * < Contains the columns width */
    public $tooltip; /*     * < Contains the tooltip for column label */
    public $captionText = ""; // Texte de la légende
    public $captionBorder = 0; // Bordure de la légende (0 par défaut)
    public $captionBold = 1; // Texte en gras (1 par défaut)
    public $captionBgColor = "grey"; // Couleur de fond (gris par défaut)
    public $captionTextColor = "black"; // Couleur du texte (noir par défaut)
    public $captionPadding = "10px 0"; // Padding vertical (par défaut)
    public $captionSize = ""; // Taille de la légende (optionnel)
    public $captionEmboss = 0; // Effet de relief sortant (0 par défaut)
    public $rowColor = ""; // Couleur des lignes des cellules (optionnel)
    public $captionStyle = "";
    public $captionClass = "";
    // public $extraInfoRaw = array();
    public $extraColumns = array();

    /**
     * constructor
     * @param $tab must be an array of array
     */
    public function __construct($tab, $description = "", $extranavbar = "", $width = "", $tooltip = "")
    {
        $this->arrInfo = $tab;
        $this->arrAction = array();
        $this->description[] = $description;
        $this->extranavbar = $extranavbar;
        $this->initVar();
        $this->col_width = array();
        $this->col_width[] = $width;
        $this->tooltip = array();
        $this->tooltip[] = $tooltip;
        $this->firstColumnActionLink = true;
        $this->dissociateColumnsActionLink = [];
        $this->_addInfo = array();
    }


    // 1. Définir le style CSS complet
    public function setCaptionText($texte)
    {
        $this->captionText = $texte;
    }

    // 1. Définir le style CSS complet
    public function setCssCaptionStyle($style)
    {
        $this->captionStyle = $style;
    }

    // 2. Définir le style via paramètres
    public function setCssCaption(
        $border = 0,
        $bold = 1,
        $bgColor = "grey",
        $textColor = "black",
        $padding = "5px 0",
        $size = "",
        $emboss = 0,
        $rowColor = ""
    )
    {
        $this->captionBorder = (bool)$border;
        $this->captionBold = (bool)$bold;
        $this->captionBgColor = $bgColor;
        $this->captionTextColor = $textColor;
        $this->captionPadding = $padding;
        $this->captionSize = !empty($size) ? (int)$size . "px" : "";
        $this->captionEmboss = $emboss;
        $this->rowColor = $rowColor;
    }


    // 3. Définir une classe CSS
    public function setCssCaptionClass($class)
    {
        $this->captionClass = $class;
    }


    // Dessiner le caption
    public function drawCaption()
    {
        if (empty($this->captionText)) {
            return; // rien à afficher
        }

        $style = "";

        // Priorité 1 : style complet direct
        if (!empty($this->captionStyle)) {
            $style = $this->captionStyle;
        }
        // Sinon style construit à partir des paramètres
        elseif (!empty($this->captionText)) {
            $style .= "background-color: " . htmlspecialchars($this->captionBgColor, ENT_QUOTES, 'UTF-8') . "; ";

            $style .= "color: " . htmlspecialchars($this->captionTextColor, ENT_QUOTES, 'UTF-8') . "; ";

            $style .= "padding: " . htmlspecialchars($this->captionPadding, ENT_QUOTES, 'UTF-8') . "; ";

            if ($this->captionBorder) {
                $style .= "border: 1px solid " . htmlspecialchars($this->rowColor ?: $this->captionTextColor, ENT_QUOTES, 'UTF-8') . "; ";
            }
            if ($this->captionBold) {
                $style .= "font-weight: bold; ";
            }
            if (!empty($this->captionSize)) {
                $style .= "font-size: " . htmlspecialchars($this->captionSize, ENT_QUOTES, 'UTF-8') . "; ";
            }
            if ($this->captionEmboss) {
                $style .= "box-shadow: 2px 2px 5px " . htmlspecialchars($this->rowColor ?: "#000", ENT_QUOTES, 'UTF-8') . "; ";
            }
        }
        // echo $style;
        // Si une classe est définie, on l'ajoute
        $classAttr = !empty($this->captionClass) ? ' class="' . htmlspecialchars($this->captionClass, ENT_QUOTES, 'UTF-8') . '"' : '';

       echo "<caption$classAttr style=\"$style\">" . htmlspecialchars($this->captionText, ENT_QUOTES, 'UTF-8') . "</caption>";
    }

    public function setAdditionalInfo($addinfo)
    {
        $this->_addInfo = $addinfo;
    }

    /**
     * Set the number of rows to display per ListInfos page.
     * It overrides the default value defined by $conf["global"]["maxperpage"].
     *
     * @param $value The number of rows
     */
    public function setRowsPerPage($value)
    {
        $this->end = $value;
    }

    /**
     *  add an ActionItem
     *  @param $objActionItem object ActionItem
     */
    public function addActionItem($objActionItem)
    {
        $this->arrAction[] = &$objActionItem;
    }

    /**
     * Add an array of ActionItem
     * Useful if all action items are not the same for each row of the list
     *
     */
    public function addActionItemArray($objActionItemArray)
    {
        if(is_array($objActionItemArray)) {
            $this->arrAction[] = &$objActionItemArray;
        }
    }

    public function addExtraInfo($arrString, $description = "", $width = "", $tooltip = "")
    {
        if (is_array($arrString)) {
            $this->extraColumns[] = [
                "data" => $arrString,
                "isRaw" => false,
                "description" => $description,
                "width" => $width,
                "tooltip" => $tooltip
            ];
        }
    }
    public function addExtraInfoRaw($arrString, $description = "", $width = "", $tooltip = "")
    {
        if (is_array($arrString)) {
            $this->extraColumns[] = [
                "data" => $arrString,
                "isRaw" => true,
                "description" => $description,
                "width" => $width,
                "tooltip" => $tooltip
            ];
        }
    }
    public function addExtraInfodirecthtml($arrString, $description = "", $directhtml = false, $width = "",
    $tooltip = "")
    {
        if (is_array($arrString)) {
            $this->extraColumns[] = [
                "data" => $arrString,
                "isRaw" => $directhtml,
                "description" => $description,
                "width" => $width,
                "tooltip" => $tooltip
            ];
        }
    }

    /**
     *  set parameters array for main action
     *  @param $arrString an Array of string to be used as parameters for the main action
     */
    public function setParamInfo($arrString)
    {
        if(is_array($arrString)) {
            $this->paramInfo = $arrString;
        }
    }

    /**
     * Set the left padding of the table header.
     * It will be set to 32 by default
     * @param $padding an integer
     */
    public function setTableHeaderPadding($padding)
    {
        $this->first_elt_padding = $padding;
    }

    /**
     * Disable the link to the first available action in the table
     * This link is always done by default
     */
    public function disableFirstColumnActionLink()
    {
        $this->firstColumnActionLink = false;
    }

    public function dissociateColumnActionLink($ids)
    {
        foreach($ids as $id) {
            if(!in_array($id, $this->dissociateColumnsActionLink)) {
                $this->dissociateColumnsActionLink[] = intval($id);
            }
        }
    }
    /**
     *  init class' vars
     */
    public function initVar()
    {

        $this->name = "Elements";

        global $conf;

        $this->maxperpage = (isset($_REQUEST['maxperpage'])) ? $_REQUEST['maxperpage'] : $conf['global']['maxperpage'];

        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
                $this->start = 0;

                if (safeCount($this->arrInfo) > 0) {
                    $this->end = $this->maxperpage - 1;
                } else {
                    $this->end = 0;
                }
            }
        } else {
            $this->start = $_GET["start"];
            $this->end = $_GET["end"];
        }
        /* Set a basic navigation bar */
        $this->setNavBar(new SimpleNavBar($this->start, $this->end, safeCount($this->arrInfo), $this->extranavbar));
    }

    /**
     *  set the name of the array (for CSS)
     */
    public function setName($name)
    {
        $this->name = $name;
    }

    /**
     *  set the cssclass of a row
     */
    public function setCssClass($name)
    {
        $this->cssClass = $name;
    }


    /**
     * set cssids for each row
     */
    public function setCssIds($a_names)
    {
        $this->cssIds = $a_names;
    }

    /**
     * set a cssclass for each row
     */
    public function setCssClasses($a_names)
    {
        $this->cssClasses = $a_names;
    }

    /**
     * set cssclass for each MainAction column
     */
    public function setMainActionClasses($classes)
    {
        $this->mainActionClasses = $classes;
    }

    /**
     * Set the ListInfos navigation bar
     */
    public function setNavBar($navbar)
    {
        $this->navbar = $navbar;
    }

    /**
     *
     * Display the widget navigation bar if $navbar is True
     *
     * @param $navbar: if $navbar is true the navigation bar is displayed
     */
    public function displayNavbar($navbar)
    {
        if ($navbar) {
            $this->navbar->display();
        }
    }

    /**
     *  draw number of page etc...
     */
    public function drawHeader($navbar = 1)
    {

        $this->displayNavbar($navbar);
        echo "<p class=\"listInfos\">";

        /*
         * Management of the numbers "start" and "end" to display depending on the maxperpage set in the selector
         * These numbers are more user-friendly and do not begin with 0
         */
        echo $this->name . " <strong>" . min($this->start + 1, safeCount($this->arrInfo)) . "</strong>\n ";
        echo _("to") . " <strong>" . min($this->end + 1, safeCount($this->arrInfo)) . "</strong>\n";

        printf(_(" - Total <b>%s </b>") . "\n", safeCount($this->arrInfo));
        /* Display page counter only when useful */
        if (safeCount($this->arrInfo) > $this->maxperpage) {
            echo "(" . _("page") . " ";
            printf("%.0f", ($this->end + 1) / $this->maxperpage);
            echo " / ";
            $pages = intval((safeCount($this->arrInfo) / $this->maxperpage));
            if ((safeCount($this->arrInfo) % $this->maxperpage > 0) && (safeCount($this->arrInfo) > $this->maxperpage)) {
                $pages++;
            } elseif ((safeCount($this->arrInfo) > 0) && ($pages < 1)) {
                $pages = 1;
            } elseif ($pages < 0) {
                $pages = 0;
            }
            printf("%.0f", $pages);
            echo ")\n";
        }
        echo "</p>";
    }

    /**
     * display main action (first action
     */
    public function drawMainAction($idx)
    {
        if (!empty($this->cssClass)) {
            echo "<td class=\"" . $this->cssClass . "\">";
        } elseif (!empty($this->mainActionClasses)) {
            echo "<td class=\"" . $this->mainActionClasses[$idx] . "\">";
        } else {
            echo "<td>";
        }
        if (is_a($this->arrAction[0], 'ActionItem')) {
            $firstAction = $this->arrAction[0];
        } elseif (is_array($this->arrAction[0])) {
            $firstAction = $this->arrAction[0][$idx];
        }
        echo $firstAction->encapsulate($this->arrInfo[$idx], $this->paramInfo[$idx]);
        if (isset($this->_addInfo[$idx])) {
            print " " . $this->_addInfo[$idx];
        }
        echo "</td>";
    }






    public function drawTable($navbar = 1)
{
    echo "<table border=\"1\" cellspacing=\"0\" cellpadding=\"5\" class=\"listinfos\">\n";
    $this->drawCaption();

    // En-têtes du tableau
    echo "<thead><tr>";
    $first = false;

    // Colonnes principales (description)
    foreach ($this->description as $key => $desc) {
        $width_styl = isset($this->col_width[$key]) ? 'width: ' . $this->col_width[$key] . ';' : '';
        if (!$first) {
            if (!isset($this->first_elt_padding)) {
                $this->first_elt_padding = 32;
            }
            echo "<td style=\"$width_styl\"><span style=\"padding-left: " . $this->first_elt_padding . "px;\">$desc</span></td>";
            $first = true;
        } else {
            $tooltipbegin = !empty($this->tooltip[$key]) ? "<a href=\"#\" class=\"tooltip\">" : "";
            $tooltipend = !empty($this->tooltip[$key]) ? "<span>" . $this->tooltip[$key] . "</span></a>" : "";
            echo "<td style=\"$width_styl\"><span>$tooltipbegin$desc$tooltipend</span></td>";
        }
    }

    // Colonnes extra (normales et brutes)
    foreach ($this->extraColumns as $extraCol) {
        $width_styl = !empty($extraCol["width"]) ? 'width: ' . $extraCol["width"] . ';' : '';
        $tooltipbegin = !empty($extraCol["tooltip"]) ? "<a href=\"#\" class=\"tooltip\">" : "";
        $tooltipend = !empty($extraCol["tooltip"]) ? "<span>" . $extraCol["tooltip"] . "</span></a>" : "";
        echo "<td style=\"$width_styl\"><span>$tooltipbegin" . $extraCol["description"] . "$tooltipend</span></td>";
    }

    // Colonne "Actions" si nécessaire
    if (safeCount($this->arrAction) != 0) {
        $width_styl = !empty(end($this->col_width)) ? 'width: ' . end($this->col_width) . ';' : '';
        echo "<td style=\"text-align: center; $width_styl\"><span>Actions</span></td>";
    }

    echo "</tr></thead>";

    // Lignes du tableau
    for ($idx = $this->start; ($idx < safeCount($this->arrInfo)) && ($idx <= $this->end); $idx++) {
        // Début de la ligne
        echo "<tr";
        if (!empty($this->cssIds[$idx])) {
            echo " id='" . $this->cssIds[$idx] . "'";
        }
        if (!empty($this->cssClasses[$idx])) {
            echo " class=\"" . $this->cssClasses[$idx] . "\"";
        } else {
            echo " class=\"alternate" . (!empty($this->cssClasses[$idx]) ? " " . $this->cssClasses[$idx] : "") . "\"";
        }
        echo ">";

        // Première colonne (lien vers la première action si disponible)
        if (safeCount($this->arrAction) && $this->firstColumnActionLink && !in_array($idx, $this->dissociateColumnsActionLink)) {
            $this->drawMainAction($idx);
        } else {
            echo "<td>";
            echo $this->arrInfo[$idx];
            echo "</td>";
        }

        // Colonnes extra (normales et brutes)
        foreach ($this->extraColumns as $extraCol) {
            echo "<td>";
            if (isset($extraCol["data"][$idx])) {
                if ($extraCol["isRaw"]) {
                    echo $extraCol["data"][$idx]; // Affichage brut
                } else {
                    if (is_subclass_of($extraCol["data"][$idx], "HtmlContainer")) {
                        $extraCol["data"][$idx]->display();
                    } elseif (trim($extraCol["data"][$idx]) != "") {
                        echo_obj($extraCol["data"][$idx]);
                    } else {
                        echo "&nbsp;";
                    }
                }
            } else {
                echo "&nbsp;";
            }
            echo "</td>";
        }

        // Colonne "Actions" si nécessaire
        if (safeCount($this->arrAction) != 0) {
            echo "<td class=\"action\">";
            echo "<ul class=\"action\">";
            foreach ($this->arrAction as $objActionItem) {
                if (is_a($objActionItem, 'ActionItem')) {
                    $objActionItem->display($this->arrInfo[$idx], $this->paramInfo[$idx]);
                } elseif (is_array($objActionItem)) {
                    $obj = $objActionItem[$idx];
                    $obj->display($this->arrInfo[$idx], $this->paramInfo[$idx]);
                }
            }
            echo "</ul>";
            echo "</td>";
        }

        echo "</tr>\n";
    }

    echo "</table>\n";
    $this->displayNavbar($navbar);
}
















    public function display($navbar = 1, $header = 1)
    {
        if (!isset($this->paramInfo)) {
            $this->paramInfo = $this->arrInfo;
        }
        if ($header == 1) {
            $this->drawHeader($navbar);
        }
        $this->drawTable($navbar);
    }
}


/**
 * A modified version of Listinfos
 */
class OptimizedListInfos extends ListInfos
{
    public $itemCount;
    public $startreal;
    public $endreal;
    /**
     * Allow to set another item count
     */
    public function setItemCount($count)
    {
        $this->itemCount = $count;
    }

    public function getItemCount()
    {
        return $this->itemCount;
    }

    /**
     *  init class' vars
     */
    public function initVar()
    {
        $this->name = "Elements";
        global $conf;
        if (!isset($_GET["start"])) {
            if (!isset($_POST["start"])) {
                $this->start = 0;
                if (safeCount($this->arrInfo) > 0) {
                    $this->end = (isset($_REQUEST['maxperpage'])) ? ($_REQUEST['maxperpage'] - 1) : ($conf["global"]["maxperpage"] - 1);
                } else {
                    $this->end = 0;
                }
            }
        } else {
            $this->start = $_GET["start"];
            $this->end = $_GET["end"];
        }
        $this->maxperpage = (isset($_REQUEST['maxperpage'])) ? $_REQUEST['maxperpage'] : $conf["global"]["maxperpage"];
        $this->setItemCount(safeCount($this->arrInfo));
        $this->startreal = $this->start;
        $this->endreal = $this->end;
    }

    /**
     *  draw number of page etc...
     */
    public function drawHeader($navbar = 1)
    {
        $count = $this->getItemCount();
        $this->displayNavbar($navbar);
        echo "<p class=\"listInfos\">";

        /*
         * Management of the numbers "start" and "end" to display depending on the maxperpage set in the selector
         * These numbers are more user-friendly and do not begin with 0
         */
        echo $this->name . " <strong>" . min($this->startreal + 1, $count) . "</strong>\n ";
        echo _("to") . " <strong>" . min($this->endreal + 1, $count) . "</strong>\n";

        printf(_(" - Total <b>%s </b>") . "\n", $count);
        /* Display page counter only when useful */
        if ($count > $this->maxperpage) {
            echo "(" . _("page") . " ";
            printf("%.0f", ($this->endreal + 1) / $this->maxperpage);
            echo " / ";
            $pages = intval(($count / $this->maxperpage));
            if (($count % $this->maxperpage > 0) && ($count > $this->maxperpage)) {
                $pages++;
            } elseif (($count > 0) && ($pages < 1)) {
                $pages = 1;
            } elseif ($pages < 0) {
                $pages = 0;
            }
            printf("%.0f", $pages);
            echo ")\n";
        }
        echo "</p>";
    }

}

/**
 * specific class for UserDisplay
 */
class UserInfos extends OptimizedListInfos
{
    public $css = array(); //css for first column

    public function drawMainAction($idx)
    {
        echo "<td class=\"" . $this->css[$idx] . "\">";
        echo $this->arrAction[0]->encapsulate($this->arrInfo[$idx], $this->paramInfo[$idx]);
        echo "</td>";
    }

}

/**
 *
 *  Display a previous/next navigation bar for ListInfos widget
 *
 */
class SimpleNavBar extends HtmlElement
{
    /**
     * @param $curstart: the first item index to display
     * @param $curent: the last item index
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $max: max quantity of elements in a page
     * @param $paginator: boolean which enable the selector of the number of results in a page
     */
    public $max;
    public $curstart;
    public $itemcount;
    public $extra;
    public $paginator;
    public $curpage;
    public $curend;
    public $nbpages;
    public $filter;
    public $jsfunc;

    public function __construct($curstart, $curend, $itemcount, $extra = "", $max = "", $paginator = false)
    {
        global $conf;
        if (isset($max) && $max != "") {
            $this->max = $max;
        } else {
            $this->max = $conf["global"]["maxperpage"];
        }
        $this->curstart = $curstart;
        $this->curend = $curend;
        $this->itemcount = $itemcount;
        $this->extra = $extra;
        $this->paginator = $paginator;
        # number of pages
        $this->nbpages = ceil($this->itemcount / $this->max);
        # number of current page
        $this->curpage = floor(($this->curend + 1) / $this->max);
    }

    public function display($arrParam = array())
    {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        if ($this->curstart != 0 || ($this->curstart - $this->max > 0)) {
            $start = $this->curstart - $this->max;
            $end = $this->curstart - 1;
            echo "<li class=\"previousList\"><a href=\"" . $_SERVER["SCRIPT_NAME"];
            /* FIXME: maybe we can get rid of $_GET["filter"] ? */
            printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s%s", $_GET["module"], $_GET["submod"], $_GET["action"], $start, $end, $_GET["filter"], $this->extra);
            echo "\">" . _("Previous") . "</a></li>\n";
        }

        if ($this->paginator) {
            // Display the maxperpage selector
            $this->displaySelectMax();
        }

        if (($this->curend + 1) < $this->itemcount) {
            $start = $this->curend + 1;
            $end = $this->curend + $this->max;
            $filter = isset($_GET["filter"]) ? $_GET["filter"] : "";
            echo "<li class=\"nextList\"><a href=\"" . $_SERVER["SCRIPT_NAME"];
            printf("?module=%s&amp;submod=%s&amp;action=%s&amp;start=%d&amp;end=%d&amp;filter=%s%s", $_GET["module"], $_GET["submod"], $_GET["action"], $start, $end, $filter, $this->extra);
            echo "\">" . _("Next") . "</a></li>\n";
        }

        if ($this->paginator) {
            // Display a border at the left of the "Next" link
            $this->displayNextListBorder();
        }

        echo "</ul></form>\n";
    }

    /*
     * This function displays a selector to choose the maxperpage value
     * dynamically.
     * This is useful with AjaxNavBar
     * @param $jsfunc: optional javascript function which updates ListInfos
     */

    public function displaySelectMax($jsfunc = null)
    {
        global $conf;
        echo '<span class="pagination">' . _('Pagination') . ': ';
        if (isset($jsfunc)) {
            $start = $this->curstart;

            echo "<select id=\"maxperpage\" name=\"maxperpage\" onChange=\"updateMaxPerPage(this); return false;\">";
        } else {
            echo "<select id=\"maxperpage\" name=\"maxperpage\">";
        }
        /* Display the selector and each option of the array set in the config
          file */
        foreach ($conf["global"]["pagination"] as $quantity) {
            $selected = '';
            if ($_REQUEST['maxperpage'] == $quantity) {
                /* Set by default if already selected before */
                $selected = ' selected="selected"';
            }
            echo "<option value=\"$quantity\"$selected>$quantity</option>";
        }
        echo "</select></span>";

        /*
         * Print the script which will launch an update of the ListInfos when
         * selectMax value changes.
         * It also synchronizes the value of the two selectors of the widget.
         * Then it calls the javascript function which do an AJAX update of
         * the ListInfos.
         */
        ?>
        <script type="text/javascript">
            updateMaxPerPage = function(elem) {
                // Get the selector element (the first of the page)
                var maxperpageElement = document.getElementById('maxperpage');
                if (jQuery('#maxperpage').length)
                {
                    jQuery('#maxperpage').val(jQuery(elem).val());
                    var maxperpageValue = jQuery('#maxperpage').val();
                    // Evaluate the end depending on the maxperpage value selected
                    var end = parseInt(maxperpageValue) + parseInt(<?php echo $start ?>) - 1;
                    // Call the function to update the ListInfos
        <?php echo $jsfunc ?>('<?php echo $this->filter ?>', '<?php echo $start ?>', end);
                }

                return false;
            }
        </script>
        <?php
    }

    /**
     * This function just print a script which add a border at the left of the "Next" link
     */
    public function displayNextListBorder()
    {
        ?>
        <script type="text/javascript">
            jQuery('.nextListInactive').css('borderLeft', 'solid 1px #CCC');
            jQuery('.nextList').css('borderLeft', 'solid 1px #CCC');
        </script>
        <?php
    }

    public function displayGotoPageField()
    {
        echo '
        <script type="text/javascript">
            gotoPage = function(input) {
                page = input.value;
                if (page <= ' . $this->nbpages . ') {
                    end = (' . $this->max . ' * page);
                    start = end - ' . $this->max . ';
                    end -= 1;
                    cur =  (' . $this->curend . ' + 1) / 10;
                    ' . $this->jsfunc . '("' . $this->filter . '", start, end, document.getElementById("maxperpage"));
                }
            }
        </script>';
        echo '<span class="pagination">' . _("Go to page") . ': <input type="text" size="2" onchange="gotoPage(this)" /></span>';
    }

    public function displayPagesNumbers()
    {
        # pages links
        # show all pages
        if ($this->nbpages <= 10) {
            if ($this->nbpages > 1) {
                echo '<span class="pagination">';
                for ($i = 1; $i <= $this->nbpages; $i++) {
                    echo $this->makePageLink($i);
                }
                echo '</span>';
            }
        }
        # show start/end pages and current page
        else {
            echo '<span class="pagination">';
            for ($i = 1; $i <= 3; $i++) {
                echo $this->makePageLink($i);
            }
            if ($this->curpage > 2 and $this->curpage < 5) {
                for ($i = $this->curpage; $i <= $this->curpage + 2; $i++) {
                    if ($i > 3) {
                        echo $this->makePageLink($i);
                    }
                }
            } elseif ($this->curpage > 4 and $this->curpage < $this->nbpages - 3) {
                echo '.. ';
                for ($i = $this->curpage - 1; $i <= $this->curpage + 1; $i++) {
                    echo $this->makePageLink($i);
                }
            }
            echo '.. ';
            if ($this->curpage <= $this->nbpages - 2 and $this->curpage >= $this->nbpages - 3) {
                for ($i = $this->nbpages - 4; $i <= $this->nbpages - 3; $i++) {
                    echo $this->makePageLink($i);
                }
            }
            for ($i = $this->nbpages - 2; $i <= $this->nbpages; $i++) {
                echo $this->makePageLink($i);
            }
            echo '</span>';
        }
    }

    public function makePageLink($page)
    {
        $end = ($this->max * $page);
        $start = $end - $this->max;
        $end -= 1;
        if ($page == $this->curpage) {
            return '<span>' . $page . '</span> ';
        } else {
            return '<a href="#" onclick="' . $this->jsfunc . '(\'' . $this->filter . '\',\'' . $start . '\',\'' . $end . '\', document.getElementById(\'maxperpage\')); return false;">' . $page . '</a> ';
        }
    }

}

/**
 * Class which creates a SimpleNavBar with the paginator always enabled by
 * default
 */
class SimplePaginator extends SimpleNavBar
{
    /**
     * Just call the constructor of SimpleNavBar with "true" value for the
     * $paginator attribute
     *
     * @param $curstart: the first item index to display
     * @param $curent: the last item index
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $max: max quantity of elements in a page
     */
    public function __construct($curstart, $curend, $itemcount, $extra = "", $max = "")
    {
        parent::__construct($curstart, $curend, $itemcount, $extra, $max, true);
    }

}

/**
 *  Display a previous/next navigation bar for ListInfos widget
 *  The AjaxNavBar is useful when an Ajax Filter is set for a ListInfos widget
 */
class AjaxNavBar extends SimpleNavBar
{
    /**
     *
     * The AjaxNavBar start/end item are get from $_GET["start"] and
     * $_GET["end"]
     *
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $extra: extra URL parameter to pass the next/list button
     * @param $jsfunc: the name of the javascript function that applies the AJAX filter for the ListInfos widget
     * @param $max: the max number of elements to display in a page
     */
    public function __construct($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "", $paginator = false)
    {
        global $conf;

        if (isset($_GET["start"])) {
            $curstart = $_GET["start"];
            $curend = $_GET["end"];
        } else {
            $curstart = 0;
            if ($itemcount > 0) {
                if ($max != "") {
                    $curend = $max - 1;
                } else {
                    $curend = $conf["global"]["maxperpage"] - 1;
                }
            } else {
                $curend = 0;
            }
        }
        parent::__construct($curstart, $curend, $itemcount, null, $max, $paginator);
        $this->filter = $filter;
        $this->jsfunc = $jsfunc;
        if (isset($_GET['divID'])) {
            $this->jsfunc = $this->jsfunc . $_GET['divID'];
        }
    }

    public function display($arrParam = array())
    {
        echo '<form method="post">';
        echo "<ul class=\"navList\">\n";

        if ($this->paginator) {
            // Display the maxperpage selector
            $this->displaySelectMax($this->jsfunc);
        }

        // show goto page field
        if ($this->nbpages > 20) {
            $this->displayGotoPageField();
        }

        # previous link
        if ($this->curstart != 0 || ($this->curstart - $this->max > 0)) {
            $start = $this->curstart - $this->max;
            $end = $this->curstart - 1;
            echo "<li class=\"previousList\"><a href=\"#\" onClick=\"" . $this->jsfunc . "('" . $this->filter . "','$start','$end', document.getElementById('maxperpage')); return false;\">" . _("Previous") . "</a></li>\n";
        }

        // display pages numbers
        $this->displayPagesNumbers();

        # next link
        if (($this->curend + 1) < $this->itemcount) {
            $start = $this->curend + 1;
            $end = $this->curend + $this->max;
            echo "<li class=\"nextList\"><a href=\"#\" onClick=\"" . $this->jsfunc . "('" . $this->filter . "','$start','$end', document.getElementById('maxperpage')); return false;\">" . _("Next") . "</a></li>\n";
        }

        // Display a border at the left of the "Next" link
        if ($this->nbpages > 1) {
            $this->displayNextListBorder();
        }

        echo "</ul>\n";
    }

}

/**
 * Class which creates an AjaxNavBar with the paginator always enabled by
 * default
 */
class AjaxPaginator extends AjaxNavBar
{
    /**
     * Just call the constructor of AjaxNavBar with "true" value for the $paginator attribute
     *
     * @param $itemcount: total number of item
     * @param $filter: the current list filter
     * @param $jsfunc: the name of the javascript function that applies the AJAX filter for the ListInfos widget
     * @param $max: the max number of elements to display in a page
     */
    public function __construct($itemcount, $filter, $jsfunc = "updateSearchParam", $max = "")
    {
        parent::__construct($itemcount, $filter, $jsfunc, $max, true);
        parent::__construct($itemcount, $filter, $jsfunc, $max, true);
    }

}


/**
 * @class AjaxFilter
 * @brief Génère un formulaire AJAX permettant de filtrer dynamiquement le contenu d'une div.
 *
 * Cette classe :
 * - génère un champ de recherche + boutons
 * - construit dynamiquement une URL d'appel AJAX
 * - stocke le filtre et paramètres en session (pagination, maxperpage…)
 * - recharge automatiquement la div ciblée lors de la saisie
 * - gère un refresh automatique optionnel
 *
 * Usage :
 * @code
 * $filter = new AjaxFilter("ajax.php?module=test", "resultDiv");
 * $filter->display();
 * $filter->displayDivToUpdate();
 * @endcode
 */
class AjaxFilter extends HtmlElement
{
    /**
     * @brief Constructeur du filtre AJAX.
     *
     * @param string $url      URL cible pour les appels AJAX
     * @param string $divid    ID de la div à mettre à jour
     * @param array|string $params Paramètres additionnels à ajouter à l’URL
     * @param string $formid   Identifiant unique du formulaire
     */
    public function __construct($url, $divid = "container", $params = array(), $formid = "")
    {
        // --- Normalisation de l'URL ("?" ou "&") ---
        if (strpos($url, "?") === false) {
            $this->url = $url . "?";
        } else {
            $this->url = rtrim($url, '&') . "&";
        }

        $this->divid   = $divid;
        $this->formid  = $formid;
        $this->refresh = 0;

        // --- Convertit les paramètres en chaîne propre ---
        if (is_array($params)) {
            $this->params = http_build_query($params);
        } elseif (is_string($params)) {
            $this->params = ltrim($params, '&');
        } else {
            $this->params = '';
        }

        // --- Ajoute les paramètres à l’URL ---
        if (!empty($this->params)) {
            if (!in_array(substr($this->url, -1), ['?', '&'])) {
                $this->url .= '&';
            }
            $this->url .= $this->params;
        }

        // --- Stockage en session selon contexte ---
        $module = $_GET["module"] ?? "default";
        $submod = $_GET["submod"] ?? "default";
        $action = $_GET["action"] ?? "default";
        $tab    = $_GET["tab"] ?? "default";

        $extra = "";
        foreach ($_GET as $key => $value) {
            if (!in_array($key, ['module','submod','tab','action','filter','start','end','maxperpage'])) {
                if (is_array($value)) {
                    $value = implode(",", $value);
                }
                $extra .= $key . "_" . $value;
            }
        }

        $session_prefix = "{$module}_{$submod}_{$action}_{$tab}_{$extra}_";

        // --- Rechargement des valeurs depuis la session ---
        $this->storedfilter = $_SESSION[$session_prefix . "filter"] ?? null;
        $this->storedmax    = $_SESSION[$session_prefix . "maxperpage"] ?? null;
        $this->storedstart  = $_SESSION[$session_prefix . "start"] ?? null;
        $this->storedend    = $_SESSION[$session_prefix . "end"] ?? null;
    }

    /**
     * @brief Active ou désactive le refresh automatique périodique.
     *
     * @param int $refresh Délai en ms. 0 = désactivé.
     */
    public function setRefresh($refresh)
    {
        $this->refresh = $refresh;
    }

    /**
     * @brief Génère le formulaire AJAX + JavaScript associé.
     *
     * @param array $arrParam Paramètres non utilisés mais conservés pour compatibilité.
     */
    public function display($arrParam = array())
    {
        global $conf;
        $maxperpage = $conf["global"]["maxperpage"];
?>

<!-- FORMULAIRE DE RECHERCHE AJAX -->
<form name="Form<?php echo $this->formid ?>"
      id="Form<?php echo $this->formid ?>"
      onsubmit="return false;"
      style="margin:20px 0;">

    <div id="searchSpan<?php echo $this->formid ?>" class="searchbox">

        <div id="searchBest">
            <input type="text"
                   class="searchfieldreal"
                   name="param"
                   id="param<?php echo $this->formid ?>" />

            <!-- Bouton pour effacer le champ -->
            <button type="button"
                    class="search-clear"
                    onclick="document.getElementById('param<?php echo $this->formid ?>').value=''; pushSearch<?php echo $this->formid ?>();">
            </button>

            <!-- Bouton rechercher -->
            <button onclick="pushSearch<?php echo $this->formid ?>(); return false;">
                <?php echo _T("Search", "glpi"); ?>
            </button>
        </div>

        <span class="loader"></span>

    </div>

<script type="text/javascript">

/* --------------------------------------------------------------------------
 * INITIALISATION DU FORMULAIRE
 * -------------------------------------------------------------------------- */

// Recharge le filtre mémorisé
<?php if (isset($this->storedfilter)) { ?>
document.Form<?php echo $this->formid ?>.param.value = "<?php echo $this->storedfilter ?>";
<?php } ?>

var refreshtimer<?php echo $this->formid ?>      = null;
var refreshparamtimer<?php echo $this->formid ?> = null;
var refreshdelay<?php echo $this->formid ?>      = <?php echo $this->refresh ?>;
var maxperpage                                   = <?php echo $this->storedmax ?? $maxperpage ?>;

/**
 * @brief Réinitialise les timers de refresh.
 */
clearTimers<?php echo $this->formid ?> = function() {
    if (refreshtimer<?php echo $this->formid ?> !== null)
        clearTimeout(refreshtimer<?php echo $this->formid ?>);

    if (refreshparamtimer<?php echo $this->formid ?> !== null)
        clearTimeout(refreshparamtimer<?php echo $this->formid ?>);
};

/**
 * @brief Appel AJAX principal pour mise à jour du tableau.
 */
updateSearch<?php echo $this->formid ?> = function() {

    clearTimers<?php echo $this->formid ?>();

    var searchValue = document.Form<?php echo $this->formid ?>.param.value;

    // Construction de l’URL AJAX
    var finalUrl =
        '<?php echo rtrim($this->url, "&"); ?>'
        + '&filter='     + encodeURIComponent(searchValue)
        + '&maxperpage=' + maxperpage
        <?php if ($this->storedstart !== null && $this->storedend !== null) { ?>
        + '&start=<?php echo $this->storedstart ?>'
        + '&end=<?php echo $this->storedend ?>'
        <?php } ?>
    ;

    // Lancement AJAX
    jQuery.ajax({
        url: finalUrl,
        type: 'get',
        success: function(data) {
            jQuery("#<?php echo $this->divid ?>").html(data);
        }
    });

    // Refresh automatique éventuel
    <?php if ($this->refresh) { ?>
    refreshtimer<?php echo $this->formid ?> =
        setTimeout(updateSearch<?php echo $this->formid ?>, refreshdelay<?php echo $this->formid ?>);
    <?php } ?>
};

/**
 * @brief Appel AJAX utilisé pour la pagination.
 *
 * @param string filter  Filtre
 * @param int start      Début
 * @param int end        Fin
 * @param int max        Nombre max par page
 */
updateSearchParam<?php echo $this->formid ?> = function(filter, start, end, max) {

    clearTimers<?php echo $this->formid ?>();

    var finalUrl =
        '<?php echo rtrim($this->url, "&"); ?>'
        + '&filter='     + encodeURIComponent(filter)
        + '&start='      + start
        + '&end='        + end
        + '&maxperpage=' + max;


    jQuery.ajax({
        url: finalUrl,
        type: 'get',
        success: function(data) {
            jQuery("#<?php echo $this->divid ?>").html(data);
        }
    });

    <?php if ($this->refresh) { ?>
    refreshparamtimer<?php echo $this->formid ?> =
        setTimeout(function() {
            updateSearchParam<?php echo $this->formid ?>(filter, start, end, max);
        }, refreshdelay<?php echo $this->formid ?>);
    <?php } ?>
};

/**
 * @brief Lance la recherche 500ms après la dernière frappe (debounce).
 */
pushSearch<?php echo $this->formid ?> = function() {
    clearTimers<?php echo $this->formid ?>();
    refreshtimer<?php echo $this->formid ?> =
        setTimeout(updateSearch<?php echo $this->formid ?>, 500);
};

// Appel initial
updateSearch<?php echo $this->formid ?>();

</script>

</form>

<?php
    }

    /**
     * @brief Affiche la div destinée à recevoir le contenu AJAX.
     */
    public function displayDivToUpdate()
    {
        echo '<div id="' . $this->divid . '"></div>';
    }
}

/**
 * @class AjaxFilterTimer
 * @brief Classe dérivée d'AjaxFilter pour appels AJAX automatiques périodiques.
 *
 * Cette classe hérite de AjaxFilter et ajoute la possibilité de déclencher
 * automatiquement les requêtes AJAX à intervalles réguliers si un refresh
 * est défini via setRefresh().
 *
 * Fonctionnalités :
 * - Hérite de tout le comportement de AjaxFilter (formulaire AJAX + filtre)
 * - Lance automatiquement la recherche AJAX au chargement de la page
 * - Continue les mises à jour périodiques selon l'intervalle défini
 *
 * Exemple d'utilisation :
 * @code
 * $ajax = new AjaxFilterTimer(urlStrRedirect("pkgs/pkgs/ajaxPackageList"));
 * $ajax->setRefresh(10000);  // refresh toutes les 10 secondes
 * $ajax->display();
 * $ajax->displayDivToUpdate();
 * @endcode
 */
class AjaxFilterTimer extends AjaxFilter
{
    /**
     * @brief Affichage du formulaire + initialisation du timer automatique
     *
     * Cette méthode surcharge display() pour lancer automatiquement
     * la première recherche AJAX et démarrer le refresh périodique.
     *
     * @param array $arrParam Paramètres supplémentaires (compatibilité)
     */
    public function display($arrParam = array())
    {
        // --- Appel de la méthode parent pour générer le formulaire AJAX ---
        parent::display($arrParam);

        // --- Si aucun refresh défini, on ne fait rien ---
        if (!$this->refresh) {
            return;
        }

        // --- Injection JavaScript pour démarrer automatiquement le timer ---
        ?>
<script type="text/javascript">
/* --------------------------------------------------------------------------
 * TIMER AUTOMATIQUE POUR AJAXFILTERTIMER
 * -------------------------------------------------------------------------- */
document.addEventListener("DOMContentLoaded", function () {

    // console.log("AjaxFilterTimer: refresh auto démarré (<?php echo $this->formid ?>) : <?php echo $this->refresh ?> ms");

    // --- Première mise à jour immédiate de la div ---
    updateSearch<?php echo $this->formid ?>();
});
</script>
        <?php
    }
}


class multifieldTpl extends AbstractTpl
{
    public $fields;

    public function __construct($fields)
    {
        $this->fields = $fields;
    }

    public function display($arrParam = array())
    {
        if (!isset($this->fields)) {
            return;
        }
        $separator = isset($arrParam['separator']) ? $arrParam['separator'] : ' &nbsp;&nbsp; ';

        for ($i = 0 ; $i < safeCount($this->fields) ; $i++) {
            $params = array();
            foreach($arrParam as $key => $value) {
                if(isset($value[$i])) {
                    $params[$key] = $value[$i];
                }
            }
            $this->fields[$i]->display($params);
            echo $separator;
        }
    }
}

class textTpl extends AbstractTpl
{
    public function __construct($text)
    {
        $this->text = $text;
    }

    public function display($arrParam = array())
    {
        echo $this->text;
    }
}

class NoLocationTpl extends AbstractTpl
{
    public function __construct($name)
    {
        $this->name = $name;
        $this->size = '13';
    }

    public function display($arrParam = array())
    {
        print '<span class="error">' . _("No item available") . '</span>';
        print '<input name="' . $this->name . '" id="' . $this->name . '" type="HIDDEN" size="' . $this->size . '" value="" class="searchfieldreal" />';
    }

    public function setSelected($elemnt)
    {

    }

}

class SingleLocationTpl extends AbstractTpl
{
    public function __construct($name, $label)
    {
        $this->name = $name;
        $this->label = $label;
        $this->value = null;
    }

    public function setElementsVal($value)
    {
        $this->value = array_values($value);
        $this->value = $this->value[0];
    }

    public function setSelected($elemnt)
    {

    }

    public function display($arrParam = array())
    {
        print $this->label;
        print '<input name="' . $this->name . '" id="' . $this->name . '" type="HIDDEN" value="' . $this->value . '" class="searchfieldreal" />';
    }

}

class AjaxFilterLocation extends AjaxFilter
{
    public function __construct($url, $divid = "container", $paramname = 'location', $params = array())
    {
        parent::__construct($url, $divid, $params);
        $this->location = new SelectItem($paramname, 'pushSearch', 'searchfieldreal noborder');
        $this->paramname = $paramname;
        $this->checkbox = array();
        $this->onchange = "pushSearch(); return false;";
    }
    public function addCheckbox($checkbox)
    {
        $checkbox->onchange = $this->onchange;
        $this->checkbox[] = $checkbox;
    }
    public function setElements($elt)
    {
        if (safeCount($elt) == 0) {
            $this->location = new NoLocationTpl($this->paramname);
        } elseif (safeCount($elt) == 1) {
            $loc = array_values($elt);
            $this->location = new SingleLocationTpl($this->paramname, $loc[0]);
        } else {
            $this->location->setElements($elt);
        }
    }

    public function setElementsVal($elt)
    {
        if (safeCount($elt) >= 1) {
            $this->location->setElementsVal($elt);
        }
    }

    public function setSelected($elemnt)
    {
        $this->location->setSelected($elemnt);
    }

    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        ?>
        <form name="Form" id="Form" action="#" onsubmit="return false;">
            <div id="searchSpan" class="searchbox">
            <div id="searchBest">
                <?php foreach ($this->checkbox as $checkbox) {
                    $checkbox->display();
                }
        ?>
                <span class="searchfield">
                    <?php
        $this->location->display();
        ?>
                </span>
                <input type="text" class="searchfieldreal" name="param" id="param" onkeyup="pushSearch();
                        return false;" />
                    <button type="button" class="search-clear" aria-label="<?php echo _T('Clear search', 'base'); ?>"
                         onclick="document.getElementById('param').value = '';
                                 pushSearch();
                                 return false;"></button>
            </div>
            <span class="loader" aria-hidden="true"></span>
            </div>

            <script type="text/javascript">
                jQuery('#param').focus();
                if(!(navigator.userAgent.toLowerCase().indexOf('chrome') > -1)) {
                    jQuery("#searchBest").width(jQuery("#searchBest").width()+20);
                }

        <?php
        if (isset($this->storedfilter)) {
            ?>
                    document.Form.param.value = "<?php echo $this->storedfilter ?>";
            <?php
        }
        ?>
                var maxperpage = <?php echo $conf["global"]["maxperpage"] ?>;
                if (jQuery('#maxperpage').length)
                    maxperpage = jQuery('#maxperpage').val();

                /**
                 * update div with user
                 */
                function updateSearch() {
                    /*add checkbox param*/
                    var strCheckbox ="";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                        }
                    });
                    launch--;
                    if (launch == 0) {
                        jQuery.ajax({
                            'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(document.Form.param.value) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + document.Form.<?php echo $this->paramname ?>.value + '&maxperpage=' + maxperpage +strCheckbox,
                            type: 'get',
                            success: function(data) {
                                jQuery("#<?php echo $this->divid; ?>").html(data);
                            }
                        });
                    }
                }

                /**
                 * provide navigation in ajax for user
                 */

                function updateSearchParam(filt, start, end) {
                    /*add checkbox param*/
                    var strCheckbox ="";
                    jQuery(".checkboxsearch").each(function() {
                        if (jQuery(this).is(":checked")) {
                            strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                        }
                    });
                    var reg = new RegExp("##", "g");
                    var tableau = filt.split(reg);
                    var location = "";
                    var filter = "";
                    var reg1 = new RegExp(tableau[0] + "##", "g");
                    if (filt.match(reg1)) {
                        if (tableau[0] != undefined) {
                            filter = tableau[0];
                        }
                        if (tableau[1] != undefined) {
                            location = tableau[1];
                        }
                    } else if (tableau.length == 1) {
                        if (tableau[0] != undefined) {
                            location = tableau[0];
                        }
                    }
                    if (jQuery('#maxperpage').length)
                        maxperpage = jQuery('#maxperpage').val();
                    if (!location)
                        location = document.Form.<?php echo $this->paramname ?>.value;
                    if (!filter)
                        filter = document.Form.param.value;

                    jQuery.ajax({
                        'url': '<?php echo $this->url; ?>filter=' + encodeURIComponent(filter) + '<?php echo $this->params ?>&<?php echo $this->paramname ?>=' + location + '&start=' + start + '&end=' + end + '&maxperpage=' + maxperpage +strCheckbox,
                        type: 'get',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        }
                    });

                }

                /**
                 * wait 500ms and update search
                 */

                function pushSearch() {
                    launch++;
                    setTimeout("updateSearch()", 500);
                }

                pushSearch();
            </script>

        </form>
        <?php
    }

}


/** NEW ajaxLocation */
class AjaxLocation extends AjaxFilterLocation
{
    public function __construct($url, $divid = "container", $paramname = 'location', $params = array())
    {
        parent::__construct($url, $divid, $paramname, $params);
        $this->location = new SelectItem($paramname, 'pushSearchLocation', 'searchfieldreal noborder');
        $this->onchange = "pushSearchLocation(); return false;";
    }

    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        ?>
        <form name="FormLocation" id="FormLocation" action="#" onsubmit="return false;">
            <div id="Location">
                <span id="searchSpan" class="searchbox">
                    <?php foreach ($this->checkbox as $checkbox) {
                        $checkbox->display();
                    } ?>
                    <span class="locationtext">&nbsp;<?php echo _("Select entity") ?>:&nbsp;</span>
                    <span class="locationfield">
                        <?php
                        // Le <select> est affiché par SelectItem
                        $this->location->display();
                        ?>
                    </span>
                </span>
                <span class="loader" aria-hidden="true"></span>
            </div>

            <script type="text/javascript">
                /**
                * Parse une querystring ("a=1&b=2") en objet {a:1, b:2}
                */
                function parseQuery(qs) {
                    var params = {};
                    qs = qs.replace(/^\?/, ''); // enlève le "?" si présent
                    var pairs = qs.split("&");
                    for (var i=0; i<pairs.length; i++) {
                        if (!pairs[i]) continue;
                        var parts = pairs[i].split("=");
                        var key = decodeURIComponent(parts[0] || "");
                        var val = decodeURIComponent(parts[1] || "");
                        params[key] = val;
                    }
                    return params;
                }

            function updateSearchLocation() {
                /* add checkbox param */
                var strCheckbox ="";
                jQuery(".checkboxsearch").each(function() {
                    if (jQuery(this).is(":checked")) {
                        strCheckbox+='&'+jQuery(this).attr('id')+"=true";
                    }
                });

                // Récupère l’option sélectionnée
                var selectedVal = jQuery("#<?php echo $this->paramname; ?>").val();
                var strSelected = "";

                if (selectedVal) {
                    // Parse la querystring contenue dans value
                    var parsed = parseQuery(selectedVal);

                    // Construit selected_location[clé]=valeur
                    for (var k in parsed) {
                        if (parsed.hasOwnProperty(k)) {
                            strSelected += "&<?php echo $this->paramname; ?>["+k+"]="+encodeURIComponent(parsed[k]);
                        }
                    }
                }

                launch--;
                if (launch == 0) {
                    jQuery.ajax({
                        'url': '<?php echo $this->url; ?><?php echo $this->params ?>' + strSelected + strCheckbox,
                        type: 'get',
                        success: function(data) {
                            jQuery("#<?php echo $this->divid; ?>").html(data);
                        }
                    });
                }
            }

                function pushSearchLocation() {
                    launch++;
                    setTimeout(updateSearchLocation, 500);
                }

                // Premier chargement
                pushSearchLocation();
            </script>
        </form>
        <?php
    }
}

class Checkbox
{
    public function __construct($paramname, $description)
    {
        $this->paramname = $paramname;
        $this->description = $description;
        $this->onchange = "";
    }
    public function display($arrParam = array())
    {
        global $conf;
        $root = $conf["global"]["root"];
        ?>
        <input checked style="top: 2px; left: 5px; position: relative; float: left"
        type="checkbox"
        class="checkboxsearch"
        name="<?php echo $this->paramname ?>"
        id="<?php echo  $this->paramname ?>" onchange=" <?php echo $this->onchange ?> "/>
        <span style="padding: 7px 15px; position: relative; float: left"><?php echo $this->description ?></span>
        <?php
    }
}

/**
 *  side menu items class
 *     this class is required by SideMenu class
 *     each SideMenuItem is all necessary information to
 *     create a link.
 *
 *     ex: create action "bar" in module "foo" with submodule "subfoo"
 *     new SideMenuItem("foobar example","foo","subfoo","bar");
 */
class SideMenuItem
{
    public $text;
    public $module;
    public $submod;
    public $action;
    public $activebg;
    public $inactivebg;
    public $active = false;

    /**
     *  main constructor
     * @param $text text for the link
     * @param $module module for link
     * @param $submod sub module for link
     * @param $action action param for link /!\ use for class id too
     * @param $activebg background image to use when menu is currently activated
     * @param $inactivebg background image to use when menu is currently inactivated
     */
    public function __construct($text, $module, $submod, $action, $activebg = "", $inactivebg = "")
    {
        $this->text = $text;
        $this->module = $module;
        $this->submod = $submod;
        $this->action = $action;
        $this->cssId = $action;
        $this->activebg = $activebg;
        $this->inactivebg = $inactivebg;
    }

    /**
     * @return a formated link like: main.php?module=base&submod=users&action=add
     *
     */
    public function getLink()
    {
        return 'main.php?module=' . $this->module . '&amp;submod=' . $this->submod . '&amp;action=' . $this->action;
    }

    /**
     *  display the SideMenuItem on the screen
     */
    public function display()
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            $activeClass = $this->active ? ' class="active"' : '';
            echo '<li id="' . $this->cssId . '"' . $activeClass . '>';
            echo '<a href="' . $this->getLink() . '">' . $this->text . '</a></li>';
        }
    }

    /**
     * Allows to set another CSS id then the default one which is the action
     * string
     *
     * @param id: the CSS id to use
     */
    public function setCssId($id)
    {
        $this->cssId = $id;
    }

    /**
     * Return the menu item CSS
     *
     * @param active: this menu item is active
     */
    public function getCss($active = false)
    {
        $this->active = $active;

        $bgi_active = $bgi_inactive = "";
        if ($this->activebg != "" && $this->inactivebg != "") {
            $bgi_active = "background-image: url(" . $this->activebg . ");";
            $bgi_inactive = "background-image: url(" . $this->inactivebg . ");";
        }

        if ($active && $bgi_active) {
            return "#sidebar ul.$this->submod li#$this->cssId a {
                        $bgi_active
            }";
        } elseif ($bgi_inactive) {
            return "#sidebar ul.$this->submod li#$this->cssId a {
                        $bgi_inactive
                    }
                    #sidebar ul.$this->submod li#$this->cssId a:hover {
                        $bgi_active
                    }";
        }

        return;
    }

}

class SideMenuItemNoAclCheck extends SideMenuItem
{
    /**
     *  display the SideMenuItem on the screen
     */
    public function display()
    {
        $activeClass = $this->active ? ' class="active"' : '';
        echo '<li id="' . $this->cssId . '"' . $activeClass . '>';
        echo '<a href="' . $this->getLink() . '" target="_self">' . $this->text . '</a></li>' . "\n";
    }

}

/**
 *  SideMenu class
 *     this class display side menu item
 *     side menu is mmc's left menu, it regroups
 *     possible actions we can do in a spécific module
 *     like index/configuration/add machine/ add share in
 *     samba module
 *     this class require SideMenuItem
 */
class SideMenu
{
    public $itemArray;
    public $className;
    public $backgroundImage;
    public $activatedItem;

    /**
     *  SideMenu default constructor
     *     initalize empty itemArray for SideMenuItem
     */
    public function __construct()
    {
        $this->itemArray = array();
        $this->backgroundImage = null;
        $this->activatedItem = null;
    }

    /**
     *  add a sideMenu Item into the SideMenu
     * @param $objSideMenuItem object SideMenuItem
     */
    public function addSideMenuItem($objSideMenuItem)
    {
        $this->itemArray[] = &$objSideMenuItem;
    }

    /**
     * CSS class
     */
    public function setClass($class)
    {
        $this->className = $class;
    }

    /**
     * @return className for CSS
     */
    public function getClass()
    {
        return $this->className;
    }

    /**
     * Set the sidemenu background image
     */
    public function setBackgroundImage($bg)
    {
        $this->backgroundImage = $bg;
    }

    /**
     * Get the sidemenu background image
     */
    public function getBackgroundImage()
    {
        return $this->backgroundImage;
    }

    /**
     *  print the SideMenu and the sideMenuItem
     */
    public function display()
    {
        global $sidebarDisplayed;
        $sidebarDisplayed = true;

        echo "<style>#section {display:grid; grid-template-columns:220px 1fr; gap:30px; align-items:start;}</style>";
        echo "<div id=\"sidebar\">\n";

        $MMCApp = &MMCApp::getInstance();
        $mod = $MMCApp->getModule($_GET['module']);
        $submod = $mod->getSubmod($_GET['submod']);
        $desc = $submod->getDescription();
        $icon = $submod->_img ? $submod->_img . '.svg' : '';

        echo '<div class="sidebar-header">';
        if ($icon) {
            echo '<img src="' . $icon . '" alt="" class="sidebar-header-icon" />';
        }
        echo '<span>' . $desc . '</span>';
        echo '</div>';

        echo "<ul class=\"" . $this->className . "\">\n";
        foreach ($this->itemArray as $objSideMenuItem) {
            $objSideMenuItem->display();
        }
        echo "</ul></div><div class=\"section-content\">";
    }

    /**
     *  @return return the Css content for a sidebar
     *  static method to get SideBarCss String
     */
    // public function getSideBarCss()
    // {
    //     $css = "";
    //     foreach ($this->itemArray as $objSideMenuItem) {
    //         $active = (($objSideMenuItem->submod == $_GET["submod"])
    //         && (($objSideMenuItem->action == $_GET["action"]) ||
    //         ($objSideMenuItem->action == $this->activatedItem)));
    //         $css = $css . $objSideMenuItem->getCss($active);
    //     }
    //     if ($this->backgroundImage) {
    //         $css .= "#sectionContainer { background-image: url(" . $this->backgroundImage . ") }";
    //     }
    //     return $css;
    // }
    public function getSideBarCss()
    {
        $css = "";
        $submod = $_GET["submod"] ?? "";
        $action = $_GET["action"] ?? "";

        foreach ($this->itemArray as $objSideMenuItem) {
            $active = (
                ($objSideMenuItem->submod == $submod)
                && (($objSideMenuItem->action == $action)
                || ($objSideMenuItem->action == $this->activatedItem))
            );
            $css .= $objSideMenuItem->getCss($active);
        }

        if ($this->backgroundImage) {
            $css .= "#sectionContainer { background-image: url(" . $this->backgroundImage . ") }";
        }

        return $css;
    }

    /**
     * Force a menu item to be displayed as activated
     * Useful for pages that don't have a dedicated tab
     */
    public function forceActiveItem($item)
    {
        $this->activatedItem = $item;
    }

}

/**
 *  PageGenerator class
 */
class PageGenerator
{
    public $sidemenu;  /* < SideMenu Object */
    public $content;   /* < array who contains contents Objects */

    /**
     *  Constructor
     */
    public function __construct($title = "")
    {
        $content = array();
        $this->title = $title;
    }

    /**
     *  set the sideMenu object
     */
    public function setSideMenu($objSideMenu)
    {
        $this->sidemenu = $objSideMenu;
    }

    /**
     * Set the page title
     */
    public function setTitle($title)
    {
        $this->title = $title;
    }

    /**
     *  display the whole page
     */
    public function display()
    {
        $this->displaySideMenu();
        if ($this->title) {
            $this->displayTitle();
        }
    }

    public function displayCss()
    {
        echo'<style type="text/css">' . "\n";
        echo '<!--' . "\n";
        echo $this->sidemenu->getSideBarCss();
        echo '-->' . "\n";
        echo '</style>' . "\n\n";
    }

    /**
     *  display the side Menu
     */
    public function displaySideMenu()
    {
        if ($this->sidemenu) {
            $this->displayCss();
            $this->sidemenu->display();
        }
    }

    /**
     *  display the page title
     */
    public function displayTitle()
    {
        if (isset($this->title)) {
            print "<h2>" . $this->title . "</h2>\n";
        }
    }

    /**
     * Sometimes, we don't want to add the fixheight div in the page
     */
    public function setNoFixHeight()
    {
        $this->fixheight = false;
    }

}

/**
 * Little wrapper that just include a PHP file as a HtmlElement
 */
class DisplayFile extends HtmlElement
{
    public function __construct($file)
    {
        parent::__construct();
        $this->file = $file;
    }

    public function display($arrParam = array())
    {
        require($this->file);
    }

}

/**
 * Class for a tab content
 */
class TabbedPage extends Div
{
    public function __construct($title, $file)
    {
        parent::__construct(array("class" => "tabdiv"));

        $this->title = $title;
        $this->add(new DisplayFile($file));
    }

    public function displayTitle()
    {
        return "<h2>" . $this->title . "</h2>\n";
    }

    public function begin()
    {
        $s = Div::begin();
        $s .= $this->displayTitle();
        return $s;
    }

}

/**
 * Class for tab displayed by TabSelector
 */
class TabWidget extends HtmlElement
{
    public function __construct($id, $title, $params = array())
    {
        $this->id = $id;
        $this->title = $title;
        $this->params = $params;
        $this->active = false;
        $this->last = false;
    }

    public function getLink()
    {
        return urlStr($_GET["module"] . "/" . $_GET["submod"] . "/" . $_GET["action"], array_merge(array("tab" => $this->id), $this->params));
    }

    public function setActive($flag)
    {
        $this->active = $flag;
    }

    public function display($arrParam = array())
    {
        if ($this->active) {
            $klass = ' class="tabactive"';
        } else {
            $klass = "";
        }
        print '<li id="' . $this->id . '"' . $klass . '"> '
                . '<a href="' . $this->getLink() . '">'
                . $this->title . "</a></li>";
    }

}

/**
 * This class allow to create a page with a tab selector
 */
class TabbedPageGenerator extends PageGenerator
{
    public function __construct()
    {
        parent::__construct();
        $this->topfile = null;
        $this->tabselector = new TabSelector();
        $this->pages = array();
        $this->firstTabActivated = false;
        $this->description = false;
    }

    /**
     * add a header above the tab selector
     */
    public function addTop($title, $file)
    {
        $this->title = $title;
        $this->topfile = $file;
    }

    public function setDescription($desc)
    {
        $this->description = $desc;
    }

    public function displayDescription()
    {
        if ($this->description) {
            printf('<p>%s</p>', $this->description);
        }
    }

    /**
     * Add a new tab to a page
     *
     * @param name: the tab id
     * @param title: the tab title in the tab selector
     * @param pagetitle: the page title
     * @param file: the file that renders the page
     * @param params: an array of URL parameters
     */
    public function addTab($id, $tabtitle, $pagetitle, $file, $params = array())
    {
        global $tabAclArray;
        if (hasCorrectTabAcl($_GET["module"], $_GET["submod"], $_GET["action"], $id)) {
            if (isset($_GET["tab"]) && $_GET["tab"] == $id) {
                $this->tabselector->addActiveTab($id, $tabtitle, $params);
            } else {
                if (isset($_GET["tab"])) {
                    $this->tabselector->addTab($id, $tabtitle, $params);
                } else {
                    if (!$this->firstTabActivated) {
                        $this->tabselector->addActiveTab($id, $tabtitle, $params);
                        $this->firstTabActivated = true;
                    } else {
                        $this->tabselector->addTab($id, $tabtitle, $params);
                    }
                }
            }
            $this->pages[$id] = array($pagetitle, $file);
        }
    }

    public function display()
    {
        $this->page = null;
        $this->displaySideMenu();
        $this->displayTitle();
        $this->displayDescription();
        if ($this->topfile) {
            require($this->topfile);
        }
        $this->tabselector->display();
        if (isset($_GET["tab"]) && isset($this->pages[$_GET["tab"]])) {
            list($title, $file) = $this->pages[$_GET["tab"]];
            $this->page = new TabbedPage($title, $file);
        } else {
            /* Get the first tab page */
            $tab = $this->tabselector->getDefaultTab();
            if ($tab != null) {
                list($title, $file) = $this->pages[$tab->id];
                $this->page = new TabbedPage($title, $file);
            }
        }
        if ($this->page != null) {
            $this->page->display();
        }
    }

}

/**
 * Allow to draw a tab selector
 */
class TabSelector extends HtmlContainer
{
    public function __construct()
    {
        parent::__construct();
        $this->tabs = array();
        $this->order = array();
    }

    public function getDefaultTab()
    {
        if (empty($this->elements)) {
            return null;
        } else {
            return $this->elements[0];
        }
    }

    public function addActiveTab($name, $title, $params = array())
    {
        $tab = new TabWidget($name, $title, $params);
        $tab->setActive(true);
        $this->add($tab);
    }

    public function addTab($name, $title, $params = array())
    {
        $this->add(new TabWidget($name, $title, $params));
    }

    public function begin()
    {
        return '<div class="tabselector"><ul>';
    }

    public function end()
    {
        return "</ul></div>";
    }

}

/**
 * display popup window if notify add in queue
 *
 */
class NotifyWidget
{
    public $id;
    public $strings;
    public $level;
    /**
     * default constructor
     */
    public function __construct($save = true)
    {
        $this->id = uniqid();
        $this->strings = array();
        // 0: info (default, blue info bubble)
        // 1: error for the moment (red icon)
        // 5 is critical
        $this->level = 0;
        if ($save) {
            $this->save();
        }
    }

    /**
     * Save the object in the session
     */
    public function save()
    {
        if (!isset($_SESSION["notify"])) {
            $_SESSION["notify"] = array();
        }
        if ($this->strings) {
            $_SESSION["notify"][$this->id] = serialize($this);
        }
    }

    public function setSize()
    {
        // Deprecated
        return;
    }

    public function setLevel($level)
    {
        $this->level = $level;
    }

    /**
     * Add a string in notify widget
     * @param $str any HTML CODE
     */
    public function add($str, $save = true)
    {
        $this->strings[] = $str;
        if ($save) {
            $this->save();
        }
    }

    public function getImgLevel()
    {
        if ($this->level != 0) {
            return "img/common/icn_alert.gif";
        } else {
            return "img/common/big_icn_info.png";
        }
    }

    public static function begin()
    {
        return '<div style="padding: 10px">';
    }

    public function content()
    {
        $str = '<div style="width: 50px; padding-top: 15px; float: left; text-align: center"><img src="' . $this->getImgLevel() . '" /></div><div style="margin-left: 60px">';
        foreach ($this->strings as $string) {
            $str .= $string;
        }
        $str .= '</div>';
        return $str;
    }

    public static function end()
    {
        $str = '<div style="clear: left; text-align: right; margin-top: 1em;"><button class="btn btn-small" onclick="closePopup()">' . _("Close") . '</button></div></div>';
        return $str;
    }

    public function flush()
    {
        unset($_SESSION["notify_render"][$this->id]);
    }

}

/**
 * display a popup window with a message for a successful operation
 *
 */
class NotifyWidgetSuccess extends NotifyWidget
{
    public function __construct($message)
    {
        // parent::NotifyWidget();
        parent::__construct();
        $this->add("<div class=\"alert alert-success\">$message</div>");
    }

}

/**
 * display a popup window with a message for a failure
 *
 */
class NotifyWidgetFailure extends NotifyWidget
{
    public function __construct($message)
    {
        parent::__construct();
        // parent::NotifyWidget();
        $this->add("<div class=\"alert alert-error\">$message</div>");
        $this->level = 4;
        $this->save();
    }

}

/**
 * display a popup window with a message for a warning
 *
 */
class NotifyWidgetWarning extends NotifyWidget
{
    public function __construct($message)
    {
        // parent::NotifyWidget();
        parent::__construct();

        $this->add("<div class=\"alert\">$message</div>");
        $this->level = 3;
        $this->save();
    }

}

/**
 * Display a simple DIV with a message
 */
class Message extends HtmlElement
{
    public function __construct($msg, $type = "info")
    {
        $this->msg = $msg;
        $this->type = $type;
    }

    public function display($arrParam = array())
    {
        print '<div class="alert alert-' . $this->type . '">' . $this->msg . '</div>';
    }

}

class ErrorMessage extends Message
{
    public function __construct($msg)
    {
        parent::__construct($msg, "error");
    }

}

class SuccessMessage extends Message
{
    public function __construct($msg)
    {
        parent::__construct($msg, "success");
    }

}

class WarningMessage extends Message
{
    public function __construct($msg)
    {
        parent::__construct($msg, "warning");
    }

}

/**
 * Create an URL
 *
 * @param $link string accept format like "module/submod/action" or
 *              "module/submod/action/tab"
 * @param $param assoc array with param to add in GET method
 * @param $ampersandEncode bool defining if we want ampersand to be encoded in URL
 */
// function urlStr($link, $param = array(), $ampersandEncode = true)
// {
//     $arr = array();
//     $arr = explode('/', $link);
//
//     if ($ampersandEncode) {
//         $amp = "&amp;";
//     } else {
//         $amp = "&";
//     }
//
//     $enc_param = "";
//     foreach ($param as $key => $value) {
//         $enc_param .= "$amp" . "$key=$value";
//     }
//     if (safeCount($arr) == 3) {
//         $ret = "main.php?module=" . $arr[0] . "$amp" . "submod=" . $arr[1] . "$amp" . "action=" . $arr[2] . $enc_param;
//     } elseif (safeCount($arr) == 4) {
//         $ret = "main.php?module=" . $arr[0] . "$amp" . "submod=" . $arr[1] . "$amp" . "action=" . $arr[2] . "$amp" . "tab=" . $arr[3] . $enc_param;
//     } else {
//         die("Can't build URL");
//     }
//
//     return $ret;
// }

/**
 * Retourne un nouveau tableau sans les clés spécifiées.
 *
 * @param array|null $array Tableau à filtrer (par défaut $_GET)
 * @param array|null $keysToRemove Clés à supprimer (par défaut ['module', 'submod', 'action'])
 * @return array Nouveau tableau filtré
 */
function getFilteredGetParams(?array $array = null, ?array $keysToRemove = null): array
{
    // Définir le tableau à filtrer
    $array = $array ?? $_GET;

    // Définir les clés à supprimer (par défaut)
    $keysToRemove = $keysToRemove ?? ['module', 'submod', 'action' ];

    // Retourner un nouveau tableau sans les clés indésirables
    return array_diff_key($array, array_flip($keysToRemove));
}



function urlStr($link, $param = array(), $ampersandEncode = true)
{
    $arr = explode('/', $link);
    $amp = $ampersandEncode ? "&amp;" : "&";

    // Construction de la base de l'URL selon le nombre d'éléments
    if (count($arr) == 3) {
        $baseUrl = "main.php?module={$arr[0]}{$amp}submod={$arr[1]}{$amp}action={$arr[2]}";
    } elseif (count($arr) == 4) {
        $baseUrl = "main.php?module={$arr[0]}{$amp}submod={$arr[1]}{$amp}action={$arr[2]}{$amp}tab={$arr[3]}";
    } else {
        die("Can't build URL");
    }

    // Ajout des paramètres supplémentaires avec http_build_query
    if (!empty($param)) {
        $queryString = http_build_query($param);
        // Remplace le premier '&' par le séparateur choisi ($amp)
        $baseUrl .= $amp . str_replace('&', $amp, $queryString);
    }

    return $baseUrl;
}

function urlStrRedirect($link, $param = array())
{
    return(urlStr($link, $param, false));
}

function findInSideBar($sidebar, $query)
{
    foreach ($sidebar['content'] as $arr) {
        if (preg_match("/$query/", $arr['link'])) {
            return $arr['text'];
        }
    }
}

function findFirstInSideBar($sidebar)
{
    return $sidebar['content'][0]['text'];
}

class HtmlElement
{
    public $options;

    public function __construct()
    {
        $this->options = array();
    }

    public function setOptions($options)
    {
        $this->options = $options;
    }

    public function hasBeenPopped()
    {
        return true;
    }

    public function display($arrParam = array())
    {
        die("Must be implemented by the subclass");
    }

}

class HtmlContainer
{
    public $elements;
    public $index;
    public $popped;
    public $debug;

    public function __construct()
    {
        $this->elements = array();
        $this->popped = false;
        $this->index = -1;
    }

    public function begin()
    {
        die("Must be implemented by the subclass");
    }

    public function end()
    {
        die("Must be implemented by the subclass");
    }

    public function display()
    {
        print "\n" . $this->begin() . "\n";
        foreach ($this->elements as $element) {
            $element->display();
        }
        print "\n" . $this->end() . "\n";
    }

    public function add($element, $options = array())
    {
        $element->setOptions($options);
        $this->push($element);
    }

    public function push($element)
    {
        if ($this->index == -1) {
            /* Add first element to container */
            $this->index++;
            $this->elements[$this->index] = $element;
        //print "pushing " . $element->options["id"] . " into " . $this->options["id"] . "<br>";
        } else {
            if ($this->elements[$this->index]->hasBeenPopped()) {
                /* All the contained elements have been popped, so add the new element in the list */
                $this->index++;
                $this->elements[$this->index] = $element;
            //print "pushing " . $element->options["id"] . " into " . $this->options["id"] . "<br>";
            } else {
                /* Recursively push a new element into the container */
                $this->elements[$this->index]->push($element);
            }
        }
    }

    public function hasBeenPopped()
    {

        if ($this->popped) {
            $ret = true;
        } elseif ($this->index == -1) {
            $ret = false;
        } else {
            $ret = false;
        }
        return $ret;
    }

    public function pop()
    {
        if (!$this->popped) {
            if ($this->index == -1) {
                $this->popped = true;
            } elseif ($this->elements[$this->index]->hasBeenPopped()) {
                $this->popped = true;
            } else {
                $this->elements[$this->index]->pop();
            }
        //if ($this->popped) print "popping " . $this->options["id"] . "<br>";
        } else {
            die("Nothing more to pop");
        }
    }

}

class Div extends HtmlContainer
{
    public function __construct($options = array(), $class = null)
    {
        //$this->HtmlContainer();
        parent::__construct();
        $this->name = $class;
        $this->options = $options;
        $this->display = true;
    }

    public function begin()
    {
        $str = "";
        foreach ($this->options as $key => $value) {
            $str .= " $key=\"$value\"";
        }
        if (!$this->display) {
            $displayStyle = ' style =" display: none;"';
        } else {
            $displayStyle = "";
        }
        return "<div$str$displayStyle>";
    }

    public function end()
    {
        return "</div>";
    }

    public function setVisibility($flag)
    {
        $this->display = $flag;
    }

}

class Form extends HtmlContainer
{
    public function __construct($options = array())
    {
        parent::__construct();

        if (!isset($options["method"])) {
            $options["method"] = "post";
        }
        if (!isset($options["id"])) {
            $options["id"] = "Form";
        }
        $this->options = $options;
        $this->buttons = array();
        $this->summary = null;
    }

    public function begin()
    {
        $str = "";
        foreach ($this->options as $key => $value) {
            $str .= " $key=\"$value\"";
        }
        $ret = "<form class=\"mmc-form\"$str>";
        if (isset($this->summary)) {
            $ret = "<p>" . $this->summary . "</p>\n" . $ret;
        }
        return $ret;
    }

    public function end()
    {
        $str = '<input type="hidden" name="auth_token" value="' . $_SESSION['auth_token'] . '">'."\n";
        foreach ($this->buttons as $button) {
            $str .= "\n$button\n";
        }
        $str .= "\n</form>\n";
        return $str;
    }

    public function addButton($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        $b = new Button();
        $this->buttons[] = $b->getButtonString($name, $value, $klass, $extra, $type);
    }

    public function addValidateButton($name)
    {
        $b = new Button();
        $this->buttons[] = $b->getValidateButtonString($name);
    }

    public function addValidateButtonWithValue($name, $value)
    {
        $b = new Button();
        $this->buttons[] = $b->getButtonString($name, $value);
    }

    public function addCancelButton($name)
    {
        $b = new Button();
        $this->buttons[] = $b->getCancelButtonString($name);
    }

    public function addExpertButton($name, $value)
    {
        $d = new DivExpertMode();
        $b = new Button();
        $this->buttons[] = $d->begin() . $b->getButtonString($name, $value) . $d->end();
    }

    public function addSummary($msg)
    {
        $this->summary = $msg;
    }

    public function getButtonString($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        $b = new Button();
        return $b->getButtonString($name, $value, $klass, $extra, $type);
    }

    public function addOnClickButton($text, $url)
    {
        $b = new Button();
        $this->buttons[] = $b->getOnClickButton($text, $url);
    }

}

class Button
{
    public function __construct($module = null, $submod = null, $action = null) # TODO also verify ACL on tabs
    {
        if ($module == null) {
            $this->module = $_GET["module"];
        } else {
            $this->module = $module;
        }
        if ($submod == null) {
            $this->submod = $_GET["submod"];
        } else {
            $this->submod = $submod;
        }
        if ($action == null) {
            $this->action = $_GET["action"];
        } else {
            $this->action = $action;
        }
    }

    public function getButtonString($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        if (hasCorrectAcl($this->module, $this->submod, $this->action)) {
            return $this->getButtonStringWithRight($name, $value, $klass, $extra, $type);
        } else {
            return $this->getButtonStringWithNoRight($name, $value, $klass, $extra, $type);
        }
    }

    public function getButtonStringWithRight($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        return "<input type=\"$type\" name=\"$name\" value=\"$value\" class=\"$klass\" $extra />";
    }

    public function getButtonStringWithNoRight($name, $value, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        return "<input disabled type=\"$type\" name=\"$name\" value=\"$value\" class=\"btnDisabled\" $extra />";
    }

    public function getValidateButtonString($name, $klass = "btnPrimary", $extra = "", $type = "submit")
    {
        return $this->getButtonString($name, _("Confirm"), $klass);
    }

    public function getCancelButtonString($name, $klass = "btnSecondary", $extra = "", $type = "submit")
    {
        return $this->getButtonString($name, _("Cancel"), $klass);
    }

    public function getOnClickButton($text, $url, $klass = "btnPrimary", $extra = "", $type = "button")
    {
        return $this->getButtonString("onclick", $text, $klass, $extra = "onclick=\"location.href='" . $url . "';\"", $type);
    }

}

class ValidatingForm extends Form
{
    public function __construct($options = array())
    {
        parent::__construct($options);

        $this->options["onsubmit"] = "return validateForm('" . $this->options["id"] . "');";
    }

    public function end()
    {
        $str = parent::end();
        $str .= "
        <script type=\"text/javascript\">
            jQuery('#" . $this->options["id"] . ":not(.filter) :input:visible:enabled:first').focus();
        </script>\n";
        return $str;
    }

}

/**
 *
 * Allow to easily build the little popup displayed when deleting a user for example
 *
 */
class PopupForm extends Form
{
    public function __construct($title, $id = 'Form')
    {
        $options = array("action" => $_SERVER["REQUEST_URI"], 'id' => $id);
        parent::__construct($options);

        $this->title = $title;
        $this->text = array();
        $this->ask = "";
    }

    public function begin()
    {
        $str = "<h2>" . $this->title . "</h2>\n";
        $str .= parent::begin();
        foreach ($this->text as $text) {
            $str .= "<p>" . $text . "</p>";
        }
        return $str;
    }

    public function end()
    {
        $str = "<p>" . $this->ask . "</p>";
        $str .= parent::end();
        return $str;
    }

    public function addText($msg)
    {
        $this->text[] = $msg;
    }

    public function setQuestion($msg)
    {
        $this->ask = $ask;
    }

    public function addValidateButtonWithFade($name)
    {
        $this->buttons[] = $this->getButtonString($name, _("Confirm"), "btnPrimary", "onclick=\"closePopup(); return true;\"");
    }

    public function addCancelButton($name)
    {
        $this->buttons[] = $this->getButtonString($name, _("Cancel"), "btnSecondary", "onclick=\"closePopup(); return false;\"");
    }

}

/**
 *
 * Allow to easily build the little popup, summon a new window
 *
 */
class PopupWindowForm extends PopupForm
{
    public function __construct($title)
    {
        $options = array("action" => $_SERVER["REQUEST_URI"]);
        parent::__construct($options);
        $this->title = $title;
        $this->text = array();
        $this->ask = "";
        $this->target_uri = "";
    }

    public function addValidateButtonWithFade($name)
    {
        $this->buttons[] = $this->getButtonString($name, _("Confirm"), "btnPrimary", "onclick=\"jQuery('popup').fadeOut(); window.open('" . $this->target_uri . "', '', 'toolbar=no, location=no, menubar=no, status=no, status=no, scrollbars=yes, width=330, height=200'); return false;\"");
    }

}

class Table extends HtmlContainer
{
    public function __construct($options = array())
    {
        parent::__construct();
        $this->lines = array();
        $this->tr_style = '';
        $this->td_style = '';
        $this->options = $options;
        if (isset($options['tr_style'])) {
            $this->tr_style = $options['tr_style'];
        }
        if (isset($options['td_style'])) {
            $this->td_style = $options['td_style'];
        }
    }

    public function setLines($lines)
    {
        $this->lines = $lines;
    }

    public function begin()
    {
        return '<table class="mmc-form-table" cellspacing="0">';
    }

    public function end()
    {
        return "</table>";
    }

    public function getContent()
    {
        $str = '';
        foreach ($this->lines as $line) {
            $str .= sprintf("<tr%s><td%s>%s</td></tr>", $this->tr_style, $this->td_style, implode(sprintf('</td><td%s>', $this->td_style), $line));
        }
        return $str;
    }

    public function displayTable($displayContent = false)
    {
        print $this->begin();
        if ($displayContent) {
            print $this->getContent();
        }
        print $this->end();
    }

}

class DivForModule extends Div
{
    public function __construct($title, $color, $options = array())
    {
        $options["style"] = "background-color: " . $color;
        $options["class"] = "formblock";
        parent::__construct($options);
        $this->title = $title;
        $this->color = $color;
    }

    public function begin()
    {
        print parent::begin();
        print "<h3>" . $this->title . "</h3>";
    }

}

class DivExpertMode extends Div
{
    public function begin()
    {
        $str = '<div id="expertMode" ';
        if (isExpertMode()) {
            $str .= ' style="display: inline;"';
        } else {
            $str .= ' style="display: none;"';
        }
        return $str . ' >';
    }

}

class ModuleTitleElement extends HtmlElement
{
    public function __construct($title)
    {
        $this->title = $title;
    }

    public function display($arrParam = array())
    {
        print '<br><h1>' . $this->title . '</h1>';
    }

}

class TitleElement extends HtmlElement
{
    public function __construct($title, $level = 2, $attributes = [])
    {
        $this->title = $title;
        $this->level = $level;
        $this->attributes = $attributes;
    }

    public function display($arrParam = array())
    {
        $attrs = array_merge($this->attributes, $arrParam);
        $attr_str = '';
        foreach ($attrs as $k => $v) {
            $attr_str .= ' ' . htmlspecialchars($k) . '="' . htmlspecialchars($v) . '"';
        }
        print '<br/><h' . $this->level . $attr_str . '>' . $this->title . '</h' . $this->level . '>';
    }
}

class SpanElement extends HtmlElement
{
    public function __construct($content, $class = null)
    {
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
    }

    public function display($arrParam = array())
    {
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        } else {
            $class = '';
        }
        printf('<span%s>%s</span>', $class, $this->content);
    }
}

class ParaElement extends HtmlElement
{
    public function __construct($content, $class = null)
    {
        $this->name = $class;
        $this->content = $content;
        $this->class = $class;
    }

    public function display($arrParam = array())
    {
        if ($this->class) {
            $class = ' class="' . $this->class . '"';
        } else {
            $class = '';
        }
        printf('<p%s>%s</p>', $class, $this->content);
    }

}

class SelectElement extends HtmlElement
{
    public function __construct($name, $nametab)
    {
        $this->name = $name;
        $this->nametab = $nametab;
    }

    public function display($arrParam = array())
    {
        $p = new ParaElement('<a href="javascript:void(0);" onclick="checkAll(this, \'' . $this->name . '\',1); checkAll(this, \'' . $this->nametab . '\',1);">' . _("Select all") . ' </a> / <a href="javascript:void(0);" onclick="checkAll(this, \'' . $this->name . '\',0); checkAll(this, \'' . $this->nametab . '\',0);">' . _("Unselect all") . '</a>');
        $p->display();
    }

}

class TrTitleElement extends HtmlElement
{
    public function __construct($arrtitles)
    {
        $this->titles = $arrtitles;
    }

    public function display($arrParam = array())
    {
        $colsize = 100 / sizeof($this->titles);
        print '<tr>';
        foreach ($this->titles as $value) {
            print '<td width="' . $colsize . '%"><b>' . $value . '</b></td>';
        }
        print '</tr>';
    }

}

class AjaxUrlDiv extends AjaxPage
{
    public function __construct($url, $id = "container", $params = array())
    {
        // Appel du constructeur parent sans le paramètre refresh
        parent::__construct($url, $id, $params, null);
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <div id="{$this->id}" class="{$this->class}"></div>
        <script type="text/javascript">
        jQuery.ajax({
            url: '{$this->url}',
            type: 'get',
            data: {$this->params},
            success: function(data){
                jQuery("#{$this->id}").html(data);
            }
        });
        </script>
EOT;
    }
}

class AjaxPage extends HtmlElement
{
    public function __construct($url, $id = "container", $params = array(), $refresh = 10)
    {
        $this->url = $url;
        $this->id = $id;
        $this->class = "";
        $this->params = json_encode($params);
        $this->refresh = $refresh;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <div id="{$this->id}" class="{$this->class}"></div>
        <script type="text/javascript">
        function update_{$this->id}(){
            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);
                    setTimeout('update_{$this->id}()',1000*{$this->refresh});
                }
            });
        }
        update_{$this->id}();

        </script>
EOT;
    }
}

class AjaxPagebar extends AjaxPage
{
    protected $progressBarId;

    public function __construct($url, $id = "container", $params = array(), $refresh = 10, $progressBarId = "progressBarContainer")
    {
        parent::__construct($url, $id, $params, $refresh);
        $this->progressBarId = $progressBarId;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <div id="{$this->id}" class="{$this->class}"></div>
        <div id="{$this->progressBarId}" style="width: 100%; background-color: #f3f3f3; margin-top: 5px;">
            <div id="{$this->progressBarId}_bar" style="width: 100%; height: 20px; background-color: #4CAF50; text-align: center; line-height: 20px; color: white;"></div>
        </div>
        <script type="text/javascript">
        var remainingTime_{$this->id} = {$this->refresh};
        var timerInterval_{$this->id};

        function updateProgressBar_{$this->id}() {
            var percent = (remainingTime_{$this->id} / {$this->refresh}) * 100;
            jQuery("#{$this->progressBarId}_bar").width(percent + "%");
            jQuery("#{$this->progressBarId}_bar").text("Rafraîchissement dans " + remainingTime_{$this->id} + "s");
        }

        function update_{$this->id}(){
            clearInterval(timerInterval_{$this->id});
            remainingTime_{$this->id} = {$this->refresh};
            updateProgressBar_{$this->id}();

            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);
                    timerInterval_{$this->id} = setInterval(function() {
                        remainingTime_{$this->id}--;
                        updateProgressBar_{$this->id}();
                        if (remainingTime_{$this->id} <= 0) {
                            clearInterval(timerInterval_{$this->id});
                        }
                    }, 1000);
                    setTimeout('update_{$this->id}()',1000*{$this->refresh});
                }
            });
        }
        update_{$this->id}();
        </script>
EOT;
    }
}

class AjaxPagerefreshanim extends AjaxPage
{
    protected $animationContainerId;

    public function __construct($url, $id = "container", $params = array(), $refresh = 10, $animationContainerId = "refreshAnimationContainer")
    {
        parent::__construct($url, $id, $params, $refresh);
        $this->animationContainerId = $animationContainerId;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <style>
            #{$this->animationContainerId} {
                display: flex;
                align-items: center;
                justify-content: center;
                margin-top: 10px;
                font-family: Arial, sans-serif;
            }
            .pulse-circle {
                width: 20px;
                height: 20px;
                background-color: #4CAF50;
                border-radius: 50%;
                margin-right: 10px;
                animation: pulse 1.5s infinite;
            }
            @keyframes pulse {
                0% { transform: scale(1); opacity: 1; }
                50% { transform: scale(1.5); opacity: 0.7; }
                100% { transform: scale(1); opacity: 1; }
            }
            #{$this->animationContainerId}_text {
                font-size: 14px;
                color: #555;
            }
        </style>
        <div id="{$this->id}" class="{$this->class}"></div>
        <div id="{$this->animationContainerId}">
            <div class="pulse-circle"></div>
            <div id="{$this->animationContainerId}_text">Rafraîchissement dans {$this->refresh}s</div>
        </div>
        <script type="text/javascript">
        var remainingTime_{$this->id} = {$this->refresh};
        var timerInterval_{$this->id};

        function updateAnimationText_{$this->id}() {
            jQuery("#{$this->animationContainerId}_text").text("Rafraîchissement dans " + remainingTime_{$this->id} + "s");
        }

        function update_{$this->id}(){
            clearInterval(timerInterval_{$this->id});
            remainingTime_{$this->id} = {$this->refresh};
            updateAnimationText_{$this->id}();

            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);
                    timerInterval_{$this->id} = setInterval(function() {
                        remainingTime_{$this->id}--;
                        updateAnimationText_{$this->id}();
                        if (remainingTime_{$this->id} <= 0) {
                            clearInterval(timerInterval_{$this->id});
                        }
                    }, 1000);
                    setTimeout('update_{$this->id}()',1000*{$this->refresh});
                }
            });
        }
        update_{$this->id}();
        </script>
EOT;
    }
}

class AjaxPagetimebar extends AjaxPage
{
    protected $progressBarId;

    public function __construct($url, $id = "container", $params = array(), $refresh = 10, $progressBarId = "progressBarContainer")
    {
        parent::__construct($url, $id, $params, $refresh);
        $this->progressBarId = $progressBarId;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <style>
            #{$this->progressBarId} {
                width: 100%;
                background-color: #f0f0f0;
                border-radius: 10px;
                margin-top: 10px;
                overflow: hidden;
                box-shadow: inset 0 1px 3px rgba(0, 0, 0, 0.2);
            }
            #{$this->progressBarId}_bar {
                width: 100%;
                height: 20px;
                background: linear-gradient(90deg, #4CAF50, #8BC34A);
                border-radius: 10px;
                text-align: center;
                line-height: 20px;
                color: white;
                font-family: Arial, sans-serif;
                font-size: 12px;
                transition: width 0.3s ease;
                box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2);
            }
        </style>
        <div id="{$this->id}" class="{$this->class}"></div>
        <div id="{$this->progressBarId}">
            <div id="{$this->progressBarId}_bar">Rafraîchissement dans {$this->refresh}s</div>
        </div>
        <script type="text/javascript">
        var remainingTime_{$this->id} = {$this->refresh};
        var timerInterval_{$this->id};

        function updateProgressBar_{$this->id}() {
            var percent = (remainingTime_{$this->id} / {$this->refresh}) * 100;
            jQuery("#{$this->progressBarId}_bar").width(percent + "%");
            jQuery("#{$this->progressBarId}_bar").text("Rafraîchissement dans " + remainingTime_{$this->id} + "s");
        }

        function update_{$this->id}(){
            clearInterval(timerInterval_{$this->id});
            remainingTime_{$this->id} = {$this->refresh};
            updateProgressBar_{$this->id}();

            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);
                    timerInterval_{$this->id} = setInterval(function() {
                        remainingTime_{$this->id}--;
                        updateProgressBar_{$this->id}();
                        if (remainingTime_{$this->id} <= 0) {
                            clearInterval(timerInterval_{$this->id});
                        }
                    }, 1000);
                    setTimeout('update_{$this->id}()',1000*{$this->refresh});
                }
            });
        }
        update_{$this->id}();
        </script>
EOT;
    }
}


class AjaxPageAdminTime extends AjaxPage
{
    protected $animationContainerId;

    public function __construct($url, $id = "container", $params = array(), $refresh = 10, $animationContainerId = "circularProgressContainer")
    {
        parent::__construct($url, $id, $params, $refresh);
        $this->animationContainerId = $animationContainerId;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <style>
            .circular-progress-container {
                display: inline-flex;
                align-items: center;
                vertical-align: middle;
                margin-left: 8px;
            }
            .circular-progress {
                position: relative;
                width: 20px;
                height: 20px;
                border-radius: 50%;
                background: conic-gradient(#4CAF50 0%, #e0e0e0 0%);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.3s ease;
            }
            .circular-progress::before {
                content: "";
                position: absolute;
                width: 16px;
                height: 16px;
                border-radius: 50%;
                background: white;
            }
            .circular-progress-text {
                font-size: 8px;
                font-weight: bold;
                color: #555;
                z-index: 1;
            }
            #{$this->animationContainerId} {
                position: relative;
                width: 20px;
                height: 20px;
                margin: 0 auto 10px;
            }
        </style>
        <div id="{$this->id}" class="{$this->class}"></div>
        <script type="text/javascript">
        var remainingTime_{$this->id} = {$this->refresh};
        var timerInterval_{$this->id} = null;
        var isFirstLoad_{$this->id} = true;

        function updateCircularProgress_{$this->id}() {
            var percent = (remainingTime_{$this->id} / {$this->refresh}) * 100;
            var angle = (360 * percent) / 100;
            jQuery("#{$this->animationContainerId}_progress").css("background", "conic-gradient(#4CAF50 " + angle + "deg, #e0e0e0 0deg)");
            jQuery("#{$this->animationContainerId}_text").text(remainingTime_{$this->id});
        }

        function update_{$this->id}(){
            if (timerInterval_{$this->id} !== null) {
                clearInterval(timerInterval_{$this->id});
            }

            remainingTime_{$this->id} = {$this->refresh};
            updateCircularProgress_{$this->id}();

            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);

                    if (isFirstLoad_{$this->id}) {
                        var firstH2 = jQuery("h2").first();
                        if (firstH2.length > 0) {
                            var progressHTML = `
                                <span class="circular-progress-container" id="{$this->animationContainerId}">
                                    <div class="circular-progress" id="{$this->animationContainerId}_progress">
                                        <div class="circular-progress-text" id="{$this->animationContainerId}_text">{$this->refresh}</div>
                                    </div>
                                </span>
                            `;
                            firstH2.append(progressHTML);
                        } else {
                            var progressHTML = `
                                <div id="{$this->animationContainerId}" style="position: relative; width: 20px; height: 20px; margin: 0 auto 10px;">
                                    <div class="circular-progress" id="{$this->animationContainerId}_progress">
                                        <div class="circular-progress-text" id="{$this->animationContainerId}_text">{$this->refresh}</div>
                                    </div>
                                </div>
                            `;
                            jQuery("#{$this->id}").before(progressHTML);
                        }
                        isFirstLoad_{$this->id} = false;
                    }

                    timerInterval_{$this->id} = setInterval(function() {
                        remainingTime_{$this->id}--;
                        updateCircularProgress_{$this->id}();
                        if (remainingTime_{$this->id} <= 0) {
                            clearInterval(timerInterval_{$this->id});
                        }
                    }, 1000);

                    setTimeout(function() {
                        update_{$this->id}();
                    }, 1000 * {$this->refresh});
                }
            });
        }

        update_{$this->id}();
        </script>
EOT;
    }
}

class AjaxPagebartitlletime extends AjaxPage
{
    protected $animationContainerId;

    public function __construct($url, $id = "container", $params = array(), $refresh = 10, $animationContainerId = "circularProgressContainer")
    {
        parent::__construct($url, $id, $params, $refresh);
        $this->animationContainerId = $animationContainerId;
    }

    public function display($arrParam = array())
    {
        echo <<< EOT
        <style>
            .circular-progress-container {
                display: inline-flex;
                align-items: center;
                vertical-align: middle;
                margin-left: 10px;
            }
            .circular-progress {
                position: relative;
                width: 30px;
                height: 30px;
                border-radius: 50%;
                background: conic-gradient(#4CAF50 0%, #e0e0e0 0%);
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.3s ease;
            }
            .circular-progress::before {
                content: "";
                position: absolute;
                width: 24px;
                height: 24px;
                border-radius: 50%;
                background: white;
            }
            .circular-progress-text {
                font-size: 10px;
                font-weight: bold;
                color: #555;
                z-index: 1;
            }
            #{$this->animationContainerId} {
                position: relative;
                width: 60px;
                height: 60px;
                margin: 0 auto 10px;
            }
        </style>
        <div id="{$this->id}" class="{$this->class}"></div>
        <script type="text/javascript">
        var remainingTime_{$this->id} = {$this->refresh};
        var timerInterval_{$this->id} = null;
        var isFirstLoad_{$this->id} = true;

        function updateCircularProgress_{$this->id}() {
            var percent = (remainingTime_{$this->id} / {$this->refresh}) * 100;
            var angle = (360 * percent) / 100;
            jQuery("#{$this->animationContainerId}_progress").css("background", "conic-gradient(#4CAF50 " + angle + "deg, #e0e0e0 0deg)");
            jQuery("#{$this->animationContainerId}_text").text(remainingTime_{$this->id});
        }

        function update_{$this->id}(){
            // Nettoyage de l'intervalle précédent
            if (timerInterval_{$this->id} !== null) {
                clearInterval(timerInterval_{$this->id});
            }

            remainingTime_{$this->id} = {$this->refresh};
            updateCircularProgress_{$this->id}();

            jQuery.ajax({
                'url': '{$this->url}',
                type: 'get',
                data: {$this->params},
                success: function(data){
                    jQuery("#{$this->id}").html(data);

                    // Intégration dynamique dans le premier <h2> s'il existe
                    if (isFirstLoad_{$this->id}) {
                        var firstH2 = jQuery("h2").first();
                        if (firstH2.length > 0) {
                            var progressHTML = `
                                <span class="circular-progress-container" id="{$this->animationContainerId}">
                                    <div class="circular-progress" id="{$this->animationContainerId}_progress">
                                        <div class="circular-progress-text" id="{$this->animationContainerId}_text">{$this->refresh}</div>
                                    </div>
                                </span>
                            `;
                            firstH2.append(progressHTML);
                        } else {
                            var progressHTML = `
                                <div id="{$this->animationContainerId}" style="position: relative; width: 60px; height: 60px; margin: 0 auto 10px;">
                                    <div class="circular-progress" id="{$this->animationContainerId}_progress">
                                        <div class="circular-progress-text" id="{$this->animationContainerId}_text">{$this->refresh}</div>
                                    </div>
                                </div>
                            `;
                            jQuery("#{$this->id}").before(progressHTML);
                        }
                        isFirstLoad_{$this->id} = false;
                    }

                    // Démarrage du timer
                    timerInterval_{$this->id} = setInterval(function() {
                        remainingTime_{$this->id}--;
                        updateCircularProgress_{$this->id}();
                        if (remainingTime_{$this->id} <= 0) {
                            clearInterval(timerInterval_{$this->id});
                        }
                    }, 1000);

                    // Prochain rafraîchissement
                    setTimeout(function() {
                        update_{$this->id}();
                    }, 1000 * {$this->refresh});
                }
            });
        }

        // Initialisation
        update_{$this->id}();
        </script>
EOT;
    }
}



class medulla_progressbar extends HtmlElement
{
    private static $scriptIncluded = false;
    /** @var int $value Valeur de la barre de progression (entre 0 et 100). */
    private $value;

    /** @var string $cssClass Nom de la classe CSS pour la barre de progression. */
    protected $cssClass = 'progressbar_med';

    /** @var string $dataValue Valeur de l'attribut data-value. */
    private $dataValue;

    /** @var string $title Valeur de l'attribut title. */
    private $title;

    /**
     * Constructeur de la classe.
     *
     * @param int $value Valeur initiale de la barre de progression (0-100).
     * @param string $dataValue Valeur de l'attribut data-value.
     * @param string $title Valeur de l'attribut title.
     */
    public function __construct($value, $dataValue = "", $title = "")
    {
        parent::__construct();
        // Assure que la valeur reste entre 0 et 100
        $this->value = max(0, min(100, (int)$value));
        $this->dataValue = $dataValue;
        $this->title = $title;
        if (!self::$scriptIncluded) {
            $this->includeScript();
            self::$scriptIncluded = true;
        }
    }

    /**
     * Affiche la barre de progression sous forme de code HTML.
     *
     * @param array $arrParam Paramètres optionnels (non utilisés ici).
     */
    public function display($arrParam = array())
    {
        // echo $this->toString();
        echo $this->my_string();
    }

    /**
     * Retourne une chaîne de caractères représentant la barre de progression.
     *
     * @return string Chaîne de caractères de la barre de progression.
     */
    public function my_string()
    {
        return $this->generateHtml();

    }

    /**
     * Retourne le code HTML de la barre de progression.
     *
     * @return string HTML de la barre de progression.
     */
    public function __toString()
    {
        return $this->generateHtml();
    }

   private function toString() {
        // Retourne une représentation sous forme de chaîne de caractères de l'objet
        return $this->generateHtml();
    }
    /**
     * Génère le code HTML de la barre de progression.
     *
     * @return string HTML de la barre de progression.
     */
    private function generateHtml()
    {
        $titleAttr = !empty($this->title) ? ' title="' . htmlspecialchars($this->title, ENT_QUOTES, 'UTF-8') . '"' : '';
        $dataValueAttr = !empty($this->dataValue) ? ' data-value="' . htmlspecialchars($this->dataValue, ENT_QUOTES, 'UTF-8') . '"' : '';

        return str_replace(array("\r", "\n"), ' ', '<div class="' . $this->cssClass . '">
                    <span class="value_progress"' . $titleAttr . ' style="display: none;"' . $dataValueAttr . '>' . (string)$this->value . '</span>
                </div>');
    }

    private function includeScript() {
        echo <<<EOT
<script type="text/javascript">
    /**
     * Fonction qui renvoie une couleur intermédiaire entre rouge, jaune et vert en fonction d'une valeur de 0 à 100.
     * @param {number} value - Valeur entre 0 et 100.
     * @return {string} - Couleur au format RGB.
     */
    function ensureProgressStyles() {
        if (document.getElementById('medulla-progress-style')) {
            return;
        }
        var css = [
            '.medulla-progress {',
            '  display: block;',
            '  font-size: 12px;',
            '  color: #1f2b3a;',
            '  line-height: 1.4;',
            '  margin: 4px 0;',
            '}',
            '.medulla-progress__track {',
            '  position: relative;',
            '  width: 100%;',
            '  height: 20px;',
            '  background: #e6ecf3;',
            '  border-radius: 8px;',
            '  overflow: hidden;',
            '  border: 1px solid #d2dae3;',
            '}',
            '.medulla-progress__fill {',
            '  position: absolute;',
            '  inset: 0;',
            '  height: 100%;',
            '  border-radius: inherit;',
            '  background: #3ca175;',
            '  transition: width 0.35s ease;',
            '}',
            '.medulla-progress__label {',
            '  position: absolute;',
            '  inset: 0;',
            '  display: flex;',
            '  align-items: center;',
            '  justify-content: center;',
            '  font-weight: 600;',
            '  pointer-events: none;',
            '  transition: color 0.2s ease;',
            '}',
            '.medulla-progress.is-static .medulla-progress__label,',
            '.medulla-progress.is-dynamic .medulla-progress__label { font-size: 12px; }',
            '.medulla-progress__fill.is-low { background: #f28b82; }',
            '.medulla-progress__fill.is-medium { background: #f6bf65; }',
            '.medulla-progress__fill.is-high { background: #3ca175; }',
            '.medulla-progress__fill.is-empty { background: transparent; }',
            '.medulla-progress__value { font-weight: 600; }'
        ].join('\\n');

        var style = document.createElement('style');
        style.id = 'medulla-progress-style';
        style.type = 'text/css';
        style.appendChild(document.createTextNode(css));
        document.head.appendChild(style);
    }

    function getProgressTone(value) {
        if (value <= 0) {
            return {
                className: 'is-empty',
                color: 'transparent',
                textColor: '#1f2b3a',
                textShadow: 'none'
            };
        }
        if (value < 40) {
            return {
                className: 'is-low',
                color: '#f28b82',
                textColor: '#5c1a18',
                textShadow: '0 1px 0 rgba(255,255,255,0.65)'
            };
        }
        if (value < 75) {
            return {
                className: 'is-medium',
                color: '#f6bf65',
                textColor: '#56360b',
                textShadow: '0 1px 0 rgba(255,255,255,0.55)'
            };
        }
        return {
            className: 'is-high',
            color: '#3ca175',
            textColor: '#ffffff',
            textShadow: '0 1px 2px rgba(15,23,42,0.45)'
        };
    }

    function renderProgress(container, options) {
        if (!container.length || container.data('medullaProgressInit')) {
            return;
        }
        var spanChild = container.find('.value_progress').first();
        if (!spanChild.length) {
            return;
        }

        container.data('medullaProgressInit', true);

        var rawValue = parseFloat(spanChild.text());
        if (isNaN(rawValue)) {
            rawValue = 0;
        }

        var clampedValue = Math.max(0, Math.min(100, rawValue));
        var widthValue = clampedValue;
        var labelPrefix = (spanChild.attr('data-value') || '').trim();
        var formatter = options && typeof options.formatValue === 'function'
            ? options.formatValue
            : function (value) { return Math.round(value); };
        var displayValue = formatter(rawValue, clampedValue);
        var labelText = (labelPrefix ? labelPrefix + ' ' : '') + displayValue + '%';
        var title = spanChild.attr('title') || container.attr('title') || '';

        spanChild.remove();
        container.empty();

        container.addClass('medulla-progress');
        if (options && options.variant) {
            container.addClass('is-' + options.variant);
        }

        container.attr({
            role: 'progressbar',
            'aria-valuemin': 0,
            'aria-valuemax': 100,
            'aria-valuenow': Math.round(clampedValue)
        });

        if (title) {
            container.attr('title', title);
        }

        var tone = getProgressTone(clampedValue);
        var track = jQuery('<div class="medulla-progress__track"></div>');
        var fill = jQuery('<div class="medulla-progress__fill"></div>')
            .addClass(tone.className)
            .css('background', tone.color)
            .css('width', widthValue + '%');

        var label = jQuery('<div class="medulla-progress__label"></div>')
            .text(labelText.trim())
            .css({
                color: tone.textColor,
                'text-shadow': tone.textShadow || 'none'
            });

        track.append(fill).append(label);
        container.append(track);
    }

    jQuery(document).ready(function() {
        ensureProgressStyles();

        jQuery(".progressbarstaticvalue_med").each(function() {
            renderProgress(jQuery(this), { variant: 'static' });
        });

        jQuery(".progressbar_med").each(function() {
            renderProgress(jQuery(this), {
                variant: 'dynamic',
                formatValue: function(value) {
                    return Math.round(value);
                }
            });
        });
    });
</script>
EOT;
    }
}

class medulla_progressbar_static extends medulla_progressbar
{
    /**
     * Constructeur de la classe.
     *
     * @param int $value Valeur initiale de la barre de progression (0-100).
     * @param string $dataValue Valeur de l'attribut data-value.
     * @param string $title Valeur de l'attribut title.
     */
    public function __construct($value, $dataValue = "", $title = "")
    {
        parent::__construct($value, $dataValue, $title);
        // Modifie la classe CSS pour la barre de progression statique
        $this->cssClass = 'progressbarstaticvalue_med';
    }
}
?>
