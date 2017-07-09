from setuptools import setup

setup(
    name='CallerLookup',
    description='Reverse Caller Identity',
    url='http://github.com/scottphilip/caller-lookup',
    author='Scott Philip',
    author_email='sp@scottphilip.com',
    packages=['CallerLookup'],
    version='0.1',
    install_requires=['GoogleToken', 'phonenumbers'],
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