import datetime
import logging
import datetime
import time
import stats

from google.appengine.ext import db
from google.appengine.api import users

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def to_dict(model):
    output = {}
    output['key'] = model.key().name()
    for key, prop in model.properties().iteritems():
        value = getattr(model, key)

        if value is None or isinstance(value, SIMPLE_TYPES):
            output[key] = value
        elif isinstance(value, datetime.date):
            # Convert date/datetime to ms-since-epoch ("new Date()").
            ms = time.mktime(value.utctimetuple()) * 1000
            ms += getattr(value, 'microseconds', 0) / 1000
            output[key] = int(ms)
        elif isinstance(value, db.GeoPt):
            output[key] = { 'lon': value.lon, 'lat': value.lat }
        elif isinstance(value, db.Model):
            output[key] = to_dict(value)
        else:
            raise ValueError('cannot encode ' + repr(prop))
    return output

def pek_parse(raw, aqi):
 p = raw.value.split(';')
 aqi.aqi = int(p[4])
 aqi.pm_2_5 = float(p[3])
 aqi.timestamp = raw.timestamp
 raw.processed = True
 raw.put()

parsers = {'pek': pek_parse}

class City(db.Model):
 name = db.StringProperty(required=True)
 location = db.GeoPtProperty()
 current_aqi = db.IntegerProperty()
 last_week_avg_aqi = db.IntegerProperty()
 last_month_avg_aqi = db.IntegerProperty()
 all_time_avg_aqi = db.IntegerProperty()	
 parser = None
  
 def parse(self, raw, aqi_obj):
  parsers['pek'](raw, aqi_obj)

 def update(self):
  self.last_week_avg_aqi = stats.average(self, 7)
  self.last_month_avg_aqi = stats.average(self, 30)
  self.all_time_avg_aqi = stats.average(self, 0)
  self.put()

class AQIRecord(db.Expando):
 timestamp = db.DateTimeProperty()
 aqi = db.IntegerProperty()

class RawRecord(db.Model):
 timestamp = db.DateTimeProperty()
 value = db.StringProperty()
 processed = db.BooleanProperty()

def city(key):
 return db.get( db.Key.from_path('City', key) )

if(city('pek') == None):
 pek = City(key_name='pek',
              name='Beijing')
 pek.parser = pek_parse
 pek.location = db.GeoPt(lat=39.913889,lon=116.391667)
 pek.put()

if(city('wuh') == None):
 wuh = City(key_name='wuh',
               name='Wuhan')
 wuh.location = db.GeoPt(lat=30.583333,lon=114.283333)
 wuh.put()

if(city('sha') == None):
 sha = City(key_name='sha',
               name='Shanghai')
 sha.location = db.GeoPt(lat=31.2,lon=121.5)
 sha.put()

if(city('tyn') == None):
 tyn = City(key_name='tyn',
               name='Taiyuan')
 tyn.location = db.GeoPt(lat=37.869444,lon=112.560278)
 tyn.put()

if(city('can') == None):
 can = City(key_name='can',
               name='Guangzhou')
 can.location = db.GeoPt(lat=23.128889,lon=113.258889)
 can.put()

if(city('ckg') == None):
 ckg = City(key_name='ckg',
               name='Chongqing')
 ckg.location = db.GeoPt(lat=29.558333,lon=106.566667)
 ckg.put()
# 
# if(city('nrt') == None):
#  nrt = City(key_name='nrt',
#                name='Tokyo')
#  nrt.location = db.GeoPt(lat=35.700556,lon=139.715)
#  nrt.put()
# 
# if(city('hlp') == None):
#  hlp = City(key_name='hlp',
#                name='Jakarta')
#  hlp.location = db.GeoPt(lat=-6.2,lon=106.8)
#  hlp.put()

if(city('bkk') == None):
 bkk = City(key_name='bkk',
               name='Bangkok')
 bkk.location = db.GeoPt(lat=13.752222,lon=100.493889)
 bkk.put()


if(city('sin') == None):
 sin = City(key_name='sin',
                name='Singapore')
 sin.location = db.GeoPt(lat=1.283333,lon=103.833333)
 sin.put()


if(city('kul') == None):
 kul = City(key_name='kul',
              name='Kuala Lumpur')
 kul.location = db.GeoPt(lat=3.1475,lon=101.693333)
 kul.put()

if(city('hkg') == None):
 kul = City(key_name='hkg',
              name='Hong Kong')
 kul.location = db.GeoPt(lat=22.275469,lon=114.143828)
 kul.put()

if(city('bom') == None):
 kul = City(key_name='bom',
              name='Mumbai')
 kul.location = db.GeoPt(lat=18.975,lon=72.825833)
 kul.put()

if(city('cmb') == None):
 kul = City(key_name='cmb',
              name='Colombo')
 kul.location = db.GeoPt(lat=6.934444,lon=79.842778)
 kul.put()

