# --------------------------------------------------------------------------
# Copyright 2014 Digital Sapphire Development Team
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# --------------------------------------------------------------------------
from __future__ import unicode_literals

import logging
import sys

from pyupdater import settings
from pyupdater.utils.exceptions import UtilsError, VersionError

log = logging.getLogger(__name__)


def lazy_import(func):
    """Decorator for declaring a lazy import.

    This decorator turns a function into an object that will act as a lazy
    importer.  Whenever the object's attributes are accessed, the function
    is called and its return value used in place of the object.  So you
    can declare lazy imports like this:

        @lazy_import
        def socket():
            import socket
            return socket

    The name "socket" will then be bound to a transparent object proxy which
    will import the socket module upon first use.

    The syntax here is slightly more verbose than other lazy import recipes,
    but it's designed not to hide the actual "import" statements from tools
    like pyinstaller or grep.
    """
    try:
        f = sys._getframe(1)
    except Exception:  # pragma: no cover
        namespace = None
    else:
        namespace = f.f_locals
    return _LazyImport(func.__name__, func, namespace)


class _LazyImport(object):
    """Class representing a lazy import."""

    def __init__(self, name, loader, namespace=None):
        self._pyu_lazy_target = _LazyImport
        self._pyu_lazy_name = name
        self._pyu_lazy_loader = loader
        self._pyu_lazy_namespace = namespace

    def _pyu_lazy_load(self):
        if self._pyu_lazy_target is _LazyImport:
            self._pyu_lazy_target = self._pyu_lazy_loader()
            ns = self._pyu_lazy_namespace
            if ns is not None:
                try:
                    if ns[self._pyu_lazy_name] is self:
                        ns[self._pyu_lazy_name] = self._pyu_lazy_target
                except KeyError:  # pragma: no cover
                    pass

    def __getattribute__(self, attr):  # pragma: no cover
        try:
            return object.__getattribute__(self, attr)
        except AttributeError:
            if self._pyu_lazy_target is _LazyImport:
                self._pyu_lazy_load()
            return getattr(self._pyu_lazy_target, attr)

    def __nonzero__(self):  # pragma: no cover
        if self._pyu_lazy_target is _LazyImport:
            self._pyu_lazy_load()
        return bool(self._pyu_lazy_target)


@lazy_import
def bz2():
    import bz2
    return bz2


@lazy_import
def gzip():
    import gzip
    return gzip


@lazy_import
def hashlib():
    import hashlib
    return hashlib


@lazy_import
def os():
    import os
    return os


@lazy_import
def re():
    import re
    return re


@lazy_import
def shutil():
    import shutil
    return shutil


@lazy_import
def StringIO():
    import StringIO
    return StringIO


@lazy_import
def subprocess():
    import subprocess
    return subprocess


@lazy_import
def tarfile():
    import tarfile
    return tarfile


@lazy_import
def time():
    import time
    return time


@lazy_import
def zipfile():
    import zipfile
    return zipfile


@lazy_import
def jms_utils():
    import jms_utils
    import jms_utils.system
    import jms_utils.terminal
    return jms_utils


@lazy_import
def six():
    import six
    import six.moves
    return six


def check_repo():
    "Checks if current directory is a pyupdater repository"
    repo = True
    if not os.path.exists(settings.CONFIG_DATA_FOLDER):
        log.warning('PyUpdater config data folder is missing')
        repo = False
    if repo is False:
        log.error('Not a PyUpdater repo: must init first.')
        sys.exit(1)


def convert_to_list(data, default=None):
    """Converts data to list. If data isn't a list, tuple or string
    returns Default

    Args:

        data (object): list, tuple or string

    Kwargs:

        default (object): list


    Returns:

        list or default
    """
    if isinstance(data, list):
        return data
    if isinstance(data, tuple):
        return list(data)
    if isinstance(data, six.string_types):
        return [data]
    log.debug('Got type: {}'.format(type(data)))
    log.warning('Using default value of {}'.format(type(default)))
    return default


def get_filename(name, version, platform, easy_data):
    """Gets full filename for given name & version combo

    Args:

        name (str): name of file to get full filename for

       version (str): version of file to get full filename for

       easy_data (dict): data file to search

    Returns:

       (str) Filename with extension
    """
    filename_key = '{}*{}*{}*{}*{}'.format('updates', name, version,
                                           platform, 'filename')
    filename = easy_data.get(filename_key)

    log.debug("Filename for {}-{}: {}".format(name, version, filename))
    return filename


