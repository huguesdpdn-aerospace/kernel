#  -*- coding: iso-8859-1 -*-
# Copyright (C) 2007-2014  CEA/DEN, EDF R&D, OPEN CASCADE
#
# Copyright (C) 2003-2007  OPEN CASCADE, EADS/CCR, LIP6, CEA/DEN,
# CEDRAT, EDF R&D, LEG, PRINCIPIA R&D, BUREAU VERITAS
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
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
from optparse import OptionParser
from NSparam import getNSparams
import socket
import subprocess
import re
from salomeContextUtils import getScriptsAndArgs, formatScriptsAndArgs

# Use to display newlines (\n) in epilog
class MyParser(OptionParser):
    def format_epilog(self, formatter):
        return self.epilog
#

class SessionParameters:
  def __init__(self, mode, port, machine, user, directory):
    self.mode = mode
    self.port = port
    self.machine = machine
    self.user = user
    self.directory = directory
#

def configureSession(args=None):
  if args is None:
    args = []
  usage = "Usage: %prog [options] [command]"
  epilog  = """\n
If the command is not given a shell is opened; else execute the given command.
Command may be a series of Python scripts with arguments: [PYTHON_FILE [args] [PYTHON_FILE [args]...]]
Python file arguments, if any, must be comma-separated (without blank characters) and prefixed by "args:" (without quotes), e.g. myscript.py args:arg1,arg2=val,...
\n
If PORT and MACHINE are not given, try to connect to the last active session on the local machine.
If PORT and MACHINE are given, try to connect to the remote session associated with PORT on MACHINE.
If MACHINE is not given, try to connect to the session associated to PORT on the local machine.
If PORT is not given, try to connect to the remote session associated to port 2810 on MACHINE.
\n
If MACHINE is remote, the following options MUST be provided:
     * DIRECTORY: The full path to the salome command on remote machine.
     * USER: The user on the computer to connect to.
"""
  parser = MyParser(usage=usage, epilog=epilog)
  parser.add_option("-p", "--port", metavar="<port>", default=0,
                    action="store", type="string", dest="port",
                    help="The port to connect to."
                    )
  parser.add_option("-m", "--machine", metavar="<machine>", default=0,
                    action="store", type="string", dest="host",
                    help="The machine to connect to."
                    )
  parser.add_option('-d', '--directory', dest="directory", default=None,
                    help="[Remote mode] The full path to the salome command on remote machine."
                    )
  parser.add_option('-u', '--user', dest="user", default=None,
                    help="[Remote mode] The user on the computer to connect to."
                    )
  try:
    (options, args) = parser.parse_args(args)
  except Exception, e:
    print e
    return

  port = options.port
  host = options.host

  # :GLITCH: this code defines specific environment variables (OMNIORB_CONFIG, NSPORT,
  # NSHOST) which are later used by other modules. Working, but not really "safe"...
  if not port:
    if not host:
      # neither MACHINE nor PORT are given
      # --- set omniORB configuration to current session if any
      omniorbUserPath = os.environ['OMNIORB_USER_PATH']
      fileOmniConfig = omniorbUserPath + '/.omniORB_' + os.environ['USER'] + '_last.cfg'
      if os.path.isfile(fileOmniConfig):
        os.environ['OMNIORB_CONFIG'] = fileOmniConfig
        # --- set environment variables for port and hostname of NamingService
        host, port = getNSparams()
      else:
        # No running session
        host = "no_host"
        port = "no_port"
    else:
      # only MACHINE is given
      port = '2810'
      _writeConfigFile(port, host)
    #
  else:
    if not host:
      # only PORT is given
      host = socket.gethostname()
    # both MACHINE and PORT are given
    _writeConfigFile(port, host)
  #
  os.environ['NSPORT'] = port
  os.environ['NSHOST'] = host

  # determine running mode, taht is either 'local' or 'remote'
  from salomeContextUtils import getHostname
  here = getHostname()
  mode = "local"
  if host != here and host != "localhost" and host != "no_host":
    mode="remote"
    pass
  params = SessionParameters(mode, port, host, options.user, options.directory)
  return params, args
#

# --- set the OMNIORB_CONFIG file and environment relative to this run of SALOME
def _writeConfigFile(port, host):
  path = os.environ['OMNIORB_USER_PATH']
  kwargs = {'with_username' : os.environ['USER']}

  from ORBConfigFile import writeORBConfigFile
  [ filename, msgSize ] = writeORBConfigFile(path, host, port, kwargs)

  os.environ['OMNIORB_CONFIG'] = filename
#

