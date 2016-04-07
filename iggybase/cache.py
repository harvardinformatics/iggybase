from werkzeug.contrib.cache import SimpleCache
from functools import wraps
import logging

class Cache:

    TIMEOUT = 5 * 60
    VERSION_MIN = 1
    VERSION_MAX = 100

    def __init__(self):
        self.store = SimpleCache()
        self.refresh_key = {}
        self.version = {}

    def get(self, key):
        if key in self.refresh_key:
            key = self.add_version(key)
        logging.info('GET: ' + key)
        res = self.store.get(key)
        return res

    def set(self, key, val, timeout = None, refresh_on = [], set_refresh = True):
        if set_refresh:
            self.set_refresh(key, refresh_on)
        if key in self.refresh_key:
            key = self.add_version(key)
        if not timeout:
            timeout = self.TIMEOUT
        logging.info('SET: ' + key)
        self.store.set(key, val, timeout)

    def set_refresh(self, key, refresh_on):
        if refresh_on:
            refresh_on = self.lower_list(refresh_on)
            self.refresh_key[key] = refresh_on
        elif key in self.refresh_key:
            self.refresh_key.pop(key, None)

    def add_version(self, key):
        version = []
        for obj in self.refresh_key[key]:
            if not obj in self.version:
                self.version[obj] = self.VERSION_MIN
            version.append(obj + str(self.version[obj]))
        return key + '|v.' + '_'.join(version)

    def increment_version(self, objs):
        objs = self.lower_list(objs)
        for obj in objs:
            obj = obj.lower()
            # versions 1 - 100 then start back at 1
            if obj in self.version:
                self.version[obj] += 1
                if self.version[obj] > self.VERSION_MAX:
                    self.version[obj] = self.VERSION_MIN
            else:
                self.version[obj] = self.VERSION_MIN
            logging.info('Increment version: ' + obj + ' to: ' + self.version[obj])

    def make_key(self, route, role, dynamic = None, criteria = None):
        key = route + '|' + str(role)
        if dynamic:
            key += '|' + dynamic
        if criteria:
            key += '|' + criteria
        return key

    def get_version(self, obj):
        if obj in self.version:
            return self.version[obj]
        else:
            return None

    def set_version(self, obj, version):
        if obj and version:
            self.version[obj] = version
            return True
        return False

    @staticmethod
    def lower_list(objs):
        for obj in objs:
            obj = obj.lower()
        return objs


