import os
import shutil
import gtk
import pango
import gobject
import enchant
from subprocess import *
from espeak import espeak
import ConfigParser
class lios_preferences:
	# FUNCTION TO Read PREFERENCES #
	def read_preferences(self):
		config = ConfigParser.ConfigParser()
		if config.read('%s/Lios/.preferences.cfg'%(os.environ['HOME'])) != []:
			try:
				self.time_between_repeated_scanning=int(config.get('cfg',"time_between_repeated_scanning"))
				self.scan_resolution=int(config.get('cfg',"scan_resolution"))
				self.scan_brightness=int(config.get('cfg',"scan_brightness"))
				self.ocr_engine=config.get('cfg',"ocr_engine")
				self.scan_area=int(config.get('cfg',"scan_area"))
				self.auto_skew=int(config.get('cfg',"auto_skew"))			
				self.language=config.get('cfg',"language")
				self.number_of_pages_to_scan=int(config.get('cfg',"number_of_pages_to_scan"))#pages
				self.mode_of_rotation = int(config.get('cfg',"mode_of_rotation"))
				self.rotation_angle = int(config.get('cfg',"angle"))		
				self.page_numbering_type=int(config.get('cfg',"numbering_type"))
				self.scanner_driver=int(config.get('cfg',"scanner_driver"))						
				self.starting_page_number=int(config.get('cfg',"starting_page_number"))
				self.background_color=config.get('cfg',"background_color")
				self.font_color=config.get('cfg',"font_color")
				self.highlight_color=config.get('cfg',"highlight_color")
				self.background_highlight_color=config.get('cfg',"highlight_background_color")
				self.font=config.get('cfg',"font")
				self.highlight_font=config.get('cfg',"highlight_font")
				self.voice_message_state=int(config.get('cfg',"voice_message_state"))
				self.voice_message_voice=int(config.get('cfg',"voice_message_voice"))
				self.voice_message_rate=int(config.get('cfg',"voice_message_rate"))
				self.voice_message_volume=int(config.get('cfg',"voice_message_volume"))
				self.voice_message_pitch=int(config.get('cfg',"voice_message_pitch"))
				self.cam_take_time=int(config.get('cfg',"cam_take_time"))
				self.cam_waitkey=int(config.get('cfg',"cam_waitkey"))
				self.cam_device=int(config.get('cfg',"cam_device"))				
				self.mode_switch = True
			except ConfigParser.NoOptionError:
				self.on_Restore_preferences_activate(self,data=None)
		else:
			self.on_Restore_preferences_activate(self,data=None)
			

	def on_Save_preferences_activate(self,wedget,data=None):
		save_preferences = gtk.FileChooserDialog(title="save_preferences as ",action=gtk.FILE_CHOOSER_ACTION_SAVE,
		                     buttons=(gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		save_preferences.set_current_folder("%s/Lios"%(os.environ['HOME']))
		response = save_preferences.run()		
		if response == gtk.RESPONSE_OK:
			shutil.copy2("%s/Lios/.preferences.cfg"%(os.environ['HOME']),"%s.cfg"%(save_preferences.get_filename()))
			self.notify("preferences saved as %s.cfg" % (save_preferences.get_filename()),False,None,True)
		save_preferences.destroy()



	def on_Load_preferences_activate(self,wedget,data=None):
		load_preferences = gtk.FileChooserDialog("Select the image",None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
		load_preferences.set_default_response(gtk.RESPONSE_OK)
		load_preferences.set_current_folder("%s/Lios"%(os.environ['HOME']))
		filter = gtk.FileFilter()
		filter.add_pattern("*.cfg")
		load_preferences.add_filter(filter)
		response = load_preferences.run()
		if response == gtk.RESPONSE_OK:
			shutil.copy2("%s"%(load_preferences.get_filename()),"%s/Lios/.preferences.cfg"%(os.environ['HOME']))
			self.read_preferences()
			self.notify("preferences loaded from %s" % (load_preferences.get_filename()),False,None,True)
		self.dict = enchant.Dict("%s" % self.key_value[self.language])
		load_preferences.destroy()
		
		
				
	def on_Restore_preferences_activate(self,wedget,data=None):
		#Setting Default Values
		self.font="Georgia 14";self.highlight_font="Georgia 14";self.background_color="#000";self.font_color="#fff";self.highlight_color="#1572ffff0000"
		self.background_highlight_color="#00000bacffff";self.time_between_repeated_scanning=0;self.scan_resolution=300;self.scan_brightness=40;self.scan_area=0;self.ocr_engine="CUNEIFORM";self.language="eng"
		self.mode_of_rotation=0;self.number_of_pages_to_scan=100;self.page_numbering_type=0;self.starting_page_number=1;self.scanner_driver=1;self.auto_skew=0;self.rotation_angle=00;
		self.voice_message_state=1;self.voice_message_rate=170;self.voice_message_volume=150;self.voice_message_pitch=50;self.voice_message_voice=9;
		self.cam_take_time=7;self.cam_waitkey=30;self.cam_device=0;
		#Writing it to user configuration file
		self.set_preferences_to_file()				
		self.notify("preferences restored!",False,None,True)

	def set_preferences_to_file(self):
		#Removing old configuration file
		try:
			os.remove('%s/Lios/.preferences.cfg'%(os.environ['HOME']))
		except:
			pass		
		config = ConfigParser.ConfigParser()
		config.read('%s/Lios/.preferences.cfg'%(os.environ['HOME']))
		config.add_section('cfg')
		config.set('cfg',"time_between_repeated_scanning","%s"%self.time_between_repeated_scanning)
		config.set('cfg',"scan_resolution","%s"%self.scan_resolution)
		config.set('cfg',"scan_brightness","%s"%self.scan_brightness)
		config.set('cfg',"ocr_engine","%s"%self.ocr_engine)
		config.set('cfg',"scan_area","%s"%self.scan_area)
		config.set('cfg',"auto_skew","%s"%self.auto_skew)
		config.set('cfg',"language","%s"%self.language)
		config.set('cfg',"number_of_pages_to_scan","%s"%self.number_of_pages_to_scan)
		config.set('cfg',"mode_of_rotation","%s"%self.mode_of_rotation)
		config.set('cfg',"angle","%s"%self.rotation_angle)
		config.set('cfg',"numbering_type","%s"%self.page_numbering_type)
		config.set('cfg',"scanner_driver","%s"%self.scanner_driver)				
		config.set('cfg',"starting_page_number","%s"%self.starting_page_number)
		config.set('cfg',"background_color","%s"%self.background_color)
		config.set('cfg',"font_color","%s"%self.font_color)
		config.set('cfg',"highlight_color","%s"%self.highlight_color)
		config.set('cfg',"highlight_background_color","%s"%self.background_highlight_color)
		config.set('cfg',"font","%s"%self.font)
		config.set('cfg',"highlight_font","%s"%self.highlight_font)
		config.set('cfg',"voice_message_state","%s"%self.voice_message_state)
		config.set('cfg',"voice_message_voice","%s"%self.voice_message_voice)
		config.set('cfg',"voice_message_rate","%s"%self.voice_message_rate)
		config.set('cfg',"voice_message_volume","%s"%self.voice_message_volume)
		config.set('cfg',"voice_message_pitch","%s"%self.voice_message_pitch)
		config.set('cfg',"cam_take_time","%s"%self.cam_take_time)
		config.set('cfg',"cam_waitkey","%s"%self.cam_waitkey)
		config.set('cfg',"cam_device","%s"%self.cam_device)
		with open('%s/Lios/.preferences.cfg'%(os.environ['HOME']), 'wb') as configfile:
			config.write(configfile)
	
	
	#Function for manipulating preferences		
	def preferences(self,wedget,data=None):
		glade_file = "/usr/share/lios/Gui/Preferences.glade"
		self.tree = gtk.glade.XML(glade_file)		        
		signals = { "apply" : self.Apply_settings,
					"exit" : self.Ok_settings}
		self.tree.signal_autoconnect(signals)			
		self.window = self.tree.get_widget("window")
		self.window.show()


		#General
		
		#Font and font color
		self.start_spin = self.tree.get_widget("spinbutton_start")
		self.start_spin.set_value(self.starting_page_number)
		self.pages_spin = self.tree.get_widget("spinbutton_repeat")
		self.pages_spin.set_value(self.number_of_pages_to_scan)		
		
		self.background_color_button = self.tree.get_widget("colorbutton_background")
		color = gtk.gdk.Color(self.background_color)
		self.background_color_button.set_color(color)		

		self.highlight_color_button = self.tree.get_widget("colorbutton_highlight")
		color = gtk.gdk.Color(self.highlight_color)
		self.highlight_color_button.set_color(color)

		self.highlight_background_color_button = self.tree.get_widget("colorbutton_highlight_background")
		color = gtk.gdk.Color(self.background_highlight_color)
		self.highlight_background_color_button.set_color(color)
					
		self.font_color_button = self.tree.get_widget("colorbutton_font")		
		color = gtk.gdk.Color(self.font_color)
		self.font_color_button.set_color(color)	
			
		self.font_button = self.tree.get_widget("fontbutton")
		self.font_button.set_font_name(self.font)

		self.fontbutton_highlight_button = self.tree.get_widget("fontbutton_highlight")
		self.fontbutton_highlight_button.set_font_name(self.highlight_font)
		
		#Voice Message
		self.hscale_rate = self.tree.get_widget("hscale_rate")
		self.hscale_rate.set_value(self.voice_message_rate)
		self.hscale_volume = self.tree.get_widget("hscale_volume")
		self.hscale_volume.set_value(self.voice_message_volume)
		self.hscale_pitch = self.tree.get_widget("hscale_pitch")
		self.hscale_pitch.set_value(self.voice_message_pitch)
		self.combobox_voice = self.tree.get_widget("combobox_voice")
		for item in self.voice_list:
			self.combobox_voice.append_text(item)
		self.combobox_voice.set_active(self.voice_message_voice)


		self.checkbutton_say = self.tree.get_widget("checkbutton_say")
		if self.voice_message_state == 1:
			self.checkbutton_say.set_active(True)
		else:
			self.checkbutton_say.set_active(False)
		

		
		# Scanning
		self.time_spin = self.tree.get_widget("spinbutton_time")
		self.re_spin = self.tree.get_widget("spinbutton_resolution")
		self.bt_spin = self.tree.get_widget("spinbutton_brightness")
		self.time_spin.set_value(self.time_between_repeated_scanning)
		self.re_spin.set_value(self.scan_resolution)
		self.bt_spin.set_value(self.scan_brightness)
		
		#Angle
		self.angle_cb = self.tree.get_widget("combobox_angle")
		self.label_angle = self.tree.get_widget("label_angle")
		
		#AREA						      
		area = self.tree.get_widget("combobox_scan_area")
		area.connect('changed', self.change_area)
		area.set_active(self.scan_area)
		
		
		#ENGINE
		engine = self.tree.get_widget("combobox_engine")	
		engine.connect('changed', self.change_engine)
		set_engine = 0
		if self.ocr_engine == "CUNEIFORM":
			set_engine = 0
		elif self.ocr_engine == "TESSERACT":
			set_engine = 1
		else:
			set_engine = 2		
		engine.set_active(set_engine)
		
		#LANGUAGE
		self.language_cb = self.tree.get_widget("combobox_language")
		self.language_cb.connect('changed',self.change_language)
		l = 0
		for i in self.language_cb.get_model():
			if self.language == i[0]:
				self.language_cb.set_active(l)
			l += 1	
		
		#ROTATION
		rotation = self.tree.get_widget("combobox_rotation")
		rotation.connect("changed",self.change_rotation)
		rotation.set_active(self.mode_of_rotation)
		

		#DRIVER
		self.driver_cb = self.tree.get_widget("combobox_driver")
		self.driver_cb.set_active(self.scanner_driver)

		#DRIVER
		self.checkbutton_skew = self.tree.get_widget("checkbutton_skew")
		self.checkbutton_skew.set_active(self.auto_skew)
		

	
		#PAGE-NUMBARING
		numbering = self.tree.get_widget("combobox_page_type")
		numbering.connect("changed",self.change_numbering)
		numbering.set_active(self.page_numbering_type)
		
		
		#Cam_and_Webcam
		self.spinbutton_cam_time = self.tree.get_widget("spinbutton_cam_time")
		self.spinbutton_cam_time.set_value(self.cam_take_time)
		self.spinbutton_fps = self.tree.get_widget("spinbutton_fps")
		self.spinbutton_fps.set_value(self.cam_waitkey)
		self.combobox_cam_device = self.tree.get_widget("combobox_cam_device")
		self.combobox_cam_device.set_active(self.cam_device)
		

		notebook = self.tree.get_widget("notebook")
		try:
			notebook.set_page(data)
		except TypeError:
			pass
		else:
			pass	
		gtk.main()
		
	
	#FUNCTIONS-COMBOBOX	
	def change_area(self, area):
		self.model_area = area.get_model()
		self.index_area = area.get_active()
	
	def change_engine(self, engine):
		self.model_engine = engine.get_model()
		self.index_engine = engine.get_active()

		if self.model_engine[self.index_engine][0] == "ML-OCR-IIIT-Hyderabad":
			self.language_cb = self.tree.get_widget("combobox_language")
			ls = gtk.ListStore(gobject.TYPE_STRING)
			ls.append(["mal"])
			self.language_cb.set_model(ls)
			self.language_cb.set_active(0)			

		if self.model_engine[self.index_engine][0] == "CUNEIFORM":
			self.language_cb = self.tree.get_widget("combobox_language")
			ls = gtk.ListStore(gobject.TYPE_STRING)
			for i in 'eng' ,'ger','fra','rus','swe','spa','ita','ruseng','ukr','srp','hrv','pol','dan','por','dut','cze','rum','hun','bul','slo','lav','lit','est','tur':
				ls.append([i])			
			self.language_cb.set_model(ls)
			self.language_cb.set_active(0)		
		
		if self.model_engine[self.index_engine][0] == "TESSERACT":
			self.language_cb = self.tree.get_widget("combobox_language")
			ls = gtk.ListStore(gobject.TYPE_STRING)
			list = "afr","ara","aze","bel","ben","bul","cat","ces","chi-sim","chi-tra","chr","dan","deu","deu-frk","ell","eng","enm","epo","est","eus","fin","fra","frk","frm","glg","heb","hin","hrv","hun","ind","isl","ita","ita-old","jpn","kan","kor","lav","lit","mal","mkd","mlt","msa","nld","nor","pol","ron","rus","slk","slk-frak","slv","spa","spa-old","sqi","srp","swa","swe","tam","tel","tgl","tha","tur","ukr","vie"
			check_list = []
			check = Popen(['ls', '/usr/share/tesseract-ocr/tessdata/'],stdout=PIPE)
			for lan in check.stdout:
				if "." in lan:
					if lan.split(".")[0] in list:		
						if [lan.split(".")[0]] in check_list:
							pass
						else:
							ls.append([lan.split(".")[0]])
							check_list.append([lan.split(".")[0]])			
			self.language_cb.set_model(ls)
			self.language_cb.set_active(0)	

	def change_language(self,language):
		self.model_language = language.get_model()
		self.index_language = language.get_active()	


	def change_rotation(self,rotation):
		self.model_rotation = rotation.get_model()
		self.index_rotation = rotation.get_active()
		if self.model_rotation[self.index_rotation][0] == "Manuel":
			self.angle_cb.show()
			self.label_angle.show()
			if int(self.rotation_angle) == 00:
				self.angle_cb.set_active(0)
			elif int(self.rotation_angle) == 90:
				self.angle_cb.set_active(1)
			elif int(self.rotation_angle) == 180:
				self.angle_cb.set_active(2)
			else:
				self.angle_cb.set_active(3)					
		else:
			self.angle_cb.hide()
			self.label_angle.hide()
		
	
	def change_numbering(self,numbering):
		self.model_numbering = numbering.get_model()
		self.index_numbering = numbering.get_active()

	
	#FUNCTIONS-BUTTONS
	def Ok_settings(self,widget,data=None):
		self.notify("Its-all-right!",False,None,True)
		self.window.destroy()
	def Apply_settings(self,widget,data=None):
		try:
			language = (self.model_language[self.index_language][0])
		except AttributeError:
			language = self.language
		else:
			pass
		
		self.cam_take_time=self.spinbutton_cam_time.get_value_as_int()
		self.cam_waitkey=self.spinbutton_fps.get_value_as_int()
		self.cam_device=self.combobox_cam_device.get_active()
		
		
		self.voice_message_voice=self.combobox_voice.get_active()
		self.voice_message_rate=int(self.hscale_rate.get_value())
		self.voice_message_volume=int(self.hscale_volume.get_value())
		self.voice_message_pitch=int(self.hscale_pitch.get_value())
		if self.checkbutton_say.get_active() == True:
			self.voice_message_state = 1
		else:
			self.voice_message_state = 0
			
		
		self.font=self.font_button.get_font_name();self.highlight_font=self.fontbutton_highlight_button.get_font_name();
		self.background_color=self.background_color_button.get_color().to_string();self.font_color=self.font_color_button.get_color().to_string();
		self.highlight_color=self.highlight_color_button.get_color().to_string();self.time_between_repeated_scanning=self.time_spin.get_value_as_int();
		self.background_highlight_color=self.highlight_background_color_button.get_color().to_string();
		self.scan_resolution = self.re_spin.get_value_as_int();self.scan_brightness=self.bt_spin.get_value_as_int();self.scan_area=self.index_area;
		self.ocr_engine=self.model_engine[self.index_engine][0];self.language=language
		self.mode_of_rotation=self.index_rotation;self.number_of_pages_to_scan=self.pages_spin.get_value_as_int();self.page_numbering_type=self.index_numbering;
		self.starting_page_number=self.start_spin.get_value_as_int();self.scanner_driver=self.driver_cb.get_active()
		
		if self.angle_cb.get_visible() ==True:
			model_angle = self.angle_cb.get_model()
			self.rotation_angle = model_angle[self.angle_cb.get_active()][0]
		
		self.auto_skew = int(self.checkbutton_skew.get_active())
		
		
		
		espeak.set_parameter(espeak.Parameter.Rate,self.voice_message_rate)
		espeak.set_parameter(espeak.Parameter.Pitch,self.voice_message_pitch)
		espeak.set_parameter(espeak.Parameter.Volume,self.voice_message_volume)
		espeak.set_voice(self.voice_list[self.voice_message_voice])
		
		
		self.highlight_tag.set_property('foreground',gtk.gdk.Color(self.highlight_color))
		self.highlight_tag.set_property('font',self.highlight_font)
		self.highlight_tag.set_property('background',gtk.gdk.Color(self.background_highlight_color))
		
		pangoFont = pango.FontDescription(self.font)
		self.textview.modify_font(pangoFont)
		self.textview.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(self.background_color))
		self.textview.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(self.font_color))
		self.dict = enchant.Dict("%s" % self.key_value[self.language])
		self.set_preferences_to_file()
		self.notify("Lios ,Settings Reloaded!",False,None,True)
		self.window.destroy()

################# END OF PREFERENCES FUNCTIONS #################################
################################################################################