def get_hash(data):
    """Get hash of object

    Args:

        data (object): Object you want hash of.

    Returns:

        (str): sha256 hash
    """
    hash_ = hashlib.sha256(data).hexdigest()
    log.debug('Hash for binary data: {}'.format(hash_))
    return hash_


def get_highest_version(name, plat, easy_data):
    """Parses version file and returns the highest version number.

    Args:

       name (str): name of file to search for updates

       easy_data (dict): data file to search

    Returns:

       (str) Highest version number
    """
    version_key = '{}*{}*{}'.format('latest', name, plat)
    version = easy_data.get(version_key)

    if version is not None:
        log.debug('Highest version: {}'.format(version))
    else:
        log.error('No updates for "{}" on {} exists'.format(name, plat))
    return version


def get_mac_dot_app_dir(directory):
    """Returns parent directory of mac .app

    Args:

       directory (str): Current directory

    Returns:

       (str): Parent directory of mac .app
    """
    return os.path.dirname(os.path.dirname(os.path.dirname(directory)))


def get_package_hashes(filename):
    """Provides hash of given filename.

    Args:

        filename (str): Name of file to hash

    Returns:

        (str): sha256 hash
    """
    log.debug('Getting package hashes')
    filename = os.path.abspath(filename)
    with open(filename, 'rb') as f:
        data = f.read()

    _hash = hashlib.sha256(data).hexdigest()
    log.debug('Hash for file {}: {}'.format(filename, _hash))
    return _hash


def gzip_decompress(data):
    """Decompress gzip data

    Args:

        data (str): Gzip data


    Returns:

        (data): Decompressed data
    """
    compressed_file = StringIO.StringIO()
    compressed_file.write(data)
    #
    # Set the file's current position to the beginning
    # of the file so that gzip.GzipFile can read
    # its contents from the top.
    #
    compressed_file.seek(0)
    decompressed_file = gzip.GzipFile(fileobj=compressed_file, mode='rb')
    data = decompressed_file.read()
    compressed_file.close()
    decompressed_file.close()
    return data


def setup_appname(config):  # pragma: no cover
    if config.APP_NAME is not None:
        default = config.APP_NAME
    else:
        default = None
    config.APP_NAME = jms_utils.terminal.get_correct_answer('Please enter '
                                                            'app name',
                                                            required=True,
                                                            default=default)


def setup_company(config):  # pragma: no cover
    if config.COMPANY_NAME is not None:
        default = config.COMPANY_NAME
    else:
        default = None
    temp = jms_utils.terminal.get_correct_answer('Please enter your comp'
                                                 'any or name',
                                                 required=True,
                                                 default=default)
    config.COMPANY_NAME = temp


def setup_urls(config):  # pragma: no cover
    url = jms_utils.terminal.get_correct_answer('Enter a url to ping for '
                                                'updates.', required=True)
    config.UPDATE_URLS = [url]
    while 1:
        answer = jms_utils.terminal.ask_yes_no('Would you like to add '
                                               'another url for backup?',
                                               default='no')
        if answer is True:
            url = jms_utils.terminal.get_correct_answer('Enter another url.',
                                                        required=True)
            config.UPDATE_URLS.append(url)
        else:
            break


def setup_patches(config):  # pragma: no cover
    config.UPDATE_PATCHES = jms_utils.terminal.ask_yes_no('Would you like to '
                                                          'enable patch upda'
                                                          'tes?',
                                                          default='yes')


def setup_scp(config):  # pragma: no cover
    _temp = jms_utils.terminal.get_correct_answer('Enter remote dir',
                                                  required=True)
    config.SSH_REMOTE_DIR = _temp
    config.SSH_HOST = jms_utils.terminal.get_correct_answer('Enter host',
                                                            required=True)

    config.SSH_USERNAME = jms_utils.terminal.get_correct_answer('Enter '
                                                                'usernmae',
                                                                required=True)


def setup_object_bucket(config):  # pragma: no cover
    _temp = jms_utils.terminal.get_correct_answer('Enter bucket name',
                                                  required=True)
    config.OBJECT_BUCKET = _temp


