# py7zip
Archiving application.  Goal is to replace 7zip with Python

An archiver with the highest compression ratio (that implements LZMA compression algorithm by default).
The program supports currently supports output file formats of bz2, gz, tar, tar.gz, tar.xz, tgz, txz, xz, zip.

This is designed to work out of the box on a linux system (you'll see the symlinks), since the linux world has little to no love from p7zip.  Better stated, the challenges and complexity of getting 7zip on various unix platforms it is a bit much.
If you have Python and get run the required modules (*see `requirements.txt`) then you're golden

```
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
```

## `py7za`
In the spirti of 7zip's 7za naming, we have `py7za`.  This is the the entry point and the magic.

### Example Usage

#### *Example 1*
Adds dir1/ to a tar archive file compress with LZMA.

./bin/py7za a myArchive.txz dir1


#### *Example 2*
Adds dir1/ and file1 to a tar archive file in the 'storage_path'
* If '-o' is used it will be ignored in favor of 'storage_path'. If no path is supplied, then '-o' will be honored or default to current directory.

    ./bin/py7za a <storage_path>/myArchive.txz dir1 file1


#### *Example 3*
e(X)tracts tar archive file into same directory as the input file (ie 'storage_path').

    ./bin/py7za x <storage_path>/myArchive.txz


#### *Example 4*
e(X)tracts tar archive file into specifiec output directory.

    ./bin/py7za x <storage_path>/myArchive.txz -o <output_dir>/


## `keygen`
Archiving with encryption is possible.  This requires a key file or a key to be passed on the command line.  See help (-h) for usage.

### Key generation
In order to generate a key using `keygen` you'll need to provide a passphrase.  This will generate the encryption key.  You can then provide this at the command line or within a file.

```
$ ./keygen
Enter the password you would like to use: This is my passphrase, good stuff
Your new key is: c090d8272aee89963d8788c46b6656a539981bc2e67d1ba5bb896aa8af0c12e2
```