<?php
/**
 * (c) 2018 Siveo, http://siveo.net
 *
 * This file is part of Management Console (MMC).
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
 * Modify the specified if it is already used.
 *
 * @param $name
 * @return mixed|string
 */
function rename_profile($name)
{
    // strips some special characters
    $name = str_replace(['@', '#', '&', '"', "'", '(', '§', '!', ')', '-', '\[', '\]', '\{', '\}', '°', '/', '|', '\\', '<', '>'], '_', $_POST['name']);
    //turns the name to lowercase
    $name = strtolower($name);

    while(in_array($name, xmlrpc_get_profiles_name_list()))
    {
        // if the profile already exists, then the profile is renamed.
        $name .= '_';
    }
    return $name;

}

/**
 * Generate the formated string for the tree structure and save it in $result
 *
 * @param array $array
 * @param &$result the reference which will contains the result of the function.
 */

function recursiveArrayToList(Array $array = array(), &$result, &$count)
{

    if(isset($array['child']))
    {
        $name = $array['name'];

        // The limit set the limit of displayed characters for each rows in the tree
        $limit = 15;
        if(isset($array['name']) && $array['name'] != "")
            if(strlen($name) > $limit)
            {
                $count +=1;
                $result.= '<li title="'.$name.'" data-id="j1_'.$count.'" data-root="'.$array['path'].'">'.substr($name,0,$limit).'...';
            }
            else
            {
                $count +=1;
                $result.= '<li data-id="j1_'.$count.'" data-root="'.$array['path'].'">'.$name;
            }
        recursiveArrayToList($array['child'], $result, $count);
        $result.= '</li>';
    }
    else
    {
        if(count($array)> 0)
        {
            $result.= '<ul>';
            foreach($array as $element)
            {
                recursiveArrayToList($element,$result, $count);
            }
            $result.= '</ul>';
        }

    }

}

?>
