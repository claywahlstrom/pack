
"""
Utilities for Python

TODO (Pollen): allow multiple zipcodes for the given sources
                 - retrieve each api link
                 - use zip codes to lookup the dictionary of url sources

"""
import datetime as _dt
import inspect as _inspect
import json as _json
import math as _math
import time as _time

from bs4 import BeautifulSoup as _BeautifulSoup
import requests as _requests

from clay.web import WEB_HDR as _WEB_HDR

def human_hex(dec):
    """Converts decimal values to human readable hex.
       Mainly used in engineering class"""
    return hex(dec)[2:]

def map_args(function, iterable, *args, **kwargs):
    """Maps iterable to a function with arguments/keywords.
       Dynamic types can be used"""
    return type(iterable)(function(x, *args, **kwargs) for x in iterable)

def map_args_test(x, y=2, z=3):
    """A test function for the map_args function. Returns the sum of x, y, z"""
    return x + y + z

class ObjectInitializer(object):
    """Class ObjectInitializer can be used to initialize properties
       using a list, tuple, or dictionary"""
    def __init__(self, *initial_data, **kwargs):
        for param in initial_data:
            if type(param) == dict:
                for key in param:
                    setattr(self, key, param[key])
            elif type(param) in (list, tuple):
                for item in param:
                    setattr(self, item, item)
            else:
                setattr(self, param, param)
        for key in kwargs:
            setattr(self, key, kwargs[key])

    def get_attributes(self):
        attrs = _inspect.getmembers(self, lambda a:not(_inspect.isroutine(a)))
        return [a[0] for a in attrs if a[0].count('__') < 2]

    def to_dict(self):
        result = {} # dict
        for attr in self.get_attributes():
            result[attr] = getattr(self, attr)
        return result

class Pollen(object):

    """Class Pollen can be used to retrieve and store information about
       the pollen forecast from The Weather Channel (tm) and Wunderground (tm)"""

    MAX_REQUESTS = 4
    SOURCE_SPAN = {'weather text': 7, 'weather values': 7, 'wu poll': 4}
    SOURCE_URLS = {98105: {'weather text': 'https://weather.com/forecast/allergy/l/',
                           'weather values': 'https://api.weather.com/v2/indices/pollen/daypart/7day?apiKey=6532d6454b8aa370768e63d6ba5a832e&geocode=47.654003%2C-122.309166&format=json&language=en-US',
                           'wu poll': 'https://www.wunderground.com/health/us/wa/seattle/KWASEATT446?cm_ven=localwx_modpollen'},
                   98684: {'weather text': 'https://weather.com/forecast/allergy/l/',
                           'weather values': 'https://api.weather.com/v2/indices/pollen/daypart/7day?apiKey=6532d6454b8aa370768e63d6ba5a832e&geocode=45.639816%2C-122.497902&format=json&language=en-US',
                           'wu poll': 'https://www.wunderground.com/health/us/wa/camas/KWACAMAS42?cm_ven=localwx_modpollen'}}
    TYPES = ('grass', 'ragweed', 'tree')
    WEATHER_QUERY_PARAMS = ':4:US'

    def __init__(self, source, zipcode=98105, print_sources=True):
        """Constructs a new Pollen object using the given source and zipcode"""
        if not(zipcode in Pollen.SOURCE_URLS.keys()):
            raise ZipCodeNotFoundException(zipcode)
        self.zipcode = zipcode
        self.print_sources = print_sources
        self.source = source
        self.set_source(source)
        self.set_zipcode(zipcode)
        self.__has_built = False
        self.build()
        
    def __repr__(self):
        """Returns the string representation of this Pollen instance"""
        return f'Pollen(source={{{self.source}}}, zipcode={self.zipcode}, print_sources={self.print_sources})'

    def __check_built(self):
        """Throws a RuntimeError if this Pollen instance has not been built"""
        if not(self.__has_built):
            raise RuntimeError('Pollen must be build after zipcode or source has been changed')

    def __get_markup(self, uri):
        """Retrieves the markup with up to 4 max tries"""
        if self.source == 'weather text':
            params = _WEB_HDR
        else:
            params = dict()
        req = _requests.get(uri, params=params)
        retried = False
        tries = 1
        if req.status_code != 200:
            print('Retrying Pollen request', end='')
        while req.status_code != 200 and tries <= Pollen.MAX_REQUESTS:
            print('.', end='')
            _time.sleep(1.0)
            req = _requests.get(uri, params=params)
            tries += 1
        if tries > 1:
            print()
        return req.content

    def build(self, add_weather_query=True):
        """Builds and populates the pollen record database"""
        uri = self.uri
        if self.source == 'weather text' and add_weather_query:
            uri += self.WEATHER_QUERY_PARAMS
        markup = self.__get_markup(uri)

        page = _BeautifulSoup(markup, 'html.parser')

        if self.source == 'weather text':
            found = page.select('button > div')
            db = dict()
            if len(found) > 0:
                for elm in found:
                    divs = elm.select('div')
                    db[divs[0].get_text()] = divs[-1].get_text()
        elif self.source == 'weather values':
            js = _json.loads(markup)
            base = js['pollenForecast12hour']
            stored = list(base[layer + 'PollenIndex'] for layer in Pollen.TYPES)
            lzt = list(zip(*stored))
            db = {i / 2: lzt[i] for i in range(len(lzt))}
        else:
            j = page.select('.count') # or class .status
            db = {i: j[i].get_text() for i in range(Pollen.SOURCE_SPAN[self.source])}
        if len(db) == 0:
            if self.source == 'weather text':
                self.build(add_weather_query=not(add_weather_query)) # retry using the alternate query
            else:
                db = {i: 'null' for i in range(Pollen.SOURCE_SPAN[self.source])['null']}
        self.src = page
        self.db = db
        self.__has_built = True

    def get_day(self, day):
        """Returns the value in the db for the given day"""
        self.__check_built()
        data = None
        if self.source == 'weather text':
            date = str((_dt.date.today() + _dt.timedelta(days=day)).day)
            for dong in self.db:
                if dong.endswith(' ' + date):
                    data = self.db[dong]
                    break # not the best style but saves runtime
        else:
            # updates afternoon forecasts for today only (floor of cos of day)
            day += 0.5 * _math.floor(_math.cos(day)) * _math.floor(_dt.datetime.now().hour / 12)
            if type(self.db[day]) == str:
                data = self.db[int(day)].title()
            else:
                data = self.db[day]
        if data is not None and self.print_sources:
            print('[{}] day={}'.format(self.source, day))
        return data

    def get_today(self):
        """Returns the type of pollen for today"""
        self.__check_built()
        if self.source == 'weather text':
            if 'Tonight' in self.db:
                return self.db['Tonight']
            elif 'Today' in self.db:
                return self.db['Today']
        return self.get_day(0)

    def get_tomorrow(self):
        """Returns the type of pollen forecasted for tomorrow"""
        return self.get_day(1) # checks for valid db in get_day
        
    def print_db(self):
        """Prints all of the db information in a table format"""
        self.__check_built()
        print('Pollen data for', self.zipcode)
        for i, j in self.db.items():
            print('{:>{}}: {}'.format(i, len('Tonight'), j))

    def set_source(self, source):
        """Sets the source for this Pollen object. Requires `build` to be called to update data"""
        if not(source in Pollen.SOURCE_SPAN.keys()):
            raise ValueError(f'source must be one from [{", ".join(Pollen.SOURCE_SPAN.keys())}]')
        self.uri = Pollen.SOURCE_URLS[self.zipcode][source]
        if source == 'weather text':
            self.uri += str(self.zipcode)
        self.source = source
        self.__has_built = False

    def set_zipcode(self, zipcode):
        """Sets the zipcode for this Pollen object. Requires `build` to be called to update data"""
        if (self.source != 'weather text' and not(zipcode in Pollen.SOURCE_URLS.keys())) or \
            not(zipcode in Pollen.SOURCE_URLS.keys()) or zipcode < 0 or zipcode > 99501:
            raise ZipCodeNotFoundException(zipcode)
        self.zipcode = zipcode
        self.set_source(self.source) # ensures data is updated if the method is 'weather text'

