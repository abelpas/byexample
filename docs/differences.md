# Showing the differences

``byexample`` will show what are the differences between the result that
you are expecting and the result actually got

Image that you have a file with the following text:

```
$ cat <<EOF > w/license.doc
> To protect your rights, we need to prevent no-one from denying you
> these rights or asking you to surrender the rights.  Therefore, you don't have
> certain responsibilities if you distribute copies of the software, or if
> you modify it: responsibilities to respect the freedom of others.
> EOF

```

Now let's image that you also have a document/test about GPL license
that checks that file:

```
$ cat <<EOF > w/wiki-about-license.doc
> Let's check a GPL license file
>
> $ cat w/license.doc
> To protect your rights, we need to prevent others from denying you
> these rights or asking you to surrender the rights.  Therefore, you have
> certain responsibilities if you distribute copies of the software, or if
> you modify it: responsibilities to respect the freedom of others.
>
> EOF

```

We can corroborate that the test passes or not running ``byexample``

```
$ byexample --pretty none -l shell w/wiki-about-license.doc
<...>
Expected:
To protect your rights, we need to prevent others from denying you
these rights or asking you to surrender the rights.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.
Got:
To protect your rights, we need to prevent no-one from denying you
these rights or asking you to surrender the rights.  Therefore, you don't have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.
<...>

```

Do you see where are the typos/errors?

By default ``byexample`` shows the two strings, the expected and the got.

For small strings is enough to spot the differences but for larger blobs
like this one is a little harder.

For this reason ``byexample`` allows you to change the diff algorithm:

```
$ byexample --pretty none -l shell --diff ndiff w/wiki-about-license.doc   # byexample: +rm=~
<...>
Differences:
- To protect your rights, we need to prevent others from denying you
?                                             ^^ --
~
+ To protect your rights, we need to prevent no-one from denying you
?                                            + ^^^
~
- these rights or asking you to surrender the rights.  Therefore, you have
+ these rights or asking you to surrender the rights.  Therefore, you don't have
?                                                                    ++++++
~
  certain responsibilities if you distribute copies of the software, or if
  you modify it: responsibilities to respect the freedom of others.
<...>

```

Now it is easier: someone replaced 'others' by 'no-one' and put a 'don't' to
negate some sentence.

``ndiff`` is better to spot this kind little typos.

## Guessing the tags

Now in the practice what your example may contain tags
like ``<...>`` or ``<foo>``.

Those are used to ignore long uninteresting strings or to capture specific
ones.

So let's change the example to be more realistic with some tags:

```
$ cat <<EOF > w/wiki-about-license.doc
> Let's check a GPL license file
>
> $ cat w/license.doc
> To protect <protect>, we need to prevent others from <prevent1>
> or <prevent2>.  Therefore, you have
> certain responsibilities if you distribute copies of the software, or if
> you modify it: <responsibilities>.
>
> EOF

```

```
$ byexample --pretty none -l shell w/wiki-about-license.doc
<...>
Captured:
    protect: your rights                responsibilities: responsi ... f others
<...>
Expected:
To protect your rights, we need to prevent others from <prevent1>
or <prevent2>.  Therefore, you have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.
Got:
To protect your rights, we need to prevent no-one from denying you
these rights or asking you to surrender the rights.  Therefore, you don't have
certain responsibilities if you distribute copies of the software, or if
you modify it: responsibilities to respect the freedom of others.
<...>

```

The test fails as expected: we didn't fix the typos in the ``license.doc``.

But what it is interesting is how ``byexample`` show us the differences.

Read carefully the ``Expected`` string, notice how the tags ``<prevent1>``
and ``<prevent2>`` are there exactly as we defined in the test.

But the ``<protect>`` and ``<responsibilities>`` are not.

``byexample`` captured the fragments "your rights" and "responsibilities to
respect the freedom of others" and replaced the tags by the captured text.

This guess makes the differences shorter and more easy to spot:

```
$ byexample --pretty none -l shell --diff ndiff w/wiki-about-license.doc   # byexample: +rm=~
<...>
Captured:
    protect: your rights                responsibilities: responsi ... f others
<...>
Differences:
- To protect your rights, we need to prevent others from <prevent1>
?                                             ^^ --      ^^^^^  ^^^
~
+ To protect your rights, we need to prevent no-one from denying you
?                                            + ^^^       ^  ^^^^^^^^
~
- or <prevent2>.  Therefore, you have
+ these rights or asking you to surrender the rights.  Therefore, you don't have
  certain responsibilities if you distribute copies of the software, or if
  you modify it: responsibilities to respect the freedom of others.
<...>

```

``byexample`` sees that there is enough text surrounding the tags ``<protect>``
and ``<responsibilities>`` therefore it has confidence that the captured string
are correct and can be used to update the diff.

Keep in mind that the test is failing therefore, the captured strings
may not be correct.

## Diff algorithms

In addition to the default diff algorithm and the ``ndiff`` algorithm,
``byexample`` implements two more.

```
$ byexample -h                      # byexample: +norm-ws
usage: <byexample> [-d {none,unified,ndiff,context}] <...>

```

The ``unified`` diff algorithm:

```
$ byexample --pretty none -l shell --diff unified w/wiki-about-license.doc
<...>
Captured:
    protect: your rights                responsibilities: responsi ... f others
<...>
Differences:
@@ -1,4 +1,4 @@
-To protect your rights, we need to prevent others from <prevent1>
-or <prevent2>.  Therefore, you have
+To protect your rights, we need to prevent no-one from denying you
+these rights or asking you to surrender the rights.  Therefore, you don't have
 certain responsibilities if you distribute copies of the software, or if
 you modify it: responsibilities to respect the freedom of others.
<...>

```

And the ``context`` diff algorithm:

```
$ byexample --pretty none -l shell --diff context w/wiki-about-license.doc
<...>
Captured:
    protect: your rights                responsibilities: responsi ... f others
<...>
Differences:
*** 1,4 ****
! To protect your rights, we need to prevent others from <prevent1>
! or <prevent2>.  Therefore, you have
  certain responsibilities if you distribute copies of the software, or if
  you modify it: responsibilities to respect the freedom of others.
--- 1,4 ----
! To protect your rights, we need to prevent no-one from denying you
! these rights or asking you to surrender the rights.  Therefore, you don't have
  certain responsibilities if you distribute copies of the software, or if
  you modify it: responsibilities to respect the freedom of others.
<...>

```
