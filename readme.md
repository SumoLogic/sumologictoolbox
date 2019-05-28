Sumotoolbox
===========

 Sumotoolbox is a GUI utility for accessing the various Sumo Logic APIs (currently the search
 and collector APIs.) The idea is to make it easier to perform common API tasks such as copying
 sources and generating CSV files from searches.

 Sumotoolbox makes use of the sumologic-python-sdk that is available here:

 https://github.com/SumoLogic/sumologic-python-sdk

Using Sumotoolbox
=================

The easiest way to use sumotoolbox is to look in the "dist" directory of this repo and grab the executable for your platform. Run the executable, pick your region, enter your creds, and start using the tool. 

If you prefer to clone the archive and run from source then you'll need Python 3.6 or higher and the modules listed in the dependency section.  

Essentially the steps are as follows: 

1. Download and install python 3.6 or higher from python.org. Make sure to choose the "add python the default path" checkbox in the installer (may be in advanced settings.)

2. Open a new shell

3. execute the following commands to install the module dependencies:

 pip3 install pyqt5
 
 pip3 install requests
 
 pip3 install tzlocal
 
 pip3 install pytz
 
4. Download this repo (either as a zip from the main repo download link or using git.) Unzip if you downloaded the zip. 
5. Change to the directory you put sumotoolbox in.Type the following to run the script:

 python3 sumotoolbox.py

Dependencies
============

Sumotoolbox was created using python 3.6, pyqt5 and the Qt designer application. The following python modules are required:

pyqt5

requests

tzlocal

pytz



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
    
    Note: There is not currently a collector restore capability in this tool. 

Collector Delete:

    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" for destination to populate the collector list
    4. Choose one or more collectors
    6. Click "Delete Collector(s)"
    7. Verify that you really want to delete the collector(s) by typing "DELETE"
    8. Click "OK"
    
    NOTE: This can be very dangerous. Accidentally deleting the wrong collector(s) could result in log collection interruption 
    and many, many hours of restoration work. Use with EXTREME caution. 
    
Source Delete:

    1. Input Credentials for your org
    2. Select your region for your org
    3. Click "Update" for destination to populate the collector list
    4. Choose a collector
    5. Choose one or more sources
    6. Click "Delete Source(s)"
    7. Verify that you really want to delete the source(s) by typing "DELETE"
    8. Click "OK"

    NOTE: This can be very dangerous. Accidentally deleting the wrong sources(s) could result in log collection interruption 
    and many, many hours of restoration work. Use with EXTREME caution. 
    
Search API:

    1. Input source credentials
    2. Select your source region
    3. Select your timezone (defaults to local system timezone)
    4. Select your time range (defaults to a relative 15 minute window from the time the app was launched)
    5. Enter a valid Sumo Logic search query
    6. Select whether you want to see message results or record results (raw messages vs. aggregate data.)
    7. (Optional) Check "Save to CSV" to create a CSV file from the results
    8. (Optional) Check "Convert to Selected Timezone from UTC Epoch". This will return message times and "_timeslice"
    fields as local time formatted as %Y-%m-%d %H:%M:%S rather than UTC epoch time.
    9. Click "Start"
    
    NOTE: The use case for this fuctionality is dumping to CSV. The Sumo Logic UI export feature is currently limited to 100,000 log messages. This tool should reliable dump much more than that, however the UI will "freeze" during the dump. This could take minutes or even hours depending on the size of the dump. Please resist the temptation to rage quit because of an unresposive UI. 

Screen Shots:
=============

![Collector Source Copy](https://github.com/voltaire321/sumologictoolbox/blob/master/screenshots/sumotoolbox_collector_example.png "Source Copy")

![Search API Example](https://github.com/voltaire321/sumologictoolbox/blob/master/screenshots/sumotoolbox_search_example.png "Search API")

Known Issues:
=============

* No status updates during searches/copy operations. When making API calls the UI becomes non-responsive
until the calls complete. This is due to the requests library blocking Qt5 when REST calls are being used. One day this might be fixed by multithreading the app but currently this is expected behaviour. 

* Entering an invalid search into the search box and executing may result in a "Bad Credentials" error rather than
indicating that the syntax was wrong. Test your searches in the Sumo Logic UI prior to using this tool to dump logs
to CSV. 

To Do:
======

* Implement the content API tab (content copying, etc...)

* Improve error handling

* Implement non-blocking "Working" dialog box to indicate search progress for long searches.

* Add "source restore" functionality

* Add "source update" functionality (for instance to add filters)

* Add "hosted collector create" functionality

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

Better yet feel free to contribute fixes directly. 
