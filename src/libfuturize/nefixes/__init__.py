import sys
from lib2to3 import refactor

# The following fixers are "safe": they convert Python 2 code to more
# modern Python 2 code. They should be uncontroversial to apply to most
# projects that are happy to drop support for Py2.5 and below. Applying
# them first will reduce the size of the patch set for the real porting.

libfuturize_nefix_names_stage1 = set([
    'libfuturize.nefixes.fix_file',
    'libfuturize.nefixes.fix_raise',
])

libfuturize_nefix_names_stage2 = set([
    'libfuturize.nefixes.fix_dict',
    'libfuturize.nefixes.fix_intern',
    'libfuturize.nefixes.fix_itertools',
    'libfuturize.nefixes.fix_itertools_import',
    'libfuturize.nefixes.fix_itertools_imports',
    'libfuturize.nefixes.fix_reload',
])
