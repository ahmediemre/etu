"""TOBB Ekonomi ve Teknoloji Universitesi veritabanindaki
herkese acik bilgilere erisim saglayan python modulu

Bu erisimi saglarken oim.etu.edu.tr altindaki sayfalari
okur ve gerekli bilgileri toplar."""

# Yapilacaklar Listesi
# --------------------
# + Acik dersler OK
# + Ogrencinin aldigi dersler OK
# + Ogrencinin ara sinav programi OK
# + Ogrenci no - sifre kontrolu
# + Secili dersin subelerinin listesi OK
# + Secili dersin (veya belli bir subesinin) ders programi
# + Secili dersi alanlarin listesi

from urllib2 import urlopen, Request #urllib2 >= 2.7
from urllib import urlencode
from BeautifulSoup import BeautifulSoup 

# sonradan ogrencinin aldigi derslere gore filtre eklenebilir
def arasinav(filter_func=(lambda data: True)):
    """Arasinavlari dict listi olarak doner
    Opsiyonel olarak filtreleme yapmasi icin bir fonksiyon alir."""
    url = urlopen("http://oim.etu.edu.tr/tr/content/ara-sinav-programi")
    soup = BeautifulSoup(url.read())

    examlist = []
    table = soup.find("table")
    rows = table.findAll("tr")
    for tr in rows[1:]:
        cols = tr.findAll("td")
        row = {}

        row["kod"] = unicode(cols[0].text)
        row["ad"] = unicode(cols[1].text)
        row["sube"] = int(cols[2].text)
        row["derslik"] = unicode(cols[4].text)
        row["tarih"] = unicode(cols[5].text)
        row["saat"] = _parse_saat(cols[7].text)
        
        if filter_func(row):
            examlist.append(row)

    return examlist

        
def acik_dersler():
    "Icinde bulunulan donem acilmis dersler dict[ders_kodu] = (ad, value) seklinde dictionary'si"
    url = urlopen("http://kayit.etu.edu.tr/Ders/_Ders_prg_start.php")
    soup = BeautifulSoup(url.read())

    parser_kod = lambda string: string[:8].rstrip()
    parser_ad = lambda string: string[8:].strip()

    classdict = {}
    select = soup.find("select") #name = dd_ders
    options = select.findAll("option")
    for opt in options:
        classdict[parser_kod(opt.text)] = (parser_ad(opt.text), opt.get("value"))

    return classdict

    
def kayitli_dersler(student_id):
    "Ogrencinin o donem kayitli oldugu derslerin(ders_kodu, sube) ikilisi olarak seti"
    form = { 'ogrencino': student_id, 'btn_ogrenci': True }
    soup = BeautifulSoup(_post("http://kayit.etu.edu.tr/Ders/Ders_prg.php", form))

    classset = set()
    table = soup.find("table")
    rows = table.findAll("tr")
    for tr in rows[1:]:
        cols = tr.findAll("td")
        for td in cols:
            if td.text != u'-':
                classset.add(_parse_derskodu(td.text))

    if not classset:
        raise ValueError # TODO aciklama: ogrenci no bulunamadi

    return classset

    
def ders_sube_prog(ders_kodu, sube=0):
    "Secili ders/subenin programini doner."
    pass


# zaman iyilestirmesi yapilabilir
def ders_sube_list(ders_kodu):
    "Secili dersin (sube_no, hoca) ikilisi listesini doner"
    ders = acik_dersler()[ders_kodu] #ders = (ad, value)
    form = { 'dd_ders': ders[1], 'sube': 0, 'btn_ders': True} 
    soup = BeautifulSoup(_post("http://kayit.etu.edu.tr/Ders/Ders_prg.php", form))

    sectionlist = []
    tables = soup.findAll("table")
    for t in tables:
        sectionlist.append(_parse_sube(t.tr.th.text))

    return sectionlist

    
def sifre_kontrol(student_id, password):
    form = { "login_username": "st%s" % student_id, "secretkey": password, "js_autodetect_results": 1, "just_logged_in": 1 }
    soup = BeautifulSoup(_post("https://mail.etu.edu.tr/sq/src/redirect.php", form))
    print soup


    
# Module ici fonksiyonlar
def _parse_saat(saat):
    """arasinav fonksiyonuna yardimci fonk.
    Verilen saati (baslangic, bitis) seklinde doner.
    Eger sinav kendi saatinde ise ('00:00', '00:00') doner."""
    if saat == "Ders Saati":
        return (u'00:00', u'00:00')
    else:
        return (saat[0:5], saat[6:11])

def _parse_derskodu(string):
    """kayitli_dersler fonksiyonuna yardimci fonk
    Aldigi girdiyi parcalayarak (ders_kodu, ders,n_subesi) seklinde tuple doner."""
    kod = unicode(string[:8].rstrip())
    sube = int(string[string.index("- ") + 2:string.index("Derslik")])
    return (kod, sube)

def _parse_sube(string):
    """ders_sube_list fonksiyonuna yardimci fonk
    Aldigi girdiyi parcalayarak (sube, hoca) seklinde tuple doner."""
    sube = int(string[5:string.index(' ')])
    hoca = string[string.index(' '):].strip()
    return (sube, hoca)

def _post(url, args):
    #headers = { 'User-Agent': 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)' }
    request = Request(url, urlencode(args))
    response = urlopen(request)
    return response.read()
