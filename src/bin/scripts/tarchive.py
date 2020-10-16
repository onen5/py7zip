
#
# py7zip
#
#   py(thon)7zip
#

# System imports
import argparse
import errno
import os
import re
import sys

# Project imports
import py7zip.archiver as archiver
import py7zip.constant as const

# Global Constants
#
const.EXT_FORMAT = {
    'enc': None,
    'bz2': 'bz2',
    'gz': 'gzfile',
    'tar': '',
    'tar.gz': 'gz',
    'tar.xz': 'xz',
    'tgz': 'gz',
    'txz': 'xz',
    'xz': 'xzfile',
    'zip': 'zip'
}
const.SUPPORTED_FILE_EXT = const.EXT_FORMAT.keys()

const.SCRIPT = 'py7zip'
const.DESCRIPTION = '''
An archiver with the highest compression ratio (that implements LZMA compression algorithm by default).
The program supports currently supports output file formats of ({0}).
'''.format(', '.join(const.SUPPORTED_FILE_EXT))

const.EPILOG = '''
    Function Letters:
    a 
        Add
    x 
        eXtract with full paths

    Diagnositics:
        Exit Codes:
            0
                Normal (no errors or warnings detected)
            {EINTR}
                User stopped the process with control-C (or similar)
            {EIO}
                File archiving operation failed. Possibly a file format problem
            {EINVAL}
                Invalid usage

    Example 1:

    py7zip a myArchive.txz dir1
        Adds dir1/ to a tar archive file compress with LZMA.


    Example 2:

    py7zip a <storage_path>/myArchive.txz dir1 file1
        Adds dir1/ and file1 to a tar archive file in the 'storage_path'
        * If '-o' is used it will be ignored in favor of 'storage_path'. If no path is supplied, then '-o' will be honored or default to current directory.


    Example 3:

    py7zip x <storage_path>/myArchive.txz
        e(X)tracts tar archive file into same directory as the input file (ie 'storage_path').


    Example 4:

    py7zip x <storage_path>/myArchive.txz -o <output_dir>/
        e(X)tracts tar archive file into specifiec output directory.

'''.format(EIO=errno.EIO, EINTR=errno.EINTR, ENOEXEC=errno.ENOEXEC, EINVAL=errno.EINVAL)

#
#
# Functions
#
def _error_usage(msg:str, errcode:int):
    print('{0}: Error: {1}\n'.format(const.SCRIPT, msg))
    const.ARG_PARSER.print_help()
    sys.exit(errcode)

def _get_full_extension(archive_filename:str):
    (base, ext) = os.path.splitext(archive_filename)
    ext = re.sub('^\.', '', ext)

    if ext not in const.SUPPORTED_FILE_EXT:
        return None
    
    base_ext = _get_full_extension(base)
    if base_ext is None:
        return ext
    
    return '.'.join([base_ext, ext])


def _sanitize_file_format(archive_ext:str):
    if archive_ext is None:
        _error_usage('Cannot determine format type based on archive name ({0}).'.format(archive_ext), errno.EINVAL)

    if archive_ext not in const.SUPPORTED_FILE_EXT:
        _error_usage('File extension ({0}) on archive name is not supported.'.format(archive_ext), errno.EINVAL)

    return const.EXT_FORMAT.get(archive_ext)

def _sanitize_key(arg_k:str, arg_K:str):# pylint: disable=invalid-name
    if (arg_k is not None) and (arg_K is not None):
        _error_usage('Password options are mutually exclusive', errno.EINVAL)
    if arg_K is not None:
        if not os.path.isfile( arg_K ):
            _error_usage('Password file provided ({0}) does not exist.'.format(arg_K), errno.EINVAL)
        with open(arg_K, 'r') as file:
            arg_k = file.read()

    return arg_k


#
#
# Main
#
def main():

    # parse args
    const.ARG_PARSER = argparse.ArgumentParser(
        prog=const.SCRIPT,
        description=const.DESCRIPTION,
        epilog=const.EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter)

    const.ARG_PARSER.add_argument('function', metavar='FUNC', type=str,
                                  choices=['a','x'],
                                  help='Function letters')
    const.ARG_PARSER.add_argument('archive_filepath', metavar='ARCHIVE_FILEPATH', type=str,
                                  help='Archive file path')
    const.ARG_PARSER.add_argument('-o', metavar='OUTPUT_DIRECTORY', type=str,
                                  help='Set Output directory')
    const.ARG_PARSER.add_argument('-k', metavar='ENCRYPT_KEY', type=str,
                                  help='Encyption Key')
    const.ARG_PARSER.add_argument('-K', metavar='ENCRYPT_KEY_FILE', type=str,
                                  help='Encyption Key file')

    args, archive_items = const.ARG_PARSER.parse_known_args()

    const.USER_KEY = _sanitize_key(args.k, args.K)

    archive_basename = os.path.basename( args.archive_filepath )
    archive_ext = _get_full_extension(archive_basename)

    if (args.function != 'a') and (len(archive_items) > 0):
        _error_usage('Extra agrument(s) found ({0}).'.format(', '.join(archive_items)), errno.EINVAL)

    elif args.function == 'x':
        if not os.path.isfile(args.archive_filepath):
            _error_usage('Supplied file does not exist. ({0})'.format(args.archive_filepath), errno.EINVAL)

        if re.match(r'.*\.enc$', archive_ext):
            if const.USER_KEY is None:
                _error_usage('Encrypted file supplied requires a key.', errno.EINVAL)
        elif const.USER_KEY is not None:
            _error_usage('Key supplied for non-encrypted file extension.', errno.EINVAL)

        archive_ext = os.path.splitext(archive_ext)[0]

    archiver = archiver.Archiver(
        archive_format=_sanitize_file_format(archive_ext),
        key=const.USER_KEY
    )

    # Create Archive
    try:
        func_switch = {
            'a': (archiver.add, {
                'archive_filepath': args.archive_filepath,
                'args_o': args.o,
                'archive_items': archive_items,
            }),
            'x': (archiver.extract, {
                'archive_filepath': args.archive_filepath,
                'args_o': args.o,
            })
        }

        # Get the function from switcher dictionary
        (func, kwargs) = func_switch.get(args.function, lambda: print("Invalid function"))

        try:
            # Execute the function
            func(**kwargs)
        except archiver.ArchiverException as arex:
            _error_usage(arex, arex.errno)

    except KeyboardInterrupt:
        sys.exit( errno.EINTR )

main()
