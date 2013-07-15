# Threading libraries
import threading
import multiprocessing
import gobject


# Gui libraries
import pygtk
import gtk
import pango
import gtk.glade
import gnomecanvas

# System libraries
from subprocess import *
import sys
import os
import time
import shutil

# Spell checker
import enchant

# Espeak
from espeak import espeak

# Lios libraries 
import tools
import ocr_me
import scan_image
import image_manipulation
import preferences
from skew import *



# Checking Home Directories
directory = ("%s/Lios/" % (os.environ['HOME']))
temp_directory = ("%s/Lios/temp/" % (os.environ['HOME']))


try:
	os.chdir(directory)
except OSError:
	os.makedirs(directory)
	os.chdir(directory)	

try:
	os.chdir("Feedback")
except OSError:
	os.makedirs("Feedback")

os.chdir(directory)
try:
	os.chdir(temp_directory)
except OSError:
	os.makedirs("temp")

	
try:
	os.system("rfkill block bluetooth")
except:
	pass	
	
	
from espeak import espeak
class linux_intelligent_ocr_solution(tools.lios_tools,scan_image.scan_image,preferences.lios_preferences,image_manipulation.image_manipulation):
	def __init__(self):
		self.guibuilder = gtk.Builder()
		self.guibuilder.add_from_file("/usr/share/lios/Gui/main.glade")
		self.window = self.guibuilder.get_object("window")
		self.textbuffer = self.guibuilder.get_object("textbuffer")
		self.textview = self.guibuilder.get_object("textview")
		self.image_frame = self.guibuilder.get_object("frame")
		self.progressbar = self.guibuilder.get_object("progressbar")
		self.random_label = self.guibuilder.get_object("random_label")
		self.random_spinbutton = self.guibuilder.get_object("random_spinbutton")
		self.random_entry = self.guibuilder.get_object("random_entry")
		self.random_label.hide()
		self.random_spinbutton.hide()
		self.random_entry.hide()
		self.textview.grab_focus()
		self.guibuilder.connect_signals(self)
		

		self.progressbar.set_pulse_step(.01)
		self.pulse = True
		
		#self.image = self.guibuilder.get_object("image")
		
		self.scrolledwindow_image = self.guibuilder.get_object("scrolledwindow_image")
		self.vruler = self.guibuilder.get_object("vruler")
		self.hruler = self.guibuilder.get_object("hruler")
		self.scrolledwindow_image.connect_object("motion_notify_event", self.motion_notify, self.hruler)
		self.scrolledwindow_image.connect_object("motion_notify_event", self.motion_notify, self.vruler)
		
		

		
		self.voice_list=[]
		for item in espeak.list_voices():
			self.voice_list.append(item.name)

		for item in "scan_to_ui","ocr_pdf","ocr_folder","ocr_image","scan_and_ocr","scan_and_ocr_repeatedly","cam_scan","optimise_brightness","ocr_ui_image":
			self.guibuilder.get_object(item).connect("activate",self.run_process,item)
			
			
		ocr_ui_image_button = self.guibuilder.get_object("ocr_ui_image_button")
		ocr_ui_image_button.connect("clicked",self.run_process,"ocr_ui_image")

		ocr_selected_image_region_button = self.guibuilder.get_object("ocr_selected_image_region_button")
		ocr_selected_image_region_button.connect("clicked",self.run_process,"ocr_selected_image_region")
		
		
		scan_to_ui_button = self.guibuilder.get_object("scan_to_ui_button")		 
		scan_to_ui_button.connect("clicked",self.run_process,"scan_to_ui")
		
		
		#Preferences
		General_Preferences = self.guibuilder.get_object("General_Preferences")
		General_Preferences.connect("activate",self.preferences,0)
		Preferences_Recognition = self.guibuilder.get_object("Preferences_Recognition")
		Preferences_Recognition.connect("activate",self.preferences,1)
		Preferences_Scanning = self.guibuilder.get_object("Preferences_Scanning")
		Preferences_Scanning.connect("activate",self.preferences,2)
		Preferences_CamaraWebcam = self.guibuilder.get_object("Preferences_CamaraWebcam")
		Preferences_CamaraWebcam.connect("activate",self.preferences,3)
		
		#Getting Preferences Values
		self.read_preferences()
		
		#Init Keep Runner
		self.keep_running = False

		# Intiating thred in PyGtk
		gtk.threads_init()
		
		#Espeak And event
		espeak.set_parameter(espeak.Parameter.Rate,self.voice_message_rate)
		espeak.set_parameter(espeak.Parameter.Pitch,self.voice_message_pitch)
		espeak.set_parameter(espeak.Parameter.Volume,self.voice_message_volume)
		espeak.set_voice(self.voice_list[self.voice_message_voice])
		espeak.set_SynthCallback(self.espeak_event)


		#Gnome-Canvas
		self.first_run = True
		self.canvas = gnomecanvas.Canvas(aa=True)
		self.dragging = False
		self.scrolledwindow_image.add(self.canvas)
		self.canvas.connect("event", self.canvas_event)
		self.set_image(self,data=None)
		self.canvas.show()
		self.window.maximize()		

		#Reading Dictionarys		
		self.key_value = {"eng" : "en","afr" : "af","am" : "am","ara" : "ar","ara" : "ar","bul" : "bg","ben" : "bn","br" : "br","cat" : "ca","ces" : "cs","cy" : "cy","dan" : "da","ger" : "de","ger" : "de","ell" : "el","eo" : "eo","spa" : "es","est" : "et","eu" : "eu","fa" : "fa","fin" : "fi","fo" : "fo","fra" : "fr","ga" : "ga","gl" : "gl","gu" : "gu","heb" : "he","hin" : "hi","hrv" : "hr","hsb" : "hsb","hun" : "hu","hy" : "hy","id" : "id","is" : "is","ita" : "it","kk" : "kk","kn" : "kn","ku" : "ku","lit" : "lt","lav" : "lv","mal" : "ml ","mr" : "mr ","dut" : "nl","no" : "no","nr" : "nr","ns" : "ns ","or" : "or ","pa" : "pa ","pol" : "pl ","por" : "pt","por" : "pt","por" : "pt","ron" : "ro","rus" : "ru ","slk" : "sk","slv" : "sl","ss" : "ss","st" : "st","swe" : "sv","tam" : "ta","tel" : "te","tl" : "tl","tn" : "tn","ts" : "ts","ukr" : "uk","uz" : "uz","xh" : "xh","zu" : "zu" }
		self.dict = enchant.Dict("%s" % self.key_value[self.language])
		
		#Font 
		pangoFont = pango.FontDescription(self.font)
		self.textview.modify_font(pangoFont)
		
		#Opening Recent Document
		try:
			recent_open = open("%srecent"%directory,'r')
		except IOError:
			pass
		else:
			recent_text = recent_open.read()
			self.textbuffer.set_text(recent_text)
		
		#Color
		self.highlight_tag = self.textbuffer.create_tag('Reading')
		self.textview.modify_text(gtk.STATE_NORMAL, gtk.gdk.Color(self.font_color))
		self.textview.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(self.background_color))
		self.highlight_tag.set_property('foreground',gtk.gdk.Color(self.highlight_color))
		self.highlight_tag.set_property('background',gtk.gdk.Color(self.background_highlight_color))		
		self.highlight_tag.set_property('font',self.highlight_font)
		
		#Welcome
		self.notify("Welcome To Linux-Intelligent-O.C.R-Solution",True,None,True)
		gobject.timeout_add(20, self.pulse_progressbar)

		#Placing cursor
		self.textbuffer.place_cursor(self.textbuffer.get_start_iter())
		
		self.window.show()
		gtk.main()
		


