#!/usr/bin/env python2.7

import sys, os, getopt, socket, logging
from stat import *
import stat, signal, mimetypes, binascii


# Constants

PROGRAM  = os.path.basename(sys.argv[0])
LOGLEVEL = logging.INFO
ADDRESS  = '0.0.0.0'
DOCROOT  = '.'
PORT     = 9234
FORKING  = False

# Utility Functions

def usage(status=0):
    print >>sys.stderr, '''./spidey.py -h
Usage: spidey.py [-d DOCROOT -p PORT -f -v]

Options:

    -h         Show this help message
    -f         Enable forking mode
    -v         Set logging to DEBUG level

    -d DOCROOT Set root directory (default is current directory)
    -p PORT    TCP Port to listen to (default is 9234)'''
    sys.exit(status)

# BaseHandler Class

class BaseHandler(object):
    def __init__(self, fd, address):
        self.logger  = logging.getLogger()
        self.socket  = fd
        self.address = '{}:{}'.format(*address)
        self.stream  = self.socket.makefile('w+')

        self.debug('Connect')

    def debug(self, message, *args):
        message = message.format(*args)
        self.logger.debug('{} | {}'.format(self.address, message))

    def info(self, message, *args):
        message = message.format(*args)
        self.logger.info('{} | {}'.format(self.address, message))

    def warn(self, message, *args):
        message = message.format(*args)
        self.logger.warn('{} | {}'.format(self.address, message))

    def error(self, message, *args):
        message = message.format(*args)
        self.logger.error('{} | {}'.format(self.address, message))

    def exception(self, message, *args):
        message = message.format(*args)
        self.logger.error('{} | {}'.format(self.address, message))

    def handle(self):
        #raise NotImplementedError
        pass

    def finish(self):
        self.debug('Finish')
        try:
            self.stream.flush()
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error as e:
            pass
        finally:
            self.socket.close()

# HTTPHandler Class

class HTTPHandler(BaseHandler):
    def __init__(self, fd, address, docroot=None):
        BaseHandler.__init__(self, fd, address)
        self.docroot = docroot

    # HTTPClient.handle Pseudo-code
    def handle(self):
        self.debug('Handle')

        # parse HTTP request and headers
        self._parse_request()

        # build uripath by normalizing REQUEST_URI
        self.uripath = os.path.normpath(self.docroot + os.environ['REQUEST_URI'])
        # check path existence and types and then dispatch
        if not os.path.exists(self.uripath): #or not (os.path.basename(self.uripath) == self.docroot):
            self.debug('404 error on {}'.format(self.uripath))
            self._handle_error(404) # 404 error
        elif S_ISREG(os.stat(self.uripath).st_mode) and os.access(self.uripath,os.X_OK):
            self.debug('Script at {}'.format(self.uripath))
            self._handle_script() # CGI script
        elif S_ISREG(os.stat(self.uripath).st_mode) and os.access(self.uripath,os.R_OK):
            self.debug('Static file at {}'.format(self.uripath))
            self._handle_file() # Static file
        elif S_ISDIR(os.stat(self.uripath).st_mode) and os.access(self.uripath,os.R_OK):
            self.debug('Directory at path {}'.format(self.uripath))
            self._handle_directory() # Directory listing
        else:
            self.debug('403 error on {}'.format(self.uripath))
            self._handle_error(403) # 403 error
        self.stream.write('</body>\n')
        self.stream.write('</html>\n')

    # split up request
    def _parse_request(self):
        os.environ['REMOTE_ADDR'] = self.address.split(':', 1)[0]

        data = self.stream.readline().strip().split(' ')
        if '?' in data[1]:
            os.environ['QUERY_STRING'] = data[1].split('?',1)[1]
            os.environ['REQUEST_URI'] = data[1].split('?',1)[0]
        else:
            os.environ['REQUEST_URI'] = data[1]

        os.environ['REQUEST_METHOD'] = data[0]
        

        data = self.stream.readline().strip()
        while data:
            key = '{}{}'.format('HTTP_',data.split(':',1)[0].upper().replace('-','_'))
            os.environ[key]=data.split(':',1)[1]
            data = self.stream.readline().strip()

    # execute script
    def _handle_script(self):
        signal.signal(signal.SIGCHLD, signal.SIG_DFL)
        try:
            for line in os.popen(self.uripath):
                self.stream.write(line)
        except OSError as e:
            self.error('Unable to execute script {}: {}',self.uripath,e)
        signal.signal(signal.SIGCHLD, signal.SIG_IGN)

    # open contents of file
    def _handle_file(self):
        self._header()

        mimetype, _ = mimetypes.guess_type(self.uripath)
        if mimetype is None:
            mimetype = 'application/octet-stream'
        maintype, subtype = mimetype.split('/', 1)
        if subtype == 'plain':
            self.stream.write('<pre>\n')
            with open(self.uripath,'rb') as f:
                data = f.read()
                self.stream.write(data)
                f.close()
            self.stream.write('</pre>\n')
        elif subtype == 'html':
            with open(self.uripath,'rb') as f:
                data = f.read()
                self.stream.write(data)
                f.close()
        else:
            with open(self.uripath,'rb') as f:
                data = f.read()
                self.stream.write(data)
                f.close()

    # lists entries in a directory - name, size, type
    def _handle_directory(self):
        self._header()

        entries = os.listdir(self.uripath)
        dirs = []
        files = []
        for entry in entries:
            path = os.path.normpath(self.uripath+'/'+entry)
            if S_ISDIR(os.stat(path).st_mode):
                dirs.append(entry)
            else:
                files.append(entry)

        sorted(dirs)
        sorted(files)
        self.stream.write('<h1>Directory: {}</h1><hr><br>\n'.format(self.uripath))
        self.stream.write('<table border="1" style="width:100%">\n')
        self.stream.write('<tr><th>Type</th><th>Name</th><th>Size</th></tr>\n')
        basedir = os.path.basename(os.path.normpath(self.uripath))
        for d in dirs:
            path = os.path.normpath(self.uripath+'/'+d)
            relpath = os.path.normpath(basedir+'/'+d)

            self.stream.write('<tr>\n')
            self.stream.write('<td>D</td>\n')
            self.stream.write('<td><a href="{}">{}</a></td>\n'.format(relpath,d))
            self.stream.write('<td>{}</td>\n'.format(os.stat(path).st_size))
            self.stream.write('</tr>\n')
        for f in files:
            path = os.path.normpath(self.uripath+'/'+f)
            relpath = os.path.normpath(basedir+'/'+f)

            self.stream.write('<tr>\n')
            self.stream.write('<td>F</td>\n')
            self.stream.write('<td><a href="{}">{}</a></td>\n'.format(relpath,f))
            self.stream.write('<td>{}</td>\n'.format(os.stat(path).st_size))
            self.stream.write('</tr>\n')
        self.stream.write('</table>\n')

    # HTTP error + picture
    def _handle_error(self,errno):
        self._header()
        self.stream.write('<h1>{} Error!</h1><hr>\n'.format(errno))
        if errno == 404:
            self.stream.write('<img src={} alt={}>\n'.format('http://static.splashnology.com/articles/404_Pages_feb_2012/main.jpg','404 Error!'))
        else: #assume 403 error
            self.stream.write('<img src={} alt={}>\n'.format('http://scratiphone.com/wp-content/uploads/2012/11/error403.jpg', '403 Error!'))
    def _header(self):
        self.stream.write('HTTP/1.0 200 OK\r\n')
        self.stream.write('Content-Type: text/html\r\n')
        self.stream.write('\r\n')

        self.stream.write('<html lang="en">\n')
        self.stream.write('<head>\n')
        self.stream.write('<meta charset="utf-8">\n')
        self.stream.write('<meta http-equiv="X-UA-Compatible" content="IE=edge">\n')
        self.stream.write('<meta name="viewport" content="width=device-width, initial-scale=1">\n')
        self.stream.write('<title>spidey.sh</title>\n')
        self.stream.write('</head>\n')
        self.stream.write('<body>\n')
