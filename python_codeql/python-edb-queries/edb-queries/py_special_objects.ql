import python

from Object obj,string name
where py_special_objects(obj,name)
select obj,
       name.replaceAll("\n", "\\n").replaceAll("\r", "\\r").replaceAll("\t", "\\t")