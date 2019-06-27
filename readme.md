Sumotoolbox
===========

 Sumotoolbox is a GUI utility for accessing the various Sumo Logic APIs (currently the search, content and collector
 APIs.) The idea is to make it easier to perform common API tasks such as copying
 sources and generating CSV files from searches.

Using Sumotoolbox
=================

The easiest way to use sumotoolbox is to look in the "dist" directory of this repo and grab the executable for your 
platform. Run the executable, pick your region, enter your creds, and start using the tool. 

Note: The executables are built for 64-bit only and may not run on less than current operating systems. 
In the case of Windows my build is for a very recent version of Windows 10 and has failed to work on older versions.
Unfortunately I do not have access to an older version of Windows 10 to build against. If it doesn't work your only
option may be to install the source as described below. 

Installing the Source
=====================

If you prefer to clone the archive and run from source then you'll need Python 3.6 or higher and the modules listed 
in the dependency section.  

The steps are as follows: 

1. Download and install python 3.6 or higher from python.org. Make sure to choose the "add python to the default 
path" checkbox in the installer (may be in advanced settings.)

    If you have Linux you can skip this step, but ensure you have python3 installed for your distro. 

    If you have OS X you cannot use the python that comes with the OS, it is too old.

2. Open a new shell

3. execute the following command to install pipenv, which will manage all of the library dependencies for us:

    pip3 install pipenv
 
