# -*- coding: utf-8 -*-
import os, sys
from PyQt5 import QtCore, uic, QtWidgets, QtGui
from SAP_Gerente.config import Config
from SAP_Gerente.widgets.mDialogV2 import MDialogV2
from .addFotos import AdicionarFotos
import json
import datetime

class MPhotos(MDialogV2):
    
    def __init__(self, 
                controller,
                qgis,
                sap
            ):
        super(MPhotos, self).__init__(controller=controller)
        self.qgis = qgis
        self.sap = sap
        self.adicionarFotosDlg = None
        self.tableWidget.setColumnHidden(6, True)
        self.fetchData()

    def getUiPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            '..',
            'uis',
            'mPhotos.ui'
        )
    
    def getColumnsIndexToSearch(self):
        return [2, 3, 4]

    def fetchData(self):
        data = self.sap.getFotos()
        self.addRows(data)

    def addRows(self, fotos):
        self.clearAllItems()
        for foto in fotos:
            self.addRow(
                foto['id'],
                foto['descricao'],
                self.formatarDataHora(foto.get('data_imagem')),
                foto.get('campo_nome', 'N/A'),
                foto.get('data_criacao', ''),
                json.dumps(foto)
            )
        self.adjustTable()

    def formatarDataHora(self, data_str):
        """Formata a data/hora para exibição"""
        if not data_str:
            return "N/A"
        
        try:
            # Tenta converter para o formato desejado
            data = datetime.datetime.strptime(data_str, '%Y-%m-%d %H:%M:%S')
            return data.strftime('%d/%m/%Y %H:%M')
        except:
            # Se não conseguir converter, retorna o valor original
            return data_str

    def addRow(self, 
            primaryKey, 
            descricao,
            data_imagem,
            campo_nome,
            data_criacao,
            dump
        ):
        idx = self.getRowIndex(primaryKey)
        if idx < 0:
            idx = self.tableWidget.rowCount()
            self.tableWidget.insertRow(idx)
        self.tableWidget.setItem(idx, 0, self.createNotEditableItemNumber(primaryKey))
        self.tableWidget.setCellWidget(idx, 2, self.createLabelV2(descricao, idx, 2))
        self.tableWidget.setItem(idx, 3, self.createNotEditableItem(data_imagem))
        self.tableWidget.setItem(idx, 4, self.createNotEditableItem(campo_nome))
        self.tableWidget.setItem(idx, 5, self.createNotEditableItem(data_criacao))
        self.tableWidget.setItem(idx, 6, self.createNotEditableItem(dump))
        optionColumn = 1
        self.tableWidget.setCellWidget(
            idx, 
            optionColumn, 
            self.createRowEditWidget(
                self.tableWidget,
                idx,
                optionColumn, 
                self.handleViewBtn, 
                self.handleDeleteBtn
            )
        )

    def handleViewBtn(self, index):
        """
        Manipula o clique no botão de visualização de uma foto.
        Apenas mostra informações básicas da foto.
        
        Args:
            index: Índice da linha na tabela
        """
        # Obtém os dados completos da foto
        foto_data = self.getRowData(index.row())
        
        # Mostra informações básicas sobre a foto
        info = f"ID: {foto_data.get('id', 'N/A')}\n"
        info += f"Descrição: {foto_data.get('descricao', 'N/A')}\n"
        info += f"Data: {foto_data.get('data_imagem', 'N/A')}\n"
        info += f"Campo: {foto_data.get('campo_nome', 'N/A')}"
        
        self.showInfo('Informações da Foto', info)
    

        
    def handleDeleteBtn(self, index):
        result = self.showQuestion('Atenção', 'Tem certeza que deseja excluir a foto?')
        if not result:
            return
        data = self.getRowData(index.row())
        message = self.sap.deletaFoto(data['id'])
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
        # Abre a janela existente AdicionarFotos
        self.adicionarFotosDlg = AdicionarFotos(self.controller, self.sap)
        # Você pode adicionar um evento para atualizar a tabela após adicionar fotos
        self.adicionarFotosDlg.finished.connect(self.fetchData)
        self.adicionarFotosDlg.show()
        
    @QtCore.pyqtSlot(bool)
    def on_refreshBtn_clicked(self):
        """Atualiza os dados da tabela"""
        self.fetchData()
        
    @QtCore.pyqtSlot()
    def on_tableWidget_itemSelectionChanged(self):
        """Quando uma linha é selecionada, não faz nada especial"""
        pass