def setup_uploader(config):  # pragma: no cover
    answer1 = jms_utils.terminal.ask_yes_no('Would you like to add scp '
                                            'settings?', default='no')

    answer2 = jms_utils.terminal.ask_yes_no('Would you like to add a '
                                            'bucket?', default='no')

    if answer1:
        setup_scp(config)

    if answer2:
        setup_object_bucket(config)


def initial_setup(config):  # pragma: no cover
    setup_appname(config)
    setup_company(config)
    setup_urls(config)
    setup_patches(config)
    setup_uploader(config)
    return config


def repo_update_attr_urls(config):  # pragma: no cover
    "Updates url to new attribute"
    log.info('Checking for deprecated UPDATE_URL')
    if hasattr(config, 'UPDATE_URLS'):
        if config.UPDATE_URLS is None:
            config.UPDATE_URL = []
        if isinstance(config.UPDATE_URLS, tuple):
            config.UPDATE_URLS = list(config.UPDATE_URLS)
        if isinstance(config.UPDATE_URLS, six.string_types):
            config.UPDATE_URLS = [config.UPDATE_URLS]

    if hasattr(config, 'UPDATE_URL'):
        log.info('Updating to UPDATE_URLS')
        if isinstance(config.UPDATE_URL, six.string_types):
            config.UPDATE_URLS.append(config.UPDATE_URL)
        if isinstance(config.UPDATE_URL, list):
            config.UPDATE_URLS += config.UPDATE_URL
        if isinstance(config.UPDATE_URL, tuple):
            config.UPDATE_URLS += list(config.UPDATE_URL)
        del config.UPDATE_URL


def repo_update_remove_attr(config):  # pragma: no cover
    "Removes unused attributes"
    log.info('Looking for unused attributes')
    upload_settings = False
    if hasattr(config, 'REMOTE_DIR'):
        log.info('Deleting REMOTE_DIR')
        del config.REMOTE_DIR
        upload_settings = True
    if hasattr(config, 'HOST'):
        log.info('Deleting HOST')
        del config.HOST
        upload_settings = True
    if hasattr(config, 'USERNAME'):
        log.info('Deleting USERNAME')
        del config.USERNAME
        upload_settings = True
    if hasattr(config, 'PASSWORD'):
        log.info('Deleting PASSWORD')
        del config.PASSWORD
        upload_settings = True
    if hasattr(config, 'DEBUG'):
        log.info('Deleting DEBUG')
        del config.DEBUG
    if upload_settings is True:
        log.info('Need uploader settings update')
        setup_uploader(config)


def repo_update(config):
    repo_update_attr_urls(config)
    repo_update_remove_attr(config)


def make_archive(name, version, target):
    """Used to make archives of file or dir. Zip on windows and tar.gz
    on all other platforms

    Args:
        name - Name of app. Used to create final archive name

        version - Version of app. Used to create final archive name

        target - name of actual target file or dir.

    Returns:
         (str) - name of archive
    """
    file_dir = os.path.dirname(os.path.abspath(target))
    filename = '{}-{}-{}'.format(name, jms_utils.system.get_system(), version)
    filename_path = os.path.join(file_dir, filename)

    log.debug('starting archive')

    ext = os.path.splitext(target)[1]
    temp_file = name + ext

    # Remove file if it exists. Found during testing...
    if os.path.exists(temp_file):
        log.debug('Removing: {}'.format(temp_file))
        if os.path.isdir(temp_file):
            shutil.rmtree(temp_file, ignore_errors=True)
        else:
            os.remove(temp_file)
    if os.path.isfile(target):
        shutil.copy(target, temp_file)
    else:
        shutil.copytree(target, temp_file)
    # Only use zip on windows. Zip doens't preserve file
    # permissions on nix & mac
    if jms_utils.system.get_system() == 'win':  # pragma: no cover
        ext = '.zip'
        with zipfile.ZipFile(filename_path + '.zip', 'w') as zf:
            zf.write(target, temp_file)
    else:
        ext = '.tar.gz'
        if os.path.isfile(target):
            with tarfile.open(filename_path + '.tar.gz', 'w:gz') as tar:
                tar.add(target, temp_file)
        else:
            shutil.make_archive(filename, 'gztar', file_dir, temp_file)

    if os.path.exists(temp_file):
        log.debug('Removing: {}'.format(temp_file))
        if os.path.isfile(temp_file):
            os.remove(temp_file)
        else:
            shutil.rmtree(temp_file, ignore_errors=True)
    output_filename = filename + ext
    log.debug('Archive output filename: {}'.format(output_filename))
    return output_filename


