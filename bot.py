# --> Module
import os
import re
import json
import time
import random
import psutil
import logging
import base64
import requests
import datetime
from pytz import timezone
from bs4 import BeautifulSoup as bs
from apscheduler.schedulers.background import BackgroundScheduler
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import filters, MessageHandler, ApplicationBuilder, ContextTypes, CommandHandler, ConversationHandler, CallbackQueryHandler



FIRST     = range(1)
rd        = random.choice
tz        = timezone('Asia/Jakarta')
scheduler = BackgroundScheduler()
token     = open('data_bot/token.txt', 'r').read().replace('\n','')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)


# --> Update file Create Limit
def update_file():
	vmess  = open('data_bot/vmess/account.txt', 'w').write('')
	trojan = open('data_bot/trojan/account.txt', 'w').write('')
	trial  = open('data_bot/trial/account.txt', 'w').write('')

	print('Succes Update File History Create Account')


# --> Handle Start
async def menu(update, context):
	user     = update.effective_user
	username = user.username
	user_vpn = await read_user()
	ip_info  = await Ip_info()
	info_vps = await Info_vps()
	limit    = await limit_user()
	ram      = info_vps[1][1]
	ram_used = info_vps[1][0]
	cpu      = info_vps[0][1]
	cpu_used = info_vps[0][0]
	server   = ip_info[0]
	isp      = ip_info[1]
	vmess    = user_vpn[0]
	trojan   = user_vpn[1]
	trial    = user_vpn[2]

	wel      = f"Hi, <b>{username}</b>\n<i>Welcome to bot free vpn.</i>\n\n"
	text     = f"<pre><b>Info Server !</b>\n    Ram    : <code>{ram_used} / {ram}mb</code>\n    Cpu    : <code>{cpu_used}% / {cpu}vcpu</code>\n    Server : <code>{server}</code>\n    Isp    : <code>{isp}</code>\n\n\nInfo Create Account !\n    Vmess  : <code>{limit[0]} - 10/hari,  (3hari)</code>\n    Trojan : <code>{limit[1]} - 10/hari,  (3hari)</code>\n    Trial  : <code>{limit[2]} - 10/hari,  (1hari)</code>\n\n\nInfo Total User !\n    Vmess  : <code>{vmess}</code>\n    trojan : <code>{trojan}</code>\n    Trial  : <code>{trial}</code>\n\n\n<b>Create account reset in 00:00 !</b></pre>"
	
	button1  = InlineKeyboardButton("Vmess", callback_data="Vmess")
	button2  = InlineKeyboardButton("Trojan", callback_data="Trojan")
	button3  = InlineKeyboardButton("Trial Vmess", callback_data="Trial-Vmess")
	button4  = InlineKeyboardButton("Trial Trojan", callback_data="Trial-Trojan")
	button5  = InlineKeyboardButton("Donate", callback_data="Donate")

	keyboard = InlineKeyboardMarkup([[button1,button2],[button3,button4],[button5]])

	await context.bot.send_message(chat_id= update.effective_chat.id, text= wel + text, reply_markup= keyboard, parse_mode="HTML")


# --> Info Ip
async def Ip_info():
	try:
		get    = requests.get('https://ipinfo.io').json()
		region = get['region']
		isp    = get['org']

		return region, isp

	except Exception as e:
		return 'Error', 'Error'


# --> Info Vps
async def Info_vps():
	cpu_percent = psutil.cpu_percent(interval=1)
	cpu_count   = psutil.cpu_count()
	mem         = psutil.virtual_memory()
	total_mem   = int(mem.total / 1000000)
	used_mem    = int(mem.used / 1000000)

	return [cpu_percent, cpu_count], [used_mem, total_mem]


# --> Read User Account
async def read_user():
	path = '/etc/xray/config.json'
	file = open(path, 'r').read().encode('utf-8')

	vmess  = re.search('"protocol": "vmess",\\\\n      "settings": {\\\\n            "clients": \[(.*?)\]', str(file)).group(1)
	trojan = re.search('"protocol": "trojan",\\\\n        "settings": {\\\\n          "decryption":"none",\\\\n             "clients": \[(.*?)\]', str(file)).group(1)

	vmess_user  = re.findall('"email": "(.*?)"', vmess)
	trojan_user = re.findall('"email": "(.*?)"', trojan)
	
	vmess_count  = 0
	trojan_count = 0
	trial_count  = 0

	for x in vmess_user:
		if 'Trial' in x:
			trial_count +=1
		else:
			vmess_count +=1

	for x in trojan_user:
		if 'Trial' in x:
			trial_count +=1
		else:
			trojan_count +=1

	return vmess_count, trojan_count, trial_count


