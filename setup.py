from distutils.core import setup

setup(
    name='HorizonJPL',
    version='0.1.6',
    author='Matthew Mihok',
    author_email='matthew.mihok@niewma.com',
    packages=['horizon', 'horizon.test'],
    scripts=[],
    url='http://pypi.python.org/pypi/HorizonJPL/',
    license='LICENSE.txt',
    description='Access to NASA\'s JPL HORIZON Ephemeris System',
    
long_description='{0}\r\n{1}'.format(open('README.txt').read(),open('CHANGES.txt').read()),
    install_requires=[
        'pytest-timeout >= 0.3'
    ]
)
