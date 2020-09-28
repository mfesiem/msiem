#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Add datasources from CSV or INI files, list, search, remove.  """

import csv
import os
import sys
import time
import traceback
from configparser import ConfigParser, NoSectionError, MissingSectionHeaderError
from pathlib import Path
from datetime import timedelta, datetime

from msiempy import DataSource, DevTree, NitroSession

devtree=None

def verify_dir(dir):
    """
    Checks if a directory exists, if not, it creates it.
    
    Args:
        path (str): name of directory to check
    
    Returns:
        path object for directory
    
    Raises:
        OSError if unable to create the directory due to permissions
        or whatnot. 
        RuntimeError if the dir is a file.  
    """
    path = Path(dir)

    if os.path.isdir(path):
        pass
    elif os.path.isfile(dir):
        raise RuntimeError("The dir is a file")
    elif not os.path.exists(dir): 
        try:
            os.makedir(path)
        except OSError:
            raise
    return path
    
def scan_dir(dir):
    """
    Args:
        dir (str): directory name to scan
    
    Returns:
        list of any files in dir or none
    """
    path = Path(dir)
    return [file for file in path.iterdir()]
     
def convert_ds_files(files):
    """
    Abstraction function between cli and file processing. 
    
    Checks given list of filenames to see if they are ini, 
    csv or otherwise. If so, routes them to appropriate
    conversion function.
    
    Args:
        filenames (list): list of filenames to convert         
   
    Returns:
        list of dicts - each represents a single datasource config            
    """
    ds_lods = []
    for file in files:
        ds_dict = ini_to_dict(file, 'datasource')
        if ds_dict:
            ds_lods.append(ds_dict)
        else:    
            csv_lod = csv_to_dict(file)
            if csv_lod:
                ds_lods.extend(csv_lod)
    return ds_lods

def csv_to_dict(file):
    """
    Attempts to convert csv file into dict. 
    
    First it's converted into a list of lists containing the rows.
    
    Validity is determined by the column count; valid datasource
    csv files will have 3 or more columns. 
    
    Args:
        file (str): filename to convert
        types (dict): {type_id: file_str}
    Returns:
        list of lists from the CSV file or None on failure
        
    Raises:
        ValueError: if 3col datasource file detected without ini types
    """
    csv_lol = csv_to_lol(file)
    
    if not csv_lol:
        ds_dicts = None
    elif len(csv_lol[0]) < 3:
        ds_dicts = None
    else:
        ds_dicts = process_export_csv(csv_lol)   
    return ds_dicts
 
def process_export_csv(lol):
    """
    Args:
        list of lists - converted datasource export file
    """
    headers, lol = get_csv_headers(lol)
    
    if not headers:
        return None
    ds_dicts=[]
    for line in lol:
        ds_dicts.append(dict(zip(headers, line)))
    
    return ds_dicts

def get_csv_headers(lol):
    """
    """
    headers = lol.pop(0)
    return (headers, lol)
    
def ini_to_dict(filename, subdict):
    """
    ini_to_dict() wrapper to extract subdict
    
    Args:
        filename (str): ini file to convert
        subdict (str): section in ini file / dict key 
    
    Returns:
        dict (str:str) key, val
     
    Note:
        Without this wrapper the result would be {key {k1:v1, k2:v2}}
        instead of flat {k1:v1, k2:v2}
        
    """
    ini_dict = _ini_to_dict(filename)
    
    try:
        return ini_dict.get(subdict)
    except AttributeError:
        pass
    
def _ini_to_dict(filename):
    """
    Returns:
        dict containing values of ini file or None if file is not valid
    """
    class INI_Parser(ConfigParser):
        def get_ini_dict(self):
            ini_dict = dict(self._sections)
            for key in ini_dict:
                ini_dict[key] = dict(self._defaults, **ini_dict[key])
                ini_dict[key].pop('__name__', None)
            return ini_dict
    parser = INI_Parser()

    try:
        with open(filename, 'r') as open_f:
            parser.read_file(open_f)
            return parser.get_ini_dict()
    except (OSError, PermissionError, UnicodeDecodeError,
            MissingSectionHeaderError, NoSectionError):
        pass

def csv_to_lol(file):
    """
    Returns:
        list of lists from the CSV file or None on failure
    """
    csv_data = []
    try:
        with open(file, 'r') as open_f:
            reader = csv.reader(open_f)
            return list(reader)
    except (OSError, PermissionError, UnicodeDecodeError) as e:
        raise RuntimeError("Looks like the CSV file can't be read.") from e
                    
