import os
import tempfile
import time
import base64
try:
    import cPickle as pickle
except:
    import pickle

class FileCache:
    
    def __init__(self, name, expireInMinutes = 1, tempdir = None, prefix = 'tmp', suffix = 'cache'):
        if not expireInMinutes:
            self.expire = None
        else:
            self.expire = expireInMinutes * 60
        temppath = tempdir or tempfile.gettempdir()
        self.name = os.path.join(temppath, prefix + name + "." + suffix)
         
    def load(self):
        data = None
        if os.path.exists(self.name):
            mtime = os.path.getmtime(self.name)
            if self.expire is None or mtime + self.expire > time.time():
                _file = None
                try:
                    _file = open(self.name,'rb')
                    data = pickle.load(_file)
                except:
                    raise
                finally:
                    if _file: _file.close()
            else:
                try:
                    # lets clean up if expired
                    os.unlink(self.name)
                except:
                    pass
        return data

    def save(self, data):
        _file = None
        try:
            _file = open(self.name, 'wb')
            pickle.dump(data, _file, pickle.HIGHEST_PROTOCOL)
            _file.flush()
        except:
            raise
        finally:
            if _file: _file.close()            
