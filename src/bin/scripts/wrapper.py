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

    print(os.environ.get("PYTHONPATH"))
    print(sys.path)
    python_exe = sys.executable

    if sys.version_info[0] < 3:
        try:
            python_exe = sproc.check_output(['which', 'python3']).rstrip()
        except:
            print( 'Python 3 must be installed!' )
            exit( os.EX_USAGE )

    args = sys.argv
    args.pop(0)
    args.insert(0, python_exe)
    args.insert(1, os.path.join(script_path, basename + '.py'))

    try:
        exit( sproc.call(args) )
    except KeyboardInterrupt:
        exit( 1 )

main()