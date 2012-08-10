daemon-manager
==============

manage linux daemons.

###Usage
```
#run a daemon
dm run "sleep 10"

#list all daemons
dm list
```

####cmdline help
```
$ dm -h
usage: dm.py [-h] {list,run} ...

client tool for daemon-manager

positional arguments:
  {list,run}
    run       start a daemon
    list      list daemons

optional arguments:
  -h, --help  show this help message and exit

$ dm run -h
usage: dm.py run [-h] [-o log_file] [-c dir] commandline

positional arguments:
  commandline           cmd to run

optional arguments:
  -h, --help            show this help message and exit
  -o log_file, --stdout log_file
                        output log file
  -c dir, --chdir dir   chdir to run

$$ dm list -h
usage: dm.py list [-h]

optional arguments:
  -h, --help  show this help message and exit
```