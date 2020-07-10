<?php
/**
 * (c) 2016-2018 Siveo, http://www.siveo.net/
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

/**
 * The Step class is used to get datas issue from the options form, when the action is configured.
 *
 */
class Step {
    /**
     * The label of the step
     *
     * @var string $label
     *
     */
    protected $label;

    /**
     * The action of the step
     *
     * @var string $action
     *
     */
    protected $action;

    /**
     * The options of the step
     *
     * @var array $options
     *
     */
    protected $options = [];

    /**
     * The os of the step
     *
     * @var array $os
     *
     */
    protected $os = [];

    /**
     * Constructor
     *
     * @param array $params Contains all parameters used to define the step
     * @return void
     *
     * - $params['label']
     * - $params['action']
     * - $params['os']
     * - $params['step']
     * - etc.
     */
    public function Step($params)
    {
        $this->label = $params['label'];
        unset($params['label']);			//Extract label

        $this->action = $params['action'];
        unset($params['action']);			//Extract action

        $this->os = $params['os'];
        unset($params['os']);				//Extract os

        $this->options = $params;			//Extract parameters
    }

    /**
     * Get all parameters contained in $params. The label and the action are included but not the os.
     *
     * @param void
     * @return array
     */
    public function getAll()
    {
        $tmp = [];
        $tmp['label'] = $this->label;
        $tmp['action'] = $this->action;
        foreach($this->options as $option=>$value)
        {
            $tmp[$option] = $value;
        }
        return $tmp;
    }

    /**
     * Set the step option in $params
     *
     * @param int $step is the step number used to order the sequence
     * @return void
     */
    public function setOptionStep($step)
    {
        if(is_int($step))
            $this->options['step'] = $step;
    }

    public function setOptionSuccess($step)
    {
    """
     Set the success option in $params

     @deprecated replaced by setOption
     @param int $step is the step number used to order the sequence
     @return void
     """
        if(is_int($step))
            $this->options['succes'] = $step;
    }

    /**
     * Set the gotoapply option in $params
     *
     * @deprecated replaced by setOption
     * @param int $step is the step number used to order the sequence
     * @return void
     */
    public function setOptionGotoapply($step)
    {
        if(is_int($step))
            $this->options['gotoapply'] = $step;
    }

    /**
     * Set the specified option in $params
     *
     * @param string $option is the option to be set
     * @param mixed $value is the new value for the option
     * @return void
     */
    public function setOption($option, $value)
    {
        switch($option)
        {
            case 'succes' :
                if(is_int($value))
                    $this->options['succes'] = $value;
                break;
            case 'error' :
                if(is_int($value))
                    $this->options['error'] = $value;
            case 'step' :
                if(is_int($value))
                    $this->options['step'] = $value;
                break;

            case 'goto' :
                if(is_int($value))
                    $this->options['goto'] = $value;
                break;

            case 'gotoapply' :
                if(is_int($value))
                    $this->options['gotoapply'] = $value;
                break;

            case 'gotosucces' :
                if(is_int($value))
                    $this->options['gotosucces'] = $value;
                break;
            case 'gotoyes' :
                if(is_int($value))
                    $this->options['gotoyes'] = $value;
                break;
            case 'gotono' :
                if(is_int($value))
                    $this->options['gotono'] = $value;
                break;
            case 'gotoopen' :
                if(is_int($value))
                    $this->options['gotoopen'] = $value;
                break;
            case 'gotosave' :
                if(is_int($value))
                    $this->options['gotosave'] = $value;
                break;
            case 'gotocancel' :
                if(is_int($value))
                    $this->options['gotocancel'] = $value;
                break;
            case 'gotoclose' :
                if(is_int($value))
                    $this->options['gotoclose'] = $value;
                break;
            case 'gotodiscard' :
                if(is_int($value))
                    $this->options['gotodiscard'] = $value;
                break;
            case 'gotoreset' :
                if(is_int($value))
                    $this->options['gotoreset'] = $value;
                break;
            case 'gotorestoreDefaults' :
                if(is_int($value))
                    $this->options['gotorestoreDefaults'] = $value;
                break;
            case 'gotoabort' :
                if(is_int($value))
                    $this->options['gotoabort'] = $value;
                break;
            case 'gotoretry' :
                if(is_int($value))
                    $this->options['gotoretry'] = $value;
                break;
            case 'gotoignore' :
                if(is_int($value))
                    $this->options['gotoignore'] = $value;
                break;
            default :
                $this->options[$option] = $value;
                break;
        }
    }