def parse_platform(name):
    """Parses platfrom name from given string

    Args:

        name (str): Name to be parsed

    Returns:

        (str): Platform name
    """
    try:
        re_str = '[mnw]{1}[ai]{1}[cnx]{1}[6]?[4]?'
        platform_name = re.compile(re_str).findall(name)[0]
        log.debug('Platform name is: {}'.format(platform_name))
    except IndexError:
        raise UtilsError('')

    return platform_name


def pretty_time(sec):
    """Turns seconds into a human readable format. Example: 2020/07/31 12:22:83

    Args:

        sec (int): seconds since unix epoch

    Returns:

        (str): Human readable time
    """
    return time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime(sec))


def remove_dot_files(files):
    """Removes hidden dot files from file list

    Args:

        files (list): List of file names

    Returns:

        (list): List of filenames with dot files, .stuff, removed
    """
    new_list = []
    for l in files:
        if not l.startswith('.'):
            new_list.append(l)
    return new_list


def run(cmd):
    """Logs a command before running it in subprocess.

    Args:

        cmd (str): command to be ran in subprocess

    Returns:

        (int): Exit code
    """
    log.debug('Command: {}'.format(cmd))
    exit_code = subprocess.call(cmd)
    return exit_code


def _decode_offt(bytes):
    """Decode an off_t value from a string.

    This decodes a signed integer into 8 bytes.  I'd prefer some sort of
    signed vint representation, but this is the format used by bsdiff4.
    """
    if sys.version_info[0] < 3:
        bytes = map(ord, bytes)
    x = bytes[7] & 0x7F
    for b in xrange(6, -1, -1):
        x = x * 256 + bytes[b]
    if bytes[7] & 0x80:
        x = -x
    return x


class bsdiff4_py(object):
    """Pure-python version of bsdiff4 module that can only patch, not diff.

    By providing a pure-python fallback, we don't force frozen apps to
    bundle the bsdiff module in order to make use of patches.  Besides,
    the patch-applying algorithm is very simple.
    """
    @staticmethod
    def patch(source, patch):  # pragma: no cover
        #  Read the length headers
        l_bcontrol = _decode_offt(patch[8:16])
        l_bdiff = _decode_offt(patch[16:24])
        #  Read the three data blocks
        e_bcontrol = 32 + l_bcontrol
        e_bdiff = e_bcontrol + l_bdiff
        bcontrol = bz2.decompress(patch[32:e_bcontrol])
        bdiff = bz2.decompress(patch[e_bcontrol:e_bdiff])
        bextra = bz2.decompress(patch[e_bdiff:])
        #  Decode the control tuples
        tcontrol = []
        for i in xrange(0, len(bcontrol), 24):
            tcontrol.append((
                _decode_offt(bcontrol[i:i+8]),
                _decode_offt(bcontrol[i+8:i+16]),
                _decode_offt(bcontrol[i+16:i+24]),
            ))
        #  Actually do the patching.
        #  This is the bdiff4 patch algorithm in slow, pure python.
        source = six.BytesIO(source)
        result = six.BytesIO()
        bdiff = six.BytesIO(bdiff)
        bextra = six.BytesIO(bextra)
        for (x, y, z) in tcontrol:
            diff_data = bdiff.read(x)
            orig_data = source.read(x)
            if sys.version_info[0] < 3:
                for i in xrange(len(diff_data)):
                    result.write(chr((ord(diff_data[i]) +
                                 ord(orig_data[i])) % 256))
            else:
                for i in xrange(len(diff_data)):
                    result.write(bytes([(diff_data[i] + orig_data[i]) % 256]))
            result.write(bextra.read(y))
            source.seek(z, os.SEEK_CUR)
        return result.getvalue()


