""" Test suite for the fixer modules.

Based on lib2to3/tests/test_fixers.py

"""
# Support code for test_*.py files, from lib2to3/tests/support.py by Collin Winter:

# Python imports
import sys
import os
import os.path
from itertools import chain
from textwrap import dedent
from operator import itemgetter
from lib2to3 import pygram, pytree, refactor, fixer_util
from lib2to3.pgen2 import driver

# Local imports
from future.tests.base import unittest
from future.builtins import str


test_dir = os.path.dirname(__file__)
proj_dir = os.path.normpath(os.path.join(test_dir, ".."))
# grammar_path = os.path.join(test_dir, "..", "Grammar.txt")
# grammar = driver.load_grammar(grammar_path)
# driver = driver.Driver(grammar, convert=pytree.convert)
#
# def parse_string(string):
#     return driver.parse_string(reformat(string), debug=True)


def run_all_tests(test_mod=None, tests=None):
    if tests is None:
        tests = unittest.TestLoader().loadTestsFromModule(test_mod)
    unittest.TextTestRunner(verbosity=2).run(tests)


def reformat(string):
    return dedent(string) + u"\n\n"


def get_refactorer(fixer_pkg="libfuturize", fixers=None, options=None):
    """
    A convenience function for creating a RefactoringTool for tests.

    fixers is a list of fixers for the RefactoringTool to use. By default
    "libfuturize.nefixes.*" is used. options is an optional dictionary of options to
    be passed to the RefactoringTool.
    """
    if fixers is not None:
        fixers = [fixer_pkg + ".nefixes.fix_" + fix for fix in fixers]
    else:
        fixers = refactor.get_fixers_from_package(fixer_pkg + ".nefixes")
    options = options or {}
    return refactor.RefactoringTool(fixers, options, explicit=True)


def all_project_files():
    for dirpath, dirnames, filenames in os.walk(proj_dir):
        for filename in filenames:
            if filename.endswith(".py"):
                yield os.path.join(dirpath, filename)


class FixerTestCase(unittest.TestCase):

    # Other test cases can subclass this class and replace "fixer_pkg" with
    # their own.
    def setUp(self, fix_list=None, fixer_pkg="libfuturize", options=None):
        if fix_list is None:
            fix_list = [self.fixer]
        self.refactor = get_refactorer(fixer_pkg, fix_list, options)
        self.fixer_log = []
        self.filename = u"<string>"

        for fixer in chain(self.refactor.pre_order,
                           self.refactor.post_order):
            fixer.log = self.fixer_log

    def _check(self, before, after):
        before = reformat(before)
        after = reformat(after)
        tree = self.refactor.refactor_string(before, self.filename)
        self.assertEqual(after, str(tree))
        return tree

    def check(self, before, after, ignore_warnings=False):
        tree = self._check(before, after)
        self.assertTrue(tree.was_changed)
        if not ignore_warnings:
            self.assertEqual(self.fixer_log, [])

    def warns(self, before, after, message, unchanged=False):
        tree = self._check(before, after)
        self.assertTrue(message in "".join(self.fixer_log))
        if not unchanged:
            self.assertTrue(tree.was_changed)

    def warns_unchanged(self, before, message):
        self.warns(before, before, message, unchanged=True)

    def unchanged(self, before, ignore_warnings=False):
        self._check(before, before)
        if not ignore_warnings:
            self.assertEqual(self.fixer_log, [])

    def assert_runs_after(self, *names):
        fixes = [self.fixer]
        fixes.extend(names)
        r = get_refactorer("lib2to3", fixes)
        (pre, post) = r.get_fixers()
        n = "fix_" + self.fixer
        if post and post[-1].__class__.__module__.endswith(n):
            # We're the last fixer to run
            return
        if pre and pre[-1].__class__.__module__.endswith(n) and not post:
            # We're the last in pre and post is empty
            return
        self.fail("Fixer run order (%s) is incorrect; %s should be last."
                  % (", ".join([x.__class__.__module__ for x in (pre+post)]), n))


# EDIT the tests below ...

class Test_reload(FixerTestCase):
    fixer = "reload"

    def test(self):
        b = """x = reload(a)"""
        a = """from future import standard_library\nstandard_library.install_aliases()\nfrom importlib import reload\nx = reload(a)"""
        self.check(b, a)

        b = """y = reload("b" # test
              )"""
        a = """from future import standard_library\nstandard_library.install_aliases()\nfrom importlib import reload\ny = reload("b" # test
              )"""
        self.check(b, a)

        b = """z = reload(a+b+c.d,   )"""
        a = """from future import standard_library\nstandard_library.install_aliases()\nfrom importlib import reload\nz = reload(a+b+c.d,   )"""
        self.check(b, a)

