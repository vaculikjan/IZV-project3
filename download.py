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
        "p9",
        "p10",
        "p11",
        "p12",
        "p13a",
        "p13b",
        "p13c",
        "p14",
        "p15",
        "p16",
        "p17",
        "p18",
        "p19",
        "p20"
        "p21",
        "p22",
        "p23",
        "p24",
        "p27",
        "p28",
        "p34",
        "p35",
        "p39",
        "p44",
        "p45a",
        "p47",
        "p48a",
        "p49",
        "p50a",
        "p50b",
        "p51",
        "p52",
        "p53",
        "p55a",
        "p57",
        "p58",
        "a",
        "b",
        "c",
        "d",
        "e",
        "f",
        "g",
        "h",
        "i",
        "j",
        "k",
        "l",
        "n",
        "o",
        "p",
        "q",
        "r",
        "s",
        "t",
        "p5a"
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
            for file in os.listdir(self.folder):

                if zf.is_zipfile(self.folder + '/' +file):
                    
                    current_zip = zf.ZipFile(self.folder + '/' +file)
                    with current_zip.open(DataDownloader.region_match[region], 'r') as csvfile:
                        current_csv = csv.reader(io.TextIOWrapper(csvfile, encoding="ISO 8859-2"), delimiter=';')  
                        csv_list = list(current_csv)
                        print(csv_list[0])


download = DataDownloader()
#download.download_data()
download.parse_region_data("PHA")