class EasyAccessDict(object):
    """Provides access to dict by pass a specially made key to
    the get method. Default key sep is "*". Example key would be
    updates*mac*1.7.0 would access {"updates":{"mac":{"1.7.0": "hi there"}}}
    and return "hi there"

    Kwargs:

        dict_ (dict): Dict you would like easy asses to.

        sep (str): Used as a delimiter between keys
    """

    def __init__(self, dict_=None, sep='*'):
        self.sep = sep
        if not isinstance(dict_, dict):
            log.debug('Did not pass dict')
            self.dict = dict()
            log.debug('Loading empty dict')
        else:
            self.dict = dict_

    def get(self, key):
        """Retrive value from internal dict.

        args:

            key (str): Key to access value

        Returns:

            (object): Value of key if found or None
        """
        try:
            layers = key.split(self.sep)
            value = self.dict
            for key in layers:
                value = value[key]
            log.debug('Found Key')
            return value
        except KeyError:
            log.debug('Key Not Found')
            return None
        except Exception as err:  # pragma: no cover
            log.error(str(err), exc_info=True)
            return None

    # Because I always forget call the get method
    def __call__(self, key):
        return self.get(key)

    def __str__(self):
        return str(self.dict)


class Version(object):
    """Normalizes version strings of different types. Examples
    include 1.2, 1.2.1, 1.2b and 1.1.1b

    Args:

        version (str): Version number to normalizes
    """
    v_re = re.compile('(?P<major>\d+)\.(?P<minor>\d+)\.?(?P<'
                      'patch>\d+)?-?(?P<release>[a,b])?(?P<'
                      'releaseversion>\d+)?')

    v_re_big = re.compile('(?P<major>\d+)\.(?P<minor>\d+)\.'
                          '(?P<patch>\d+)\.(?P<release>\d+)'
                          '\.(?P<releaseversion>\d+)')

    def __init__(self, version):
        self.version_str = version
        self._parse_version_str(version)

    def _parse_version_str(self, version):
        count = self._quick_sanatize(version)
        try:
            # version in the form of 1.1, 1.1.1, 1.1.1-b1, 1.1.1a2
            if count == 4:
                version_data = self._parse_parsed_version(version)
            else:
                version_data = self._parse_version(version)
        except AssertionError:
            raise VersionError('Cannot parse version')

        self.major = int(version_data.get('major', 0))
        self.minor = int(version_data.get('minor', 0))
        patch = version_data.get('patch')
        if patch is None:
            self.patch = 0
        else:
            self.patch = int(patch)
        release = version_data.get('release')
        if release is None:
            self.release = 2
        # Convert to number for easy comparison and sorting
        elif release == 'b':
            self.release = 1
        elif release == 'a':
            self.release = 0
        else:
            try:
                self.release = int(release)
            except ValueError:
                log.debug('Cannot parse release. Setting as stable')
                # Marking release as stable
                self.release = 2

        release_version = version_data.get('releaseversion')
        if release_version is None:
            self.release_version = 0
        else:
            self.release_version = int(release_version)
        self.version_tuple = (self.major, self.minor, self.patch,
                              self.release, self.release_version)

    def _parse_version(self, version):
        r = self.v_re.search(version)
        assert r is not None
        return r.groupdict()

    def _parse_parsed_version(self, version):
        r = self.v_re_big.search(version)
        assert r is not None
        return r.groupdict()

    def _quick_sanatize(self, version):
        log.debug('Version str: {}'.format(version))
        ext = os.path.splitext(version)[1]
        # Removing file extensions, to ensure count isn't
        # contaminated
        if ext == '.zip':
            log.debug('Removed ".zip"')
            version = version[:-4]
        elif ext == '.gz':
            log.debug('Removed ".tar.gz"')
            version = version[:-7]
        count = version.count('.')
        # There will be 4 dots when version is passed
        # That was created with Version object.
        # 1.1 once parsed will be 1.1.0.0.0
        if count not in [1, 2, 4]:
            msg = ('Incorrect version format. 1 or 2 dots '
                   'You have {} dots'.format(count))
            log.error(msg)
            raise VersionError(msg)
        return count

    def __str__(self):
        return '.'.join(map(str, self.version_tuple))

    def __repr__(self):
        return '{}: {}'.format(self.__class__.__name__,
                               self.version_str)

    def __eq__(self, obj):
        return self.version_tuple == obj.version_tuple

    def __ne__(self, obj):
        return self.version_tuple != obj.version_tuple

    def __lt__(self, obj):
        return self.version_tuple < obj.version_tuple

    def __gt__(self, obj):
        return self.version_tuple > obj.version_tuple

    def __le__(self, obj):
        return self.version_tuple <= obj.version_tuple

    def __ge__(self, obj):
        return self.version_tuple >= obj.version_tuple
