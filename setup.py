#!/usr/bin/env python
from setuptools import setup, find_packages
from io import open

readme = open('README.md', encoding='utf8').read()

setup(
	name = "b2btest",
	version = "1.3.2",
	install_requires=[
		'consolemsg',
		'pathlib2;python_version<"3.5"',
		'setuptools>40.5',
		],
	extras_require= dict(
		audio=[
			'wavefile',
		],
		xml=[
			'lxml<4.4.0;python_version<"3.5"',
			'lxml;python_version>="3.5"',
		],
	),
	description = "Light framework to setup back-to-back test",
	author = "David Garcia Garzon",
	author_email = "voki@canvoki.net",
	url = 'https://github.com/vokimon/back2back',
	long_description = readme,
	long_description_content_type = 'text/markdown',
	license = 'GNU General Public License v3 or later (GPLv3+)',
	test_suite = 'b2btest',
	scripts=[
		'back2back'
	],
	packages=find_packages(exclude=['*_test']),
	classifiers = [
		'Programming Language :: Python',
		'Programming Language :: Python :: 2',
		'Topic :: Software Development :: Libraries :: Python Modules',
		'Intended Audience :: Developers',
		'Development Status :: 5 - Production/Stable',
		'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
		'Operating System :: OS Independent',
		],
	entry_points={
		'console_scripts': [
			'diffaudio=b2btest.diffaudio:main [audio]',
			'diffxml=b2btest.diffxml:main [xml]',
		],
		'back2back.diff': [
			'text=b2btest.difftext:differences',
			'audio=b2btest.diffaudio:differences [audio]',
			'xml=b2btest.diffxml:differences [xml]',
			]
		},
	)

