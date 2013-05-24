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

/**
 * Singleton objet, register all main mmc data
 */
class MMCApp {


   var $_modules;
   var $_styleobj;
   /**
    * Constructor
    * private
    */
   function MMCApp() {
        $this->_modules = array();
        $this->_styleobj = new StyleGenerator();
   }

   /**
    * getInstance (return uniq object)
    * fake static element (due to php4 bad object integration) with
    * a global value
    */
   public static function &getInstance() {

      if (!isset($GLOBALS["__INSTANCE_MMC_APP__"])) {
         $GLOBALS["__INSTANCE_MMC_APP__"] = new MMCApp();
      }

      return $GLOBALS["__INSTANCE_MMC_APP__"];

   }

   /**
    * @brief this function return uniq style object
    * this is used to add CSS in an uniq part of the page
    * instead of flooding fragmented css in whole page.
    * styleobject id display at the end of the page.
    * @return unique style object
    */
   function &getStyle() {
       return $this->_styleobj;
   }

   /**
    * add a module into MMCApp
    * @param mod Module Object to add
    */
   function addModule($mod) {
       $this->_modules[$mod->getName()]= $mod;
   }

   /**
    * @brief return all modules list
    * @return an associeted array like
            'base' => 'base object',
            'samba'=> 'samba object'
    */
   function &getModules() {
       return $this->_modules;
   }

   /**
    * @brief return a specific module
    * @param $modname name
    * @return Module Object
    * @warning if Module name do not exist... unknown value is return
    */
   function &getModule($modname) {
        return $this->_modules[$modname];
   }

   /**
    * function called at very end of each page (css creation, etc...)
    */
   function render() {
        $this->_styleobj->render();
   }

   /**
    * This function process all Modules
    * Create old array for retro compatibility etc...
    */
   function process() {
        foreach ($this->getModules() as $module) {
            $module->process();
        }
   }
}

/**
 * Object dedicated to style creation
 */
class StyleGenerator {
    var $_csslines;


    /**
     * Default constructor
     */
    function StyleGenerator() {
        $this->_csslines = array();
    }

    /**
     * add a css line into StyleGenerator
     * @param $css cssline to add
     * @warning "\n" value at end of line is not an obligation
     */
    function addCSS($css) {
        $this->_csslines[] = $css;
    }

    /**
     * display all css line on same part of code
     */
    function render() {
        print "<style type=\"text/css\">\n";
        foreach ($this->_csslines as $line) {
            print "$line\n";
        }
        print "</style>\n";
    }
}


class SubModule {
    var $_name; /**< submodule name */
    var $_desc; /**< submodule description */
    var $_pages; /**< pages array */
    var $_defaultpage; /**< default page. ex: 'base/user/index' */
    var $_visibility; /**< default is visible */
    var $_img; /**< img, help generation of css */
    var $_imgsize; /**< tab size */
    var $_module; /**< Module parent */
    var $_parentname; /**< Module parent name */
    var $_alias; /**< alias icon if submod not appear */
    var $_priority; /**< specify order to show submod */


    function SubModule($name,$desc = "") {
        $this->_name = $name;
        $this->setDescription($desc);
        $this->_visibility = True;
        $this->_defaultpage = Null;
        $this->_img = Null;
        $this->_imgsize = 70;
        $this->_parentname = Null;
        $this->_alias = Null;
        $this->_priority = 50; //default priority
    }

    /**
     * Set Module that owns this SubModule
     */ 
    function setModule($module) {
        $this->_module = $module;
    }    

    /**
     * provide alias to submod
     * ex: when you select "machines", shares is selected
     * @param $alias alias name. Correspond to an existing submodule name.
     */
    function setAlias($alias) {
        $this->_alias = $alias;
    }

    /**
     * @brief set image for navbar
     * @param $img image short path
     * if you specify 'img/foo/bar'
     * 3 files must exist
     * img/foo/bar.png for normal status
     * img/foo/bar_hl.png for highlight status
     * img/foo/bar_select.png for selected status
     */
    function setImg($img) {
        $this->_img =$img;
    }

