#!/usr/bin/env python

from setuptools import setup

setup(
    name = 'PhpBBAuth',
    version = '0.3',
    author = 'Denom',
    author_email = 'thelickie@gmail.com',
    url = 'http://trac-hacks.org/wiki/PhpBbAuthPlugin',
    description = 'Authentication against PhpBB3.  Requires Account Manager',

    license = 'MIT',
    zip_safe=True,
    packages=['phpbbauth'],
    install_requires = [
        'TracAccountManager>=0.2dev',
        'phpbb-python',
        'bcrypt'
    ],

    classifiers = [
        'Framework :: Trac',
    ],

    keywords="acct_mgr phpbb",

    entry_points = {
        'trac.plugins': [
            'phpbbauth.main = phpbbauth.main',
        ]
    },

)
