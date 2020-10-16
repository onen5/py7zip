#!/usr/bin/env python

import os
import subprocess as sproc
import sys

def main():
    my_path   = os.path.abspath( __file__ )
    (bin_path, basename)  = os.path.split( my_path )
    root_path   = os.path.dirname( bin_path )
    script_path = os.path.join( bin_path, "scripts" )

    os.environ["LOCAL_ROOT"]  = os.path.dirname(root_path)
    os.environ["UNMAN_DIR"]   = os.path.join( os.environ.get("LOCAL_ROOT"), "unmanaged" )

    lib_path = os.path.join(root_path, "pylib")
    if os.path.isdir( lib_path ):
        os.environ["PYTHONPATH"] = lib_path + (os.pathsep + os.environ.get("PYTHONPATH") if os.environ.get("PYTHONPATH")!=None else "")

    use_ipython = os.path.exists( os.path.join(script_path, basename + '.ipy') )

    python_exe = ''
    if use_ipython:
        python_exe = sproc.check_output(['which', 'ipython']).rstrip()
    else:
        python_exe = sys.executable


    if sys.version_info[0] < 3:
        try:
            py3exe = ''
            # we may or may not want this text.  Defaults tend to be py2 so this will be printed every time.
            # print( 'Found ' + py3exe + '.  Switching interpreter to this version' )
            
            if use_ipython:
                py3exe = sproc.check_output(['which', 'ipython3']).rstrip()
            else:
                py3exe = sproc.check_output(['which', 'python3']).rstrip()

            python_exe = py3exe
        except:
            print( 'Python 3 must be installed!' )
            exit( os.EX_USAGE )

    args = sys.argv
    args.pop(0)
    args.insert(0, python_exe)
    args.insert(1, os.path.join(script_path, basename + ('.ipy' if use_ipython else '.py')))

    try:
        exit( sproc.call(args) )
    except KeyboardInterrupt:
        exit( 1 )

main()