#!/usr/bin/env python
# Licensed under a 3-clause BSD style license - see LICENSE.rst

import glob
import os
import sys

import ah_bootstrap
from setuptools import setup

#A dirty hack to get around some early import/configurations ambiguities
if sys.version_info[0] >= 3:
    import builtins
else:
    import __builtin__ as builtins
builtins._ASTROPY_SETUP_ = True

from astropy_helpers.setup_helpers import (
    register_commands, get_debug_option, get_package_info)
from astropy_helpers.git_helpers import get_git_devstr
from astropy_helpers.version_helpers import generate_version_py

# Get some values from the setup.cfg
try:
    from ConfigParser import ConfigParser
except ImportError:
    from configparser import ConfigParser

conf = ConfigParser()
conf.read(['setup.cfg'])
metadata = dict(conf.items('metadata'))

PACKAGENAME = metadata.get('package_name', 'packagename')
DESCRIPTION = metadata.get('description', 'Astropy affiliated package')
AUTHOR = metadata.get('author', '')
AUTHOR_EMAIL = metadata.get('author_email', '')
LICENSE = metadata.get('license', 'unknown')
URL = metadata.get('url', 'http://astropy.org')

# Get the long description from the package's docstring
__import__(PACKAGENAME)
package = sys.modules[PACKAGENAME]
LONG_DESCRIPTION = package.__doc__

# Store the package name in a built-in variable so it's easy
# to get from other parts of the setup infrastructure
builtins._ASTROPY_PACKAGE_NAME_ = PACKAGENAME

# VERSION should be PEP386 compatible (http://www.python.org/dev/peps/pep-0386)
VERSION = '0.3.9'

# Indicates if this version is a release version
RELEASE = 'dev' not in VERSION

if not RELEASE:
    VERSION += get_git_devstr(False)

# Populate the dict of setup command overrides; this should be done before
# invoking any other functionality from distutils since it can potentially
# modify distutils' behavior.
cmdclassd = register_commands(PACKAGENAME, VERSION, RELEASE)

# Freeze build information in version.py
generate_version_py(PACKAGENAME, VERSION, RELEASE,
                    get_debug_option(PACKAGENAME))

# Treat everything in scripts except README.rst as a script to be installed
scripts = [fname for fname in glob.glob(os.path.join('scripts', '*'))
           if os.path.basename(fname) != 'README.rst']


# Get configuration information from all of the various subpackages.
# See the docstring for setup_helpers.update_package_files for more
# details.
package_info = get_package_info()

# Add the project-global data
package_info['package_data'].setdefault(PACKAGENAME, [])
package_info['package_data'][PACKAGENAME].append('data/*')

# These lines are only needed if astroquery acquires command line scripts
# # Define entry points for command-line scripts
# entry_points = {}
# entry_points = {'console_scripts': []}

# Currently the only entry points installed by Astropy are hooks to
# zest.releaser for doing Astropy's releases
entry_points = {}
for hook in [('prereleaser', 'middle'), ('releaser', 'middle'),
             ('postreleaser', 'before'), ('postreleaser', 'middle')]:
    hook_ep = 'zest.releaser.' + '.'.join(hook)
    hook_name = 'astroquery.release.' + '.'.join(hook)
    hook_func = 'astropy.utils.release:' + '_'.join(hook)
    entry_points[hook_ep] = ['%s = %s' % (hook_name, hook_func)]

entry_point_list = conf.items('entry_points')
for entry_point in entry_point_list:
    entry_points['console_scripts'].append('{0} = {1}'.format(entry_point[0],
                                                              entry_point[1]))

# Include all .c files, recursively, including those generated by
# Cython, since we can not do this in MANIFEST.in with a "dynamic"
# directory name.
c_files = []
for root, dirs, files in os.walk(PACKAGENAME):
    for filename in files:
        if filename.endswith('.c'):
            c_files.append(
                os.path.join(
                    os.path.relpath(root, PACKAGENAME), filename))
package_info['package_data'][PACKAGENAME].extend(c_files)

required_packages = ['astropy>=1.0', 'requests>=2.4.3', 'keyring>=4.0',
                     'beautifulsoup4>=4.3.2', 'html5lib>=0.999']

extras_require = {
    'test': ['pytest-astropy']
}

setup(name=PACKAGENAME,
      version=VERSION,
      description=DESCRIPTION,
      scripts=scripts,
      requires=['astropy', 'requests', 'keyring', 'beautifulsoup4',
                'html5lib'],
      install_requires=required_packages,
      include_package_data=True,
      provides=[PACKAGENAME],
      license=LICENSE,
      cmdclass=cmdclassd,
      zip_safe=False,
      use_2to3=False,
      entry_points=entry_points,
      extras_require=extras_require,
      tests_require=['pytest_astropy'],
      **package_info
)
