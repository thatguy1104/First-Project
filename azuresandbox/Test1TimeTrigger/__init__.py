import datetime
import logging

import azure.functions as func

from . import dummy
import numpy
#import requests
#import pyodbc

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()

    if mytimer.past_due:
        logging.info('The timer is past due!')

    print("WOW, IT PRINTS!?")

    logging.info('Python timer trigger function ran at %s', utc_timestamp)
    
    dummy.dummyfunc()
    
#    a = np.arange(15).reshape(3, 5)
#    print(a)
