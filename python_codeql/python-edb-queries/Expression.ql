import python

from Expr id, int kind, int idx
where py_exprs(id, kind, id.getParent(), idx)
select id, kind, idx, id.getEnclosingModule(), id.getParent()
