2/14/2021
Just a few simple guidelines for now, more to come later. 

-Tim MacDonald, tmacdonald@sumologic.com

1. Always issue your pull requests against the master branch. The default branch of the repo will always 
be 1 branch older than the master. This means if you take the default clone options you will be cloning 
something other than the master. 

2. Follow PEP8 ( https://www.python.org/dev/peps/pep-0008/ )

I know that the source code has a TON of PEP8 violations in it. I am working on cleaning these up slowly.
Please don't add anymore. I suggest using an editor with a built in PEP8 linter like Pycharm.

3. Tabs should strive to be independent from each other. If something needs to be shared between tabs 
put that in the shared.py file. This includes methods that import things in the org.  The the "orgs tab" 
will need access to import methods for all object types so they should go in shared.py. 


