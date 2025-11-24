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

?>