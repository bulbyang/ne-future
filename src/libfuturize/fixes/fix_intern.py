# Copyright 2006 Georg Brandl.
# Licensed to PSF under a Contributor Agreement.

"""Fixer for intern().

intern(s) 
->
from future.moves.sys import intern 
intern(s)"""

# Local imports
from lib2to3 import fixer_base
from lib2to3.fixer_util import touch_import, ImportAndCall 


class FixIntern(fixer_base.BaseFix):
    BM_compatible = True
    order = "pre"

    PATTERN = """
    power< 'intern'
           trailer< lpar='('
                    ( not(arglist | argument<any '=' any>) obj=any
                      | obj=arglist<(not argument<any '=' any>) any ','> )
                    rpar=')' >
           after=any*
    >
    """

    def transform(self, node, results):
        if results:
            # I feel like we should be able to express this logic in the
            # PATTERN above but I don't know how to do it so...
            obj = results['obj']
            if obj:
                if (obj.type == self.syms.argument and
                    obj.children[0].value in {'**', '*'}):
                    return  # Make no change.
        touch_import('future.moves.sys', 'intern', node)
        return node 
