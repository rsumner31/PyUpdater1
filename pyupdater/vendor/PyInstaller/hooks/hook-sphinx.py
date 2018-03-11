#-----------------------------------------------------------------------------
# Copyright (c) 2013, PyInstaller Development Team.
#
# Distributed under the terms of the GNU General Public License with exception
# for distributing bootloader.
#
# The full license is in the file COPYING.txt, distributed with this software.
#-----------------------------------------------------------------------------
#
# ********************************************
# hook-sphinx.py - Pyinstaller hook for Sphinx
# ********************************************
from PyInstaller.compat import is_py2
#
# The following analysis applies to Sphinx v. 1.3.1, reported by ``pip show
# sphinx``.
#
# From sphinx.application line 248::
#
#    __import__('sphinx.builders.' + mod, None, None, [cls]), cls)
#
# Therefore, we need all modules in ``sphinx.builders``.
from PyInstaller.hooks.hookutils import collect_submodules, collect_data_files

hiddenimports = ( collect_submodules('sphinx.builders') +
#
# From sphinx.application line 429::
#
#    mod = __import__(extension, None, None, ['setup'])
#
# Per http://sphinx-doc.org/extensions.html#builtin-sphinx-extensions,
# Sphinx extensions are all placed in ``sphinx.ext``. Include these.
                  collect_submodules('sphinx.ext') +
#
# From sphinx.search line 228::
#
#    lang_class = getattr(__import__(module, None, None, [classname]),
#                         classname)
#
# From sphinx. search line 119::
#
#    languages = {
#        'da': 'sphinx.search.da.SearchDanish',
#        'de': 'sphinx.search.de.SearchGerman',
#        'en': SearchEnglish,
#
# So, we need all the languages in ``sphinx.search``.
                  collect_submodules('sphinx.search') +
#
# From sphinx.websupport line 100::
#
#    mod = 'sphinx.websupport.search.' + mod
#    SearchClass = getattr(__import__(mod, None, None, [cls]), cls)
#
# So, include modules under ``sphinx.websupport.search``.
                  collect_submodules('sphinx.websupport.search') +
#
# From sphinx.util.inspect line 21::
#
#    inspect = __import__('inspect')
#
# And from sphinx.cmdline line 173::
#
#    locale = __import__('locale')  # due to submodule of the same name
#
# Add these two modules.
                  ['inspect', 'locale',
#
# Plus, two Sphinx themes (I term them external themes) are located outside
# the Sphinx package. Include them as well.
                   'alabaster', 'sphinx_rtd_theme'] )
#
# Finally, there are a HUGE number of imports from six that must be manually
# listed. These will be auto-detected in Python 3, so omit them.
if is_py2:
    hiddenimports += ('StringIO', 'cStringIO', 'cPickle', 'itertools',
                      'UserString', 'urllib', 'urllib2', 'HTMLParser',
                      'ConfigParser')
#
# Sphinx also relies on a number of data files in its directory hierarchy: for
# example, *.html and *.conf files in sphinx.themes, translation files in
# sphinx.locale, etc.
datas = ( collect_data_files('sphinx') +
#
# The external themes also need their data files.
          collect_data_files('alabaster') +
          collect_data_files('sphinx_rtd_theme') )

