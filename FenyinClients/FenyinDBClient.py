#! /usr/bin/env python
# -*- coding: utf-8 -*-
__author__ = 'gripleaf'

import sqlite3
import logging as rootlogging
import thread
import threading
from datetime import date, datetime
import os
import json
import sys


class SqliteClient:
    '''
        sqlite client
        use for record all the message we need to record
    '''

    def __init__(self, db_file="tmp/my_mqs.db"):
        '''
            @:param db_file: file path and file name of database
            @:return: an instance of sqlite_client
        '''
        self.db_file = db_file
        self.__lock = thread.allocate_lock()
        self.__init_connect()


    def __init_connect(self):
        if not os.path.isdir(os.path.dirname(self.db_file)):
            raise Exception("uncorrect path of db file [%s]" % os.path.dirname(self.db_file))
        _first = False
        if not os.path.isfile(self.db_file):
            _first = True

        self.__conn = sqlite3.connect(self.db_file, check_same_thread=False)
        self.__cursor = self.__conn.cursor()

        if _first == True:
            self.__init_db_sturct()

    def __init_db_sturct(self):
        '''
            create table FenyinMqs -> id, updated_at, message
        '''
        self.__cursor.execute(
            "CREATE TABLE FenyinMqs(id INTEGER PRIMARY KEY AUTOINCREMENT, updated_at DATE,file_key VARCHAR(512), message VARCHAR(512))")

    def insert_into_db(self, tb_name, cols, vals):
        """
            @:param ta_name: the name of table to process
            @:param cols: the list of columns need to be inserted
            @:param vals: the list of values should be inserted
            @:return
        """
        _query = "insert into %s(%s, updated_at) values(%s, ?)" % (
            tb_name, ','.join(cols), ','.join(["'%s'" % val for val in vals]))

        logging.info("(INSERT)$ %s" % _query)
        try:
            self.__lock.acquire()
            self.__cursor.execute(_query, (datetime.now(),))
            self.__conn.commit()
        except Exception, ex:
            logging.warning("!INSERT!$ %s -> %s" % (_query, ex.message))
        finally:
            self.__lock.release()

    def select_from_db(self, tb_name, cols, cons=[]):
        '''
            @:param tb_name: the name of table to process
            @:param cols: the list of columns need to be
            @:param cons: the list of condition after where
        '''
        _query = "select %s from %s where %s" % (', '.join(cols), tb_name, ' and '.join(cons.append(1)))

        logging.info("(SELECT)$ %s" % _query)
        try:
            self.__lock.acquire()
            _res = self.__cursor.execute(_query)
        except Exception, ex:
            logging.warning("!SELECT!$ %s -> %s" % (_query, ex.message))
            return []
        finally:
            self.__lock.release()
        return _res

    def update_cols_db(self, tb_name, cols, vals, cons=[]):
        '''
            @:param tb_name: the name of table to process
            @:param cols: the list of columns need to be update
            @:param vals: the list of values need to be update
            @:param cons: the list of conditions after where
        '''
        _query = "update %s set %s, updated_at=? where %s" % (
            tb_name, ','.join(['='.join([cols[it], vals[it]]) for it in range(len(vals))]), 'and'.join(cons.append(1)))

        logging.info("(UPDATE)$ %" % _query)
        try:
            self.__lock.acquire()
            self.__cursor.execute(_query, (datetime.now,))
            self.__conn.commit()
        except Exception, ex:
            logging.warning("!UPDATE!$ %s -> %s" % (_query, ex.message))
        finally:
            self.__lock.release()

    def del_cols_db(self, tb_name, cons=[]):
        '''
            @:param tb_name: the name of table
            @:param cons: the list of conditions after where
            @:return: none
        '''
        _query = "delete from %s where %s" % (tb_name, 'and'.join(cons.append(1)))

        logging.info("(DELETE)$ %s" % _query)
        try:
            self.__lock.acquire()
            self.__cursor.execute(_query)
            self.__conn.commit()
        except Exception, ex:
            logging.warning("!DELETE!$: %s -> %s" % (_query, ex.message))
        finally:
            self.__lock.release()


class FenyinDBClient:
    '''
        Fenyin DB Cilent
        use for record all the message we need to record
        be carefull we only use for
    '''

    def __init__(self, Settings):
        '''
            @:param Settings: use for get setting info
            @:return: an instance of fenyin db client
        '''
        # get settings
        try:
            self.__logfile = Settings.Sqlite["log"]
            self.__dbfile = Settings.Sqlite["file"]
        except Exception, e:
            rootlogging.warning("loading fenyin db config failed")
            return
        # initialize the client
        try:
            self.__init_logging()
            self.__init_sqlite()
        except Exception, e:
            rootlogging.warning("initialze client failed. %s" % e.message)

    def __init_logging(self):
        '''
            initialze the logging => record the db system on other log file.
            @:return:
        '''
        global logging
        logging = rootlogging.getLogger("fenyin_db_client_log")
        fh = rootlogging.FileHandler(self.__logfile, 'a', "utf-8")
        fh.setFormatter('%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s')
        fh.setLevel(rootlogging.INFO)
        logging.addHandler(fh)

    def __init_sqlite(self):
        self._db_ins = SqliteClient(self.__dbfile)


    def set_mqs_message(self, json_obj):
        '''
            :param json_obj:
            :return:
        '''
        self._db_ins.insert_into_db('FenyinMqs', ['file_key', 'message'], [json_obj['key'], json.dumps(json_obj)])


    def get_mqs_message(self, key):
        '''
            get mqs message
            @:param key: the key of file in mqs
            @:return:
        '''
        self._db_ins.select_from_db('FenyinMqs', ['file_key', 'message', 'updated_at'], ["file_key='%s'" % key])
        # TODO: return
