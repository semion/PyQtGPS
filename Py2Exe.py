from distutils.core import setup
import py2exe
setup(windows=[{"script":"Calc2.pyw"}], options={"py2exe":{"includes":["sip"]}})
