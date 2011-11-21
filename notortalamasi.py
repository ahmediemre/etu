#!/usr/bin/python2.7

import sys
import argparse
from urllib2 import urlopen
import BeautifulSoup as BS
import codecs

class Ogrenci:
    def __init__(self, ogrid):
        self.data = self.__parse(ogrid)

    def __parse(self, ogrid):
        url = urlopen("http://kayit.etu.edu.tr/kayit/x01.php?oid=%d" % ogrid)
        soup = BS.BeautifulSoup(url.read())
        dic = {}

        rows = soup.findAll("tr");
        cols = rows[1].findAll("td")
        if rows[1].td.text is rows[2].td.text: #cap veya yandal
            cap = rows[2].findAll("td")
            dic["capbolum"] = cap[3].text
            dic["caport"] = self.__make_float(cap[8].text)

        dic["ogrno"] = cols[0].text
        dic["adi"] = cols[1].text
        dic["soyadi"] = cols[2].text
        dic["bolum"] = cols[3].text
        dic["ort"] = self.__make_float(cols[8].text)
        return dic

    def __make_float(self, data):
        return float(data.replace(u',', u'.'))

    def __repr__(self):
        return u"%s %s: %.2f" % (self.data["adi"], self.data["soyadi"], self.data["ort"])

    def __getitem__(self, key):
        return self.data[key]

    def __cmp__(self, ogr):
        if isinstance(ogr, Ogrenci):
            return cmp(self["ort"], ogr["ort"])
        else:
            raise ValueError #mantiksiz
        

def parse_db(dbfile="db"):
    f = codecs.open(dbfile, "r")
    dbdict = {}
    for line in f:
        data = line.split(";")
        ogrid = int(data[0])
        ogrno = data[1]
        dbdict[ogrno] = ogrid
    f.close()    
    return dbdict

    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ogrenci numaralarina gore ortalama sirali liste getirir.")
    parser.add_argument('inputfile', help='input file: her satirda 1 ogrenci numarasi icermeli')
    args = parser.parse_args(sys.argv[1:])

    db = parse_db()
    liste = []
    f = codecs.open(args.inputfile, "r")

    for line in f:
        liste.append(Ogrenci(db[line.strip()]))
    
    f.close()

    liste.sort(reverse=True)
    for entry in liste:
        print unicode(entry)
