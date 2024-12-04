# Change log


## b2btest audio 1.4.0

- Audio plugin separated from b2btest package

In earlier versions this plugin was distributed
as an optional plugin in `b2btest`

## b2btest 1.3.3

- Simplified dependency on lxml

## b2btest 1.3.2

- `diffaudio` as console script
- `diffxml` as console script
- Fix: entry points for xml and audio plugins
- Just markdown README

## b2btest 1.3.1

- Updated README

## b2btest 1.3

- Avoid larg diffs by telling just the generated file with the failed results
- Fix unicode problems in certain python versions
- Using older lxml versions for python<3.5

## b2btest 1.2

- CLI: Fix: only the first output was actually checked
- Plugin based type sensitive diff
- Specific diff for XML
- XML and Audio diffing now are extras
- 'extensions' key in yaml testcases to associate custom file extensions to a diff plugin

## b2btest 1.1

- Unit test like usage for back-to-back test Python code instead of command line programs.
- New commandline tool `back2back` that takes a yaml file with the test cases definitions.

## b2btest 1.0

- First github version
- (There were previous unpublished versions)

