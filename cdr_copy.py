#!/usr/bin/env python

import os
import ftplib
import time
import shutil
import glob
conffile="cdr_copy.conf"
cdr_list_local=[]
cdr_list_roam=[]


def config_read(config_file):
	result = []
	try:
		conf_cursor = open(config_file,'r');
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

def log(message):
	message =  time.strftime("%d-%m-%Y %H:%M:%S: ", time.localtime()) + message + '\n'
	print message
	try:
		logfile = open('logs/cdr_copy.log', 'a')
		logfile.write(message)
	except Exception:
		print 'Cannot open logfile'
		return
	finally:
		logfile.close()
		return




def movefiles(config):
	cdr_list_roam=glob.glob('tmp/' + config['cdr_wildcard_roam'] + '*')
	cdr_list_local=glob.glob('tmp/' + config['cdr_wildcard_local'] + '*')
	if len(cdr_list_roam) > 0:
		for filename in cdr_list_roam:
			log ('Moving ' + filename + ' to BRT roam('+config['brt_dir_roam']+')')
			shutil.move(filename,config['brt_dir_roam'])
	if len(cdr_list_local) > 0:
		for filename in cdr_list_local:
			log ('Moving ' + filename + ' to BRT local('+config['brt_dir_local']+')')
			shutil.move(filename,config['brt_dir_local'])

	return

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
		log ('Scanning \"' + config['ftp_dir'] + '\" folder on ftp server for CDR files')
		ftp_connection.retrlines('NLST ' + config['cdr_wildcard_local']+'*',cdr_list_local.append)
		ftp_connection.retrlines('NLST ' + config['cdr_wildcard_roam'] + '*',cdr_list_roam.append)

		if len(cdr_list_roam) > 0:
			for filename in cdr_list_roam:
				log ('Processing '+filename)
				ftp_connection.retrbinary('RETR '+filename,open('tmp/'+filename,'wb').write)
				ftp_connection.delete(filename)
		if len(cdr_list_local) > 0:
			for filename in cdr_list_local:
				log ('Processing '+filename)
				ftp_connection.retrbinary('RETR '+filename,open('tmp/'+filename,'wb').write)
				ftp_connection.delete(filename)
		movefiles(config)
		cdr_list_local=[]
		cdr_list_roam=[]
		time.sleep(float(config['rescan_time']))


	return



config = config_read(conffile)
ftp_flow(config)