    /**
     * specify tab size (usually used for long icons or
     * long text behind icons)
     * @param $int integer. Default size is 70
     */
    function setImgSize($int) {
        $this->_imgsize = $int;
    }

    function getName() {
        return $this->_name;
    }

    function addPage($page) {
        $this->_pages[$page->_action] = $page;
    }

    function getPage($action) {
        return $this->_pages[$action];
    }

    function getPages() {
        return $this->_pages;
    }

    function hasVisible() {
        foreach ($this->_pages as $page) {
            if ($page->isVisible())
                return true;
        }
        return false;
    }

    function setDefaultPage($page) {
        $this->_defaultpage = $page;
    }

    function setDescription($desc) {
        $this->_desc = $desc;
    }

    function getDescription() {
        return $this->_desc;
    }

    function setVisibility($bool) {
        $this->_visibility = $bool;
    }

    function getPriority() {
        return $this->_priority;
    }

    function setPriority($prio) {
         $this->_priority = $prio;
    }

    /**
     * this function provide compatibility with old ACL,
     * infoPackage.inc.php system
     * generate css for all subproc
     */
    function process($module) {
        foreach ($this->_pages as $page) {
            $page->process($module,$this->getName());
        }
        $MMC =&MMCApp::getInstance();

        if (empty($_GET['submod'])) {
            $selected = False;
        } else {
            $selected = ($_GET['submod'] == $this->getName());
        }

        if ($this->_visibility!=True&&$selected) {
            if ($this->_alias!=Null) {

                $tmp = $_GET["submod"];
                $_GET["submod"] = $this->_alias; //fake url
                $parent = &$MMC->getModule($this->_parentname);
                $submod = &$parent->getSubmod($this->_alias);
                $submod->process($module);

                $_GET["submod"] = $tmp;
                return;
            }
        }
        if ($this->_img!=Null) {


            if (!$selected) {
                $css = '#navbar ul li#navbar'.$this->getName().' {
                    width: '.$this->_imgsize.'px;
                }
                #navbar ul li#navbar'.$this->getName().' a {
                    background: url("'.$this->_img.'.png") no-repeat transparent;
                    background-position: 50% 10px;
                }
                #navbar ul li#navbar'.$this->getName().' a:hover {
                    background: url("'.$this->_img.'_hl.png") no-repeat transparent;
                    background-position: 50% 10px;
                }';
            } else {
                $css = '#navbar ul li#navbar'.$this->getName().' {
                    width: '.$this->_imgsize.'px;
                }
                #navbar ul li#navbar'.$this->getName().' a {
                    background: url("'.$this->_img.'_select.png") no-repeat white;
                    border-left: 1px solid #B2B2B2;
                    border-right: 1px solid #B2B2B2;
                    color: #EE5010;
                    background-position: 50% 8px;
                }';
            }

            $style = &$MMC->getStyle();
            $style->addCSS($css);
        }

    }

    /**
     * Add the submodule icon and the URL link to the top navigation bar
     */ 
    function generateNavBar() {
        if (($this->_visibility == False)||(!hasCorrectModuleAcl($this->_parentname))) {
            return;
        }
        list($module,$submod,$action) = split('/',$this->_defaultpage,3);
        /*
           If the user has no right to access the default page, try to find
           another page.
        */
        if (!hasCorrectAcl($module, $submod, $action)) {
            $found = False;
            foreach($this->getPages() as $page) {
                if (($page->isVisible()) && (hasCorrectAcl($module, $submod, $page->getAction()))) {
                    $found = True;
                    $action = $page->getAction();
                    break;
                }
            }
            /* No page found, so don't display the submodule icon */
            if (!$found) return;
        }
        global $root;
        print "<li id=\"navbar".$this->getName()."\"><a href=\"".$root."main.php?module=$module&amp;submod=$submod&amp;action=$action\">\n";
        print $this->_desc."</a></li>\n";
    }
}

