#!/usr/bin/env python
#  -*- coding: iso-8859-1 -*-
# Copyright (C) 2007-2013  CEA/DEN, EDF R&D, OPEN CASCADE
#
# Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
# CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
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

import os
import sys

def __setup_config(nsport, args, save_config):
  #
  from salome_utils import generateFileName, getHostName
  hostname = getHostName()
  #
  omniorbUserPath = os.getenv("OMNIORB_USER_PATH")
  kwargs={}
  if omniorbUserPath is not None:
    kwargs["with_username"]=True
  #
  from ORBConfigFile import writeORBConfigFile
  omniorb_config, giopsize = writeORBConfigFile(omniorbUserPath, hostname, nsport, kwargs)
  args['port'] = os.environ['NSPORT']
  #
  if save_config:
    last_running_config = generateFileName(omniorbUserPath, prefix="omniORB",
                                           suffix="last",
                                           extension="cfg",
                                           hidden=True,
                                           **kwargs)
    #os.environ['LAST_RUNNING_CONFIG'] = last_running_config
    try:
      if sys.platform == "win32":
        import shutil
        shutil.copyfile(omniorb_config, last_running_config)
      else:
        try:
          if os.access(last_running_config, os.F_OK):
            os.remove(last_running_config)
        except OSError:
          pass
        os.symlink(omniorb_config, last_running_config)
        pass
      pass
    except:
      pass
  #
#

def searchFreePort(args={}, save_config=1, use_port=None):
  """
  Search free port for SALOME session.
  Returns first found free port number.
  """

  import PortManager
  client = PortManager.start_client() # :NOTE: might specify a (remote) IP
  portManager = client.PortManager()

  if use_port:
    print "Check if port can be used: %d" % use_port,
    if not portManager.isPortUsed(use_port):
      print "- OK"
      __setup_config(use_port, args, save_config)
      return
    else:
      print "- KO: port is busy"
      pass
  #
  print "Searching for a free port for naming service:",
  port = portManager.getPort()
  print "%s - OK"%(port)
  __setup_config(port, args, save_config)
  port = portManager.releasePort(port)
#
