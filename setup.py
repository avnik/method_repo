__version__ = '0.1'

import os
import sys

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
try:
    README = open(os.path.join(here, 'README.txt')).read()
    CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()
except IOError:
    README = CHANGES = ''

install_requires=[
    'setuptools',
    'six',
    'pyramid',
    'pyramid_zcml',
    'composite.alchemist',
    'repozitory',
    'deform',
    'pyramid_deform',
    'waitress',
    ]

setup(name='method_repo',
      version=__version__,
      description='Methods repository',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Intended Audience :: Customer",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "License :: AGPL",
        ],
      keywords='web wsgi zope',
      author="Alexander V. Nikolaev",
      author_email="avn@daemon.hole.ru",
      url="http://github.org/avnik/method_repo",
      packages=find_packages(),
      include_package_data=True,
      namespace_packages = ['method_repo'],
      zip_safe=False,
      install_requires = install_requires,
      extras_require = {
            'test': ['zope.testing'],
      },
      entry_points = """\
      [paste.app_factory]
      main = method_repo.wsgi:main

      [console_scripts]
      method-repo-populate = method_repo.scripts.populate:main
      method-repo-upload = method_repo.scripts.upload:main
      """,
)