class Test_intern(FixerTestCase):
    fixer = "intern"

    def test_prefix_preservation(self):
        b = """x = intern(a)"""
        a = """from future.moves.sys import intern\nx = intern(a)"""
        self.check(b, a)

        b = """y = intern("b" # test
              )"""
        a = """from future.moves.sys import intern\ny = intern("b" # test
              )"""
        self.check(b, a)

        b = """z = intern(a+b+c.d,   )"""
        a = """from future.moves.sys import intern\nz = intern(a+b+c.d,   )"""
        self.check(b, a)

    def test(self):
        b = """x = intern(a)"""
        a = """from future.moves.sys import intern\nx = intern(a)"""
        self.check(b, a)

        b = """z = intern(a+b+c.d,)"""
        a = """from future.moves.sys import intern\nz = intern(a+b+c.d,)"""
        self.check(b, a)

        b = """intern("y%s" % 5).replace("y", "")"""
        a = """from future.moves.sys import intern\nintern("y%s" % 5).replace("y", "")"""
        self.check(b, a)

    # These should not be refactored

    def test_unchanged(self):
        s = """intern(a=1)"""
        self.unchanged(s)

        s = """intern(f, g)"""
        self.unchanged(s)

        s = """intern(*h)"""
        self.unchanged(s)

        s = """intern(**i)"""
        self.unchanged(s)

        s = """intern()"""
        self.unchanged(s)

class Test_raise(FixerTestCase):
    fixer = "raise"

    def test_basic(self):
        b = """raise Exception, 5"""
        a = """raise Exception(5)"""
        self.check(b, a)

    def test_prefix_preservation(self):
        b = """raise Exception,5"""
        a = """raise Exception(5)"""
        self.check(b, a)

        b = """raise   Exception,    5"""
        a = """raise   Exception(5)"""
        self.check(b, a)

    def test_with_comments(self):
        b = """raise Exception, 5 # foo"""
        a = """raise Exception(5) # foo"""
        self.check(b, a)

        b = """
        def foo():
            raise Exception, 5, 6 # foo"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            raise_with_traceback(Exception(5), 6) # foo"""
        self.check(b, a)

    def test_None_value(self):
        b = """
        raise Exception(5), None, tb"""
        a = """
        from future.utils import raise_with_traceback
        raise_with_traceback(Exception(5), tb)"""
        self.check(b, a)

    def test_tuple_value(self):
        b = """raise Exception, (5, 6, 7)"""
        a = """raise Exception(5, 6, 7)"""
        self.check(b, a)

    def test_tuple_exc_1(self):
        b = """raise (((E1, E2), E3), E4), 5"""
        a = """raise E1(5)"""
        self.check(b, a)

    def test_tuple_exc_2(self):
        b = """raise (E1, (E2, E3), E4), 5"""
        a = """raise E1(5)"""
        self.check(b, a)

    def test_unknown_value(self):
        b = """
        raise E, V"""
        a = """
        from future.utils import raise_
        raise_(E, V)"""
        self.check(b, a)

    def test_unknown_value_with_traceback_with_comments(self):
        b = """
        raise E, Func(arg1, arg2, arg3), tb # foo"""
        a = """
        from future.utils import raise_
        raise_(E, Func(arg1, arg2, arg3), tb) # foo"""
        self.check(b, a)

    def test_unknown_value_with_indent(self):
        b = """
        while True:
            print()  # another expression in the same block triggers different parsing
            raise E, V
        """
        a = """
        from future.utils import raise_
        while True:
            print()  # another expression in the same block triggers different parsing
            raise_(E, V)
        """
        self.check(b, a)

    # These should produce a warning

    def test_string_exc(self):
        s = """raise 'foo'"""
        self.warns_unchanged(s, "Python 3 does not support string exceptions")

    def test_string_exc_val(self):
        s = """raise "foo", 5"""
        self.warns_unchanged(s, "Python 3 does not support string exceptions")

    def test_string_exc_val_tb(self):
        s = """raise "foo", 5, 6"""
        self.warns_unchanged(s, "Python 3 does not support string exceptions")

    # These should result in traceback-assignment

    def test_tb_1(self):
        b = """
        def foo():
            raise Exception, 5, 6"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            raise_with_traceback(Exception(5), 6)"""
        self.check(b, a)

    def test_tb_2(self):
        b = """
        def foo():
            a = 5
            raise Exception, 5, 6
            b = 6"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            a = 5
            raise_with_traceback(Exception(5), 6)
            b = 6"""
        self.check(b, a)

    def test_tb_3(self):
        b = """
        def foo():
            raise Exception,5,6"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            raise_with_traceback(Exception(5), 6)"""
        self.check(b, a)

    def test_tb_4(self):
        b = """
        def foo():
            a = 5
            raise Exception,5,6
            b = 6"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            a = 5
            raise_with_traceback(Exception(5), 6)
            b = 6"""
        self.check(b, a)

    def test_tb_5(self):
        b = """
        def foo():
            raise Exception, (5, 6, 7), 6"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            raise_with_traceback(Exception(5, 6, 7), 6)"""
        self.check(b, a)

    def test_tb_6(self):
        b = """
        def foo():
            a = 5
            raise Exception, (5, 6, 7), 6
            b = 6"""
        a = """
        from future.utils import raise_with_traceback
        def foo():
            a = 5
            raise_with_traceback(Exception(5, 6, 7), 6)
            b = 6"""
        self.check(b, a)

