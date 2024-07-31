"""
Fixer for iterkeys() -> future.utils.iterkeys(), and similarly for iteritems and itervalues.
"""

from __future__ import generator_stop

# Local imports
from lib2to3 import pytree
from lib2to3.fixes import fix_dict
from libfuturize import fixer_util


class FixDict(fix_dict.FixDict):
    def transform_iter(self, node, results):
        """Call six.(iter|view)items() and friends."""
        # Make sure six is imported.
        # fixer_util.touch_import(None, "six", node)
        # fixer_util.touch_import_top(u"future.utils",u"utils",node)

        # Copy of self.transform() from fissix.fix_dict with some changes to
        # use the future.utils methods.

        head = results["head"]
        method = results["method"][0]  # Extract node for method name
        tail = results["tail"]
        syms = self.syms
        method_name = method.value
        fixer_util.touch_import_top(u"future.utils", method_name , node)
        name = fixer_util.Name(method_name, prefix=node.prefix)
        assert method_name.startswith(("iter", "view")), repr(method)
        assert method_name[4:] in ("keys", "items", "values"), repr(method)
        head = [n.clone() for n in head]
        tail = [n.clone() for n in tail]
        new = pytree.Node(syms.power, head)
        new.prefix = ""
        new = fixer_util.Call(name, [new])
        if tail:
            new = pytree.Node(syms.power, [new] + tail)
        new.prefix = node.prefix
        return new

    def transform(self, node, results):
        method = results["method"][0]
        method_name = method.value
        if method_name in ("keys", "items", "values"):
            return super().transform(node, results)
        else:
            return self.transform_iter(node, results)

    def in_special_context(self, node, isiter):
        # Redefined from parent class to make "for x in d.items()" count as
        # in special context; fissix only counts for loops as special context
        # for the iter* methods.
        return super().in_special_context(node, True)
