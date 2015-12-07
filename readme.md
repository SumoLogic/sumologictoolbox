Sumotoolbox
===========

 Sumotoolbox is a GUI utility for accessing the various Sumo Logic APIs (currently the search
 and connector APIs.) The idea is to make it easier to perform common API tasks such as copying
 sources and generating CSV files from searches.

 Sumotoolbox makes use of the sumologic-python-sdk by Yoway Buorn that is available here:

 https://github.com/SumoLogic/sumologic-python-sdk

Dependencies
============

Sumotoolbox was created using python 2.7, pyqt4 and the Qt designer application. A working pyqt4 installation must be
present to execute this script within your python environment. Alternatively you can download the Windows or Mac OS X
binaries available in the "dist" folder which come bundled with all required libraries. They were created on Windows 10
and OS X Yosemite so your mileage may vary with older OS releases.

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

Search API use:

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

Known Issues:
=============

* Option to modify collection start time when copying collectors does not currently work. Needs tweaking
as currently the Sumo Logic Collector API does not like the value and substitutes "All Time" instead.

* No status updates during searches. When executing a search, especially a lengthy one the UI becomes non-responsive
until the search completes. This is due to the search loop blocking updates to the UI.

* Entering an invalid search into the search box and executing may result in a "Bad Credentials" error rather than
indicating that the syntax was wrong.

To Do:
======

* Add "export to file" and "import to file" options for collectors/sources.

* Implement content copying.

* Improve time search time conversion to work on arbitrary fields (for instance a timeslice field not named "_timeslice"

* Add custom time formats for time conversion

* Improve error handling

* Implement non-blocking "Working" dialog box to indicate search progress for long searches.

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

This repository and the code within is not supported by Sumo Logic.
