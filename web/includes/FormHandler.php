<?php

/**
 * (c) 2011 Mandriva, http://www.mandriva.com
 *
 * $Id$
 *
 * This file is part of Mandriva Management Console (MMC).
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
 * along with MMC.  If not, see <http://www.gnu.org/licenses/>.
 */

class FormHandler {

    var $post_data;
    var $data;
    var $arr;

    function FormHandler($name, $data) {
        //echo "<pre>";
        //print_r($data);
        //echo '</pre>';
        $this->name = $name;
        $this->data = array();

        if (!$data) {
            $this->isError(false);
        }

        // get the old posted data in case of
        // error
        if(isset($_SESSION[$this->name])) {
            $oldFH = unserialize($_SESSION[$this->name]);
            $this->post_data = $oldFH->post_data;
            // update with new data
            foreach($data as $name => $value) {
                if(preg_match('/^old_/', $name) == 0)
                    $this->post_data[$name] = $value;
            }
        }
        else {
            // the raw $_POST data
            $this->post_data = $data;
        }
        // the LDAP array
        $this->arr = array();
        $this->sanitize();
        //echo "<pre>";
        //print_r($this->data);
        //echo '</pre>';
    }

    /* Create array with updated fields from $_POST
       If the field_name != old_field_name store
       the new value in $this->data */
    function sanitize() {
        // get all updated fields
        foreach($this->post_data as $name => $value) {

            // handle checkboxes and arrays widgets
            if(preg_match('/^old_/', $name) > 0 and !isset($this->post_data[substr($name, 4)])) {
                if($value == "on") {
                    $this->data[substr($name, 4)] = "off";
                }
                else if (is_array($value)) {
                    $this->data[substr($name, 4)] = array();
                }
            }

            if(isset($this->post_data['old_'.$name])) {
                if($this->post_data['old_'.$name] != $this->post_data[$name]) {
                    // remove empty strings from array
                    if(is_array($value))
                        $value = array_filter($value);
                    $this->data[$name] = $value;
                }
            }
        }
    }

    function isError($state) {
        if ($state) {
            $_SESSION[$this->name] = serialize($this);
        }
        else {
            if (isset($_SESSION[$this->name]))
                unset($_SESSION[$this->name]);
        }
    }

    /* Check if field has changed */
    function isUpdated($field) {
        return isset($this->data[$field]);
    }

    /* Get updated value */
    function getValue($field) {
        if(isset($this->data[$field]))
            return $this->data[$field];
        else
            return false;
    }

/**
 * \brief       Calcule la dureté d'un mot de passe
 * \details     pour chaque caractere on attribut une valeur
 *                 1 point minuscule
 *                 2 points Majuscule
 *                 3 points chiffre
 *                 5 points autres caracteres
 *               add un bonus pour chaque ensemble utilise
 *               on Calcul du coefficient points/longueur
 *               on Calcul du coefficient de la diversité des types de caractères...
 *               on Multiplication le coefficient de diversité avec la longueur de la chaine
 
 * \param     $mdp  le mot de passe passé en paramètre
 * \return    Un \e Entier :  indice de durete du mot de passe
 */
    function testpassword($mdp)     {
        // On récupère la longueur du mot de passe
        $longueur = strlen($mdp);
        $point=0;$point_min=0;$point_maj=0;$point_caracteres=0;$point_chiffre=0;
        $testdiversification=1;
        $testdiversificationautre=0;
        $testdiversificationmin=0;
        $testdiversificationmaj=0;
        $testdiversificationchif=0;
        // On fait une boucle pour lire chaque lettre
        for($i = 0; $i < $longueur; $i++)       {
            // On sélectionne une à une chaque lettre
            // $i étant à 0 lors du premier passage de la boucle
            $lettre = $mdp[$i];
            if ($lettre>='a' && $lettre<='z'){
                    // On ajoute 1 point pour une minuscule
                    $point = $point + 1;
                    // On rajoute le bonus pour une minuscule
                    $point_min = 1;
                    $testdiversificationmin=1;
            }
            else if ($lettre>='A' && $lettre <='Z'){
                    // On ajoute 2 points pour une majuscule
                    $point = $point + 2;
                    // On rajoute le bonus pour une majuscule
                    $point_maj = 2;
                    $testdiversificationmaj=1;
            }
            else if ($lettre>='0' && $lettre<='9'){
                    // On ajoute 3 points pour un chiffre
                    $point = $point + 3;
                    // On rajoute le bonus pour un chiffre
                    $point_chiffre = 3;
                    $testdiversificationchif=1;
            }
            else {
                    // On ajoute 5 points pour un caractère autre
                    $point = $point + 5;
                    // On rajoute le bonus pour un caractère autre
                    $point_caracteres = 5;
                    $testdiversificationautre=1;
            }
        }
        // Calcul du coefficient points/longueur
        $etape1 = $point / $longueur;
        // Calcul du coefficient de la diversité des types de caractères...
        $etape2 = $point_min + $point_maj + $point_chiffre + $point_caracteres;
        // Multiplication du coefficient de diversité avec celui de la longueur
        $resultat = $etape1 * $etape2;
        // Multiplication du résultat par la longueur de la chaîne
        $final = $resultat * $longueur;
        $test = 5-($testdiversificationautre + $testdiversificationchif + $testdiversificationmaj + $testdiversificationmin) ;
        if($test != 1 ) $test=$test*2;
        $final = $final/$test;
        return intval($final);
    }

    /* Get all updated values */
    function getValues() {
        return $this->data;
    }

    /* Update value */
    function setValue($field, $value) {
        $this->data[$field] = $value;
    }

    /* Remove value */
    function delValue($field) {
        unset($this->data[$field]);
    }

    /* Get value from original $_POST array */
    function getPostValue($field) {
        if(isset($this->post_data[$field]) and $this->post_data[$field] != "")
            return $this->post_data[$field];
        else
            return false;
    }

    /* Get all values from original $_POST array */
    function getPostValues() {
        return $this->post_data;
    }

    /* Update value in original $_POST array */
    function setPostValue($field, $value) {
        $this->post_data[$field] = $value;
    }

    /* Remove value from original $_POST array */
    function delPostValue($field) {
        unset($this->post_data[$field]);
    }

    function setArr($arr) {
        $this->arr = $arr;
    }

    /*
     * Get value from $_POST or from the user LDAP detailled array
     * This is usefull in case of error in the user edit form
     * So we don't lost the user input
     * POST value is returned before the LDAP value (wanted/actual)
     */
    function getArrayOrPostValue($field, $type = "string") {

        if ($type == "array") {
            $value = array('');
            if($this->getPostValue($field)) {
                $value = $this->getPostValue($field);
            }
            else if(isset($this->arr[$field])) {
                $value = $this->arr[$field];
            }
        }
        else {
            $value = "";
            if($this->getPostValue($field)) {
                $value = $this->getPostValue($field);
            }
            else if(isset($this->arr[$field][0])) {
                $value = $this->arr[$field][0];
            }
        }

        return $value;
    }

}

?>
