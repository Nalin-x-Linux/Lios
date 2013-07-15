# coding: latin-1
import sys
import os
import gtk
import enchant
from espeak import espeak
import threading
import multiprocessing
import time

class lios_tools:		

# FUNCTION TO CLEAN LIOS DIRECTORY #
	def clean(self):
		grabage_formats = ['txt','text','pnm','tif','tiff','html','wav','bmp','pyc','png','jpeg','jpg','pdf','pbm','ppm']
		for garbage in os.listdir(os.getcwd()):
			try:
				if garbage.split(".")[1] in grabage_formats:
					os.remove(garbage)
			except IndexError:
				pass
		print "Clean   		          [ Ok ]"
			

# FUNCTION TO COUNT WORDS IN A FILE #	
	def count_me(self,file_name_to_count):
		count = 1
		try:
			file = open(file_name_to_count)
			text = file.read().decode('utf8')
			for word in text.split(" "):
				try:
					if self.dict.check(word) == True:
						count = count + 1
				except:
					pass
					
		except IOError:
			count = 1
		return count
	

    # Read the text
	def Read_Stop(self,wedget,data=None):
		image_read_stop = self.guibuilder.get_object("image_read_stop")
		if espeak.is_playing() == False:
			image_read_stop.set_from_file("/usr/share/lios/Gui/stop")
			self.textbuffer.remove_tag(self.highlight_tag, self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			mark = self.textbuffer.get_insert()
			start = self.textbuffer.get_iter_at_mark(mark)
			end = self.textbuffer.get_end_iter()
			self.to_count = start.get_offset()
			text = self.textbuffer.get_text(start,end)
			espeak.synth(text)
			self.textview.set_editable(False)
		else:
			espeak.cancel()
			image_read_stop.set_from_file("/usr/share/lios/Gui/play")
			self.textbuffer.remove_tag(self.highlight_tag, self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			self.textview.set_editable(True)
			
		
	def espeak_event(self, event, pos, length):
		gtk.gdk.threads_enter()
		if event == espeak.core.event_WORD:
			pos += self.to_count-1
			s = self.textbuffer.get_iter_at_offset(pos)
			e = self.textbuffer.get_iter_at_offset(length+pos)			
			
			self.textbuffer.remove_all_tags(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			self.textbuffer.apply_tag(self.highlight_tag, s, e)

		if event == espeak.event_END:
			self.point = self.textbuffer.get_iter_at_offset(pos+self.to_count)
			self.textbuffer.place_cursor(self.point)
			self.textview.scroll_to_iter(self.point, 0.0, use_align=True, xalign=0.0, yalign=0.2)

							
					
		if event == espeak.event_MSG_TERMINATED:
			espeak._playing = False
			self.textview.set_editable(True)
			try:
				self.textbuffer.remove_all_tags(self.textbuffer.get_start_iter(),self.textbuffer.get_end_iter())
			except:
				pass
		
		if not espeak.is_playing():
			mark = self.textbuffer.get_insert()
			start = self.textbuffer.get_iter_at_mark(mark)
			end = self.textbuffer.get_end_iter()
			self.to_count = start.get_offset()
			text = self.textbuffer.get_text(start,end)
			if text != "":
				espeak.synth(text)			
		gtk.gdk.threads_leave()	
		return True
		
		
#  FUNCTION TO CHECK SPELLING		
	def spell_checker(self,data=None):
		#Builder And Gui
		builder = gtk.Builder()
		builder.add_from_file("/usr/share/lios/Gui/Spell.glade")
		self.spell_window = builder.get_object("window")
		builder.connect_signals(self)
		self.entry = builder.get_object("entry")
		
		self.liststore = gtk.ListStore(str)
		self.treeview = builder.get_object("treeview")
		
		self.treeview.connect("row-activated",self.activate_treeview)
		
		self.treeview.set_model(self.liststore)
		column = gtk.TreeViewColumn("Suggestions : ")
		self.treeview.append_column(column)		
		cell = gtk.CellRendererText()
		column.pack_start(cell, False)
		column.add_attribute(cell, "text", 0)
		
					
		self.user_dict={}
		mark = self.textbuffer.get_insert()
		self.word_start = self.textbuffer.get_iter_at_mark(mark)
		self.word_end = self.textbuffer.get_iter_at_mark(mark)

		self.word = self.textbuffer.get_text(self.word_start,self.word_end)	
		while(True):
			try:
				if self.dict.check(self.word) == False and len(self.word) > 1:
					break
			except enchant.errors.Error:
				pass
			else:
				pass
			self.word_start.forward_word_ends(2)
			self.word_end.forward_word_end()
			self.word_start.backward_word_start()
			self.word = self.textbuffer.get_text(self.word_start,self.word_end)
			self.textview.scroll_to_iter(self.word_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
		
		
		self.liststore.clear()
		for item in self.dict.suggest(self.word):
			self.liststore.append([item])
			
		
		self.context_sentence_start = self.word_start.copy()
		self.context_sentence_end = self.word_start.copy()
		self.context_sentence_start.backward_sentence_start()
		self.context_sentence_end.forward_sentence_end()		
		self.textbuffer.apply_tag(self.highlight_tag,self.context_sentence_start,self.context_sentence_end)
		
		self.entry.set_text(self.word)
		self.spell_window.show()
	
	def activate_treeview(self,widget, row, col):
		model = widget.get_model()
		text = model[row][0]
		self.entry.set_text(text)
		self.entry.grab_focus()  

	def say_context(self,data=None):
		context_sentence_start = self.word_start.copy()
		context_sentence_end = self.word_start.copy()
		context_sentence_start.backward_sentence_start()
		context_sentence_end.forward_sentence_end()
		self.notify(self.textbuffer.get_text(context_sentence_start,context_sentence_end),False,None,True)
				
	def close(self,widget,data=None):
		self.spell_window.destroy()	

	def change(self,data=None):
		self.textbuffer.remove_tag(self.highlight_tag,self.context_sentence_start,self.context_sentence_end)
		self.textbuffer.delete(self.word_start, self.word_end)
		self.textbuffer.insert(self.word_start, self.entry.get_text())
		self.entry.set_text("")
		self.word_start.forward_word_end()
		self.word_end = self.word_start.copy()
		self.word_start.backward_word_starts(1)		
		self.word = self.textbuffer.get_text(self.word_start,self.word_end)
		self.find_next_miss_spelled()
		
		
	def change_all(self,data=None):
		self.textbuffer.delete(self.word_start, self.word_end)
		self.textbuffer.insert(self.word_start, self.entry.get_text())
		self.user_dict[self.word] = self.entry.get_text()
		self.entry.set_text("")
		self.word_start.forward_word_end()
		self.word_end = self.word_start.copy()
		self.word_start.backward_word_starts(1)		
		self.word = self.textbuffer.get_text(self.word_start,self.word_end)
		self.entry.set_text("")
		self.word_start.forward_word_end()
		self.word_end = self.word_start.copy()
		self.word_start.backward_word_starts(1)		
		self.find_next_miss_spelled()

	def ignore(self,data=None):
		self.entry.set_text("")
		self.word_start.forward_word_ends(2)
		self.word_end = self.word_start.copy()
		self.word_start.backward_word_starts(1)
		self.find_next_miss_spelled()	

	def ignore_all(self,data=None):
		if self.dict.is_added(self.word) == False:
			self.dict.add(self.word)
		self.entry.set_text("")
		self.word_start.forward_word_ends(2)
		self.word_end = self.word_start.copy()
		self.word_start.backward_word_starts(1)	
		self.find_next_miss_spelled()	

	def find_next_miss_spelled(self):
		self.textbuffer.remove_tag(self.highlight_tag,self.context_sentence_start,self.context_sentence_end)
		if self.word_end.is_end() == True:
			try:
				self.textbuffer.get_text(sentence_start,sentence_end)
			except NameError:
				self.notify("Spell Checking Compleated!",True,0,True)
				self.spell_window.destroy()
			else:
				pass	
			
		self.word = self.textbuffer.get_text(self.word_start,self.word_end)
		while(True):
			try:
				if self.dict.check(self.word) == False and len(self.word) > 1: 
					break
			except enchant.errors.Error:
				pass
			else:
				pass
			if self.word in self.user_dict.keys():
				self.textbuffer.delete(self.word_start, self.word_end)
				self.textbuffer.insert(self.word_start, self.user_dict[self.word])
				self.entry.set_text("")
				self.word_start.forward_word_end()
				self.word_end = self.word_start.copy()
				self.word_start.backward_word_starts(1)		
				self.word = self.textbuffer.get_text(self.word_start,self.word_end)
			else:
				self.word_start.forward_word_ends(2)
				self.word_end.forward_word_end()
				self.word_start.backward_word_start()
				self.word = self.textbuffer.get_text(self.word_start,self.word_end)
		
		
		self.context_sentence_start = self.word_start.copy()
		self.context_sentence_end = self.word_start.copy()
		self.context_sentence_start.backward_sentence_start()
		self.context_sentence_end.forward_sentence_end()		
		self.textbuffer.apply_tag(self.highlight_tag,self.context_sentence_start,self.context_sentence_end)
		self.textview.scroll_to_iter(self.word_start, 0.2, use_align=False, xalign=0.5, yalign=0.5)
		
		
		
		self.entry.set_text(self.word)
		self.liststore.clear()
		for item in self.dict.suggest(self.word):
			self.liststore.append([item])
		
		self.entry.grab_focus()
		
		
	def audio_converter(self,wedget,data=None):
		try:
			start,end = self.textbuffer.get_selection_bounds()
		except ValueError:
			self.notify("Nothing selected!",False,None,True)
		else:
			self.text_to_convert = self.textbuffer.get_text(start,end)
			to_convert = open("temp.txt",'w')
			to_convert.write(self.text_to_convert)
			to_convert.close()
			
			
			glade_file = "/usr/share/lios/Gui/audio_converter.glade"
			tree = gtk.glade.XML(glade_file)
			self.audio_converter_window = tree.get_widget("window")
			signals = {"close" : self.close_audio_converter,
			"convert_to_audio" : self.convert_to_audio}
			tree.signal_autoconnect(signals)
			
			self.spinbutton_speed = tree.get_widget("spinbutton_speed")
			self.spinbutton_speed.set_value(self.voice_message_rate)
			self.spinbutton_pitch = tree.get_widget("spinbutton_pitch")
			self.spinbutton_pitch.set_value(self.voice_message_pitch)
			self.spinbutton_split = tree.get_widget("spinbutton_split")
			self.spinbutton_vloume = tree.get_widget("spinbutton_vloume")
			self.spinbutton_vloume.set_value(self.voice_message_volume)
			
			voice = tree.get_widget("combobox_language_convert")
			for item in self.voice_list:
				voice.append_text(item)
			voice.connect('changed', self.change_voice)
			voice.set_active(self.voice_message_voice)
			self.audio_converter_window.show()		                

	def change_voice(self, voice):
		self.model_voice = voice.get_model()
		self.index_voice = voice.get_active()
		
	def close_audio_converter(self,widget,data=None):
		self.audio_converter_window.destroy()	
		
	def convert_to_audio(self,widget,data=None):
		self.filename = gtk.FileChooserDialog("Type the output wav name",
                               None,
                               gtk.FILE_CHOOSER_ACTION_SAVE,
                               (gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_SAVE, gtk.RESPONSE_OK))
                self.filename.set_current_folder("%s/Lios"%(os.environ['HOME']))
                self.filename.run()
                self.file_to_output = self.filename.get_filename()
                self.filename.destroy()
                threading.Thread(target=self.record_to_wave,args=()).start()
                self.audio_converter_window.destroy()
		
	def record_to_wave(self):
		self.notify("Converting Please Wait!",True,0,True)
		convert_ps = multiprocessing.Process(target=self.convert_function)
		convert_ps.start()
		while convert_ps.is_alive():
			time.sleep(.05)
			self.progressbar.pulse()	
		self.notify("Convertion Done!",True,1,True)
		self.clean()
	def convert_function(self):
		os.system('espeak -a %s -v %s -f temp.txt -w %s.wav --split=%s -p %s -s %s' % (self.spinbutton_vloume.get_value(),self.model_voice[self.index_voice][0],self.file_to_output,self.spinbutton_split.get_value(),self.spinbutton_pitch.get_value(),self.spinbutton_speed.get_value()))

# Find_and_Replace Functions
	def on_Find_Replace_activate(self,wedget,data=None):
		#Builder And Gui
		self.find_and_replace_builder = gtk.Builder()
		self.find_and_replace_builder.add_from_file("/usr/share/lios/Gui/find_and_replace.glade")
		self.find_and_replace_window = self.find_and_replace_builder.get_object("window")
		self.entry_word = self.find_and_replace_builder.get_object("entry_word")
		self.entry_replace_word = self.find_and_replace_builder.get_object("entry_replace_word")
		self.find_and_replace_builder.connect_signals(self)
		self.find_and_replace_window.show()
		
	def on_Find_and_Replace_Close_clicked(self,wedget,data=None):
		try:
			del self.replace_end_iter
		except AttributeError:
			pass
		self.find_and_replace_window.destroy()

	def on_Find_and_Replace_Find_activate(self,wedget,data=None):
		word = self.entry_word.get_text()
		try:
			self.replace_end_iter
		except AttributeError:
			self.replace_end_iter = self.textbuffer.get_start_iter()
		
		res = self.replace_end_iter.forward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)
		if not res:	res = self.replace_end_iter.backward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)
		if res:
			self.replace_start_iter, self.replace_end_iter = res;
			self.textbuffer.select_range(self.replace_start_iter, self.replace_end_iter)
			self.textview.scroll_to_iter(self.replace_end_iter, 0.0)

			
					
				
	def on_Find_and_Replace_Say_Context_activate(self,wedget,data=None):
		context_sentence_start = self.replace_end_iter.copy()
		context_sentence_end = self.replace_end_iter.copy()
		context_sentence_start.backward_sentence_start()
		context_sentence_end.forward_sentence_end()
		self.notify(self.textbuffer.get_text(context_sentence_start,context_sentence_end),False,None,True)

	def on_Find_and_Replace_Replace_activate(self,wedget,data=None):
		replace_word = self.entry_replace_word.get_text()
		self.textbuffer.delete(self.replace_start_iter, self.replace_end_iter)
		self.textbuffer.insert(self.replace_end_iter,replace_word)
		self.on_Find_and_Replace_Find_activate(self)
		
		
		
	def on_Find_and_Replace_Replace_All_activate(self,wedget,data=None):
		word = self.entry_word.get_text()
		replace_word = self.entry_replace_word.get_text()
		try:
			self.replace_end_iter
		except:
			self.replace_end_iter = self.textbuffer.get_start_iter()
		while(1):
			res = self.replace_end_iter.forward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)
			if not res:	res = self.replace_end_iter.backward_search(word, gtk.TEXT_SEARCH_TEXT_ONLY)
			if res:
				self.replace_start_iter, self.replace_end_iter = res;
				self.textbuffer.delete(self.replace_start_iter, self.replace_end_iter)
				self.textbuffer.insert(self.replace_end_iter,replace_word)
			else:
				break
		try:
			del self.replace_end_iter
		except:
			pass
