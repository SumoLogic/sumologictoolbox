from distutils.core import setup
import py2exe
setup(windows=[{"script" : "sumotoolbox.py"}], options={"py2exe" : {"includes" : ["sip"]}})
