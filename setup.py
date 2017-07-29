import os
from setuptools import setup


def read(name):
    with open(os.path.join(os.path.dirname(__file__), name)) as f:
        return f.read()

setup(
    name='CallerLookup',
    description='Reverse Caller Identity',
    long_description=read('README.rst'),
    url='http://github.com/scottphilip/caller-lookup',
    author='Scott Philip',
    author_email='sp@scottphilip.com',
    packages=['CallerLookup'],
    version='1.2.1',
    install_requires=read('REQUIREMENTS.txt').splitlines(),
    test_suite='nose.collector',
    tests_require=['nose'],
    license='GNU (v3) License',
    keywords=['Reverse Caller Identity', 'TrueCaller'],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6'
    ],
)