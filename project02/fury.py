#!/usr/bin/env python2.7

import sys
import work_queue

# Constants

LENGTH   = int(sys.argv[1])
ATTEMPTS = int(sys.argv[2])
HASHES   = sys.argv[3]
TASKS    = int(sys.argv[4])
SOURCES  = ('hulk.py', HASHES)
PORT     = 9241

# Main Execution

if __name__ == '__main__':
    # Create Work Queue master with:
# 1. Random port between 9000 - 9999
# 2. Project name of hulk-NETID
# 3. Catalog mode enabled
    queue = work_queue.WorkQueue(work_queue.WORK_QUEUE_RANDOM_PORT, name='fury-kherring', catalog=True)
    queue.specify_log('fury-kherring.log') # Specify Work Queue log location


    for _ in range(TASKS):
        command = './hulk.py {} {} {}'.format(LENGTH, ATTEMPTS, HASHES)
        

        # Example check
        if command in JOURNAL:
            print >>sys.stderr, 'Already did', command
        else:
            task    = work_queue.Task(command)

        for source in SOURCES:
            task.specify_file(source, source, work_queue.WORK_QUEUE_INPUT)

        queue.submit(task)

    while not queue.empty():
        task = queue.wait()
        JOURNAL[task.command] = task.output.split()
        with open('journal.json.new', 'w') as stream:
            json.dump(JOURNAL, stream)
        os.rename('journal.json.new', 'journal-kherring.json')
        if task and task.return_status == 0:
            sys.stdout.write(task.output)
            sys.stdout.flush()
        # Example recording

