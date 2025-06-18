<?php
/**
 * This page handle the rendering of the bootmenu when no param are given
 */
if(defined("DEBUG") && DEBUG == true){?>
@render(partials.header)
<pre>
<code>
@render(partials.Default.noParamBody)
</code>
</pre>
@render(partials.footer)
<?php }
else{ ?>
@render(partials.Default.noParamBody)

<?php }?>
