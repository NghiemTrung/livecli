import pkgutil
import unittest

import imp
from livecli import Livecli

import livecli.plugins
import os.path


class PluginTestMeta(type):
    def __new__(mcs, name, bases, dict):
        plugin_path = os.path.dirname(livecli.plugins.__file__)
        plugins = []
        for loader, pname, ispkg in pkgutil.iter_modules([plugin_path]):
            file, pathname, desc = imp.find_module(pname, [plugin_path])
            module = imp.load_module(pname, file, pathname, desc)
            if hasattr(module, "__plugin__"):
                plugins.append((pname, file, pathname, desc))

        session = Livecli()

        def gentest(pname, file, pathname, desc):
            def load_plugin_test(self):
                session.load_plugin(pname, file, pathname, desc)

            return load_plugin_test

        for pname, file, pathname, desc in plugins:
            dict['test_{0}_load'.format(pname)] = gentest(pname, file, pathname, desc)

        return type.__new__(mcs, name, bases, dict)


class TestPlugins(unittest.TestCase):
    """
    Test that an instance of each plugin can be created.
    """
    __metaclass__ = PluginTestMeta
