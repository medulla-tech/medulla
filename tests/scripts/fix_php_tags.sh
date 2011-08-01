#!/bin/bash
#
# Replace all php tags with the long form <?php ... ?>
#
for file in `find -name '*.php'`; do
    sed -i -e 's/<?=/<?php echo /g; s/<? /<?php /g; s/\S?>/ ?>/g' $file
done