
from lib2to3 import fixer_base
from libfuturize.fixer_util import touch_import_top

class FixReload(fixer_base.BaseFix):

    BM_compatible = True
    order = "pre"

    PATTERN = """
    power< name='reload'
        trailer<
            '(' any ')'
        > any*
    >
    """

    def transform(self, node, results):
        touch_import_top(u"importlib", u"reload", node)
        touch_import_top(u"future", u"standard_library", node)
