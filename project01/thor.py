#!/usr/bin/env python2.7
#thor.py
#Author: Kat Herring

import getopt, logging, os, time, socket, sys

# Constants
ADDRESS  = '127.0.0.1'
PORT     = 80
URL      = 'localhost'
PROGRAM  = os.path.basename(sys.argv[0])
LOGLEVEL = logging.INFO
PATH = '/'
REQUESTS = 1
PROCESSES = 1

# Utility Functions

def usage(exit_code=0):
    print >>sys.stderr, '''Usage: {program} [-r REQUESTS -p PROCESSES -v] URL

Options:

    -h              Show this help message
    -v              Set logging to DEBUG level

    -r REQUESTS     Number of requests to process (Default is 1)
    -p PROCESSES    Number of processes (Default is 1)
'''.format(program=PROGRAM)
    sys.exit(exit_code)

# TCPClient class

class TCPClient(object):
    def __init__(self, address=ADDRESS, port=PORT):
        self.logger = logging.getLogger()
        self.address = address
        self.port    = port
        self.socket  = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def handle(self):
        #handle connection
        self.logger.debug('Handle')
        raise NotImplementedError

    def run(self):
        self.logger.debug('Inputted URL: {}'.format(self.url))
        
        #parse URL
        self.url = self.url.split('://')[-1]

        #get host
        self.host = self.url.split('/',1)[0]
        self.host = self.host.split(':',1)[0]
        self.logger.debug('Parsed Host: {}'.format(self.host))
        
        # port
        if ':' in self.url:
            self.port = self.url.split(':',1)[1]
            self.port = self.port.split('/',1)[0]
        
        self.logger.debug('Parsed Port: {}'.format(self.port))
       
        # path
        if '/' in self.url:
            self.path = '/' + self.url.split('/',1)[1]
        else: #set to default
            self.path = PATH 
        
        self.logger.debug('Current Path: {}'.format(self.path))
        
        # query
        if '?' in self.path:
            self.query = self.path.split('?',1)[1]
            self.path = self.path.split('?',1)[0]
            
        else:
            self.query = ''

        #get address
        try:
            self.address = socket.gethostbyname(self.host)
        except socket.error as e:
            self.logger.error('Unable to find {}: {}'.format(self.host,e))
            sys.exit(1)

        #connect
        try:
            self.socket.connect((self.host, self.port))
            self.stream = self.socket.makefile('w+')
        except socket.error as e:
            self.logger.error("Unable to connect to {}:{}: {}".format(self.address, self.port, e))
        
        self.logger.debug('Connected to {}:{}...'.format(self.address, self.port))
        
        try:
            self.logger.debug('Handle...')
            self.handle()
        except Exception as e:
            self.logger.debug('Finish...')
        finally:
            self.finish()

    def finish(self):
        try:
            self.socket.shutdown(socket.SHUT_RDWR)
        except socket.error:
            pass
        finally:
            self.socket.close()

class HTTPClient(TCPClient):
    def __init__(self, url=URL):
        TCPClient.__init__(self, ADDRESS, PORT)
        self.url = url

    def handle(self):
        # Send request
        self.logger.debug('Sending Request...')
        self.stream.write('GET {} HTTP/1.0\r\n'.format(self.path))
        self.stream.write('Host: {}\r\n'.format(self.host))
        self.stream.write('\r\n')
        self.stream.flush()

        # Receive response
        self.logger.debug('Getting Response...')
        try: 
            data = self.stream.readline()
            while data:
                print data
                data = self.stream.readline()
        except socket.error: 
            pass


# Main execution

if __name__ == '__main__':
    # Set logging level
        # Parse command-line arguments
    try:
        options, arguments = getopt.getopt(sys.argv[1:], "hvr:p:")
    except getopt.GetoptError as e:
        print e
        usage(1)

    for option, value in options:
        if option == '-v':
            LOGLEVEL = logging.DEBUG
        elif option == '-p':
            PROCESSES = int(value)
        elif option == '-r':
            REQUESTS == int(value)
        else: #invalid opt
            usage(1)

    if len(arguments) != 1:
        usage(1)

    URL = arguments[0]
    #logging level
    logging.basicConfig(
        level   = LOGLEVEL,
        format  = '[%(asctime)s] %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )

    children = [] #empty array of PIDs
    times = []
    processes = dict()

    for process in range(PROCESSES):
        try:
            pid = os.fork()
        except OSError as e:
            logging.error('Unable to fork: {}'.format(e))
        if pid: 
            children.append(pid)
        else:    
            for request in range(REQUESTS):      
                start_time = time.time()
                client = HTTPClient(URL)
                try:
                    client.run()
                except KeyboardInterrupt:
                    sys.exit(0)
                end_time = time.time()
                times.append(end_time-start_time)
                logging.info('Elapsed time: {:0.2f}'.format(end_time - start_time))     
    for child in children:
        try: 
            pid, status = os.waitpid(child, 0)
            processes[pid] = status
        except OSError as e:
            logging.error('Failed to wait for {}: {}'.format(child, e))

    for pid, status in processes.items():
        logging.debug('Process {} killed with exit status {}'.format(pid, status))

    sys.exit(0)
