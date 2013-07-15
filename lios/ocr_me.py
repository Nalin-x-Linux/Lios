import os
import sys
import gtk
import time
import shutil
import multiprocessing
from subprocess import *
class do:
	def __init__(self,name,engine,language):
		self.name = name
		self.engine = engine
		self.language = language
		os.system("convert %s.pnm image"%(self.name))
		if self.engine == "CUNEIFORM":
			self.cuneiform("%s"%(self.name),"%s"%(self.language))
		elif self.engine == "TESSERACT":
			self.tesseract("%s"%(self.name),"%s"%(self.language))
		else:
			self.counter = 1
			os.system("convert %s.pnm image.tif"%(self.name))			
			os.system("convert %s.pnm %s.tif"%(self.name,self.name))
			self.block_count = 0 
			self.image_l_list = []
			self.image_t_list = []
			self.image_r_list = []
			self.image_b_list = []
			self.drawing_count = 0
			self.block_l_list = []
			self.block_t_list = []
			self.block_r_list = []
			self.block_b_list = []		
			result = Popen(["i-layout","image.tif"],stdout=PIPE)
			for line in result.stdout:
				if "File-Name" in line:
					print line			
				if "Height" in line:
					self.height = int(line[9:])			
					print self.height			
				if "drawing" in line:
					words=line.split()
					for word in words:
						if "X=" in word:
							x = int(word[2:])
						if "Y=" in word:
							y = int(word[2:])
						if "W=" in word:
							Image_w = int(word[2:])
						if "H=" in word:
							Image_h = int(word[2:])
					self.image_l_list.append(x)
					self.image_t_list.append(y)
					self.image_r_list.append(x+Image_w)
					self.image_b_list.append(y+Image_h)
					self.drawing_count = self.drawing_count + 1	
					print "B-Imange L=",x,"T=",y,"R=",x+Image_w,"B=",y+Image_h
				if "Block" in line:
					words=line.split()
					for word in words:
						if "T=" in word:
							t = self.height-int(word[2:])
						if "B=" in word:
							b = self.height-int(word[2:])
						if "R=" in word:
							r = word[2:]
						if "L=" in word:
							l = word[2:]
					width = int(l)-int(r)
					height = int(t)-int(b)
					if self.drawing_count == 0:
						if (~width > 25) & (~height > 25):
							block_information = open("/usr/share/lios/Block.txt",'w')
							block_information.write("%s %s %s %s\n"%(0,0,~width,~height))
							block_information.close()
							os.system("convert BinImg.tif -crop %sx%s+%s+%s BinImgBlock.tif" %(~width,~height,int(l),int(t)))
							#os.system("cp BinImgBlock.tif %s" % self.counter)
							#self.counter = self.counter + 1
							os.system("./wordocr BinImgBlock.tif temp.txt Block.txt /usr/share/lios/mal_1000_32_32.model /usr/share/lios/MAPS/")
						self.block_l_list.append(l)
						self.block_t_list.append(t)
						self.block_r_list.append(r)
						self.block_b_list.append(b)
						self.block_count = self.block_count + 1
					else:
						if (~width > 25) & (~height > 25):
							self.block_l_list.append(l)
							self.block_t_list.append(t)
							self.block_r_list.append(r)
							self.block_b_list.append(b)
							self.block_count = self.block_count + 1
			self.o_count = 1
			for j in range (0,self.block_count):
				bl = int(self.block_l_list[j])
				bt = int(self.block_t_list[j])
				br = int(self.block_r_list[j])
				bb = int(self.block_b_list[j])
				block_area = (br-bl)*(bb-bt)
				for i in range(0,self.drawing_count):
					il = int(self.image_l_list[i])
					it = int(self.image_t_list[i])
					ir = int(self.image_r_list[i])
					ib = int(self.image_b_list[i])
					image_area = (ir-il)*(ib-it)
					
					print "Block area = ",block_area
					overlap_width = 0
					overlap_height = 0
					for y in range(it,ib):
						if y<bb:
							overlap_height = overlap_height + 1
					print "overlap_height : ",overlap_height
					for x in range(il,ir):
						if x<br:
							overlap_width = overlap_width + 1
					print "overlap_width : ",overlap_width					
					overlap_area = overlap_height*overlap_width
					print "overlap_area : ",overlap_area
					if block_area < image_area:
						big_area = image_area
					else:
						big_area = block_area
					try:
						overlap = big_area/overlap_area
					except ZeroDivisionError:
						overlap = 0
					else:
						pass
					print "Overlap : ",overlap
					if overlap == 1:
						pass
					else:
						if (br-bl > 15) & (bb-bt > 15):
							block_information = open("/usr/share/lios/Block.txt",'w')
							block_information.write("%s %s %s %s\n"%(0,0,br-bl,bb-bt))
							block_information.close()
							os.system("convert BinImg.tif -crop %sx%s+%s+%s BinImgBlock.tif" %(br-bl,bb-bt,bl,bt))
							#os.system("cp BinImgBlock.tif %s" % self.counter)
							#self.counter = self.counter + 1
							os.system("./wordocr BinImgBlock.tif temp.txt Block.txt /usr/share/lios/mal_1000_32_32.model /usr/share/lios/MAPS/")
							self.o_count = self.o_count + 1
						break						
				
	def cuneiform(self,image,language):
		os.system("convert -compress none %s.pnm %s.bmp"%(image,image))
		os.system("cuneiform -f text -l %s -o %s.txt %s.bmp"%(language,image,image))

	def tesseract(self,image,language):
		os.system("convert %s.pnm %s.png"%(image,image))
		os.system("tesseract %s.png %s -l %s"%(image,image,language))

