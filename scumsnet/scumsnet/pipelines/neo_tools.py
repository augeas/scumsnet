
# Licensed under the Apache License Version 2.0: http://www.apache.org/licenses/LICENSE-2.0.txt

import logging
import re
import time


noSlash = re.compile(r'\\')


def cypherval(val):
    """Escape quotes and slashes for use in Cypher queries."""    
    if isinstance(val, (int, bool)):
        return str(val).lower()
    else:
        # Escape all the backslashes.
        escval = re.sub(noSlash, r'\\\\', val)
        escval = str(re.sub("'", "\\'", escval))
        escval = str(re.sub('"', '\\"', escval))
        escval = str(re.sub("\n", "\\\\n", escval))
        return "'"+escval+"'"


def unwind_query(*clauses):
    return '\n'.join(['UNWIND {data} AS d'] + list(clauses))


def neo_tx(db, query, data=None):
    with db.session() as session:
        success = False
        tries = 0
        max_tries = 50
        while not success and tries < max_tries:
            try:
                with session.begin_transaction() as tx:
                    if data is None:
                        tx.run(query)
                    else:
                        tx.run(query, data=data)
                success = True
            except:
                logging.warning('*** Neo tx failed, attempt %d ***' % (tries+1,), exc_info=True)
                tries += 1
                time.sleep(10)
                

def unwind_tx(db, data, *clauses):
    query = unwind_query(*clauses)
    neo_tx(db, query, data)
     
    
