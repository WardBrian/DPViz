# rcviz : a small recursion call graph vizualization decorator
# Copyright (c) Ran Dugal 2014
# Licensed under the GPLv2, which is available at
# http://www.gnu.org/licenses/gpl-2.0.html

# Modified 11/2019 by Brian Ward to use graphviz over pygraphviz and to pipe image instead of render

import inspect
import graphviz as gviz
import logging
import copy
import functools


class callgraph(object):
    '''singleton class that stores global graph data
       draw graph using graphviz
    '''

    _callers = {}  # caller_fn_id : node_data
    _counter = 1  # track call order
    _unwindcounter = 1  # track unwind order
    _frames = []  # keep frame objects reference

    @staticmethod
    def reset():
        callgraph._callers = {}
        callgraph._counter = 1
        callgraph._frames = []
        callgraph._unwindcounter = 1

    @staticmethod
    def get_callers():
        return callgraph._callers

    @staticmethod
    def get_counter():
        return callgraph._counter

    @staticmethod
    def get_unwindcounter():
        return callgraph._unwindcounter

    @staticmethod
    def increment():
        callgraph._counter += 1

    @staticmethod
    def increment_unwind():
        callgraph._unwindcounter += 1

    @staticmethod
    def get_frames():
        return callgraph._frames

    @staticmethod
    def render(ext='png', show_null_returns=True):

        g = gviz.Digraph()
        g.graph_attr['fontname'] = "helvetica"
        g.graph_attr['bgcolor'] = "transparent"
        g.node_attr['fontname'] = "helvetica"
        g.edge_attr['fontname'] = "helvetica"
        g.graph_attr['dpi'] = '100'

        # create nodes
        for frame_id, node in callgraph._callers.items():

            auxstr = ""
            for param, val in node.auxdata.items():
                auxstr += " | %s: %s" % (param, val)

            if not show_null_returns and node.ret is None:
                label = "{ %s(%s) %s }" % (node.fn_name, node.argstr(), auxstr)
            else:
                label = "{ %s(%s) %s | ret: %s }" % (node.fn_name, node.argstr(), auxstr, node.ret)
            g.node(str(frame_id), shape='Mrecord', label=label, fontsize='13', labelfontsize='13')

        # create edges
        for frame_id, node in callgraph._callers.items():
            child_nodes = []
            for child_id, counter, unwind_counter in node.child_methods:
                child_nodes.append(child_id)
                label = f"<{counter} (&#8593; {unwind_counter})>"
                g.edge(str(frame_id), str(child_id), label=label, fontsize='8', labelfontsize='8', fontcolor="#999999")

        return g.pipe(format=ext)


class node_data(object):
    def __init__(self, _args=None, _kwargs=None, _fnname="", _ret=None, _childmethods=[]):
        self.args = _args
        self.kwargs = _kwargs
        self.fn_name = _fnname
        self.ret = _ret
        self.child_methods = _childmethods  # [ (method, gcounter) ]

        self.auxdata = {}  # user assigned track data

    def __str__(self):
        return "%s -> child_methods: %s" % (self.nodestr(), self.child_methods)

    def nodestr(self):
        return "%s = %s(%s)" % (self.ret, self.fn_name, self.argstr())

    def argstr(self):
        s_args = ",".join([str(arg) for arg in self.args])
        s_kwargs = ",".join([(str(k), str(v)) for (k, v) in self.kwargs.items()])
        return "%s%s" % (s_args, s_kwargs)


class rcviz(object):
    ''' decorator to construct the call graph with args and return values as labels '''
    def __init__(self, wrapped):
        self._verbose = False
        self.wrapped = wrapped
        functools.update_wrapper(self, wrapped)

    def track(self, **kwargs):
        call_frame_id = id(inspect.stack()[2][0])
        g_callers = callgraph.get_callers()
        node = g_callers.get(call_frame_id)
        if node:
            node.auxdata.update(copy.deepcopy(kwargs))

    def __call__(self, *args, **kwargs):

        g_callers = callgraph.get_callers()
        g_frames = callgraph.get_frames()

        # find the caller frame, and add self as a child node
        caller_frame_id = None

        fullstack = inspect.stack()

        if (self._verbose):
            logging.debug("full stack: %s" % str(fullstack))

        if len(fullstack) > 2:
            caller_frame_id = id(fullstack[2][0])
            if (self._verbose):
                logging.debug("caller frame: %s %s" % (caller_frame_id, fullstack[2]))

        this_frame_id = id(fullstack[0][0])
        if (self._verbose):
            logging.info("this frame: %s %s" % (this_frame_id, fullstack[0]))

        if this_frame_id not in g_frames:
            g_frames.append(fullstack[0][0])

        if this_frame_id not in g_callers.keys():
            g_callers[this_frame_id] = node_data(args, kwargs, self.wrapped.__name__, None, [])

        edgeinfo = None
        if caller_frame_id:
            edgeinfo = [this_frame_id, callgraph.get_counter()]
            if (caller_frame_id in g_callers):
                g_callers[caller_frame_id].child_methods.append(edgeinfo)
            callgraph.increment()

        # invoke wraped
        ret = self.wrapped(*args, **kwargs)

        if (self._verbose):
            logging.debug('unwinding frame id: %s' % this_frame_id)

        if edgeinfo:
            edgeinfo.append(callgraph.get_unwindcounter())
            callgraph.increment_unwind()

        g_callers[this_frame_id].ret = copy.deepcopy(ret)

        return ret
