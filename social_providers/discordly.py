#import os

from discord_webhook import DiscordWebhook
import ntpath

class Discordly:

	def sendMessage(url, message, imageList=None, videoList=None):

		webhook = DiscordWebhook(url=url, content=message)

		if imageList!=None:
			for image in imageList:

				head, tail = ntpath.split(image)

				with open(image, "rb") as f:
					webhook.add_file(file=f.read(), filename=tail)

		if videoList!=None:
			for video in videoList:

				head, tail = ntpath.split(video)

				with open(video, "rb") as f:
					webhook.add_file(file=f.read(), filename=tail)

		response = webhook.execute()