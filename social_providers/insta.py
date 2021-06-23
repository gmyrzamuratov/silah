from instabot import Bot

class Instagram:

	def sendMessage(profile, message, imageList=None, videoList=None):

		bot = Bot()

		bot.login(username = profile.name, password = profile.access_token, is_threaded=True)

		if imageList!=None:
			bot.upload_album(imageList, caption = message)