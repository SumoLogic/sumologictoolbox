2/14/2021
Just a few simple guidelines for now, more to come later. 

-Tim MacDonald, tmacdonald@sumologic.com

1. When contributing, always fork from the master branch, not the current default. The default branch of 
the repo will always be 1 branch older than the master. This means if you take the default clone option
you will be cloning something other than the master. 

2. Follow PEP8 ( https://www.python.org/dev/peps/pep-0008/ )

I know that the source code has a TON of PEP8 violations in it. I am working on cleaning these up slowly.
Please don't add anymore. I suggest using an editor with a built in PEP8 linter like Pycharm.

3. Tabs should not be imported into each other. If a function should be shared put it in the shared.py file.

4. all "copy" operations should be split into 2 methods, an export and an import. These export and import 
functions should reside in shared.py. All copy/backup/restore methods should leverage the import/export
functions. This way if you improve or modify export/import then all copy/backup/restore methods
will get the improvement. 