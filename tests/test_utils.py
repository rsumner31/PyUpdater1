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

import os

from jms_utils.paths import ChDir
import pytest

from pyupdater.utils import (check_repo,
                             convert_to_list,
                             EasyAccessDict,
                             get_hash,
                             get_mac_dot_app_dir,
                             get_package_hashes,
                             parse_platform,
                             remove_dot_files,
                             Version
                             )
from pyupdater.utils.exceptions import UtilsError, VersionError
from pyupdater.utils.package import Patch, Package


TEST_DATA_DIR = os.path.join(os.path.dirname(__file__), 'test data',
                             'patcher-test-data')


@pytest.mark.usefixtures('cleandir')
class TestUtils(object):

    @pytest.fixture()
    def hasher(self):
        with open('hash-test.txt', 'w') as f:
            f.write('I should find some lorem text' * 123)
        return None

    def test_check_repo_fail(self):
        with pytest.raises(SystemExit):
            check_repo()

    def test_convert_to_list(self):
        assert isinstance(convert_to_list('test'), list)
        assert isinstance(convert_to_list(('test', 'test2')), list)
        assert isinstance(convert_to_list(['test']), list)

    def test_convert_to_list_default(self):
        assert isinstance(convert_to_list({}, default=[]), list)

    def test_package_hash(self, hasher):
        digest = ('cb44ec613a594f3b20e46b768c5ee780e0a9b66ac'
                  '6d5ac1468ca4d3635c4aa9b')
        assert digest == get_package_hashes('hash-test.txt')

    def test_get_hash(self):
        digest = ('380fd2bf3d78bb411e4c1801ce3ce7804bf5a22d79'
                  '405d950e5d5c8f3169fca0')
        assert digest == get_hash('Get this hash please')

    def test_get_mac_app_dir(self):
        main = 'Main'
        path = os.path.join(main, 'Contents', 'MacOS', 'app')
        assert get_mac_dot_app_dir(path) == main

    def test_easy_access_dict(self):
        good_data = {'test': True}
        easy = EasyAccessDict()
        assert easy('bad-key') is None
        good_easy = EasyAccessDict(good_data)
        assert good_easy.get('test') is True
        assert good_easy.get('no-test') is None

    def test_parse_platform(self):
        assert parse_platform('app-mac-0.1.0.tar.gz') == 'mac'
        assert parse_platform('app-win-1.0.0.zip') == 'win'
        assert parse_platform('Email Parser-mac-0.2.0.tar.gz') == 'mac'

    def test_parse_platform_fail(self):
        with pytest.raises(UtilsError):
            parse_platform('app-nex-1.0.0.tar.gz')

    def test_remove_dot_files(self):
        bad_list = ['.DS_Store', 'test', 'stuff', '.trash']
        good_list = ['test', 'stuff']
        for n in remove_dot_files(bad_list):
            assert n in good_list

    def test_version(self):
        v1 = Version('1.1b1')
        v2 = Version('1.1')
        assert v2 > v1
        v3 = Version('1.2.1b1')
        v4 = Version('1.2.1')
        assert v3 < v4
        v5 = Version('1.2.1a1')
        v6 = Version('1.2.1a2')
        assert v5 < v6
        assert Version('5.0') == Version('5.0')
        assert Version('4.5') != Version('5.1')
        with pytest.raises(VersionError):
            Version('1')
        with pytest.raises(VersionError):
            Version('1.1.1.1')

    def test_package_1(self):
        test_file_1 = 'jms-mac-0.0.1.zip'
        with ChDir(TEST_DATA_DIR):
            p1 = Package(test_file_1)

        assert p1.name == 'jms'
        assert p1.version == '0.0.1.2.0'
        assert p1.filename == test_file_1
        assert p1.platform == 'mac'
        assert p1.info['status'] is True

    def test_package_ignored_file(self):
        with open('.DS_Store', 'w') as f:
            f.write('')
        p = Package('.DS_Store')
        assert p.info['status'] is False

    def test_package_bad_extension(self):
        test_file_2 = 'pyu-win-0.0.2.bzip2'
        with ChDir(TEST_DATA_DIR):
            p2 = Package(test_file_2)

        assert p2.filename == test_file_2
        assert p2.name is None
        assert p2.version is None
        assert p2.info['status'] is False
        assert p2.info['reason'] == ('Not a supported archive format: '
                                     '{}'.format(test_file_2))

    def test_package_bad_version(self):
        with ChDir(TEST_DATA_DIR):
            p = Package('pyu-win-1.tar.gz')
        assert p.info['reason'] == 'Package version not formatted correctly'

    def test_package_bad_platform(self):
        with ChDir(TEST_DATA_DIR):
            p = Package('pyu-wi-1.1.tar.gz')
        assert p.info['reason'] == 'Package platform not formatted correctly'

    def test_package_bad_version(self):
        with ChDir(TEST_DATA_DIR):
            p = Package('pyu-win-1.tar.gz')
        assert p.info[u'reason'] == u'Package version not formatted correctly'

    def test_package_bad_platform(self):
        with ChDir(TEST_DATA_DIR):
            p = Package('pyu-wi-1.1.tar.gz')
        assert p.info[u'reason'] == u'Package platform not formatted correctly'

    def test_package_ignored_file(self):
        test_file_3 = '.DS_Store'
        with ChDir(TEST_DATA_DIR):
            Package(test_file_3)

    def test_package_missing(self):
        test_file_4 = 'jms-nix-0.0.3.tar.gz'
        with ChDir(TEST_DATA_DIR):
            Package(test_file_4)

    def test_patch(self):
        with open('app.py', 'w') as f:
            f.write('a = 0')

        info = {
            'dst': 'app.py',
            'patch_name': 'p-name-1',
            'package': 'filename-mac-0.1.1.tar.gz'
            }
        p = Patch(info)
        assert p.ready is True

    def test_patch_bad_info(self):
        info = {
            'dst': 'app.py',
            'patch_name': 'p-name-1',
            'package': 'filename-mac-0.1.1.tar.gz'
            }
        temp_dst = info['dst']
        info['dst'] = None
        p = Patch(info)
        assert p.ready is False

        info['dst'] = temp_dst
        temp_patch = info['patch_name']
        info['patch_name'] = None
        p = Patch(info)
        assert p.ready is False

        info['patch_name'] = temp_patch
        info['package'] = None
        p = Patch(info)
        assert p.ready is False
