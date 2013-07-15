import sane
import types
import sys
import os
import tools
import time
import gtk
import multiprocessing
from multiprocessing import Pipe
class scan_image(tools.lios_tools):
	def init_scanner(self):
		sane_version = sane.init()
		result = multiprocessing.Queue()
		init_process=multiprocessing.Process(target=self.get_the_devices,args=(result,))
		init_process.start()
		while init_process.is_alive():
			pass
		sane_devices = result.get()
		
		if sane_devices == []:
			self.keep_running = False
			self.notify("Scanner Not Detected!",True,0,True)
		else:
			for device in sane_devices:
				print "Device : ",device[2]
				if device[2] == "(unknown model)":
					self.notify("Unknown model! Or Busy please repin the scanner, and try again!",True,0,True)
					self.keep_running = False				
				try:
					self.scanner = sane.open(device[0])
				except _sane.error:
					self.notify("Sane Error Or Busy! Please repin the scanner, and try again!",True,0,True)				
				else:
					pass
				break
		options = self.scanner.get_options()
		self.scanner.mode="Color"
		self.mode="Color"
		try:
			self.scanner.mode = "Gray"
		except:
			pass
		else:
			self.mode = "Gray"

		try:
			self.scanner.mode = "Binary"
		except:
			pass
		else:
			self.mode = "Binary"

		try:
			self.scanner.mode = "Lineart"
		except:
			pass
		else:
			self.mode = "Lineart"		
		options = self.get_scanner_option (self.scanner, 'br-x')
		self.scanner.br_x = options[8][1]
		self.br_x = options[8][1]
		options = self.get_scanner_option(self.scanner, 'br-y')
		self.br_y_pass = options[8][1]
		
		
		options = self.get_scanner_option (self.scanner, 'brightness')
		if options:
			self.light_parameter_state = True
			self.light_parameter = "--brightness"
				
		options = self.get_scanner_option (self.scanner, 'threshold')
		if options:
			self.light_parameter = '--threshold'
			self.light_parameter_state = True
			if type(options[8]) == types.ListType:
				min =  options[8][0]
				max = options[8][-1]
			else:
				min =  options[8][0]
				max = options[8][1]
			self.vary = max-min
		print "Inetialising Scanner      	  [ Ok ]"


	def get_the_devices(self,result):
		result.put(sane.get_devices())
	
		
		
	def check_brightness_support(self):
		try:
			options = self.get_scanner_option (self.scanner, 'brightness')
		except sane._sane.error:
			self.init_scanner()
		else:
			pass
		if options:
			self.notify("Brightness option available for your scanner!",False,None,True)
		else:
			options = self.get_scanner_option (self.scanner, 'threshold')
			if options:
				self.notify("Threshold option available for your scanner!",True,None,True)
			else:
				self.notify("Sorry! brightness or threshold options are not available for your scanner!",False,0,True)
				self.keep_running = False
				 
		
	def get_scanner_option (self,scanner, name):
		options = self.scanner.get_options()
		for option in options:
			if option[1] == name:
				return option
		return False
		
	def scan_image(self,file_name,resolution,brightness,region):
		if region == 0:
			self.br_y = self.br_y_pass
		elif region == 1:
			self.br_y = 3*(self.br_y_pass/4)			
		elif region == 2:
			self.br_y = self.br_y_pass/2
		elif region == 3:
			self.br_y = self.br_y_pass/4	
		else:
			pass
			
		if brightness != None:
			if self.light_parameter == "--brightness":
				self.brightness = brightness
			if self.light_parameter == '--threshold':
				if self.vary	== 100:
					self.brightness = brightness
				else:
					self.brightness = brightness+100
		print "\n1\n"			
		if self.scanner_driver == 0:
			try:
				if brightness != None:
					if self.light_parameter == "--brightness":
						try:
							self.scanner.brightness = brightness
						except AttributeError:
							print "ooh"
						else:
							pass
					if self.light_parameter == '--threshold':
						if self.vary == 100:
							self.brightness = brightness
							try:
								self.scanner.threshold = brightness
							except AttributeError:
								print "Ohhh "
							else:
								pass
						else:
							self.brightness = brightness+100
							try:
								self.scanner.threshold = brightness+100
							except AttributeError:
								print "Ohhh 100"
							else:
								pass
				self.scanner.resolution = resolution
				self.scanner.br_y = self.br_y
				pil_image = self.scanner.scan()#.convert('L')
			except sane._sane.error, err:
				dialog =  gtk.Dialog("Lios Scanner Error!",("Close" ,gtk.RESPONSE_CLOSE))
				lbl = gtk.Label("Sorry scanner driver error!. Please change your Scanner Driver!!")
				lbl.show()
				dialog.vbox.pack_start(lbl)                             						
				response = dialog.run()
				if response == gtk.RESPONSE_CLOSE:
					dialog.destroy()
					self.notify("Closing",False,None,True)
					self.keep_running = False
			else:
				pil_image.save("%s.png" % (file_name))
				os.system("convert %s.png %s.pnm " % (file_name,file_name))
		else:
			self.scanner.close()
			print "\n2\n"
			if self.light_parameter_state == True:
				os.system("scanimage --resolution %s --mode %s -x %s -y %s %s %s > %s.pnm" % (resolution,self.mode,self.br_x,self.br_y,self.light_parameter,self.brightness,file_name))	
			else:
				os.system("scanimage --resolution %s --mode %s -x %s -y %s > %s.pnm" % (resolution,self.mode,self.br_x,self.br_y,file_name))
			print "\n3\n"		

