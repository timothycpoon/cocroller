from pymongo import MongoClient

class DB:
    def __init__(self):
        self.initialized = False
        self.db = None

    def initialize(self, connection_string: str):
        if self.initialized:
            return
        self.db = MongoClient(connection_string)['cocroller']
        self.initialized = True

    def collection(self, collection: str):
        return self.db[collection]

db = DB()

class Doc(object):
    def primary_fil(self):
        return {}
    def load(self, doc):
        if not doc:
            return
        for k, v in doc.items():
            setattr(self, k, v)
    def save(self):
        db.collection(self.collection).replace_one(self.primary_fil(), vars(self), True)
