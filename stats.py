import entities
import datetime

from google.appengine.ext import db

from datetime import datetime as dt
from datetime import timedelta

def all(city):
 return db.Query(entities.AQIRecord).ancestor(city).order('timestamp')

def latest(city):
 return all(city).fetch(1)[0]

def since(city, cutoff):
 return db.GqlQuery(
           'SELECT * FROM AQIRecord WHERE ANCESTOR IS :1 AND timestamp > :2',
           city, cutoff)

def cutoff(days):
 if days == 0:
  return dt.min
 return dt.now() - timedelta(days=days)

def average(city, days):
 records = since( city, cutoff(days) )
 aqi_vals = map( lambda x: x.aqi, records)
 return reduce(lambda x, y: x + y, aqi_vals, 0) / len(aqi_vals)

def all_time(city):
 pass