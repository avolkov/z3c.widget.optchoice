from setuptools import setup, find_packages
import sys, os
import multiprocessing

version = '0.1'

setup(name='z3c.widget.optchoice',
      version=version,
      description="Optional choice widget for z3c library.",
      long_description="""\
Optional choice widget for z3c library. This widget lets user select an entry from a list or specify it through an input field.""",
      classifiers=[], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      keywords='z3c widget',
      author='Alex Volkov',
      author_email='alex@flamy.ca',
      url='',
      license='BSD',
      packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
      include_package_data=True,
      zip_safe=False,
      extras_require = dict(
            test=['zope.testing', 'zope.app.testing', 'z3c.coverage',
                  'unittest2', 'Nose', 'coverage']
                            ),
      install_requires=[
          'z3c.form',
          'z3c.schema',
          'zope.browserpage',
          'zope.location <= 3.9.1' ,
          'zope.component <= 3.9.1',
          'lxml'
      ],
      test_suite='nose.collector',
#      test_requires=['unittest2', 'Nose','coverage'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
