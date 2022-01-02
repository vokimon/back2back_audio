b2btest audio - Audio file plugin for b2btest
============================================================

[![CI](https://github.com/vokimon/back2back_audio/actions/workflows/main.yml/badge.svg)](https://github.com/vokimon/back2back_audio/actions/workflows/main.yml)
[![Coverage Status](https://coveralls.io/repos/github/vokimon/back2back_audio/badge.svg?branch=master)](https://coveralls.io/github/vokimon/back2back_audio?branch=master)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/b2btest_audio)](https://pypi.org/b2btest_audio)
[![PyPI - Version](https://img.shields.io/pypi/v/b2btest_audio)](https://pypi.org/b2btest_audio)


![B2BLogo](icon_b2btest.png)

This package adds audio file support to b2btest.
b2btest is a tool to automate tests that compare results
to some previous ones, and this plugin,
is helpful to compare audiofiles in a sensible way.

See [https://github.com/vokimon/back2back](b2btest) README
for a deeper discussion on why you should avoid to do
those back-to-back tests but sometimes it is the way to proceed.

This plugin handles audiofiles specially in several ways:

- It considers two outputs to be different if the sample-by-sample difference is beyond some sound to noise ratio.
- In the case of differences, it generates a diff audio by substracting both waves sample by sample.

By using `python-wavefile`, it supports floating point samples, and multichannel waves.

How to install
--------------

Just use:

```bash
$ pip install b2btest_audio
```

Dependencies
------------

This plugin requires the [wavefile] module,
which in turn requires having [libsndfile] library installed in your system.

[wavefile]: https://github.com/vokimon/python-wavefile
[libsndfile]: http://www.mega-nerd.com/libsndfile/


Back2Back testing of cli programs
---------------------------------

When you are testing back-to-back the output of a command line,
you define a yaml file like this (name it b2bcases.yaml).

```yaml
#!/usr/bin/env back2back 

datapath: "b2bdata" # Point it to the directory containing your reference data
testcases:

  Generate1KHzSine:
    command: sox -n /tmp/sine.wav synth 1.0 sine  1000.0
    outputs:
    - /tmp/sine.wav
```

Ouputs with supported audio file extension will be recognize
and this plugin diff will be used for them.

See [b2btest] documentation on how to use this file.



Change log
----------

### b2btest audio 1.4.0

- Audio plugin separated from b2btest package

In earlier versions this plugin was distributed
as an optional plugin in `b2btest`

### b2btest 1.3.3

- Simplified dependency on lxml

### b2btest 1.3.2

- `diffaudio` as console script
- `diffxml` as console script
- Fix: entry points for xml and audio plugins
- Just markdown README

### b2btest 1.3.1

- Updated README

### b2btest 1.3

- Avoid larg diffs by telling just the generated file with the failed results
- Fix unicode problems in certain python versions
- Using older lxml versions for python<3.5

### b2btest 1.2

- CLI: Fix: only the first output was actually checked
- Plugin based type sensitive diff
- Specific diff for XML
- XML and Audio diffing now are extras
- 'extensions' key in yaml testcases to associate custom file extensions to a diff plugin

### b2btest 1.1

- Unit test like usage for back-to-back test Python code instead of command line programs.
- New commandline tool `back2back` that takes a yaml file with the test cases definitions.

### b2btest 1.0

- First github version
- (There were previous unpublished versions)



