<?php

class RenderedImage extends HtmlElement {

    function RenderedImage($url, $alt = '', $style = '') {
        $this->url = $url;
        $this->alt = $alt;
        $this->style = $style;
    }

    function display() {
        print '<img src="' . $this->url . '" alt="'.$this->alt.'" style="'.$this->style.'"/>';
    }
}

class RenderedLink extends HtmlElement {
    function RenderedLink($link, $content) {
        $this->link = $link;
        $this->content = $content;
    }

    function display() {
        print '<a href="'.$this->link.'">'.$this->content.'</a>';
    }
}

?>

