import os
import re

from setuptools import setup, find_packages

name = 'gandi-pyramid-prometheus'
here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.rst')).read()
CHANGES = open(os.path.join(here, 'CHANGES.rst')).read()

with open(os.path.join(*([here] + [name.replace('-', '_'), '__init__.py'])
                       )) as v_file:
    version = re.compile(r".*__version__ = '(.*?)'",
                         re.S).match(v_file.read()).group(1)

requires = [
    'pyramid',
    'prometheus_client',
    ]


extras_require = {
    'doc': [],   # TODO
    'test': ['webtest', 'zope.interface'],
}

setup(name=name,
      version=version,
      description=u'Pyramid Plugin for prometheus integration on multiprocess '
                  u'wsgi server',
      long_description=README + '\n\n' + CHANGES,
      classifiers=['Programming Language :: Python',
                   'Framework :: Pyramid',
                   'Topic :: Internet :: WWW/HTTP',
                   'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
                   ],
      author='Gandi',
      author_email='feedback@gandi.net',
      url='https://github.com/Gandi/gandi-pyramid-prometheus',
      keywords='pyramid prometheus metrics',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='{name}.tests'.format(name=name).replace('-', '_'),
      install_requires=requires,
      extras_require=extras_require,
      tests_require=extras_require['test'],
      license="BSD-derived (http://www.repoze.org/LICENSE.txt)",
      )
