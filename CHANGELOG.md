# Changelog

## 0.17.0 - Reruns, pipeline error tracing, ruff
2026-07-26

New release is finally out!

### Adds
* Reruns by @Oxid15 in [282](https://github.com/Oxid15/cascade/pull/282)

### Changes
* Rm artifact by @Oxid15 in [280](https://github.com/Oxid15/cascade/pull/280)
* Ruff migration by @Oxid15 in [283](https://github.com/Oxid15/cascade/pull/283)

### Removes
pandera integration is now dropped

## 0.16.0 - Cascade UI is out!
2025-06-08

This release features Cascade UI support - new web-based dashboard that is native to Cascade. Learn more in the [docs](https://oxid15.github.io/cascade/en/latest/tutorials/ui.html).

### Changes
* UI by @Oxid15 in [276](https://github.com/Oxid15/cascade/pull/276)

### Fixes
* Meta prefix fixes by @Oxid15 in [277](https://github.com/Oxid15/cascade/pull/277)

### Docs
* UI docs by @Oxid15 in [278](https://github.com/Oxid15/cascade/pull/278)

## 0.15.1
2025-05-06

### Fixes

* Fix broken logging during some cascade run calls by @Oxid15 in [275](https://github.com/Oxid15/cascade/pull/275)
* Fix cascade rm artifact not working inside model lines by @Oxid15 in [275](https://github.com/Oxid15/cascade/pull/275)

### Docs

* Update index page docs by @Oxid15 in [275](https://github.com/Oxid15/cascade/pull/275)


## 0.15.0 - CLI Queries and Configuration Management
2025-04-06

### Adds
* Configs by @Oxid15 in [266](https://github.com/Oxid15/cascade/pull/266)
* CLI queries by @Oxid15 in [268](https://github.com/Oxid15/cascade/pull/268)
* Add simple confirmation before removing artifacts by @Oxid15 in [269](https://github.com/Oxid15/cascade/pull/269)

### Changes
* Replaced flatten_dict by own implementation and added tests for flatten_dict by @SlideForSlice in [265](https://github.com/Oxid15/cascade/pull/265) and @Oxid15 in [267](https://github.com/Oxid15/cascade/pull/267)
* Handle missing init calls for Dataset by @Oxid15 in [270](https://github.com/Oxid15/cascade/pull/270)
* Handle external removes by @Oxid15 in [272](https://github.com/Oxid15/cascade/pull/272)

### Special thanks to contributors

Thank you, @SlideForSlice for contributing to Cascade!

## 0.14.2
2024-08-28

### Fixes
* Fixed ApplyModifier returning Nones after v0.14.1 by @Oxid15 in [262](https://github.com/Oxid15/cascade/pull/262)

### Changes
* Adjust the library for new deepdiff 8  by @Oxid15 in [263](https://github.com/Oxid15/cascade/pull/263)

### Removes
* Remove types removed from numpy 2, releasing the version constraint by @Oxid15 in [263](https://github.com/Oxid15/cascade/pull/263)

## 0.14.1
2024-08-27

### Fixes
* Fix check for input type in ApplyModifier by @Oxid15 in [262](https://github.com/Oxid15/cascade/pull/262)
* Fix infinite iterations in CyclicSampler by @Oxid15 in [262](https://github.com/Oxid15/cascade/pull/262)

### Changes
* Remove Python 3.6 from supported versions by @Oxid15 in [262](https://github.com/Oxid15/cascade/pull/262)


## 0.14.0
2024-08-26

### Adds
* Validation system by @Oxid15 in [241](https://github.com/Oxid15/cascade/pull/241)
* Filter by @Oxid15 in [243](https://github.com/Oxid15/cascade/pull/243)
* Artifact management by @Oxid15 in [249](https://github.com/Oxid15/cascade/pull/249)
* Experiment tracking by @Oxid15 in [250](https://github.com/Oxid15/cascade/pull/250)
* Pickler update by @Oxid15 in [251](https://github.com/Oxid15/cascade/pull/251)
* Dataline by @Oxid15 in [252](https://github.com/Oxid15/cascade/pull/252)
* Lines by @Oxid15 in [253](https://github.com/Oxid15/cascade/pull/253)
* Sync meta by @Oxid15 in [247](https://github.com/Oxid15/cascade/pull/247)

### Changes
* Update CLI by @Oxid15 in [235](https://github.com/Oxid15/cascade/pull/235)
* Raise exceptions in data registrator as warnings by default by @Oxid15 in [236](https://github.com/Oxid15/cascade/pull/236)
* Allow batch size being bigger than sequence by @Oxid15 in [239](https://github.com/Oxid15/cascade/pull/239)
* Trainer update by @Oxid15 in [244](https://github.com/Oxid15/cascade/pull/244)
* Concatenator update by @Oxid15 in [246](https://github.com/Oxid15/cascade/pull/246)
* Optional log callback when creating model from line by @Oxid15 in [248](https://github.com/Oxid15/cascade/pull/248)
* Iterators by @Oxid15 in [254](https://github.com/Oxid15/cascade/pull/254)
* Description update by @Oxid15 in [255](https://github.com/Oxid15/cascade/pull/255)
* ApplyModifier with probabilities by @Oxid15 in [256](https://github.com/Oxid15/cascade/pull/256)
* Installation Extras by @Oxid15 in [257](https://github.com/Oxid15/cascade/pull/257)
* Meta fields of training time changed names to `training_started_at` and `training_ended_at` by @Oxid15 in [244](https://github.com/Oxid15/cascade/pull/244)

### Fixes
* Viewer fixes by @Oxid15 in [240](https://github.com/Oxid15/cascade/pull/240)
* Traceable bug with sync_meta idempotence is fixed by @Oxid15 in [244](https://github.com/Oxid15/cascade/pull/244)

### Removes
* Remove deprecated methods and classes by @Oxid15 in [238](https://github.com/Oxid15/cascade/pull/238)

### Deprecates
* Deprecations by @Oxid15 in [245](https://github.com/Oxid15/cascade/pull/245)
* Pickler update by @Oxid15 in [251](https://github.com/Oxid15/cascade/pull/251)

### Docs
* Docs update by @Oxid15 in [258](https://github.com/Oxid15/cascade/pull/258)

## 0.13.1 - CLI fixes
2023-12-04

### Fixes
* Fix missing CLI module by @Oxid15 in [234](https://github.com/Oxid15/cascade/pull/234)

## 0.13.0 - Large release, lots of new features
2023-11-26

This version introduces a lot of great changes including rich metadata of experiments like descriptions, comments and tags, Metrics as value and meta containers and also descriptions of computing those values, links between objects, file and model artifacts, slugs for models as well as lots of other improvements.

### Adds
* Basic CLI by @Oxid15 in [195](https://github.com/Oxid15/cascade/pull/195)
* Cli access meta by @Oxid15 in [198](https://github.com/Oxid15/cascade/pull/198)
* CLI commands by @Oxid15 in [224](https://github.com/Oxid15/cascade/pull/224)
* Improve CLI by @Oxid15 in [228](https://github.com/Oxid15/cascade/pull/228)
Cascade now introduces command line interface. The first version is simple and
allows to use viewers, comment, tag and describe objects, view meta.
* Metrics by @Oxid15 in [208](https://github.com/Oxid15/cascade/pull/208)
* Sklearn metrics by @Oxid15 in [217](https://github.com/Oxid15/cascade/pull/217)
* Improve metrics by @Oxid15 in [223](https://github.com/Oxid15/cascade/pull/223)
Metrics are new entity that helps to organize metric values, build metadata around simple numerical values
* Links by @Oxid15 in [210](https://github.com/Oxid15/cascade/pull/210)
* Write dir by @Oxid15 in [211](https://github.com/Oxid15/cascade/pull/211)
* Make absolute paths in links if possible by @Oxid15 in [229](https://github.com/Oxid15/cascade/pull/229)
* Experiment ids by @Oxid15 in [192](https://github.com/Oxid15/cascade/pull/192)
* Meta access by @Oxid15 in [199](https://github.com/Oxid15/cascade/pull/199)
* Experiment sequences by @Oxid15 in [200](https://github.com/Oxid15/cascade/pull/200)
* Comments by @Oxid15 in [202](https://github.com/Oxid15/cascade/pull/202)
* Add descriptions by @Oxid15 in [196](https://github.com/Oxid15/cascade/pull/196)
* Add tags by @Oxid15 in [197](https://github.com/Oxid15/cascade/pull/197)
* Rename methods and merge them by @Oxid15 in [203](https://github.com/Oxid15/cascade/pull/203)
* Separate artifacts from wrappers by @Oxid15 in [193](https://github.com/Oxid15/cascade/pull/193)
* File artifacts by @Oxid15 in [194](https://github.com/Oxid15/cascade/pull/194)

### Changes
* Version to py file by @Oxid15 in [201](https://github.com/Oxid15/cascade/pull/201)
* Handle fit eval errors in trainer by @Oxid15 in [204](https://github.com/Oxid15/cascade/pull/204)
* Lazy Repo by @Oxid15 in [206](https://github.com/Oxid15/cascade/pull/206)
* ModelLine handles saving errors by @Oxid15 in [207](https://github.com/Oxid15/cascade/pull/207)
* Meta from folder by @Oxid15 in [209](https://github.com/Oxid15/cascade/pull/209)
* Version management by @Oxid15 in [212](https://github.com/Oxid15/cascade/pull/212)
* Unify container interface by @Oxid15 in [213](https://github.com/Oxid15/cascade/pull/213)
* Improve line by @Oxid15 in [214](https://github.com/Oxid15/cascade/pull/214)
* History in diffs by @Oxid15 in [215](https://github.com/Oxid15/cascade/pull/215)
* Improve HV by @Oxid15 in [227](https://github.com/Oxid15/cascade/pull/227)
* Separate tests by submodule by @Oxid15 in [216](https://github.com/Oxid15/cascade/pull/216)
* Improve meta prefix by @Oxid15 in [226](https://github.com/Oxid15/cascade/pull/226)
* Versioning by @Oxid15 in [230](https://github.com/Oxid15/cascade/pull/230)
* Links by @Oxid15 in [210](https://github.com/Oxid15/cascade/pull/210)
* Write dir by @Oxid15 in [211](https://github.com/Oxid15/cascade/pull/211)
* Make absolute paths in links if possible by @Oxid15 in [229](https://github.com/Oxid15/cascade/pull/229)

### Fixes
* Meta writing fixes by @Oxid15 in [221](https://github.com/Oxid15/cascade/pull/221)
* Fix type diffs by @Oxid15 in [225](https://github.com/Oxid15/cascade/pull/225)


### Removes
* Do not store all file names in meta of folder dataset by @Oxid15 in [191](https://github.com/Oxid15/cascade/pull/191)
* `meta_prefix` was removed from constructors and update_meta no longer accepts path to files, to migrate use `link`s

## 0.12.1 - Security release
2023-11-06

### Changes
* Optimize HV by @Oxid15 in [205](https://github.com/Oxid15/cascade/pull/205)

### Fixes
* Handle fit eval errors in trainer by @Oxid15 in [204](https://github.com/Oxid15/cascade/pull/204)
* v0.12.1 - Security fixes and minor improvements by @Oxid15 in [222](https://github.com/Oxid15/cascade/pull/222)

### Special thanks to contributors

Thank you, @zer0h-bb for contribution in finding security issues!

## 0.12.0 - Major update!
2023-07-14

Version 0.12.0 brings a lot of improvements and new functionality, restructures `utils` even more than 0.11.0 and becomes a last milestone before even bigger changes!

Attention! Some changes are breaking when switching from 0.11.1

### Adds
* Unify repos and lines by @Oxid15 in [166](https://github.com/Oxid15/cascade/pull/166)
* Unify line and repo by @Oxid15 in [176](https://github.com/Oxid15/cascade/pull/176)
* Feature table by @Oxid15 in [173](https://github.com/Oxid15/cascade/pull/173)
* Dataset server by @Oxid15 in [175](https://github.com/Oxid15/cascade/pull/175)
* Workspace by @Oxid15 in [177](https://github.com/Oxid15/cascade/pull/177)
* Iterator modifier by @Oxid15 in [183](https://github.com/Oxid15/cascade/pull/183)
* Simple dataloader by @Oxid15 in [187](https://github.com/Oxid15/cascade/pull/187)
* Do not create MetaHandler to use it by @Oxid15 in [169](https://github.com/Oxid15/cascade/pull/169)

### Changes
* Folder improv by @Oxid15 in [156](https://github.com/Oxid15/cascade/pull/156)
* Update HistoryViewer by @Oxid15 in [161](https://github.com/Oxid15/cascade/pull/161)
* Unify repos and lines by @Oxid15 in [166](https://github.com/Oxid15/cascade/pull/166)
* Save model by @Oxid15 in [168](https://github.com/Oxid15/cascade/pull/168)
* Diff view layout by @Oxid15 in [171](https://github.com/Oxid15/cascade/pull/171)
* Model save load by @Oxid15 in [172](https://github.com/Oxid15/cascade/pull/172)
* Format base by @Oxid15 in [174](https://github.com/Oxid15/cascade/pull/174)
* New model load by @Oxid15 in [180](https://github.com/Oxid15/cascade/pull/180)
* Constant update by @Oxid15 in [185](https://github.com/Oxid15/cascade/pull/185)
* Image folder backends by @Oxid15 in [186](https://github.com/Oxid15/cascade/pull/186)
* PIL backend update by @Oxid15 in [188](https://github.com/Oxid15/cascade/pull/188)
* Move Dataset's repr up to the Traceable by @Oxid15 in [162](https://github.com/Oxid15/cascade/pull/162)

### Fixes
* Check if model already exists to not overwrite in line by @Oxid15 in [179](https://github.com/Oxid15/cascade/pull/179)
* Line ordering hv by @Oxid15 in [167](https://github.com/Oxid15/cascade/pull/167)
* Fix HistoryViewer by @Oxid15 in [160](https://github.com/Oxid15/cascade/pull/160)
* Do not duplicate repo's meta prefix in line meta by @Oxid15 in [163](https://github.com/Oxid15/cascade/pull/163)

### Removes
* Remove logging in repo by @Oxid15 in [184](https://github.com/Oxid15/cascade/pull/184)
* Utils restructure by @Oxid15 in [181](https://github.com/Oxid15/cascade/pull/181)

### Docs
* Docs update by @Oxid15 in [182](https://github.com/Oxid15/cascade/pull/182)

## 0.11.2-alpha - Utility release
2023-06-05

This is the release to get the badge

## 0.11.1 - Update with bugfixes
2023-04-23

### Changes

* Improve errors by @Oxid15 in [159](https://github.com/Oxid15/cascade/pull/159)

### Fixes
* Fix last_models showing order was reversed by @Oxid15 in [157](https://github.com/Oxid15/cascade/pull/157)
* Fix history logging when no logging setting is set by @Oxid15 in [158](https://github.com/Oxid15/cascade/pull/158)

## 0.11.0 - Goodbye, cdu!
2023-03-30

This version separates cascade.utils into several submodules which are now to be used individually.
This changes the API of utils, but given the wide range of tools and their dependencies, it releases the constraint of having all of them installed at once for the user to use certain feature.

No other changes introduced in this release intentionally to make it a transfer point - users can stay at 0.10.0 until they will adapt to the new API and still use the same new features.

### Removes
* v0.11.0 - Goodbye cdu! by @Oxid15 in [155](https://github.com/Oxid15/cascade/pull/155)

## 0.10.0 - Update
2023-03-01

New Cascade version is here! New metadata viewing tools are now available, tools for logging object states and more

- Important - version log format in `VersionAssigner` changed and old logs are now not supported
- Important - plotly is now an optional dependency

### Adds
* Dataset history by @Oxid15 in [148](https://github.com/Oxid15/cascade/pull/148)
* View history by @Oxid15 in [149](https://github.com/Oxid15/cascade/pull/149)
* View diffs in version logs by @Oxid15 in [151](https://github.com/Oxid15/cascade/pull/151)
* Choose metric in HistoryViewer by @Oxid15 in [150](https://github.com/Oxid15/cascade/pull/150)
* Add .yaml as format that also supported since it is another name of YAML by @Oxid15 in [143](https://github.com/Oxid15/cascade/pull/143)

### Changes
* More thorough typing, especially with meta by @Oxid15
* Optional plotly by @Oxid15 in [142](https://github.com/Oxid15/cascade/pull/142)
* Meta typing by @Oxid15 in [144](https://github.com/Oxid15/cascade/pull/144)
* ModelRepo logging by @Oxid15 in [145](https://github.com/Oxid15/cascade/pull/145)
* Data registration by @Oxid15 in [146](https://github.com/Oxid15/cascade/pull/146)
* Dataset history by @Oxid15 in [148](https://github.com/Oxid15/cascade/pull/148)
* View history by @Oxid15 in [149](https://github.com/Oxid15/cascade/pull/149)
* Choose metric in HistoryViewer by @Oxid15 in [150](https://github.com/Oxid15/cascade/pull/150)
* View diffs in version logs by @Oxid15 in [151](https://github.com/Oxid15/cascade/pull/151)

### Fixes
* Fix weighed sampler by @Oxid15 in [147](https://github.com/Oxid15/cascade/pull/147)

### Docs
* Update README by @Oxid15 in [140](https://github.com/Oxid15/cascade/pull/140)
* Documentation update by @Oxid15 in [141](https://github.com/Oxid15/cascade/pull/141)

## 0.9.0 - Stability update
2022-12-16

New Cascade version is here - now it is an update that enhances stability and reliability of the package. New bugfixes, improved error messages, dataset versioning, more thorough testing.

### Adds
* Pipeline structure by @Oxid15 in [137](https://github.com/Oxid15/cascade/pull/137)
* Write pipeline as object in log and not string by @Oxid15 in [138](https://github.com/Oxid15/cascade/pull/138)
- The notion of `SizedDataset` which should solve the inconsistencies with Dataset interface that has no `__len__` method
* More useful constant by @Oxid15 in [135](https://github.com/Oxid15/cascade/pull/135)
* Time series meta by @Oxid15 in [136](https://github.com/Oxid15/cascade/pull/136)

### Changes

* Better typing in all modules, parameters and methods
* Better code formatting
* `RangeSampler` now more protected against non-intended usage
* `split` now more protected against missing parameters
* `HistoryVIewer`'s work with lines
* `MetricViewer.get_best_by` method is now informs that it does not work with non-sortable metrics
* `BasicTrainer.train` protected against missing `test_ds` when `eval_strategy` provided
* `YAMLHandler` now raises an error if reading an empty file

### Fixes
* Copyright notices added where missing
* The problem in `UnderSampler` with repeating elements
* The problem in `WeighedSampler` with string labels

## 0.8.0
2022-11-15

New Cascade version at last!
0.8.0 brings some useful changes and improvements

### Adds
* Improve repo by @Oxid15 in [104](https://github.com/Oxid15/cascade/pull/104)
* Improve trainer by @Oxid15 in [107](https://github.com/Oxid15/cascade/pull/107)
* SkModel hash check  by @Oxid15 in [111](https://github.com/Oxid15/cascade/pull/111)
* The way to get dataset from pickler by @Oxid15 in [113](https://github.com/Oxid15/cascade/pull/113)
* Auto name new line by @Oxid15 in [114](https://github.com/Oxid15/cascade/pull/114)
* Auto data versioning by @Oxid15 in [112](https://github.com/Oxid15/cascade/pull/112)
* Composer by @Oxid15 in [121](https://github.com/Oxid15/cascade/pull/121)
* Weighed sampler by @Oxid15 in [125](https://github.com/Oxid15/cascade/pull/125)
* Add DataleakValidator by @Oxid15 in [126](https://github.com/Oxid15/cascade/pull/126)

### Changes
* Improve trainer by @Oxid15 in [107](https://github.com/Oxid15/cascade/pull/107)
* Improve repo performace by @Oxid15 in [109](https://github.com/Oxid15/cascade/pull/109)
* Refactor and update docs by @Oxid15 in [116](https://github.com/Oxid15/cascade/pull/116)
- Under- and OverSampler

### Removes
* Improve repo performace by @Oxid15 in [109](https://github.com/Oxid15/cascade/pull/109)
* Improve repo by @Oxid15 in [104](https://github.com/Oxid15/cascade/pull/104)
* Drop deprecated by @Oxid15 in [110](https://github.com/Oxid15/cascade/pull/110)

### Docs
* Refactor and update docs by @Oxid15 in [116](https://github.com/Oxid15/cascade/pull/116)

## 0.7.3 - Patch and new docs
2022-10-06

### Changes
* Update versions of requirements, make them more compatible by @Oxid15 in [117](https://github.com/Oxid15/cascade/pull/117)

### Fixes
* Patch Concatenator's meta by @Oxid15 in [119](https://github.com/Oxid15/cascade/pull/119)

### Docs
* Update docs by @Oxid15 in [118](https://github.com/Oxid15/cascade/pull/118)

## 0.7.2 - Patch and docs update
2022-09-29

### Docs
* Add trainers example by @Oxid15 in [115](https://github.com/Oxid15/cascade/pull/115)
* Refactor and update docs by @Oxid15 in [116](https://github.com/Oxid15/cascade/pull/116)

## 0.7.1 - Patch
2022-09-23

### Adds
* Add message in HistoryViewer by @Oxid15 in [106](https://github.com/Oxid15/cascade/pull/106)

### Docs
* Docs update by @Oxid15 in [105](https://github.com/Oxid15/cascade/pull/105)

## 0.7.0
2022-09-05

### Adds
* Model line only meta by @Oxid15 in [83](https://github.com/Oxid15/cascade/pull/83)
* Add lines and models constraints by @Oxid15 in [85](https://github.com/Oxid15/cascade/pull/85)
* Split dataset by @Oxid15 in [86](https://github.com/Oxid15/cascade/pull/86)
* Viewers live update by @Oxid15 in [87](https://github.com/Oxid15/cascade/pull/87)
* Improve random sampler by @Oxid15 in [92](https://github.com/Oxid15/cascade/pull/92)
* Trainers by @Oxid15 in [95](https://github.com/Oxid15/cascade/pull/95)
* Improve validators by @Oxid15 in [99](https://github.com/Oxid15/cascade/pull/99)

### Changes
* Refactor - make some fields protected by @Oxid15 in [84](https://github.com/Oxid15/cascade/pull/84)
* More reliable repos by @Oxid15 in [90](https://github.com/Oxid15/cascade/pull/90)
* Optimize ModelLine
* Refactor by @Oxid15 in [91](https://github.com/Oxid15/cascade/pull/91)
* Robust meta handling by @Oxid15 in [93](https://github.com/Oxid15/cascade/pull/93)
* Error robustness by @Oxid15 in [100](https://github.com/Oxid15/cascade/pull/100)

### Fixes
* More reliable repos by @Oxid15 in [90](https://github.com/Oxid15/cascade/pull/90)
* Fix MetricVIewer by @Oxid15 in [94](https://github.com/Oxid15/cascade/pull/94)

### Removes
* Model line only meta by @Oxid15 in [83](https://github.com/Oxid15/cascade/pull/83)
* Drop model agg by @Oxid15 in [97](https://github.com/Oxid15/cascade/pull/97)

### Docs
* Update docs by @Oxid15 in [98](https://github.com/Oxid15/cascade/pull/98)

## 0.6.2 - Patch release
2022-08-05

### Fixes
* Patch by @Oxid15 in [89](https://github.com/Oxid15/cascade/pull/89)

## 0.6.1 - Patch
2022-08-01

### Fixes
* Bug when all columns missing except num and line in MetricViewer's serve by @Oxid15 in [82](https://github.com/Oxid15/cascade/pull/82)

## 0.6.0
2022-07-31

### Adds
* Add TorchModel by @Oxid15 in [68](https://github.com/Oxid15/cascade/pull/68)

### Changes
* Dates are now dates and not just strings by @Oxid15 in [62](https://github.com/Oxid15/cascade/pull/62)
* Update meta from file by @Oxid15 in [63](https://github.com/Oxid15/cascade/pull/63)
* Update tests by @Oxid15 in [64](https://github.com/Oxid15/cascade/pull/64)
* Model update by @Oxid15 in [70](https://github.com/Oxid15/cascade/pull/70)
* Abstract from json by @Oxid15 in [66](https://github.com/Oxid15/cascade/pull/66)
* Serve args by @Oxid15 in [71](https://github.com/Oxid15/cascade/pull/71)
* Concatenator's meta is now dict by @Oxid15 in [74](https://github.com/Oxid15/cascade/pull/74)
* TorchModel now has graph description in meta by @Oxid15 in [75](https://github.com/Oxid15/cascade/pull/75)
* Repo summing by @Oxid15 in [76](https://github.com/Oxid15/cascade/pull/76)
* Metric viewer update by @Oxid15 in [77](https://github.com/Oxid15/cascade/pull/77)
* Utils update by @Oxid15 in [78](https://github.com/Oxid15/cascade/pull/78)
* Use fixtures by @Oxid15 in [65](https://github.com/Oxid15/cascade/pull/65)

### Fixes
* Debug num in mv by @Oxid15 in [73](https://github.com/Oxid15/cascade/pull/73)

### Removes
* Drop skclassifier by @Oxid15 in [67](https://github.com/Oxid15/cascade/pull/67)

### Docs
* Update docs by @Oxid15 in [69](https://github.com/Oxid15/cascade/pull/69)
* Docs update by @Oxid15 in [79](https://github.com/Oxid15/cascade/pull/79)

## 0.5.2 - Patch release
2022-06-29

### Adds
* Adds sorting of model names in ModelLine (which was needed to be noticed and added long ago...) by @Oxid15 in [61](https://github.com/Oxid15/cascade/pull/61)

### Changes
* Refreshes SkModel interface by @Oxid15 in [61](https://github.com/Oxid15/cascade/pull/61)

### Fixes
* Fixes the bug in legacy repos handling in MetricViewer by @Oxid15 in [61](https://github.com/Oxid15/cascade/pull/61)
* Fixes the behavior of RandomSampler by @Oxid15 in [61](https://github.com/Oxid15/cascade/pull/61)
* Prevents the recording of meta_prefix in parameters of Model by @Oxid15 in [61](https://github.com/Oxid15/cascade/pull/61)


## 0.5.1
2022-06-25

Hotfix of forgotten ModelModifier

### Fixes
* Patch typo by @Oxid15 in [60](https://github.com/Oxid15/cascade/pull/60)

## 0.5.0
2022-06-25

* Dash is now conditional dependency
* Fixes SkModel's evaluate error
* MetricViewer now flattens parameters
* HistoryViewer now also flattens params

### Adds
* History logging for ModelRepo
* RandomSampler
* Table Validation
* Base class - Traceable
* Meta prefix from file
* ModelModifier
* ModelModifier by @Oxid15 in [59](https://github.com/Oxid15/cascade/pull/59)

### Changes
* Random sampler by @Oxid15 in [47](https://github.com/Oxid15/cascade/pull/47)
* Refine meta by @Oxid15 in [48](https://github.com/Oxid15/cascade/pull/48)
* Dash conditional by @Oxid15 in [49](https://github.com/Oxid15/cascade/pull/49)
* Repo history by @Oxid15 in [50](https://github.com/Oxid15/cascade/pull/50)
* Refine metric viewer by @Oxid15 in [51](https://github.com/Oxid15/cascade/pull/51)
* Swap true and pred in SKModel evaluate by @Oxid15 in [52](https://github.com/Oxid15/cascade/pull/52)
* Flatten in MetricViewer by @Oxid15 in [53](https://github.com/Oxid15/cascade/pull/53)
* History viewer update by @Oxid15 in [55](https://github.com/Oxid15/cascade/pull/55)
* Base classes by @Oxid15 in [56](https://github.com/Oxid15/cascade/pull/56)

### Fixes
* Fix meta viewer by @Oxid15 in [54](https://github.com/Oxid15/cascade/pull/54)
* Prefix from file by @Oxid15 in [57](https://github.com/Oxid15/cascade/pull/57)

## 0.4.2 - Patch
2022-06-23

### Fixes
* Fix samplers inheritance error by @Oxid15 in [43](https://github.com/Oxid15/cascade/pull/43)
* Fix Wrappers meta by @Oxid15 in [44](https://github.com/Oxid15/cascade/pull/44)
* Missing super calls and args by @Oxid15 in [45](https://github.com/Oxid15/cascade/pull/45)

## 0.4.1
2022-06-18

* Fixed bug when call get_meta of Concatenator
* Unified Validator's Inteface with Dataset's

### Fixes
* 0.4.1 by @Oxid15 in [42](https://github.com/Oxid15/cascade/pull/42)

## 0.4.0 - 0.4.0
2022-06-10

- MetricViewer now has dash-based web-interface!
- MetaHandler now writes human-readable meta and can be set to not overwrite it
- ModelRepo now does not overwrite previously written on disk meta, only updates it
- Adds data validation by means of pandera's schema API
- Adds NullValidator with very detailed report on where NaNs occured in your dataset, when you didn't want them to be there
- Extends documentation

### Changes
* Metric viewer update by @Oxid15 in [37](https://github.com/Oxid15/cascade/pull/37)
* Update repos meta by @Oxid15 in [39](https://github.com/Oxid15/cascade/pull/39)
* Meta handler update by @Oxid15 in [38](https://github.com/Oxid15/cascade/pull/38)
* Table validation by @Oxid15 in [41](https://github.com/Oxid15/cascade/pull/41)

## 0.3.3
2022-05-23

### Changes
* 0.3.3 by @Oxid15 in [36](https://github.com/Oxid15/cascade/pull/36)

## 0.3.2 - PyPI publication and json backend fixed
2022-05-23

### Changes
* 0.3.2 by @Oxid15 in [35](https://github.com/Oxid15/cascade/pull/35)

## 0.3.1 - Patch
2022-05-19

### Fixes
* Bugfixes by @Oxid15 in [33](https://github.com/Oxid15/cascade/pull/33)

## 0.3.0
2022-05-18

* Extended documentation that is still WIP, but already exists!
* Setuptools configured to be able to just pip install package!
* Cascade utils are now kind of separate package
* Notion of SkModel instead of SkClassifier
* Meta handling for Repos and Lines
* Adds ModelAggregate
* Adds NumpyWrapper
* Adds to_pandas to TimeSeriesDataset

### Adds
* Make pip-installable package by @Oxid15 in [21](https://github.com/Oxid15/cascade/pull/21)

### Changes
* Cascade utils setup by @Oxid15 in [24](https://github.com/Oxid15/cascade/pull/24)
* SkModel by @Oxid15 in [25](https://github.com/Oxid15/cascade/pull/25)
* Time series to pd by @Oxid15 in [26](https://github.com/Oxid15/cascade/pull/26)
* Meta changes by @Oxid15 in [27](https://github.com/Oxid15/cascade/pull/27)
* Model aggregate by @Oxid15 in [29](https://github.com/Oxid15/cascade/pull/29)
* NumpyWrapper and such by @Oxid15 in [30](https://github.com/Oxid15/cascade/pull/30)
* 0.3.0 by @Oxid15 in [32](https://github.com/Oxid15/cascade/pull/32)

### Fixes
* Root prefix by @Oxid15 in [23](https://github.com/Oxid15/cascade/pull/23)

### Docs
* Extend docs by @Oxid15 in [28](https://github.com/Oxid15/cascade/pull/28)
* Extend docs by @Oxid15 in [31](https://github.com/Oxid15/cascade/pull/31)

## 0.2.1 - First patch
2022-05-03

### Changes
* 0.2.1 by @Oxid15 in [19](https://github.com/Oxid15/cascade/pull/19)

## 0.2.0 - 0.2.0
2022-05-02

### Adds
* Model repo accepts cls only in add_line by @Oxid15 in [8](https://github.com/Oxid15/cascade/pull/8)
* Tables new interface by @Oxid15 in [15](https://github.com/Oxid15/cascade/pull/15)

### Changes
* Meta validation by @Oxid15 in [4](https://github.com/Oxid15/cascade/pull/4)
* Time series dataset by @Oxid15 in [5](https://github.com/Oxid15/cascade/pull/5)
* Log model's params by @Oxid15 in [6](https://github.com/Oxid15/cascade/pull/6)
* Different meta classes by @Oxid15 in [7](https://github.com/Oxid15/cascade/pull/7)
* Repo update by @Oxid15 in [10](https://github.com/Oxid15/cascade/pull/10)
* Meta in hidden folder by @Oxid15 in [11](https://github.com/Oxid15/cascade/pull/11)
* Metric viz by @Oxid15 in [12](https://github.com/Oxid15/cascade/pull/12)
* Time series by @Oxid15 in [14](https://github.com/Oxid15/cascade/pull/14)
* Models in separate folder by @Oxid15 in [16](https://github.com/Oxid15/cascade/pull/16)
* 0.2.0 by @Oxid15 in [18](https://github.com/Oxid15/cascade/pull/18)

### Fixes
* Add meta prefix to Dataset and Model by @Oxid15 in [9](https://github.com/Oxid15/cascade/pull/9)
* Patch by @Oxid15 in [13](https://github.com/Oxid15/cascade/pull/13)
* Patch by @Oxid15 in [17](https://github.com/Oxid15/cascade/pull/17)

## 0.1.0 - 0.1.0 - First release
2022-04-06
