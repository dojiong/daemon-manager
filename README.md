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
usage: dm [-h] {list,run} ...

client tool for daemon-manager

positional arguments:
  {list,run}
    run       start a daemon
    list      list daemons

optional arguments:
  -h, --help  show this help message and exit

$ dm run -h
usage: dm run [-h] [-o log_file] [-c dir] commandline

positional arguments:
  commandline           cmd to run

optional arguments:
  -h, --help            show this help message and exit
  -o log_file, --log log_file
                        output log file
  -c dir, --chdir dir   chdir to run

$ dm list -h
usage: dm list [-h]

optional arguments:
  -h, --help  show this help message and exit
```