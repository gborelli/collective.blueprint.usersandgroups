# -*- coding: utf-8 -*-
"""Installer for the collective.blueprint.usersandgroups package."""

from setuptools import find_packages
from setuptools import setup


long_description = '\n\n'.join([
    open('README.rst').read(),
    open('CONTRIBUTORS.rst').read(),
    open('CHANGES.rst').read(),
])


setup(
    name='collective.blueprint.usersandgroups',
    version='0.2.1.dev0',
    description="transmogrifier blueprints for importing users and groups into plone",
    long_description=long_description,
    # Get more from https://pypi.org/classifiers/
    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 4.3",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='plone transmogrifier blueprint user group',
    author='',
    author_email='',
    url='https://github.com/collective/collective.blueprint.usersandgroups',
    project_urls={
        'PyPI': 'https://pypi.python.org/pypi/collective.blueprint.usersandgroups',
        'Source': 'https://github.com/collective/collective.blueprint.usersandgroups',
        'Tracker': 'https://github.com/collective/collective.blueprint.usersandgroups/issues',
        # 'Documentation': 'https://collective.blueprint.usersandgroups.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['collective', 'collective.blueprint'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires="==2.7, >=3.6",
    install_requires=[
        'collective.transmogrifier',
        'setuptools',
    ],
    extras_require={
        'test': [
            'plone.api',
            'plone.app.testing'
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = collective.blueprint.usersandgroups.locales.update:update_locale
    """,
)
