# -*- coding:utf-8 -*-
import json
import re
import types


# json utils
# author: jerry lin
# e-mial: jerry.lin3000@gmail.com

# dict-json, json-dict

def obj2dict(obj):
    d = {}
    d.update(obj.__dict__)
    return d


def obj2json(obj, encoding="UTF-8", ensure_ascii=False):
    """
    obj2json string
    """
    return json.dumps(obj, encoding, ensure_ascii, default=obj2dict)


class DictMapper(object):
    """
        get object in dict or json by multi_level_key
        :param key_pattern:str
        example:
        a.b.c {a:{b:{c:...}}},
        a[b.c {a:{b:[{c:...},{},{}]}}
        a&dot.b.c {a.:{b:{c:...}}},
        a&lsb[b.c {a[:{b:[{c:...},{},{}]}}
        a&&[b.c {a&:{b:[{c:...},{},{}]}}

        "." : object operator
        "[" : array operator
        "." in key, replaced by &dot
        "[" in key, replaced by &lsb
        "&" in key, replaced by &&
    """

    class Key(object):
        """docstring for Key"""

        def __init__(self, key, int_type=False):
            super(DictMapper.Key, self).__init__()
            self._key = key
            self._int_type = int_type

        def key(self):
            return self._key if self.is_object() else int(self._key)

        def is_array(self):
            return self._int_type

        def is_object(self):
            return not self.is_array()

    def __init__(self, key_pattern):
        super(DictMapper, self).__init__()
        self.keys = []
        self.__parse_keys(key_pattern)

    def __parse_keys(self, keys):
        pattern = re.compile(r"[.\[]")
        keys_ = pattern.split(keys)
        if u'' == keys_[0]:
            keys_.pop(0)
        keys_symbols = pattern.findall(keys)
        if len(keys_) != len(keys_symbols):
            raise Exception(u"{key_pattern} form is wrong, it should start with '.' or '['."
                            .format(key_pattern=keys, ))

        idx = 0
        k_pattern = re.compile(r"&dot|&lsb|&&")
        for k in keys_:
            int_type = "[" == keys_symbols[idx]
            new_k = u""

            kks_ = k_pattern.split(k)
            if u'' == kks_[0]:
                kks_.pop(0)
            kks_symbols = [m.group() for m in k_pattern.finditer(k)]
            if 0 == len(kks_symbols):
                new_k = kks_[0]
            elif not k.startswith(kks_symbols[0]):
                new_k = kks_[0]
                kks_.pop(0)

            i = 0
            for sy in kks_symbols:
                if "&dot" == sy:
                    origin_sy = "."
                elif "&lsb" == sy:
                    origin_sy = "["
                else:
                    origin_sy = "&"

                new_k += origin_sy + kks_[i]
                i += 1

            self.keys.append(DictMapper.Key(new_k, int_type))
            idx += 1

    def dict_get(self, dict_obj, default=None):
        """
        get object in dict or json by multi_level_key
        see json_get
        """
        return self.json_get(dict_obj, default)

    def json_get(self, json_obj, default=None):
        """
        :param json_obj:dict
        :param default
        :return default if key is not exist
        """
        ret = json_obj
        for key in self.keys:
            if key.is_array():
                if not isinstance(ret, types.ListType) \
                        or len(ret) <= key.key():
                    return default
            else:
                if not isinstance(ret, types.DictType) \
                        or key.key() not in ret:
                    return default
            ret = ret[key.key()]
        return ret
