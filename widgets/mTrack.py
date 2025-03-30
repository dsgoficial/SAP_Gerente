# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addTrack import AdicionarTrack
import json
import datetime

class MTrack(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap
            ):
        super(MTrack, self).__init__(controller=controller)
        self.qgis = qgis
        self.sap = sap
        self.adicionarTrackDlg = None
        self.tableWidget.setColumnHidden(0, True)
        self.tableWidget.setColumnHidden(6, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mTrack.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2, 3, 4, 5]

    def fetchData(self):
        data = self.sap.getTracks()
        self.addRows(data)

    def addRows(self, tracks):
        self.clearAllItems()
        for track in tracks:
            self.addRow(
                track['id'],
                track['chefe_vtr'],
                self.formatarDataHora(track.get('dia')),
                track.get('nome_campo', 'N/A'),
                track['placa_vtr'],
                json.dumps(track)
            )
        self.adjustTable()

    def formatarData(self, data_str):
        """Formata a data para exibição"""
        if not data_str:
            return "N/A"
        
        try:
            # Tenta converter para o formato desejado
            data = datetime.datetime.strptime(data_str, '%Y-%m-%d')
            return data.strftime('%d/%m/%Y')
        except:
            # Se não conseguir converter, retorna o valor original
            return data_str

    def addRow(self, 
            primaryKey, 
            chefe_vtr,
            dia,
            campo_nome,
            placa_vtr,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(chefe_vtr, idx, 2))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(dia))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(campo_nome))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(placa_vtr))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(dump))
        optionColumn = 1
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx,
                optionColumn, 
                self.handleEditBtn,  # Alterado de handleViewBtn para handleEditBtn 
                self.handleDeleteBtn
            )
        )

    def handleEditBtn(self, index):
        """
        Manipula o clique no botão de edição de um tracker.
        Abre o formulário de adicionar tracker preenchido com os dados do tracker selecionado.
        
        Args:
            index: Índice da linha na tabela
        """
        # Obtém os dados completos do tracker
        track_data = self.getRowData(index.row())
        
        # Abre o formulário de edição com os dados preenchidos
        self.adicionarTrackDlg = AdicionarTrack(self.controller, self.sap, self.qgis, track_data)
        self.adicionarTrackDlg.finished.connect(self.fetchData)
        self.adicionarTrackDlg.show()
        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir o tracker?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deletaTracker(data['id'])
        message and self.showInfo('Aviso', message)
        self.fetchData()

    def getRowIndex(self, primaryKey):
        for idx in range(self.tableWidget.rowCount()):
            if not (
                    primaryKey == self.tableWidget.model().index(idx, 0).data()
                ):
                continue
            return idx
        return -1

    def getRowData(self, rowIndex):
        data = json.loads(self.tableWidget.model().index(rowIndex, 6).data())
        return data

    @QtCore.pyqtSlot(bool)
    def on_addFormBtn_clicked(self):
        # Abre a janela AdicionarTrack
        self.adicionarTrackDlg = AdicionarTrack(self.controller, self.sap, self.qgis)
        # Você pode adicionar um evento para atualizar a tabela após adicionar um tracker
        self.adicionarTrackDlg.finished.connect(self.fetchData)
        self.adicionarTrackDlg.show()
        
    @QtCore.pyqtSlot(bool)
    def on_refreshBtn_clicked(self):
        """Atualiza os dados da tabela"""
        self.fetchData()

    def formatarDataHora(self, data_str):
        """Formata a data/hora para exibição"""
        if not data_str:
            return "N/A"
        
        try:
            # Tenta converter para o formato de exibição
            data_str = data_str.replace('Z', '')
            data = datetime.datetime.fromisoformat(data_str)
            data.strftime("%Y-%m-%d %H:%M")
            return data.strftime("%Y-%m-%d")
        except:
            # Se falhar, usa o valor original
            return data_str