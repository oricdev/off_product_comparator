# coding=utf-8
from flask import Flask, session
from array import array
from pprint import pprint


class Log(object):
    """
    Logs to be printed and also returned to the client (ajax mode)
    """

    @staticmethod
    def __init__():
        print "init log"
        # todo: global class? voir ci-dessous
        # https://stackoverflow.com/questions/16511321/python-global-object-variable
        global toto
        toto = []
        # Log.ptr = 0
        # Max. number of log-lines to return in one call (from bottom-up)
        Log.MAX_RETURNED_IN_ONE_SHOT = 100
        # todo: NOT IMPLEMENTED
        # Delay in seconds between 2 Ajax requests from a specific client (use hash with ips => not implemented yet)
        Log.DELAY_BETWEEN_TWO_REQUESTS_PER_USER = 2

    @staticmethod
    def clear():
        print "clearing log"
        Log.ptr = 0
        session['logs'] = []

    @staticmethod
    def initialize(init_with_list):
        # session['logs'] = init_with_list
        Log.ptr = len(init_with_list)
        print "initialized back.. Log.ptr = %r " % str(Log.ptr)

    @staticmethod
    def add_msg(message):
        # if bool(message and message.strip()):
        global toto
        toto.append(message)

    @staticmethod
    def get_bunch(from_ptr):
        global toto
        try:
            if len(toto) - int(from_ptr) > Log.MAX_RETURNED_IN_ONE_SHOT:
                from_ptr = len(toto) - Log.MAX_RETURNED_IN_ONE_SHOT
            return toto[from_ptr:]
        except NameError:
            return []
