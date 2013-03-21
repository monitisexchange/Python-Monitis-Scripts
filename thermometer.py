#!/usr/bin/env python

from monitis.api import Monitis
from monitis.monitors.custom import CustomMonitor
from monitis.monitors.params import ResultParams, DataType

from sys import stdin


def read_id():
    """read_id() -
     gets and returns monitor id from local file.
    """
    return open('.monitor.id').readline().strip('\n')


def read_data():
    """read_data() -
     reads data from standard input.
     Example of input 
     '2013/01/29 23:33:00 Temperature 63.16F 17.31C'
    """
    data = stdin.read().split()
    timestamp = ' '.join(data[:2]) # two first fields (data and time)
    temperature = float(data[-1].rstrip('C')) # last field - temp in C
    return (timestamp, temperature)


def add_result():
    """add_result() -
     adds results to a Monitis monitor define by id save locally. 
    """    
    time, temp = read_data()
    cm = CustomMonitor(monitor_id=read_id())
    cm.add_result(temperature=temp)


def main():
    """"main() -
     standard main function.
    """
    add_result()



if __name__ == "__main__":
    main()
