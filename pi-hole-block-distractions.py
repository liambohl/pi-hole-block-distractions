import time
import schedule
import subprocess
import sys
from datetime import datetime

log_file_name = 'pi-hole-focus.log'
verbose = False

block_list = [
	'youtube.com',
	'googlevideo.com',	# YouTube CDN
	'reddit.com',
	'redditstatic.com',
	'redditmedia.com',
	'redd.it',
	'netflix.com',
	'nflxvideo.net',		# Netflix CDN
	'akamaihd.net',		# Prime Video CDN
	'nebula.tv',
	'nebula.app',
]

# When do we unblock domains (time to veg in the evening)
unblock_hour = 19
unblock_minute = 30
# When do we block domains (time to get ready for bed)
block_hour = 22
block_minute = 0

def log_append(string):
	time_str = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
	log = '{}\n{}\n'.format(time_str, string)
	if (verbose):
		print(log)
	with open(log_file_name, 'a') as log_file:
		log_file.write(log)

def unblock():
	command = 'pihole --regex -nuke'
	completed_process = subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
	log_append(completed_process.stdout)

def block():
	command = 'pihole --regex {}'.format(' '.join(block_list))
	completed_process = subprocess.run(command, shell=True, stderr=subprocess.STDOUT)
	log_append(completed_process.stdout)

def block_or_unblock_first_time():
	now = datetime.today()
	unblock_time_today = now.replace(hour=unblock_hour, minute=unblock_minute, second=0, microsecond=0)
	block_time_today = now.replace(hour=block_hour, minute=block_minute, second=0, microsecond=0)

	unblock()
	if (now < unblock_time_today or block_time_today < now):
		block()

if (__name__ == '__main__'):
	if ('-v' in sys.argv or '--verbose' in sys.argv):
		verbose = True
	block_or_unblock_first_time()

	# schedule.every().day.at(f'{unblock_hour:02d}:{unblock_minute:02d}').do(unblock)
	# schedule.every().day.at(f'{block_hour:02d}:{block_minute:02d}').do(block)
	schedule.every().minute.do(unblock)
	time.sleep(30)
	schedule.every().minute.do(block)

	while(True):
		schedule.run_pending()
		time.sleep(15)