import time
import smtplib
from twitter import *
from datetime import datetime
import re
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText
from email.utils import formataddr, formatdate
from jinja2 import Environment, PackageLoader


consumer_key = 'Wx2lGU5aLowSXDxFNmMBzg'
consumer_secret = 'pF9BYbosXaRZQaIORc4KNviY29LbtOBdEyfJmaAXnwA'

oauth_token = '1135522998-RMEw1Z7MSmv3yWkFM3TszQX0MzWdkGOpmykVw1e'
oauth_secret = 'ZxZ1ey5qyoUmpV5etMXfm3CktukaM2mVdCAkxIGgo'

twitter_keys = []
app_key = 'blah'
sendgrid_key = 'ok'

types = ['washer', 'dryer', 'toilet', 'sink', 'dishwasher', 'broken']

user = {'email':'sam@livelovely.com', 'name':'Sam Bolgert'}

def run():
	print 'Starting TweetSlice'
	#start threads
	last_tweet = None
	while True:
	#create twitter
		t = Twitter(
			auth=OAuth(oauth_token, oauth_secret,
				consumer_key, consumer_secret)
		)
		tweets = t.statuses.mentions_timeline()

		#for tweets from old to new
		for tweet in tweets:
			print 'Checking Tweets'
			#if tweet is new
			created_at = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')
			if last_tweet is None or created_at > last_tweet:
				check_tweet_for_maintaince(tweet)
				last_tweet = created_at
		time.sleep(60)

def check_tweet_for_maintaince(tweet):
	if tweet['in_reply_to_status_id_str'] is None:
		urgent = False
		for hash in tweet['entities']['hashtags']:
			if hash['text'] == 'asap':
				print 'Urgent Tweet Found!'
				urgent = True
				break

		#search for other types
		#if main is True:
		email = False
		for type in types:
			match = re.search(type, tweet['text'])
			if match is not None:
				print 'Type Email Sent'
				send_email_to_user(user, type, tweet, urgent)
				email = True
				break

		if email is False:
			send_email_to_user(user, '', tweet, urgent)

def send_email_to_user(user, type, tweet, urgent=False):
	print 'Sending Email'
	c = dict()
	c['type'] = type
	c['name'] = tweet['user']['name']
	c['text'] = tweet['text']
	if tweet['entities'].has_key('media'):
		c['photourl'] = tweet['entities']['media'][0]['media_url_https']
	env = Environment(loader=PackageLoader('tweetslice', 'templates'))
	tmp = env.get_template('general.html')
	html = tmp.render({'c':c})
	#html = render('/messages/alert.html')
	from_ad = '%s+%s@maintenance.livelovely.com' % (str(tweet['user']['screen_name']), str(tweet['id_str']))

	if urgent is False:
		subject = "Request to fix %s's maintenance issue" % (tweet['user']['name'])
	else:
		subject = "URGENT: Request to fix %s's maintenance issue " % (tweet['user']['name'])
	_sendHtmlEmail(from_ad, user['email'], subject ,None, html, 'Lovely Maintenance', user['name'])

def _sendHtmlEmail(fromAddress, toAddress, title, textMessage, htmlMessage, fromName=None, toName=None, attachments=None, ignoreOverride=False, sender=None):

	header_charset = 'ISO-8859-1'
	bodyCharsets = 'US-ASCII', 'ISO-8859-1', 'UTF-8'

	#Encode to and From Names
	if fromName is not None:
		fromName = str(Header(unicode(fromName), header_charset))

	if toName is not None:
		toName = str(Header(unicode(toName), header_charset))

	#Encode the text and html bodies
	if textMessage is not None:
		for textCharset in bodyCharsets:
			try:
				textMessage.encode(textCharset)
			except UnicodeError:
				pass
			else:
				break

	for htmlCharset in bodyCharsets:
		try:
			htmlMessage.encode(htmlCharset)
		except UnicodeError:
			pass
		else:
			break

	#Encode the email addresses
	fromAddress = fromAddress.encode('ascii')
	toAddress = toAddress.encode('ascii')

	#Create the message
	message = MIMEMultipart("alternative")

	#Add the encoded subject
	message["Subject"] = Header(unicode(title), header_charset)

	#Add the Date Header
	message["Date"] = formatdate(localtime=True)

	#Add the from address
	if fromName is None:
		message["From"] = fromAddress
	else:
		message["From"] = formataddr((fromName, fromAddress))

	#Add the to address
	if toName is None:
		message["To"] = toAddress
	else:
		message["To"] = formataddr((toName, toAddress))

	#do the headers
	if sender is not None:
		message.add_header('Sender', sender)
		message.add_header('Return-Path', sender)

	#Add the text body
	if textMessage is not None:
		textPart = MIMEText(textMessage.encode(textCharset), 'plain', textCharset)
		message.attach(textPart)

	#Add the html body
	htmlPart = MIMEText(htmlMessage.encode(htmlCharset), 'html', htmlCharset)
	message.attach(htmlPart)

	#Add the attachments
	if attachments is not None:
		for attachment in attachments:
			a = MIMEApplication(attachment[0])
			a.add_header('Content-Disposition', 'attachment', filename=attachment[1])
			message.attach(a)

	#Send the message
	session = smtplib.SMTP('smtp.sendgrid.net')
	session.login('doug@homeboodle.com', '88gg88')
	smtpResult = session.sendmail(fromAddress, toAddress, message.as_string())

	print 'made it'

	#Quit the session
	session.quit()

if __name__ == '__main__':
	run()
