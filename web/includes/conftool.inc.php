<?php
/**
 * (c) 2004-2006 Linbox / Free&ALter Soft, http://linbox.com
 *
 * $Id$
 *
 * This file is part of LMC.
 *
 * LMC is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * LMC is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with LMC; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
 */
?>
<?php
/* $Id$ */


/**
 * get param from samba.conf file 
 * /!\ deprecated for future use
 */

function dump_conf()
{
  global $conf;

  $cf = fopen("/etc/linbox/webface/samba/samba.conf", "w");  

  if ($cf === false)
    {
      return false;
    }

  foreach ($conf as $key => $val)
    {
      fwrite($cf, "[".$key."]\n");

      if (($key == "allow") || ($key == "deny"))
	{
	  if (is_array($val["user"]))
            {
	      foreach ($val["user"] as $user)
	        {
	          fwrite($cf, $user."\n");
	        }
             }

	  if (isset($val["group"]))
	    {
	      foreach($val["group"] as $group)
                {
		  fwrite($cf, "group = ".$group."\n");
	        }
	     }
	}
      else
	{
	  foreach ($val as $kkey => $vval)
	    {
	      fwrite($cf, $kkey." = ".$vval."\n");
	    }
	}
      fwrite($cf, "\n");
    }

  fclose($cf);

  return true;
}

/**
 * write the global $conf info a file
 * /!\ deprecated for future use
 */
function dump_conf_php()
{
  global $conf;

  $phpcf = fopen("/etc/linbox/webface/samba/samba.inc.php", "w");

  if ($phpcf === false)
    {
      return false;
    }

  fwrite($phpcf, "<?php\n");
  fwrite($phpcf, "\$conf = array(\n"); // start of configuration array
  
  $c = count($conf);
  foreach ($conf as $sect => $dict)
    {
      $cc = count($dict);
      fwrite($phpcf, "  \"".$sect."\" => array("."\n"); // start of section array
      foreach ($dict as $key => $val)
	{
	  if (is_array($val))
	    {
	      $ccc = count($val);
	      fwrite($phpcf, "    \"".$key."\" => array(\n"); // start of value array
	      foreach ($val as $vval)
		{
		  fwrite($phpcf, "      \"".$vval."\"");
		  
		  if (--$ccc == 0)
		    {
		      fwrite($phpcf, "\n");
		    }
		  else
		    {
		      fwrite($phpcf, ",\n");
		    }
		}
	      
	      fwrite($phpcf, "    )"); // end of value array
	    }
	  else
	    {
	      fwrite($phpcf, "    \"".$key."\" => \"".$val."\"");
	    }
	  
	  if (--$cc == 0)
	    {
	      fwrite($phpcf, "\n");
	    }
	  else
	    {
	      fwrite($phpcf, ",\n");
	    }
	}
      
      /* end of section array */
      if (--$c == 0)
	{
	  fwrite($phpcf, "  )\n");
	}
      else
	{
	  fwrite($phpcf, "  ),\n");
	}
    }
  
  fwrite($phpcf, ");\n"); // end of configuration array
  fwrite($phpcf, "?>\n");
  fclose($phpcf);

  return true;
}

?>