def verify_ds(ds_names):
    """
    """
    for name in ds_names:
        if devtree.ds(name):
            return True
        else:
            return None

def search(term, devtree):
    """
    Search the device tree for a datasource
    
    Args:
        term (str):  name, IPv4/IPv6 address, hostname or datasource ID
                     for the datasource to locate
                     
        devtree (obj): devtree object to be searched

    Returns:
        dict (str:str) of datasource attributes
    """
    return devtree.search(term)
    
def dstools(pargs):
    """
    Add datasources from CSV or INI files, list, search, remove.  
    """
    global devtree

    devtree = DevTree()

    if pargs.add:   
        ds_dir = pargs.add
        new_files = None

        if os.path.isfile(ds_dir):
            new_files = [ds_dir]
        else:
            dsdir_path = verify_dir(ds_dir)
            new_files = scan_dir(dsdir_path)

        if not new_files:
            print("No datasource files found.")
            sys.exit(0)
        
        
        ds_lod = convert_ds_files(new_files)

        ds_to_verify = []
        
        for ds in ds_lod:
            if ds['name'] in devtree:
                print('Duplicate datasource Name. Datasource not ' 
                       'added: {} - {}.'.format(ds['name'], ds['ds_ip']))
                continue

            if ds['ds_ip'] in devtree:
                print('Duplicate datasource IP. Datasource not ' 
                       'added: {} - {}.'.format(ds['name'], ds['ds_ip']))
                continue
            
            try:

                if ds.get('client', None):
                    print("Adding Client Datasource: {}".format(ds))
                    resp = devtree.add_client(ds)
                else: 
                    print("Adding Datasource: {}".format(ds))
                    resp = devtree.add(ds)
                
                if not resp:
                    print('Something went wrong, Datasource {} not added.')
                    continue
                else:
                    # Wait for the add DS query to execuite ...
                    time.sleep(1)
                    ds_status = NitroSession().api_request('dsAddDataSourcesStatus', {"jobId": resp}, retry=0)
                    if not isinstance(ds_status, dict):
                        print('Something went wrong, Datasource {} not added.\n{}'.format(ds['name'], ds_status))
                        continue
                    while not ds_status['jobStatus'] == 'COMPLETE':
                        time.sleep(1)
                        ds_status = NitroSession().api_request('dsAddDataSourcesStatus', {"jobId": resp}, retry=0)
                    if len(ds_status['unsuccessfulDatasources'])>0:
                        print('Something went wrong, Datasource {} not added. {}'.format(ds['name'], ds_status['unsuccessfulDatasources'][0]))
                        continue
                    else:
                        ds_to_verify.append(ds['name'])
                        devtree.refresh()

            except Exception:
                print('Something went wrong, Datasource {} not added.\n{}'.format(ds['name'], traceback.format_exc() ))
                continue

        if len(ds_to_verify)>0:
            time.sleep(3)
            devtree.refresh()
            for ds in ds_to_verify:
                if search(ds, devtree):
                    print('DataSource successfully added: {}'.format(ds))
                else:
                    print("Unknown issue occured while adding datasource {} and it was not added.".format(ds))
            
    if pargs.search:
        print(search(pargs.search, devtree))

    if pargs.delete:
        for ds_id in pargs.delete:
            ds = list(devtree.search_ds_group(field='ds_id', term=ds_id))
            if len(ds):
                ds=ds[0]
                if pargs.force or input("Delete the datasource and all the data? \n{}\n[y/n]".format(ds)).lower().startswith('y'):
                    ds.delete()
                else:
                    print("Datasource not deleted")
            else:
                print("Datasource {} not found".format(ds_id))

    if pargs.deleteclients:
        for ds_id in pargs.deletelients:
            ds = list(devtree.search_ds_group(field='ds_id', term=ds_id))
            if len(ds):
                if pargs.force or input("Delete the datasource's clients and all the data. \n{}\n[y/n]".format(ds)).lower().startswith('y'):
                    ds.delete_client()
                else:
                    print("Datasource client not deleted")
            else:
                print("Datasource {} not found".format(ds_id))
        
    if pargs.list:
        print(devtree.get_text(fields=['name', 'ds_ip', 'ds_id', 'parent_id', 'client', 'type_id', 'type','last_time']))
    