class ExpertSubModule extends SubModule {
    function generateNavBar() {
        if (isExpertMode()) {
            parent::generateNavBar();
        }

    }




}

/**
 * define Modules
 */
class Module {
    var $_name; /**< module name */
    var $_version;
    var $_apiversion;
    var $_revision;
    var $_submod;
    var $_acl;
    var $_priority;


    function Module($name) {
        $this->_name = $name;
        $this->_pages = array();
        $this->_submod = array();
        $this->_priority = 50;
    }

    function __toString() {
        return "default module";
    }


    /**
     * global setter/getter section
     */
    /**
     * get module name
     */
    function getName() {
        return $this->_name;
    }
    /**
     * set revision
     */
    function setRevision($rev) {
        // STAY FOR COMPATIBILITY REASON
        global $__revision;
	$tmp = split(" ", $rev);
	if (count($tmp)>1)
	  $rev = $tmp[1];
	else
	  $rev = 0;
        $__revision[$this->getName()]=$rev;

        $this->_revision = $rev;
    }

    /**
     * set version
     */
    function setVersion($ver) {
        // STAY FOR COMPATIBILITY REASON
        global $__version;
        $__version[$this->getName()]=$ver;

        $this->_version = $ver;
    }

    /**
     * set version api
     */
    function setAPIVersion($ver) {
        // STAY FOR COMPATIBILITY REASON
        global $__apiversion;
        $__apiversion[$this->getName()]=$ver;

        $this->_apiversion = $ver;
    }

    /**
     * get revision number
     */
    function getRevision() {
        return $this->_revision;
    }

    /**
     * get version number
     */
    function getVersion() {
        return $this->_version;
    }

    /**
     * get api version number
     */
    function getAPIVersion() {
        return $this->_apiversion;
    }

    function addACL($aclname,$description) {
        //for compatibility
        global $aclArray;
        $aclArray[$this->getName()][$aclname] = $description;

        $this->_acl[$aclname] = $description;
    }

    function addSubmod($sub) {
        $sub->_parentname = $this->getName();
        $this->_submod[$sub->getName()] = &$sub;
    }

    function &getSubmod($subname) {
        return $this->_submod[$subname];
    }

    function &getSubmodules() {
        return $this->_submod;
    }

    function hasVisible() {
        foreach ($this->_submod as $submod) {
            if ($submod->hasVisible())
                return true;
        }
        return false;
    }

    function getPriority() {
        return $this->_priority;
    }

    function setPriority($prio) {
         $this->_priority = $prio;
    }


   function process() {
        foreach ($this->_submod as $submod) {
            if ($submod)
                $submod->process($this->getName());
        }
   }

   function setDescription($desc) {
       $this->_desc = $desc;
   }

   function getDescription() {
     $desc = $this->_desc;
     if (!$desc) {
        return $this->getName();
     }
     return $desc;
   }

}

/**
 * Page declaration
 */
class Page {
    var $_module;
    var $_submod;
    var $_action;

    var $_desc;
    var $_options;
    var $_file;

    function Page($action,$desc = "") {
        $this->_action = $action;
        $this->_noheader = 0;
        $this->_tab = array();
        $this->setDescription($desc);
        $this->setFile();
        $this->_options["visible"] = True;
        $this->_options["noHeader"] = False;
        $this->_options["AJAX"] = False;
        $this->_options["noACL"] = False;	
    }

    /**
     * Set Module that owns this page
     */ 
    function setModule($module) {
        $this->_module = $module;
    }
    
    /**
     * Set SubModule that owns this page
     */ 
    function setSubModule($submod) {
        $this->_submod = $submod;
    }

    function setDescription($desc) {
        $this->_desc = $desc;
    }

    function getDescription() {
        return $this->_desc;
    }

    function getOptions() {
        return $this->_options;
    }