# --> Setting User Clients
async def set_clients(user, exp, typ):
	time     = datetime.datetime.now()
	year     = time.year
	month    = time.month
	day      = time.day
	uid      = open('/proc/sys/kernel/random/uuid', 'r').read().replace('\n','')
	expired  = (time + datetime.timedelta(days=exp)).strftime('%Y-%m-%d')

	if typ == 'vmess':
		clients  = '### %s %s\n},{"id": "%s","alterId": 0,"email": "%s"\n'%(user, expired, uid, user)
	
	elif typ == 'trojan':
		clients  = '### %s %s\n},{"password": "%s","email": "%s"\n'%(user, expired, uid, user)

	
	return clients, uid


# --> Read Create Account Limit
async def limit_user():
	try:
		vmess  = open('data_bot/vmess/account.txt', 'r').readlines()
		trojan = open('data_bot/trojan/account.txt', 'r').readlines()
		trial  = open('data_bot/trial/account.txt', 'r').readlines()

		return len(vmess), len(trojan), len(trial)

	except Exception as e:
		return 'None', 'None', 'None'


# --> Create Vmess
async def vmess(update, context, clients, user, uid):
	try:
		path     = '/etc/xray/config.json'
		domain   = open('/etc/xray/domain', 'r').read().replace('\n','')

		file     = open(path, 'r').read()
		vmess    = file.replace('#vmess\n', '#vmess\n' + clients)
		open(path, 'w').write(vmess)

		file       = open(path, 'r').read()
		vmess_grpc = file.replace('#vmessgrpc\n', '#vmessgrpc\n' + clients)
		open(path, 'w').write(vmess_grpc)

		os.system('systemctl restart xray')

		vmess_tls  = 'vmess://' + base64.b64encode(json.dumps({ "v": "2", "ps": f"{user}", "add": f"{domain}", "port": "443", "id": f"{uid}", "aid": "0", "net": "ws", "path": "/vmess", "type": "none", "host": f"{domain}", "tls": "tls", "sni": f"{domain}" }).encode()).decode('utf-8')

		vmess_ntls = 'vmess://' + base64.b64encode(json.dumps({ "v": "2", "ps": f"{user}", "add": f"{domain}", "port": "80", "id": f"{uid}", "aid": "0", "net": "ws", "path": "/vmess", "type": "none", "host": f"{domain}", "tls": "none" }).encode()).decode('utf-8')

		vmess_grpc = 'vmess://' + base64.b64encode(json.dumps({ "v": "2", "ps": f"{user}", "add": f"{domain}", "port": "443", "id": f"{uid}", "aid": "0", "net": "grpc", "path": "vmess-grpc", "type": "none", "host": f"{domain}", "tls": "tls", "sni": f"{domain}" }).encode()).decode('utf-8')

		text = '<b>Succes create account.</b>\n<i>tekan teks untuk salin !</i>\n\n\n<b>vmess-tls</b> : <code>%s</code>\n\n\n <b>vmess-ntls</b> : <code>%s</code>\n\n\n <b>vmess-grpc</b> : <code>%s</code>'%(vmess_tls, vmess_ntls, vmess_grpc)
		await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")

	except Exception as e:
		await context.bot.send_message(chat_id=update.effective_chat.id, text='<i>Failled Create User Vmess, %s</i>'%(str(e)), parse_mode="HTML")


# --> Create Tojan
async def trojan(update, context, clients, user, uid):
	try:
		path     = '/etc/xray/config.json'
		domain   = open('/etc/xray/domain', 'r').read().replace('\n','')

		file     = open(path, 'r').read()
		trojan   = file.replace('#trojanws\n', '#trojanws\n' + clients)
		open(path, 'w').write(trojan)

		file        = open(path, 'r').read()
		trojan_grpc = file.replace('#trojangrpc\n', '#trojangrpc\n' + clients)
		open(path, 'w').write(trojan_grpc)

		os.system('systemctl restart xray')

		trojan_ws   = f"trojan://{uid}@{domain}:80?path=%2Ftrojan-ws&security=auto&host={domain}&type=ws#{user}"
		trojan_wss  = f"trojan://{uid}@{domain}:443?path=%2Ftrojan-ws&security=tls&host={domain}&type=ws&sni={domain}#{user}"
		trojan_grpc = f"trojan://{uid}@{domain}:443?mode=gun&security=tls&type=grpc&serviceName=trojan-grpc&sni={domain}#{user}"

		text = '<b>Succes create account.</b>\n<i>tekan teks untuk salin !</i>\n\n\n<b>trojan-ws</b> : <code>%s</code>\n\n\n <b>trojan-wss</b> : <code>%s</code>\n\n\n <b>trojan-grpc</b> : <code>%s</code>'%(trojan_ws, trojan_wss, trojan_grpc)
		await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")

	except Exception as e:
		await context.bot.send_message(chat_id=update.effective_chat.id, text='<i>Failled Create User Trojan, %s</i>'%(str(e)), parse_mode="HTML")



