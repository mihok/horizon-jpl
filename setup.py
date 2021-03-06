from distutils.core import setup

setup(
    name='HorizonJPL',
    version='0.1.8',
    author='Matthew Mihok',
    author_email='4d.69.68.6f.6b@gmail.com',
    packages=['horizon', 'horizon.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/HorizonJPL/',
    license='LICENSE.txt',
    description='Access to NASA\'s JPL HORIZON Ephemeris System',
    long_description=open('README.txt').read(),
    install_requires=[
        'pytest-timeout >= 0.3'
    ]
)
