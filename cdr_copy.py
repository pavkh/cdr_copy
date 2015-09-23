#!/usr/bin/env python

import os
import ftplib
import time
conffile="cdr_copy.conf"
cdr_list_local=[]
cdr_list_roam=[]



def config_read(config):
	result = []
	try:
		conf_cursor = open(config,'r');
	except IOError:
		print ("config file "+config + " not found")
		return
	for line in conf_cursor:
		a = line.find('#')
		if a<>-1:
			line = line[0:a:1]
		line = line.rstrip()
		if len(line) > 0:
			key = line.split("=")
			result.append(key)
	result_dict=dict(result)
	conf_cursor.close()
	return result_dict

def ftp_flow(config):
	global cdr_list_local
	global cdr_list_roam
	try:
		ftp_connection=ftplib.FTP(config['ftp_server'])
		ftp_connection.login()
	except Exception:
		print ('Ftp server access error')
		return
	try:
		ftp_connection.cwd(config['ftp_dir'])
	except Exception:
		print ('Ftp directory ' + config['ftp_dir'] + ' was not found on server')
		return
	while 1:
        	ftp_connection.retrlines('NLST ' + config['cdr_wildcard_local']+'*',cdr_list_local.append)
		ftp_connection.retrlines('NLST ' + config['cdr_wildcard_roam'] + '*',cdr_list_roam.append)
		time.sleep(float(config['rescan_time']))
		if len(cdr_list_roam) > 0:
			
		print (cdr_list_roam)
		print (cdr_list_local)


	return



config = config_read(conffile)
ftp_flow(config)
