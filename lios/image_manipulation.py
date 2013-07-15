################# User interface Image Manipulation #######################################################

# Threading libraries
import threading
import multiprocessing


import gtk
import gnomecanvas
import os
import shutil

from skew import *


class image_manipulation():
	def on_Deskew_Image_activate(self,wedget,data=None):
		self.notify("Correcting skew, please wait!",True,None,True)
		threading.Thread(target=self.skew_1,args=()).start()

	def skew_1(self):
		process=multiprocessing.Process(target=self.skew_2,args=())
		process.start()
		while process.is_alive():
			pass
		self.set_image(self)
		self.notify("Completed!",False,None,True)

	def skew_2(self):
		image_deskewer = ImageDeskewer()
		os.system("convert image work.jpg")
		image_deskewer.deskew("work.jpg", "image")

	def set_image(self,widget,data=None):
		if self.first_run == False:
			self.im_widget.destroy()
		else:
			self.first_run = False
		try:
			self.pixbuf = gtk.gdk.pixbuf_new_from_file("image")
		except:
			shutil.copy("/usr/share/lios/Gui/lios","image")
			self.pixbuf = gtk.gdk.pixbuf_new_from_file("image")
		else:
			pass
		self.width = self.pixbuf.get_width()
		self.height = self.pixbuf.get_height()
		self.vruler.set_range(0.0, float(self.height), 0.0, float(self.height))
		self.hruler.set_range(0.0, float(self.width), 0.0, float(self.width))
		self.im_widget = self.canvas.root().add(gnomecanvas.CanvasPixbuf, x=0, y=0, pixbuf=self.pixbuf)		
		self.canvas.set_scroll_region(0, 0, self.width, self.height)
		self.zoom_level = 0
		self.notify("Ok !",True,None,False)
	
	def clear_selection(self,widget):
		self.rubberband.destroy()
		os.remove("selected")
		self.clean()
		
	def motion_notify(self,ruler, event):
		return ruler.emit("motion_notify_event", event)
								
	def zoom_in(self,wedget,data=None):
		self.im_widget.destroy()
		self.width = self.width*2
		self.height = self.height*2
		self.pixbuf = self.pixbuf.scale_simple(self.width, self.height, gtk.gdk.INTERP_HYPER)
		self.canvas.set_scroll_region(0, 0, self.width, self.height)
		self.im_widget = self.canvas.root().add(gnomecanvas.CanvasPixbuf, x=0, y=0, pixbuf=self.pixbuf)
		self.zoom_level = self.zoom_level - 2
		self.vruler.set_range(0.0, float(self.height), 0.0, float(self.height))
		self.hruler.set_range(0.0, float(self.width), 0.0, float(self.width))

	def zoom_out(self,wedget,data=None):
		self.im_widget.destroy()
		self.width = self.width/2 
		self.height = self.height/2
		self.pixbuf = self.pixbuf.scale_simple(self.width, self.height, gtk.gdk.INTERP_HYPER)
		self.canvas.set_scroll_region(0, 0, self.width, self.height)
		self.im_widget = self.canvas.root().add(gnomecanvas.CanvasPixbuf, x=0, y=0, pixbuf=self.pixbuf)
		self.zoom_level = self.zoom_level + 2
		self.vruler.set_range(0.0, float(self.height), 0.0, float(self.height))
		self.hruler.set_range(0.0, float(self.width), 0.0, float(self.width))

				
	def rotate_right(self,wedget,data=None):
		os.system("convert -rotate 90 image image")
		self.set_image(self)
	def rotate_left(self,wedget,data=None):
		os.system("convert -rotate 270 image image")
		self.set_image(self)

	def hide_show(self,wedget,data=None):
		if self.image_frame.get_visible():
			self.image_frame.hide()
		else:
			self.image_frame.show()
			
	def ui_image_save(self,wedget,data=None):
		save_image = gtk.FileChooserDialog(title="Save..",action=gtk.FILE_CHOOSER_ACTION_SAVE,
		                     buttons=(gtk.STOCK_SAVE,gtk.RESPONSE_OK)) 
		save_image.set_current_folder("%s/Lios"%(os.environ['HOME']))		
		filter = gtk.FileFilter()
		for pattern in "*.png","*.pnm","*.jpg","*.jpeg","*.tif","*.tiff","*.bmp","*.pbm":
			filter.add_pattern(pattern)
		save_image.add_filter(filter) 
		response = save_image.run()		
		if response == gtk.RESPONSE_OK:
			save_name = "%s"%(save_image.get_filename())
			if "." in save_name:
				os.system("convert image %s"%(save_name.replace(" ","\ ")))
				save_image.destroy()
			else:
				os.system("convert image %s.jpg"%(save_name.replace(" ","\ ")))
				save_image.destroy()

	# Returns a referance to a rectangle drawn on the canvas
	def get_rect(self, x, y):
		itemType = gnomecanvas.CanvasRect
		rect = self.canvas.root().add(itemType, x1=x, y1=y, x2=x, y2=y, #0x0 dimensions at first
						fill_color_rgba=0xFFCC3355, outline_color_rgba=0xFFEECC99,
						width_units=1.0)
		return rect

	def canvas_event(self, widget, event):
		# Creates a rubberband on left-click
		if (event.type == gtk.gdk.BUTTON_PRESS):
			if (event.button == 1):
				self.dragging = True
				self.startx = event.x
				self.starty = event.y
				try:
					self.rubberband.destroy()
				except:
					pass
				self.rubberband = self.get_rect(self.startx, self.starty)

		# Updates the rubberband size while a mouse drags
		if (event.type == gtk.gdk.MOTION_NOTIFY) and (self.dragging):
			self.rubberband.set(x2=event.x, y2=event.y)

		# Destroys the rubberband and sends selection data to the relevant method
		if (event.type == gtk.gdk.BUTTON_RELEASE) and (self.dragging):
			if (event.button == 1):
				self.dragging = False
				self.endx = event.x
				self.endy = event.y
				self.rubberband.set(x2=self.endx, y2=self.endy)
				
				# Finding Real X1 X2 Y1 Y2
				if self.startx > self.endx:
					temp = self.startx;
					self.startx = self.endx; 
					self.endx = temp;
				if self.starty > self.endy:
					temp = self.starty;
					self.starty = self.endy; 
					self.endy = temp;
				
				# Resetting to original values	
				if self.zoom_level == 0:
					self.startx,self.starty,self.endx,self.endy = int(self.startx),int(self.starty),int(self.endx),int(self.endy)
				elif self.zoom_level < 0:
					self.startx,self.starty,self.endx,self.endy = int(self.startx)/self.zoom_level,int(self.starty)/self.zoom_level,int(self.endx)/self.zoom_level,int(self.endy/self.zoom_level)
				else:
					self.startx,self.starty,self.endx,self.endy = int(self.startx*self.zoom_level),int(self.starty*self.zoom_level),int(self.endx*self.zoom_level),int(self.endy*self.zoom_level)
				
				self.select([abs(self.startx),abs(self.starty),abs(self.endx),abs(self.endy)])

	def select(self, selection):
		os.system("convert image -crop %sx%s+%s+%s selected" %(int(selection[2])-int(selection[0]),int(selection[3])-int(selection[1]),int(selection[0]),int(selection[1])))
