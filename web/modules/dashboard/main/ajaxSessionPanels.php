<?php
if (($_SERVER['REQUEST_METHOD'] ?? '') !== 'POST') {
  http_response_code(405);
  exit;
}

$sessionStarted = session_start();
verifyCSRFToken($_POST);
echo $sessionStarted;

if(isset($_POST['widget'], $_POST['toggled']))
{
  $widget = htmlentities($_POST['widget']);
  $toggled = htmlentities($_POST['toggled']);

  $_SESSION['user']['widgets'][$widget] = $toggled;
}
