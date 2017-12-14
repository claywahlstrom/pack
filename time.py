
"""
time module

"""

DEF_COUNTRY = 'usa'
DEF_CITY    = 'vancouver'

MONTHS = ['january', 'february', 'march',
          'april', 'may', 'june', 'july',
          'august', 'september', 'october',
          'november', 'december']

TAD_BASE = 'https://www.timeanddate.com/astronomy'

def get_time_struct():
    """Returns the local time as struct object"""
    from time import localtime, time
    return localtime(time())

class SunInfo:
    """A class for storing sun data collected from timeanddate.com (c) in the following form:
    |    Rise/Set    |     Daylength       |   Solar Noon
    Sunrise | Sunset | Length | Difference | Time | Million Miles

    Countries with more than one occurence of a city require state abbrev.s,
    such as Portland, OR, and Portland, ME:
         city -> portland-or
         city -> portland-me
    
    """

    COLS = 6
    
    def __init__(self, country=DEF_COUNTRY, city=DEF_CITY):
        self.country = country
        self.city = city
        self.build()
        
    def build(self):
        """Collects sun data and creates the following fields:
            req  = request response
            cont = web request content
            soup = `bs4` soup object
            data = list of data scraped
        
        """
        from bs4 import BeautifulSoup as _BS
        import requests as _requests
        req = _requests.get('/'.join([TAD_BASE, self.country, self.city]))
        cont = req.content
        soup = _BS(cont, 'html.parser')
        scraped = [td.text for td in soup.select('#as-monthsun > tbody > tr > td')]

        # parse the data into rows
        data = list()
        for i in range(0, len(scraped), SunInfo.COLS):
            data.append(scraped[i: i + SunInfo.COLS])

        # store relevant varss
        self.req = req
        self.cont = cont
        self.soup = soup
        self.scraped = scraped
        self.data = data
        
    def get_data(self):
        """Returns data retrieved and parsed from timeanddate.com (c)"""
        return self.data

    def get_sunrise(self, day=0):
        """Returns string of sunrise time"""
        sunrise = self.data[day][0]
        return sunrise

    def get_sunset(self, day=0):
        """Returns string of sunset time"""
        sunset = self.data[day][1]
        return sunset

    def rebuild(self):
        """An alias for the `build` method"""
        self.build()
        
def time_until(year, month, day):
    """Finds time until year, month, day and returns a dt.timedelta object"""
    import datetime as dt
    start = dt.datetime.today()
    end = dt.datetime(year, month, day, 0, 0, 0)
    return end - start

if __name__ == '__main__':
    print(get_time_struct())
    suninfo = SunInfo()
    print(suninfo.get_sunset())
    
    print('birthday', time_until(2017, 11, 6))
    print('exams over', time_until(2017, 12, 14))
