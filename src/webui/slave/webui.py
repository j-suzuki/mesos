import bottle
import commands
import datetime

from bottle import abort, route, send_file, template
from slave import get_slave

start_time = datetime.datetime.now()


@route('/')
def index():
  bottle.TEMPLATES.clear() # For rapid development
  return template("index", start_time = start_time)


@route('/framework/:id#[0-9]*#')
def framework(id):
  bottle.TEMPLATES.clear() # For rapid development
  return template("framework", framework_id = int(id))


@route('/static/:filename#.*#')
def static(filename):
  send_file(filename, root = './webui/static')


@route('/log/:level#[A-Z]*#')
def log_full(level):
  send_file('nexus-slave.' + level, root = '/tmp',
            guessmime = False, mimetype = 'text/plain')


@route('/log/:level#[A-Z]*#/:lines#[0-9]*#')
def log_tail(level, lines):
  bottle.response.content_type = 'text/plain'
  return commands.getoutput('tail -%s /tmp/nexus-slave.%s' % (lines, level))


@route('/framework-logs/:fid#[0-9]*#/:log_type#[a-z]*#')
def framework_log_full(fid, log_type):
  sid = get_slave().id
  if sid != -1:
    send_file(log_type, root = './work/slave-%d/framework-%s' % (sid, fid),
              guessmime = False, mimetype = 'text/plain')
  else:
    abort(403, 'Slave not yet registered with master')


@route('/framework-logs/:fid#[0-9]*#/:log_type#[a-z]*#/:lines#[0-9]*#')
def framework_log_tail(fid, log_type, lines):
  bottle.response.content_type = 'text/plain'
  sid = get_slave().id
  if sid != -1:
    filename = './work/slave-%d/framework-%s/%s' % (sid, fid, log_type)
    print filename
    return commands.getoutput('tail -%s %s' % (lines, filename))
  else:
    abort(403, 'Slave not yet registered with master')


bottle.TEMPLATE_PATH.append('./webui/slave/')
bottle.run(host = '0.0.0.0', port = 8081)