# command looks like a Bash command-line:
# script1.py [args] ; script2.py [args] ; ...
def __runLocalSession(command):
  if command:
    sep = ";"
    if sys.platform == "win32":
      sep= "&"
    command = command.split(sep)
    outmsg = []
    errmsg = []
    for cmd in command:
      single_cmd = cmd.strip().split(' ')
      proc = subprocess.Popen(single_cmd)
      (stdoutdata, stderrdata) = proc.communicate() # Wait for process to terminate
      if stdoutdata:
        outmsg.append(stdoutdata)
      if stderrdata:
        errmsg.append(stderrdata)

      if proc.returncode != 0:
        errmsg.append("Error raised when executing command: %s\n"%cmd)
        if outmsg:
          sys.stdout.write("".join(outmsg))
        if errmsg:
          sys.stderr.write("".join(errmsg))
        sys.exit(proc.returncode)

    return ("".join(outmsg), "".join(errmsg))
  else:
    absoluteAppliPath = os.getenv('ABSOLUTE_APPLI_PATH','')
    cmd = ["/bin/bash",  "--rcfile", absoluteAppliPath + "/.bashrc" ]
    proc = subprocess.Popen(cmd, shell=False, close_fds=True)
    return proc.communicate()
#

def __copyFiles(user, machine, script, infiles, outfiles):
  """Modify script, copy files to remote computer and return lists of copied files."""

  namescript = os.path.basename(script)
  import getpass
  logname = getpass.getuser()
  tmp_script = "/tmp/%s_%s_%s" % (logname, os.getpid(), namescript)
  with open(script, 'r') as fscript:
    script_text = fscript.read()

  list_infiles = []
  list_outfiles = []
  n = 0
  for infile in infiles:
    # generate a temporary file name
    namefile = os.path.basename(infile)
    tmp_file = "/tmp/%s_%s_i%s_%s" % (logname, os.getpid(), n, namefile)

    # modify the salome script
    script_text = re.sub(infile, tmp_file, script_text)

    # copy the infile to the remote server
    cmd = "scp %s %s@%s:%s" % (infile, user, machine, tmp_file)
    print "[  SCP  ]", cmd
    os.system(cmd)

    list_infiles.append(tmp_file)
    n = n + 1
  #
  n = 0
  for outfile in outfiles:
    # generate a temporary file name
    namefile = os.path.basename(outfile)
    tmp_file = "/tmp/%s_%s_o%s_%s" % (logname, os.getpid(), n, namefile)

    # modify the salome script
    script_text = re.sub(outfile, tmp_file, script_text)

    list_outfiles.append(tmp_file)
    n = n + 1
  #

  with open(tmp_script,'w') as fscript:
    fscript.write(script_text)

  # copy the salome script on the remote server
  cmd = "scp %s %s@%s:%s" % (tmp_script, user, machine, tmp_script)
  print "[  SCP  ]", cmd
  os.system(cmd)

  return list_infiles, list_outfiles, tmp_script
#

# sa_obj is a ScriptAndArgs object (from salomeContextUtils)
def __runRemoteSession(sa_obj, params):
  if not params.user:
    print "ERROR: The user login on remote machine MUST be given."
    return
  if not params.directory:
    print "ERROR: The remote directory MUST be given."
    return

  # sa_obj.script may be 'python script.py' --> only process .py file
  header = " ".join(sa_obj.script.split()[:-1])
  script = sa_obj.script.split()[-1]

  tmp_in, tmp_out, tmp_script = __copyFiles(params.user, params.machine, script, sa_obj.args or [], sa_obj.out or [])

  # execute command on the remote SALOME application
  command = "ssh %s@%s %s/runSession " % (params.user, params.machine, params.directory)
  if params.port:
    command = command + "-p %s "%params.port
  command = command + " ".join([header,tmp_script] + tmp_in)
  print '[  SSH   ] ' + command
  os.system(command)

  # Get remote files and clean
  temp_files = tmp_in + tmp_out + [tmp_script]

  # get the outfiles
  for outfile in (sa_obj.out or []):
    remote_outfile = tmp_out.pop(0)
    command = "scp %s@%s:%s %s" %(params.user, params.machine, remote_outfile, outfile)
    print "[  SCP  ] " + command
    os.system(command)

  # clean temporary files
  command = "ssh %s@%s \\rm -f %s" % (params.user, params.machine, " ".join(temp_files))
  print '[  SSH   ] ' + command
  os.system(command)
  os.remove(tmp_script)

#

def runSession(params, args):
  scriptArgs = getScriptsAndArgs(args)
  command = formatScriptsAndArgs(scriptArgs)

  if params.mode == "local":
    command = formatScriptsAndArgs(scriptArgs)
    return __runLocalSession(command)

  elif params.mode == "remote":
    for sa_obj in scriptArgs:
      __runRemoteSession(sa_obj, params)
#
