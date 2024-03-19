try:
	import os
	import psutil
	from pytz import timezone
	from bs4 import BeautifulSoup as bs
	from apscheduler.schedulers.background import BackgroundScheduler
	from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile

except Exception as e:
	import os
	os.system('apt install python3-pip -y')
	os.system('pip3 install bs4')
	os.system('pip3 install psutil')
	os.system('pip3 install apscheduler')
	os.system('pip3 install python-telegram-bot')



os.system('clear')
token = input('Input Token Bot : ')
owner = input('Input Owner Username : ')

try:
	os.listdir('data_bot')
except:
	os.system('mkdir data_bot')

open('data_bot/token.txt','w').write(token)
open('data_bot/owner.txt','w').write(owner)

ctl  = open('/etc/rc.local', 'r').read()
text = ctl.replace('exit 0', 'python3 /root/bot.py & \n\nexit 0')

open('/etc/rc.local', 'w').write(text)
os.system('chmod +x /etc/rc.local')
os.system('clear')

print('Succes Setup Bot Telegram!\n Server akan di reboot, Jika token valid, bot akan langsung berjalan')
os.system('systemctl reboot')