    //Getters mainly used to manipulate the step object from flow object.
    public function os(){return $this->os;}
    public function label(){return $this->label;}
    public function id(){return $this->options['step'];}

}

/**
 * The Flow class is the step controller. It allows to add, remove, update steps and get final JSON
 *
 */
class Flow {
    /**
     * The list of steps for Mac
     *
     * @var array $sequenceMac
     */
    protected $sequenceMac = [];

    /**
     * The list of steps for Linux
     *
     * @var array $sequenceLinux
     */
    protected $sequenceLinux = [];

    /**
     * The list of steps for Windows
     *
     * @var array $sequenceLinux
     */
    protected $sequenceWindows = [];

    /**
     * Add a step class to the good sequence
     * @uses Flow::exists to know if the specified step exists in the workflow
     *
     * @param Step $new		Step to add
     * @return void
     */
    public function add(Step $new)
    {
        foreach($new->os() as $os)
        {

            if($os == "mac" && !$this->exists($new->label(), $os))
            {
                $this->sequenceMac[] = $new;
            }
            if($os == "linux" && !$this->exists($new->label(), $os))
            {
                $this->sequenceLinux[] = $new;
            }
            if($os == "windows" && !$this->exists($new->label(), $os))
            {
                $this->sequenceWindows[] = $new;
            }
        }
    }

    /**
     * Return array which contains the labels of the specified os
     *
     * @param string $os	Os selected
     * @return array 		The array contains all the label of the specified os sequence
     */
    public function labelList($os)
    {
        $tmp = [];
        $sequence = 'sequence'.ucfirst($os);
        foreach($this->$sequence as $step)
        {
            $tmp[] = $step->label();
        }
        return $tmp;
    }

    /**
     * Remove the step which contains the specified label from the sequence specified
     *
     * @uses Flow::exists
     *
     * @param string $label		Label searched
     * @param string $os		Os selected
     * @return void
     */
    public function remove($label, $os)
    {
        //locate the label in the os sequence specified
        $sequence = 'sequence'.ucfirst($os);
        $tmp = [];
        if($this->exists($label, $os))
        {
            foreach($this->$sequence as $key=>$step)
            {
                if($step->label() != $label)
                {
                    $tmp[] = $step;
                }
            }
        }

        $this->$sequence = $tmp;
        unset($tmp);
    }

    /**
     * Get the position of the step specified by its os and label
     *
     * @param string $label 	label researched
     * @param string $os 	select the sequence of the specified os
     * @return int $id 		the position in the array of the step
     * @return -1	 		if the label is not founded
     */
    public function stepId($label, $os)
    {
        $sequence = 'sequence'.ucfirst($os);

        //Iterator
        reset($this->$sequence);
        $cursor = 0;
        $current = current($this->$sequence);

        while ($current && $current->label() != $label)
        {
            $current = next($this->$sequence);
            $cursor++;
        }


        if($cursor != sizeof($this->$sequence))
            return $cursor;
        else
            return $sizeof($this->$sequence);
    }

    /**
     * Search the specified label in the specified os sequence
     *
     * @param string $label		label researched
     * @param string $os		select the sequence of the specified os
     * @return bool 			true if exists else false
     */
    function exists($label, $os)
    {
        $sequence = 'sequence'.ucfirst($os);
        $exists = false;
        foreach($this->$sequence as $key=>$element)
        {
            if($label == $element->label())
            {
                $exists = true;
            }
        }
        return $exists;
    }

    /**
     * Modify step order in the flow
     *
     * @param string $listOfLabelsByOs 	stringified json of the labelList
     * @return void
     */
    public function setOrder($listOfLabelsByOs)
    {
        $labelsByOs = json_decode($listOfLabelsByOs);

        $sequenceMac = $this->sequenceMac;
        $sequenceLinux = $this->sequenceLinux;
        $sequenceWindows = $this->sequenceWindows;
        $tmpMac = [];
        $tmpLinux = [];
        $tmpWindows = [];

        $tmp = null;
        // Extrait de $label $os=>[entry]
        foreach($labelsByOs as $os=>$entry)
        {
            $sequence = 'sequence'.ucfirst($os);
            $tmpSeq = 'tmp'.ucfirst($os);

            foreach($entry as $step=>$label)
            {
                foreach($$sequence as $row)
                {
                    if($row->label() == $label)
                    {
                        // echo $os.' '.$step.' '.$label.'<br />';
                        array_push($$tmpSeq, $row);
                    }
                }
            }
            $this->$sequence = $$tmpSeq;
        }
    }

