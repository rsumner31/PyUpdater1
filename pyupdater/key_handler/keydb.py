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
import json
import logging
import os
import time

from pyupdater import settings
from pyupdater.storage import Storage

log = logging.getLogger(__name__)


class KeyDB(object):
    u"""Handles finding, sorting, getting meta-data, moving packages.

    Kwargs:

        data_dir (str): Path to directory containing key.db

        load (bool):

            Meaning:

                True: Load db on initialization

                False: Do not load db on initialization
    """

    def __init__(self, data_dir, load=False):
        self.data_dir = data_dir
        self.key_file = os.path.join(self.data_dir, 'key.db')
        self.db = Storage(self.data_dir)
        self.data = None
        if load is True:
            self.load()

    def add_key(self, public, private, key_type='ed25519'):
        u"""Adds key pair to database

        Args:

            public (str): Public key

            private (str): Private key

            key_type (str): The type of key pair. Default ed25519
        """
        _time = time.time()
        if self.data is None:
            self.load()
        num = len(self.data) + 1
        data = {
            u'date': _time,
            u'public': public,
            u'private': private,
            u'revoked': False,
            u'key_type': key_type,
        }
        log.info('Adding public key to db: {}'.format(public))
        self.data[num] = data
        self.save()

    def get_public_keys(self):
        u"Returns a list of all valid public keys"
        return self._get_keys(u'public')

    def get_private_keys(self):
        u"Returns a list of all valid private keys"
        return self._get_keys(u'private')

    def _get_keys(self, key):
        order = []
        keys = []
        log.debug(u'KeyDB: {}'.format(self.data.items()))
        for k, v in self.data.items():
            if v[u'revoked'] is False:
                order.append(int(k))
            else:
                log.debug(u'Key revoked: {}'.format(k))
        order = sorted(order)
        for o in order:
            try:
                data = self.data[o]
                log.debug(u'Got key data')
                pub_key = data[key]
                log.debug(u'Pub key: {}'.format(pub_key))
                keys.append(pub_key)
                log.debug(u'Got public key')
            except KeyError:  # pragma: no cover
                log.debug(u'Key error')
                continue
        return keys

    def get_revoked_key(self):
        u"Returns most recent revoked key pair"
        keys = []
        for k, v in self.data.items():
            if v[u'revoked'] is True:
                keys.append(int(k))
        if len(keys) >= 1:
            key = sorted(keys)[-1]
            info = self.data[key]
        else:
            info = None
        return info

    def revoke_key(self, count=1):
        u"""Revokes key pair

        Args:

            count (int): The number of keys to revoke. Oldest first
        """
        keys = map(str, self.data.keys())
        keys = sorted(keys)
        log.debug(u'List of keys: {}'.format(keys))
        c = 0
        for k in keys:
            if c >= count:
                break
            print(u'Key Type: {}'.format(type(k)))
            k = int(k)
            if self.data[k][u'revoked'] is False:
                self.data[k][u'revoked'] = True
                log.debug(u'Revoked key')
                c += 1
        self.save()

    def load(self):
        u"Loads data from key.db"
        # ToDo: Remove in v1.0
        if os.path.exists(self.key_file):  # pragma: no cover
            log.info('Beginning key.db migration')
            try:
                with open(self.key_file, u'r') as f:
                    self.data = json.loads(f.read())
                log.debug(u'Loaded key.db')
                self.save()
                log.info(u'key.db migration successful')
                os.remove(self.key_file)
                log.info(u'Removed {}'.format(self.key_file))
            except Exception as err:
                log.error(u'Failed to load key.db')
                log.debug(str(err), exc_info=True)
                log.error(u'Migration failed')
        else:
            self.data = self.db.load(settings.CONFIG_DB_KEY_KEYS)
            if self.data is None:
                log.info('Key.db file not found creating new')
                self.data = dict()

    def save(self):
        u"Saves data to key.db"
        log.debug(u'Saving keys...')
        self.db.save(settings.CONFIG_DB_KEY_KEYS, self.data)
        log.debug(u'Saved keys...')