4. Download this repo (either as a zip from the main repo download link or using git.) Unzip if you downloaded the zip. 
5. Change to the directory in which you installed sumotoolbox. Type the following to install all the package 
    dependencies (this may take a while as this will download all of the libraries that sumotoolbox uses:

    pipenv install
    
6. Finally, to run sumotoolbox type:

    pipenv run python3 sumotoolbox.py

Dependencies
============

See the contents of "pipfile"

Features and Usage
==================

Collector Source Copying:

    1. Input Credentials for your source and destination orgs
    2. Select your regions for source and destination orgs
    3. Click "Update" for source and destination to populate the collector lists
    4. Choose a source collector to populate the sources list.
    5. Select one or more sources
    6. Select a destination collector
    7. Click "Copy".

    NOTE: You can use the same credentials for both source and destination to copy sources from one collector to another
    within the same org.

Collector Backup:

    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" to populate the collector list
    4. Choose one or more collectors
    5. Click 'Backup Collector(s)' to write a json dump of the selected collectors and their sources
    
    NOTE: There is not currently a collector restore capability in this tool. 

Collector Delete:

    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" for destination to populate the collector list
    4. Choose one or more collectors
    6. Click "Delete Collector(s)"
    7. Verify that you really want to delete the collector(s) by typing "DELETE"
    8. Click "OK"
    
    NOTE: This can be very dangerous. Accidentally deleting the wrong collector(s) could result
    in log collection interruption and many, many hours of restoration work. Use with EXTREME
    caution. 
    
Source Delete:

    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" for destination to populate the collector list
    4. Choose a collector
    5. Choose one or more sources
    6. Click "Delete Source(s)"
    7. Verify that you really want to delete the source(s) by typing "DELETE"
    8. Click "OK"

    NOTE: This can be very dangerous. Accidentally deleting the wrong sources(s) could result in log
    collection interruption and many, many hours of restoration work. Use with EXTREME caution. 
    
Search API:

    1. Input source credentials
    2. Select your source region
    3. Select your timezone (defaults to local system timezone)
    4. Select your time range (defaults to a relative 15 minute window from the time
    the app was launched)
    5. Enter a valid Sumo Logic search query
    6. Select whether you want to see message results or record results (raw messages
    vs. aggregate data.)
    7. (Optional) Check "Save to CSV" to create a CSV file from the results
    8. (Optional) Check "Convert to Selected Timezone from UTC Epoch". This will return message
    times and "_timeslice"fields as local time formatted as %Y-%m-%d %H:%M:%S rather than 
    UTC epoch time.
    9. Click "Start"
    
    NOTE: The use case for this fuctionality is dumping to CSV. The Sumo Logic UI export feature is
    currently limited to 100,000 log messages. This tool should reliably dump much more than that,
    however the UI will "freeze" during the dump. This could take minutes or even hours depending 
    on the size of the dump. Please resist the temptation to rage quit because of an unresposive UI. 

Content Folder Creation:    !NEW!
    
    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" for destination to populate the collector list
    4. (Optional) Select "Personal Folder" or "Admin Recommended" radio button to switch context
    4. Navigate to the location you want to create the new folder. 
    6. Click "New Folder".
    7. Enter a name for the new folder. 
    8. Click "OK"
    
    NOTE: You cannot create top level folders when in the "Admin Recommeded" context. This
    should be fixed in the future. 
    
    NOTE: Global folder browsing (other peoples shares) is currently disabled. Look for that in a future release. 
    
Content Deletion:    !NEW!
    
    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" for destination to populate the collector list
    4. (Optional) Select "Personal Folder" or "Admin Recommended" radio button to switch context
    4. Navigate to the location that contains the content you wish to delete. 
    6. Select one or more items from the list. 
    7. Click "Delete"
    7. Verify that you really want to delete the source(s) by typing "DELETE"
    8. Click "OK"
    
    NOTE: You cannot delete top level folders when in the "Admin Recommeded" context. This
    should be fixed in the future. 
    
    NOTE: This can be very dangerous. Accidentally deleting the wrong content could result in serious issues and
    many hours of restoration work. Use with EXTREME caution. 
    
    NOTE: Global folder browsing (other peoples shares) is currently disabled. Look for that in a future release.   

Content Copying:    !NEW!

    1.  Input Credentials for your source and destination orgs
    2. Select your regions for source and destination orgs
    3. Click "Update" for source and destination to populate the content lists
    4. (Optional) Select "Personal Folder" or "Admin Recommended" radio button to switch context in either pane. 
    5. Select one or more items from the list
    6. Click "Copy" (left to right or right to left). Your content will be copied to the current folder in the
    destination pane.
    
Content Find/Replace/Copy:  !EXPERIMENTAL!

    Copying content between orgs often requires that the sourceCategory tags be changed to match the new 
    environment. The Find/Replace/Copy feature is intended to lighten this burden by doing sourceCategory
    tag replacement during the copy. It finds all of the sourceCategory tags in your original content and presents
    them to you along with the sourceCategory tags in your destination environment allowing you to match them for
    replacement.
    
    1.  Input Credentials for your source and destination orgs
    2. Select your regions for source and destination orgs
    3. Click "Update" for source and destination to populate the content lists
    4. (Optional) Select "Personal Folder" or "Admin Recommended" radio button to switch context in either pane. 
    5. Select one or more items from the list
    6. Click "Find/Replace/Copy" (left to right or right to left). 
    7. Wait a bit (the REST calls involved can take a while)
    8. Choose what tags to replace. 
    9. Click "OK"
    10. Wait a bit (lot) more. If you are copying large amounts of content the wait can be significant. The UI will
    seem to freeze or lockup during the copy because the tool is not multithreaded. Have patience and resist the urge
    to rage quit, it's still a million times faster than doing this by hand.
    11. Once the pop-up window closes your content should be copied to the current folder in the destination pane.
    
Content Backup: !New!

    1.  Input Credentials for your source and destination orgs
    2. Select your regions for source and destination orgs
    3. Click "Update" for source and destination to populate the content lists
    4. (Optional) Select "Personal Folder" or "Admin Recommended" radio button to switch context in either pane. 
    5. Select one or more items from the list
    6. Click "Backup"
    7. Choose a folder to save your backup files into
    8. The selected content will be exported and written as JSON to the selected folder, one file per selected item. 
    
    Note: The filenames are created automatically from the item names that are selected for backup. 
    
Content Restore: !New!

    1.  Input Credentials for your source and destination orgs
    2. Select your regions for source and destination orgs
    3. Click "Update" for source and destination to populate the content lists
    4. (Optional) Select "Personal Folder" or "Admin Recommended" radio button to switch context in either pane. 
    5. Navigate to the folder you wish to restore into. 
    6. Click "Restore"
    7. Select one or more valid Sumo Logic exports files to restore. These must be valid JSON that has been 
    previously exported from Sumo Logic, either using this tool, the API, or the Sumo Logic UI. 
    8. Your content will be restored into the current directory. 
    
    Note: You cannot currently restore into the root admin folder. This will be fixed soon.     

Logging:    !NEW!

    The tool should now generate a "sumologic.log" file in the directory it lives in. If you experience a bug, which is
    likely, please delete the log file, recreate the bug, and send me the new log file along with a screenshot and/or 
    description or what you were doing at the time. I can't promise an immediate fix but I will do my best.
    
    tmacdonald@sumologic.com
   
    
    

Screen Shots:
=============

![Collector Source Copy](https://github.com/voltaire321/sumologictoolbox/blob/master/screenshots/sumotoolbox_collector_example.png "Source Copy")

![Search API Example](https://github.com/voltaire321/sumologictoolbox/blob/master/screenshots/sumotoolbox_search_example.png "Search API")

![Content API Example](https://github.com/voltaire321/sumologictoolbox/blob/master/screenshots/sumotoolbox_content_example.png "Search API")

Known Issues:
=============

* No status updates during searches/copy operations. When making API calls the UI becomes non-responsive
until the calls complete. This is due to the requests library blocking Qt5 when REST calls are being used. One day this
might be fixed by multithreading the app but currently this is expected behaviour. 

* Search API: Entering an invalid search into the search box and executing may result in a "Bad Credentials" error rather than
indicating that the syntax was wrong. Test your searches in the Sumo Logic UI prior to using this tool to dump logs
to CSV. 

* Access to Globally Shared Content Folders is currently disabled until that code is refined. 

To Do:
======

* Implement global folders in the content tab

* Add "source restore" functionality

* Add "source update" functionality (for instance to add filters)

* Add encrypted keystore (so you don't have to type in creds each time)

License
=======

Copyright 2015 Timothy MacDonald

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

Support
=======

This is an opensource tool that I've written in my spare time. It is NOT an official Sumo Logic product. Use at your
own risk. 

This repository and the code within are NOT supported by Sumo Logic.

Feel free to e-mail me with issues however and I will provide "best effort" fixes: tmacdonald@sumologic.com


