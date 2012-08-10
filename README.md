daemon-manager
==============

manage linux daemons.

###Usage
```
#start server
python server.py

#run a daemon
python dm.py run "sleep 10"
```

####cmdline help
```
$ ./dm.py -h
usage: dm.py [-h] {list,run} ...

client tool for daemon-manager

positional arguments:
  {list,run}
    run       start a daemon
    list      list daemons

optional arguments:
  -h, --help  show this help message and exit

$ ./dm.py run -h
usage: dm.py run [-h] [-u user] [-o stdout_file] [-c dir] commandline

positional arguments:
  commandline           cmd to run

optional arguments:
  -h, --help            show this help message and exit
  -u user, --user user  run as
  -o stdout_file, --stdout stdout_file
                        stdout log file
  -c dir, --chdir dir   chdir to run

$ ./dm.py list -h
usage: dm.py list [-h] [-a]

optional arguments:
  -h, --help  show this help message and exit
  -a, --all   filter by user
```