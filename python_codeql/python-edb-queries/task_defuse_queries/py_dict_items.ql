import python
import extra_classes

from MyDictItem id,int kind, MyDictItemList parent, int idx
where py_dict_items(id, kind, parent,idx)
  and id.getScope().inSource()
select id,kind,parent,idx