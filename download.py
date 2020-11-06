import os
import requests
import re
from bs4 import BeautifulSoup
import numpy as np
import zipfile as zf
import csv
import io

class DataDownloader:

    #dictionary used to match a Region with a corresponding .csv file 
    region_match = {
        "PHA" : "00.csv",
        "STC" : "01.csv",
        "JHC" : "02.csv",
        "PLK" : "03.csv",
        "ULK" : "04.csv",
        "HKK" : "05.csv",
        "JHM" : "06.csv",
        "MSK" : "07.csv",
        "OLK" : "14.csv",
        "ZLK" : "15.csv",
        "VYS" : "16.csv",
        "PAK" : "17.csv",
        "LBK" : "18.csv",
        "KVK" : "19.csv"
    }

    column_types = {
        "p1" : "Identifikační číslo",
        "p36" : "Druh pozemní komunikace",
        "p37" : "Číslo pozemní komunikace",
        "p2a" : "Den, Měsíc, Rok",
        "weekday(p2a)" : "Den týdne",
        "p2b" : "Čas",
        "p6" : "Druh nehody",
        "p7" : "Druh srážky jedoucích vozidel",
        "p8" : "Druh pevné překážky",
        "p9": "Charakter nehody",
        "p10" : "Zavinění nehody",
        "p11" : "Alkohol u viníka nehody přítomen",
        "p12" : "Hlavní příčiny nehody",
        "p13a" : "Usmrceno osob",
        "p13b" : "Těžce zraněno osob",
        "p13c" : "Lehce zraněno osob",
        "p14" : "Celková hmotná škoda",
        "p15" : "Druh povrchu vozovky",
        "p16" : "Stav povrchu vozovky v době nehody",
        "p17" : "Stav komunikace",
        "p18" : "Povětrnostní podmínky v době nehody",
        "p19" : "Viditelnost",
        "p20" : "Rozhledové poměry",
        "p21" : "Dělení komunikace",
        "p22" : "Situování nehody na komunikaci",
        "p23" : "Řízení provozu v době nehody",
        "p24" : "Místní úprava přednosti v jízdě",
        "p27" : "Specifická místa a objekty v místě nehody",
        "p28" : "Směrové poměry",
        "p34" : "Počet zúčastněných vozidel",
        "p35" : "Místo dopravní nehody",
        "p39" : "Druh křižující komunikace",
        "p44" : "Druh vozidla",
        "p45a" : "Výrobní značka motorového vozidla",
        "p47" : "Rok výroby vozidla",
        "p48a" : "Charakteristika vozidla",
        "p49" : "Smyk",
        "p50a" : "Vozidlo po nehodě",
        "p50b" : "Únik provozních, přepravovaných hmot",
        "p51" : "Způsob vyproštění osob z vozidla",
        "p52" : "Směr jízdy nebo postavení vozidla",
        "p53" : "Škoda na vozidle",
        "p55a" : "Kategorie řidiče",
        "p57" : "Stav řidiče",
        "p58" : "Vnější ovlivnění řidiče",
        "a" : "a",
        "b" : "b",
        "d" : "Souřadnice X",
        "e" : "Souřadnice Y",
        "f" : "f",
        "g" : "g",
        "h" : "h",
        "i" : "i",
        "j" : "j",
        "k" : "k",
        "l" : "l",
        "n" : "n",
        "o" : "o",
        "p" : "p",
        "q" : "q",
        "r" : "r",
        "s" : "s",
        "t" : "t",
        "p5a" : "Lokalita nehody"
    }
    
    #
    def __init__(self,url='https://ehw.fit.vutbr.cz/izv/', folder="data", cache_filename='data_{}.pkl.gz'):
        self.url = url
        self.folder = folder
        
        self.PHA = None
        self.STC = None
        self.JHC = None
        self.PLK = None
        self.KVK = None
        self.ULK = None
        self.LBK = None
        self.HKK = None
        self.PAK = None
        self.OLK = None
        self.MSK = None
        self.JHM = None
        self.ZLK = None
        self.VYS = None        

        if not os.path.exists(folder):
            os.makedirs(folder)
        
    def download_data(self):
        headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}
        r = requests.get(self.url, headers = headers)
        data = r.text
        soup = BeautifulSoup(data, features='html.parser')
        soup.prettify()
        links = soup.findAll('a', string = "ZIP", )
        last_month = -1
        regex =re.compile(r'(1[0-2]|0[1-9])-')

        for item in links:
            name = str(item).split('href=', 1)[1].split('"', 2)[1].split("/", 1)[1]
            path = self.folder + '/' + name
            link = self.url + str(item).split('href=', 1)[1].split('"', 2)[1]
            
            if "2020" in name:
                month = int(name.split('-',1)[1].split('-',1)[0])

                if month > last_month:
                    last_month = month

            else:
                if regex.search(name) is None:

                    if not os.path.exists(path):
                        r = requests.get(link, headers = headers)
                        open(path, 'wb').write(r.content)

        for item in links:
            name = str(item).split('href=', 1)[1].split('"', 2)[1].split("/", 1)[1]

            if "2020" in name:
                month = int(name.split('-',1)[1].split('-',1)[0])

                if month == last_month:

                    if not os.path.exists(path):
                        r = requests.get(link, headers = headers)
                        open(path, 'wb').write(r.content)

    def parse_region_data(self,region):
        #self.download_data()
        
        if getattr(self, region) is None:

            parsed_data = (list(), list())

            for value in DataDownloader.column_types.values():
                parsed_data[0].append(value)
           
            for file in os.listdir(self.folder):

                if zf.is_zipfile(self.folder + '/' +file):
                    
                    current_zip = zf.ZipFile(self.folder + '/' +file)
                    with current_zip.open(DataDownloader.region_match[region], 'r') as csvfile:
                        current_csv = csv.reader(io.TextIOWrapper(csvfile, encoding="windows-1250"), delimiter=';')  
                        csv_list = list(current_csv)
                        print(csv_list[0])
                        if len(parsed_data[1]) == 0:

                            for _ in range(len(parsed_data[0])):
                                parsed_data[1].append(np.zeros([1,len(csv_list)]))
                            
                            for i, row in enumerate(csv_list):
                                for j, cell in enumerate(row):
                                    if cell == '':
                                        parsed_data[1][j][0,i] = np.nan
                                    elif cell.isalpha()
                                    else:
                                        #parsed_data[1][j][0,i] = int(cell)
                                        pass
                                


download = DataDownloader()
#download.download_data()
download.parse_region_data("PHA")