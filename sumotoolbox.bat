@ECHO OFF
WHERE pipenv
IF %ERRORLEVEL% NEQ 0 (
    echo The pipenv command could not be found.
    echo To run SumoToolBox from source code you
    echo must have python 3.x and pipenv installed.
    echo Python can be downloaded from python.org.
    echo Once python is installed pipenv can be
    echo installed using the pip command:
    echo pip install pipenv
    goto :BREAK
)

set /A QT_FONT_DPI = 96
pipenv install
pipenv run python sumotoolbox.py

:BREAK