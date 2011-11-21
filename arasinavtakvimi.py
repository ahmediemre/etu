#!/usr/bin/env python2

# requires icalender
import sys
from icalendar import Calendar, Event, UTC 
from datetime import datetime
import argparse # python >= 2.7
from etu import kayitli_dersler, arasinav

def _get_dt(tarih, saat):
    "Sinav tarihini ve saatini datetime fonksiyonuna gore parse eder"
    gun = int(tarih[:2])
    ay = int(tarih[3:5])
    yil = int(tarih[6:])

    saat_dt = int(saat[:2])
    dakika = int(saat[3:])

    return datetime(yil, ay, gun, saat_dt, dakika, tzinfo=UTC)


# Komut satiri argumanlari
parser = argparse.ArgumentParser(description="Ogrencinin ara sinav programini iCalendar formatinda kaydeder.")
parser.add_argument('st', help='Ogrenci numarasi')
parser.add_argument('-o', '--output-file', help='kaydedilecek dosya adi (default: stdout)')
#Argumanlari al ve parse et
args = parser.parse_args(sys.argv[1:])
ogr_no = args.st
output_file = args.output_file
if not output_file:
    f = sys.stdout #default: stdout
else:
    f = open(output_file, 'wb')

ogr_kayitli_dersler = kayitli_dersler(ogr_no) #ogrencinin kayitli dersleri
filtre_fonk = (lambda data: (data['kod'], data['sube']) in ogr_kayitli_dersler ) # sadece ogrencinin kayitli oldugu dersleri almak icin gerekli filtre fonksiyonu
ogr_sinav_takvimi = arasinav(filtre_fonk) #ogrencinin kayitli oldugu derslerin programi

takvim = Calendar() #takvim olustur
takvim.add('proid', '-//TOBB ETU Arasinav Takvimi//%s//' % ogr_no)
takvim.add('version', '2.0')

for sinav in ogr_sinav_takvimi:
    event = Event()
    event.add('summary', sinav['kod'])
    event.add('description', sinav['ad'])
    event.add('uid', '%s[%d]@st%s' % (sinav['kod'], sinav['sube'], ogr_no))
    
    if not sinav['saat'] == (u'00:00', u'00:00'): #saati belli olan sinavlar
        event.add('dtstart', _get_dt(sinav['tarih'], sinav['saat'][0]))
        event.add('dtend', _get_dt(sinav['tarih'], sinav['saat'][1]))
    else: #kendi saatinde olan sinavlar
        pass #tum gunluk event eklenecek
        
    takvim.add_component(event)

f.write(takvim.as_string())
f.close()

# TODO: python2 olayini kesinlestir. gerekli kutuphaneleri dahil et.
# TODO: filtre sorununu coz
