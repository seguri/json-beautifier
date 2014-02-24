from google.appengine.api import memcache
from webapp2_extras.security import generate_random_string
import jinja2
import json
import os
import webapp2

MEMCACHE_EXPIRE = 5 * 60 # seconds

JINJA_ENVIRONMENT = jinja2.Environment(
    loader=jinja2.FileSystemLoader(os.path.dirname(__file__)),
)


def is_json(s):
    try:
        json.loads(s)
    except ValueError:
        return False
    return True


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.response.write('Make a POST with json=your_stringified_json to have it beautified.')

    def post(self):
        json_ = self.request.get('json')
        if json_ and is_json(json_):
            random_string = generate_random_string(length=16)
            if memcache.add(random_string, json_, MEMCACHE_EXPIRE):
                self.response.write('%s/%s' % (self.request.host, random_string))
            else:
                self.response.write('ERROR: Could not set cache.')
        else:
            self.response.write('ERROR: You must provide a valid json.')


class CacheHandler(webapp2.RequestHandler):

    def get(self, key):
        cached = memcache.get(key)
        if cached:
            template = JINJA_ENVIRONMENT.get_template('templates/beautified.html')
            self.response.write(template.render({'json': cached}))
        else:
            self.response.set_status(404)
            self.response('ERROR: Could not find element "%s" in cache.' % key)

urls = (
    (r'/', MainPage),
    (r'/(\w+)', CacheHandler),
)
application = webapp2.WSGIApplication(urls, debug=True)
