import python

from ParameterList id,Function parent
where py_parameter_lists(id,parent)
  and parent.getScope().inSource()
select id,parent