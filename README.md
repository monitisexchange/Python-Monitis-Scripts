Examples of Creating Monitors and Recording Metrics in python
=============================================================

monitis_create_monitor.py


## create a new monitor
    $ ./monitis_create_monitor.py -a <api_key> -s <api_secret> \
     -r "1m:1 Min. Average:processes:4;5m:5 Min. Average:processes:4;15m:15 Min. Average:processes:4"\
     -m loadMonitor  -n "load monitor"
    {"status":"ok","data":794}

## list existing monitors
    $ ./monitis_create_monitor.py -a <api_key> -s <secret_key>  -l
    491	loadMonitor	load monitor
    793	loginMonitor	login monitor
    794	loginMonitor	login monitor

## delete a monitor
    $ ./monitis_create_monitor.py -a <api_key> -s <api_secret> -d -i 794
    {"status":"ok","data":null}

    $ ./monitis_create_monitor.py -a <api_key> -s <api_secret>  -l
    491	loadMonitor	load monitor
    793	loginMonitor	login monitor

## record a metric to an existing monitor
    $ python ./monitis_record_load.py -a <api_key> -s <api_secret>
    {"status":"ok","data":null}
