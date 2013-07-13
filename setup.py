from setuptools import setup

setup(name='forestcost',
      version='0.1',
      packages=['forestcost'],
      package_data={'forestcost': ['*.xls']},
      include_package_data=True,
      install_requires=['xlrd'],
      )
