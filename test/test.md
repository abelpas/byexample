# ``byexample`` tests

## Unit tests

The source code of ``byexample`` has some runnable documentation.
If you want to know how ``byexample`` works, it is the best place
to start.

```shell
$ pretty=none make lib-test         # byexample: +rm=~ +timeout=60
<...>
File byexample/differ.py, 17/17 test ran in <...> seconds
[PASS] Pass: 17 Fail: 0 Skip: 0
~
File byexample/expected.py, 98/98 test ran in <...> seconds
[PASS] Pass: 98 Fail: 0 Skip: 0
~
File byexample/finder.py, 56/56 test ran in <...> seconds
[PASS] Pass: 56 Fail: 0 Skip: 0
~
File byexample/options.py, 64/64 test ran in <...> seconds
[PASS] Pass: 64 Fail: 0 Skip: 0
~
File byexample/parser.py, 126/126 test ran in <...> seconds
[PASS] Pass: 126 Fail: 0 Skip: 0
<...>


```

Then, each module (Finder, Parser and Runner) provided by ``byexample`` has
a little documentation and tests as well.

```shell
$ pretty=none make modules-test         # byexample: +rm=~ +timeout=60
<...>
File byexample/modules/cpp.py, 2/2 test ran in <...> seconds
[PASS] Pass: 2 Fail: 0 Skip: 0
~
File byexample/modules/gdb.py, 2/2 test ran in <...> seconds
[PASS] Pass: 2 Fail: 0 Skip: 0
~
File byexample/modules/python.py, 3/3 test ran in <...> seconds
[PASS] Pass: 3 Fail: 0 Skip: 0
~
File byexample/modules/ruby.py, 7/7 test ran in <...> seconds
[PASS] Pass: 7 Fail: 0 Skip: 0
~
File byexample/modules/shell.py, 3/3 test ran in <...> seconds
[PASS] Pass: 3 Fail: 0 Skip: 0
<...>


```

## Integration tests

If what you are looking for is what is capable of, you definetly need
to see the README.md and the rest of the documentation in ``docs/``

```shell
$ pretty=none make docs-test         # byexample: +rm=~ +timeout=60
<...>
File CONTRIBUTING.md, 5/5 test ran in <...> seconds
[PASS] Pass: 0 Fail: 0 Skip: 5
~
File README.md, 7/7 test ran in <...> seconds
[PASS] Pass: 5 Fail: 0 Skip: 2
~
File docs/how_to_support_new_finders_and_languages.md, 35/35 test ran in <...> seconds
[PASS] Pass: 35 Fail: 0 Skip: 0
~
File docs/languages/cpp.md, 2/2 test ran in <...> seconds
[PASS] Pass: 2 Fail: 0 Skip: 0
~
File docs/languages/gdb.md, 8/8 test ran in <...> seconds
[PASS] Pass: 8 Fail: 0 Skip: 0
~
File docs/languages/ruby.md, 14/14 test ran in <...> seconds
[PASS] Pass: 14 Fail: 0 Skip: 0
~
File docs/languages/python.md, 41/41 test ran in <...> seconds
[PASS] Pass: 40 Fail: 0 Skip: 1
~
File docs/languages/shell.md, 15/15 test ran in <...> seconds
[PASS] Pass: 15 Fail: 0 Skip: 0
~
File docs/usage.md, 24/24 test ran in <...> seconds
[PASS] Pass: 23 Fail: 0 Skip: 1
~
File docs/differences.md, 10/10 test ran in <...> seconds
[PASS] Pass: 10 Fail: 0 Skip: 0
~
File docs/how_to_hook_to_events_with_concerns.md, 2/2 test ran in <...> seconds
[PASS] Pass: 2 Fail: 0 Skip: 0
<...>


```

## Coverage tests

```shell
$ pretty=none make coverage         # byexample: +pass

```