from db import Doc, db

class User(Doc):
    collection = "users"
    def __init__(self, user_id):
        self.user_id = user_id
        self.fumbles = 0
        self.crits = 0
        self.nat100s = 0
        self.load(db.collection(self.collection).find_one(self.primary_fil()))

    def primary_fil(self):
        return {'user_id': self.user_id}

    def increment_fumble_count(self):
        self.fumbles += 1

    def increment_crit_count(self):
        self.crits += 1

    def increment_nat_100_count(self):
        self.nat100s += 1
