<?php
$preprocess = [
    new \Middlewares\DebugMiddleware(),
];

foreach($preprocess as $process){
    $process->execute();
}
?>
