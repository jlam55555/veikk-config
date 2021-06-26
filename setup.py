from setuptools import setup

setup(name='veikk-config',
      version='0.1',
      description='VEIKK Digitizer Configuration Tool',
      url='https://www.github.com/jlam55555/veikk-config',
      author='Jonathan Lam',
      author_email='jonlamdev@gmail.com',
      license='GNU General Public License v2.0',
      packages=['veikk', 'veikkctl'],
      zip_safe=False,
      entry_points={
          'console_scripts': [
              'veikk=veikk.__init__:main'
          ]
      })