# TCPServer Class

class TCPServer(object):
    def __init__(self, address=ADDRESS, port=PORT, docroot=DOCROOT, forking=FORKING, handler=HTTPHandler):
        self.logger  = logging.getLogger()
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.port    = port
        self.docroot = docroot
        self.forking = forking
        self.handler = handler
        try:
            self.address = socket.gethostbyname(address)
        except socket.gaierror as e:
            logging.error('Unable to lookup {}: {}'.format(ADDRESS,e))
            sys.exit(1)
        '''
        os.environ['REMOTE_ADDR']=self.address
        os.environ['REMOTE_HOST']=address
        os.environ['REMOTE_PORT']=self.port
        '''
    def run(self):
        try:
            # bind socket to address and port and then listen
            self.socket.bind((self.address,self.port))
            self.socket.listen(0)
        except socket.error as e:
            self.logger.error('Could not listen on {}:{}: {}'.format(self.address, self.port, e))
            sys.exit(1)

        self.logger.info('Listening on {}:{}...'.format(self.address,self.port))

        while True:
            # accept incoming connection
            client, address = self.socket.accept()
            self.logger.debug('Accepted connection from {}:{}'.format(*address))
            # instantiate handler, handle connection, finish connection
            handler = self.handler(client,address,self.docroot)
            if not self.forking:
                try:
                    handler.handle()
                except Exception as e:
                    handler.exception('Exception: {}', e)
                finally:
                    handler.finish()
            else:
                try:
                    pid = os.fork()
                except OSError as e:
                    logging.getLogger().error('Unable to fork: {}',e)

                if pid == 0:
                    try:    
                        handler.handle()
                    except Exception as e:
                        handler.exception('Exception: {}', e)
                    finally:
                        handler.finish()
                    os._exit(0)
                else:
                    try:
                        pid, status = os.wait()
                    except OSError as e:
                        logging.error('Unable to wait: {}',e)
                    client.close()


# Main Execution
if __name__ == '__main__':
    try:
        opts, args = getopt.getopt(sys.argv[1:], "d:p:fvh")
    except getopt.GetoptError as err:
        print err
        usage()

    for o,a in opts:
        if o == '-d':
            DOCROOT = a
        elif o == '-p':
            PORT = int(a)
        elif o == '-f':
            FORKING = True
        elif o == '-v':
            LOGLEVEL = logging.DEBUG
        else:
            usage(1)

    # set logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    server = TCPServer(port=PORT,docroot=DOCROOT,forking=FORKING)

    try:
        server.run()
    except KeyboardInterrupt:
        sys.exit(0)