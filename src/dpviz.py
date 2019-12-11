# Brian Ward and Algorithms Group 4 (2019)
# Based on https://stackoverflow.com/questions/9186395/python-is-there-a-way-to-get-a-local-function-variable-from-within-a-decorator
# With reference to https://realpython.com/primer-on-python-decorators/

import sys, functools, numpy as np


class dpviz(object):

    # Initialize the dpviz wrapper
    def __init__(self, func, arraylike=True):
        self._tables = []
        self.func = func
        functools.update_wrapper(self, func)
        self.arraylike = arraylike

    ## This replaces any calls to the original function wrapped
    def __call__(self, *args, **kwargs):
        # Reset the stored tables when called again
        self.clear_tables()

        # Define a local function used as a call trace while the function is executing
        def tracer(frame, event, arg):
            # Store any dp_table if it exists
            if ('dp_table' in frame.f_locals):
                # Don't store duplicates of array-like
                if (not self._tables or not self.arraylike or not np.array_equal(frame.f_locals['dp_table'], self._tables[-1])):
                    self._tables.append(frame.f_locals['dp_table'].copy())
            return tracer

        # Set tracer to the active trace
        sys.settrace(tracer)

        try:
            # trace the function call
            res = self.func(*args, **kwargs)
        finally:
            # disable tracer and replace with old one
            sys.settrace(None)

        return res

    # Clear out the table when necessary
    def clear_tables(self):
        self._tables = []

    @property
    def tables(self):
        return self._tables
