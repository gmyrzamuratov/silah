import tweepy
from django.conf import settings
import time
import requests
from requests_oauthlib import OAuth1

class Twitter:

	def splitWords(self, sentence):

		return sentence.split(' ')

	def splitMessage(self, profileName, message):

		counterPlace = 8

		threadWord = "..."

		if len(message) > settings.TWITTER_MAX_SYMBOL_COUNT - counterPlace:
			message = threadWord + message

		splittedTweet = []

		tempMessage = message
		tweetWords = self.splitWords(tempMessage)

		sentence = ""

		for word in tweetWords:

			if len(sentence + ' ' + word) < settings.TWITTER_MAX_SYMBOL_COUNT - counterPlace:
				if len(sentence) == 0:
					if len(splittedTweet) == 0:
						sentence = word
					else:
						sentence = "@%s %s" % (profileName, word)
				else:    
					sentence = sentence + ' ' + word
			else:
				if sentence.strip() != '@' + profileName:
					splittedTweet.append(sentence)
				sentence = "@%s %s" % (profileName, word)
				
		if sentence.strip() != '@' + profileName:
			splittedTweet.append(sentence)

		"""
		splittedByEnterText = message.split('\r\n')

		firstTweet = True

		for tweet in splittedByEnterText:

			if tweet == '':
				continue

			if firstTweet == False:
				tweet = "@%s %s" % (profileName, tweet)

			if len(tweet) > settings.TWITTER_MAX_SYMBOL_COUNT - counterPlace:

				tweetWords = self.splitWords(tweet)

				sentence = ""

				for word in tweetWords:

					if len(sentence + ' ' + word) < settings.TWITTER_MAX_SYMBOL_COUNT - counterPlace:
						if len(sentence) == 0:
							if len(splittedTweet) == 0:
								sentence = word
							else:
								sentence = "@%s %s" % (profileName, word)
						else:    
							sentence = sentence + ' ' + word
					else:
						if sentence.strip() != '@' + profileName:
							splittedTweet.append(sentence)
						sentence = "@%s %s" % (profileName, word)
				
				if sentence.strip() != '@' + profileName:
					splittedTweet.append(sentence)
			else:
				if tweet.strip() != '@' + profileName:
					splittedTweet.append(tweet)

			firstTweet = False
		"""

		count = len(splittedTweet)
		for ind in range(0, count):
			splittedTweet[ind] = splittedTweet[ind] + " [%s/%s]" % (ind + 1, count)

			if threadWord in splittedTweet[ind]:
				splittedTweet[ind] = splittedTweet[ind].replace(threadWord, '')
				splittedTweet[ind] = splittedTweet[ind] + ' ' + threadWord

		return splittedTweet


	def find_punctuation(self, sequence):
		'''
		returns the end point closest to 137 with a punctuation in it
		returns 0 if not found (ie a string with no punctuation in it at all
		'''
		punctuation = '.-,;'
		if len(sequence) <= 137:
			return len(sequence)
		for end in range(136, 0, -1):
			if sequence[end] in punctuation:
				return end +1

		return 0

	def find_space(self, sequence):
		'''
		returns the end point closest to 137 with a space in it
		returns 0 if not found (ie a string with no punctuation in it at all
		'''
		if len(sequence) <= 137:
			return len(sequence)

		for end in range(136, 0, -1):
			if sequence[end] == ' ':
				return end+1

		return 0

	def trim(self, sequence):
		'''
		simple version:  returns a list of strings split on punctuation, closest to
		137
		'''

		result = []
		while sequence:
			end = self.find_punctuation(sequence)
			if not end:
				# ok, no endpoint found so slice at 137, unless the len of the
				# sequence is now shorter
				end = min(137,len(sequence))
			result.append(sequence[0:end].strip())
			sequence = sequence[end:]

		return result

	def splitTweet(self, sequence):
		'''
		slightly smarter version
		slices at punctuation, unless that gives you slices that are shorter than
		100 characters, then try and slice on spaces if it gives you are larger
		slice
		'''
		result = []
		while sequence:
			end = self.find_punctuation(sequence)
			if end < 100 and len(sequence)>200:
				end = max(end, self.find_space(sequence))
			if not end:
				end = min(137,len(sequence))

			result.append(sequence[0:end].strip())
			sequence = sequence[end+1:]

		return result

	def check_status(self, profile, media_id, processing_info):

		oauth = OAuth1(settings.TWITTER_KEY,
			client_secret=settings.TWITTER_SECRET,
			resource_owner_key=profile.access_token,
			resource_owner_secret=profile.client_secret)

		MEDIA_ENDPOINT_URL = 'https://upload.twitter.com/1.1/media/upload.json'
		
		if processing_info is None:
			return

		state = processing_info['state']

		print('Media processing status is %s ' % state)

		if state == u'succeeded':
			return

		if state == u'failed':
			sys.exit(0)

		check_after_secs = processing_info['check_after_secs']

		print('Checking after %s seconds' % str(check_after_secs))

		time.sleep(check_after_secs)

		print('STATUS')

		request_params = {
		'command': 'STATUS',
		'media_id': media_id
		}		

		req = requests.get(url=MEDIA_ENDPOINT_URL, params=request_params, auth=oauth)

		processing_info = req.json().get('processing_info', None)
		self.check_status(profile, media_id, processing_info)

	def uploadImage(self, profile, imagePath):

		auth = tweepy.OAuthHandler(
			settings.TWITTER_KEY,
			settings.TWITTER_SECRET
		)
		auth.set_access_token(
			profile.access_token,
			profile.client_secret
		)

		api = tweepy.API(auth)
		
		return api.media_upload(imagePath)

	def uploadVideo(self, profile, videoPath):

		auth = tweepy.OAuthHandler(
			settings.TWITTER_KEY,
			settings.TWITTER_SECRET
		)
		auth.set_access_token(
			profile.access_token,
			profile.client_secret
		)

		api = tweepy.API(auth)
		
		result = api.upload_chunked(videoPath)
		self.check_status(profile, result.media_id_string, result.processing_info)

		return result

	def publish(self, profile, mainId, tweet, imageList=None, videoList=None):

		auth = tweepy.OAuthHandler(
			settings.TWITTER_KEY,
			settings.TWITTER_SECRET
		)
		auth.set_access_token(
			profile.access_token,
			profile.client_secret
		)

		api = tweepy.API(auth)

		if mainId == None:
			if imageList!=None and len(imageList) > 0 and len(imageList) <= 4:
				return api.update_status(status=tweet, media_ids=imageList)
			elif videoList!=None and len(videoList) > 0:
				return api.update_status(status=tweet, media_ids=videoList)
			else:
				return api.update_status(status=tweet)
		else:
			if imageList!=None and len(imageList) > 0 and len(imageList) <= 4:
				return api.update_status(status=tweet, in_reply_to_status_id=mainId, media_ids=imageList)
			elif videoList!=None and len(videoList) > 0:
				return api.update_status(status=tweet, in_reply_to_status_id=mainId, media_ids=videoList)
			else:
				print(f'Replied to status {mainId}')
				return api.update_status(status=tweet, in_reply_to_status_id=mainId)
