# Copyright (c) 2020 Jarret Dyrbye
# Distributed under the MIT software license, see the accompanying
# file LICENSE or http://www.opensource.org/licenses/mit-license.php

import os
import json
import logging

from moneysocket.wad.rate import Rate


PERSIST_FILENAME = "rate-persist.json"

EMPTY_DB = {"rates": {},
           }

class RateDb():
    def __init__(self, persist_dir):
        RateDb._make_dirs_exist(persist_dir)
        self.filename = os.path.join(persist_dir, PERSIST_FILENAME)
        logging.info("using: %s" % self.filename)
        self.make_exist(self.filename)
        self.db = self.read_json(self.filename)

    ###########################################################################

    @staticmethod
    def _make_dirs_exist(dir_path):
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

    ###########################################################################

    def make_exist(self, filename):
        if os.path.exists(filename):
            return
        logging.info("initializing new rate persist db: %s" % filename)
        dir_path = os.path.dirname(filename)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        record = EMPTY_DB.copy()
        self.write_json(filename, record)

    def write_file(self, path, content):
        f = open(path, 'w')
        f.write(content)
        f.close()

    def write_json(self, path, info, quick=True):
        content = (json.dumps(info) if quick else
                   json.dumps(info, indent=1, sort_keys=True))
        self.write_file(path, content)

    def read_json(self, path):
        f = open(path, 'r')
        c = f.read()
        info = json.loads(c)
        f.close()
        return info

    def persist(self):
        self.write_json(self.filename, self.db)

    def depersist(self):
        os.remove(self.filename)

    ###########################################################################

    def key_str(self, base_code, quote_code):
        return "%s_%s" % (base_code, quote_code)

    def add_rate(self, rate):
        self.db['rates'][rate.key_str()] = rate
        inv = rate.invert()
        self.db['rates'][inv.key_str()] = inv
        self.persist()

    def remove_rate(self, base_code, quote_code):
        k = self.key_str(base_code, quote_code)
        _ = self.db['rates'].pop(k, None)
        k = self.key_str(quote_code, base_code)
        _ = self.db['rates'].pop(k, None)
        self.persist()

    def has_rate(self, base_code, quote_code):
        k = self.key_str(base_code, quote_code)
        return k in self.db['rates']

    def get_rates(self):
        return [Rate.from_dict(r) for r in self.db['rates'].values()]

    def get_rate(self, base_code, quote_code):
        k = self.key_str(base_code, quote_code)
        return Rate.from_dict(self.db['rates'][k])