    /**
     * Create the final JSON and return it
     *
     * @param void
     * @return string Contains the stringified json
     */
    public function json()
    {
        $tmp = [];
        $tmp = ['mac'=>array(), 'linux'=>array(),'windows'=>array()];

        $seq = ['mac','linux','windows'];

        //each os
        foreach($seq as $os)
        {
            $sequence = "sequence".ucfirst($os);
            foreach($this->$sequence as $id=>$step)
            {
                $step->setOption('step',$id);

                reset($this->$sequence);
                $current = current($this->$sequence);
                while($current->label() != $step->label())
                    $current = next($this->$sequence);

                if($next = next($this->$sequence))
                {}//$next = step if exists, else $next = false

                $optionList = ['succes','error','goto','gotoyes','gotono','gotoopen','gotosave','gotocancel','gotoclose','gotodiscard','gotoreset','gotorestoreDefaults','gotoabort','gotoretry','gotoignore', 'gotoapply'];

                //Each "goto" options
                foreach($optionList as $option)
                {
                    if(array_key_exists($option.'-label',$step->getAll()))
                    {
                        if($step->getAll()[$option.'-label'] == 'NEXT' && $step != end($this->$sequence))
                            $step->setOption($option, $id+1);

                        else
                        {
                            $nextLabel = $step->getAll()[$option.'-label'];
                            $step->setOption($option, $this->stepId($nextLabel,$os));
                        }
                    }
                }

                array_push($tmp[$os], $step->getAll());
            }

        }
        $tmp['mac'] = ['sequence'=>$tmp['mac']];
        $tmp['linux'] = ['sequence'=>$tmp['linux']];
        $tmp['win'] = ['sequence'=>$tmp['windows']];
        unset($tmp['windows']);
        return json_encode($tmp);
    }
}

/**
 * arrayCleaner is used to clean posted values
 *
 * @param array $parameters
 * @return array $parameters 	with the modifications
 */
function arrayCleaner($parameters)
{
    $os = [];
    if (isset($parameters['os'])) {
        $os[] = 'linux';
        unset($parameters['os']);
    }

    unset($parameters['firstStep']);
    $parameters['os'] = $os;

    return $parameters;
}

class TextareaTplArray extends AbstractTpl{
  /**
  * The class TextareaTplArray works in the same way as TextareaTpl but the
  * parameters are given in a array, and not anymore separately.
  *
  * All the parameters given are send as html parameters to the textarea tag,
  * excepted for the value. The value is treated separately
  *
  * protected $params : this array contains all the parameters given to the tag
  * protected $value : string contains the displayed value in the textarea.
  */
  protected $params = array();
  protected $value;
  public function TextareaTplArray($params = [])
  {
    if(is_array($params))
    {
      // Some tests to be sure to have a name and / or id option
      if(array_key_exists("name", $params) && !array_key_exists("id", $params))
      {
        $params["id"] = $params["name"];
      }
      if(!array_key_exists("name", $params) && array_key_exists("id", $params))
      {
        $params["name"] = $params["id"];
      }

      // Set cols and rows size by default if not precised
      if(!array_key_exists("rows", $params))
      {
        $params["rows"] = 3;
      }
      if(!array_key_exists("cols", $params))
      {
        $params["cols"] = 21;
      }

      // The value displayed
      if(array_key_exists("value", $params))
      {
        $this->value = $params['value'];
        unset($params['value']);
      }
      else {
        $this->value="";
      }
      $this->params = $params;
    }
  }

  // The function called when the page is displayed
  public function display($arrParam = array()) {
      $stringToDisplay = '<textarea ';
      foreach($this->params as $opt=>$value)
      {
        $stringToDisplay .= $opt.'="'.$value.'" ';
      }
      $stringToDisplay .= '>'.$this->value.'</textarea>';
      echo $stringToDisplay;
  }
}

class AsciiInputTpl extends InputTpl {
  /**
  * AsciiInputTpl generates an input text which specifies a regex. The regex excludes non ascii chars.
  * If the user try to send the form with non ascii chars (I.E. like accents), the focus is set on the
  * concerned field.
  *
  * Param :
  *   $name : string which corresponding to the name of the input and the GET/POST data of the form
  */

  function AsciiInputTpl($name) {
    $this->InputTpl($name, '/^[A-Za-z0-9\.\-\!\?\ \.\#%$&@\*\+_\/]*$/');
  }
}
?>
