#!/usr/bin/env python

from time import localtime, strptime
from datetime import datetime

from Tkinter import *
from os import getenv, system
from PIL import Image, ImageTk 
from glob import glob

dropbox_link = getenv("DROPBOX_LINK")
download_interval = int(getenv("DOWNLOAD_INTERVAL_HOURS")) * 60 * 60 * 1000
carousel_interval = int(getenv("CAROUSEL_INTERVAL_SECONDS")) * 1000
frame_owner = getenv("FRAME_OWNER")
ifttt_key = getenv("IFTTT_KEY")

dropbox_link2 = getenv("DROPBOX_LINK2")
dropbox_link3 = getenv("DROPBOX_LINK3")
dropbox_link4 = getenv("DROPBOX_LINK4")

turn_backlight_on = strptime(getenv("turn_backlight_on"), "%H:%M")
turn_backlight_off = strptime(getenv("turn_backlight_off"), "%H:%M")

base_path = "/usr/src/app/images/"
carrousel_status = True
image_index = 0
image_list = []
initial_init = True
last_command = "none"

def download_images(url,scope):
	archive = base_path + "temp.zip"
	
	remove = "sudo rm -rf " + base_path + scope
	download = "wget -q  "+ url + " -O " + archive
	extract = "unzip -j -n " + archive + " *.jpg -d " + base_path # added *.jpg to get only images, added -j to not make directories -n to skip existing files
	
	system(remove)
	print("download")
	system(download)
	print("extract")
	system(extract)
	print("download_images is done")
	
	
def resize_images():
	images = list_images()
	
	print("resize")
	for file in images:
		img = Image.open(file)
		img = img.resize((640, 480), Image.ANTIALIAS)
		img.save(file, "JPEG")
	
def list_images():
	images = []
	
	dir = base_path + "*.jpg"
	
	images = glob(dir)
	
	return images
	
def previous_image():
	global image_index
	image_index = image_index - 1
	
	if image_index < 0:
		image_index = len(image_list) - 1
	
	image_path = image_list[image_index]
	
	update_image(image_path)
	
def next_image():
	global image_index
	
	if image_index < 1:
		set_backlight()
	
	image_index = image_index + 1
	
	if image_index > len(image_list) - 1:
		image_index = 0
	
	image_path = image_list[image_index]
	
	update_image(image_path)
	
def play_pause():
	global carrousel_status
	
	carrousel_status = not carrousel_status
	
	if(carrousel_status):
		img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/pause.png"))
	else:
		img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/play.png"))
	
	play_button.configure(image=img)
	play_button.image = img
	
def carrousel():
	if(carrousel_status):
		next_image()
	
	root.after(carousel_interval, carrousel)
	
def update_image(image_path):
	img = ImageTk.PhotoImage(Image.open(image_path))
	center_label.configure(image=img)
	center_label.image = img
	
	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/like.png"))
	like_button.configure(image=img)
	like_button.image = img
	
	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/reload_off.png")) # new
	reload_button.configure(image=img)
	reload_button.image = img
	
def initialize():
	global image_list, carrousel_status, initial_init, last_command
	current_carrousel_status = carrousel_status
	carrousel_status = False
	
	download_images(dropbox_link,"*")
	if( len(dropbox_link2) > 4 ):
		download_images(dropbox_link2,"temp.zip")
	if( len(dropbox_link3) > 4 ):
		download_images(dropbox_link3,"temp.zip")
	if( len(dropbox_link4) > 4 ):
		download_images(dropbox_link4,"temp.zip")
	
	resize_images()
	image_list = list_images()
	print (len(image_list))
	
	carrousel_status = current_carrousel_status
	
	if(initial_init):
		initial_init = False
#		root.after(1000, initialize) # removed to stop loading images twice
	else:
		root.after(download_interval, initialize)
	
def send_event():
	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/liked.png"))
	like_button.configure(image=img)
	like_button.image = img
	
	command = "curl -X POST -H \"Content-Type: application/json\" -d '{\"value1\":\"" + frame_owner + "\",\"value2\":\"" + image_list[image_index] + "\"}' https://maker.ifttt.com/trigger/connectedframe_like/with/key/" + ifttt_key
	
	system(command)
	
def force_reload():
	print("reload triggered")
	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/reload_on.png")) # new
	reload_button.configure(image=img)
	reload_button.image = img
	
	img = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/Reload.jpg"))
	center_label.configure(image=img)
	center_label.image = img
	
	root.after(100, initialize)
	
def set_backlight():
#	print("set_backlight()")
	
	local_time=localtime()
	time_now = datetime(local_time.tm_year,local_time.tm_mon,local_time.tm_mday,local_time.tm_hour,local_time.tm_min,local_time.tm_sec)
	time_on = datetime(local_time.tm_year,local_time.tm_mon,local_time.tm_mday,turn_backlight_on.tm_hour,turn_backlight_on.tm_min,local_time.tm_sec)
	time_off = datetime(local_time.tm_year,local_time.tm_mon,local_time.tm_mday,turn_backlight_off.tm_hour,turn_backlight_off.tm_min,local_time.tm_sec)
		
	if time_on < time_now > time_off :
		command = "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"
	else:
		command = "echo 0 > /sys/class/backlight/rpi_backlight/bl_power"
	
#	if time_now < time_on :
#		command = "echo 1 > /sys/class/backlight/rpi_backlight/bl_power"
	
	print(command)
	if command != last_command :
		system(command)
		last_command = command
	
root = Tk()
root.title('Connected Frame')
root.geometry('{}x{}'.format(800, 480))
root.attributes("-fullscreen", True)
root.config(cursor='none')

initialize()

left_column = Frame(root, bg='black', width=80, height=480)
center_column = Frame(root, bg='black', width=640, height=480)
right_column = Frame(root, bg='black', width=80, height=480)

left_column.pack_propagate(0)
center_column.pack_propagate(0)
right_column.pack_propagate(0)

left_column.grid(row=0, column=0, sticky="nsew")
center_column.grid(row=0, column=1, sticky="nsew")
right_column.grid(row=0, column=2, sticky="nsew")

next_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/next.png"))
previous_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/previous.png"))
play_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/pause.png"))
like_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/like.png"))

previous_button = Button(left_column, image=previous_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=previous_image)
next_button = Button(left_column, image=next_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=next_image)
play_button = Button(right_column, image=play_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=play_pause)
like_button = Button(right_column, image=like_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=send_event)

center_image = Image.open(image_list[0])
center_photo = ImageTk.PhotoImage(center_image)
center_label = Label(center_column, image=center_photo)

previous_button.pack(fill=BOTH, expand=1)
next_button.pack(fill=BOTH, expand=1)
center_label.pack(side="bottom", fill=BOTH, expand=1)
play_button.pack(fill=BOTH, expand=1)
like_button.pack(fill=BOTH, expand=1)

reload_icon = ImageTk.PhotoImage(Image.open("/usr/src/app/icons/reload_off.png"))
reload_button = Button(right_column, image=reload_icon, borderwidth=0, background="black", foreground="white", activebackground="black", activeforeground="white", highlightthickness=0, command=force_reload)
reload_button.pack(fill=BOTH, expand=1)

carrousel()

root.mainloop()
