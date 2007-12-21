function select_all_files(v)
{
  the_form="main_form";

  var elts      = document.forms[the_form].elements['select_to_copy[]'];
  var elts_cnt  = elts.length;

  for (var i = 0; i < elts_cnt; i++) {
    elts[i].checked = v;
  } // end for

  return true;
}

