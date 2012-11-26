from setuptools import setup, find_packages
import sys, os

version = '0.1dev'

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
      install_requires=[
          'z3c.form'
      ],
      test_suite='nose.collector',
      test_requires=['Nose'],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
