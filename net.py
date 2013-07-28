#-*- coding: utf-8 -*-
import entities

import httplib
import logging
import re
from datetime import datetime

from google.appengine.ext import db
from google.appengine.api import urlfetch

from xml.dom.minidom import parseString
from BeautifulSoup import BeautifulSoup

def getText(nodelist):
    rc = []
    for node in nodelist:
        if node.nodeType == node.TEXT_NODE:
            rc.append(node.data)
    return u''.join(rc)

def process_records():
 """"""

class HongKong:
 host='www.epd-asg.gov.hk'
 path='/eindex.html'

 def load(self):
  conn = httplib.HTTPConnection(self.host, timeout=20)
  conn.request("GET", self.path)
  html = conn.getresponse().read()
  soup = BeautifulSoup(html)
  logging.info(html)
  row = soup.find('td', text="Central/Western").findParent('tr')
  logging.info(row)
  cells = row.findAll('td')
  aqi = int(cells[1].find('font').contents[0])
  city = entities.city('hkg')
  city.current_aqi = aqi
  aqi_record = entities.AQIRecord(parent=city) 
  aqi_record.aqi = aqi
  aqi_record.timestamp = datetime.now()
  aqi_record.put()
  city.update()

class Malaysia:
 url='http://www.doe.gov.my/apims/index.php'

 def handle_result(self, rpc):
  result = rpc.get_result()
  logging.info('malaysia[ response: + ' + str(result.status_code) + ' ]')
  html = result.content
  soup = BeautifulSoup(html)
  row = soup.find('td', text="Cheras,Kuala Lumpur").findParent('tr')
  cells = row.findAll('td');
  raw_cell = cells[2].contents[0]
  p = re.compile('[^0-9]')
  aqi = int(p.sub('', raw_cell))
  city = entities.city('kul')
  aqi_record = entities.AQIRecord(parent=city) 
  aqi_record.aqi = aqi
  aqi_record.timestamp = datetime.now()
  aqi_record.put()
  city.update()
 
 def create_callback(self, rpc):
  return lambda: self.handle_result(rpc)

 def load(self):
  rpc = urlfetch.create_rpc(deadline=10)
  rpc.callback = self.create_callback(rpc)
  urlfetch.make_fetch_call(rpc, self.url)
  rpc.wait()

class Singapore:
 host='app2.nea.gov.sg'
 path='/psi.aspx'

 def load(self):
  conn = httplib.HTTPConnection(self.host)
  conn.request("GET", self.path)
  html = conn.getresponse().read()
  soup = BeautifulSoup(html)
  row = soup.find('td', text="Overall Singapore*").findParent('tr')
  cells = row.findAll('td');
  aqi = int(cells[len(cells) - 3].contents[0])
  city = entities.city('sin')
  aqi_record = entities.AQIRecord(parent=city) 
  aqi_record.aqi = aqi
  aqi_record.timestamp = datetime.now()
  aqi_record.put()
  city.update()

def extract_aqi(self, results, city_name):
  """"""
class Thailand:
 host='www.pcd.go.th/'
 path='/AirQuality/Bangkok/Default.cfm'
 cities = ['Bang Khunthien', 'Din Daeng', 'Huai Khwang', 'Intrapituk', 'Klong Chan', 'Lad Phrao', 'Thai Meteorological Department(Bangna)']

 def load(self):
  conn = httplib.HTTPConnection(self.host)
  conn.request("GET", self.path)
  html = conn.getresponse().read()
  soup = BeautifulSoup(html)
  avg = reduce(lambda x, y: x + y, 
        [self.extract_aqi(soup, n) for n in self.cities], 0.0) / len(self.cities)
  city = entities.city('bkk')
  aqi_record = entities.AQIRecord(parent=city) 
  aqi_record.aqi = int(avg)
  aqi_record.timestamp = datetime.now()
  aqi_record.put()
  city.update()

 def extract_aqi(self, results, city_name):
  logging.info(city_name)
  row = results.find('td', text=city_name).findParent('tr')
  cells = row.findAll("td")
  result  =  float(cells[len(cells) - 1].contents[0])
  return result

class China:
 host='www.mep.gov.cn'
 path='/images/ImageForTRS/dataSourceXML/air_data.xml'
 cities = {u'北京': 'pek', u'上海': 'sha', u'广州': 'can', u'重庆': 'ckg', u'太原': 'tyn', u'武汉': 'wuh'}

 def latest(self):
  """"""

 def load(self):
  ts = datetime.now()
  conn = httplib.HTTPConnection('www.mep.gov.cn')
  conn.request("GET", '/images/ImageForTRS/dataSourceXML/air_data.xml')
  xml_response = conn.getresponse().read()
  dom_o = parseString(xml_response)

  root = dom_o.getElementsByTagName('root')[0]
  data = root.getElementsByTagName('data')

  for r in data:
   zh_name = r.getElementsByTagName('city')[0].childNodes[0].data
   logging.info(zh_name.encode('utf-8'))
   if zh_name in self.cities:
    city_code = self.cities[zh_name]
    city = entities.city(city_code)
    aqi_record = entities.AQIRecord(parent=city)
    aqi_value = int(r.getElementsByTagName('api')[0].childNodes[0].data)
    aqi_record.aqi = aqi_value
    aqi_record.timestamp = ts
    aqi_record.put()
    city.update()

 def date(self,data):
  return datetime.datetime.strptime(data['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

 def callback(self, city, ts, v):
  rec = entities.RawRecord(parent = city)
  rec.timestamp = ts
  rec.value = v
  rec.put()