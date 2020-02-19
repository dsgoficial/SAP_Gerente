import os
import csv
from shutil import copyfile

class Rules:

    def getTemplateCsvPath(self):
        return os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            'templates',
            'csvRules.csv'
        )
        
    def getRulesFromCsv(self, srcPath):
        newRules = {}
        with open(srcPath, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                if not( row['GRUPO_DE_REGRA'] in newRules ):
                    newRules[row['GRUPO_DE_REGRA']] = {
                        'cor_rgb' : row['COR_RGB'],
                        'regras' : []
                    }
                newRules[row['GRUPO_DE_REGRA']]['regras'].append({
                    'schema': row['SCHEMA'],
                    'camada': row['CAMADA'],
                    'atributo': row['ATRIBUTO'],
                    'regra': row['REGRA'],
                    'descricao': row['DESCRICAO'],
                })
        return newRules

    def saveTemplateCsv(self, destPath):
        copyfile(self.getTemplateCsvPath(), destPath)