Sumotoolbox
===========

 Sumotoolbox is a GUI utility for accessing the various Sumo Logic APIs. The idea is to make
 it easier to perform common API tasks such as copying sources and generating CSV files from
 searches.

This version contains critical updates to the 'collectors' and 'source updates' tab. It is highly recommended that you
upgrade to this version or later (0.9.1)

For a description of functionality please see the [wiki](https://github.com/SumoLogic/sumologictoolbox/wiki)

Recommended Method of Getting and Running Sumotoolbox, download the binaries
============================================================================

The easiest way to download and use this tool is to download the latest binary release from the "releases"
section of this page. 

https://github.com/SumoLogic/sumologictoolbox/releases

Be aware that you these binaries may trigger false positives in your AV tool. This is due to the use of "pyinstaller" 
to package and "freeze" this python code. Pyinstaller is a legitimate tool however it has been used by bad actors in 
the past to package malware.As a result the pyinstaller bootloader code has become associated with malware by many AV and
endpoint protection tools. For a more comprehensive discussion of this topic the following article may be of interest:

https://stevepython.wordpress.com/2019/01/22/do-avs-treat-python-as-a-virus/

Updating the Binaries
=====================

When it's time to upgrade to a new version of sumotoolbox simply download the new executable and use it to replace
your old one, leaving your ini and db file in place. 

Installing the Source
=====================

If you prefer to clone the archive and run from source then you'll need Python 3.6 or higher and the modules listed 
in the dependency section.  

The steps are as follows: 

    1. Download and install python 3.6, 3.7, 3.8 from python.org.  
       Make sure to choose the "add python to the default "path" checkbox in the installer (may be in 
       advanced settings.)

       Note: If you have Linux you can usually skip this step, but ensure you have python3 installed for your distro. 

       Note: If you have OS X you cannot use the python that comes with the OS, it is too old.

    2. Download and install git for your platform if you don't already have it installed.
       It can be downloaded from https://git-scm.com/downloads
    
    3. Open a new shell/command prompt. It must be new since only a new shell will include the new python 
       path that was created in step 1. Cd to the folder where you want to install sumotoolbox.
    
    4. Execute the following command to install pipenv, which will manage all of the library dependencies 
       for us:

        pip3 install pipenv
    
        -or-
    
        sudo pip3 install pipenv 
 
    5. Clone this repo using the following command:
    
        git clone https://github.com/SumoLogic/sumologictoolbox.git
    
    This will create a new folder called sumotoolbox. 
    
    6. Change into the sumotoolbox folder. Type the following to install all the package 
       dependencies (this may take a while as this will download all of the libraries that sumotoolbox uses):

    pipenv install
    
To run sumotoolbox cd into the sumotoolbox directory and type:

    pipenv run python3 sumotoolbox.py
    
Updating the Source
===================

When it's time to upgrade to a new version of sumotoolbox cd into the sumotoolbox directory and type:
    
    1. git pull https://github.com/SumoLogic/sumologictoolbox.git
    
    2. pipenv install
    
To run sumotoolbox cd into the sumotoolbox directory and type:

    pipenv run python3 sumotoolbox.py

Dependencies
============

See the contents of "pipfile"

  


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

Please submit bugs using the project [issues](https://github.com/SumoLogic/sumologictoolbox/issues) page. 
