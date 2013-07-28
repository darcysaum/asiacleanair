import os
import entities
import logging
import stats
import net

from google.appengine.api import taskqueue
from google.appengine.ext import webapp
from google.appengine.ext.webapp import util
from google.appengine.ext.webapp import template
from google.appengine.ext import db

from django.utils import simplejson

class MainHandler(webapp.RequestHandler):
 def get(self):
  tpath = os.path.join(os.path.dirname(__file__), 'templates/index.html')
  self.response.out.write(template.render(tpath, ()))

class AQIWorker(webapp.RequestHandler):
 def post(self):
  k = self.request.get['k']
  raw = db.get(k)
  city = raw.parent()
  aqi_rec = entities.AQIRecord(parent=city)
  city.parse(raw, aqi_rec)
  aqi_rec.put()

class ChinaAQIWorker(webapp.RequestHandler):
 def get(self):
  net.China().load()

class ThailandAQIWorker(webapp.RequestHandler):
 def get(self):
  net.Thailand().load()

class MalaysiaAQIWorker(webapp.RequestHandler):
 def get(self):
  net.Malaysia().load()

class HongKongAQIWorker(webapp.RequestHandler):
 def get(self):
  net.HongKong().load()

class SingaporeAQIWorker(webapp.RequestHandler):
 def get(self):
  net.Singapore().load()

class StatsWorker(webapp.RequestHandler):
 def get(self):
  city_code = self.request.params['city']
  city = entities.city(city_code)
  for_days = self.request.params['days']
  avg = stats.average(city_code, data)

  stats.calc(data_type)(city)

class ListCitiesHandler(webapp.RequestHandler):
 def get(self):
  cities = entities.City.all()
  self.response.headers.add_header("content-type", 'application/json')
  self.response.out.write(simplejson.dumps([entities.to_dict(c) for c in cities]))

class CityDetailsHandler(webapp.RequestHandler):
 def get(self):
  k = self.request.params['k']
  city = entities.city(k)
  self.response.headers.add_header("content-type", 'application/json')
  self.response.out.write(simplejson.dumps(entities.to_dict(city)))

class CityHandler(webapp.RequestHandler):
 def get(self):
  k = self.request.params['k']
  city = entities.city(k)
  tpath = os.path.join(os.path.dirname(__file__), 'templates/city.html')
  self.response.out.write(template.render(tpath, 
                                   {'city':city, 
                                   'city_page': 'cities/' + city.key().name() + ".html", 
                                   'cities' : entities.City.all()}))

class AQIDataHandler(webapp.RequestHandler):
 def get(self):
  k = self.request.params['k']
  city = entities.city(k)
  self.response.headers.add_header("content-type", 'application/json')
  self.response.out.write(simplejson.dumps([entities.to_dict(r) for r in stats.all(city)]))

class FAQHandler(webapp.RequestHandler):
 def get(self):
  tpath = os.path.join(os.path.dirname(__file__), 'templates/faq.html')
  self.response.out.write(template.render(tpath, {'cities' : entities.City.all()}))

def main():
 application = webapp.WSGIApplication(
            [('/', MainHandler),
             ('/aqi/record/create', AQIWorker),
             ('/aqi/stats/update', AQIWorker),
             ('/aqi/cities/list', ListCitiesHandler),
             ('/aqi/cities/show', CityDetailsHandler),
             ('/aqi/data', AQIDataHandler),
             ('/tasks/aqi/china', ChinaAQIWorker),
             ('/tasks/aqi/thailand', ThailandAQIWorker),
             ('/tasks/aqi/singapore', SingaporeAQIWorker),
             ('/tasks/aqi/malaysia', MalaysiaAQIWorker),
             ('/tasks/aqi/hongkong', HongKongAQIWorker),
             ('/city/*', CityHandler),
             ('/faq*', FAQHandler)
            ], debug=True)
 util.run_wsgi_app(application)
 
if __name__ == '__main__':
 main()

def populate():
 for r in entities.RawRecord.all():
  taskqueue.add(url='/aqi/record/create', params={'k': r.key()})
