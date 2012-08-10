daemon-manager
==============

manage linux daemons.

###Usage
```
#run a daemon
dm run "sleep 10"

#list all daemons
dm list

#kill a daemon named "server"
dm kill -n server
```

####cmdline help
```
$ dm -h
$ dm run -h
$ dm list -h
$ dm kill -h
```