    /**
     * Return true if the current user has access right to this page
     */
    function hasAccess($module, $submod) {
        return ($_SESSION["login"]=="root")
            || ($this->_options["noACL"])
            || isset($_SESSION["acl"][$module->getName()][$submod->getName()][$this->_action]["right"]);
    }
        
    /**
     * Return true if the current user can access this page, and the page
       shortcut can be displayed on the home page
     */
    function hasAccessAndVisible($module, $sudmod) {
        return $this->isVisible() && $this->hasAccess($module, $sudmod);
    }

    /**
     * Return true if the page shortcut can be displayed on the home page
     */
    function isVisible() {
        $ret = true;
        if (isset($this->_options['visible'])) $ret = $this->_options['visible'];
        return $ret && $this->inCurrentMode();
    }

    /**
     * Return true if the page can be displayed in the current mode
     */
    function inCurrentMode() {
        if (isset($this->_options["expert"])) $ret = ($this->_options["expert"]) && isExpertMode();
        else $ret = true;
        return $ret;
    }

    function getAction() {
        return $this->_action;
    }

    /**
     *  @param options: array can contain "noHeader", "AJAX", "noACL"
     * ex  $options = array("noHeader" => True, "noACL" => True)
     * AJAX implicititely define  noHeader => True and noACL => true (AJAX reply cannot contain header)
     *
     * default: all options set to "False"
     */
    function setFile($file = False,$options = array()) {
        $this->_file = $file;
        $this->setOptions($options);
    }

    /**
     * @see setFile
     * @param $options same as describe in setFile member
     */
    function setOptions($options = array()) {
        foreach($options as $key => $value) {	  
            $this->_options[$key] = $value;
        }
    }

    function addTab($tab) {
        $this->_tab[] = $tab;
    }

    /**
     * function for compatibility
     * FIXME: still needed ?
     */
    function process($module, $submod) {
        global $descArray;
        global $noheaderArray;
        global $redirAjaxArray;
        global $redirArray;
        global $noAclArray;
        global $tabAclArray;
        global $noAclTabArray;
        global $tabDescArray;

        $descArray[$module][$submod][$this->_action] = $this->_desc;

        $file = $this->_file;
        $options = $this->_options;

        if ($file == False) { //if we not set a file
            $file = 'modules/'.$module.'/'.$submod.'/'.$this->_action.'.php';
        }

        if ($options["noHeader"] == True) {
            $noheaderArray[$module][$submod][$this->_action] = 1;
        }

        if ($options["AJAX"] == True) {
            $noheaderArray[$module][$submod][$this->_action] = 1;
            $redirAjaxArray[$module][$submod][$this->_action] = $file;
            unset($redirArray[$module][$submod][$this->_action]);
        } else {
            $redirArray[$module][$submod][$this->_action] = $file;
        }

        if ($options["noACL"] == True || $options["AJAX"] == True) {
            $noAclArray[$module][$submod][$this->_action] = 1;
        }

        foreach($this->_tab as $tab) {
            $tabAclArray[$module][$submod][$this->_action][$tab->getName()] = 1;
            $tabDescArray[$module][$submod][$this->_action][$tab->getName()] = $tab->getDescription();
            if ($tab->_options["noACL"]) {
                $noAclTabArray[join("/", array($module, $submod, $this->_action, $tab->getName()))] = 1;
            }
        }
    }

}

/**
 * Class to declare a tab inside a page
 */
class Tab {

    var $_name;
    var $_desc;

    function Tab($name, $description) {
        $this->_name = $name;
        $this->_desc = $description;
        $this->_options["noACL"] = False;	
    }

    function getName() {
        return $this->_name;
    }

    function getDescription() {
        return $this->_desc;
    }

    /**
     * @see setFile
     * @param $options same as describe in setFile member
     */
    function setOptions($options = array()) {
        foreach($options as $key => $value) {	  
            $this->_options[$key] = $value;
        }
    }
}
?>
