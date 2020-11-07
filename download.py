from bs4 import BeautifulSoup
from copy import deepcopy
import numpy as np
import zipfile as zf
import os, sys, requests, re, csv, io, pickle, gzip

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

    #dictionary used to store the column types with their description
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
        "p5a" : "Lokalita nehody",
        "p99" : "Region"
    }
    
    def __init__(self,url='https://ehw.fit.vutbr.cz/izv/', folder="data", cache_filename='data_{}.pkl.gz'):
        
        self.url = url
        self.folder = folder
        self.cache_filename = cache_filename
        
        #variables for storing region data
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
        
        #create dir "folder" if it doesn't exist
        if not os.path.exists(folder):
            os.makedirs(folder)
        
    def download_data(self):
        
        #robots don't get access, so we add header
        headers = {'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Safari/605.1.15'}

        #GET website and parse with beautiful soup for download links
        r = requests.get(self.url, headers = headers)
        data = r.text
        soup = BeautifulSoup(data, features='html.parser')
        soup.prettify()
        links = soup.findAll('a', string = "ZIP", )
        last_month = -1
        regex =re.compile(r'(1[0-2]|0[1-9])-')

        #download items - only download latest sets so we don't have redundant data
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
                    
                    #don't download already existing files
                    if not os.path.exists(path):
                        r = requests.get(link, headers = headers)
                        open(path, 'wb').write(r.content)

    def parse_region_data(self,region):
        #self.download_data()

        parsed_data = (list(), list())

        #intialize first list in the tuple and fill it with strings corresponding to column type of csv file
        for value in DataDownloader.column_types.values():
            parsed_data[0].append(value)
        
        #go through the folder
        for file in os.listdir(self.folder):
            
            #if file is zip we open it and look for specific region file based on region id e.g. "PHA"
            if zf.is_zipfile(self.folder + '/' +file):
                
                current_zip = zf.ZipFile(self.folder + '/' +file)
                
                #we open the zip and the corresponding csv file
                with current_zip.open(DataDownloader.region_match[region], 'r') as csvfile:
                    current_csv = csv.reader(io.TextIOWrapper(csvfile, encoding="windows-1250"), delimiter=';')  
                    csv_list = list(current_csv)

                #parsing

                    #if this is the first file we create the array, later we only append to it
                    if len(parsed_data[1]) == 0:

                        self.initialize_nd_list(parsed_data[1], len(csv_list))
                        self.parse_csv(parsed_data[1], csv_list, region)
                    
                    #if this is not a first file, we create temp array and then append to ndarray
                    else:

                        #temp array
                        numpy_parsed = list()

                        #prepare temp array with ndarrays of corresponding types where necessary, elsewhere leave float
                        self.initialize_nd_list(numpy_parsed, len(csv_list))

                        #fill ndarrays with values
                        self.parse_csv(numpy_parsed, csv_list, region)
                        
                        #concat to parent array
                        for i, data in enumerate(numpy_parsed):
                            parsed_data[1][i] = np.append(parsed_data[1][i], data, axis=0) 
                    
        #save region data to memory -- save it to instance variable
        return(parsed_data)

    def get_list(self, regions = None):

        #download data, doesn't download duplicate data
        self.download_data()
        region_list = None
        #return data on all regions
        if regions == None:
            region_list = DataDownloader.region_match
        else:
            if not isinstance(regions, list):
                print("Arg has to be list", file=sys.stderr)
                return
            region_list = regions

        full_data = (list(), list())
        for value in DataDownloader.column_types.values():
            full_data[0].append(value)
        self.initialize_nd_list(full_data[1], 0)

        for region in region_list:
            if region not in DataDownloader.region_match:
                print("Region {} doesn't exist".format(region), file=sys.stderr)
                continue
            region_data = None

            #try to get data from variable
            if getattr(self, region) is not None:
                region_data = getattr(self, region)

            #try to open from file if it fails, start parsing
            else:
                try:
                    region_data = self.load_pickle(region)
                    #print(region_data)
                except:
                    region_data = self.get_region(region)
                    #cache data and save to memory
                    self.save_pickle(region_data, region)
                    setattr(self, region, deepcopy(region_data))

            for i, data in enumerate(region_data[1]):
                full_data[1][i] = np.append(full_data[1][i], data, axis=0)
            
        return full_data

    def get_region(self, region):
        #get single region data
        region_data = None
        if getattr(self, region) == None:
            region_data = self.parse_region_data(region)
        return region_data

    def save_pickle(self, region_data, region):
        with gzip.GzipFile(self.folder + '/' + self.cache_filename.format(region), mode='wb') as f:
            pickle.dump(region_data, f)

    def load_pickle(self, region):
        with gzip.open(self.folder + '/' + self.cache_filename.format(region), mode='rb') as f:
            region_data = pickle.load(f)
            return region_data

    def initialize_nd_list(self, nd_list, len):
        #create list of ndarrays with correct types)
        for key in DataDownloader.column_types:
            if key == "p2a":
                nd_list.append(np.zeros([len], dtype = "datetime64[D]"))
            elif key == "h" or key == "i":
                nd_list.append(np.zeros([len], dtype = "U64"))
            elif key == "k" or key == "t":
                nd_list.append(np.zeros([len], dtype = "U32"))
            elif key == "l" or key == "p99":
                nd_list.append(np.zeros([len], dtype = "U8"))
            elif key == "p" or key == "q":
                nd_list.append(np.zeros([len], dtype = "U16"))
            else:
                nd_list.append(np.zeros([len]))
    
    def parse_csv(self, nd_list, csv_list, region):
        #parse csv file and save values to list of ndarrays
        for i, row in enumerate(csv_list):
            for ((j, cell), ct) in zip(enumerate(row), DataDownloader.column_types):
                if ct == "p2a":
                    nd_list[j][i] = np.datetime64(cell)   
                elif ct == "p47" and cell.upper() =="XX":
                    nd_list[j][i] = -1
                elif ',' in cell and (ct == "a" or ct == "b" or ct == "d" or ct =="e" or ct == "f" or ct =="g" or ct == "o"):
                    nd_list[j][i] = float(cell.replace(',','.',1))
                elif cell == '':
                    nd_list[j][i] = np.nan
                else:
                    try:
                        nd_list[j][i] = cell
                    except:
                        try:
                            nd_list[j][i] = float.fromhex(cell)
                        except:
                            nd_list[j][i] = np.nan
            nd_list[-1][i] = region


if __name__ == "__main__":
    download = DataDownloader()
    dataset = download.get_list(["PHA", "JHM", "KVK"])
    print("Sloupce:")
    for data in dataset[0]:
        print(data, end=', ')
    print("\nPočet záznamů:")
    print( dataset[1][0].size)
    print("\nRegiony:\nPHA, JHM, KVK")
       
