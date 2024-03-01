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


try:
	open('data_bot/token.txt','r').read()

except:
	os.system('clear')
	token = input('Input Token Bot : ')

	try:
		os.listdir('data_bot')
	except:
		os.system('mkdir data_bot')

	open('data_bot/token.txt','w').write(token)


os.system('nohup python3 bot.py')