#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
# sys.path.append("..")
# from FenyinGlobals import Settings
# sys.path.remove("..")
#import MySQLdb


class DBClient:
    '''
        fenyin db client
    '''

    def __init__(self, addr, port, db, user, passwd):
        pass

    # return False if failed or True for success
    def connect(self):
        pass

    # return False if failed or True for success
    def disconnect(self):
        pass

    def update(self, tb_name, data, pattern):
        print "now"

    # return deleted data
    def delete(self, tb_name, patten):
        pass

    def insert(self, tb_name, data):
        pass

    def search(self, tb_name, cols, pattern):
        pass

    def runCommand(self, cmd, is_commit=False):
        pass

    def _gen_bill(self, pattern, and_jn=' and ', eq_jn='='):
        if not type(pattern) == dict:
            raise TypeError("uncorrect type")
        wh = ""
        for ky, val in pattern.items():
            and_jn.join([wh, eq_jn.join([ky, val])])
        return wh

    @staticmethod
    def overrider(method):
        assert (method.__name__ in dir(DBClient))
        return method


class MySqlClient(DBClient):
    '''
        mysql client
    '''

    INSERT_FORMAT = "insert into %s (%s) values(%s)"

    SEARCH_FORMAT = "select %s from %s where %s"

    UPDATE_FORMAT = "update %s set %s where %s"

    DELETE_FORMAT = "delete from %s where %s"


    def __init__(self, addr, db, user, passwd, port=3306):
        DBClient.__init__(self, addr, port, db, user, passwd)
        self._addr_ = addr
        self._port_ = port
        self._db_ = db
        self._user_ = user
        self._passwd_ = passwd
        self._db_conn_ = None


    @DBClient.overrider
    def insert(self, tb_name, data):
        """
            :desc insert method of sql

            :param tb_name
                string, the name of table in mysql
            :param data
                dict, (key, value) => key is the name of col, value is value of col

            :return: True => success, False => failed
        """
        cmd = self.INSERT_FORMAT % (tb_name, ', '.join(data.keys), ', '.join(data.values))
        curs = self.runCommand(cmd, is_commit=True)
        if curs is None:
            return False
        return True

    @DBClient.overrider
    def update(self, tb_name, data, pattern):
        """
            :desc update method of sql

            :param tb_name
                string, the name of table in mysql
            :param data
                dict, (key, value) => key is the name of col, value the new value of col
            :param pattern
                dict, (key, value) => key is the name of col, value the filter value of col

            :return: True => success, False => failed
        """
        wh = self._gen_bill(pattern)
        sd = self._gen_bill(data, ', ', '=')
        cmd = self.UPDATE_FORMAT % (tb_name, sd, wh)
        curs = self.runCommand(cmd)
        if curs is None:
            return False
        return True


    @DBClient.overrider
    def delete(self, tb_name, patten):
        """
        :desc delete method of sql
        :param tb_name:
            string, the name of table in mysql
        :param patten:
            dict, (key, value) => key is the name of col, value is the filter value of col
        :return: True => success, False => failed
        """
        wh = self._gen_bill(patten)
        cmd = self.DELETE_FORMAT % (tb_name, wh)
        curs = self.runCommand(cmd, is_commit=True)
        if curs is None:
            return False
        return True

    @DBClient.overrider
    def search(self, tb_name, cols, pattern):
        """
        :desc select method of sql
        :param tb_name:
            string, the name of table in mysql
        :param data:
            list, the cols you want to know. empty means all
        :param pattern:
            dict, (key, value) =. key is the name of col, value is the filter value of col
        :return: if failed return [], or return all the values
        """
        if not type(data) == list:
            raise TypeError("uncorrect type")
        wh = self._gen_bill(pattern)
        if len(data) == 0:
            data = "*"
        else:
            data = ", ".join(data)
        cmd = self.SEARCH_FORMAT % (data, tb_name, wh)
        curs = self.runCommand(cmd)
        if curs is None:
            return []
        return curs.fetchall()


    @DBClient.overrider
    def runCommand(self, cmd, is_commit=True):
        print cmd
        cursor = self._db_conn_.cursor()
        try:
            cursor.execute(cmd)
            if is_commit:
                self._db_conn_.commit()
            return cursor
        except:
            self._db_conn_.rollback()
        return None

    @DBClient.overrider
    def connect(self):
        self._db_conn_ = MySQLdb.connect(self._addr_, self._user_, self._passwd_, self._db_, self._port_)


    @DBClient.overrider
    def disconnect(self):
        # close the connection with
        self._db_conn_.close()


class MongoClient(DBClient):
    '''
        mongodb client
    '''

    def __init__(self, addr, port, db, user, passwd):
        DBClient.__init__(self, addr, port, db, user, passwd)

    @DBClient.overrider
    def insert(self, tb_name, data):
        pass

    @DBClient.overrider
    def update(self, tb_name, data, pattern):
        pass

    @DBClient.overrider
    def delete(self, tb_name, data):
        pass

    @DBClient.overrider
    def insert(self, tb_name, data):
        pass

    @DBClient.overrider
    def search(self, tb_name, cols, pattern):
        pass

    @DBClient.overrider
    def runCommand(self, cmd, is_commit=False):
        pass

    @DBClient.overrider
    def connect(self):
        pass

    @DBClient.overrider
    def disconnect(self):
        pass


if __name__ == "__main__":
    print "TODO"


