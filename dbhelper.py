import sqlite3


class DBHelper:
    def __init__(self, dbname="events.sqlite"):
        self.dbname = dbname
        self.conn = sqlite3.connect(dbname, check_same_thread=False)
        self.setup()

    def setup(self):
        print("creating table")
        stmt = """CREATE TABLE IF NOT EXISTS events (
                    event_id INTEGER PRIMARY KEY,
                    event_name TEXT,
                    event_date TEXT,
                    event_time TEXT,
                    duration INTEGER,
                    duration_unit TEXT,
                    attendees TEXT,
                    venue TEXT,
                    owner TEXT
                );"""
        self.conn.execute(stmt)
        self.conn.commit()

    def new_event_id(self):
        stmt = "SELECT MAX(event_id) FROM events;"
        return self.conn.execute(stmt).fetchone()[0] + 1

    def add_event(self, event_details, owner):
        try:
            # temporary: to ensure that all the details are given.
            assert len(event_details) == 5
        except AssertionError as e:
            print("Missing information about the event")

        stmt = "INSERT INTO events (event_id, event_name, event_date, event_time, attendees, venue, owner) VALUES (?, ?, ?, ?, ?, ?, ?)"
        event_id = self.new_event_id()
        print(event_id)
        args = (event_id, *event_details, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def delete_event(self, event_id, owner):
        stmt = "DELETE FROM events WHERE event_id = (?) AND owner = (?)"
        args = (event_id, owner)
        self.conn.execute(stmt, args)
        self.conn.commit()

    def get_events(self, owner):
        stmt = "SELECT event_id, event_name FROM events WHERE owner = (?)"
        args = (owner,)
        return [x[0:2] for x in self.conn.execute(stmt, args)]

    def get_event_info(self, owner, event_id):
        stmt = """
        SELECT event_id, event_name, event_date, event_time, venue, attendees FROM events WHERE owner = (?) AND event_id = (?)
        ;"""
        args = (owner, event_id)
        c = self.conn.cursor().execute(stmt, args)
        cols = [x[0] for x in c.description]
        details = c.fetchall()
        print(details)
        event_dic = {c: d for c, d in zip(cols, details[0])}
        return event_dic

    def update_event_info(self, owner, event_details):
        print(event_details)
        event_id = event_details["UPDATE"]["CURRENT_EVENT"]
        feature = event_details["UPDATE"]["CURRENT_FEATURE"]
        input = event_details["UPDATE"]["FEATURE_INPUT"]
        stmt = """
        UPDATE events SET {} = (?) WHERE owner = (?) AND event_id = (?)
        ;""".format(
            feature
        )
        print(stmt)
        args = (input, owner, event_id)
        self.conn.execute(stmt, args)
        self.conn.commit()
        return


db = DBHelper()
