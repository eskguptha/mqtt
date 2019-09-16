# MQTT Settings 
MQTT_BROKER = "202.153.34.171"
MQTT_PORT = 1883
KEEP_ALIVE_INTERVAL = 45

import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../")))
os.environ['DJANGO_SETTINGS_MODULE'] = 'demo.settings'
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
from django.conf import settings
from django.core.urlresolvers import reverse

import paho.mqtt.client as mqtt
import random, threading, json, time, requests, traceback
from datetime import datetime
import logging

logger = logging.getLogger('mqtt')

class VMMqttAPILog():
	
	def __init__(self, *args, **kwargs):
		self.is_connected = None
		self.mqtt_con = mqtt.Client()
		self.mqtt_con.on_connect = self.on_connect
		self.mqtt_con.on_message = self.on_message
		self.mqtt_con.on_publish = self.on_publish
		self.mqtt_con.on_subscribe = self.on_subscribe
		self.mqtt_con.on_disconnect = self.on_disconnect
		logger.info("***__init__****"*5)
		try:
			self.mqtt_con.connect(settings.MQTT_BROKER, int(settings.MQTT_PORT), int(settings.KEEP_ALIVE_INTERVAL))
			self.is_connected = True
			logger.info("*"*50)
			logger.info("is_connected with MQTT Broker: " + str(settings.MQTT_BROKER))
		except Exception as e:
			logger.info("*"*50)
			logger.info(traceback.format_exc())
			self.is_connected = False
		pass

	def on_connect(self, client, userdata, rc):
		logger.info("on_connect*"*50)
		if rc != 0:
			logger.info("*"*50)
			logger.info('Unable to connect to MQTT Broker...')
			self.is_connected = False
			pass
		else:
			self.is_connected = True
			logger.info("*"*50)
			logger.info("is_connected with MQTT Broker: " + str(settings.MQTT_BROKER))

	def on_publish(self, client, userdata, mid):
		logger.info("hello")
		logger.info("{0} {1} {2} {3}".format(mid, userdata,dir(client), client))
		pass

	def on_subscribe(self, mosq, obj, mid, granted_qos):
		pass

	def on_message(self, mosq, obj, msg):
		# This is the Master Call for saving MQTT Data into DB
		# For details of "sensor_Data_Handler" function please refer "sensor_data_to_db.py"
		logger.info("on_message*"*50)
		logger.info(msg.topic)
		logger.info(msg.payload)


		if msg.topic == 'eSub-issued-Drugs':
			try:
				api_url = reverse('case_sheet_drugs_api')
				url = settings.WEB_API_URL + api_url
				logger.info(url)
				payload = json.loads(msg.payload)
				requests.post(url=url, data=payload, verify=False)
				# todo save log
				logger.info("to do save vm log")
				create_mqttlog(msg.topic,msg.topic,payload,payload["case_number"],"YES","YES")
			except Exception as e:
				logger.info("*"*50)
				logger.info(traceback.format_exc())
				pass
		elif msg.topic == 'eSub-Dispense-Drugs-VM':
			try:
				payload = json.loads(msg.payload)
				create_mqttlog(msg.topic,msg.topic,msg.payload,payload["case_number"],"YES","YES")
				logger.info("to do save vm issue log")
			except Exception as e:
				logger.info(traceback.format_exc())


		else:
			pass
	def on_disconnect(self, client, userdata, rc):
		if rc !=0:
			pass

if __name__ == '__main__':
	vm_obj = VMMqttAPILog()
	# vm_obj.mqtt_con.publish('test', 'hello esk')
	# vm_obj.mqtt_con.subscribe('test')
	if vm_obj.is_connected:
		vm_obj.mqtt_con.subscribe('eSub-issued-Drugs')
		vm_obj.mqtt_con.loop_start()                        #start the loop
		while vm_obj.is_connected != True:    #Wait for connection
			time.sleep(0.1)
		try:
			while True:
				time.sleep(1) 
		except KeyboardInterrupt as e:
			vm_obj.mqtt_con.on_disconnect()
			vm_obj.mqtt_con.loop_stop()
	else:
		print "not connected"
