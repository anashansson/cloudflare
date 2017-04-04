import requests
import json
import urllib
import logger
import sys
import re

class CloudFlare(object):
	"""docstring for CloudFlare"""
	def __init__(self, email, global_key):
		super(CloudFlare, self).__init__()
		self.email = email
		self.global_key = global_key
		
	def getHeader(self):
		return {
			"X-Auth-Email": self.email,
			"X-Auth-Key": self.global_key,
			"Content-Type": "application/json"
		}

	def apiCall(self, method, type = "GET", data = None):
		apiUrl = "https://api.cloudflare.com/client/v4"
		if type == "POST":
			r = requests.post(apiUrl + method, headers = self.getHeader(), data = json.dumps(data))
		elif type == "PUT":
			r = requests.put(apiUrl + method, headers = self.getHeader(), data = json.dumps(data))
		else:
			if data == None:
				r = requests.get(apiUrl + method, headers = self.getHeader())
			else: 
				r = requests.get(apiUrl + method + '?' + urllib.urlencode(data), headers = self.getHeader())

		return json.loads(r.text)


# Initialize
email = raw_input('Enter email: ')
if len(email) < 4:
	logger.fail('Invalid email address') 
	sys.exit()
key = raw_input('Enter global key: ')
if len(key) < 32:
	logger.fail('Invalid global key')
	sys.exit()
ip = raw_input('Enter new IP address: ')
if not re.match('([\d]{1,3}\.){3}[\d]{1,3}', ip):
	logger.fail('Invalid IP address')
	sys.exit()

cf = CloudFlare(email,key)
pages = cf.apiCall('/zones')['result_info']['total_pages']

for page in xrange(0,pages):
	zones = cf.apiCall('/zones','GET', {'page': page})['result']
	
	for zone in zones:
		zone_id = zone['id']

		records = cf.apiCall("/zones/"+zone_id+"/dns_records","GET")['result']

		for record in records:
			if record['type'] == 'A':
				identifier = record['id']

				data = {
					'type': 'A',
					'name': record['name'],
					'content': ip,
					'proxied': record['proxied'],
					'ttl': record['ttl']
				}

				res = cf.apiCall("/zones/"+zone_id+"/dns_records/"+identifier,"PUT",data)['result']

				if res != None:
					logger.success(res['name'])
				else:
					logger.fail(record['name'])