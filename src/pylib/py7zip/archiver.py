
# System imports
import errno
import gzip
import lzma
import os
import shutil
import tarfile
import zipfile

# Project imports
import py7zip.crypt as crypt

# pylint: disable=no-self-use
class Archiver:

    def __init__(self, archive_format:str=None, key:str=None):
        self.archive_format=archive_format
        self.key=key

    def __sanitize_archive_directory(self, archive_filepath:str, default=lambda:None):
        archive_dir = os.path.dirname( archive_filepath )

        if (archive_dir == '') or (archive_dir is None):
            return default()

        if not os.path.isdir( archive_dir ):
            raise ArchiverException('Archive directory ({0}) does not exist.'.format(archive_dir))

        return archive_dir


    def __sanitize_output_dir(self, arg_o:str):
        if arg_o is None:
            arg_o = os.getcwd()

        elif not os.path.isdir( arg_o ):
            raise ArchiverException('Output directory ({0}) does not exist.'.format(arg_o))

        return os.path.abspath(arg_o)


    def __pack_gzfile(self, archive_filepath:str, archive_item:str):
        """Pack gz `archive_item` to `archive_filepath`
        """
        with open(archive_item, 'rb') as f_in:
            with gzip.open(archive_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)


    def __pack_tarfile(self, archive_filepath:str, archive_items:list):
        """Pack `archive_items` into a tar/tar.gz/tar.bz2/tar.xz based on `archive_filepath`
        """
        tar_args = {
            'name': archive_filepath,
            'mode': 'w:%s' % self.archive_format
        }

        if self.archive_format == 'xz':
            tar_args['preset'] = 2 # fixed compression level

        with tarfile.open(**tar_args) as tar:
            for entry in archive_items:
                if (not os.path.isdir(entry)) and (not os.path.isfile(entry)):
                    raise ArchiverException('Could not find directory/file ({0}).'.format(entry))
                tar.add(entry)


    def __pack_xzfile(self, archive_filepath:str, archive_item:str):
        """Pack xz `archive_item` to `archive_filepath`
        """
        with open(archive_item, 'rb') as f_in:
            with lzma.open(archive_filepath, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)


    def __pack_zipfile(self, archive_filepath:str, archive_items:list):
        """Create `archive_filepath` zip file from all the items in `archive_items`
        """
        with zipfile.ZipFile(archive_filepath, "w", compression=zipfile.ZIP_LZMA) as zipf: #no specifications on lzma compression level
            for entry in archive_items:
                if (not os.path.isdir(entry)) and (not os.path.isfile(entry)):
                    raise ArchiverException('Could not find directory/file ({0}).'.format(entry))

                if os.path.isfile(entry):
                    path = os.path.abspath(entry)
                    zipf.write(path, entry)
                    continue

                for dirpath, dirnames, filenames in os.walk(entry):
                    for name in sorted(dirnames):
                        archname = os.path.join(dirpath, name)
                        path = os.path.abspath(archname)
                        zipf.write(path, archname)

                    for name in filenames:
                        archname = os.path.join(dirpath, name)
                        path = os.path.abspath(archname)
                        zipf.write(path, archname)


    def __unpack_gzfile(self, archive_filepath:str, extract_filepath:str):
        """Unpack gz `archive_filepath` to `extract_filepath`
        """
        try:
            with gzip.open(archive_filepath, 'rb') as f_in:
                with open(extract_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except tarfile.TarError:
            raise ArchiverFileFormatException('File ({0}) is not a compressed or uncompressed tar file.'.format(archive_filepath))


    def __unpack_tarfile(self, archive_filepath:str, extract_dir:str):
        """Unpack tar/tar.gz/tar.bz2/tar.xz `archive_filepath` to `extract_dir`
        """
        try:
            tar = tarfile.open(archive_filepath)
        except tarfile.TarError:
            raise ArchiverFileFormatException('File ({0}) is not a compressed or uncompressed tar file.'.format(archive_filepath))

        try:
            tar.extractall(extract_dir)
        finally:
            tar.close()


    def __unpack_xzfile(self, archive_filepath:str, extract_filepath:str):
        """Unpack xz `archive_filepath` to `extract_filepath`
        """
        try:
            with lzma.open(archive_filepath, 'rb') as f_in:
                with open(extract_filepath, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
        except tarfile.TarError:
            raise ArchiverFileFormatException('File ({0}) is not a compressed or uncompressed tar file.'.format(archive_filepath))


    def __unpack_zipfile(self, archive_filepath:str, extract_dir:str):
        """Unpack zip `archive_filepath` to `extract_filepath`
        """
        with zipfile.ZipFile(archive_filepath) as zipf:
            zipf.extractall(extract_dir)


    def add(self, archive_filepath:str, args_o:str, archive_items:list):
        """Add files to archive.  Currently assumes a brand new archive,
            so this does not append to existing archive file.

            archive_filepath:
                Archive file path

            args_o:
                User supplied output directory

            archive_items:
                List of files and/or directories to include in the archive.
        """
        # default to the path supplied with the archive name
        archive_dir = self.__sanitize_archive_directory(archive_filepath)
        if archive_dir is None:
            archive_dir = self.__sanitize_output_dir(args_o)

        created_archive_filepath = os.path.join(archive_dir, os.path.basename( archive_filepath ))

        if (self.archive_format == 'gzfile') or (self.archive_format == 'xzfile'):
            if len(archive_items) > 1:
                raise ArchiverException('Too many files provided for gzip compression.  Only 1 file allowed.')

            if self.archive_format == 'gzfile':
                self.__pack_gzfile(created_archive_filepath, archive_items[0])
            else:
                self.__pack_xzfile(created_archive_filepath, archive_items[0])

        elif self.archive_format == 'zip':
            self.__pack_zipfile(created_archive_filepath, archive_items)

        else:
            self.__pack_tarfile(created_archive_filepath, archive_items)

        if self.key is not None:
            crypt.encrypt_file(self.key, created_archive_filepath)
            os.remove(created_archive_filepath)  # TODO: optionally persist unencrypted file?


    def extract(self, archive_filepath:str, args_o:str):
        """Extract archived file.  Decrypts if necessary

            archive_filepath:
                Archive file path

            args_o:
                User supplied output directory
        """
        if self.key is not None:
            archive_filepath = crypt.decrypt_file(self.key, archive_filepath)

        # default to option '-o'
        archive_dir = args_o
        if archive_dir is None:
            archive_dir = self.__sanitize_archive_directory(archive_filepath, os.getcwd())

        if (self.archive_format == 'gzfile') or (self.archive_format == 'xzfile'):
            (basename) = os.path.splitext(os.path.basename(archive_filepath))

            if self.archive_format == 'gzfile':
                self.__unpack_gzfile(archive_filepath, os.path.join(archive_dir, basename))
            else:
                self.__unpack_xzfile(archive_filepath, os.path.join(archive_dir, basename))

        elif self.archive_format == 'zip':
            self.__unpack_zipfile(archive_filepath, archive_dir)

        else:
            self.__unpack_tarfile(archive_filepath, archive_dir)

        if self.key is not None:
            os.remove(archive_filepath)


class ArchiverException(Exception):
    def __init__(self, msg, err_no=errno.EINVAL):
        self.errno = err_no
        super().__init__(msg)

class ArchiverFileFormatException(ArchiverException):
    def __init__(self, msg):
        super().__init__(msg, errno.EIO)
