import scrapy
import json
from string import ascii_lowercase
import pandas as pd

df = pd.read_csv("input.csv")

completeList = []
for row in df.values.tolist():
    for a in ascii_lowercase[0:25]:
        for b in ascii_lowercase:
            for c in ascii_lowercase:
                completeList.append(f'https://services.naic.org/api/licenseLookup/search?jurisdiction={row[0]}&searchType=Licensee&entityType=IND&licenseType=PRO&lastName={a}{b}{c}&residentLicense=Yes&licenseStatus=A&businessCity={row[1]}&businessState={row[0]}')
    
class DetailsSpider(scrapy.Spider):
    name = 'details'
    # allowed_domains = ['https://services.naic.org/api/licenseLookup/search?jurisdiction=TN&searchType=Licensee&entityType=IND&licenseType=PRO&lastName=a&residentLicense=Yes&licenseStatus=A&loaType=4']
    start_urls = completeList

    def parse(self, response):
        data = json.loads(response.text)
        for d in data:
            lnum = d['licenseNumber']
            npn = d['npn']
            name = d['name']
            ltype = d['licenseType']
            leffec = d['licenseEffectiveDate']
            lexpiry = d['licenseExpirationDate']
            isresidence = d['residency']
            address = d['businessAddress']
            businessPhone = d['businessPhone']
            
            datadic = {'License Number':lnum,'NPN':npn,'Name':name,'License Type':ltype,'License Effective Date':leffec,'License Expiration Date':lexpiry,'Residency':isresidence,'Address':address,'Business Phone':businessPhone}
            yield scrapy.Request("https://services.naic.org/api/licenseeLookup/summary/licenseTypes/TN/{}".format(lnum),meta={'datadic':datadic},callback=self.next,dont_filter=True)
            
            
            
    def next(self,response):
        datadic = response.meta.get("datadic")
        lid = json.loads(response.text)[0]['licenseId']
        yield scrapy.Request("https://services.naic.org/api/licenseeLookup/summary/lookupPhoneEmailWebsite/{}".format(lid),meta={'datadic':datadic},callback=self.next2,dont_filter=True)


    def next2(self,response):
        datadic = response.meta.get("datadic")
        try:
            email = json.loads(response.text)['emails'][0]['emailAddress']
        except:
            email = ""
        for f in json.loads(response.text)['phones']:
            print(f)
            try:
                if f['Mailing Primary Phone']:
                    mailPhone = f['phoneNumber']
            except:
                mailPhone = ""
                continue
        datadic.update({'Email':email,'Mailing Phone':mailPhone})
        yield datadic