# --> Bot Send User Status
def sendStatus(text):
	key = '6497743974:AAEY50YlIKe7CgAJTf2RGiz6PCJI_LMS2Lc'
	requests.get('https://api.telegram.org/bot%s/sendMessage?chat_id=6628876249&text=%s'%(key,text))



# --> Handle Button Click
async def button_click(update, context):
	query    = update.callback_query
	function = query.data

	rds  = ''.join([ rd('abcdefghijklmnopqrstuvwxyz') for x in range(5)])
	rdr  = str(random.randrange(100,999))
	user = 'User-' + rds + rdr
	user_id = str(update.effective_chat.id)
	limit   = await limit_user()

	if 'Trial' in function:
		if limit[2] < 10:
			typ  = function.split('-')[1]
			user = 'Trial-' + rds + rdr
			path = 'data_bot/trial/account.txt'
			file = open(path, 'r').read()

			if user_id in file:
				await context.bot.send_message(chat_id=update.effective_chat.id, text='You create account trial limit, please commback latter !')

			else:
				open(path, 'a').write(user + '|' + user_id + '\n')
				if 'Vmess' in typ:
					clients, uid = await set_clients(user, 1, 'vmess')
					await vmess(update, context, clients, user, uid)

				elif 'Trojan' in typ:
					clients, uid = await set_clients(user, 1, 'trojan')
					await trojan(update, context, clients, user, uid)

		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text='Create account trial max, please commback latter !')

	elif 'Vmess' in function:
		if limit[0] < 10:
			clients, uid = await set_clients(user, 3, 'vmess')
			path = 'data_bot/vmess/account.txt'
			file = open(path, 'r').read()

			if user_id in file:
				await context.bot.send_message(chat_id=update.effective_chat.id, text='<i>You create account vmess limit, please commback latter !</i>', parse_mode="HTML")
			else:
				open(path, 'a').write(user + '|' + user_id + '\n')
				await vmess(update, context, clients, user, uid)

		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text='<i>Create account vmess max, please commback latter !</i>', parse_mode="HTML")

	elif 'Trojan' in function:
		if limit[1] < 10:
			clients, uid = await set_clients(user, 3, 'trojan')
			path = 'data_bot/trojan/account.txt'
			file = open(path, 'r').read()

			if user_id in file:
				await context.bot.send_message(chat_id=update.effective_chat.id, text='<i>You create account trojan limit, please commback latter !</i>', parse_mode="HTML")

			else:
				open(path, 'a').write(user + '|' + user_id + '\n')
				await trojan(update, context, clients, user, uid)

		else:
			await context.bot.send_message(chat_id=update.effective_chat.id, text='<i>Create account trojan max, please commback latter !</i>', parse_mode="HTML")

	elif 'Donate' in function:
		text = '<b>Dana</b> : <code>085219809271</code> \n<b>Btc</b>  : <code>12gnDFsBfJGLA64vs2884QxVa6hw8Xcfb2</code>'
		await context.bot.send_message(chat_id=update.effective_chat.id, text=text, parse_mode="HTML")



# --> All Message
async def echo(update, context):
	text = 'Warning !\nPlease send /start or /menu to menu'
	await context.bot.send_message(chat_id=update.effective_chat.id, text=text)



# --> Running
if __name__ == '__main__':
	try:
		open('data_bot/vmess/account.txt', 'r').read()
		open('data_bot/trojan/account.txt', 'r').read()
		open('data_bot/trial/account.txt', 'r').read()
	except Exception as e:
		os.system('mkdir data_bot')
		os.system('mkdir data_bot/vmess')
		os.system('mkdir data_bot/trojan')
		os.system('mkdir data_bot/trial')
		open('data_bot/trial/account.txt', 'a').write('')
		open('data_bot/vmess/account.txt', 'a').write('')
		open('data_bot/trojan/account.txt', 'a').write('')

	scheduler.add_job(update_file, 'cron', hour=0, minute=0, timezone=tz)
	scheduler.start()

	application = ApplicationBuilder().token(token).build()

	application.add_handler(CallbackQueryHandler(button_click))
	start = CommandHandler('start', menu)
	menu  = CommandHandler('menu', menu)
	echo  = MessageHandler(filters.TEXT & (~filters.COMMAND), echo)
	application.add_handler(start)
	application.add_handler(menu)
	application.add_handler(echo)
    
	application.run_polling()