class ViewModel(ObjectInitializer):
    """Class ViewModel can be used to set properties
       to be rendered in a web page"""
    pass

class ZipCodeNotFoundException(Exception):
    def __init__(self, zipcode, *args, **kwargs):
        super(ZipCodeNotFoundException, self).__init__(repr(self), *args, **kwargs)
        self.zipcode = zipcode

    def __repr__(self):
        zipcodes = ", ".join(map(str, Pollen.SOURCE_URLS.keys()))
        plural = zipcodes.count(',') > 0
        string = 'The only zipcode'
        if plural:
            string += 's'
        string += ' currently supported for Pollen '
        if plural:
            string += 'are'
        else:
            string += 'is'
        string += ' ' + zipcodes
        return string

if __name__ == '__main__':

    print('human hex for 2700 is', human_hex(2700))
    array = (1, 4, 16, 25)
    print('map args for', array, '->', map_args(map_args_test, array, z = 4))

    obj = ObjectInitializer({
        'one': 1,
        'two': 2,
        'three': 3
    })
    print('prints', obj.one, '-> expects 1')
    print('prints', obj.two, '-> expects 2')
    print('prints', obj.three, '-> expects 3')
    print('get attrs prints', len(obj.get_attributes()) == 3, '-> expects True')

    import sys
    import traceback
    
    p = Pollen('weather text')
    p.print_db()
    p.set_source('weather values')
    p.set_zipcode(98105)
    p.build()
    p.print_db()
    
    print('The next two tests will throw exceptions.')
    try:
        p.set_source('wrong source')
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)
    print()
    try:
        p.set_zipcode(97132)
    except Exception:
        exc_type, exc_value, exc_tb = sys.exc_info()
        traceback.print_exception(exc_type, exc_value, exc_tb)