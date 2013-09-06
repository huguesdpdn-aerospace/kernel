# Copyright (C) 2013  CEA/DEN, EDF R&D, OPEN CASCADE
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307 USA
#
# See http://www.salome-platform.org/ or email : webmaster.salome@opencascade.com
#

import unittest

import os
import sys
import imp
from cStringIO import StringIO
import logging

logger = logging.getLogger("TestLauncherLogger")
logger.level = logging.DEBUG
logger.addHandler(logging.StreamHandler())

class TestSessionArgs(unittest.TestCase):
  @classmethod
  def setUpClass(cls):
    # Initialize path to SALOME application
    path_to_launcher = os.getenv("SALOME_LAUNCHER")
    appli_dir = os.path.dirname(path_to_launcher)
    envd_dir = os.path.join(appli_dir, "env.d")

    # Configure session startup
    cls.SALOME = imp.load_source("SALOME", os.path.join(appli_dir,"salome"))
    cls.SALOME_args = ["shell", "--config="+envd_dir]

    cls.logFile = "log.txt"
    sys.stdout = StringIO()

    # Set some predefined command args and corresponding output messages
    cls.hello0 = ["hello.py", "args:outfile="+cls.logFile]
    cls.hello0Msg = "Hello!"
    cls.hello1 = ["hello.py", "args:you,outfile="+cls.logFile]
    cls.hello1Msg = "Hello to: you"
    cls.helloToAdd = ["hello.py", "args:add.py,1,2,3,outfile="+cls.logFile]
    cls.helloToAddMsg = "Hello to: add.py, 1, 2, 3"
    cls.add0 = ["add.py", "args:outfile="+cls.logFile]
    cls.add0Msg = "No args!"
    cls.add3 = ["add.py", "args:1,2,3,outfile="+cls.logFile]
    cls.add3Msg = "1+2+3 = 6"
    cls.lines0 = ["lines.py", "args:outfile="+cls.logFile]
    cls.lines0Msg = "No files given"
    cls.lines2 = ["lines.py", "args:hello.py,add.py,outfile="+cls.logFile]
    cls.lines2Msg = "hello.py is 16 lines longadd.py is 18 lines long"
    cls.linesUnreadable = ["lines.py", "args:hello.py,add.py,1,2,outfile="+cls.logFile]
    cls.linesUnreadableMsg = "hello.py is 16 lines longadd.py is 18 lines longFile '1' cannot be readFile '2' cannot be read"
  #
  @classmethod
  def tearDownClass(cls):
    pass
  #
  def setUp(self):
    self.removeLogFile()
  #
  def tearDown(self):
    self.removeLogFile()
  #
  def session(self, args=[]):
    self.SALOME.main(self.SALOME_args + args)
  #
  def removeLogFile(self):
    try:
      os.remove(self.logFile)
    except OSError:
      pass
  #
  def assertLogFileContentsEqual(self, message):
    with open(self.logFile, "r") as f:
      contents = f.read().replace('\n', '')

    #sys.stderr.write("Generated contents :%s\n"%contents)
    #sys.stderr.write("Expected contents :%s\n"%message)
    self.assertTrue(contents==message)
  #
  def testHello0(self):
    self.session(self.hello0)
    self.assertLogFileContentsEqual(self.hello0Msg)
  #
  def testPythonHello0(self):
    self.session(["python"]+self.hello0)
    self.assertLogFileContentsEqual(self.hello0Msg)
  #
  def testHello1(self):
    self.session(self.hello1)
    self.assertLogFileContentsEqual(self.hello1Msg)
  #
  def testAdd0(self):
    self.session(self.add0)
    self.assertLogFileContentsEqual(self.add0Msg)
  #
  def testAdd3(self):
    self.session(self.add3)
    self.assertLogFileContentsEqual(self.add3Msg)
  #
  def testHello0Add3(self):
    self.session(self.hello0+self.add3)
    self.assertLogFileContentsEqual(self.hello0Msg+self.add3Msg)
  #
  def testHello1Add3(self):
    self.session(self.hello1+self.add3)
    self.assertLogFileContentsEqual(self.hello1Msg+self.add3Msg)
  #
  def testHelloToAdd(self):
    self.session(self.helloToAdd)
    self.assertLogFileContentsEqual(self.helloToAddMsg)
  #
  def testLines0(self):
    self.session(self.lines0)
    self.assertLogFileContentsEqual(self.lines0Msg)
  #
  def testLines2(self):
    self.session(self.lines2)
    self.assertLogFileContentsEqual(self.lines2Msg)
  #
  def testLines2Add3(self):
    self.session(self.lines2+self.add3)
    self.assertLogFileContentsEqual(self.lines2Msg+self.add3Msg)
  #
  def testLinesUnreadable(self):
    self.session(self.linesUnreadable)
    self.assertLogFileContentsEqual(self.linesUnreadableMsg)
  #
  def testAddAddHello(self):
    self.session(self.add3+self.add3+self.hello1)
    self.assertLogFileContentsEqual(self.add3Msg+self.add3Msg+self.hello1Msg)
  #
  def testHello0Add3Hello0Add3Hello0(self):
    self.session(self.hello1+self.add3+self.hello0+self.add3+self.hello0)
    self.assertLogFileContentsEqual(self.hello1Msg+self.add3Msg+self.hello0Msg+self.add3Msg+self.hello0Msg)
  #
#


if __name__ == "__main__":
  path_to_launcher = os.getenv("SALOME_LAUNCHER")
  if not path_to_launcher:
    msg = "Error: please set SALOME_LAUNCHER variable to the salome command of your application folder."
    raise Exception(msg)

  unittest.main()
#