############################################## W---O---R-----K   G---R---O----U---N---D ######################################################		
		
	def run_process(self,wedget,data=None):
		if threading.active_count() == 1:
			self.keep_running = True
			threading.Thread(target=self.process,args=(data,)).start()
			self.window.queue_draw()					
		else:
			self.notify("Resource Busy!",True,None,True)

	def stop(self,widget,data=None):
		if self.keep_running == True:
			self.keep_running = False
			for item in "wordocr","cuneiform","tesseract","scanimage":
				os.system("pkill %s"%item)
			self.clean()
			self.notify("Terminated!",True,0,True)



############################################## W---O---R-----K   G---R---O----U---N---D ######################################################	
		
	
		
	def pulse_progressbar(self):
		if self.pulse == True:
			self.progressbar.pulse()
		return True

	# Lios notify 
	def notify(self,text,set_progress_bar=True,progress_bar_set=None,set_speeh=True):
		if set_progress_bar == True:
			if progress_bar_set == None:
				self.pulse = True
			else:
				self.pulse = False
				self.progressbar.set_fraction(progress_bar_set)
			self.progressbar.set_text(text)
		if self.voice_message_state == 1 and set_speeh == True:
			os.system("pkill paplay")
			os.system("espeak -v %s -a %s -s %s -p %s '%s' --stdout|paplay &"%(self.voice_list[self.voice_message_voice],self.voice_message_volume,self.voice_message_rate,self.voice_message_pitch,text.replace("'",'"')))
	def stop_speak(self):
		os.system("pkill paplay")

				
	def get_text_to_buffer(self):
		try:
			text = open("temp.text")
		except IOError:
			return True
		else:
			read_text = text.read()
			text.close()
			start,end = self.textbuffer.get_bounds()
			text = self.textbuffer.get_text(start,end)
			recent_open = open("%srecent"%directory,'w')
			recent_open.write(text)
			recent_open.close()					
			if read_text != "":
				iter = self.textbuffer.get_end_iter()
				iter.backward_visible_word_start()	
				iter.forward_visible_word_end()

				gtk.gdk.threads_enter()
				
				if self.page_numbering_type == 0:				
					self.textbuffer.insert(iter,"\nPage-%s\n%s"%(self.starting_page_number,read_text))
					self.notify("Page-%s"%self.starting_page_number,False,None,True)
					self.starting_page_number = self.starting_page_number + 1
				else:
					self.textbuffer.insert(iter,"\nPage-%s-%s\n%s"%(self.starting_page_number,self.starting_page_number+1,read_text))
					self.notify("Page-%s-%s" % (self.starting_page_number,self.starting_page_number+1),False,None,True)
					self.starting_page_number+=2

				gtk.gdk.threads_leave()
				os.remove("temp.text")
				os.remove("temp.txt")
				
				return True
			else:
				return True
		

	

		
				
