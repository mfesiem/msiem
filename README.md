## McAfee SIEM Command Line Interface

[![Tests](https://github.com/mfesiem/msiem/workflows/test/badge.svg)](https://github.com/mfesiem/msiem/actions)
[![PyPI version](https://badge.fury.io/py/msiem.svg)](https://pypi.org/project/msiem/)
[![Docs](https://img.shields.io/badge/-manpage-blue)](https://mfesiem.github.io/docs/msiem/index.html)

```
                _                
  _ __ ___  ___(_) ___ _ __ ___  
 | '_ ` _ \/ __| |/ _ | '_ ` _ \ 
 | | | | | \__ | |  __| | | | | |
 |_| |_| |_|___|_|\___|_| |_| |_| CLI
     
 McAfee SIEM Command Line Interface
```

Most of the core `[msiempy](https://github.com/mfesiem/msiempy)` features accessible with CLI.  

Based on the work of [andywalen](https://github.com/andywalden).  

## Features

    msiem config              Set and print your msiempy config.
    msiem alarms              Query alarms with alarms and events based regex filters. 
                              Print, acknowledge, unacknowledge and delete alarms.
    msiem esm                 Show ESM version and misc informations regarding your ESM.
    msiem ds                  Add datasources from CSV or INI files, list, search, remove.
    msiem events              Query events with any simple filter.
    msiem api                 Quickly make API requests to any enpoints with any data.

## Installation
```bash
$ python3 -m pip install msiem --upgrade
```

## Command Line Interface documentation
**Read the [manpage](https://mfesiem.github.io/docs/msiem/)** or use `msiem -h`.  

#### More to come !

