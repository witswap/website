import datetime
import os
import sys
import time


class Log(object):
    def __init__(self, filename, lock, types_file, types_stdout):
        self.filename = filename
        self.lock = lock
        self.types_file = types_file.split(",")
        self.types_stdout = types_stdout.split(",")

        if not os.path.exists(os.path.dirname(filename)):
            os.makedirs(os.path.dirname(filename))

        self.log_file = open(filename, "w+")

    def log_info(self, message, message_type="", prefix=None, acquire_lock=True):
        if self.lock and acquire_lock:
            self.lock.acquire()

        msg = "[INFO] "
        msg += "[" + datetime.datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S") + "] "
        if prefix:
            msg += "[" + str(prefix) + "] "
        msg += str(message)
        if msg[-1] != "\n":
            msg += "\n"

        if message_type in self.types_file:
            self.log_file.write(msg)
            self.log_file.flush()

        if message_type in self.types_stdout:
            sys.stdout.write(msg)

        if self.lock and acquire_lock:
            self.lock.release()

    def log_warn(self, message, message_type="", prefix=None, acquire_lock=True):
        if self.lock and acquire_lock:
            self.lock.acquire()

        msg = "[WARN] "
        msg += "[" + datetime.datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S") + "] "
        if prefix:
            msg += "[" + str(prefix) + "] "
        msg += str(message)
        if msg[-1] != "\n":
            msg += "\n"

        if message_type in self.types_file:
            self.log_file.write(msg)
            self.log_file.flush()

        if message_type in self.types_stdout:
            sys.stdout.write(msg)

        if self.lock and acquire_lock:
            self.lock.release()

    def log_error(self, message, message_type="", prefix=None, acquire_lock=True):
        if self.lock and acquire_lock:
            self.lock.acquire()

        msg = "[ERROR] "
        msg += "[" + datetime.datetime.utcfromtimestamp(time.time()).strftime("%Y-%m-%d %H:%M:%S") + "] "
        if prefix:
            msg += "[" + str(prefix) + "] "
        msg += str(message)
        if msg[-1] != "\n":
            msg += "\n"

        if message_type in self.types_file:
            self.log_file.write(msg)
            self.log_file.flush()

        if message_type in self.types_stdout:
            sys.stdout.write(msg)

        if self.lock and acquire_lock:
            self.lock.release()

    def get_filename(self):
        return self.filename

    def close(self):
        self.log_file.close()
