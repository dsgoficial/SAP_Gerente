# -*- coding: utf-8 -*-
from PyQt5 import QtCore
from qgis import gui, core
from platform import system 
import os, requests, sys, re, subprocess, json
from Ferramentas_Gerencia.utils import msgBox

CONFIG = {}

def server_on(server):
    try:
        session = requests.Session()
        session.trust_env = False
        session.get(server, timeout=8)
        return True
    except:
        return False

def POST(host, url, post_data={}, header={}):
    if server_on(host):
        header['content-type'] = 'application/json'
        session = requests.Session()
        session.trust_env = False
        response = session.post(url, data=json.dumps(post_data), headers=header)
        return False if show_erro(response) else response
    show_erro({"_erro" : u"Sem conexão com servidor."})

def GET(host, url, header={}):
    try:
        if server_on(host):
            session = requests.Session()
            session.trust_env = False
            response = session.get(url, headers=header)
            return False if show_erro(response) else response
        show_erro({"_erro" : u"Sem conexão com servidor."})
    except requests.exceptions.ConnectionError:
        show_erro({"_erro" : u"Erro de conexão."})
    except requests.exceptions.InvalidURL:
        show_erro({"_erro" : u"Url inválida."})
            
def show_erro(response):
    html = ""
    if "_erro" in response:
        html = u"<p>{}</p>".format(response['_erro'])
    elif not(response.json()['sucess']):
        html = "<p>{}</p>".format(response.json()['message'])
    if html:
        if "parent" in CONFIG:
            msgBox.show(text=html, title=u"Error", parent=CONFIG['parent'])
        else:
            msgBox.show(text=html, title=u"Error") 
        return True
    return False
