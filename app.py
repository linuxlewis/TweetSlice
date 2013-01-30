import time

twitter_keys = []
app_key = 'blah'
sendgrid_key = 'ok'



def run():
	print 'Starting TweetSlice'

	#start threads

	while True:

		for key in twitter_keys:
			#check maintaince tweets
			pass
		time.sleep(60)

def check_tweet_for_maintaince(tweet):
	pass

def send_email_to_user(user, type, tweet):
	pass

if __name__ == '__main__':
	run()
