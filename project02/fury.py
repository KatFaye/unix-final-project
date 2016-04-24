#!/usr/bin/env python2.7

import sys
import work_queue

# Constants
ALPHABET = string.ascii_lowercase + string.digits

# Main Execution

if __name__ == '__main__':

    #load journal

    try:
        JOURNAL = json.load(open('journal.json'))
    except:
        JOURNAL = dict()
    # Create Work Queue master with:
# 1. Random port between 9000 - 9999
# 2. Project name of hulk-NETID
# 3. Catalog mode enabled
    queue = work_queue.WorkQueue(work_queue.WORK_QUEUE_RANDOM_PORT, name='fury-kherring', catalog=True)
    queue.specify_log('fury-kherring.log') # Specify Work Queue log location

    for i in range(6):
        command = './hulk.py -l "{}"'.format(i)
    for i in range(6): #last five
        for j in itertools.product(ALPHABET, repeat = j): #first 1-3 prefix
            command = './hulk.py -l "{}" -p "{}"'.format(i, j)
        

        # Example check
        if command in JOURNAL:
            print >>sys.stderr, 'Already did', command
        else:
            task    = work_queue.Task(command)

        for source in ('hulk.py', 'hashes.txt'):
            task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)

        queue.submit(task)

    while not queue.empty():
        task = queue.wait()
       
        if task and task.return_status == 0:
            JOURNAL[task.command] = task.output.split()
            with open('journal.json.new', 'w') as stream:
                json.dump(JOURNAL, stream)
            os.rename('journal.json.new', 'journal-kherring.json')
        # Example recording

