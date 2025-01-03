import yaml
from pathlib import Path
C = None

class AttrDict(dict):
    def __getattr__(self, name):
        try:
            return self[name]
        except (KeyError, RecursionError):
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value


def dict2attrdict(dictionary):
    ret = AttrDict()
    for key, value in dictionary.items():
        if isinstance(value, dict):
            ret[key] = dict2attrdict(value)
        elif isinstance(value, list):
            ret[key] = []
            for v in value:
                if isinstance(v, dict):
                    ret[key].append(dict2attrdict(v))
                else:
                    ret[key].append(v)
        else:
            ret[key] = value
    return ret


def attrdict2dict(attrdict):
    ret = dict()
    for key, value in attrdict.items():
        if isinstance(value, AttrDict):
            ret[key] = attrdict2dict(value)
        elif isinstance(value, list):
            ret[key] = []
            for v in value:
                if isinstance(v, AttrDict):
                    ret[key].append(attrdict2dict(v))
                else:
                    ret[key].append(v)
        else:
            ret[key] = value
    return ret


def load_config(fpath):
    with open(fpath, "r") as stream:
        try:
            c = dict2attrdict(yaml.safe_load(stream))
            return c
        except Exception as ex:
            print(ex)
            return None


C = load_config('config.yaml')

if Path('config_private.yaml').exists():
    Cp = load_config('config_private.yaml')
    for k,v in Cp.items():
        C[k] = v
    
