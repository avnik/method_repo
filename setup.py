import os

from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.txt')).read()
CHANGES = open(os.path.join(here, 'CHANGES.txt')).read()

requires = [
    'pyramid',
    'substanced',
    'waitress',
    'docutils',
    'pytz',
    'pyramid_tm',
    'zope.schema',
    'six',
    ]

setup(name='method_repo',
      version='0.0',
      description='Method repo',
      long_description=README + '\n\n' +  CHANGES,
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Internet :: WWW/HTTP :: WSGI",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
        ],
      author='',
      author_email='',
      url='',
      keywords='web pyramid pylons substanced',
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False,
      test_suite='blog.tests',
      install_requires = requires,
      entry_points = """\
      [paste.app_factory]
      main = method_repo:main
      [console_scripts]
      method-repo-import = method_repo.scripts.import:main
      """
      )