class ImportsFixerTests:

    def test_import_module(self):
        for old, new in self.modules.items():
            b = "import %s" % old
            a = "import %s" % new
            self.check(b, a)

            b = "import foo, %s, bar" % old
            a = "import foo, %s, bar" % new
            self.check(b, a)

    def test_import_from(self):
        for old, new in self.modules.items():
            b = "from %s import foo" % old
            a = "from %s import foo" % new
            self.check(b, a)

            b = "from %s import foo, bar" % old
            a = "from %s import foo, bar" % new
            self.check(b, a)

            b = "from %s import (yes, no)" % old
            a = "from %s import (yes, no)" % new
            self.check(b, a)

    def test_import_module_as(self):
        for old, new in self.modules.items():
            b = "import %s as foo_bar" % old
            a = "import %s as foo_bar" % new
            self.check(b, a)

            b = "import %s as foo_bar" % old
            a = "import %s as foo_bar" % new
            self.check(b, a)

    def test_import_from_as(self):
        for old, new in self.modules.items():
            b = "from %s import foo as bar" % old
            a = "from %s import foo as bar" % new
            self.check(b, a)

    def test_star(self):
        for old, new in self.modules.items():
            b = "from %s import *" % old
            a = "from %s import *" % new
            self.check(b, a)

    def test_import_module_usage(self):
        for old, new in self.modules.items():
            b = """
                import %s
                foo(%s.bar)
                """ % (old, old)
            a = """
                import %s
                foo(%s.bar)
                """ % (new, new)
            self.check(b, a)

            b = """
                from %s import x
                %s = 23
                """ % (old, old)
            a = """
                from %s import x
                %s = 23
                """ % (new, old)
            self.check(b, a)

            s = """
                def f():
                    %s.method()
                """ % (old,)
            self.unchanged(s)

            # test nested usage
            b = """
                import %s
                %s.bar(%s.foo)
                """ % (old, old, old)
            a = """
                import %s
                %s.bar(%s.foo)
                """ % (new, new, new)
            self.check(b, a)

            b = """
                import %s
                x.%s
                """ % (old, old)
            a = """
                import %s
                x.%s
                """ % (new, old)
            self.check(b, a)
#
#
class Test_itertools_import(FixerTestCase, ImportsFixerTests):
    fixer='itertools_import'
    from libfuturize.fixes.fix_itertools_import import MAPPING as modules
    def test_ifilter_and_zip_longest(self):
        b = """
            import itertools
            s = itertools.ifilterfalse(a,b)
            """
        a = """
            import future.moves.itertools
            s = future.moves.itertools.ifilterfalse(a,b)
            """
        self.check(b, a)
        b = """
            import itertools
            s = itertools.ifilterfalse(a,b)
            s = itertools.izip_longest(a,b)
            """
        a = """
            import future.moves.itertools
            s = future.moves.itertools.ifilterfalse(a,b)
            s = future.moves.itertools.izip_longest(a,b)
            """
        self.check(b, a)

class Test_itertools_imports(FixerTestCase):
    fixer = 'itertools_imports'

    def test_reduced(self):
        b = "from itertools import imap, izip, foo"
        a = "from builtins import zip\nfrom builtins import map\nfrom itertools import foo"
        self.check(b, a)

        b = "from itertools import bar, imap, izip, foo"
        a = "from builtins import zip\nfrom builtins import map\nfrom itertools import bar, foo"
        self.check(b, a)

        b = "from itertools import chain, imap, izip"
        a = "from builtins import zip\nfrom builtins import map\nfrom itertools import chain"

        self.check(b, a)

    def test_comments(self):
        b = "#foo\nfrom itertools import imap, izip"
        a = "#foo\nfrom builtins import zip\nfrom builtins import map\n"
        self.check(b, a)

    def test_none(self):
        b = "from itertools import imap, izip"
        a = "from builtins import zip\nfrom builtins import map\n"
        self.check(b, a)

        b = "from itertools import izip"
        a = "from builtins import zip\n"
        self.check(b, a)

    def test_ifilter_and_zip_longest(self):
        for name in "filterfalse", "zip_longest":
            b = "from itertools import i%s" % (name,)
            a = "from future.moves.itertools import %s\n" % (name,)
            self.check(b, a)

            b = "from itertools import imap, i%s, chain" % (name,)
            a = "from future.moves.itertools import %s\nfrom builtins import map\nfrom itertools import chain" % (name,)
            self.check(b, a)

            b = "from itertools import bar, i%s, foo" % (name,)
            a = "from future.moves.itertools import %s\nfrom itertools import bar, foo" % (name,)
            self.check(b, a)

    def test_import_star(self):
        s = "from itertools import *"
        self.unchanged(s)


    def test_unchanged(self):
        s = "from itertools import foo"
        self.unchanged(s)
