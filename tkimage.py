from Tkinter import *
from PIL import Image, ImageTk, ImageFilter, ImageEnhance
import os

class Application(Frame):
	def __init__(self, master=None, image1=None, image2=None, image3=None, title=None):
		Frame.__init__(self, master)
		self.master = master
		if not title:
			title = image1
		if not title:
			title = "No Image"
		if title:
			master.iconbitmap(os.path.join(os.path.dirname(__file__), 'favicon.ico'))
		else:
			master.iconbitmap(os.path.join(os.path.dirname(__file__), 'nofavicon.ico'))
		self.image1 = image1
		self.image2 = image2
		self.image3 = image3
		self.size1 = (0, 0)
		self.size2 = (0, 0)
		self.size3 = (0, 0)
		
		master.wm_title(title)
		self.pack()
		# self.createWidgets(image1)
		master.resizable(0,0)
		if image1:
			if os.path.isfile(image1):
				self.showImage1()
				if image2:
					if os.path.isfile(image2):
						self.showImage2()
					self.showNextButton()
		else:
			self.showNoImage(master)
		# if name:
		# 	self.label0 = Label(self, text=name, relief=SUNKEN, height=10, font='Consolas 10 bold')
		# 	self.label0.grid(row=1, column=0, padx=5, pady=5, rowspan=150)

		self.binder(master)
		# print "self.size1 =", self.size1
		# print "self.size2 =", self.size2
		# print "self.size3 =", self.size3
		# if not image3:
		# else:
		self.first_center()
		self.center()

	def first_center(self, final_width=None, final_height=None):
		all_size_width = [self.size1[0], self.size2[0], self.size3[0]]
		all_size_height = [self.size1[1], self.size2[1], self.size3[1]]
		if not self.image2:
			self.master.geometry("%sx%s+30+30"%(str(max(all_size_width)), str(max(all_size_width))))
		else:
			if not final_width:
				if self.image3:
					final_width = sum(all_size_width) + 70
				else:
					final_width = sum(all_size_width) + 40
			if not final_height:
				if self.image3:
					final_height = max(all_size_height[:-1])
				else:
					final_height = max(all_size_height) + 30
			# else:
			# 	final_width = sum(all_size_width)
			# 	final_height = max(all_size_height)
			self.master.geometry("%sx%s+30+30"%(
				str(final_width), 
				str(final_height)
			  )
			)

	def center(self):
		"""
		centers a tkinter window
		:param win: the root or Toplevel window to center
		"""
		self.master.update_idletasks()
		width = self.master.winfo_width()
		frm_width = self.master.winfo_rootx() - self.master.winfo_x()
		win_width = width + 2 * frm_width
		height = self.master.winfo_height()
		titlebar_height = self.master.winfo_rooty() - self.master.winfo_y()
		win_height = height + titlebar_height + frm_width
		x = self.master.winfo_screenwidth() // 2 - win_width // 2
		y = self.master.winfo_screenheight() // 2 - win_height // 2
		self.master.geometry('{}x{}+{}+{}'.format(width, height, x, y))
		self.master.deiconify()

	def quitX(self, event=None):
		self.destroy()
		sys.exit()

	def binder(self, master):
		if self.image2:
			if self.image3:
				if os.path.isfile(self.image3):
					master.bind("n", self.showImage3)
		master.bind("q", self.quitX)

	def showNoImage(self, master):
		master.iconbitmap(os.path.join(os.path.dirname(__file__), 'nofavicon.ico'))
		self.label1 = Label(self, text="No Image", relief=SUNKEN, width=20, height=10, font='Consolas 28 bold')
		self.label1.grid(row=0, column=0, padx=5, pady=5, rowspan=10)

	def showImage1(self, event=None):
		if self.image1:
			self.img = Image.open(self.image1)
			self.size1 = self.img.size
			# print "self.size1 0 =", self.size1
			self.photo1 = ImageTk.PhotoImage(self.img.convert("RGB"))
			self.label1 = Label(self, image=self.photo1)
			self.label1.grid(row=0, column=0, padx=5, pady=5, rowspan=10)

	def showImage2(self, event=None):
		if self.image2:
			img = Image.open(self.image2)
			self.size2 = img.size
			# print "self.size2 0 =", self.size2
			self.photo2 = ImageTk.PhotoImage(img.convert("RGB"))
			self.label2 = Label(self, image=self.photo2)
			self.label2.grid(row=0, column=1, padx=5, pady=5, rowspan=10)

	def showImage3(self, event=None):
		self.label2.grid(rowspan=1)
		if self.image3:
			img = Image.open(self.image3)
			self.size3 = img.size
			# print "self.size3 0 =", self.size3
			all_size_width = [self.size1[0], self.size2[0], self.size3[0]]
			all_size_height = [self.size1[1], self.size2[1], self.size3[1]]
			final_width = sum(all_size_width[:-1]) + 70
			final_height = sum(all_size_height[1:]) + 40
			self.first_center(final_width, final_height)
			self.photo3 = ImageTk.PhotoImage(img.convert("RGB"))
			self.label3 = Label(self, image=self.photo3)
			self.label3.grid(row=1, column=1, padx=5, pady=5, rowspan=10)
		self.center()

	def showNextButton(self):
		if self.image2 and self.image3:
			button5 = Button(self, text="Next", command=self.showImage3)
			button5.grid(row=4, column= 2, sticky = N)

	def sharpen(self):
		img2 = self.img.filter(ImageFilter.SHARPEN)
		self.photo2 = ImageTk.PhotoImage(img2)
		self.label2 = Label(self, image=self.photo2)
		self.label2.grid(row=0, column=1, padx=5, pady=5, rowspan=10)

	def showOther(self, event=None):
		self.label2.grid(rowspan=1)
		img = Image.open(self.image2)
		self.photo3 = ImageTk.PhotoImage(img)
		self.label3 = Label(self, image=self.photo3)
		self.label3.grid(row=1, column=1, padx=5, pady=5, rowspan=10)

def showImages(title="", image1=None, image2=None, image3=None):
	root = Tk()
	root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
	c = Application(root, image1, image2, image3, title)
	c.mainloop()	

if __name__ == '__main__':
	# import sys
	# root = Tk()
	# root.eval('tk::PlaceWindow %s center' % root.winfo_pathname(root.winfo_id()))
	# c = Application(root, sys.argv[1], sys.argv[2], sys.argv[3], "TEST Image V")
	# c.mainloop()
	showImages(*sys.argv[1:])
