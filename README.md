# py7zip
Archiving application.  Goal is to replace 7zip with Python

An archiver with the highest compression ratio (that implements LZMA compression algorithm by default).
The program supports currently supports output file formats of bz2, gz, tar, tar.gz, tar.xz, tgz, txz, xz, zip.

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
