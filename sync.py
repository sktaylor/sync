#!/usr/bin/python

import sys
import os
import json
import subprocess

def printConfig():
    from pprint import pprint
    pprint(getConfig())

def getConfig():
    configFile = open(configFilePath())
    config = json.load(configFile)
    configFile.close()

    config["local"] = config.get("local", cwd())
    config["exclude"] = config.get("exclude", [])
    config["excludePush"] = config.get("excludePush", [])
    config["excludePull"] = config.get("excludePull", [])

    if(config.get("remote") == None):
        print("You must have a remote in your config file.")
        exit(1)

    return(config)

def cwd():
    return(os.getcwd())

def configFilePath():
    return(cwd() + '/sync.json')

def main():

    if len(sys.argv) == 1:
        print 'usage: sync.py { push | pull }'
        exit()

    command = sys.argv[1].lower()
    dest = cwd()
    config = getConfig()
    
    runProcess(getRsyncCommand(command, config, True)).wait()

    confirmed = False

    if command == 'push':
	confirmed = confirm("You will replace all remote host data with your data. Are you absolutely sure you want to do this?")
    elif command == 'pull':
        confirmed = confirm("You will replace all your data with the remote host data. Are you absolutely sure you want to do this?")

    if confirmed: 
        runProcess(getRsyncCommand(command, config, False)).wait()
    

def getRsyncCommand(command, config, dryRun):
    
    rsyncCommand = ['rsync', '--verbose', '--progress', '--stats', '--compress', '--recursive', '--backup', '--backup-dir=rsyncBackup~', '--exclude', 'rsyncBackup~', '--links', '--delete', '--times']
    
    if dryRun:
        rsyncCommand.append('--dry-run')
    
    exclude = config['exclude']

    if command == 'push':
        exclude.extend(config['excludePush'])
    elif command == 'pull':
        exclude.extend(config['excludePull'])

    for folder in exclude:
        rsyncCommand.append('--exclude')
        rsyncCommand.append(folder) 

    if command == 'push':
        rsyncCommand.append(config["local"])
        rsyncCommand.append(config["remote"])
    elif command == 'pull':
        rsyncCommand.append(config["remote"])
        rsyncCommand.append(config["local"])

    return(rsyncCommand)
    

def runProcess(psData, filePathToPipe = ''):

    try:
        if filePathToPipe != '':
            fileToPipe = open(filePathToPipe, 'w')
            ps = subprocess.Popen(psData, shell=False, stdout=fileToPipe, stderr=fileToPipe)
        else:
            ps = subprocess.Popen(psData, shell=False)
        
        return(ps)

    except OSError as e:
        print("There was a problem starting the rsync process. Error: " + e.msg)        
        exit()


def confirm(prompt=None, resp=False):

    if prompt is None:
        prompt = 'Confirm'

    if resp:
        prompt = '%s (%s/%s): ' % (prompt, 'Y', 'n')
    else:
        prompt = '%s (%s/%s): ' % (prompt, 'N', 'y')
        
    while True:
        ans = raw_input(prompt)
        if not ans:
            return resp
        if ans not in ['y', 'Y', 'n', 'N']:
            print 'please enter y or n.'
            continue
        if ans == 'y' or ans == 'Y':
            return True
        if ans == 'n' or ans == 'N':
            return False

main()

