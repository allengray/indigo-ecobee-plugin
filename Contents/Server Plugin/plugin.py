from pyecobee import Ecobee, config_from_file
import sys
import json
import indigo

DEBUG=False
ACCESS_TOKEN_PLUGIN_PREF='accessToken'
AUTHORIZATION_CODE_PLUGIN_PREF='authorizationCode'
REFRESH_TOKEN_PLUGIN_PREF='refreshToken'

class IndigoLogger:
	def write(self, text):
		indigo.server.log(text)

class Plugin(indigo.PluginBase):

	def __init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs):
		indigo.PluginBase.__init__(self, pluginId, pluginDisplayName, pluginVersion, pluginPrefs)
		self.debug = DEBUG

		# redirect stdout to Indigo log
		sys.stdout = IndigoLogger()

		tmpconfig = {'API_KEY': "qyy0od74EpMz2P8X1fmAfyoxKod4t1Fo"}
		if ACCESS_TOKEN_PLUGIN_PREF in pluginPrefs:
			tmpconfig['ACCESS_TOKEN'] = pluginPrefs[ACCESS_TOKEN_PLUGIN_PREF]
		if AUTHORIZATION_CODE_PLUGIN_PREF in pluginPrefs:
			tmpconfig['AUTHORIZATION_CODE'] = pluginPrefs[AUTHORIZATION_CODE_PLUGIN_PREF]
		if REFRESH_TOKEN_PLUGIN_PREF in pluginPrefs:
			tmpconfig['REFRESH_TOKEN'] = pluginPrefs[REFRESH_TOKEN_PLUGIN_PREF]
		indigo.server.log(u"constructed config: %s" % json.dumps(tmpconfig))

		# Create an ecobee object with the config dictionary
		indigo.server.log(u"initializing ecobee module")
		self.ecobee = Ecobee(config = tmpconfig)
		indigo.server.log(u"ecobee module initialized")

		self.pluginPrefs["pin"] = self.ecobee.pin
		self.pluginPrefs["authorizationCode"] = self.ecobee.authorization_code


	def __del__(self):
		indigo.PluginBase.__del__(self)

	def startup(self):
		indigo.server.log(u"startup called")

	def shutdown(self):
		indigo.server.log(u"shutdown called")

	def request_pin(self, valuesDict = None):
		indigo.server.log(u"requesting pin")
		self.ecobee.request_pin()
		indigo.server.log(u"received pin: %s" % self.ecobee.pin)
		valuesDict['pin'] = self.ecobee.pin
		return valuesDict

	def open_browser_to_ecobee(self, valuesDict = None):
		self.browserOpen("http://www.ecobee.com")

	def refresh_credentials(self, valuesDict = None):
		self.ecobee.request_tokens()
		self._get_keys_from_ecobee(valuesDict)
		self.ecobee.update()
		indigo.server.log(json.dumps(self.ecobee.thermostats))

	def get_remote_sensors(self, filter="", valuesDict=None, typeId="", targetId=0):
		self.ecobee.update()
		remote_sensors = self.ecobee.get_remote_sensors(0)

		indigo.server.log(u"all remote sensors: %s" % json.dumps(remote_sensors))

		menuItems = []
		for rs in remote_sensors:
			indigo.server.log(u"remote sensor: %s" % rs)
			menuItems.append((rs.get('code'), rs.get('name')))
		return menuItems

	def _get_keys_from_ecobee(self, valuesDict):
		valuesDict[ACCESS_TOKEN_PLUGIN_PREF] = self.ecobee.access_token
		valuesDict[AUTHORIZATION_CODE_PLUGIN_PREF] = self.ecobee.authorization_code
		valuesDict[REFRESH_TOKEN_PLUGIN_PREF] = self.ecobee.refresh_token
		return valuesDict

	def runConcurrentThread(self):
		try:
			while True:
				for dev in indigo.devices.iter("self"):
					if not dev.enabled:
						continue

					# Plugins that need to poll out the status from the thermostat
					# could do so here, then broadcast back the new values to the
					# Indigo Server.
					# self._refreshStatesFromHardware(dev, False, False)

				self.sleep(3)
		except self.StopThread:
			pass	# Optionally catch the StopThread exception and do any needed cleanup.
