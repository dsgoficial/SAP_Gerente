# -*- coding: utf-8 -*-

def classFactory(iface):
    from .main import Main
    return Main(iface)