<?php

class FormTpl {
    private $formId;
    private $formClass;
    private $action;
    private $method;
    private $elements = [];

    public function __construct($formId, $formClass, $action, $method = 'post') {
        $this->formId = $formId;
        $this->formClass = $formClass;
        $this->action = $action;
        $this->method = $method;
    }

    public function addElement($element) {
        $this->elements[] = $element;
    }

    public function display() {
        echo '<form id="' . $this->formId . '" class="' . $this->formClass . '" method="' . $this->method . '" action="' . $this->action . '">';
        foreach ($this->elements as $element) {
            $element->display();
        }
        echo '</form>';
    }

}

class AsciiInputTpl extends InputTpl
{
    /**
     * AsciiInputTpl generates an input text which specifies a regex. The regex excludes non ascii chars.
     * If the user try to send the form with non ascii chars (I.E. like accents), the focus is set on the
     * concerned field.
     *
     * Param :
     *   $name : string which corresponding to the name of the input and the GET/POST data of the form
     */

    function __construct($name)
    {
        parent::__construct($name, '/^[A-Za-z0-9\.\-\!\?\ \.\#%$&@\*\+_\/]*$/');
    }
}

?>