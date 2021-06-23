import requests

class Telegram:

	def sendMessage(token, chat_id, message):

		url = f"https://api.telegram.org/bot{token}/sendMessage"
		result = requests.get(url, params={"chat_id": chat_id, 'text': message})
		print("sendMessage:" + result.text)

	def sendPhoto(token, chat_id, file):
	
		url = f"https://api.telegram.org/bot{token}/sendPhoto"
		files = {}
		files["photo"] = open(file, "rb")
		result = requests.get(url, params={"chat_id": chat_id}, files=files)
		print("sendPhoto:" + result.text)

	def sendVideo(token, chat_id, file):
	
		url = f"https://api.telegram.org/bot{token}/sendVideo"
		files = {}
		files["video"] = open(file, "rb")
		result = requests.get(url, params={"chat_id": chat_id}, files=files)
		print("sendVideo:" + result.text)		