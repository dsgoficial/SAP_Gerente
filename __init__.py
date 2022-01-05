# -*- coding: utf-8 -*-
from .main import Main

def classFactory(iface):
    return Main(iface)