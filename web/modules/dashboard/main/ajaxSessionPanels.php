<?php
echo session_start();

if(isset($_GET['widget'], $_GET['toggled']))
{
  $widget = htmlentities($_GET['widget']);
  $toggled = htmlentities($_GET['toggled']);

  $_SESSION['user']['widgets'][$widget] = $toggled;
}
