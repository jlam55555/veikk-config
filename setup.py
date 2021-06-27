from setuptools import setup

# read the contents of your README file
# https://packaging.python.org/guides/making-a-pypi-friendly-readme/
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='veikk-config',
      version='3.0.0a1',
      description='VEIKK Digitizer Configuration Tool',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://www.github.com/jlam55555/veikk-config',
      author='Jonathan Lam',
      author_email='jlam55555@gmail.com',
      license='GNU General Public License v2.0',
      packages=['veikk', 'veikkctl'],
      zip_safe=False,
      install_requires=[
          'pyudev',
          'evdev'
      ],
      entry_points={
          'console_scripts': [
              'veikk=veikk.__init__:main'
          ]
      })
