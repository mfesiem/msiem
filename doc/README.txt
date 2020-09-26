usage: msiem [-h] [-V] {config,alarms,esm,ds,events,api} ...

                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_| CLI
     
McAfee SIEM Command Line Interface 0.3.0.dev
License: MIT
Credits: Andy Walden, Tristan Landes

Run 'msiem <command> --help' for more information about a sub-command.

positional arguments:
  {config,alarms,esm,ds,events,api}
    config              Set and print your msiempy config.
    alarms              Query alarms with alarms and events based regex filters. Print, acknowledge,
                        unacknowledge and delete alarms.
    esm                 Show ESM version and misc informations regarding your ESM.
    ds                  Add datasources from CSV or INI files, list, search, remove.
    events              Query events with any simple filter. Add a note to events.
    api                 Quickly make API requests to any enpoints with any data.

optional arguments:
  -h, --help            show this help message and exit
  -V, --version         Show version and exit (default: False)