##################### H - E - L - P ###############################################
	def about(self,wedget,data=None):
		glade_file = "/usr/share/lios/Gui/about.glade"
		self.about_tree = gtk.glade.XML(glade_file)
		self.about_window = self.about_tree.get_widget("window")
		signals = { "on_ok_clicked" : self.about_exit}
		self.about_tree.signal_autoconnect(signals)
		self.about_window.show()
		gtk.main()
	def about_exit(self,wedget,data=None):
		self.notify("Thanks for using lios!",False,None,True)
		self.about_window.destroy()
		
	def open_read_me(self,wedget,data=None):
		open_readme_temp = open("/usr/share/lios/Data/Readme")
		readme = open_readme_temp.read()
		open_readme_temp.close()
		self.textbuffer.set_text(readme)
		start = self.textbuffer.get_start_iter()
		self.textbuffer.place_cursor(start)			
	
	def open(self,wedget,data=None):
		open_file = gtk.FileChooserDialog(title="Select the file to open" ,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                  buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
                open_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
                filter = gtk.FileFilter()
                for patern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.text","*.txt","*.pbm":
					filter.add_pattern(patern)		
                open_file.add_filter(filter)       
                response = open_file.run()
                if response == gtk.RESPONSE_OK:
					if (".txt" in open_file.get_filename()) or (".text" in open_file.get_filename()):
						to_read = open("%s" % (open_file.get_filename()))
						self.save_name = "%s" % (open_file.get_filename())
						to_open = to_read.read()
						self.textbuffer.set_text(to_open)
						where = self.textbuffer.get_start_iter()
						self.textbuffer.place_cursor(where)
						open_file.destroy()
						self.textbuffer.set_modified(False)
					else:
						os.system("convert %s image"%(open_file.get_filename()).replace(" ","\ "))
						self.set_image(self)
						open_file.destroy()
		else:
			open_file.destroy()
					 
	def feedback(self,wedget,data=None):
		feedback_builder = gtk.Builder()
		feedback_builder.add_from_file("/usr/share/lios/Gui/feedback.glade")
		feedback_builder.connect_signals({ "ok" : self.feedback_ok, "close" : self.feedback_close})
		self.feedback_window = feedback_builder.get_object("window")
		self.feedback_entry = feedback_builder.get_object("entry")
		self.feedback_entry.set_max_length(10)
		self.feedback_textbuffer = feedback_builder.get_object("textbuffer")
		self.feedback_window.show()
	def feedback_close(self,wedget,data=None):
		self.feedback_window.destroy()
	def feedback_ok(self,wedget,data=None):
		name = self.feedback_entry.get_text()
		f_name = name.split(" ")
		file_name = f_name[0]
		os.system("i-layout image")
		os.system("convert /usr/share/lios/BinImg.tif ~/Lios/Feedback/%s.jpg"%(file_name))
		try:
			feedback_text = open("%s/Feedback/Descriptions.txt"%(directory))
		except IOError:
			feedback_text = open("%s/Feedback/Descriptions.txt"%(directory),'w')
			feedback_text.write("LINUX-INTELLIGENT-OCR-SOLUTION << FEEDBACK\n------------------------------------------\n")
		else:
			feedback_text = open("%s/Feedback/Descriptions.txt"%(directory),'a')
		start ,end = self.feedback_textbuffer.get_bounds()				
		feedback_text.write("File Name   : %s\nDescription : %s\n"%(file_name,self.feedback_textbuffer.get_text(start,end,False)))
		for line in open("%s/Lios/.preferences.cfg"%(os.environ['HOME'])):
			if "use_engine" in line:
				feedback_text.write("Engine      : %s"%(line[14:]))
			if "use_language" in line:
				feedback_text.write("Language    : %s\n"%(line[12:]))							
		self.feedback_window.destroy()
							 															
##################### H - E - L - P ###############################################

    
        def append(self,wedget,data=None):
		append_file = gtk.FileChooserDialog(title="Select the file to open" ,action=gtk.FILE_CHOOSER_ACTION_OPEN,
                                    buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		append_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
		append_file.run()
		to_read = open("%s" % (append_file.get_filename()))
		to_append = to_read.read()
		
		start ,end = self.textbuffer.get_bounds()
		self.textbuffer.insert(end,to_append)
		append_file.destroy() 

        def punch(self,wedget,data=None):
		insert_at_cursor = gtk.FileChooserDialog(title="Select the file to open" ,action=gtk.FILE_CHOOSER_ACTION_OPEN,buttons=(gtk.STOCK_OPEN,gtk.RESPONSE_OK))
		insert_at_cursor.set_current_folder("%s/Lios"%(os.environ['HOME']))
		insert_at_cursor.run()
		insert_at_cursor_to_read = open("%s" % (insert_at_cursor.get_filename()))
		to_insert_at_cursor = insert_at_cursor_to_read.read()
		start ,end = self.textbuffer.get_bounds()
		self.textbuffer.insert_at_cursor(to_insert_at_cursor)
		insert_at_cursor.destroy()          

	def quit(self, widget, event=None):
		self.set_preferences_to_file()
		if threading.active_count() == 1:
			start,end = self.textbuffer.get_bounds()
			text = self.textbuffer.get_text(start,end)
			recent_open = open("%srecent"%directory,'w')
			recent_open.write(text)
			recent_open.close()
			os.system("rm image")
			os.system("cp /usr/share/lios/Gui/lios image")
			gtk.main_quit()
			espeak.cancel()
			self.clean()
			try:
				os.system("rfkill unblock bluetooth")
			except:
				pass	
			raise SystemExit
		else:
			espeak.cancel()
			self.notify("Please close all processes before Quitting",True,None,True)
		

	def new(self,wedget,data=None):
		try:
			os.remove("selected")
		except:
			pass
		if self.textbuffer.get_modified() == True:
			dialog =  gtk.Dialog("Warning",self.window,gtk.DIALOG_DESTROY_WITH_PARENT,
			("Save As", gtk.RESPONSE_ACCEPT, "Close" ,gtk.RESPONSE_CLOSE, "Start new without saving", gtk.RESPONSE_REJECT))
			lbl = gtk.Label("Do you realy want to start new file  ?")
			lbl.show()
			dialog.vbox.pack_start(lbl)                             						
			response = dialog.run()			
			if response == gtk.RESPONSE_REJECT:
				dialog.destroy()
				start, end = self.textbuffer.get_bounds()
				self.textbuffer.delete(start, end)
				shutil.copy("/usr/share/lios/Gui/lios","image")	
				delete_temp = open("temp.text","w")
				delete_temp.close()							
				self.starting_page_number = 1
				self.set_image(self)
				self.textbuffer.set_modified(False) 															
				try:
					del self.save_file_name
				except AttributeError:
					pass
				else:
					pass
				self.notify("New!",True,None,True)	
			elif response == gtk.RESPONSE_ACCEPT:
				dialog.destroy()
				self.save_file(self)
				start, end = self.textbuffer.get_bounds()
				self.textbuffer.delete(start, end)
				os.system("cp /usr/share/lios/Gui/lios image")	
				delete_temp = open("temp.text","w")
				delete_temp.close()
				self.starting_page_number = 1
				self.textbuffer.set_modified(False)
				self.set_image(self)
				try:
					del self.save_file_name
				except AttributeError:
					pass
				else:
					pass
				self.notify("New!",True,None,True)					
			else:
				dialog.destroy()	
		else:
			self.notify("New!",True,None,True)
			start, end = self.textbuffer.get_bounds()
			self.textbuffer.delete(start, end)
			os.system("cp /usr/share/lios/Gui/lios image")	
			delete_temp = open("temp.text","w")
			delete_temp.close()							
			self.starting_page_number = 1
			self.textbuffer.set_modified(False)
			try:
				del self.save_file_name
			except AttributeError:
				pass
			else:
				pass
			self.set_image(self)
			 			
	def save(self,wedget,data=None):
		try:
			self.save_name 
		except AttributeError:
			save_file = gtk.FileChooserDialog(title="Save..",action=gtk.FILE_CHOOSER_ACTION_SAVE,
		                     buttons=(gtk.STOCK_SAVE,gtk.RESPONSE_OK)) 
			save_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
			response = save_file.run()		
			if response == gtk.RESPONSE_OK:
				start, end = self.textbuffer.get_bounds()
				chars = self.textbuffer.get_slice(start, end, False)
				self.save_name = "%s.text"%(save_file.get_filename())
				if ".txt" in self.save_name or ".text" in self.save_name:
					to_save = open("%s" % (save_file.get_filename()),'w')
				else:
					to_save = open("%s.text" % (save_file.get_filename()),'w')
				to_save.write(chars)
				
				
				save_file.destroy()
				self.textbuffer.set_modified(False)
		else:
			start, end = self.textbuffer.get_bounds()
			chars = self.textbuffer.get_slice(start, end, False)
			if ".txt" in self.save_name or ".text" in self.save_name:
				to_save = open("%s" %(self.save_name),'w')
			else:
				to_save = open("%s.text" % (self.save_name),'w')
			to_save.write(chars)
			self.textbuffer.set_modified(False) 

	def save_as(self,wedget,data=None):
		try:
			start, end = self.textbuffer.get_bounds()
			text = self.textbuffer.get_text(start, end)
		except AttributeError:
			self.notify("Nothing to save!",False,None,True)
		else:
			pass
		start, end = self.textbuffer.get_bounds()
		text = self.textbuffer.get_text(start, end)
		save_file = gtk.FileChooserDialog(title="Save As...",action=gtk.FILE_CHOOSER_ACTION_SAVE,
		                     buttons=(gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		save_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
		response = save_file.run()
		
		if response == gtk.RESPONSE_OK:
			save_name = save_file.get_filename()
			if ".txt" in save_name or ".text" in save_name:
				to_save = open("%s" %(save_name),'w')
			else:
				to_save = open("%s.text" %(save_name),'w')
		save_file.destroy()
		try:
			to_save.write(text)
		except IOError:
			self.notify("Sorry file not saved!",False,None,True)
		else:
			pass

	def append_save(self,wedget,data=None):
		save_file = gtk.FileChooserDialog(title="Save..",action=gtk.FILE_CHOOSER_ACTION_SAVE,
		                     buttons=(gtk.STOCK_SAVE,gtk.RESPONSE_OK))
		save_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
		response = save_file.run()
				
		if response == gtk.RESPONSE_OK:
			start, end = self.textbuffer.get_bounds()
			chars = self.textbuffer.get_slice(start, end, False)
			to_save = open(save_file.get_filename(),'a')
			to_save.write(chars)
			save_file.destroy()
			self.textbuffer.set_modified(False)


	def copy(self,wedget,data=None):
		self.textbuffer.copy_clipboard(self.clipboard)
	def cut(self,wedget,data=None):
		self.textbuffer.cut_clipboard(self.clipboard, True)
	def paste(self,wedget,data=None):
		self.textbuffer.paste_clipboard(self.clipboard, None, True)
	def delete(self,wedget,data=None):
		self.textbuffer.delete_selection(True, True)
	def artha(self,wedget,data=None):
		os.system("artha &")
	
	
	def find(self,wedget,data=None):		
		self.random_entry.grab_focus()
		self.random_label.set_label("Find")
		self.random_entry.connect("activate",self.find_function)
		self.random_entry.show()
		self.random_label.show()
		self.random_label.set_mnemonic_widget(self.random_entry)
			
	def find_function(self,data=None):
		try:
			self.find_me("%s"%(self.random_entry.get_text()),self.last_search_iter)
		except TypeError:
			self.find_me("%s"%(self.random_entry.get_text()),None)
		except AttributeError:
			self.find_me("%s"%(self.random_entry.get_text()),None)
		self.random_entry.set_text("")			
		self.random_entry.hide()
		self.random_label.hide()

	def find_me(self,word,iter = None):
		if iter is None:
			iter = self.textbuffer.get_start_iter()
		self.word = word
		res = iter.forward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)
		if res:
			match_start, match_end = res
			self.textbuffer.place_cursor(match_start)
			self.textbuffer.select_range(match_start, match_end)
			self.textview.scroll_to_iter(match_start, 0.0)
			self.last_search_iter = match_end
			self.textview.grab_focus()
		else:
			try:
				res = iter.backward_search(str, gtk.TEXT_SEARCH_TEXT_ONLY)
			except TypeError:
				self.textview.grab_focus()
			else:
				match_start, match_end = res
				self.textbuffer.place_cursor(match_start)
				self.textbuffer.select_range(match_start, match_end)
				self.edit.scroll_to_iter(match_start, 0.0)
				self.last_search_iter = match_end
				self.textview.grab_focus() 
	def go_to_page(self,wedget,data=None):
		self.random_spinbutton.grab_focus()
		self.random_label.set_label("Go-To-Page")
		adj = gtk.Adjustment(value=1, lower=1, upper=self.starting_page_number-1, step_incr=1, page_incr=5, page_size=0)
		self.random_spinbutton.set_adjustment(adj)
		self.random_spinbutton.connect("activate",self.go_to_page_function)
		self.random_spinbutton.show()
		self.random_label.show()
		self.random_label.set_mnemonic_widget(self.random_spinbutton)
	def go_to_page_function(self,data=None):
		to_go = self.random_spinbutton.get_value_as_int()
		if self.page_numbering_type == 0:
			self.find_me("Page-%s"%(to_go),None)
		else:
			if to_go %2 == 0:
				self.find_me("Page-%s-%s"%(to_go-1,to_go),None)
			else:
				self.find_me("Page-%s-%s"%(to_go,to_go+1),None)	
			
		self.random_spinbutton.hide()
		self.random_label.hide()		
			
###############  Go-To-Line ###################################################
	def go_to_line(self,wedget,data=None):
		insert_mark = self.textbuffer.get_insert()
		offset = self.textbuffer.get_iter_at_mark(insert_mark)
		line = offset.get_line()
		maximum = self.textbuffer.get_line_count() 
		adj = gtk.Adjustment(value=1, lower=1, upper=maximum, step_incr=1, page_incr=5, page_size=0)
		self.random_spinbutton.set_adjustment(adj)
		self.random_spinbutton.set_value(line)		
		self.random_label.set_label("Go-To-Line : ")
		self.random_spinbutton.show()
		self.random_label.show()
		self.random_label.set_mnemonic_widget(self.random_spinbutton)
		self.random_spinbutton.connect("activate",self.go_to_line_function)
		self.random_spinbutton.grab_focus()
				
	def go_to_line_function(self,data=None):
		self.random_spinbutton.hide()
		self.random_label.hide()
		to = self.random_spinbutton.get_value_as_int()
		iter = self.textbuffer.get_iter_at_line(to)	
		self.textbuffer.place_cursor(iter)
		self.textview.scroll_to_iter(iter, 0.0)
		self.textview.grab_focus()
				
###############  Go-To-Line ###################################################

			
	def check(self,weget,data=None):
		selection = self.textbuffer.get_bounds()
		s = selection[0]
		e = selection[1]
		textline = self.textbuffer.get_text(s, e)
		for i,j in enumerate(textline):
			if j == ' ':
				r = self.textbuffer.get_iter_at_offset(i)#.forward_word_ends(0)
				text = self.textbuffer.get_text(s, r)
				s =r


########################################### DDDDOOOOOOOOO THHHHHHHHEEEEEEE DUUUUUUUUTTTYYYYYYYYYY ##################################
	def process(self,data):
		self.clean()
		if self.keep_running == False:return None # Check to terminate
		self.notify("Running !",True,None,True)			
		if data in ['scan_and_ocr','scan_to_ui','scan_and_ocr_repeatedly','optimise_brightness']:
			self.init_scanner()
		
		if self.keep_running == False:return None										
		if data == 'scan_to_ui':
			self.work(None,False,None,self.mode_of_rotation,True)	
		
		if data == 'ocr_ui_image':
			if self.mode_of_rotation == 2:
				self.work("image",True,00,self.mode_of_rotation,True)
			else:
				self.work("image",True,None,self.mode_of_rotation,True)

		if data == 'ocr_selected_image_region':
			if "selected" in os.listdir("%s/Lios/temp/"%(os.environ['HOME'])):
				if self.mode_of_rotation == 2:
					self.work("selected",True,00,self.mode_of_rotation,False)
				else:
					self.work("selected",True,None,self.mode_of_rotation,False)
			else:
				self.notify("Region not selected!",True,0,True)

		if data == 'scan_and_ocr':
			self.work(None,True,None,self.mode_of_rotation,True)				
		if data == 'scan_and_ocr_repeatedly':
			#Partial_Automatic
			if self.mode_of_rotation == 1:
				angle=self.work(None,True,None,self.mode_of_rotation,True)
				for i in range(1,self.number_of_pages_to_scan):
					if self.keep_running == False:return None
					self.work(None,True,angle,2,True)
					time.sleep(self.time_between_repeated_scanning)
			else:
				for i in range(1,self.number_of_pages_to_scan):
					if self.keep_running == False:return None
					self.work(None,True,None,self.mode_of_rotation,True)
					time.sleep(self.time_between_repeated_scanning)			

		if data == 'cam_scan':
			print "Device=%s=ok"%self.cam_device
			camcapture = cv.CreateCameraCapture(self.cam_device)
			print camcapture
			if not camcapture:
				print "Error opening WebCAM"
				self.notify("Error opening WebCAM!",False,None,True)
				self.keep_running = False
			else:
				print camcapture
				cv.SetCaptureProperty(camcapture, cv.CV_CAP_PROP_FRAME_WIDTH, 1280)
				cv.SetCaptureProperty(camcapture, cv.CV_CAP_PROP_FRAME_HEIGHT, 800);
			def repeat():
				frame = cv.QueryFrame(camcapture)
				cv.ShowImage('Camera', frame)
				cv.SaveImage("temp.pnm",frame)
				k=cv.WaitKey(self.cam_waitkey);
			i = 1
			if self.keep_running == False:return None
			while i < (self.cam_take_time * 10):
				if self.keep_running == False:return None
				repeat()
				i = i + 1
			if self.keep_running == False:return None	
			self.notify("Running OCR!",False,None,True)	
			self.work("temp.pnm",True,00,2,True)

		if data == 'ocr_image':
			image_file = gtk.FileChooserDialog("Select the image",None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			image_file.set_default_response(gtk.RESPONSE_OK)
			image_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
			filter = gtk.FileFilter()
			for pattern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.pbm":
				filter.add_pattern(pattern)
			image_file.add_filter(filter)
			gtk.gdk.threads_enter()
			response = image_file.run()
			gtk.gdk.threads_leave()
			image_filename = image_file.get_filename()
			image_file.destroy()
			if response == gtk.RESPONSE_OK:
				os.system("convert %s temp.pnm"%(image_filename.replace(" ","\ ")))
				self.work("temp.pnm",True,None,self.mode_of_rotation,True)	
				

		if data == 'ocr_folder':
			folder = gtk.FileChooserDialog("Select the folder containing images",None,gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			folder.set_default_response(gtk.RESPONSE_OK)
			folder.set_current_folder("%s/Lios"%(os.environ['HOME']))		
			filter = gtk.FileFilter()
			for pattern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.pbm":
				filter.add_pattern(pattern)
			folder.add_filter(filter)
			gtk.gdk.threads_enter()
			response = folder.run()
			gtk.gdk.threads_leave()
			image_directory = folder.get_current_folder()
			folder.destroy()
			if response == gtk.RESPONSE_OK:
				self.notify("serching for images!",False,None,True)
				file_list = os.listdir(image_directory)
				pnm_list = []
				formats = ['png','jpg','tif','pnm','jpeg','tiff','bmp']
				for image in file_list:
					try:
						if image.split(".")[1] in formats:
							os.system("convert %s/%s %s.pnm"%(image_directory,image.replace(" ","\ "),image.replace(" ","\ ").split(".")[0]))
							pnm_list.append("%s.pnm"%(image.split(".")[0]))
					except IndexError:
						pass
				
				#Partial_Automatic
				if self.mode_of_rotation == 1:
					if self.keep_running == False:return None
					angle=self.work("%s"%(pnm_list[0].replace(" ","\ ")),True,None,self.mode_of_rotation,True)
					pnm_list.remove(pnm_list[0])
					for image in pnm_list:
						if self.keep_running == False:return None
						self.work(image.replace(" ","\ "),True,angle,2,True)
				
				#Full automatic
				else:
					for image in pnm_list:
						if self.keep_running == False:return None
						self.work(image.replace(" ","\ "),True,None,self.mode_of_rotation,True)
		
		if data == "ocr_pdf":
			pdf_file = gtk.FileChooserDialog("Select the Pdf file to OCR",None,gtk.FILE_CHOOSER_ACTION_OPEN,(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,gtk.STOCK_OPEN, gtk.RESPONSE_OK))
			pdf_file.set_default_response(gtk.RESPONSE_OK)
			filter = gtk.FileFilter()
			filter.add_pattern("*.pdf")
			pdf_file.add_filter(filter)
			pdf_file.set_current_folder("%s/Lios"%(os.environ['HOME']))
			gtk.gdk.threads_enter()
			response = pdf_file.run()
			gtk.gdk.threads_leave()
			pdf_filename = pdf_file.get_filename()
			pdf_file.destroy()
			if response == gtk.RESPONSE_OK:
				self.notify("Converting %s to images"%(pdf_filename),True,None,True)
				os.system("pdfimages %s out_image" % pdf_filename.replace(" ","\ "))				
				pbm_list = []
				for image in os.listdir(temp_directory):
					if ".pbm" in image or ".ppm" in image:
						pbm_list.append(image)
						
				#Partial_Automatic or Manuel				
				if self.mode_of_rotation == 1:					
					angle=self.work("%s"%(pbm_list[0]),True,None,self.mode_of_rotation,True)
					pbm_list.remove(pbm_list[0])
					for image in pbm_list:
						if self.keep_running == False:return None
						self.work(image,True,angle,2,True)
				#Full automatic or Manuel
				else:
					for image in pbm_list:
						if self.keep_running == False:return None
						self.work(image,True,None,self.mode_of_rotation,True)

		if data == 'optimise_brightness':
			if self.keep_running == False:return None # Check to terminate			
			self.check_brightness_support()
			if self.keep_running == False:return None # Check to terminate
			if self.mode_of_rotation == 2:
				angle=self.rotation_angle	
			else:
				angle=self.work(None,True,None,self.mode_of_rotation,True)
			
			if self.keep_running == False:return None # Check to terminate
			self.optimize(angle)
		
		self.keep_running = False
		self.clean()
			
				 
			

	def work(self,data=None,ocr=False,angle=None,rotation_mode=None,alter_image=True):
		blank = False
		if self.keep_running == False:return None # Check to terminate	


		if data == None:
			self.notify("Scanning",False,None,True)	
			self.notify("Scanning with %s Resolution and %s Brightness! ..." %(self.scan_resolution,self.scan_brightness),True,None,False)
			self.scan_image("temp",self.scan_resolution,self.scan_brightness,self.scan_area)
			os.system("convert temp.pnm image")
		else:
			os.system("convert %s temp.pnm "%(data))
		
	
		if alter_image == True:
			os.system("convert temp.pnm image")

		if self.keep_running == False:return None # Check to terminate
		


			
		
		if ocr == True:
			if rotation_mode == 2:
				#Manuel
				if angle == None:
					angle = self.rotation_angle 
				
				self.notify("Running O.C.R With %s in %s Language" % (self.ocr_engine.lower(),self.language),True,None,False)
				self.skew_work_caller()
				os.system("convert -rotate %s temp.pnm temp.pnm " % (angle))
				ocr_me.do("temp","%s"%(self.ocr_engine),"%s"%(self.language))
				
				
				
			else:
				#Full_Automatic & Partial_Automatic
				self.skew_work_caller()
				os.rename("temp.pnm","00.pnm")
				self.notify("Running O.C.R With %s in %s Language" % (self.ocr_engine.lower(),self.language),True,None,False)
				ocr_me.do("00","%s"%(self.ocr_engine),"%s"%(self.language))
				a = self.count_me("00.txt")				
				os.system("convert -rotate 90 00.pnm 90.pnm ")
				self.notify("Running O.C.R With %s in %s Language" % (self.ocr_engine.lower(),self.language),True,.25,False)
				ocr_me.do("90","%s"%(self.ocr_engine),"%s"%(self.language))
				b = self.count_me("90.txt")
				os.system("convert -rotate 180 00.pnm 180.pnm ")
				self.notify("Running O.C.R With %s in %s Language" % (self.ocr_engine.lower(),self.language),True,.50,False)
				ocr_me.do("180","%s"%(self.ocr_engine),"%s"%(self.language))
				c = self.count_me("180.txt")
				os.system("convert -rotate 270 00.pnm 270.pnm ")
				self.notify("Running O.C.R With %s in %s Language" % (self.ocr_engine.lower(),self.language),True,.75,False)
				ocr_me.do("270","%s"%(self.ocr_engine),"%s"%(self.language))
				d = self.count_me("270.txt")
				if (a > b) and (a > c) and (a > d):
					angle="00"
					os.system("convert 00.pnm image")
					os.system("cat 00.txt >> temp.txt")
					self.notify("Top of the book at the front of your scanner!",False,None,True)
				elif (b > c) and (b > d) and (b > a):
					angle="90"
					os.system("convert 90.pnm image")
					os.system("cat 90.txt >> temp.txt")
					self.notify("Top of the book at the left of your scanner!",False,None,True)
				elif (c > b) and (c > a) and (c > d):
					angle="180"
					os.system("convert 180.pnm image")
					os.system("cat 180.txt >> temp.txt")
					self.notify("Top of the book at the back of your scanner!",False,None,True)
				elif (d > b) and (d > a) and (d > c):
					angle="270"
					os.system("convert 270.pnm image")
					os.system("cat 270.txt >> temp.txt")
					self.notify("Top of the book at the right of your scanner!",False,None,True)
				else:
					self.notify("The page appears to be blank!",False,None,True)
					blank = True
			
			if self.keep_running == False:return None # Check to terminate
			if blank == False:
				os.system("cat temp.txt | iconv -t utf-8 -o temp.text")
				self.get_text_to_buffer()
		if alter_image == True:
			self.set_image(self)
		else:
			self.notify("Ok !",True,None,False)
		return angle
	
	def skew_work_caller(self):
		if (self.auto_skew == True):
			process=multiprocessing.Process(target=self.skew_work,args=())
			process.start()
			while process.is_alive():
				pass		
	def skew_work(self):
		image_deskewer = ImageDeskewer()
		os.system("convert temp.pnm work.jpg")
		image_deskewer.deskew("work.jpg", "image")
		os.system("convert image temp.pnm")


############################# E #### N ######## D ###############O######F############ WORK #############################		

	def scan_and_count(self,value):
		self.optimise_progress += .07
		self.scan_image("temp",self.scan_resolution,value,self.scan_area)
		if self.keep_running == False:return None # Check to terminate
		os.system("convert -rotate %s temp.pnm temp.pnm"%(self.opt_angle))
		if self.keep_running == False:return None # Check to terminate
		ocr_me.do("temp","%s"%(self.ocr_engine),"%s"%(self.language))
		if self.keep_running == False:return None # Check to terminate
		count = self.count_me("temp.txt")
		if self.keep_running == False:return None # Check to terminate		
		label = gtk.Label("Scan at %s = %s "%(value,count))
		label.set_selectable(True)
		self.box.pack_start(label)
		label.show()
		try:
			os.remove("temp.txt")
		except:
			pass		
		self.notify("Brightness %s has detected %s Words !"%(value,count),True,self.optimise_progress,True)
		return count


	def optimize(self,opt_angle):
		self.optimise_progress = .017
		self.opt_angle = opt_angle
		self.optimise_window = gtk.Window()
		self.optimise_window.set_default_size(300,300)
		self.optimise_window.set_border_width(5)
		self.optimise_window.set_icon_from_file("/usr/share/lios/Gui/lios")

		self.box = gtk.VBox(False,0)
		label = gtk.Label('<span size="xx-large"><b>Lios-Optimization-Result</b></span>')
		label.set_use_markup(True)
		label.set_selectable(True)
		self.box.pack_start(label,True,True,5)
		label.show()

		label = gtk.Label('<span size="xx-large"><b>Primary-Result</b></span>')
		label.set_use_markup(True)
		label.set_selectable(True)
		self.box.pack_start(label,True,True,5)
		label.show()

		self.notify("Optimising Primary level Please Wait!",True,self.optimise_progress,True)
		if self.keep_running == False:return None # Check to terminate
		a = self.scan_and_count(10)
		if self.keep_running == False:return None # Check to terminate
		b = self.scan_and_count(20)
		if self.keep_running == False:return None # Check to terminate
		c = self.scan_and_count(30)
		if self.keep_running == False:return None # Check to terminate
		d = self.scan_and_count(40)		
		self.notify("Primary test result, 10 = %s, 20 = %s, 30 = %s, 40 = %s"%(a,b,c,d),True,self.optimise_progress,True)
		time.sleep(5)
		if (a >= b) and (a >= c) and (a >= d):
			print ("bigger = %s"%(a))
			add = 10
			mid = a
		if (b >= c) and (b >= d) and (b >= a):
			print ("bigger = %s"%(b))
			add = 20
			mid = b
		if (c >= d) and (c >= a) and (c >= b):
			print ("bigger = %s"%(c))
			add = 30
			mid = c  
		if (d >= a) and (d >= b) and (d >= c):
			print ("bigger = %s"%(d))
			add = 40
			mid = d	
			
		label = gtk.Label('<span size="xx-large"><b>Secondary-Result</b></span>')
		label.set_use_markup(True)
		label.set_selectable(True)
		self.box.pack_start(label,True,True,5)
		label.show()
					
		e = self.scan_and_count(add-5)
		if self.keep_running == False:return None # Check to terminate
		f = self.scan_and_count(add-4)
		if self.keep_running == False:return None # Check to terminate
		g = self.scan_and_count(add-3)
		if self.keep_running == False:return None # Check to terminate
		h = self.scan_and_count(add-2)
		if self.keep_running == False:return None # Check to terminate
		i = self.scan_and_count(add-1)
		if self.keep_running == False:return None # Check to terminate
		j = mid   #MIDIL
		k = self.scan_and_count(add+1)
		if self.keep_running == False:return None # Check to terminate
		l = self.scan_and_count(add+2)
		if self.keep_running == False:return None # Check to terminate
		m = self.scan_and_count(add+3)
		if self.keep_running == False:return None # Check to terminate
		n = self.scan_and_count(add+4)
		if self.keep_running == False:return None # Check to terminate
		o = self.scan_and_count(add+5)	
		if (e >= f) and (e >= g) and (e >= h) and (e >= i) and (e >= j) and (e >= k) and (e >= l) and (e >= m) and (e >= n) and (e >= o):
			self.final_result_brightness = add-5
			self.final_result_word_count = e 
		if (f >= e) and (f >= g) and (f >= h) and (f >= i) and (f >= j) and (f >= k) and (f >= l) and (f >= m) and (f >= n) and (f >= o):
			self.final_result_brightness = add-4
			self.final_result_word_count = f 			
		if (g >= f) and (g >= e) and (g >= h) and (g >= i) and (g >= j) and (g >= k) and (g >= l) and (g >= m) and (g >= n) and (g >= o):
			self.final_result_brightness = add-3
			self.final_result_word_count = g
		if (h >= f) and (h >= g) and (h >= e) and (j >= i) and (h >= j) and (h >= k) and (h >= l) and (h >= m) and (h >= n) and (h >= o):
			self.final_result_brightness = add-2
			self.final_result_word_count = h
		if (i >= f) and (i >= g) and (i >= h) and (i >= e) and (i >= j) and (i >= k) and (i >= l) and (i >= m) and (i >= n) and (i >= o):
			self.final_result_brightness = add-1
			self.final_result_word_count = i
		if (j >= f) and (j >= g) and (j >= h) and (j >= i) and (j >= e) and (j >= k) and (j >= l) and (j >= m) and (j >= n) and (j >= o):
			self.final_result_brightness = add
			self.final_result_word_count = j
		if (k >= f) and (k >= g) and (k >= h) and (k >= i) and (k >= j) and (k >= e) and (k >= l) and (k >= m) and (k >= n) and (k >= o):
			self.final_result_brightness = add+1
			self.final_result_word_count = k
		if (l >= f) and (l >= g) and (l >= h) and (l >= i) and (l >= j) and (l >= k) and (l >= e) and (l >= m) and (l >= n) and (l >= o):
			self.final_result_brightness = add+2
			self.final_result_word_count = l
		if (m >= f) and (m >= g) and (m >= h) and (m >= i) and (m >= j) and (m >= k) and (m >= l) and (m >= e) and (m >= n) and (m >= o):
			self.final_result_brightness = add+3
			self.final_result_word_count = m
		if (n >= f) and (n >= g) and (n >= h) and (n >= i) and (n >= j) and (n >= k) and (n >= l) and (n >= m) and (n >= e) and (n >= o):
			self.final_result_brightness = add+4
			self.final_result_word_count = n
		if (o >= f) and (o >= g) and (o >= h) and (o >= i) and (o >= j) and (o >= k) and (o >= l) and (o >= m) and (o >= n) and (o >= e):
			self.final_result_brightness = add+5
			self.final_result_word_count = o		
		self.clean()
		if self.keep_running == False:return None # Check to terminate

		label = gtk.Label('<span size="xx-large"><b>Final-Result = %s With %s Words!</b></span>'%(self.final_result_brightness,self.final_result_word_count))
		label.set_use_markup(True)
		label.set_selectable(True)
		self.box.pack_start(label,True,True,5)
		label.show()

		apply_button = gtk.Button("Apply")
		apply_button.connect("clicked",self.apply_pressed,None)
		self.box.pack_start(apply_button)
		apply_button.show()
		close_button = gtk.Button("Close")
		close_button.connect("clicked",self.close_pressed,None)
		self.box.pack_start(close_button)
		close_button.show()
		self.box.show()
		self.optimise_window.add(self.box)
		self.notify("Compleated !",True,None,True)
		self.optimise_window.present()
		gtk.gdk.threads_enter()
		self.optimise_window.show()
		gtk.gdk.threads_leave()		
		
		
	def apply_pressed(self,wedget,data=None):
		self.notify("Lios ,Brightness Updated!",True,None,True)
		self.scan_brightness=self.final_result_brightness
		self.optimise_window.destroy()
		gtk.gdk.threads_leave()	
	def close_pressed(self,wedget,data=None):
		self.notify("Ok !",True,None,True)
		self.optimise_window.destroy()
		gtk.gdk.threads_leave()

if __name__ == '__main__':
	linux_intelligent_ocr_solution()

