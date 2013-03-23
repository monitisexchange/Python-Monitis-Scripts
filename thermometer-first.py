#!/usr/bin/env python

from monitis.api import Monitis
from monitis.monitors.custom import CustomMonitor
from monitis.monitors.params import ResultParams, DataType

from sys import stdin

def first_time():
    """first_time() -
     connects to Monitis and sets new monitor mesuring temprature up.
    """
    rp = ResultParams(
        'temperature',
        'Temperature in',
        'C',
        DataType('float'))
    cm = CustomMonitor.add_monitor(
        rp,
        name='temperature monitor',
        tag='enviromental')
    return cm.get_monitor_info()['id']


def save_id():
    """save_id() -
     saves monitor id (obtained from Monitis server) into a local file.
    """
    output = open('.temperature.monitor.id','w')
    output.write(first_time() + '\n')
   
 
def main():
    """main() -
     standard main function.
    """
    save_id()



if __name__ == "__main__":
    main()

