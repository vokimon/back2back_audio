2btest - Light framework to setup back-to-back test scripts
============================================================

[![Build Status](https://travis-ci.org/vokimon/back2back.svg?branch=master)](https://travis-ci.org/vokimon/back2back)

![B2BLogo](icon_b2btest.png)

This package is helpfull to prepare and manage
back-to-back tests to get control over software
you don't have proper tests yet.

On one side, it includes `back2back`, a comand line tool
that performs back-to-back tests on any software
that can be called by command line and produces
some output files you want to get warned when they get different.
You can define the set of commands and the outputs to watch in a simple
YAML file.

On the other side, it includes comparision functions
and python-unittests like asserts you can use within
your test suites that perform similar workflows, keeping
the reference outputs in a folder and named by the testname.

Both the command line tool and the python libraries,
are extendable with plugins to get informative diff for several
file formats: audio, xml, text, pdf...


Why back-to-back testing
------------------------

A Back-to-back tests is a black box tests that just compares
that, given an input, you have the same output all the time.
Unit testing and Test Driven Development are a quite more
preferable strategy to test a piece of software.
But often we need to change a piece of software which has
been developed without proper testing.
A quick way to get control over it is setting up a set of
back-to-back tests and then proceeding with the
refactoring with a larger level of confidence than having
no test at all.

**Note of warning:**
Don't feel too confident by being backed by back2back tests.
It is black-box testing, so it is hard to ensure full coverage.
You may be changing a behaviour which is not exercised
by the b2b test, and not noticing.


Easing the workflow with b2btest
--------------------------------

When b2b tests are hard to run and maintain,
they use to get old and useless.
This script automates most tedious back2back
related task such as setting up, verifying results,
accepting changes, clearing data...

Features:
* You can put under back2back testing either
  - the outcomes (files) of any shell command line (with pipes and so on), or
  - any serializable data in a `unittest.TestCase` method
* It is auto-checked, like most Xunit frameworks
* It automagically manages the expectation data
* On failure, it generates handy data to evaluate
	the changes by providing diffs and keeping
	failed and expected data for reference.
* Provides a handy command line to accept failed 
  results as proper ones.
* When the test turns green or it is accepted all 
  failure related data gets cleared.
* Comparators and diff generators can be added for your own file type.
* You can set architecture dependant outputs for the same test.


How to install
--------------

Just use:

```bash
$ pip install b2btest
```

In order to get the by extension diffs:

```bash
$ pip install b2btest[audio,xml]
```

Dependencies
------------

B2b for audio files requires the [wavefile] module:
Which in turn requires having [libsndfile] library installed.

[wavefile]: https://github.com/vokimon/python-wavefile
[libsndfile]: http://www.mega-nerd.com/libsndfile/

For xml files, it requires [lxml] module and both
[libxml2] and [libxslt] libraries installed

[lxml]: http://lxml.de/
[libxml2]: http://xmlsoft.org/downloads.html
[libxslt]: http://xmlsoft.org/XSLT/


Back2Back testing in your unittest
----------------------------------

```python
import unittest
import b2btest # Not used but load a new assertion method for TestCase
import datetime

class MyTest(unittest.TestCase):
	def test_this(self):
		self.assertB2BEqual("data")

	def test_that_willallwaysfail(self):
		self.assertB2BEqual(str(datetime.datetime.now()))

if __name__ == '__main__':
	# acceptMode attribute makes the assert accept the results
	# expectation as new
	if '--accept' in sys.argv:
		sys.argv.remove('--accept')
		unittest.TestCase.acceptMode = True

	unittest.main()
```


Back2Back testing of cli programs
---------------------------------

When you are testing back-to-back the output of a command line,
you define a yaml file like this (name it b2bcases.yaml).

```yaml
#!/usr/bin/env back2back 

datapath: "b2bdata" # Point it to the directory containing your reference data
testcases:

  HelloWorld:
    command: echo Hello World > output.txt
    outputs:
    - output.txt

  AlwaysChanging:
    command: date > output.txt
    outputs:
    - output.txt

  Generate1KHzSine:
    command: sox -n /tmp/sine.wav synth 1.0 sine  1000.0
    outputs:
    - /tmp/sine.wav
```

To list the available test cases:

```bash
back2back b2bcases.yaml --list
```

To run them:

```bash
back2back b2bcases.yaml
```

The first time you run a test case, it will fail as there is no
expectation, you must to check it is valid and accept it.
Successive failures means that the behaviour has change.
You can accept the new result if the behavioural change is expected.

To accept a concrete case:

```bash
back2back b2bcases.yaml --accept HelloWorld
```

To accept all failing tests:

```bash
back2back b2bcases.yaml --acceptall
```

If some output depends on the computer architecture or in the platform (windows, mac...)
use the `--arch` and `--platform` options when accepting.
It will generate an independent expectation file for such architecture or platform.

```bash
back2back b2bcases.yaml --accept HelloWorld --arch
```

Old inteface
------------

If you want to generate the test cases progamaticaly,
you still are able to use the old python interface.
Instead of a yaml file, write python script like this:

Just like in this b2b script does:

```python
	#!/usr/bin/python
	import sys
	from b2btest import runBack2BackProgram

	data_path="path/to/b2bdata"
	back2BackTests = [
		("myprogram_with_option",
				"./myprogram --option input1.wav input2.wav output.wav otheroutput.wav ",
				[
					"output.wav",
					"otheroutput.wav",
		]),
		("myprogram_with_other_option",
				"./myprogram --other-option input1.wav input2.wav output.wav ignoredoutput.wav ",
				[
					"output.wav",
				]),
		]
	runBack2BackProgram(data_path, sys.argv, back2BackTests)
```

Save this file as `back2back.py`, for example, and make it executable.

Use the python script directly with the same command line
but without the yaml file.



Extra advices
-------------

### Use continuous integration

Put your tests under a continuous integration system such
* Travis-CI
* BuildBot
* TestFarm
* CDash

You might be lazy passing tests but bots aren't.
Connect your bots to your VCS so they test for every commit.

### Keep your expectations up to date

If one b2b test gets red, don't keep it for long,
either accept it or roll-back your code.
b2b detect changes, but if you are in a change
you won't notice whether a second one happens.
If your expectation data is backed by a version 
control system dare to accept wrong expectation data
until you fix it. But don't forget.


Change log
----------

### 1.3.3

- Simplified dependency on lxml

### 1.3.2

- `diffaudio` as console script
- `diffxml` as console script
- Fix: entry points for xml and audio plugins
- Just markdown README

### 1.3.1

- Updated README

### 1.3

- Avoid larg diffs by telling just the generated file with the failed results
- Fix unicode problems in certain python versions
- Using older lxml versions for python<3.5

### 1.2

- CLI: Fix: only the first output was actually checked
- Plugin based type sensitive diff
- Specific diff for XML
- XML and Audio diffing now are extras
- 'extensions' key in yaml testcases to associate custom file extensions to a diff plugin

### 1.1

- Unit test like usage for back-to-back test Python code instead of command line programs.
- New commandline tool `back2back` that takes a yaml file with the test cases definitions.

### 1.0

- First github version
- (There were previous unpublished versions)



