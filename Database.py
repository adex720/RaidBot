import mysql.connector
# https://pypi.org/project/mysql-connector-python/
# https://github.com/mysql/mysql-connector-python

import math
import time

from numpy import long


def get_first(result):
    if result is None:
        return None
    return [x for x in result][0]


def get_at(result, i):
    if result is None:
        return None
    return [x for x in result][i]


class Database:

    def __init__(self, address, port, name, username, password):
        self.db = mysql.connector.connect(host=address, port=port, database=name, username=username, password=password)
        print('Connected to database')

    def get_last_update_time(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT last_updated FROM memory;')
        return int(get_first(cursor.fetchone()))

    def updated(self, t=0):
        if t == 0:
            t = math.floor(time.time() * 1000)

        cursor = self.db.cursor()
        cursor.execute('UPDATE memory SET last_updated=' + str(t) + ';')
        self.db.commit()

    def get_update_frequency(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT update_frequency FROM memory;')
        return int(get_first(cursor.fetchone()))

    def set_update_frequency(self, hours):
        cursor = self.db.cursor()
        cursor.execute('UPDATE memory SET update_frequency=' + str(hours) + ';')

    def get_info_channel_id(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT info_channel FROM memory;')
        return int(get_first(cursor.fetchone()))

    def get_reminder_channel_id(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT reminder_channel FROM memory;')
        return int(get_first(cursor.fetchone()))

    def get_tag_by_user_id(self, user_id):
        cursor = self.db.cursor()
        cursor.execute('SELECT tag FROM members WHERE user_id="' + user_id + '";')
        return get_first(cursor.fetchone())

    def get_name_by_user_id(self, user_id):
        cursor = self.db.cursor()
        cursor.execute('SELECT name FROM members WHERE user_id="' + user_id + '";')
        return get_first(cursor.fetchone())

    def get_user_id_by_tag(self, tag):
        cursor = self.db.cursor()
        cursor.execute('SELECT user_id FROM members WHERE tag="' + tag + '";')
        return long(get_first(cursor.fetchone()))

    def get_remind_time(self, tag):
        cursor = self.db.cursor()
        cursor.execute('SELECT hours FROM members WHERE tag="' + tag + '";')
        return int(get_first(cursor.fetchone()))

    def remove_by_user_id(self, user_id, cursor=None):
        if cursor is None:
            cursor = self.db.cursor()

        cursor.execute('DELETE FROM members WHERE user_id=' + user_id + ';')
        self.db.commit()

    def remove_by_tag(self, tag, cursor=None):
        if cursor is None:
            cursor = self.db.cursor()

        cursor.execute('DELETE FROM members WHERE tag=' + tag + ';')
        self.db.commit()

    def has_reminder(self, tag, cursor=None):
        if cursor is None:
            cursor = self.db.cursor()

        cursor.execute('SELECT hours FROM members WHERE tag=' + tag + ';')
        return cursor.fetchall() is not None

    async def set_reminder_time(self, user_id, hours, tag, client):
        """Returns:
            -1 when the player is not in the clan
            0 when new reminder time was set or previous one had it's time modified
            1 when new reminder time was set and a reminder for the same tag was removed from another user id
        """

        cursor = self.db.cursor()
        cursor.execute('SELECT name FROM members WHERE tag="' + tag + '";')
        result = cursor.fetchone()
        if result is None:
            # tag is not in database
            member_data = await client.get_members()
            username = None
            for member in member_data:
                if member['tag'] == tag:
                    username = member['name']
                    break

            if username is None:
                return -1

            # tag doesn't have reminder yet
            cursor.execute('INSERT INTO members (name, tag, hours, user_id) VALUES ("' +
                           username + '", "' + tag + '", ' + str(hours) + ', ' + str(user_id) + ');')
            self.db.commit()
            return 0

        cursor.execute('SELECT user_id FROM members WHERE user_id=' + str(user_id) + ';')
        result = cursor.fetchall()
        old_user_id = -1 if result is None else int(get_first(result[0]))

        if old_user_id != user_id:
            # given tag matches another user id in database
            cursor.execute(
                'UPDATE members SET hours =' + str(hours) + ', user_id=' + str(user_id) + ' WHERE tag="' + tag + '";')
            self.db.commit()
            return 1

        # tag is already linked to the user
        cursor.execute('UPDATE members SET hours =' + str(hours) + ' WHERE user_id=' + str(user_id) + ';')
        self.db.commit()
        return 0

    def get_reminders(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM members;')
        return cursor.fetchall()

    def get_manager_roles(self):
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM manager_roles;')
        return [int(x) for x in cursor.fetchone()]
