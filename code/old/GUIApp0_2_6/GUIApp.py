#!/usr/bin/env python3
#
#  GUIApp.py
#  Version:0.2.6
#  Git repo: https://github.com/Offlinedevice
#  Offline Device for:
#     Managing GPG local keychain
#     Managing Yubikey 5C NFC. OpenPGP and FIDO2 etc
#     Managing secure and redundant backup for files, accounts and crypto wallets etc
#     Generating offline wallets (and store backup's)
#     Generating and managing private digital ID's (under construction)
#     Managing Bolt Cards for BTC payments 
#     Managing FIDO2 keys for passwordless login
#  
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, 
#  version 2 of the License.

#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
#  See the GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

#  SPDX-License-Identifier: GPL-2.0-only
#  GUIApp.py - Offline device.
#  Copyright (c) 2024 

import sys
import tkinter as tk
from tkinter import *
from tkinter import messagebox, ttk
from tkinter import filedialog
from tkinter import simpledialog
from pathlib import Path
import customtkinter as ctk
from PIL import Image, ImageTk
import gnupg
import shutil
import gzip
import webbrowser
import os
import os.path, time
import glob
import tarfile
import yubico
import usb.core
import usb.backend.libusb1
import subprocess
import time
from datetime import date
from tkcalendar import Calendar,DateEntry 
from tktimepicker import AnalogPicker, AnalogThemes,constants
import csv
import bip32utils
from mnemonic import Mnemonic
import bech32
import base58
from datetime import datetime
from typing import Optional
import hashlib
from functools import partial
import qrcode
import boltlib
from random import SystemRandom
from pywallet import wallet
import pyscreenshot as ImageGrab

check_var = ' '
my_text_buffer = ' '
path_to_USB_secure = 'Secure USB folder is not available'
PersonalGPGKey = ''
CommunicationGPGKey = ''
clicked_privateKey = ' '
clicked_privateSubKey = ' '
clicked_communicationKey = ' ' 
filepathdestinationfolder = '/home/user1'
commkey = ' '
timeSecUSBLastModified = '<Unknown>'
softwareVersion = '0.2.6'
softwareStatus = 'Beta'
HelpBodyVisible = False
newIDflag = False
statt = True 
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

text_file_data = ' '
s_width = 0
s_height = 0
U2F_VENDOR_FIRST = 0x40

System_button_color = 'DarkBlue'
GPG_button_color = 'green'
SecUSB_button_color = 'purple'
Yubikey_button_color = 'red'
DigitalID_button_color = 'brown'
Boltcard_button_color = 'brown'
Help_button_color = 'orange'
			
# FIPS specific INS values
INS_FIPS_VERIFY_PIN = U2F_VENDOR_FIRST + 3
INS_FIPS_SET_PIN = U2F_VENDOR_FIRST + 4
INS_FIPS_RESET = U2F_VENDOR_FIRST + 5
INS_FIPS_VERIFY_FIPS_MODE = U2F_VENDOR_FIRST + 6
  
class App(ctk.CTk):
	def __init__(self):
		global s_width, s_height
		#main setup
		super().__init__()
		self.title("Offline Device GUI")
		s_width = self.winfo_screenwidth()
		s_height = self.winfo_screenheight()
		geom = str(s_width) + 'x' + str(s_height)
		self.geometry(geom)
		self.wm_attributes('-fullscreen', True)
		#self.wm_attributes('-type', 'splash')
		
		self.state('normal')
		self.option_add('*Dialog.msg.font', 'Helvetica 14')
		# widget
		self.menu = Menu(self)
		
		self.mainloop()
		
class Menu(ctk.CTkFrame):	
	def msg_box_textbox(self, msg_text, size_width, size_height):
		global meny
		pop = Toplevel()
		pop.title("Information")
		box_size = size_width + 'x' + size_height
		pop.geometry(box_size)
		pop.focus()
		pop.grab_set()
		
		pop.config(bg="grey")
		
		my_text = ctk.CTkTextbox(pop, width=int(size_width), height=int(size_height), corner_radius=1, border_width=2, border_color="black", border_spacing=10, fg_color="light grey", text_color="black", font=("Arial", 16), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
		my_text.insert('end', msg_text)
	
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")		
			
		def exit_msg():
			pop.destroy()
			
		def stay_on_top():
			pop.lift()
			pop.after(1000, stay_on_top)	
		ok_button = ctk.CTkButton(pop, text="OK", text_color="black", fg_color="light grey", border_width=2, border_color="black", command=exit_msg)
		ok_button.place(relx=0.5, rely=0.9, anchor="center")
		stay_on_top()
		
	def __init__(self, parent):
		super().__init__(parent)
		global s_width,s_height
		self.place(x=0, y=0, relwidth = 1, relheight = 1)
		
		my_image = ctk.CTkImage(light_image=Image.open('/home/user1/venvpython/images/blue.jpg'), dark_image=Image.open('/home/user1/venvpython/images/blue.jpg'), size=(s_width,s_height))
		
		my_label = ctk.CTkLabel(self, text="", image=my_image)
		my_label.pack()

		self.create_meny()
				
	def encryptanddestroy(self):
	
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global s_width,s_height
		
		#The big frame
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/blue.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(s_width, s_height))
		Label_backg = ctk.CTkLabel(my_big_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		Label_backg.focus_set()
		Label_backg.focus_force()
		
		my_big_Frame.focus_set()
		my_big_Frame.focus_force()
		
		my_font = ctk.CTkFont(family="Arial", size=28, weight="bold", slant="roman", underline=False, overstrike=False)
		
		infoLabel = ctk.CTkLabel(my_big_Frame, text="Encrypting the device and shutting down...", text_color="white", font=my_font, fg_color="navy blue")
		infoLabel.place(relx=0.5, rely=0.42, anchor="center")
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		print(PersonalGPGKey)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			
			full_path = str(filepathdestinationfolder) + "/secure/"
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			# Encrypt the tarfile and remove the unencrypted tarfile
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)

			# Write the encrypted file to disk
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			full_path = str(filepathdestinationfolder) + "/secure"
			cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  full_path
			os.system(cmd)
			os.system('sudo shutdown -h now')
			#sys.exit(0)
		else:
			os.system('sudo shutdown -h now')
			#sys.exit(0)
			
	def set_colors(self, color):
		global System_button_color
		global GPG_button_color
		global SecUSB_button_color
		global Yubikey_button_color
		global DigitalID_button_color
		global Boltcard_button_color
		global Help_button_color
		
		if color != 'Varied':
			System_button_color = color
			GPG_button_color = color
			SecUSB_button_color  = color
			Yubikey_button_color  = color
			DigitalID_button_color = color
			Boltcard_button_color = color
			Help_button_color = color
		else:
			System_button_color = 'DarkBlue'
			GPG_button_color = 'green'
			SecUSB_button_color = 'purple'
			Yubikey_button_color = 'red'
			DigitalID_button_color = 'brown'
			Boltcard_button_color = 'brown'
			Help_button_color = 'orange'
			
		#self.create_meny()
				
	def create_meny(self):
		global s_width,s_height
		global System_button_color
		global GPG_button_color
		global SecUSB_button_color
		global Yubikey_button_color
		global DigitalID_button_color
		global Boltcard_button_color
		global Help_button_color
		
		#The big frame
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/blue.jpg"
		
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackground.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackground.jpg"	
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackground.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackground.jpg"
			self.set_colors(users_colors)
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(s_width, s_height))
		Label_backg = ctk.CTkLabel(my_big_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		Label_backg.focus_set()
		my_big_Frame.focus_set()
		my_big_Frame.focus_force()
						
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		GPGButton = ctk.CTkButton(self, text="Home", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.create_meny)
		GPGButton.place(relx=0.1, rely=0.1, anchor="center")
		
		if path_to_USB_secure == 'Secure USB folder is available':
			GPGButton = ctk.CTkButton(self, text="GPG", text_color="white", border_width=2, border_color="white", fg_color=GPG_button_color, width=120, height=32, font=my_font, command=self.create_GPGmeny)
			GPGButton.place(relx=0.2, rely=0.1, anchor="center")
			
			YubikeyButton = ctk.CTkButton(self, text="Yubikey", text_color="white", border_width=2, border_color="white", fg_color=Yubikey_button_color, width=120, height=32, font=my_font, command=self.create_Yubikeymeny)
			YubikeyButton.place(relx=0.3, rely=0.1, anchor="center")
			
			secusbButton = ctk.CTkButton(self, text="Secure archive", text_color="white", border_width=2, border_color="white", fg_color=SecUSB_button_color, width=120, height=32, font=my_font, command=self.create_SecUSBmeny)
			secusbButton.place(relx=0.4, rely=0.1, anchor="center")
			
			idButton = ctk.CTkButton(self, text="Digital ID", text_color="white", border_width=2, border_color="white", fg_color=DigitalID_button_color, width=120, height=32, font=my_font, command=self.create_DigitalIDmeny)
			idButton.place(relx=0.5, rely=0.1, anchor="center")
			
			boltcardButton = ctk.CTkButton(self, text="Boltcard", text_color="white", border_width=2, border_color="white", fg_color=Boltcard_button_color, width=120, height=32, font=my_font, command=self.create_Boltcardmeny)
			boltcardButton.place(relx=0.6, rely=0.1, anchor="center")
			
			HelpButton = ctk.CTkButton(self, text="Help", text_color="white", border_width=2, border_color="white", fg_color=Help_button_color, width=120, height=32, font=my_font, command=self.create_helpmeny)
			HelpButton.place(relx=0.93, rely=0.05, anchor="center")
			
			settimeButton = ctk.CTkButton(self, text="Settings", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.create_getSettimetextbox)
			settimeButton.place(relx=0.93, rely=0.1, anchor="center")

		ExitButton = ctk.CTkButton(self, text="Close and exit", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.encryptanddestroy)
		ExitButton.place(relx=0.5, rely=0.95, anchor="center")

		self.create_Hometextbox()
	
	def new_user_account_selection(self):
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is not available':
			Button8 = ctk.CTkButton(my_Frame, text="Create a new account and one extra key for external communication (Recommended)", text_color="white", fg_color="blue", border_width=2, border_color="white", height=40, font=my_font, command=self.create_getStartedmeny)
			Button8.place(relx=0.5, rely=0.3, anchor="center")
			Button7 = ctk.CTkButton(my_Frame, text="Create only a new account", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.new_secureUSB)
			Button7.place(relx=0.5, rely=0.6, anchor="center")
		else:
			Label1 = ctk.CTkLabel(my_Frame, text="You are already logged in.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.44, rely=0.4, anchor="e")
			Label11 = ctk.CTkLabel(my_Frame, text=PersonalGPGKey, text_color="white", fg_color="black", font=my_font)
			Label11.place(relx=0.45, rely=0.4, anchor="w")
			
	def create_getStartedmeny(self):
		global s_width,s_height
		#The big frame
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/blue.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(s_width, s_height))
		Label_backg = ctk.CTkLabel(my_big_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_big_Frame.focus_set()
		my_big_Frame.focus_force()

		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		GPGButton = ctk.CTkButton(self, text="Home", text_color="white", border_width=2, border_color="white", fg_color="blue", font=my_font, command=self.create_meny)
		GPGButton.place(relx=0.1, rely=0.1, anchor="center")
		
		HelpButton = ctk.CTkButton(self, text="Help", text_color="white", border_width=2, border_color="white", fg_color="orange", width=120, height=32, font=my_font, command=self.create_helpmeny)
		HelpButton.place(relx=0.93, rely=0.05, anchor="center")
		
		settimeButton = ctk.CTkButton(self, text="Settings", text_color="white", border_width=2, border_color="white", fg_color="blue", width=120, height=32, font=my_font, command=self.create_getSettimetextbox)
		settimeButton.place(relx=0.93, rely=0.1, anchor="center")
		
		ExitButton = ctk.CTkButton(self, text="Close and exit", text_color="white", border_width=2, border_color="white", fg_color="blue", width=120, height=32, font=my_font, command=self.encryptanddestroy)
		ExitButton.place(relx=0.5, rely=0.95, anchor="center")
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)

		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="italic", underline=True, overstrike=False)
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="italic", underline=True, overstrike=False)
		
		Label2 = ctk.CTkLabel(self, text="This will let you set-up:", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.38, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="italic", underline=True, overstrike=False)
		Label23 = ctk.CTkLabel(self, text="(1). An encryption key for safe, and private, communication that can be used with emails etc.", text_color="white", fg_color="black", font=my_font)
		Label23.place(relx=0.5, rely=0.44, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="italic", underline=True, overstrike=False)
		Label4 = ctk.CTkLabel(self, text="(2). An encrypted archive for important files, passwords and bitcoin wallets etc.", text_color="white", fg_color="black", font=my_font)
		Label4.place(relx=0.5, rely=0.49, anchor="center")
		Label5 = ctk.CTkLabel(self, text="(3). A secondary backup on a USB-stick in case of breakage, fire or theft.", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.54, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=14, weight="bold", slant="roman", underline=False, overstrike=False)
		Label6 = ctk.CTkLabel(self, text="(You will need a USB-stick ready to connect when instructed during the setup process.)", text_color="white", fg_color="black", font=my_font)
		Label6.place(relx=0.5, rely=0.58, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="italic", underline=True, overstrike=False)
		Label7 = ctk.CTkLabel(self, text="(4). A Yubikey 5 NFC (hardware device) with subkeys for encrypting emails on computers and smartphones (optional).", text_color="white", fg_color="black", font=my_font)
		Label7.place(relx=0.5, rely=0.63, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button3 = ctk.CTkButton(self, text="Got it. Lets Go!", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.create_getStartedmeny_Pre)
		Button3.place(relx=0.5, rely=0.7, anchor="center")
	
	def create_getStartedmeny_Pre(self):
		# Make sure time and date is correct before creating anyuy new keys 
		global filepathdestinationfolder
		global SecUSB_button_color
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_Frame.focus_set()
		my_Frame.focus_force()			
		
		def do_create_getStartedmeny_Pre():
			global filepathdestinationfolder
			key_fingerprint = ''
			# Set the date and time
			thedate = cal.get_date()
			thetime = time_picker.time()
			
			thedatestr = str('sudo date -s \'' + str(thedate) + ' ' + str(thetime[0]) + ':' + str(thetime[1]) + ':00\'')			
			os.system(thedatestr)
			thestr = 'sudo hwclock -w'	
			os.system(thestr)
			os.system(thestr)
			self.create_getStartedmeny2()
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Important! Before creating new account make sure the time and date are correct:", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.1, anchor="center")
		
		time_picker = AnalogPicker(my_Frame, type=constants.HOURS24)
		time_picker.setHours(datetime.now().hour)
		time_picker.setMinutes(datetime.now().minute)
		time_picker.place(relx=0.65, rely=0.45, anchor="e")
		
		theme = AnalogThemes(time_picker)
		theme.setNavyBlue()
		time_picker.configAnalog(textcolor="#ffffff", bg="#0a0832", bdColor="#000000", headbdcolor="#000000")
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2024)
		cal.place(relx=0.65, rely=0.73, anchor="e")
			
		Button = ctk.CTkButton(my_Frame, text="Next!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_create_getStartedmeny_Pre)
		Button.place(relx=0.5, rely=0.86, anchor="center")
		
	def create_getStartedmeny2(self):	
		global path_to_USB_secure
		global filepathdestinationfolder
		global commkey
		check_var = ctk.StringVar(value="off") 
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="italic", underline=True, overstrike=False)
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		def tPassphrase():
			if Secret_passphrasePrivateEntry.cget('show') == '':
				Secret_passphrasePrivateEntry.configure(show='*')
			else:
				Secret_passphrasePrivateEntry.configure(show='')
		def t2Passphrase():
			if Secret_passphraseCommunicationEntry.cget('show') == '':
				Secret_passphraseCommunicationEntry.configure(show='*')
			else:
				Secret_passphraseCommunicationEntry.configure(show='')
		
		def tPIN():
			if Secret_PIN.cget('show') == '':
				Secret_PIN.configure(show='*')
			else:
				Secret_PIN.configure(show='')
		
		def tAdminPIN():
			if Secret_AdminPIN.cget('show') == '':
				Secret_AdminPIN.configure(show='*')
			else:
				Secret_AdminPIN.configure(show='')
		
		def getStarted():
			global path_to_USB_secure
			global PersonalGPGKey
			global filepathdestinationfolder
			global commkey
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')

			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)	
			my_Frame.focus_set()
			my_Frame.focus_force()
				
			# Create a GPG master key for personal use, namePrivateEntry emailPrivateEntry Secret_passphrasePrivateEntry
			input_data_priv = gpg.gen_key_input(key_type='rsa', name_real=namePrivateEntry.get(), expire_date='0', key_length='4096', name_email=emailPrivateEntry.get(), passphrase=Secret_passphrasePrivateEntry.get())
			privatekey = gpg.gen_key(input_data_priv)
			
			# Create a GPG master key for communication and three subkeys, nameCommunicationEntry emailCommunicationEntry Secret_passphraseCommunicationEntry
			input_data_comm = gpg.gen_key_input(key_type='rsa',  key_usage='sign', name_real=nameCommunicationEntry.get(), expire_date='0', key_length='4096', name_email=emailCommunicationEntry.get(), passphrase=Secret_passphraseCommunicationEntry.get())
			communicationkey = gpg.gen_key(input_data_comm)
			
			PersonalGPGKey = str(privatekey.fingerprint)
			commkey = str(communicationkey.fingerprint)	
			
			key = gpg.add_subkey(commkey, algorithm='rsa4096', usage='sign', expire='3y')
			key = gpg.add_subkey(commkey, algorithm='rsa4096', usage='encrypt', expire='3y')
			key = gpg.add_subkey(commkey, algorithm='rsa4096', usage='auth', expire='3y')
			
			# Create a Secure folder
			full_path = str(filepathdestinationfolder) + "/secure/"
			full_path_wallets = str(filepathdestinationfolder) + "/secure/wallets/"
			full_path_keys = str(filepathdestinationfolder) + "/secure/keys/"
			full_path_paperwallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/"
			full_path_settings_file = str(filepathdestinationfolder) + "/secure/settings.csv"
			full_path_paperwallets_file = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
			full_path_boltcards = str(filepathdestinationfolder) + "/secure/boltcards/"
			full_path_boltcards_file = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
			full_path_FIDOKeys = str(filepathdestinationfolder) + "/secure/FIDO/"
			full_path_FIDOKeys_file = str(filepathdestinationfolder) + "/secure/FIDO/FIDOKeys.csv"
			full_path_IDs = str(filepathdestinationfolder) + "/secure/ID/"
			full_path_IDs_file = str(filepathdestinationfolder) + "/secure/ID/IDs.csv"
			
			os.makedirs(os.path.dirname(full_path))
			os.makedirs(os.path.dirname(full_path_wallets))
			os.makedirs(os.path.dirname(full_path_keys))
			os.makedirs(os.path.dirname(full_path_paperwallets))
			os.makedirs(os.path.dirname(full_path_boltcards))
			os.makedirs(os.path.dirname(full_path_FIDOKeys))
			os.makedirs(os.path.dirname(full_path_IDs))
			
			c = open(full_path + "passwords.txt", 'w')
			c.write(str("Passwords\n___________________________________\n\nYubikey\n\n   FIDO PIN:  \n\n   OpenPGP Admin PIN:  \n\n   OpenPGP PIN:  \n\n   Comment:  \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n"))
			c.close()
			c = open(full_path_wallets + "wallets.txt", 'w')
			c.write(str("Wallets\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n"))
			c.close()
			with open(full_path_settings_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['Username', 'Theme', 'Colors']
			with open(full_path_paperwallets_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['Name', 'Datecreated', 'Pubkey', 'wif', 'mnemonic', 'amount']
			with open(full_path_boltcards_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['name', 'description', 'datecreated', 'LNURLaddress', 'resetcode', 'programmingcode', 'withdrawallimit', 'dailywithdrawallimit', 'LNHublink', 'LNHubuser', 'LNHubuserpassword']	
			with open(full_path_FIDOKeys_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['name', 'description', 'services']	
			with open(full_path_IDs_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['type', 'fingerprint', 'name', 'lastname', 'address', 'address2', 'birthdate', 'sex', 'issuedate']
									
			path_to_USB_secure = 'Secure USB folder is available'
			
			# Make initial settings in settings file
			with open(full_path_settings_file, 'w') as result:
				csvwriter = csv.writer(result)
				new_settings = [
								namePrivateEntry.get(),
								'Winter',
								'Varied']
				csvwriter.writerow(new_settings)					
					
			# Backup both master keys (communication key is still with subkeys intact).
			privatekeyfilename = 'privateKey' + PersonalGPGKey + ".gpg"
			communicationkeyfilename = 'privateKey' + commkey + ".gpg"
			full_path_private = filepathdestinationfolder + "/" + privatekeyfilename
			full_path_communication = filepathdestinationfolder + "/secure/keys/" + communicationkeyfilename
			
			# Export the private key and write to file in /home/user1 and to /home/user1/secure/keys
			ascii_armored_private_key = gpg.export_keys(PersonalGPGKey, True, expect_passphrase=False)
			f2 = open(full_path_private, 'w')
			f2.write(ascii_armored_private_key)
			f2.close()
			destPriv = filepathdestinationfolder + "/secure/keys/" + privatekeyfilename
			shutil.copy(full_path_private, destPriv)
			
			# Export the communication key and write to file in /secure/keys
			ascii_armored_communication_key = gpg.export_keys(commkey, True, expect_passphrase=False)
			f2 = open(full_path_communication, 'w')
			f2.write(ascii_armored_communication_key)
			f2.close()
			
			# Export the communication subkeys and write to file in /secure/keys
			communicationsubkeyfilename = 'allsubKeys' + commkey + ".gpg"
			cmd = 'gpg --armor --export-secret-subkeys ' + commkey + ' > ' + filepathdestinationfolder + '/secure/keys/' + communicationsubkeyfilename
			os.system(cmd)
			
			# Encrypt the secure folder and place on the USB-stick. Then ask user to remove the USB-stick
			full_path = str(filepathdestinationfolder) + "/secure/"
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			
			# Encrypt the tarfile and remove the unencrypted tarfile
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)
			# Write the encrypted file to the offline device /home/user1
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()

			full_path = filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg'
			path_to_USB_secure = 'Secure USB folder is available'
			timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
			
			# Copy the exported private key to a USB-device
			messagebox.showinfo("Information", "Insert a USB-device (for making a backup) and double-click to select it.")
			time.sleep(4)
			localfilepathdestinationfolder = filedialog.askdirectory(initialdir='/media/user1/')
			shutil.copy(full_path_private, localfilepathdestinationfolder)
			
			# Write the encrypted file to second USB-stick
			compressedoutfile = open(localfilepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			messagebox.showinfo("Information", "Encrypted files and keys written to the USB-device successfully. Please remove USB-device.")
			
			# Set Admin PIN, PIN, name, email on Yubikey if checkbox is set. Secret_PIN Secret_AdminPIN (and name/email as in Communication key)
			if checkbox.get() == "on":
				tk.messagebox.showinfo('Information', 'Connect the Yubikey')
				
				backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
				Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
				Label_backg.place(x=0, y=0)
				my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
				
				Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open:\n_________________________\n1. Type \"admin\" and hit enter to toggle until it says \"admin commands are allowed\"\n2. Type \"passwd\" hit enter.\nSelect \"3\" and hit enter.\n        Enter current admin PIN (default admin PIN is 12345678).\n      Add new admin PIN (min 8 digits).\n        Confirm the new admin PIN.\n3. Select \"1\" and hit enter.\n      Enter current PIN (default PIN is 123456).\n      Add new PIN (min 6 digits).\n        Confirm new PIN.\n4. Type \"q\" and hit enter.\n5. Type \"quit\" and hit enter.\n6. Exit the terminal by typing \"exit\" and hit enter.', text_color="white", fg_color="black", font=my_font)
				Label.place(relx=0.5, rely=0.35, anchor="center")
				my_Frame.focus_set()
				my_Frame.focus_force()
				
				time.sleep(1)

				goButton = ctk.CTkButton(my_Frame, text="Start", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=next_step)
				goButton.place(relx=0.5, rely=0.8, anchor="center")

			else:
				get_started_without_Yubikey_finished()
		
		def get_started_without_Yubikey_finished():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=18, slant="roman", underline=False, overstrike=False)
			
			my_Frame.focus_set()
			my_Frame.focus_force()

			goButton = ctk.CTkButton(my_Frame, text="Click to complete the setup", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.getStartedfinnished)
			goButton.place(relx=0.5, rely=0.35, anchor="center")
			
		def next_step():
			command= 'gpg --card-edit'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open:\n_________________________\n1. Type \"admin\" and hit enter to toggle until it says \"admin commands are allowed\"\n2. Type \"passwd\" hit enter.\nSelect \"3\" and hit enter.\n        Enter current admin PIN (default admin PIN is 12345678).\n      Add new admin PIN (min 8 digits).\n        Confirm the new admin PIN.\n3. Select \"1\" and hit enter.\n      Enter current PIN (default PIN is 123456).\n      Add new PIN (min 6 digits).\n        Confirm new PIN.\n4. Type \"q\" and hit enter.\n5. Type \"quit\" and hit enter.\n6. Exit the terminal by typing \"exit\" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.35, anchor="center")
			
			goButton = ctk.CTkButton(my_Frame, text="Next", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=next_step2)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
		
		def next_step2():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open:\n_________________________\nType "toggle" and hit enter.\n2.Type "key 1" and "key 2" etc to toggle select/deselect subkey.\n        Selected subkey will be marked with "*"\n        Make sure only ONE subkey is selected before moving on to next step.\n3. Type "keytocard" to move the selected subkey to the Yubikey.\nIf the subkey is marked with \"usage: S\" then select \"(1) Signature key\".\nDeselect the \"Key 1\" by typing \"Key 1\" one more time.\n4. Repeat with all three subkeys.\n5. Type "save" and hit enter.\n6. Type "exit" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			goButton = ctk.CTkButton(my_Frame, text="Start", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=next_step3)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
				
			
		def next_step3():
			command= 'gpg --edit-key ' + commkey
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open:\n_________________________\nType "toggle" and hit enter.\n2.Type "key 1" and "key 2" etc to toggle select/deselect subkey.\n        Selected subkey will be marked with "*"\n        Make sure only ONE subkey is selected before moving on to next step.\n3. Type "keytocard" to move the selected subkey to the Yubikey.\nIf the subkey is marked with \"usage: S\" then select \"(1) Signature key\".\nDeselect the \"Key 1\" by typing \"Key 1\" one more time.\n4. Repeat with all three subkeys.\n5. Type "save" and hit enter.\n6. Type "exit" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			goButton = ctk.CTkButton(my_Frame, text="Next", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=next_step4)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
			
		def next_step4():
			global commkey
			global filepathdestinationfolder
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			# Delete the Communication key (with snubbed subkeys) and import it from secure archive (to get working subkeys again)
			try:
				key = gpg.delete_keys(commkey, True, expect_passphrase=False)  #passphrase=USER_INP)
			except ValueError as ve:
				messagebox.showinfo('Information', 'Something went wrong.')
					
			communicationkeyfilename = 'privateKey' + commkey + ".gpg"
			full_path_communication = filepathdestinationfolder + "/secure/keys/" + communicationkeyfilename
			
			import_result = gpg.import_keys_file(full_path_communication)

			goButton = ctk.CTkButton(my_Frame, text="Click to complete the setup", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.getStartedfinnished)
			goButton.place(relx=0.5, rely=0.4, anchor="center")
			
		my_font = ctk.CTkFont(family="Tahoma", size=34, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label = ctk.CTkLabel(my_Frame, text="Please provide your data:", text_color="white", fg_color="black", font=my_font)
		Label.place(relx=0.3, rely=0.1, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		# Data for the private key
		Labelprivate = ctk.CTkLabel(my_Frame, text="Private key*:", text_color="white", fg_color="black", font=my_font)
		Labelprivate.place(relx=0.3, rely=0.17, anchor="w")
		namePrivate = ctk.CTkLabel(my_Frame, text="Full name:", text_color="white", fg_color="black", font=my_font)
		namePrivate.place(relx=0.34, rely=0.22, anchor="e")
		namePrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text="Bob Smith", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		namePrivateEntry.place(relx=0.35, rely=0.22, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="Email:", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.34, rely=0.27, anchor="e")
		emailPrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text="bob.smith@cyb.org", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		emailPrivateEntry.place(relx=0.35, rely=0.27, anchor="w")
		
		LabelPassphrasePrivate = ctk.CTkLabel(my_Frame, text="Secret passphrase:", text_color="white", fg_color="black", font=my_font)
		LabelPassphrasePrivate.place(relx=0.34, rely=0.32, anchor="e")
		Secret_passphrasePrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text="*****************", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		Secret_passphrasePrivateEntry.place(relx=0.35, rely=0.32, anchor="w")
		tButton = ctk.CTkButton(my_Frame, text="Show/hide passphrase", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=tPassphrase)
		tButton.place(relx=0.7, rely=0.32, anchor="center")
		
		# Data for the communication key
		Labelcomm = ctk.CTkLabel(my_Frame, text="Communication key**:", text_color="white", fg_color="black", font=my_font)
		Labelcomm.place(relx=0.28, rely=0.37, anchor="w")
		Label11 = ctk.CTkLabel(my_Frame, text="Full name:", text_color="white", fg_color="black", font=my_font)
		Label11.place(relx=0.34, rely=0.42, anchor="e")
		nameCommunicationEntry = ctk.CTkEntry(my_Frame, placeholder_text="Carl Smitty", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		nameCommunicationEntry.place(relx=0.35, rely=0.42, anchor="w")
		
		Label22 = ctk.CTkLabel(my_Frame, text="Email:", text_color="white", fg_color="black", font=my_font)
		Label22.place(relx=0.34, rely=0.47, anchor="e")
		emailCommunicationEntry = ctk.CTkEntry(my_Frame, placeholder_text="Carl.smitty@thecave.net", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		emailCommunicationEntry.place(relx=0.35, rely=0.47, anchor="w")
		
		LabelPassphraseComm = ctk.CTkLabel(my_Frame, text="Secret passphrase:", text_color="white", fg_color="black", font=my_font)
		LabelPassphraseComm.place(relx=0.34, rely=0.52, anchor="e")
		Secret_passphraseCommunicationEntry = ctk.CTkEntry(my_Frame, placeholder_text="*****************", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		Secret_passphraseCommunicationEntry.place(relx=0.35, rely=0.52, anchor="w")
		tButton2 = ctk.CTkButton(my_Frame, text="Show/hide passphrase", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=t2Passphrase)
		tButton2.place(relx=0.7, rely=0.52, anchor="center")
		
		checkbox = ctk.CTkCheckBox(my_Frame, text="I got a Yubikey 5 NFC.", variable=check_var, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		checkbox.place(relx=0.35, rely=0.58, anchor="w")
		
		goButton = ctk.CTkButton(my_Frame, text="Lets Go! ***", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=getStarted)
		goButton.place(relx=0.5, rely=0.66, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		LLabel3 = ctk.CTkLabel(my_Frame, text="*** This can take a while.. Move mouse around to create randomness...\nFollow all the instructions for the rest of the setup.", text_color="white", fg_color="black", font=my_font)
		LLabel3.place(relx=0.5, rely=0.73, anchor="center")
		my_font = ctk.CTkFont(family="Helvetica", size=15, weight="normal", slant="roman", underline=False, overstrike=False)
		Labelinf1 = ctk.CTkLabel(my_Frame, text="* Private key is for private use (like encrypting the secure archive on the offline device etc).", text_color="white", fg_color="black", font=my_font)
		Labelinf1.place(relx=0.05, rely=0.81, anchor="w")
		Labelinf2 = ctk.CTkLabel(my_Frame, text="** Communication key is used for signing other public keys, encrypting emails etc. Subkeys should be on a Yubikey (for safe use with computers/smartphones).", text_color="white", fg_color="black", font=my_font)
		Labelinf2.place(relx=0.05, rely=0.87, anchor="w")
			
	def getStartedfinnished(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"

		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		# Output what has been done from getStarted
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="italic", underline=True, overstrike=False)
		Label2 = ctk.CTkLabel(my_Frame, text="Finished!", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.3, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="italic", underline=True, overstrike=False)
		Label23 = ctk.CTkLabel(my_Frame, text="You have sucessfully created:", text_color="white", fg_color="black", font=my_font)
		Label23.place(relx=0.5, rely=0.37, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		Label3 = ctk.CTkLabel(my_Frame, text="(1). Two encryption keys that are placed on the offline device (this device). One for securing this device and one for external communication *.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.42, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="italic", underline=False, overstrike=False)
		Label4 = ctk.CTkLabel(my_Frame, text="(2). An encrypted archive that can be used to storing files, passwords and bitcoin wallets etc.", text_color="white", fg_color="black", font=my_font)
		Label4.place(relx=0.5, rely=0.47, anchor="center")
		Label5 = ctk.CTkLabel(my_Frame, text="(3). A backup USB-stick in case the offline device breaks or there is a fire or theft etc.", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.52, anchor="center")

		Label6 = ctk.CTkLabel(my_Frame, text="(4). A Yubikey 5 NFC (hardware device) with subkeys for encrypting emails on a smartphones etc (optional).", text_color="white", fg_color="black", font=my_font)
		Label6.place(relx=0.5, rely=0.57, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button3 = ctk.CTkButton(my_Frame, text="Start using the offline device", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.create_meny)
		Button3.place(relx=0.5, rely=0.7, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
		
		Label7 = ctk.CTkLabel(my_Frame, text="* This key has been split into many parts. A master key  (to remain offline), a public key and three subkeys, to move to other devices.", text_color="white", fg_color="black", font=my_font)
		Label7.place(relx=0.5, rely=0.82, anchor="center")
		 
	def create_helpmeny(self):
		global Help_button_color
		self.create_abouthelptextbox()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		mainHelpButton = ctk.CTkButton(self, text="Help", text_color="white", border_width=2, border_color="white", fg_color="orange",  width=120, height=32, font=my_font, command=self.create_helpmeny)
		mainHelpButton.place(relx=0.93, rely=0.05, anchor="center")
		
		Button1 = ctk.CTkButton(self, text="Getting started", text_color="white", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_abouthelptextbox)
		Button1.place(relx=0.1, rely=0.2, anchor="center")
		
		Button2 = ctk.CTkButton(self, text="GPG", text_color="white", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_gpghelptextbox)
		Button2.place(relx=0.25, rely=0.2, anchor="center")
		
		Button3 = ctk.CTkButton(self, text="Yubikey", text_color="white", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_yubikeyhelptextbox)
		Button3.place(relx=0.4, rely=0.2, anchor="center")
		
		Button4 = ctk.CTkButton(self, text="Secure archive", text_color="white", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_secusbhelptextbox)
		Button4.place(relx=0.55, rely=0.2, anchor="center")
		
		Button5 = ctk.CTkButton(self, text="Digital ID\'s", text_color="white", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_digitalIDhelptextbox)
		Button5.place(relx=0.7, rely=0.2, anchor="center")
		
		Button6 = ctk.CTkButton(self, text="Bolt cards", text_color="white", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_boltcardhelptextbox)
		Button6.place(relx=0.85, rely=0.2, anchor="center")
	
	def create_GPGmeny(self):
		global GPG_button_color
		self.GnuPG_Home()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		CheckGPGButton = ctk.CTkButton(self, text="Check local keys", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.get_GnuPGKeys)
		CheckGPGButton.place(relx=0.1, rely=0.2, anchor="center")
		
		AddkeyButton = ctk.CTkButton(self, text="Add/remove key", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.newGPGFull_Key)
		AddkeyButton.place(relx=0.25, rely=0.2, anchor="center")
		
		AddsubkeyButton = ctk.CTkButton(self, text="Add subkeys", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.newGPG_Subkey)
		AddsubkeyButton.place(relx=0.4, rely=0.2, anchor="center")
		
		BackupkeysButton = ctk.CTkButton(self, text="Backup keys", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.backupGPG_Keys)
		BackupkeysButton.place(relx=0.55, rely=0.2, anchor="center")
		
		ImportkeyButton = ctk.CTkButton(self, text="Import/export", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.import_or_export)
		ImportkeyButton.place(relx=0.7, rely=0.2, anchor="center")
		
		SignkeyButton = ctk.CTkButton(self, text="Sign/validate", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.select_what_to_sign)
		SignkeyButton.place(relx=0.85, rely=0.2, anchor="center")
	
	def create_SecUSBmeny(self):
		global SecUSB_button_color
		global path_to_USB_secure
		
		self.create_secusbtextbox()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button1 = ctk.CTkButton(self, text="Secure archive", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.check_SecUSB)
		Button1.place(relx=0.1, rely=0.2, anchor="center")
		
		Button2 = ctk.CTkButton(self, text="Encrypt/view a text", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.encrypt_message)
		Button2.place(relx=0.25, rely=0.2, anchor="center")
		
		Button3 = ctk.CTkButton(self, text="Decrypt a textfile", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_message)
		Button3.place(relx=0.4, rely=0.2, anchor="center")
		
		Button4 = ctk.CTkButton(self, text="Restore from USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.restoreFromencrypted_SecUSB)
		Button4.place(relx=0.55, rely=0.2, anchor="center")
		
		Button5 = ctk.CTkButton(self, text="Backup to USB/SD", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.copy_SecUSB)
		Button5.place(relx=0.7, rely=0.2, anchor="center")
		
		Button6 = ctk.CTkButton(self, text="BTC wallets", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
		Button6.place(relx=0.85, rely=0.2, anchor="center")
		
		if path_to_USB_secure == 'Secure USB folder is not available':
			Button8 = ctk.CTkButton(self, text="Log in", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			Button8.place(relx=0.5, rely=0.5, anchor="center")
			Label = ctk.CTkLabel(self, text="Or", text_color="white", font=("Helvetica", 18), fg_color="black")
			Label.place(relx=0.5, rely=0.55, anchor="center")
			Button7 = ctk.CTkButton(self, text="Create new user account", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.new_secureUSB)
			Button7.place(relx=0.5, rely=0.6, anchor="center")
	
	def create_FIDOmeny(self):
		global FIDO_button_color
		global filepathdestinationfolder
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="brown"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		left_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=278, 
		height=634,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="gray1"
		)
		left_Frame.place(relx=0, rely=0, anchor="nw")	
		
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=650,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=0, anchor="nw")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoIDimage = str(filepathdestinationfolder) + "/venvpython/images/Yubikey5CBackground.JPG"

			IDimagebutton = ctk.CTkImage(light_image=Image.open(pathtoIDimage), dark_image=Image.open(pathtoIDimage), size=(230, 100))
			completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			counter = 0
			Buttonnew = ctk.CTkButton(right_Frame, text="New FIDO Key", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newFIDO)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			
			infoLabel = ctk.CTkLabel(right_Frame, text="Add new FIDO key:", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.1, rely=0.15, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			
			infoLabel = ctk.CTkLabel(right_Frame, text="1. Use a hardware key with FIDO2 support (ex. Yubikey 5 or similar).", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.1, rely=0.21, anchor="w")
			infoLabel2 = ctk.CTkLabel(right_Frame, text="   - Reset the key using an offline device (this will remove factory keys and generate new keys).", text_color="white", font=my_font, fg_color="black")
			infoLabel2.place(relx=0.1, rely=0.26, anchor="w")
			infoLabel3 = ctk.CTkLabel(right_Frame, text="2. - Register the FIDO-key at all services that the specific key work with.", text_color="white", font=my_font, fg_color="black")
			infoLabel3.place(relx=0.1, rely=0.32, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="3. Remember to have at minimum two keys registered for each service, as one key could get lost/stolen or break.", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.41, anchor="w")
			infoLabel5 = ctk.CTkLabel(right_Frame, text="4. Add a new FIDO key entry on the offline device (this device) by clicking \"New FIDO key\".", text_color="white", font=my_font, fg_color="black")
			infoLabel5.place(relx=0.1, rely=0.46, anchor="w")
			infoLabel6 = ctk.CTkLabel(right_Frame, text="   - Give the FIDO key a name.", text_color="white", font=my_font, fg_color="black")
			infoLabel6.place(relx=0.1, rely=0.51, anchor="w")
			infoLabel7 = ctk.CTkLabel(right_Frame, text="   - Give the FIDO key a description.", text_color="white", font=my_font, fg_color="black")
			infoLabel7.place(relx=0.1, rely=0.56, anchor="w")
			infoLabel8 = ctk.CTkLabel(right_Frame, text="5. Enter the services that the key is registered at.", text_color="white", font=my_font, fg_color="black")
			infoLabel8.place(relx=0.1, rely=0.61, anchor="w")
			infoLabel9 = ctk.CTkLabel(right_Frame, text="   - This information is only to help in remembering what key is used for what.", text_color="white", font=my_font, fg_color="black")
			infoLabel9.place(relx=0.1, rely=0.66, anchor="w")
			infoLabel10 = ctk.CTkLabel(right_Frame, text="6. Keep the extra FIDO key(s) safe.", text_color="white", font=my_font, fg_color="black")
			infoLabel10.place(relx=0.1, rely=0.71, anchor="w")
			
			proLabel = ctk.CTkLabel(right_Frame, text="(Tip: FIDO keys are more secure as it is not as simple as stealing a password to gain access to an account.)", text_color="white", font=my_font, fg_color="black")
			proLabel.place(relx=0.1, rely=0.85, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)								
			cardLabel = ctk.CTkLabel(left_Frame, text="FIDO keys", text_color="white", font=my_font, fg_color="black").pack(padx=10, pady=8, side= TOP, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			Counting = 0
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							if Counting == 0:	
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showFIDO, lines[0]))
								Button1.pack(padx=10, pady=18, side= TOP, anchor="w")
							else:
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showFIDO, lines[0]))
								Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							Counting += 1
			except FileNotFoundError:
				messagebox.showinfo("Information", "No FIDO Keys found.")
		else:
			notOKButton = ctk.CTkButton(right_Frame, text="You are not logged in.", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def showFIDO(self, FIDOname):
		global filepathdestinationfolder
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		left_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=278, 
		height=634,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="gray1"
		)
		left_Frame.place(relx=0, rely=0, anchor="nw")
		
		pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=648,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=2, anchor="nw")
		
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoicon = str(filepathdestinationfolder) + "/venvpython/images/Yubikey5CBackground.JPG"

			iconimage = ctk.CTkImage(light_image=Image.open(pathtoicon), dark_image=Image.open(pathtoicon), size=(230, 100))
			
			completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)								
			cardLabel = ctk.CTkLabel(left_Frame, text="FIDO keys", text_color="white", font=my_font, fg_color="black").pack(padx=10, pady=8, side= TOP, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			Counting = 0
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							if Counting == 0:	
								Button1 = ctk.CTkButton(left_Frame, text="", image = iconimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showFIDO, lines[0]))
								Button1.pack(padx=10, pady=18, side= TOP, anchor="w")
							else:
								Button1 = ctk.CTkButton(left_Frame, text="", image = iconimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showFIDO, lines[0]))
								Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							Counting += 1
			except FileNotFoundError:
				messagebox.showinfo("Information", "No FIDO Keys found.")
			Buttonnew = ctk.CTkButton(right_Frame, text="New FIDO key", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newFIDO)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:

						if lines[0] == FIDOname:								
							my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=True, overstrike=False)
							nameheadLabel = ctk.CTkLabel(right_Frame, text="Name of FIDO key:", text_color="white", font=my_font, fg_color="black")
							nameheadLabel.place(relx=0.05, rely=0.18, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
							nameLabel = ctk.CTkLabel(right_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							nameLabel.place(relx=0.05, rely=0.22, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
							
							descrheadLabel = ctk.CTkLabel(right_Frame, text="Description:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.05, rely=0.27, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
							descrLabel = ctk.CTkLabel(right_Frame, text=lines[1], text_color="white", font=my_font, fg_color="black")
							descrLabel.place(relx=0.05, rely=0.31, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
							descrheadLabel = ctk.CTkLabel(right_Frame, text="Used for services:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.05, rely=0.36, anchor="w")
							
							my_text = ctk.CTkTextbox(right_Frame, width=500, height=150, corner_radius=1, border_width=0, border_color="brown", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
							my_text.insert('end', lines[2])
							my_text.configure(state="disabled")
							my_text.place(relx=0.05, rely=0.4, anchor="nw")
														
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
							Buttonedit = ctk.CTkButton(right_Frame, text="Edit", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=partial(self.editFIDO, FIDOname))
							Buttonedit.place(relx=0.25, rely=0.85, anchor="center")
							delButton = ctk.CTkButton(right_Frame, text="Delete", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.deleteFIDO, FIDOname))
							delButton.place(relx=0.5, rely=0.85, anchor="center")
							backButton = ctk.CTkButton(right_Frame, text="Back", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_FIDOmeny)
							backButton.place(relx=0.75, rely=0.85, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No FIDO keys file found.")
		else:
			notOKButton = ctk.CTkButton(my_Frame, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")

	def editFIDO(self, FIDOname):
		global SecUSB_button_color
		global filepathdestinationfolder
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		theinput = ''
		my_text = ctk.CTkTextbox(my_Frame, width=500, height=150, corner_radius=1, border_width=0, border_color="brown", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
							
		def do_edit_FIDO():
			global filepathdestinationfolder
			Updated_name = nameEntry.get()
			Updated_description = descriptionEntry.get()
			theinput = self.textBox.get("1.0",'end-1c')
			
			Updated_FIDO_data = [
								Updated_name,
								Updated_description,
								theinput]
								
			completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
			updatedcompleteName = str(filepathdestinationfolder) + "/secure/FIDO/updatedFIDOkeys.csv"
			with open(completeName, 'r') as source, open(updatedcompleteName, 'w') as result:
				csvreader = csv.reader(source)
				csvwriter = csv.writer(result)
				for row in csv.reader(source):
					try:
						if row[0] == FIDOname:
							csvwriter.writerow(Updated_FIDO_data)
						else:
							csvwriter.writerow(row)						
					except:
						continue
			shutil.copy(updatedcompleteName, completeName)
			os.remove(updatedcompleteName)	
			self.create_FIDOmeny()
		
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
		# Read the content of the FIDO key in csv-file
		if path_to_USB_secure == 'Secure USB folder is available':
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[0] == FIDOname:								
							my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=True, overstrike=False)
							nameheadLabel = ctk.CTkLabel(my_Frame, text="Edit FIDO key:", text_color="white", font=my_font, fg_color="black")
							nameheadLabel.place(relx=0.2, rely=0.1, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
							nameheadLabel = ctk.CTkLabel(my_Frame, text="Name of FIDO key:", text_color="white", font=my_font, fg_color="black")
							nameheadLabel.place(relx=0.2, rely=0.18, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
							
							the_name_var = ctk.StringVar(value=lines[0])
		
							nameEntry = ctk.CTkEntry(my_Frame, placeholder_text=lines[0], textvariable=the_name_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
							nameEntry.place(relx=0.2, rely=0.24, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
							
							descrheadLabel = ctk.CTkLabel(my_Frame, text="Description:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.2, rely=0.29, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
							
							the_description_var = ctk.StringVar(value=lines[1])
							
							descriptionEntry = ctk.CTkEntry(my_Frame, placeholder_text=lines[1], textvariable=the_description_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
							descriptionEntry.place(relx=0.2, rely=0.33, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
							descrheadLabel = ctk.CTkLabel(my_Frame, text="Used for services:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.2, rely=0.38, anchor="w")
							
							self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 15), wrap = 'word', undo = True)
							self.textBox.insert("1.0", lines[2])
							self.textBox.place(relx=0.2, rely=0.42, height=220, width=600, anchor="nw")
							self.textBox.focus_set()
							self.textBox.focus_force()
							theinput = self.textBox.get("1.0",'end-1c')
							
							backButton = ctk.CTkButton(my_Frame, text="Save", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=do_edit_FIDO)
							backButton.place(relx=0.5, rely=0.85, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No FIDO keys file found.")
		else:
			my_textbox.insert('end', 'You are not logged in. Cant edit.')
			
	def deleteFIDO(self, FIDOname):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
		updatedcompleteName = str(filepathdestinationfolder) + "/secure/FIDO/updatedFIDOkeys.csv"
		with open(completeName, 'r') as source, open(updatedcompleteName, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[0] == FIDOname:
						answer = messagebox.askquestion('Important!', 'Are you sure you want to delete the FIDO key?')
						if answer == 'yes':
							print("Sure")
						else:
							csvwriter.writerow(row)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updatedcompleteName, completeName)
		os.remove(updatedcompleteName)	
		self.create_FIDOmeny()
		
	def newFIDO(self):
		global filepathdestinationfolder
		# Create a new card. Details and pictures from USB-drive
		USER_INP = simpledialog.askstring(title="Name required!", prompt="Enter name for new FIDO key:")
		USER_INP2 = simpledialog.askstring(title="Description required!", prompt="Description for the new FIDO key:")
		
		new_FIDOkey = [USER_INP, USER_INP2, '<Empty>']
		completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"	
		try:
			f = open(completeName, 'a')
			writer = csv.writer(f)
			writer.writerow(new_FIDOkey)
			f.close()
		except FileNotFoundError:
			messagebox.showinfo("Information", "No FIDO keys file found.")
		self.create_FIDOmeny()
			
	def create_Boltcardmeny(self):
		global Boltcard_button_color
		global filepathdestinationfolder
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="brown"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		left_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=278, 
		height=634,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="gray1"
		)
		left_Frame.place(relx=0, rely=0, anchor="nw")	
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=650,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=0, anchor="nw")
		pathtobackg = "/home/user1/venvpython/images/boltcardbackground.JPG"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoIDimage = str(filepathdestinationfolder) + "/venvpython/images/boltcardicon.JPG"

			IDimagebutton = ctk.CTkImage(light_image=Image.open(pathtoIDimage), dark_image=Image.open(pathtoIDimage), size=(230, 100))
			completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			counter = 0
			Buttonnew = ctk.CTkButton(right_Frame, text="New card", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newcard)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			
			readButton = ctk.CTkButton(right_Frame, text="Read UID/URI", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.readUUID_with_NFC)
			readButton.place(relx=0.9, rely=0.11, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			
			infoLabel = ctk.CTkLabel(right_Frame, text="Create a new Bolt card:", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.1, rely=0.15, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			
			infoLabel = ctk.CTkLabel(right_Frame, text="1. Register a user account at a LNBits Hub (ex. lates.lightningok.win or similar).", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.1, rely=0.2, anchor="w")
			infoLabel2 = ctk.CTkLabel(right_Frame, text="   - Create a wallet, activate the extensions \"Bolts card\" and LNURLp.", text_color="white", font=my_font, fg_color="black")
			infoLabel2.place(relx=0.1, rely=0.24, anchor="w")
			infoLabel3 = ctk.CTkLabel(right_Frame, text="2. Use apps \"NFC tools\" and \"Bolt Card NFC Card Creator\" to make a card.", text_color="white", font=my_font, fg_color="black")
			infoLabel3.place(relx=0.1, rely=0.29, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="3. With the data from your LNBits Hub- account make a text file with eight lines:", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.33, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - LNURL link", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.37, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Reset code", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.41, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Program code", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.45, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Withdrawal limit", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.49, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Daily withdrawal limit", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.53, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Link to the Bolt Hub", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.57, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Bolt Hub user name", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.61, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="   - Bolt Hub account password", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.65, anchor="w")
			infoLabel5 = ctk.CTkLabel(right_Frame, text="4. Using the text file, create a new Bolt card entry on the offline device by clicking \"New card\".", text_color="white", font=my_font, fg_color="black")
			infoLabel5.place(relx=0.1, rely=0.69, anchor="w")
			infoLabel5 = ctk.CTkLabel(right_Frame, text="Alt. You can receive an encrypted and signed file with above textlines and add it by clicking \"New card\".", text_color="white", font=my_font, fg_color="black")
			infoLabel5.place(relx=0.1, rely=0.74, anchor="w")
			
			proLabel = ctk.CTkLabel(right_Frame, text="(Pro tip1: If you get the file sent to you. Make sure it's encypted with your public key.)", text_color="white", font=my_font, fg_color="black")
			proLabel.place(relx=0.1, rely=0.8, anchor="w")
			proLabel2 = ctk.CTkLabel(right_Frame, text="(Pro tip2: Using https://ff.io or https://boltz.exchange/swap with swap from Liquid-BTC (l-BTC) will save on fees.)", text_color="white", font=my_font, fg_color="black")
			proLabel2.place(relx=0.1, rely=0.85, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)								
			cardLabel = ctk.CTkLabel(left_Frame, text="Bolt cards", text_color="white", font=my_font, fg_color="black").pack(padx=10, pady=8, side= TOP, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			Counting = 0
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							if Counting == 0:	
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showcard, lines[0]))
								Button1.pack(padx=10, pady=18, side= TOP, anchor="w")
							else:
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showcard, lines[0]))
								Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							Counting += 1
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Bolt cards file found.")
		else:
			notOKButton = ctk.CTkButton(right_Frame, text="You are not logged in.", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def showcard(self, cardname):
		global filepathdestinationfolder
		global pathtoloadaddress
		
		def save_load_QR():
			tk.messagebox.showinfo('Information', 'Insert the USB-device."')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select where to save the image with the load- address."')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			pathtopic = outputdir + '/Boltcard_load_address.png'
			shutil.copy(pathtoloadaddress, pathtopic)
			
			if os.path.isfile(pathtopic):
				tk.messagebox.showinfo('Information', 'QR image has been saved."')
			
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		left_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=278, 
		height=634,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="gray1"
		)
		left_Frame.place(relx=0, rely=0, anchor="nw")
		
		pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=650,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=0, anchor="nw")
		
		pathtobackg = "/home/user1/venvpython/images/boltcardbackground.JPG"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoboltcardicon = str(filepathdestinationfolder) + "/venvpython/images/boltcardicon.JPG"

			boltcardiconimage = ctk.CTkImage(light_image=Image.open(pathtoboltcardicon), dark_image=Image.open(pathtoboltcardicon), size=(230, 100))
			
			completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							Button1 = ctk.CTkButton(left_Frame, text="", image = boltcardiconimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showcard, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Bolt cards file found.")
			Buttonnew = ctk.CTkButton(right_Frame, text="New card", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newcard)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						try:
							if lines[0] == cardname:
								# Generate QR-codes for Public address and WIF-address and read them to display on screen
								load_address = qrcode.make(lines[3], version=1)
								reset_key = qrcode.make(lines[4], version=1)
								
								resize_load_address = load_address.resize((280, 280))
								resize_reset_key = reset_key.resize((300, 300))
								pathtoloadaddress = str(filepathdestinationfolder) + "/secure/boltcards/load.png"
								pathtoresetkey = str(filepathdestinationfolder) + "/secure/boltcards/reset.png"
								
								resize_load_address.save(pathtoloadaddress)
								resize_reset_key.save(pathtoresetkey)

								loadimg = ctk.CTkImage(light_image=Image.open(pathtoloadaddress), dark_image=Image.open(pathtoloadaddress), size=(280, 280))

								resetimg = ctk.CTkImage(light_image=Image.open(pathtoresetkey), dark_image=Image.open(pathtoresetkey), size=(300, 300))
								
								my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			
								pubLabel = ctk.CTkLabel(right_Frame, text="Load (via Lightning network):", text_color="white", font=my_font, fg_color="black")
								pubLabel.place(relx=0.06, rely=0.12, anchor="w")
								Labelpublicimg = ctk.CTkLabel(right_Frame,  text = "", image = loadimg)
								Labelpublicimg.place(relx=0.2, rely=0.4, anchor="center")
								
								wifLabel = ctk.CTkLabel(right_Frame, text="Reset Boltcard:", text_color="white", font=my_font, fg_color="black")
								wifLabel.place(relx=0.74, rely=0.12, anchor="w")
								Labelwifimg = ctk.CTkLabel(right_Frame, text = "", image = resetimg)
								Labelwifimg.place(relx=0.8, rely=0.4, anchor="center")	
								
								my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=True, overstrike=False)
								nameheadLabel = ctk.CTkLabel(right_Frame, text="Name of Bolt card:", text_color="white", font=my_font, fg_color="black")
								nameheadLabel.place(relx=0.5, rely=0.18, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
								nameLabel = ctk.CTkLabel(right_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
								nameLabel.place(relx=0.5, rely=0.22, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
								
								descrheadLabel = ctk.CTkLabel(right_Frame, text="Description:", text_color="white", font=my_font, fg_color="black")
								descrheadLabel.place(relx=0.5, rely=0.27, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
								descrLabel = ctk.CTkLabel(right_Frame, text=lines[1], text_color="white", font=my_font, fg_color="black")
								descrLabel.place(relx=0.5, rely=0.31, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
								descrheadLabel = ctk.CTkLabel(right_Frame, text="Max withrawal limit:", text_color="white", font=my_font, fg_color="black")
								descrheadLabel.place(relx=0.5, rely=0.36, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
								descrLabel = ctk.CTkLabel(right_Frame, text=lines[6], text_color="white", font=my_font, fg_color="black")
								descrLabel.place(relx=0.5, rely=0.4, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
								descrheadLabel = ctk.CTkLabel(right_Frame, text="Max daily withrawal limit:", text_color="white", font=my_font, fg_color="black")
								descrheadLabel.place(relx=0.5, rely=0.45, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)								
								descrLabel = ctk.CTkLabel(right_Frame, text=lines[7], text_color="white", font=my_font, fg_color="black")
								descrLabel.place(relx=0.5, rely=0.49, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
								dateheadLabel = ctk.CTkLabel(right_Frame, text="Created", text_color="white", font=my_font, fg_color="black")
								dateheadLabel.place(relx=0.5, rely=0.54, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
								dateLabel = ctk.CTkLabel(right_Frame, text=lines[2], text_color="white", font=my_font, fg_color="black")
								dateLabel.place(relx=0.5, rely=0.58, anchor="center")
								
								saveQRButton = ctk.CTkButton(right_Frame, text="Save the Load QR-code to USB", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=save_load_QR)
								saveQRButton.place(relx=0.06, rely=0.66, anchor="w")
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
								programButton = ctk.CTkButton(right_Frame, text="Program (using Smartcard reader)", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.programcard_with_NFC, cardname))
								programButton.place(relx=0.49, rely=0.72, anchor="center")
								programButton2 = ctk.CTkButton(right_Frame, text="Program (using a Smartphone)", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.programcard, cardname))
								programButton2.place(relx=0.49, rely=0.78, anchor="center")
								delButton = ctk.CTkButton(right_Frame, text="Delete card", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.deletecard, cardname))
								delButton.place(relx=0.49, rely=0.86, anchor="center")
								backButton = ctk.CTkButton(right_Frame, text="Back", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Boltcardmeny)
								backButton.place(relx=0.49, rely=0.92, anchor="center")
						except:
							print("Cardname not found. Except.")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Bolt cards file found.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def readUUID_with_NFC(self):
		global filepathdestinationfolder
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		def do_readUUID_with_NFC():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)

			bolt_uid = boltlib.read_uid()
			bolt_uri = boltlib.read_uri()
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			waitLabel = ctk.CTkLabel(my_Frame, text='UUID:', text_color="white", font=my_font, fg_color="black")
			waitLabel.place(relx=0.5, rely=0.24, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=34, slant="roman", underline=False, overstrike=False)
			waitLabel = ctk.CTkLabel(my_Frame, text=bolt_uid, text_color="white", font=my_font, fg_color="black")
			waitLabel.place(relx=0.5, rely=0.36, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			waitLabel = ctk.CTkLabel(my_Frame, text='URI:', text_color="white", font=my_font, fg_color="black")
			waitLabel.place(relx=0.5, rely=0.56, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			waitLabel = ctk.CTkLabel(my_Frame, text=bolt_uri, text_color="white", font=my_font, fg_color="black")
			waitLabel.place(relx=0.5, rely=0.62, anchor="center")
			backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Boltcardmeny)
			backButton.place(relx=0.5, rely=0.9, anchor="center")
			
		# Instructions to read URI from Bolt card with Smartcard reader
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)

		Label = ctk.CTkLabel(my_Frame, text="Reading a Bolt card's URI and its UUID (Unique User Identification number) using a Smartcard reader *", text_color="white", font=my_font, fg_color="black")
		Label.place(relx=0.5, rely=0.2, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label2 = ctk.CTkLabel(my_Frame, text="(* Tested with HID Omnikey 5022 CL.)", text_color="white", font=my_font, fg_color="black")
		Label2.place(relx=0.5, rely=0.26, anchor="center")
		Label3 = ctk.CTkLabel(my_Frame, text='After pressing the \"Start\"- button, hold the Bolt card close to the Smartcard reader to read it.', text_color="white", font=my_font, fg_color="black")
		Label3.place(relx=0.5, rely=0.49, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		Label4 = ctk.CTkLabel(my_Frame, text='(Make sure that the Smartcard reader is connected.).', text_color="white", font=my_font, fg_color="black")
		Label4.place(relx=0.5, rely=0.54, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		backButton = ctk.CTkButton(my_Frame, text="Start", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=do_readUUID_with_NFC)
		backButton.place(relx=0.5, rely=0.6, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Boltcardmeny)
		backButton.place(relx=0.5, rely=0.9, anchor="center")
		
	def programcard_with_NFC(self, cardname):
		global filepathdestinationfolder
		global theURI
		
		theURI = ''
		print(cardname)
		completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
		updatedcompleteName = str(filepathdestinationfolder) + "/secure/boltcards/updatedboltcards.csv"
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		def do_programcard_with_NFC():
			global theURI
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			waitLabel = ctk.CTkLabel(my_Frame, text='Waiting for smartcard.....', text_color="white", font=my_font, fg_color="black")
			waitLabel.place(relx=0.5, rely=0.37, anchor="center")
			my_Frame.focus_set()
			my_Frame.focus_force()
			write_uri = boltlib.write_uri(theURI)

			self.create_Boltcardmeny()
		
		completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
		try:
			with open(completeName, 'r') as file:
				csvfile = csv.reader(file)
				for lines in csvfile:
					if lines[0] == cardname:
						theURI = lines[3]					
		except FileNotFoundError:
			messagebox.showinfo("Information", "No Bolt cards file found.")
			
		# Instructions Bolt card programming with Smartcard reader
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)

		Label = ctk.CTkLabel(my_Frame, text="Programming a Bolt card with only a receive address (LNURL) using a Smartcard reader *", text_color="white", font=my_font, fg_color="black")
		Label.place(relx=0.5, rely=0.2, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label2 = ctk.CTkLabel(my_Frame, text="(* Tested with HID Omnikey 5022 CL. For now, full programming is not available unless using smartphone with app.)", text_color="white", font=my_font, fg_color="black")
		Label2.place(relx=0.5, rely=0.26, anchor="center")
		Label3 = ctk.CTkLabel(my_Frame, text='After pressing the \"Start\"- button, hold the card close to the Smartcard reader to program it.', text_color="white", font=my_font, fg_color="black")
		Label3.place(relx=0.5, rely=0.49, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		Label4 = ctk.CTkLabel(my_Frame, text='(Make sure that the Smartcard reader is connected.).', text_color="white", font=my_font, fg_color="black")
		Label4.place(relx=0.5, rely=0.54, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		backButton = ctk.CTkButton(my_Frame, text="Start", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=do_programcard_with_NFC)
		backButton.place(relx=0.5, rely=0.6, anchor="center")
		backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Boltcardmeny)
		backButton.place(relx=0.5, rely=0.9, anchor="center")
		
	def programcard(self, cardname):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
		updatedcompleteName = str(filepathdestinationfolder) + "/secure/boltcards/updatedboltcards.csv"
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
		try:
			with open(completeName, 'r') as file:
				csvfile = csv.reader(file)
				for lines in csvfile:
					try:
						if lines[0] == cardname:
							# Generate QR-code for programming the bolt card, display on screen
							program_QRpic = qrcode.make(lines[5], version=1)
							
							resized_program_QRpic = program_QRpic.resize((320, 320))

							pathtoprogramaddress = str(filepathdestinationfolder) + "/secure/boltcards/program.png"
							
							resized_program_QRpic.save(pathtoprogramaddress)

							programimg = ctk.CTkImage(light_image=Image.open(pathtoprogramaddress), dark_image=Image.open(pathtoprogramaddress), size=(320, 320))

							my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
		
							pubLabel = ctk.CTkLabel(my_Frame, text="Program (via smartphone app *)", text_color="white", font=my_font, fg_color="black")
							pubLabel.place(relx=0.5, rely=0.05, anchor="center")
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
							pubLabel = ctk.CTkLabel(my_Frame, text="(* Bolt Card NFC Card Creator- app from App/Play-store)", text_color="white", font=my_font, fg_color="black")
							pubLabel.place(relx=0.5, rely=0.1, anchor="center")
							Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = programimg)
							Labelpublicimg.place(relx=0.5, rely=0.4, anchor="center")
							desLabel = ctk.CTkLabel(my_Frame, text='Bolt Hub link: ' + lines[8], text_color="white", font=my_font, fg_color="black")
							desLabel.place(relx=0.5, rely=0.72, anchor="center")
							desLabel = ctk.CTkLabel(my_Frame, text='Bolt Hub User name: ' + lines[9], text_color="white", font=my_font, fg_color="black")
							desLabel.place(relx=0.5, rely=0.77, anchor="center")
							desLabel = ctk.CTkLabel(my_Frame, text='Bolt Hub user password: ' + lines[10], text_color="white", font=my_font, fg_color="black")
							desLabel.place(relx=0.5, rely=0.82, anchor="center")
					except:
							print("Cardname not found. Except.")
							
		except FileNotFoundError:
			messagebox.showinfo("Information", "No Bolt cards file found.")
		
		backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Boltcardmeny)
		backButton.place(relx=0.5, rely=0.9, anchor="center")
		
	def deletecard(self, cardname):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
		updatedcompleteName = str(filepathdestinationfolder) + "/secure/boltcards/updatedboltcards.csv"
		with open(completeName, 'r') as source, open(updatedcompleteName, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[0] == cardname:
						answer = messagebox.askquestion('Important!', 'Are you sure you want to delete the Bolt card?')
						if answer == 'yes':
							print("Not sure")
						else:
							csvwriter.writerow(row)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updatedcompleteName, completeName)
		os.remove(updatedcompleteName)	
		self.create_Boltcardmeny()
		
	def newcard(self):
		global filepathdestinationfolder
		# Create a new card. Details and pictures from USB-drive
		USER_INP = simpledialog.askstring(title="Name required!", prompt="Name for the new Bolt card:")
		USER_INP2 = simpledialog.askstring(title="Description required!", prompt="Description for the new Bolt card:")
			
		answer = messagebox.askquestion('Information!', 'Is the Bolt card data in a signed and encrypted file?')
			
		if answer == 'yes':
			try:
				messagebox.showinfo("Bolt card data required", "Connect the USB-device. Select the encrypted file with the Bolt card data.")
				time.sleep(3)
				filepathdatafile = filedialog.askopenfilename(initialdir='/media/user1')
				completeTempName = filepathdestinationfolder + '/secure/boltcards/boltcardtemp.txt'
				gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
				# Decrypt the file and output it to a temporary file
				data_ = gpg.decrypt_file(filepathdatafile, output=completeTempName)
				# Check if data was OK
				if data_.ok:
					if data_.trust_level is not None and data_.trust_level >= data_.TRUST_FULLY:
						# If the trust for the signature key is OK then read the temporary file and split into lines
						try:
							lines = open(completeTempName).read().splitlines()
						except IOError:
							messagebox.showinfo("Information", "There was a problem reading the file!")
						
						if len(lines) == 8:
							completeName = filepathdestinationfolder + "/secure/boltcards/boltcards.csv"
							thedate = str(date.today())

							new_boltcard = [USER_INP, USER_INP2, thedate, lines[0], lines[1], lines[2], lines[3], lines[4], lines[5], lines[6], lines[7]]
							
							f = open(completeName, 'a')
							writer = csv.writer(f)
							writer.writerow(new_boltcard)
							f.close()
							messagebox.showinfo("Information", "Success! Signature (Key ID: " + data_.key_id + ") is good. New Bolt card added.")
							self.create_Boltcardmeny()
						else:
							messagebox.showinfo("Information", "There was a problem reading the decrypted content! \nMake sure that it contains exactly eight lines of data.")
					else:
						messagebox.showinfo("Alert!", "Signature could not be verified!")
						self.create_Boltcardmeny()
				else:
					messagebox.showinfo('Information', data_.status)
					self.create_Boltcardmeny()
			except IOError:
				messagebox.showinfo("Information", "There was a problem reading the file!")
		else:
			messagebox.showinfo("Bolt card data required", "Connect the USB-device. Select the file with the Bolt card data.")
			time.sleep(3)
			filepathdatafile = filedialog.askopenfilename(initialdir='/media/user1')
			
			try:
				lines = open(filepathdatafile).read().splitlines()
			except IOError:
				messagebox.showinfo("Information", "There was a problem reading the file!")
			if len(lines) == 8:
				completeName = filepathdestinationfolder + "/secure/boltcards/boltcards.csv"
				thedate = str(date.today())

				new_boltcard = [USER_INP, USER_INP2, thedate, lines[0],lines[1],lines[2],lines[3], lines[4], lines[5],lines[6],lines[7]]
				
				f = open(completeName, 'a')
				writer = csv.writer(f)
				writer.writerow(new_boltcard)
				f.close()
			else:
				messagebox.showinfo("Information", "There was a problem reading the file! \nMake sure there is exactly eight lines with the required data in the file?")
			
		self.create_Boltcardmeny()
						
	def create_DigitalIDmeny(self):
		global DigitalID_button_color
		global filepathdestinationfolder
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=0,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		left_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=278, 
		height=634,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="gray1"
		)
		left_Frame.place(relx=0, rely=0, anchor="nw")		
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=650,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=0, anchor="nw")
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		pathtoIDimage = str(filepathdestinationfolder) + "/venvpython/images/DemoID.JPG"

		IDimagebutton = ctk.CTkImage(light_image=Image.open(pathtoIDimage), dark_image=Image.open(pathtoIDimage), size=(200, 100))
		
		completeName = str(filepathdestinationfolder) + "/secure/ID/IDs.csv"
		
		Counting = 0
		FirstID = 'empty'
		try:
			with open(completeName, 'r') as file:
				csvfile = csv.reader(file)
				for lines in csvfile:
					if lines:
						if Counting == 0:	
							Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=200, height=100, font=my_font, command=partial(self.showID, lines[1]))
							Button1.pack(padx=10, pady=18, side= TOP, anchor="w")
							FirstID = lines[1]
						else:
							Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=200, height=100, font=my_font, command=partial(self.showID, lines[1]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
						Counting += 1
		except FileNotFoundError:
			messagebox.showinfo("Information", "No IDs file found.")
		if FirstID != 'empty':
			self.showID(FirstID)
		else:
			Buttonnew = ctk.CTkButton(right_Frame, text="New ID", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.create_newID)
			Buttonnew.place(relx=0.88, rely=0.07, anchor="center")
		
			emptyButton = ctk.CTkButton(right_Frame, text="There are no ID's.", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.create_DigitalIDmeny)
			emptyButton.place(relx=0.5, rely=0.45, anchor="center")	
	
	def showID(self, IDfingerprint):
		global newIDflag
		global filepathdestinationfolder
		global bg_img
		global resize_QR_address_img
		global IDPhotoImage
		def add_validation():
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			tk.messagebox.showinfo('Information', 'Insert the USB-device."')
			time.sleep(4)
			tk.messagebox.showinfo('Information', 'Select the file/key with the verifying signature.')
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			
			# Scan the key in the file to get the fingerprint
			keys = gpg.scan_keys(filepathSourcefile)
			key_fingerprint = ''
			key_fingerprint = str(keys.fingerprints[0])
			
			# Import the key from file to the local keychain and assign trust
			import_result = gpg.import_keys_file(filepathSourcefile)
			gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
			
			# Sign the key on local keychain by passing argument fingerprint
			
			command= 'gpg --local-user ' + IDfingerprint + ' --quick-sign-key ' + key_fingerprint
			os.system(command) 
			self.showID(IDfingerprint)
					
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		left_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=278, 
		height=634,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="gray1"
		)
		left_Frame.place(relx=0, rely=0, anchor="nw")
		
		pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=648,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=2, anchor="nw")
		
		ID_Frame = ctk.CTkFrame(right_Frame, 
		width=720, 
		height=460,
		border_width=2,
		border_color="brown",
		fg_color="light pink"
		)
		ID_Frame.place(x=80, y=40, anchor="nw")
		
		bottom_Frame = ctk.CTkScrollableFrame(right_Frame, 
		width=700, 
		height=100,
		orientation="vertical",
		border_width=2,
		border_color="brown",
		fg_color="light pink"
		)
		bottom_Frame._scrollbar.configure(height=0)
		bottom_Frame.place(x=80, y=525, anchor="nw")
		
		def export_key():
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			ascii_armoured_public_key = gpg.export_keys(IDfingerprint)
			tk.messagebox.showinfo('Information', 'Select where to save the file with the public ID key."')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			c = open(outputdir + '/publicIDkey' + IDfingerprint + '.gpg', 'w')
			c.write(ascii_armoured_public_key)
			c.close()
			tk.messagebox.showinfo('Information', 'ID Key has been exported.')
			self.create_DigitalIDmeny()
			
		def export_image():
			tk.messagebox.showinfo('Information', 'Select the directory where you want to save the image."')
			time.sleep(4)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			full_path = outputdir + '/ID_' + IDfingerprint + '.png'

			x0 = ID_Frame.winfo_rootx()
			y0 = ID_Frame.winfo_rooty()
			x1 = x0 + 720
			y1 = y0 + 460
			
			im = ImageGrab.grab(bbox=(x0, y0, x1, y1))
			im.save(full_path)
			self.create_DigitalIDmeny()
		
		def create_ICON():
			global newIDflag
			pathtoIDicon = filepathdestinationfolder + "/secure/ID/ICON" + IDfingerprint + ".jpg"
			pathtotemppic = filepathdestinationfolder + '/ID.jpg'
			pathtotemppic2 = filepathdestinationfolder + '/venvpython/ID.jpg'
			os.remove(pathtotemppic)
			os.remove(pathtotemppic2)
			x0 = ID_Frame.winfo_rootx()
			y0 = ID_Frame.winfo_rooty()
			x1 = x0 + 720
			y1 = y0 + 460
			im = ImageGrab.grab(bbox=(x0, y0, x1, y1))
			im.save(pathtoIDicon)
			newIDflag = False
			self.create_DigitalIDmeny()
				
		pathtobackg = "/home/user1/venvpython/images/boltcardbackground.JPG"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			completeName = str(filepathdestinationfolder) + "/secure/ID/IDs.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							if not newIDflag:
								pathtoIDicon = filepathdestinationfolder + "/secure/ID/ICON" + lines[1] + ".jpg"
								IDcardiconimage = ctk.CTkImage(light_image=Image.open(pathtoIDicon), dark_image=Image.open(pathtoIDicon), size=(200, 127))
					
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDcardiconimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=200, height=127, font=my_font, command=partial(self.showID, lines[1]))
								Button1.pack(padx=20, pady=8, side= TOP, anchor="w")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No IDs file found.")
			Buttonnew = ctk.CTkButton(right_Frame, text="New ID", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.create_newID)
			Buttonnew.place(relx=0.9, rely=0.03, anchor="center")
			completeName = str(filepathdestinationfolder) + "/secure/ID/IDs.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[1] == IDfingerprint:
							# Make a canvas with background images
							bg_img = PhotoImage(file=r'/home/user1/venvpython/images/ID_map.png')
							
							# Image resize and open as PhotoImage for QR-code
							QR_address = qrcode.make(lines[1], version=1)
							resize_QR_address = QR_address.resize((180, 180))
							
							pathtoQRaddress = str(filepathdestinationfolder) + "/secure/ID/QRaddress.png"
							
							resize_QR_address.save(pathtoQRaddress)
							
							resize_QR_address_img = PhotoImage(file=r'/home/user1/secure/ID/QRaddress.png')
							
							# Image resize and open as PhotoImage for ID picture
							pathpic = filepathdestinationfolder + "/secure/ID/picture" + IDfingerprint + ".jpg"
							ID_pic = Image.open(pathpic)
							resize_ID_pic = ID_pic.resize((210, 242))
							
							pathtoIDPhotoImage = str(filepathdestinationfolder) + "/secure/ID/IDPhotoImage.png"
							
							resize_ID_pic.save(pathtoIDPhotoImage)
							
							IDPhotoImage = PhotoImage(file=r'/home/user1/secure/ID/IDPhotoImage.png')
							
							canvas_map = Canvas(ID_Frame, width=720, height=460)
							canvas_map.pack(fill="both", expand=True)
							
							canvas_map.create_image(0,0, image=bg_img, anchor="nw") 
							canvas_map.create_image(18,110, image=resize_QR_address_img, anchor="nw") 
							canvas_map.create_image(485,75, image=IDPhotoImage, anchor="nw") 							
							
							#Create texts
							my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
							canvas_map.create_text(360,32, text=lines[0], font=my_font)
							
							my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
							canvas_map.create_text(205,110, text="Name:", anchor="nw", font=my_font)
							canvas_map.create_text(315,110, text=lines[2], anchor="nw", font=my_font)
							
							canvas_map.create_text(205,140, text="Last name:", anchor="nw", font=my_font)
							canvas_map.create_text(315,140, text=lines[3], anchor="nw", font=my_font)
							
							canvas_map.create_text(205,220, text="Gender:", anchor="nw", font=my_font)
							canvas_map.create_text(315,220, text=lines[7], anchor="nw", font=my_font)
							
							canvas_map.create_text(205,250, text="Birthdate:", anchor="nw", font=my_font)
							canvas_map.create_text(315,250, text=lines[6], anchor="nw", font=my_font)
							
							canvas_map.create_text(30,360, text="Key ID:", anchor="nw", font=my_font)
							canvas_map.create_text(110,360, text=lines[1], anchor="nw", font=my_font)
							
							canvas_map.create_text(30,395, text="(Encryption standard RFC4880, RSA. Key length 4096 bits)", anchor="nw", font=my_font)							
							
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
							exportKeyButton = ctk.CTkButton(right_Frame, text="Export public ID Key", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=export_key)
							exportKeyButton.place(relx=0.12, rely=0.03, anchor="center")
							exportButton = ctk.CTkButton(right_Frame, text="Export image", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=export_image)
							exportButton.place(relx=0.32, rely=0.03, anchor="center")
							exportButton = ctk.CTkButton(right_Frame, text="Add validation", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=add_validation)
							exportButton.place(relx=0.52, rely=0.03, anchor="center")
							deleteButton = ctk.CTkButton(right_Frame, text="Delete ID", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=partial(self.do_deleteID, IDfingerprint))
							deleteButton.place(relx=0.72, rely=0.03, anchor="center")
							
							valiLabel = ctk.CTkLabel(right_Frame, text="Validating signatures: ", text_color="white", font=my_font, fg_color="black")
							valiLabel.place(x=80, y=520, anchor="nw")
							
							gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
							# Get sigs for the selected key
							public_keys = gpg.list_keys(sigs=True)
							
							if not newIDflag:
								for i in public_keys:
									if i['fingerprint'] == IDfingerprint and i['sigs']: 
										my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
								
										tuple_of_sigs_in_key = i['sigs']

										for ii in tuple_of_sigs_in_key:
											if ii:
												if ii[0] != i['keyid']:
													keyID = ii[0]
													user_id = ii[1]
													signature_class = ii[2]
													Label = ctk.CTkLabel(bottom_Frame, text= keyID + ' ' +  user_id + ' ' + signature_class, text_color="black", fg_color="light pink", font=my_font)
													Label.pack(padx=10, pady=1, side= TOP, anchor="w")
								ID_Frame.lift()	
								bottom_Frame.lift()
							else:
								messagebox.showinfo("Information", "In the terminal window that will open, type \"addphoto\" and hit Enter. Enter name of photo as \"ID.jpg\" and hit Enter. Follow the instructions. Type \"quit\" when finished. To close the terminal window type \"exit\" and hit Enter.")
								pathtopic = filepathdestinationfolder + "/secure/ID/picture" + IDfingerprint + ".jpg"
								pathtotemppic = filepathdestinationfolder + '/ID.jpg'
								pathtotemppic2 = filepathdestinationfolder + '/venvpython/ID.jpg'
								shutil.copy(pathtopic, pathtotemppic)
								shutil.copy(pathtopic, pathtotemppic2)
								command= 'gpg --edit-key ' + IDfingerprint
								os.system("lxterminal -e 'bash -c \""+command+";bash\"'") 
								ID_Frame.lift()	
								messagebox.showinfo("Information", "In the terminal window that will open, type \"addphoto\" and hit Enter. Enter name of photo as \"ID.jpg\" and hit Enter. Follow the instructions. Type \"quit\" when finished. To close the terminal window type \"exit\" and hit Enter.")
								nextButton = ctk.CTkButton(right_Frame, text="CLICK TO COMPLETE ID!", text_color="white", fg_color="brown", border_width=2, border_color="white", width=180, height=32, font=my_font, command=create_ICON)
								nextButton.place(relx=0.5, rely=0.8, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No ID file found.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
				
	def do_deleteID(self, IDfingerprint):
		global filepathdestinationfolder
		notset_str = 'all'
		path_to_IDs = str(filepathdestinationfolder) + "/secure/ID/IDs.csv"
		updated_path_to_IDs = str(filepathdestinationfolder) + "/secure/ID/updatedIDs.csv"
		with open(path_to_IDs, 'r') as source, open(updated_path_to_IDs, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[1] == IDfingerprint:
						answer = messagebox.askquestion('Important!', 'Are you sure you want to delete the ID?')
						if answer == 'yes':
							print("Not sure")
						else:
							csvwriter.writerow(row)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_IDs, path_to_IDs)
		os.remove(updated_path_to_IDs)	
		self.create_DigitalIDmeny()
		
	def create_newID(self):
		global System_button_color
		global filepathdestinationfolder
		global newIDflag
		logged_in_user = '< Not logged in >'
		
		def do_newID():
			global newIDflag
			alreadyThere = False
			today = date.today()
			entry_name = nameEntry.get()
			entry_lastname = lastnameEntry.get()
			entry_address = addressEntry.get()
			entry_address2 = address2Entry.get()
			clicked_privateKey = str(clicked.get())
			thedate = cal.get_date()
			clicked_Sex = clicked2.get()
			datetoday = today.strftime('%d/%m/%Y')
			
			messagebox.showinfo("Information", "Select your picture (.jpg format) for the ID.")
			pathpic = filedialog.askopenfilename(initialdir='/media/user1')
			pathdest = filepathdestinationfolder + "/secure/ID/picture" + clicked_privateKey + ".jpg"
			shutil.copy(pathpic, pathdest)
			
			new_ID = [
								'Standard ID',
								clicked_privateKey,
								entry_name,
								entry_lastname,
								entry_address,
								entry_address2,
								str(thedate),
								clicked_Sex,
								datetoday]
			
			completeName = filepathdestinationfolder + "/secure/ID/IDs.csv"
			# Check if ID already exists for the selected key
			with open(completeName, 'r') as file:
				csvfile = csv.reader(file)
				for lines in csvfile:
					if lines:
						if lines[1] == clicked_privateKey:
							alreadyThere = True
			if not alreadyThere:
				with open(completeName, 'a') as result:
					csvwriter = csv.writer(result)
					csvwriter.writerow(new_ID)
				newIDflag = True
				self.showID(clicked_privateKey)
			else:
				tk.messagebox.showinfo('Information', 'There already exists an ID for the selected key."')
				self.create_DigitalIDmeny()
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluewaves.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		if path_to_USB_secure == 'Secure USB folder is available':
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							logged_in_user = lines[0]
			except FileNotFoundError:
				logged_in_user = '<no settings file found>'
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		private_keys = gpg.list_keys(True)
		
		clicked = StringVar()
			
		List_fingerprints = []
		
		for i in private_keys:
			List_fingerprints.append(i['fingerprint'])
							
		List_Sex = ['Male', 'Female']
		
		clicked = StringVar()
		clicked2 = StringVar()
		
		clicked.set(List_fingerprints[0])
		clicked2.set("Male")
		
		thelogged_in_user = ctk.StringVar(value=logged_in_user)
		thelogged_in_user2 = ctk.StringVar(value=logged_in_user)
		empty_var = ctk.StringVar(value="<empty>")
		empty_var2 = ctk.StringVar(value="<empty>")
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="italic", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Create a new digital ID", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.48, rely=0.1, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		nameLabel = ctk.CTkLabel(my_Frame, text="First name:", text_color="white", fg_color="black", font=my_font)
		nameLabel.place(relx=0.28, rely=0.22, anchor="e")
		
		nameEntry = ctk.CTkEntry(my_Frame, placeholder_text=logged_in_user, textvariable=thelogged_in_user, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		nameEntry.place(relx=0.66, rely=0.22, anchor="e")
		
		lastnameLabel = ctk.CTkLabel(my_Frame, text="Last name:", text_color="white", fg_color="black", font=my_font)
		lastnameLabel.place(relx=0.28, rely=0.28, anchor="e")
		
		lastnameEntry = ctk.CTkEntry(my_Frame, placeholder_text=logged_in_user, textvariable=thelogged_in_user2, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		lastnameEntry.place(relx=0.66, rely=0.28, anchor="e")
		
		addressLabel = ctk.CTkLabel(my_Frame, text="Address row 1:", text_color="white", fg_color="black", font=my_font)
		addressLabel.place(relx=0.28, rely=0.36, anchor="e")
		
		addressEntry = ctk.CTkEntry(my_Frame, placeholder_text="<empty>", textvariable=empty_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		addressEntry.place(relx=0.66, rely=0.36, anchor="e")
		
		address2Label = ctk.CTkLabel(my_Frame, text="Address row 2:", text_color="white", fg_color="black", font=my_font)
		address2Label.place(relx=0.28, rely=0.44, anchor="e")
		
		address2Entry = ctk.CTkEntry(my_Frame, placeholder_text="<empty>", textvariable=empty_var2, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		address2Entry.place(relx=0.66, rely=0.44, anchor="e")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Select encryption key:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.28, rely=0.52, anchor="e")
		
		drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
		drop.place(relx=0.66, rely=0.52, anchor="e")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Select birth date:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.28, rely=0.6, anchor="e")
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2024)
		cal.place(relx=0.66, rely=0.6, anchor="e")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Select sex:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.28, rely=0.68, anchor="e")
		
		drop2 = OptionMenu(my_Frame, clicked2, *List_Sex)
		drop2.place(relx=0.66, rely=0.68, anchor="e")
		
		Button = ctk.CTkButton(my_Frame, text="Create new ID", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=do_newID)
		Button.place(relx=0.55, rely=0.78, anchor="w")
		
	def create_getSettimetextbox(self):
		global System_button_color
		logged_in_user = '< Not logged in >'
		users_theme = 'Standard'
		users_colors = 'Varied'
		
		def setdateandtime():
			thedate = cal.get_date()
			thetime = time_picker.time()
			
			thedatestr = str('sudo date -s \'' + str(thedate) + ' ' + str(thetime[0]) + ':' + str(thetime[1]) + ':00\'')			
			os.system(thedatestr)
			thestr = 'sudo hwclock -w'	
			os.system(thestr)
			os.system(thestr)
			self.create_Hometextbox()
		
		def update_account():
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			Updated_Username = nameEntry.get()
			clicked_Theme = clicked.get()
			clicked_Color = clicked2.get()
			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			
			with open(completeName, 'w') as result:
				csvwriter = csv.writer(result)
				new_settings = [
								Updated_Username,
								clicked_Theme,
								clicked_Color]

				csvwriter.writerow(new_settings)
			self.set_colors(clicked_Color)
			self.create_meny()
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluewaves.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		if path_to_USB_secure == 'Secure USB folder is available':
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							logged_in_user = lines[0]
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				logged_in_user = '<no settings file found>'
					
		List_Themes = ['Standard', 'Dark', 'Light', 'Summer', 'Winter']
		List_Colors = ['Varied', 'DarkBlue', 'Green', 'Red', 'Purple', 'Brown', 'deep pink']
		
		clicked = StringVar()
		clicked2 = StringVar()
		
		clicked.set(users_theme)
		clicked2.set(users_colors)
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Update account settings:", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.28, rely=0.1, anchor="e")
		
		nameLabel = ctk.CTkLabel(my_Frame, text="User name:", text_color="white", fg_color="black", font=my_font)
		nameLabel.place(relx=0.18, rely=0.24, anchor="e")
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		thelogged_in_user = ctk.StringVar(value=logged_in_user)
		
		nameEntry = ctk.CTkEntry(my_Frame, placeholder_text=logged_in_user, textvariable=thelogged_in_user, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		nameEntry.place(relx=0.19, rely=0.24, anchor="w")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Select theme:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.18, rely=0.33, anchor="e")
		
		drop = OptionMenu(my_Frame, clicked, *List_Themes)
		drop.place(relx=0.46, rely=0.33, anchor="e")

		Label1 = ctk.CTkLabel(my_Frame, text="Select color:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.18, rely=0.42, anchor="e")
		drop2 = OptionMenu(my_Frame, clicked2, *List_Colors)
		drop2.place(relx=0.46, rely=0.42, anchor="e")
		
		if path_to_USB_secure == 'Secure USB folder is available':	
			Button = ctk.CTkButton(my_Frame, text="Update account", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=update_account)
			Button.place(relx=0.32, rely=0.55, anchor="w")
				
		Label1 = ctk.CTkLabel(my_Frame, text="Set time and date:", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.68, rely=0.1, anchor="e")

		time_picker = AnalogPicker(my_Frame, type=constants.HOURS24)
		time_picker.setHours(datetime.now().hour)
		time_picker.setMinutes(datetime.now().minute)
		time_picker.place(relx=0.84, rely=0.21, anchor="ne")
		
		theme = AnalogThemes(time_picker)
		theme.setNavyBlue()
		time_picker.configAnalog(textcolor="#ffffff", bg="#0a0832", bdColor="#000000", headbdcolor="#000000")
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2024)
		cal.place(relx=0.84, rely=0.76, anchor="e")
			
		setButton = ctk.CTkButton(my_Frame, text="Set time/date", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=setdateandtime) 
		setButton.place(relx=0.84, rely=0.84, anchor="e")
		
		softwareButton = ctk.CTkButton(my_Frame, text=" (Update software)", text_color="white", fg_color="black", border_width=2, border_color="black", font=my_font, command=self.updateSoftware) 
		softwareButton.place(relx=0.5, rely=0.9, anchor="center")
	
	def updateReboot(self):
	
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global s_width,s_height
		
		#The big frame
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/blue.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(s_width, s_height))
		Label_backg = ctk.CTkLabel(my_big_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		Label_backg.focus_set()
		Label_backg.focus_force()
		
		my_big_Frame.focus_set()
		my_big_Frame.focus_force()
		
		my_font = ctk.CTkFont(family="Arial", size=28, weight="bold", slant="roman", underline=False, overstrike=False)
		
		infoLabel = ctk.CTkLabel(my_big_Frame, text="Encrypting the device and rebooting...", text_color="white", font=my_font, fg_color="navy blue")
		infoLabel.place(relx=0.5, rely=0.42, anchor="center")
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		if path_to_USB_secure == 'Secure USB folder is available':
			
			full_path = str(filepathdestinationfolder) + "/secure/"
			
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			# Encrypt the tarfile and remove the unencrypted tarfile
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)

			# Write the encrypted file to disk
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			full_path = str(filepathdestinationfolder) + "/secure"
			cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  full_path
			os.system(cmd)
			os.system('sudo shutdown -r now')
		else:
			os.system('sudo shutdown -r now')
			
	def updateSoftware(self):
		global System_button_color
		global filepathdestinationfolder
		global softwareVersion
		global softwareStatus
		
		def do_updateSoftware():			
			# Make temporary directory for software update
			pathtempfolder = filepathdestinationfolder + '/tempsystem/'
			App_source_File = pathtempfolder + '/GUIApp.py'
			App_dest_File = '/home/user1/venvpython/GUIApp.py'
			
			os.makedirs(os.path.dirname(pathtempfolder))
			
			# Select tar-file with software update
			messagebox.showinfo("Information", "Select file for software update.")
			pathSoftwarefile = filedialog.askopenfilename(initialdir='/media/user1')
				
			# Open tar-archive and write to temporary directory
			try:
				# Open the tar-archive and place the content in the system update temp directory 
				tar = tarfile.open(pathSoftwarefile) 
				tar.extractall(pathtempfolder)
				tar.close()		
			except FileNotFoundError:
				messagebox.showinfo("Information", "No file found.")
			
			# Copy the GUIapp.py file to main Python folder
			shutil.copy(App_source_File, App_dest_File)
			
			# Remove the system update temp directory 
			cmd = 'find ' +  pathtempfolder + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  pathtempfolder
			os.system(cmd)
			
			answer = messagebox.askquestion('Information!', 'Restart the Offline device for the changes to take effect?')
			
			if answer == 'yes':
				self.updateReboot()
			else:	
				self.create_meny()
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluewaves.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		my_font = ctk.CTkFont(family="Arial", size=26, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Update the system software", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.2, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		nameLabel = ctk.CTkLabel(my_Frame, text="Current software version: " + softwareVersion + " (" + softwareStatus + ")", text_color="white", fg_color="black", font=my_font)
		nameLabel.place(relx=0.5, rely=0.27, anchor="center")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Updating the software will make sure that you have the latest improvements and functionality.", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.5, rely=0.38, anchor="center")
		Label2 = ctk.CTkLabel(my_Frame, text="Make sure you have all keys and files backed-up on at least one seperate USB-device before proceeding!", font=my_font, text_color="white", fg_color="black")
		Label2.place(relx=0.5, rely=0.44, anchor="center")
		Label3 = ctk.CTkLabel(my_Frame, text="Insert the USB-device with the updated software before starting.", font=my_font, text_color="white", fg_color="black")
		Label3.place(relx=0.5, rely=0.53, anchor="center")	
		selectButton = ctk.CTkButton(my_Frame, text="Start update!", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=do_updateSoftware) 
		selectButton.place(relx=0.5, rely=0.66, anchor="center")
		
		backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=self.create_getSettimetextbox) 
		backButton.place(relx=0.5, rely=0.86, anchor="center")
		
	def create_Hometextbox(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global PersonalGPGKey
		global filepathdestinationfolder
		global System_button_color
		global softwareVersion
		global softwareStatus
		amount_round = 0.0
		amount = 0.0
		notset_str = ''
		logged_in_user = ''
		users_theme = ''
		users_colors = ''
		main_frame_bg = 'black'
		main_frame_bg_mid = 'black'
		def clock():
			hour = time.strftime("%H")
			minute = time.strftime("%M")
			second = time.strftime("%S")
			
			timeLabel.config(text=hour + ":" + minute + ":" + second)
			timeLabel.after(1000, clock)
		
		def date():
			weekday = time.strftime("%A")
			dayofmonth = time.strftime("%d")
			month = time.strftime("%B")
			
			dateLabel.config(text=weekday + " the " + dayofmonth + " of " + month)
			dateLabel.after(1000, date)
		def update():
			timeLabel.config(text="New Text")	
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluewaves.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
				main_frame_bg = 'dim grey'
				main_frame_bg_mid = 'grey21'
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		timeLabel = tk.Label(self, text="", font=("Helvetica", 16), fg="white", bg=main_frame_bg)
		dateLabel = tk.Label(self, text="", font=("Helvetica", 16), fg="white", bg=main_frame_bg)
		
		clock()
		date()
		
		timeLabel.place(relx=0.95, rely=0.94, anchor="e")
		dateLabel.place(relx=0.95, rely=0.97, anchor="e")
		
		if path_to_USB_secure == 'Secure USB folder is available':	
			completeName = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							if lines[0] != 'Spent':
								amount = amount + float(lines[5])
			except FileNotFoundError:
				messagebox.showinfo("Information", "No paper wallet file found.")
			
			amount_round = round(amount, 7)			
			theamountandBTC = str(amount_round) + ' BTC'
			amountButton = ctk.CTkButton(self, text=theamountandBTC, text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
			amountButton.place(relx=0.48, rely=0.48, anchor="w")
			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							logged_in_user = lines[0]
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
				
			my_font = ctk.CTkFont(family="Tahoma", size=34, weight="bold", slant="roman", underline=True, overstrike=False)
			welcomelabel = ctk.CTkLabel(self, text="WELCOME  " + logged_in_user, text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			welcomelabel.place(relx=0.5, rely=0.34, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="italic", underline=False, overstrike=False)
			applabel = ctk.CTkLabel(self, text="App: GUIApp.py.", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			applabel.place(relx=0.5, rely=0.37, anchor="center")
			versionLabel = ctk.CTkLabel(self, text="Version: " + softwareVersion + " (" + softwareStatus + ")", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			versionLabel.place(relx=0.5, rely=0.39, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			systemLabel = ctk.CTkLabel(self, text="------------------------------------------------------------------------------------------------ System overview ------------------------------------------------------------------------------------------------ ", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			systemLabel.place(relx=0.5, rely=0.42, anchor="center")
			Label1 = ctk.CTkLabel(self, text="Personal key (fingerprint):", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label1.place(relx=0.47, rely=0.45, anchor="e")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			
			Button1 = ctk.CTkButton(self, text= PersonalGPGKey, text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=self.create_GPGmeny)
			Button1.place(relx=0.48, rely=0.45, anchor="w")
			
			BTCLabel = ctk.CTkLabel(self, text="BTC in offline storage:", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			BTCLabel.place(relx=0.47, rely=0.48, anchor="e")
			Label3 = ctk.CTkLabel(self, text="Secure archive status:", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label3.place(relx=0.47, rely=0.51, anchor="e")
			
			Button4 = ctk.CTkButton(self, text="Available", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=self.create_SecUSBmeny)
			Button4.place(relx=0.48, rely=0.51, anchor="w")
				
			Label4 = ctk.CTkLabel(self, text="Secure archive size (MB):", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label4.place(relx=0.47, rely=0.54, anchor="e")
			
			size = 0.0
			secure_folder_path = filepathdestinationfolder + '/secure'
			the_dir = Path(secure_folder_path)
			size = sum(f.stat().st_size for f in the_dir.glob('**/*') if f.is_file())
			 
			size_kb = size / 1024
			size_mb = size_kb / 1024
			answer = str(round(size_mb, 2))
			Button3 = ctk.CTkButton(self, text=answer, text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=self.check_SecUSB)
			Button3.place(relx=0.48, rely=0.54, anchor="w")
			
			Label5 = ctk.CTkLabel(self, text="Latest modification/backup:", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label5.place(relx=0.47, rely=0.57, anchor="e")
			Button5 = ctk.CTkButton(self, text=timeSecUSBLastModified, text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=self.create_SecUSBmeny)
			Button5.place(relx=0.48, rely=0.57, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=44, weight="bold", slant="roman", underline=False, overstrike=False)
			
			iconlock_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconlocked.png"), dark_image=Image.open("/home/user1/venvpython/images/iconlocked.png"), size=(35, 35))
			iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconopen.png"), dark_image=Image.open("/home/user1/venvpython/images/iconopen.png"), size=(35, 35))

			LoginButton = ctk.CTkButton(my_Frame, image=iconlock_image, text=" Logout", compound="left", corner_radius=25, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=my_font, command=self.encrypt_SecUSB)
			LoginButton.place(relx=0.5, rely=0.7, anchor="center")
			iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconopen.png"), dark_image=Image.open("/home/user1/venvpython/images/iconopen.png"), size=(30, 30))
			openlock_Label = ctk.CTkLabel(self, text="", image=iconopen_image, fg_color=main_frame_bg)
			openlock_Label.place(relx=0.02, rely=0.94, anchor="w")
		else:
			iconlock_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconlocked.png"), dark_image=Image.open("/home/user1/venvpython/images/iconlocked.png"), size=(35, 35))
			iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconopen.png"), dark_image=Image.open("/home/user1/venvpython/images/iconopen.png"), size=(35, 35))
			
			my_font = ctk.CTkFont(family="Arial", size=44, weight="bold", slant="roman", underline=False, overstrike=False)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
			private_keys = gpg.list_keys(True)
			
			clicked = StringVar()
				
			List_fingerprints = []
			
			for i in private_keys:
				List_fingerprints.append(i['fingerprint'])
			
			if not List_fingerprints:	
				startButton = ctk.CTkButton(my_Frame, text=" Start ", corner_radius=25, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=my_font, command=self.new_user_account_selection)
				startButton.place(relx=0.5, rely=0.37, anchor="center")
			else:
				LoginButton = ctk.CTkButton(my_Frame, image=iconopen_image, text=" Login", compound="left", corner_radius=25, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=my_font, command=self.decrypt_SecUSB)
				LoginButton.place(relx=0.5, rely=0.35, anchor="center")
				
				LoginButton = ctk.CTkButton(my_Frame, text=" Create new account", corner_radius=15, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=("Arial", 18), command=self.new_user_account_selection)
				LoginButton.place(relx=0.5, rely=0.47, anchor="center")
				
				iconlock_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconlocked.png"), dark_image=Image.open("/home/user1/venvpython/images/iconlocked.png"), size=(30, 30))
				closedlock_Label = ctk.CTkLabel(self, text="", image=iconlock_image, fg_color=main_frame_bg)
				closedlock_Label.place(relx=0.02, rely=0.94, anchor="w")
				
			my_font = ctk.CTkFont(family="Times", size=14, slant="italic", underline=False, overstrike=False)	
			LoginButton = ctk.CTkButton(my_Frame, text="(Restore from backup)", corner_radius=15, text_color="white", fg_color='black', border_width=3, border_color="black", font=("Arial", 15), command=self.restoreFromencrypted_SecUSB)
			LoginButton.place(relx=0.5, rely=0.54, anchor="center")
	
	def GnuPG_Home(self):		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		l1_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="green"
		)
		l1_Frame.place(relx=0.27, rely=0.35, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(l1_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		l2_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="green"
		)
		l2_Frame.place(relx=0.27, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(l2_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		l3_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="green"
		)
		l3_Frame.place(relx=0.27, rely=0.85, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(l3_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		r1_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="green"
		)
		r1_Frame.place(relx=0.73, rely=0.35, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(r1_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		r2_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="green"
		)
		r2_Frame.place(relx=0.73, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(r2_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		r3_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="green"
		)
		r3_Frame.place(relx=0.73, rely=0.85, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(r3_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
			
		my_font = ctk.CTkFont(family="Tahoma", size=34, weight="bold", slant="roman", underline=True, overstrike=False)
		welcomelabel = ctk.CTkLabel(my_Frame, text="Gnu Privacy Guard", text_color="light green", fg_color="black", font=my_font)
		welcomelabel.place(relx=0.5, rely=0.1, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="italic", underline=False, overstrike=False)
		applabel = ctk.CTkLabel(my_Frame, text="Version: 2.2.27", text_color="light green", fg_color="black", font=my_font)
		applabel.place(relx=0.5, rely=0.17, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		systemLabel = ctk.CTkLabel(my_Frame, text="------------------------------------------------------------------------------------------------ Overview ------------------------------------------------------------------------------------------------ ", text_color="light green", fg_color="black", font=my_font)
		systemLabel.place(relx=0.5, rely=0.22, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The first left box
		Label_l1 = ctk.CTkLabel(l1_Frame, text="Check local keys", text_color="light green", fg_color="black", font=my_font)
		Label_l1.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(l1_Frame, text="View all keys on the local keychain.\nBoth the primary key's and subkey's are listed.\nSubkey's that have been moved to a Yubikey is\nmarked as such.", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The second left box
		Label5 = ctk.CTkLabel(l2_Frame,text="Add/remove key", text_color="light green", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(l2_Frame, text="Add a new key or remove keys or subkeys.\nIf a new key is going to have subkeys (that can be\nmoved) then check the box \"only certify\".\nThis will create a certifying key with three subkeys.", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The third left box
		Label5 = ctk.CTkLabel(l3_Frame, text="Add subkeys", text_color="light green", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(l3_Frame, text="Add subkeys to a already created key.\nIt will create three subkeys at once. Encrypt, sign\nand authenticate.", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The first right box
		Label_l1 = ctk.CTkLabel(r1_Frame, text="Backup keys", text_color="light green", fg_color="black", font=my_font)
		Label_l1.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r1_Frame, text="Backup all the public keys on the local keychain\nand also the secret key that you select.\nThis require that you are logged in.", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The second right box
		Label5 = ctk.CTkLabel(r2_Frame,text="Import/export", text_color="light green", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r2_Frame, text="Move a key from a file to the local keychain.\nKey file should be in ASC-format.\nExport a private or public key to a file.\n", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The third rigth box
		Label5 = ctk.CTkLabel(r3_Frame, text="Sign/validate", text_color="light green", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r3_Frame, text="Sign keys or files with one of the private keys on\nthe local keychain. Signing a file will generate\na \"detached signature\".", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		
	def get_GnuPGKeys(self):		
		my_Frame = ctk.CTkScrollableFrame(self, 
		width=1176, 
		height=634,
		border_width=2,
		border_color="green",
		fg_color="gray1"
		)

		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Keys located on the local keychain.", text_color="light green", fg_color="black", font=my_font)
		Label1.pack(padx=25, pady=2, side= TOP, anchor="w")
		Label2 = ctk.CTkLabel(my_Frame, text="Encryption: Standard: RFC 4880.", text_color="light green", fg_color="black", font=my_font)
		Label2.pack(padx=25, pady=2, side= TOP, anchor="w")
		Label4 = ctk.CTkLabel(my_Frame, text="Key lenght: 4096 bits.", text_color="light green", fg_color="black", font=my_font)
		Label4.pack(padx=25, pady=2, side= TOP, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label5 = ctk.CTkLabel(my_Frame, text="Private keys", text_color="light green", fg_color="black", font=my_font)
		Label5.pack(padx=25, pady=5, side= TOP, anchor="w")
		Label6 = ctk.CTkLabel(my_Frame, text="-------------------------------------------------------------------------------------", text_color="light green", fg_color="black", font=my_font)
		Label6.pack(padx=25, pady=2, side= TOP, anchor="w")
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		public_keys = []
		private_keys = []
		
		public_keys = gpg.list_keys()
		private_keys = gpg.list_keys(True)
		mapp = private_keys.key_map

		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		
		if private_keys:	 
			for i in private_keys:
				Label = ctk.CTkLabel(my_Frame, text=str(i['uids']) + ' ' + str(i['fingerprint']) + '\n', text_color="light green", fg_color="black", font=my_font)
				Label.pack(padx=25, pady=2, side= TOP, anchor="w")

				if i['subkeys']: 
					my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
			
					listoflistindict = i['subkeys']
					dictofsubkeyinfo = i['subkey_info']

					for ii in listoflistindict:
						if ii:
							subkinfo = ii[0]
							keytype = dictofsubkeyinfo[subkinfo]['type']
							capacity = dictofsubkeyinfo[subkinfo]['cap']
							token = dictofsubkeyinfo[subkinfo]['token']

							datecrea = int(dictofsubkeyinfo[subkinfo]['date'])		
							dt_datecrea = datetime.fromtimestamp(datecrea)
							dt_datecrea_form = dt_datecrea.strftime('%Y-%m-%d')
							
							dateexp = int(dictofsubkeyinfo[subkinfo]['expires'])
							dt_dateexp = datetime.fromtimestamp(dateexp)
							dt_dateexp_form  = dt_dateexp.strftime('%Y-%m-%d')
							
							if capacity == 's':
								capacity = 'Signing'
							if capacity == 'e':
								capacity = 'Encryption'
							if capacity == 'a':
								capacity = 'Authenticate'
							if token != '#': 
								if token == '>': 
									Label = ctk.CTkLabel(my_Frame, text= '         ' + '\"' + capacity + '\"' + ' subkey: ' + ii[2] + '. Created: ' + dt_datecrea_form + '. Expires: ' + dt_dateexp_form + ' (Moved to a Yubikey).', text_color="light green", fg_color="black", font=my_font)
									Label.pack(padx=25, pady=2, side= TOP, anchor="w")
								else:
									Label = ctk.CTkLabel(my_Frame, text= '         ' + '\"' + capacity + '\"' + ' subkey: ' + ii[2] + '. Created: ' + dt_datecrea_form + '. Expires: ' + dt_dateexp_form + ' (' + keytype + ').', text_color="light green", fg_color="black", font=my_font)
									Label.pack(padx=25, pady=2, side= TOP, anchor="w")
		else:
			Label = ctk.CTkLabel(my_Frame, text='<empty>', text_color="light green", fg_color="black", font=my_font)
			Label.pack(padx=25, pady=2, side= TOP, anchor="w") 

		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label7 = ctk.CTkLabel(my_Frame, text="Public keys", text_color="light green", fg_color="black", font=my_font)
		Label7.pack(padx=25, pady=5, side= TOP, anchor="w")

		
		Label8 = ctk.CTkLabel(my_Frame, text="-------------------------------------------------------------------------------------", text_color="light green", fg_color="black", font=my_font)
		Label8.pack(padx=25, pady=2, side= TOP, anchor="w")

		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		if public_keys:
			for i2 in public_keys:
				
				if i2['expires']:
					dictofsubkeyinfo2 = int(i2.get("expires")) 
					dateexp2 = int(dictofsubkeyinfo2)
					dt_dateexp2 = datetime.fromtimestamp(dateexp2)
					dt_dateexp_form2  = dt_dateexp2.strftime('%Y-%m-%d')
					Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']) + ' ' + str(i2['fingerprint']) + ' Expires: ' + dt_dateexp_form2, text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=25, pady=2, side= TOP, anchor="w")
				else:
					Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']) + ' ' + str(i2['fingerprint']) + ' Expires: <unknown>', text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=25, pady=2, side= TOP, anchor="w")
		else:
			Label = ctk.CTkLabel(my_Frame, text='<empty>', text_color="light green", fg_color="black", font=my_font)
			Label.pack(padx=25, pady=2, side= TOP, anchor="w")
	
	def export_subkey(self):
		global clicked_privateKey
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		def do_export_subkey():
			global clicked_privateKey
			
			clicked_privateKey = str(clicked.get())

			tk.messagebox.showinfo('Information', 'Select the directory where you want to save the subkey that will be exported from the local keychain."')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')

			command= 'gpg -a -o ' + outputdir + '/privatesubkey' + clicked_privateKey + '.gpg --export-secret-subkeys ' + clicked_privateKey
			os.system(command) 
			tk.messagebox.showinfo('Information', 'Key has been exported.')
			self.create_GPGmeny()
		
		private_keys = []
		
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Export subkeys.", text_color="light green", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="The subkeys will be exported as a ASCII armored file.", text_color="light green", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Select the subkey that you want to export.", text_color="light green", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.17, anchor="w")
		
		Label4 = ctk.CTkLabel(my_Frame, text="Then select where to place the file containing the exported subkey", text_color="light green", fg_color="black", font=my_font)
		Label4.place(relx=0.05, rely=0.22, anchor="w")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
			
		for i in private_keys:
			List_fingerprints.append(i['fingerprint'])
		if List_fingerprints:	
			privatekeysavailable = True
			
		list_subkeyfingerprints = []
		subavail = False
		if private_keys:	 
			for i in private_keys:
				if i['subkeys']: 
					listoflistindict = i['subkeys']
					dictofsubkeyinfo = i['subkey_info']
					for ii in listoflistindict:
						if ii:
							list_subkeyfingerprints.append(ii[2])
					clicked.set(list_subkeyfingerprints[0])
					subavail = True
		else:
			Label = ctk.CTkLabel(my_Frame, text='<empty>', text_color="light green", fg_color="black", font=my_font)
			Label.place(relx=0.05, rely=the_y_value, anchor="w")
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if subavail:
			Label1 = ctk.CTkLabel(my_Frame, text="Select the subkey to export:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *list_subkeyfingerprints)
			drop.place(relx=0.35, rely=0.4, anchor="w")
			
			Button2 = ctk.CTkButton(my_Frame, text="Export key", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=do_export_subkey)
			Button2.place(relx=0.56, rely=0.5, anchor="w")
		else:
			Label1 = ctk.CTkLabel(my_Frame, text="There are no subkey's to export.", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
						
	def backupGPG_Keys(self):
		global filepathdestinationfolder
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		def do_backupGPG_Keys():
			clicked_privateKey = str(clicked.get())
			
			my_Frame = ctk.CTkFrame(self, 
			width=1200, 
			height=650,
			border_width=4,
			border_color="green"
			)
			my_Frame.place(relx=0.5, rely=0.6, anchor="center")
			
			pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			public_keys = gpg.list_keys() 
			List_fingerprints = []
			
			Label5 = ctk.CTkLabel(my_Frame, text="The following public key\'s has been exported from the keychain and a copy stored in the secure archive:", text_color="light green", fg_color="black", font=my_font)
			Label5.place(relx=0.05, rely=0.1, anchor="w")
		
			Label6 = ctk.CTkLabel(my_Frame, text="________________________________________________________________________________________________________", text_color="light green", fg_color="black", font=my_font)
			Label6.place(relx=0.05, rely=0.14, anchor="w")
			ii = 0
			the_y_value = 0.2
			for i in public_keys:
				keyfilename = 'publicKey' + i['fingerprint'] + '.gpg'
				List_fingerprints.append(i['fingerprint'])
				#list_uids.append(i['uids'])
				Label = ctk.CTkLabel(my_Frame, text=str(i['uids']) + ' ' + str(i['fingerprint']), text_color="light green", fg_color="black", font=my_font)
				Label.place(relx=0.05, rely=the_y_value, anchor="w")
				the_y_value = the_y_value + 0.05
		
				ascii_armored_public_key = gpg.export_keys(List_fingerprints[ii]) 
				completeName = filepathdestinationfolder + '/secure/keys/' + keyfilename
				f2 = open(completeName, 'w')
				f2.write(ascii_armored_public_key)
				f2.close()
				ii = ii+1
			the_y_value = the_y_value + 0.05
			Label7 = ctk.CTkLabel(my_Frame, text="The following private key has been exported from the keychain and a copy stored in the secure archive:", text_color="light green", fg_color="black", font=my_font)
			Label7.place(relx=0.05, rely=the_y_value, anchor="w")
		
			the_y_value = the_y_value + 0.04
		
			Label8 = ctk.CTkLabel(my_Frame, text="________________________________________________________________________________________________________", text_color="light green", fg_color="black", font=my_font)
			Label8.place(relx=0.05, rely=the_y_value, anchor="w")
		
			the_y_value = the_y_value + 0.05

			#keyfilename = 'privateKey' + clicked_privateKey + '.gpg'
			
			Label = ctk.CTkLabel(my_Frame, text=clicked_privateKey, text_color="light green", fg_color="black", font=my_font)
			Label.place(relx=0.05, rely=the_y_value, anchor="w")
			
			ascii_armored_private_key = gpg.export_keys(clicked_privateKey, True, expect_passphrase=False)
			completeName = filepathdestinationfolder + '/secure/keys/' + 'privateKey' + clicked_privateKey + '.gpg' 
			f2 = open(completeName, 'w')
			f2.write(ascii_armored_private_key)
			f2.close()
			if clicked_privateKey == PersonalGPGKey:
				shutil.copy(completeName, filepathdestinationfolder)
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')	
		private_keys = gpg.list_keys(True)
					
		clicked = StringVar()
			
		List_fingerprints = []
		if path_to_USB_secure == 'Secure USB folder is available':
				
			for i in private_keys:
				List_fingerprints.append(i['fingerprint'])
				
			clicked.set(List_fingerprints[0])
			
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			Label1 = ctk.CTkLabel(my_Frame, text="Backup a key on the local keychain to the secure archive", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.22, anchor="center")	
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Label1 = ctk.CTkLabel(my_Frame, text="Select what private key to backup:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.42, rely=0.48, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.43, rely=0.48, anchor="w")
			
			Button = ctk.CTkButton(my_Frame, text="Backup key\'s to secure archive", text_color="white", fg_color="green", border_width=2, border_color="white", font=my_font, command=do_backupGPG_Keys)
			Button.place(relx=0.56, rely=0.54, anchor="w")
		else:
			Button8 = ctk.CTkButton(self, text="You are not logged in. Backup of keys are not possible. Decrypt now?", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			Button8.place(relx=0.5, rely=0.5, anchor="center")
	
	def import_or_export(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Button8 = ctk.CTkButton(self, text="Import key from file on USB-device", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.importGPG_Key)
		Button8.place(relx=0.5, rely=0.4, anchor="center")
		Button8 = ctk.CTkButton(self, text="Import key from file in the Secure archive", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.importGPG_Key_from_archive)
		Button8.place(relx=0.5, rely=0.45, anchor="center")
		Label = ctk.CTkLabel(self, text="Or", text_color="white", font=("Helvetica", 18), fg_color="black")
		Label.place(relx=0.5, rely=0.5, anchor="center")
		Button7 = ctk.CTkButton(self, text="Export private key from local keychain to file", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.exportGPG)
		Button7.place(relx=0.5, rely=0.55, anchor="center")
		Button8 = ctk.CTkButton(self, text="Export private subkey from local keychain to file", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.export_subkey)
		Button8.place(relx=0.5, rely=0.6, anchor="center")
		Button9 = ctk.CTkButton(self, text="Export public key from local keychain to file", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.exportGPGmypublic)
		Button9.place(relx=0.5, rely=0.65, anchor="center")	
		
	def newGPGFull_Key(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		def tPassphrase():
			if Secret_passphrase.cget('show') == '':
				Secret_passphrase.configure(show='*')
			else:
				Secret_passphrase.configure(show='')
		def do_newGPGFull():
		
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			if checkbox.get() == "on":
				input_data = gpg.gen_key_input(key_type='rsa', name_real=Real_name.get(), expire_date='0', key_length='4096', key_usage='cert', name_email=Name_email.get(), passphrase=Secret_passphrase.get())
				key = gpg.gen_key(input_data)
			else:
				input_data = gpg.gen_key_input(key_type='rsa', name_real=Real_name.get(), expire_date='0', key_length='4096', name_email=Name_email.get(), passphrase=Secret_passphrase.get())
				key = gpg.gen_key(input_data)
			tk.messagebox.showinfo('Information', 'Key has been created.')
			self.get_GnuPGKeys()
			
		def do_deleteGPGkey():
			global clicked_privateKey
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			clicked_privateKey = clicked.get()
			answer = messagebox.askquestion('WARNING!', 'WARNING! You are about to delete a private key! Are you SURE you want to remove it?')
			
			if answer == 'yes':
				try:
					key = gpg.delete_keys(clicked_privateKey, True, expect_passphrase=False) 
				except ValueError as ve:
					messagebox.showinfo('Information', 'Something went wrong.')

				messagebox.showinfo('Information', 'Private key has been removed.')
				self.get_GnuPGKeys()
			else:
				messagebox.showinfo("Information", "OK. Keeping the private key.")
				self.get_GnuPGKeys()
		
		def do_deletepublicGPGkey():			
			clicked_publicKey = str(clicked2.get())
		
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			key = gpg.delete_keys(clicked_publicKey)
			
			tk.messagebox.showinfo('Information', 'Public key has been removed.')
			self.get_GnuPGKeys()
			
		Label1 = ctk.CTkLabel(my_Frame, text="Manage the private and public keys on the local keychain.", text_color="light green", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="The private key used for encrypting the content on the offline device must be with full functionality and the \"only certify\"-", text_color="light green", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="checkbox should NOT be checked.", text_color="light green", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.17, anchor="w")
		
		Label4 = ctk.CTkLabel(my_Frame, text="Check the \"only certify\"-checkbox* for a private key intended for external communication (could be with a Yubikey)", text_color="light green", fg_color="black", font=my_font)
		Label4.place(relx=0.05, rely=0.22, anchor="w")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		private_keys = gpg.list_keys(True)
		public_keys = gpg.list_keys()
				
		clicked = StringVar()
		clicked2 = StringVar()
		check_var = ctk.StringVar(value="off")
	
		List_fingerprints = []
		List_fingerprint_info = []
		List_publicfingerprints = []
		
		privatekeysavailable = False
		publickeysavailable = False
		
		for nkey in private_keys:
			List_fingerprints.append(nkey['fingerprint'])
			
		if private_keys:
			clicked.set(List_fingerprints[0])
			privatekeysavailable = True
					
		for i2 in public_keys:
			List_publicfingerprints.append(i2['fingerprint'])
		if List_publicfingerprints:
			clicked2.set(List_publicfingerprints[0])
			publickeysavailable = True
		
		Label2 = ctk.CTkLabel(my_Frame, text="Full name:", font=my_font, text_color="white", fg_color="black")
		Label2.place(relx=0.34, rely=0.3, anchor="e")
		Real_name = ctk.CTkEntry(my_Frame, placeholder_text="Bob Smith", font=my_font, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8)
		Real_name.place(relx=0.35, rely=0.3, anchor="w")
		Label5 = ctk.CTkLabel(my_Frame, text="Email:", font=my_font, text_color="white", fg_color="black")
		Label5.place(relx=0.34, rely=0.35, anchor="e")
		Name_email = ctk.CTkEntry(my_Frame, placeholder_text="bob.smaith@cyb.org", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8)
		Name_email.place(relx=0.35, rely=0.35, anchor="w")
		Label6 = ctk.CTkLabel(my_Frame, text="Secret passphrase:", font=my_font, text_color="white", fg_color="black")
		Label6.place(relx=0.34, rely=0.4, anchor="e")
		Secret_passphrase = ctk.CTkEntry(my_Frame, placeholder_text="*********************", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8)
		Secret_passphrase.place(relx=0.35, rely=0.4, anchor="w")
		tButton = ctk.CTkButton(my_Frame, text="Show/hide passphrase", font=my_font, text_color="black", fg_color="pink", border_width=2, border_color="white", command=tPassphrase)
		tButton.place(relx=0.72, rely=0.4, anchor="center")
		checkbox = ctk.CTkCheckBox(my_Frame, text="Only certify *", font=my_font, variable=check_var, onvalue="on", offvalue="off", text_color="white", fg_color="black")
		checkbox.place(relx=0.35, rely=0.46, anchor="w")
		Button = ctk.CTkButton(my_Frame, text="Create new GPG key", font=my_font, text_color="white", fg_color="green", border_width=2, border_color="white", command=do_newGPGFull)
		Button.place(relx=0.48, rely=0.51, anchor="w")
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select private key to remove:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.58, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.35, rely=0.58, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Remove private key**", font=my_font, text_color="white", fg_color="green", border_width=2, border_color="white", command=do_deleteGPGkey)
			Button2.place(relx=0.54, rely=0.63, anchor="w")
			Label1 = ctk.CTkLabel(my_Frame, text="**Always remove the private key first in a private/public keypair", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.5, rely=0.69, anchor="center")
		if publickeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select public key to remove:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.76, anchor="e")
			drop2 = OptionMenu(my_Frame, clicked2, *List_publicfingerprints)
			drop2.place(relx=0.35, rely=0.76, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Remove public key**", font=my_font, text_color="white", fg_color="green", border_width=2, border_color="white", command=do_deletepublicGPGkey)
			Button2.place(relx=0.55, rely=0.81, anchor="w")
	
	def setup_Yubikey(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
		autPolicy = ctk.StringVar(value="off")
		encPolicy = ctk.StringVar(value="off")
		sigPolicy = ctk.StringVar(value="off")
		
		def resetFIDOYubikey():
			# Reset the FIDO on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK"')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			command= 'ykman fido reset'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.create_Yubikeymeny()
		
		def changePINsopenpgpYubikey():
			# Reset the FIDO on the Yubikey
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open: \n1. Type \"admin\" and hit enter to toggle until it says \"admin commands are allowed\"\n2. Type \"passwd\" hit enter.\nSelect \"3\" and hit enter.\n        Enter current admin PIN (default admin PIN is 12345678).\n      Add new admin PIN (min 8 digits).\n        Confirm the new admin PIN.\n3. Select \"1\" and hit enter.\n      Enter current PIN (default PIN is 123456).\n      Add new PIN (min 6 digits).\n        Confirm new PIN.\n4. Type \"q\" and hit enter.\n5. Type \"quit\" and hit enter.\n6. Exit the terminal by typing \"exit\" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.4, anchor="center")
			
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK"')
			time.sleep(3)
			
			goButton = ctk.CTkButton(my_Frame, text="Start", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=changePINsopenpgpYubikey_step2)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
		
		def changePINsopenpgpYubikey_step2():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open: \n1. Type \"admin\" and hit enter to toggle until it says \"admin commands are allowed\"\n2. Type \"passwd\" hit enter.\nSelect \"3\" and hit enter.\n        Enter current admin PIN (default admin PIN is 12345678).\n      Add new admin PIN (min 8 digits).\n        Confirm the new admin PIN.\n3. Select \"1\" and hit enter.\n      Enter current PIN (default PIN is 123456).\n      Add new PIN (min 6 digits).\n        Confirm new PIN.\n4. Type \"q\" and hit enter.\n5. Type \"quit\" and hit enter.\n6. Exit the terminal by typing \"exit\" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.4, anchor="center")
			
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			command= 'gpg --card-edit'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			
			goButton = ctk.CTkButton(my_Frame, text="Finish", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.create_Yubikeymeny)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
				
		def resetOpenPGPYubikey():
			# Reset the FIDO on the Yubikey
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='Follow the instructions in the terminal window that will open.\n\nAfter resetting the OpenPGP on the Yubikey type "exit" and hit enter to close the terminal window.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK"')
			time.sleep(3)
			
			goButton = ctk.CTkButton(my_Frame, text="Start", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=resetOpenPGPYubikey_step2)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
		
		def resetOpenPGPYubikey_step2():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='Follow the instructions in the terminal window that will open.\n\nAfter resetting the OpenPGP on the Yubikey type "exit" and hit enter to close the terminal window.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			command= 'ykman openpgp reset'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			
			goButton = ctk.CTkButton(my_Frame, text="Finish", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.create_Yubikeymeny)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
			
		def setautTouchYubikey():
			# Set aut touch policy on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window that will open.\n\nAfter resetting the OpenPGP on the Yubikey type "exit" and hit enter to close the terminal window.')
			if autPolicyCheckBox.get() == 'on':
				command= 'ykman openpgp keys set-touch aut on'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			else:
				command= 'ykman openpgp keys set-touch aut off'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.create_Yubikeymeny()
			
		def setencTouchYubikey():
			# Set enc touch policy on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			if encPolicyCheckBox.get() == 'on':
				command= 'ykman openpgp keys set-touch enc on'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			else:
				command= 'ykman openpgp keys set-touch enc off'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.create_Yubikeymeny()
			
		def setsigTouchYubikey():
			# Set sig touch policy on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			if sigPolicyCheckBox.get() == 'on':
				command= 'ykman openpgp keys set-touch sig on'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			else:
				command= 'ykman openpgp keys set-touch sig off'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.create_Yubikeymeny()
				
		def changeNameYubikey():
			# Set the PINs, name and email on the Yubikey
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, remove and re-connect the Yubikey.')
			time.sleep(3)
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open: \n1. Type \"admin\" and hit enter to toggle until it says \"admin commands are allowed\"\n2. Type \"name\" hit enter.\n3. Enter name details.\n4. Type \"quit\" and hit enter.\n5. Exit the terminal by typing \"exit\" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			goButton = ctk.CTkButton(my_Frame, text="Start", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=changeNameYubikey2)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
		
		def changeNameYubikey2():
			command= 'gpg --card-edit'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In the terminal window that will open: \n1. Type \"admin\" and hit enter to toggle until it says \"admin commands are allowed\"\n2. Type \"name\" hit enter.\n3. Enter name details.\n4. Type \"quit\" and hit enter.\n5. Exit the terminal by typing \"exit\" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			goButton = ctk.CTkButton(my_Frame, text="Next", text_color="white", fg_color="black", border_width=2, border_color="white", font=my_font, command=changeNameYubikey3)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
			
		def changeNameYubikey3():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)

			# Output what has been done from getStarted
			my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="italic", underline=True, overstrike=False)
			Label2 = ctk.CTkLabel(my_Frame, text="Finished!", text_color="white", fg_color="black", font=my_font)
			Label2.place(relx=0.5, rely=0.35, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			Label23 = ctk.CTkLabel(my_Frame, text="You have sucessfully changed name credentials on the Yubikey.", text_color="white", fg_color="black", font=my_font)
			Label23.place(relx=0.5, rely=0.42, anchor="center")
			
			Button3 = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="black", border_width=2, border_color="white", font=my_font, command=self.setup_Yubikey)
			Button3.place(relx=0.5, rely=0.55, anchor="center")
			
		def newPINFIDOYubikey():
			# Reset the FIDO on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			command= 'ykman fido access change-pin --new-pin ' +  newFIDOPIN.get()
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.create_Yubikeymeny()
			
		def changePINFIDOYubikey():
			# Reset the FIDO on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'See terminal window for information.')
			
			command= 'ykman fido access change-pin --pin ' +  currentFIDOPIN.get() + ' --new-pin ' + changedFIDOPIN.get()
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.create_Yubikeymeny()
		
		Label1 = ctk.CTkLabel(my_Frame, text="Setup Yubikey.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="Make sure that your Yubikey 5C NFC is connected.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button1 = ctk.CTkButton(my_Frame, text="Reset OpenPGP", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=resetOpenPGPYubikey)
		Button1.place(relx=0.5, rely=0.25, anchor="center")
		
		Button2 = ctk.CTkButton(my_Frame, text="Reset FIDO", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=resetFIDOYubikey)
		Button2.place(relx=0.5, rely=0.3, anchor="center")
		
		Button3 = ctk.CTkButton(my_Frame, text="Change name", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changeNameYubikey)
		Button3.place(relx=0.5, rely=0.35, anchor="center")
		
		Button4 = ctk.CTkButton(my_Frame, text="Change PINs OpenPGP", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changePINsopenpgpYubikey)
		Button4.place(relx=0.5, rely=0.4, anchor="center")
		
		FIDOLabel = ctk.CTkLabel(my_Frame, text="New FIDO PIN (min 6 digits):", text_color="white", fg_color="black", font=my_font)
		FIDOLabel.place(relx=0.15, rely=0.45, anchor="w")
		
		NEWPINLabel = ctk.CTkLabel(my_Frame, text="New PIN:", text_color="white", fg_color="black", font=my_font)
		NEWPINLabel.place(relx=0.35, rely=0.5, anchor="e")
		
		newFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8,font=my_font)
		newFIDOPIN.place(relx=0.35, rely=0.5, anchor="w")
		
		newPINButton = ctk.CTkButton(my_Frame, text="New FIDO PIN", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=newPINFIDOYubikey)
		newPINButton.place(relx=0.55, rely=0.55, anchor="center")

		FIDOLabel_ = ctk.CTkLabel(my_Frame, text="Change FIDO PIN (min 6 digits, default PIN 123456):", text_color="white", fg_color="black", font=my_font)
		FIDOLabel_.place(relx=0.15, rely=0.6, anchor="w")
		
		FIDOLabel2 = ctk.CTkLabel(my_Frame, text="Current PIN:", text_color="white", fg_color="black", font=my_font)
		FIDOLabel2.place(relx=0.34, rely=0.65, anchor="e")
		
		currentFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		currentFIDOPIN.place(relx=0.35, rely=0.65, anchor="w")
		
		CHANGEDPINLabel = ctk.CTkLabel(my_Frame, text="New PIN:", text_color="white", fg_color="black", font=my_font)
		CHANGEDPINLabel.place(relx=0.34, rely=0.7, anchor="e")
		
		changedFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		changedFIDOPIN.place(relx=0.35, rely=0.7, anchor="w")
		
		tPINButton = ctk.CTkButton(my_Frame, text="Change FIDO PIN", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changePINFIDOYubikey)
		tPINButton.place(relx=0.55, rely=0.75, anchor="center")
		
		autPolicyCheckBox = ctk.CTkCheckBox(my_Frame, text="Set Touch policy for Auth on (uncheck sets the poilcy to Off):", variable=autPolicy, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		autPolicyCheckBox.place(relx=0.2, rely=0.8, anchor="w")
		
		autButton = ctk.CTkButton(my_Frame, text="Set policy", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=setautTouchYubikey)
		autButton.place(relx=0.7, rely=0.8, anchor="center")
		
		encPolicyCheckBox = ctk.CTkCheckBox(my_Frame, text="Set Touch policy for Encr on (uncheck sets the poilcy to Off):", variable=encPolicy, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		encPolicyCheckBox.place(relx=0.2, rely=0.84, anchor="w")
		encButton = ctk.CTkButton(my_Frame, text="Set policy", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=setencTouchYubikey)
		encButton.place(relx=0.7, rely=0.84, anchor="center")
		
		sigPolicyCheckBox = ctk.CTkCheckBox(my_Frame, text="Set Touch policy for Sign on (uncheck sets the poilcy to Off):", variable=sigPolicy, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		sigPolicyCheckBox.place(relx=0.2, rely=0.88, anchor="w")
		sigButton = ctk.CTkButton(my_Frame, text="Set policy", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=setencTouchYubikey)
		sigButton.place(relx=0.7, rely=0.88, anchor="center")
		
	def add_subkey_Yubikey(self):
		global clicked_privateSubKey
		global filepathdestinationfolder
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Times", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		def do_add_subkey_Yubikey():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In terminal that will open, type "toggle" and hit enter.\n2.Type "key 1" and "key 2" etc to toggle select/deselect subkey.\n        Selected subkey will be marked with "*"\n        Make sure only ONE subkey is selected before moving on to next step.\n3. Type "keytocard" to move the selected subkey to the Yubikey.\nIf the subkey is marked with \"usage: S\" then select \"(1) Signature key\".\nDeselect the \"Key 1\" by typing \"Key 1\" one more time.\n4. Repeat with all three subkeys.\n5. Type "save" and hit enter.\n6. Type "exit" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")
			
			clicked_privateKey = str(clicked.get())
			
			# Make a backup of the key before moving the subkeys			
			# Export the private key and write to file in /home/user1/secure/keys
			key_file_path = filepathdestinationfolder + '/secure/keys/privateKey' + clicked_privateKey + '.gpg'
			ascii_armored_private_key = gpg.export_keys(clicked_privateKey, True, expect_passphrase=False)
			f2 = open(key_file_path, 'w')
			f2.write(ascii_armored_private_key)
			f2.close()
			
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK"')
			time.sleep(3)
			
			goButton = ctk.CTkButton(my_Frame, text="Start", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=do_add_subkey_Yubikey_step2)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
		
		def do_add_subkey_Yubikey_step2():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label = ctk.CTkLabel(my_Frame, text='In terminal that will open, type "toggle" and hit enter.\n2.Type "key 1" and "key 2" etc to toggle select/deselect subkey.\n        Selected subkey will be marked with "*"\n        Make sure only ONE subkey is selected before moving on to next step.\n3. Type "keytocard" to move the selected subkey to the Yubikey.\nIf the subkey is marked with \"usage: S\" then select \"(1) Signature key\".\nDeselect the \"Key 1\" by typing \"Key 1\" one more time.\n4. Repeat with all three subkeys.\n5. Type "save" and hit enter.\n6. Type "exit" and hit enter.', text_color="white", fg_color="black", font=my_font)
			Label.place(relx=0.5, rely=0.2, anchor="center")

			clicked_privateKey = str(clicked.get())
			
			command= 'gpg --edit-key ' + clicked_privateKey
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			
			goButton = ctk.CTkButton(my_Frame, text="Finish", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=do_add_subkey_Yubikey_step3)
			goButton.place(relx=0.5, rely=0.8, anchor="center")	
			
		def do_add_subkey_Yubikey_step3():
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			clicked_privateKey = str(clicked.get())
			# Delete the secret key with snubbed (moved) subkeys from the local keychain
			key = gpg.delete_keys(clicked_privateKey, True, expect_passphrase=False)  #passphrase=USER_INP)
			file_path = filepathdestinationfolder + '/secure/keys/privateKey' + clicked_privateKey + '.gpg'
			# Import back the secret key from backup (with subkeys still intact)
			import_result = gpg.import_keys_file(file_path)
			gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
			
			self.create_Yubikeymeny()
			
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		if path_to_USB_secure == 'Secure USB folder is not available':
			Button8 = ctk.CTkButton(self, text="Log in", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			Button8.place(relx=0.5, rely=0.5, anchor="center")
			Label = ctk.CTkLabel(self, text="Or", text_color="white", font=("Helvetica", 18), fg_color="black")
			Label.place(relx=0.5, rely=0.55, anchor="center")
			Button7 = ctk.CTkButton(self, text="Create a new user account", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.new_secureUSB)
			Button7.place(relx=0.5, rely=0.6, anchor="center")
		else:	
			Label1 = ctk.CTkLabel(my_Frame, text="Add subkeys to a Yubikey. IMPORTANT. There should to be a backup available for the secret key before moving the subkeys.", text_color="brown", fg_color="black", font=my_font)
			Label1.place(relx=0.05, rely=0.07, anchor="w")
			
			Label2 = ctk.CTkLabel(my_Frame, text="Select from what key to move a subkey to the the Yubikey.", text_color="brown", fg_color="black", font=my_font)
			Label2.place(relx=0.05, rely=0.12, anchor="w")
			
			Label2 = ctk.CTkLabel(my_Frame, text="There are three subkeys to move to a Yubikey. Then are moved one at the time.", text_color="brown", fg_color="black", font=my_font)
			Label2.place(relx=0.05, rely=0.17, anchor="w")
			
			Label2 = ctk.CTkLabel(my_Frame, text="Toggle them on and off with command \"Key 1\" and \"Key 2\" etc and then \"Encryption\", \"Signature\" and \"Authentication\".", text_color="brown", fg_color="black", font=my_font)
			Label2.place(relx=0.05, rely=0.22, anchor="w")
			
			private_keys = gpg.list_keys(True)
					
			clicked = StringVar()
				
			List_fingerprints = []
				
			for i in private_keys:
				List_fingerprints.append(i['fingerprint'])
				
			clicked.set(List_fingerprints[0])
			
			my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
			
			Label1 = ctk.CTkLabel(my_Frame, text="Make sure your Yubikey is connected.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.38, anchor="center")	
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Label1 = ctk.CTkLabel(my_Frame, text="Select what key to move subkey\'s from:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.42, rely=0.48, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.43, rely=0.48, anchor="w")
			
			Button = ctk.CTkButton(my_Frame, text="Move subkey\'s to Yubikey", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=do_add_subkey_Yubikey)
			Button.place(relx=0.58, rely=0.54, anchor="w")
							
	def newGPG_Subkey(self):		
		global PersonalGPGKey
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_newGPGSubkey():
			global clicked_privateSubKey
			
			clicked_privateSubKey = str(clicked.get())
		
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			key = gpg.add_subkey(clicked_privateSubKey, algorithm='rsa4096', usage='sign', expire=combo.get())
			key = gpg.add_subkey(clicked_privateSubKey, algorithm='rsa4096', usage='encrypt', expire=combo.get())
			key = gpg.add_subkey(clicked_privateSubKey, algorithm='rsa4096', usage='auth', expire=combo.get())
			
			tk.messagebox.showinfo('Information', 'Subkey has been added.')
			self.get_GnuPGKeys()
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Create subkeys (\"Encryption\", \"Signature\" and \"Authentication\"- subkeys will all be created at once).", text_color="light green", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="The subkeys will be RSA-type and 4096 in length. Three years (\"3y\") is a good validity period for subkey\'s.", text_color="light green", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
			
		for nkey in private_keys:
				if nkey['fingerprint'] != PersonalGPGKey:
					List_fingerprints.append(nkey['fingerprint'])
		
		if List_fingerprints:	
			clicked.set(List_fingerprints[0])
			privatekeysavailable = True
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select a key to add subkey\'s to:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.4, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.41, rely=0.4, anchor="w")

			Label5 = ctk.CTkLabel(my_Frame, text="Select expiry date for subkey\'s:", font=my_font, text_color="white", fg_color="black")
			Label5.place(relx=0.4, rely=0.48, anchor="e")
			combo = ttk.Combobox(my_Frame, values = ["1y","3y"], justify='right')
			combo.current(1)
			combo.place(relx=0.58, rely=0.48, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Add subkeys", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=do_newGPGSubkey)
			Button2.place(relx=0.63, rely=0.54, anchor="w")
		else:
			Button = ctk.CTkButton(my_Frame, text="There are no private keys on the keychain. Create one now?", font=my_font, text_color="white", fg_color="green", border_width=2, border_color="white", command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.5, anchor="center")
			Button = ctk.CTkButton(my_Frame, text="Or, import one?", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.55, anchor="center")
			
	def create_Yubikeymeny(self):
		global Yubikey_button_color
		self.yubikey_Home()
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		CheckYubikeyButton = ctk.CTkButton(self, text="Yubikey config info", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.scan_Yubikey)
		CheckYubikeyButton.place(relx=0.1, rely=0.2, anchor="center")
		
		EditYubikeyButton = ctk.CTkButton(self, text="OpenPGP info", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.scan_Yubikey_openpgp)
		EditYubikeyButton.place(relx=0.25, rely=0.2, anchor="center")
		
		SetupYubikeyButton = ctk.CTkButton(self, text="Credentials", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.scan_Yubikey_credentials)
		SetupYubikeyButton.place(relx=0.4, rely=0.2, anchor="center")
		
		AddkeysYubikeyButton = ctk.CTkButton(self, text="Setup Yubikey", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.setup_Yubikey)
		AddkeysYubikeyButton.place(relx=0.55, rely=0.2, anchor="center")
		
		RemovekeysYubikeyButton = ctk.CTkButton(self, text="Transfer subkeys", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.add_subkey_Yubikey)
		RemovekeysYubikeyButton.place(relx=0.7, rely=0.2, anchor="center")
		
		ImportkeyButton = ctk.CTkButton(self, text="FIDO keys", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_FIDOmeny)
		ImportkeyButton.place(relx=0.85, rely=0.2, anchor="center")
	
	def yubikey_Home(self):	
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="brown"
		)
		
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		l1_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="white"
		)
		l1_Frame.place(relx=0.27, rely=0.35, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(l1_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		l2_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="white"
		)
		l2_Frame.place(relx=0.27, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(l2_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		l3_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="white"
		)
		l3_Frame.place(relx=0.27, rely=0.85, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(l3_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		r1_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="white"
		)
		r1_Frame.place(relx=0.73, rely=0.35, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(r1_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		r2_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="white"
		)
		r2_Frame.place(relx=0.73, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(r2_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		r3_Frame = ctk.CTkFrame(my_Frame, 
		width=450, 
		height=120,
		border_width=2,
		border_color="white"
		)
		r3_Frame.place(relx=0.73, rely=0.85, anchor="center")
		pathtobackg = "/home/user1/venvpython/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(446, 116))
		Label_backg = ctk.CTkLabel(r3_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
			
		my_font = ctk.CTkFont(family="Tahoma", size=34, weight="bold", slant="roman", underline=True, overstrike=False)
		welcomelabel = ctk.CTkLabel(my_Frame, text="Yubikey", text_color="white", fg_color="black", font=my_font)
		welcomelabel.place(relx=0.5, rely=0.1, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="italic", underline=False, overstrike=False)
		applabel = ctk.CTkLabel(my_Frame, text="YubiKey Manager (ykman) version: 4.0.0a1", text_color="white", fg_color="black", font=my_font)
		applabel.place(relx=0.5, rely=0.17, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		systemLabel = ctk.CTkLabel(my_Frame, text="------------------------------------------------------------------------------------------------ Overview ------------------------------------------------------------------------------------------------ ", text_color="white", fg_color="black", font=my_font)
		systemLabel.place(relx=0.5, rely=0.22, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The first left box
		Label_l1 = ctk.CTkLabel(l1_Frame, text="Yubikey config info", text_color="white", fg_color="black", font=my_font)
		Label_l1.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(l1_Frame, text="View Yubikey system information.\nInformation on the status of applications etc.", text_color="white", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The second left box
		Label5 = ctk.CTkLabel(l2_Frame,text="OpenPGP info", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(l2_Frame, text="View general information about OpenPGP. \nView information on touch policies etc.", text_color="white", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The third left box
		Label5 = ctk.CTkLabel(l3_Frame, text="Credentials", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(l3_Frame, text="View the information such as name and emails.\nView information about subkeys on the device.", text_color="white", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The first right box
		Label_l1 = ctk.CTkLabel(r1_Frame, text="Setup Yubikey", text_color="white", fg_color="black", font=my_font)
		Label_l1.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r1_Frame, text="Reset the  FIDO or OpenPGP on the Yubikey.\nChange settigns for touch functions etc.", text_color="white", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The second right box
		Label5 = ctk.CTkLabel(r2_Frame,text="Transfer subkeys", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r2_Frame, text="Move subkeys to the Yubikey.\nA Yubikey 5 NFC can hold subkeys for encryption, signing\nand authentication.\n", text_color="white", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The third rigth box
		Label5 = ctk.CTkLabel(r3_Frame, text="FIDO Keys", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r3_Frame, text="Store details about FIDO hardware keys such as:\n  - Name.\n  - Description.\n  - Services that key is associated with.", text_color="white", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
	def create_abouthelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="orange"
		)
		
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		try:
			f = open("/home/user1/venvpython/help/getstartedHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_gpghelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/venvpython/help/gpgHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_yubikeyhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/venvpython/help/yubikeyHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_secusbhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/venvpython/help/securearchiveHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
	
	def create_digitalIDhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/venvpython/help/digitalIDHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_boltcardhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		try:
			f = open("/home/user1/venvpython/help/boltcardHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
			
	def create_secusbtextbox(self):
		global path_to_USB_secure
		global filepathdestinationfolder
		global SecUSB_button_color
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if path_to_USB_secure == 'Secure USB folder is available':
			Label1 = ctk.CTkLabel(my_Frame, text="Passwords/accounts", text_color="white", font=("Helvetica", 24), fg_color="black")
			Label1.place(relx=0.25, rely=0.05, anchor="center")
			
			my_passwords = ctk.CTkTextbox(my_Frame, width=500, height=500, corner_radius=1, border_width=3, border_color="purple", border_spacing=10, fg_color="white", text_color="black", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="purple", scrollbar_button_hover_color="red")
		
			completeName = str(filepathdestinationfolder) + "/secure/passwords.txt"

			f1 = open(completeName, "r")
			my_passwordContent = f1.read()
			f1.close()
			my_passwords.insert('end', my_passwordContent)
			
			Button1 = ctk.CTkButton(my_Frame, text="Edit", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.create_editpasswordssecusbtextbox)
			Button1.place(relx=0.25, rely=0.92, anchor="center")
			my_passwords.configure(state="disabled")
			my_passwords.place(relx=0.48, rely=0.48, anchor="e")

		if path_to_USB_secure == 'Secure USB folder is available':
			Label2 = ctk.CTkLabel(my_Frame, text="Wallets", text_color="white", font=("Helvetica", 24), fg_color="black")
			Label2.place(relx=0.75, rely=0.05, anchor="center")
			
			my_wallets = ctk.CTkTextbox(my_Frame, width=500, height=500, corner_radius=1, border_width=3, border_color="purple", border_spacing=10, fg_color="white", text_color="black", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="purple", scrollbar_button_hover_color="red")

			completeName = str(filepathdestinationfolder) + "/secure/wallets/wallets.txt"

			f2 = open(completeName, "r")
			my_walletsContent = f2.read()
			f2.close()
			my_wallets.insert('end', my_walletsContent)
			
			Button1 = ctk.CTkButton(my_Frame, text="Edit", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.create_editwalletssecusbtextbox)
			Button1.place(relx=0.75, rely=0.92, anchor="center")
			my_wallets.configure(state="disabled")
			my_wallets.place(relx=0.52, rely=0.48, anchor="w")
		
	def create_editpasswordssecusbtextbox(self):
		global SecUSB_button_color
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		# Read the content of the password fle and place it in a Text field (to be able to "get" it after edited
		if path_to_USB_secure == 'Secure USB folder is available':
			completeName = str(filepathdestinationfolder) + "/secure/passwords.txt"
			f1 = open(completeName, "r")
			my_passwordContent = f1.read()
			f1.close()
			self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 15), wrap = 'word', undo = True)
			self.textBox.insert("1.0", my_passwordContent)
			self.textBox.place(relx=0.5, rely=0.48, anchor="center")
			self.textBox.focus_set()
			self.textBox.focus_force()
			theinput = self.textBox.get("1.0",'end-1c')
			Button22 = ctk.CTkButton(my_Frame, text="Save", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.do_edit_passwords)
			Button22.place(relx=0.5, rely=0.92, anchor="center")
		else:
			my_textbox.insert('end', 'You are not logged in. Passwords can\'t be displayed.')
		
		# Write over the password text file with the updated information that we "get" from the Text field
	def do_edit_passwords(self):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/passwords.txt"
		f2 = open(completeName, 'w')
		f2.write(self.textBox.get('1.0', 'end'))
		f2.close()
		tk.messagebox.showinfo('Information', 'Passwords updated.')
		self.create_secusbtextbox()
	
	def decrypt_message(self):
		global filepathdestinationfolder
		global path_to_USB_secure
		global SecUSB_button_color
		global theinput 
		global clicked_publicKey
		global PersonalGPGKey
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
				
		def save_to_archive():
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			outputdir = filedialog.askdirectory(initialdir='/home/user1/secure')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt\" will be added automatically):")
			theinput = self.textBox.get('1.0','end-1c')
			c = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
			c.write(str(theinput))
			c.close()
			messagebox.showinfo('Information', 'File \"' +USER_INP + '.txt\"' + ' has been saved to the Secure archive')
			self.create_SecUSBmeny()
		
		def save_to_USB():
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt\" will be added automatically):")
			theinput = self.textBox.get('1.0','end-1c')
			c = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
			c.write(str(theinput))
			c.close()
			messagebox.showinfo('Information', 'File \"' +USER_INP + '.txt\"' + ' has been saved to the USB-device')
			self.create_SecUSBmeny()
				
		def do_new_encrypt_message():
			global clicked_privateKey
			global clicked_publicKey

			clicked_privateKey = str(clicked.get())
			clicked_publicKey = str(clicked2.get())

			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			encrypted_data = gpg.encrypt(self.textBox.get('1.0', 'end'), clicked_publicKey, sign=clicked_privateKey) 

			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".gpg\" will be added automatically):")
			
			# Write the encrypted file to disk
			c = open(outputdir + '/' + USER_INP + '.gpg', 'w')
			c.write(str(encrypted_data))
			c.close()
			if encrypted_data.ok:
				messagebox.showinfo('Information', 'Message has been encrypted and stored at '+ outputdir)
			else:
				messagebox.showinfo('Information', encrypted_data.ok)	
			self.create_SecUSBmeny()
			
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		if path_to_USB_secure == 'Secure USB folder is available':
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			# Select file with message to decrypt
			messagebox.showinfo("Information", "Select file with message to decrypt.")
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			stream = open(filepathSourcefile, 'rb')
			
			try:
				data_ = gpg.decrypt_file(stream)

				if data_.ok:
					gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')

					private_keys = gpg.list_keys(True)
					public_keys = gpg.list_keys()
							
					clicked = StringVar()
					clicked2 = StringVar()
				
					List_fingerprints = []
					List_publicfingerprints = []
					
					privatekeysavailable = False
					publickeysavailable = False
					
					# Dont display the private key that is only intended for Offline device encryption/decryption
					for nkey in private_keys:
						if nkey['fingerprint'] != PersonalGPGKey:
							List_fingerprints.append(nkey['fingerprint'])
						
					if private_keys:
						clicked.set(List_fingerprints[0])
						privatekeysavailable = True
								
					for i2 in public_keys:
						List_publicfingerprints.append(i2['fingerprint'])
						
					if List_publicfingerprints:
						clicked2.set(List_publicfingerprints[0])
						publickeysavailable = True
					
					if not List_fingerprints:	
						Button = ctk.CTkButton(my_Frame, text="There are no public keys on the device.", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.newGPGFull_Key)
						Button.place(relx=0.5, rely=0.5, anchor="center")
					else:
						Label1 = ctk.CTkLabel(my_Frame, text="Select private key to sign message (FROM):", text_color="white", fg_color="black", font=my_font)
						Label1.place(relx=0.59, rely=0.82, anchor="e")

						drop1 = OptionMenu(my_Frame, clicked, *List_fingerprints)
						drop1.place(relx=0.6, rely=0.82, anchor="w")

						Label2 = ctk.CTkLabel(my_Frame, text="Select public key to encrypt message (TO):", text_color="white", fg_color="black", font=my_font)
						Label2.place(relx=0.59, rely=0.87, anchor="e")

						drop2 = OptionMenu(my_Frame, clicked2, *List_publicfingerprints)
						drop2.place(relx=0.6, rely=0.87, anchor="w")
						
						# Type content in textbox and select key before encrypting
						self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 16), wrap = 'word', undo = True)
						self.textBox.insert("1.0", data_.data)
						self.textBox.place(relx=0.5, rely=0.39, height=500, width=1050, anchor="center")
						theinput = self.textBox.get("1.0",'end-1c')
						self.textBox.focus_set()
						self.textBox.focus_force()
						
						Button11 = ctk.CTkButton(my_Frame, text="Save to Secure archive", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=save_to_archive)
						Button11.place(relx=0.56, rely=0.94, anchor="center")
						
						Button11 = ctk.CTkButton(my_Frame, text="Save to USB-device", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=save_to_USB)
						Button11.place(relx=0.73, rely=0.94, anchor="center")
	
						Button22 = ctk.CTkButton(my_Frame, text="Encrypt and Sign", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_new_encrypt_message)
						Button22.place(relx=0.88, rely=0.94, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", weight="bold", underline=False, overstrike=False)
						if data_.trust_level is not None and data_.trust_level >= data_.TRUST_FULLY:
							Labelv = ctk.CTkLabel(my_Frame, text="Key ID:" + data_.key_id, text_color="light green", fg_color="black", font=my_font)
							Labelv.place(relx=0.06, rely=0.82, anchor="w")
							Labelv2 = ctk.CTkLabel(my_Frame, text="Signature is good!", text_color="light green", fg_color="black", font=my_font)
							Labelv2.place(relx=0.06, rely=0.87, anchor="w")
						else:
							Labelv = ctk.CTkLabel(my_Frame, text="Signature could not be verified!", text_color="pink", fg_color="black", font=my_font)
							Labelv.place(relx=0.05, rely=0.87, anchor="w")
				else:
					messagebox.showinfo('Information', data_.status)
					self.create_SecUSBmeny()
			except FileNotFoundError:
					messagebox.showinfo("Information", "No settings file found.")
		else:
			notOKButton = ctk.CTkButton(my_Frame, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
				
	def encrypt_message(self):
		global filepathdestinationfolder
		global path_to_USB_secure
		global SecUSB_button_color
		global theinput 
		global clicked_privateKey
		global clicked_publicKey
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		def load_message_to_encrypt():
			messagebox.showinfo("Information", "Select the file to load text from.")
			filepathSourcefile = filedialog.askopenfilename(initialdir='/home/user1/secure')
			try:
				f = open(filepathSourcefile, 'r', encoding='utf-8')
				file_content = f.read()
				f.close()
				self.textBox.delete('1.0', END)
				self.textBox.insert('1.0', file_content)
				self.textBox.place(relx=0.5, rely=0.39, height=500, width=1050, anchor="center")
				theinput = self.textBox.get('1.0','end-1c')
				self.textBox.focus_set()
				self.textBox.focus_force()
			except OSError:
				messagebox.showinfo('Information', 'There was a problem reading the file.')
				
		def load_message_to_encrypt_USB():
			messagebox.showinfo("Information", "Select the file to load text from.")
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			try:
				f = open(filepathSourcefile, 'r', encoding='utf-8')
				file_content = f.read()
				f.close()
				self.textBox.delete('1.0', END)
				self.textBox.insert('1.0', file_content)
				self.textBox.place(relx=0.5, rely=0.39, height=500, width=1050, anchor="center")
				theinput = self.textBox.get('1.0','end-1c')
				self.textBox.focus_set()
				self.textBox.focus_force()
			except OSError:
				messagebox.showinfo('Information', 'There was a problem reading the file.')
				
		def do_encrypt_message():
			global clicked_privateKey
			global clicked_publicKey
			
			clicked_privateKey = str(clicked.get())
			clicked_publicKey = str(clicked2.get())

			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			encrypted_data = gpg.encrypt(self.textBox.get('1.0', 'end'), clicked_publicKey, sign=clicked_privateKey) 

			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".gpg\" will be added automatically):")
			
			# Write the encrypted file to disk
			c = open(outputdir + '/' + USER_INP + '.txt.gpg', 'w')
			c.write(str(encrypted_data))
			c.close()
			if encrypted_data.ok:
				messagebox.showinfo('Information', 'Message has been encrypted and stored at '+ outputdir)
			else:
				messagebox.showinfo('Information', encrypted_data.ok)	
			self.create_SecUSBmeny()
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		if path_to_USB_secure == 'Secure USB folder is available':
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
				
			private_keys = gpg.list_keys(True)
			public_keys = gpg.list_keys()
					
			clicked = StringVar()
			clicked2 = StringVar()
		
			List_fingerprints = []
			List_publicfingerprints = []
			
			privatekeysavailable = False
			publickeysavailable = False
			
			for nkey in private_keys:
				if nkey['fingerprint'] != PersonalGPGKey:
					List_fingerprints.append(nkey['fingerprint'])
				
			if private_keys:
				clicked.set(List_fingerprints[0])
				privatekeysavailable = True
						
			for i2 in public_keys:
				List_publicfingerprints.append(i2['fingerprint'])
				
			if List_publicfingerprints:
				clicked2.set(List_publicfingerprints[0])
				publickeysavailable = True
			
			if not List_fingerprints:	
				Button = ctk.CTkButton(my_Frame, text="There are no private keys on the device.", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.newGPGFull_Key)
				Button.place(relx=0.5, rely=0.5, anchor="center")
			else:
				clicked.set(List_fingerprints[0])
				
				Label1 = ctk.CTkLabel(my_Frame, text="Select private key to sign message (FROM):", text_color="white", fg_color="black", font=my_font)
				Label1.place(relx=0.59, rely=0.82, anchor="e")

				drop1 = OptionMenu(my_Frame, clicked, *List_fingerprints)
				drop1.place(relx=0.6, rely=0.82, anchor="w")
				
				Label2 = ctk.CTkLabel(my_Frame, text="Select key to encrypt message (TO):", text_color="white", fg_color="black", font=my_font)
				Label2.place(relx=0.59, rely=0.87, anchor="e")

				drop2 = OptionMenu(my_Frame, clicked2, *List_publicfingerprints)
				drop2.place(relx=0.6, rely=0.87, anchor="w")

				# Type content in textbox and select key before encrypting
				self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 16), wrap = 'word', undo = True)
				self.textBox.insert("1.0", '\nFrom: \nTo: \nDate: \n\nMessage: \n-------------------------------------------------------\n')
				self.textBox.place(relx=0.5, rely=0.39, height=500, width=1050, anchor="center")
				theinput = self.textBox.get("1.0",'end-1c')
				self.textBox.focus_set()
				self.textBox.focus_force()
				Button11 = ctk.CTkButton(my_Frame, text="Load from Secure archive", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=load_message_to_encrypt)
				Button11.place(relx=0.56, rely=0.94, anchor="center")	
				Button11 = ctk.CTkButton(my_Frame, text="Load from USB-file", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=load_message_to_encrypt_USB)
				Button11.place(relx=0.73, rely=0.94, anchor="center")	
				Button22 = ctk.CTkButton(my_Frame, text="Encrypt and Sign", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_encrypt_message)
				Button22.place(relx=0.88, rely=0.94, anchor="center")
		else:
			notOKButton = ctk.CTkButton(my_Frame, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_editwalletssecusbtextbox(self):
		global filepathdestinationfolder
		global path_to_USB_secure
		global SecUSB_button_color
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		# Read the content of the password fle and place it in a Text field (to be able to "get" it after edited
		if path_to_USB_secure == 'Secure USB folder is available':
			completeName = str(filepathdestinationfolder) + "/secure/wallets/wallets.txt"
			f1 = open(completeName, "r")
			my_passwordContent = f1.read()
			f1.close()
			self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 15), wrap = 'word', undo = True)
			self.textBox.insert("1.0", my_passwordContent)
			self.textBox.place(relx=0.5, rely=0.48, anchor="center")
			self.textBox.focus_set()
			self.textBox.focus_force()
			theinput = self.textBox.get("1.0",'end-1c')
			Button22 = ctk.CTkButton(my_Frame, text="Save", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.do_edit_wallets)
			Button22.place(relx=0.5, rely=0.92, anchor="center")
		else:
			my_textbox.insert('end', 'You are not logged in. Passwords can\'t be displayed.')
	
	def do_edit_wallets(self):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/wallets/wallets.txt"
		f2 = open(completeName, 'w')
		f2.write(self.textBox.get('1.0', 'end'))
		f2.close()
		tk.messagebox.showinfo('Information', 'Wallets file updated.')
		self.create_secusbtextbox()
		
	def importGPG_Key(self):
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_text = ctk.CTkTextbox(self, width=1200, height=650, corner_radius=1, border_width=3, border_color="green", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 15), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.6, anchor="center")
		messagebox.showinfo("Information", "Select the GPG-key you like to import from USB-device")
		filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
		
		import_result = gpg.import_keys_file(filepathSourcefile)
		
		gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
	
		self.get_GnuPGKeys()
	
	def importGPG_Key_from_archive(self):
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_text = ctk.CTkTextbox(self, width=1200, height=650, corner_radius=1, border_width=3, border_color="green", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 15), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.6, anchor="center")
		messagebox.showinfo("Information", "Select the GPG-key you like to import from the Secure archive")
		filepathSourcefile = filedialog.askopenfilename(initialdir='/home/user1/secure/keys')
		
		import_result = gpg.import_keys_file(filepathSourcefile)
		
		gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
	
		self.get_GnuPGKeys()
		
	def exportGPGmypublic(self):
		global clicked_publicKey
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_exportGPGmypublic():
			global clicked_publicKey
			
			clicked_publicKey = str(clicked.get())
		
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			ascii_armoured_public_key = gpg.export_keys(clicked_publicKey)
			tk.messagebox.showinfo('Information', 'Select where to save the file with the public key."')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			c = open(outputdir + '/publickey' + clicked_publicKey + '.gpg', 'w')
			c.write(ascii_armoured_public_key)
			c.close()
			tk.messagebox.showinfo('Information', 'Key has been exported.')
			self.create_GPGmeny()
		
		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Export a public key from the local keychain to a file.", text_color="light green", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="The public key can be shared to others so that they can encrypt emails, files or messages.", text_color="light green", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Only the corresponding private key are able to decrypt it.", text_color="light green", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.17, anchor="w")
		
		Label4 = ctk.CTkLabel(my_Frame, text="Public key\s can also be signed by others, see \"Web of trust\" online for more information", text_color="light green", fg_color="black", font=my_font)
		Label4.place(relx=0.05, rely=0.22, anchor="w")

		public_keys = gpg.list_keys()
				
		clicked = StringVar()
			
		List_publicfingerprints = []
		
		publickeysavailable = False
			
		for i in public_keys:
			List_publicfingerprints.append(i['fingerprint'])
		if List_publicfingerprints:	
			clicked.set(List_publicfingerprints[0])
			publickeysavailable = True

		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			
		if publickeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select the public key to export:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_publicfingerprints)
			drop.place(relx=0.35, rely=0.4, anchor="w")
			
			Button2 = ctk.CTkButton(my_Frame, text="Export key", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=do_exportGPGmypublic)
			Button2.place(relx=0.56, rely=0.5, anchor="w")
		else:
			print("No public key")
	
	def exportGPG(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_exportGPG():
			global clicked_privateKey
			
			clicked_privateKey = str(clicked.get())
			
			tk.messagebox.showinfo('Information', 'Select the directory where you want to save the signed and encrypted private keys file."')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			ascii_armoured_private_key = gpg.export_keys(clicked_privateKey, True, expect_passphrase=False) 
			c = open(outputdir + '/privatekey' + clicked_privateKey + '.gpg', 'w')
			c.write(ascii_armoured_private_key)
			c.close()
			tk.messagebox.showinfo('Information', 'Key has been exported.')
			self.create_GPGmeny()
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Export a private key from the local keychain to a file.", text_color="light green", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="The private key should be handled and stored in a safe manner.", text_color="light green", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="The private key's can be backed up in the secure archive where they will be encrypted.", text_color="light green", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.17, anchor="w")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
			
		for i in private_keys:
			List_fingerprints.append(i['fingerprint'])
		if List_fingerprints:	
			clicked.set(List_fingerprints[0])
			privatekeysavailable = True
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select key to export:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.35, rely=0.4, anchor="w")
			
			Button2 = ctk.CTkButton(my_Frame, text="Export key", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=do_exportGPG)
			Button2.place(relx=0.55, rely=0.5, anchor="w")
		else:
			print("No private key")
		
	def getStartedbackupGPG_Keys(self):
		global filepathdestinationfolder
		global path_to_USB_secure
		
		if path_to_USB_secure == 'Secure USB folder is available':
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			private_keys = gpg.list_keys(True)

			list_fingerprints = []
			
			for i in private_keys:
				list_fingerprints.append(i['fingerprint'])
				
			# Make filenames and paths.  
			privatekeyfilename = 'privateKey' + list_fingerprints[0] + ".gpg"
			communicationkeyfilename = 'privateKey' + list_fingerprints[1] + ".gpg"
			full_path_private = filepathdestinationfolder + "/" + privatekeyfilename
			full_path_communication = filepathdestinationfolder + "/secure/keys/" + communicationkeyfilename
			
			# Export the private key and write to file in /home/user1 and to /home/user1/ssecure/keys
			ascii_armored_private_key = gpg.export_keys(list_fingerprints[0], True, expect_passphrase=False) 
			f2 = open(full_path_private, 'w')
			f2.write(ascii_armored_private_key)
			f2.close()
			destPriv = filepathdestinationfolder + "/secure/keys/" + privatekeyfilename
			shutil.copy(full_path_private, destPriv)
			
			# Export the communication key and write to file in /secure/keys
			ascii_armored_communication_key = gpg.export_keys(list_fingerprints[1], True, expect_passphrase=False) 
			f2 = open(full_path_communication, 'w')
			f2.write(ascii_armored_communication_key)
			f2.close()

		else:
			tk.messagebox.showinfo('Information', 'No Secure file available."')
	
	def select_what_to_sign(self):
		global GPG_button_color
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button = ctk.CTkButton(my_Frame, text="Sign a document", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.sign_document)
		Button.place(relx=0.5, rely=0.15, anchor="center")
	
		Button2 = ctk.CTkButton(my_Frame, text="Sign/validate a public key on the local keychain", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.sign_key_on_keychain)
		Button2.place(relx=0.5, rely=0.25, anchor="center")
		
		Button3 = ctk.CTkButton(my_Frame, text="Sign/validate a public key on a USB-device *", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.sign_key_on_USB)
		Button3.place(relx=0.5, rely=0.35, anchor="center")
		
		Button4 = ctk.CTkButton(my_Frame, text="List signatures for a key on the local keychain", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.list_sigs_on_key)
		Button4.place(relx=0.5, rely=0.45, anchor="center")
		
		Label1 = ctk.CTkLabel(my_Frame, text="* The public key will be imported to the local keychain (and assign ULTIMATE trust) then signed and exported to the USB-device again.", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.5, rely=0.85, anchor="center")
	
	def list_sigs_on_key(self):
		global GPG_button_color
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/venvpython/images/GnuPGbackground.JPG"
		
		top_Frame = ctk.CTkFrame(my_Frame, 
		width=1200, 
		height=150,
		border_width=2,
		border_color="green"
		)
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1196, 146))
		Label_backg = ctk.CTkLabel(top_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		top_Frame.place(x=0, y=0, anchor="nw")
		top_Frame.focus_set()
		top_Frame.focus_force()
		
		bottom_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=1174, 
		height=484,
		orientation="vertical",
		border_width=2,
		border_color="green",
		fg_color="gray1"
		)
		
		backg2 = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1196, 496))
		Label_backg2 = ctk.CTkLabel(bottom_Frame, image=backg2, text = "")
		Label_backg2.place(x=2, y=2)
		bottom_Frame.place(x=0, y=150, anchor="nw")	
		bottom_Frame.focus_set()
		bottom_Frame.focus_force()
		
		def do_list_sigs_on_key():
			global clicked_publicKey
			
			bottom_Frame = ctk.CTkScrollableFrame(my_Frame, 
			width=1174, 
			height=484,
			orientation="vertical",
			border_width=2,
			border_color="green",
			fg_color="gray1"
			)
			
			backg2 = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1196, 496))
			Label_backg2 = ctk.CTkLabel(bottom_Frame, image=backg2, text = "")
			Label_backg2.place(x=2, y=2)
			bottom_Frame.place(x=0, y=150, anchor="nw")	
			bottom_Frame.focus_set()
			bottom_Frame.focus_force()
			
			clicked_publicKey = str(clicked.get())
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			
			# Get sigs for the selected key
			public_keys = gpg.list_keys(sigs=True)

			# Loop through and display sigs
			if public_keys:
				for i in public_keys:
					if i['fingerprint'] == clicked_publicKey and i['sigs']: 
						my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
				
						tuple_of_sigs_in_key = i['sigs']

						for ii in tuple_of_sigs_in_key:
							if ii:
								keyID = ii[0]
								user_id = ii[1]
								signature_class = ii[2]

								Label = ctk.CTkLabel(bottom_Frame, text= keyID + ' ' +  user_id + ' ' + signature_class, fg_color="black", font=my_font)
								Label.pack(padx=10, pady=1, side= TOP, anchor="w")

		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		public_keys = gpg.list_keys()
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		pubickeysavailable = False
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)

		# List the private keys that can be used for signing			
		for i in public_keys:
			List_fingerprints.append(i['fingerprint'])
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No public keys."')
		else:
			clicked.set(List_fingerprints[0])
			pubickeysavailable = True
				
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if pubickeysavailable == True:			
			Label5 = ctk.CTkLabel(top_Frame, text="Select public key to list signatures for:", text_color="white", fg_color="black", font=my_font)
			Label5.place(relx=0.4, rely=0.3, anchor="e")
			drop = OptionMenu(top_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.41, rely=0.3, anchor="w")
			
			Button2 = ctk.CTkButton(top_Frame, text="List signatures", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_list_sigs_on_key)
			Button2.place(relx=0.63, rely=0.6, anchor="w")
		else:
			Button = ctk.CTkButton(top_Frame, text="There are no public keys on the keychain.", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.05, anchor="center")
			
	def sign_key_on_USB(self):
		global GPG_button_color
		def do_sign_key_on_USB():
			global clicked_privateSubKey
			
			clicked_privateKey = str(clicked.get())
			
			# The smaller frame
			my_Frame = ctk.CTkFrame(self, 
			width=1200, 
			height=650,
			border_width=4,
			border_color="blue"
			)
			my_Frame.place(relx=0.5, rely=0.6, anchor="center")
			
			pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
			if path_to_USB_secure == 'Secure USB folder is available':			
				completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
				try:
					with open(completeName, 'r') as file:
						csvfile = csv.reader(file)
						for lines in csvfile:
							if lines:	
								users_theme = lines[1]
								users_colors = lines[2]
				except FileNotFoundError:
					messagebox.showinfo("Information", "No settings file found.")
				if users_theme == 'Winter':
					pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
				if users_theme == 'Summer':
					pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
				if users_theme == 'Light':
					pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
				if users_theme == 'Dark':
					pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			tk.messagebox.showinfo('Information', 'Insert the USB-device."')
			time.sleep(4)
			tk.messagebox.showinfo('Information', 'Select the file with the public key."')
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Select the folder where you want to save the signed and encrypted public key after signing."')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			# Scan the key in the file to get the fingerprint
			keys = gpg.scan_keys(filepathSourcefile)
			key_fingerprint = ''
			key_fingerprint = str(keys.fingerprints[0])
			
			# Import the key from file to the local keychain and assign trust
			import_result = gpg.import_keys_file(filepathSourcefile)
			gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
			
			# Sign the key on local keychain by passing argument fingerprint
			command= 'gpg --local-user ' + clicked_privateKey + ' --quick-sign-key ' + key_fingerprint
			os.system(command) 
			
			# Define the output file
			filesname = outputdir + "/signed_" + key_fingerprint + '.gpg'
			
			# Export the signed public key and sign/encrypt with selected private key
			command= 'gpg -a ' + key_fingerprint + ' | gpg -ase -r ' + key_fingerprint + ' -u ' + clicked_privateKey + ' > ' + filesname
			os.system(command) 
			
			tk.messagebox.showinfo('Information', 'Please check that the key on the public key was signed and exported correctly to selected folder. NOTE: The public key was also left on the local keychain.')
			self.create_GPGmeny()
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Signing a public key on a USB-device using one of the private keys on the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.25, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=15, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Select (1). What private key to sign with. (2). The file with the public key on the USB-device. And (3) The folder where to place the signed key.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.30, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="(The output will be a file with the signed public key (encrypted and signed with your private key).)", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.35, anchor="center")
		
		Label4 = ctk.CTkLabel(my_Frame, text="(That way the owner of the signed public key will know that it was really you that sent it.)", text_color="white", fg_color="black", font=my_font)
		Label4.place(relx=0.5, rely=0.40, anchor="center")
		
		Label5 = ctk.CTkLabel(my_Frame, text="(Remember! If the master key is only with cerification capability then you need to select the signing subkey)", text_color="white", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.45, anchor="center")
		
		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
		
		# List the private keys that can be used for signing			
		for i in private_keys:
			List_fingerprints.append(i['fingerprint'])
		if private_keys:	 
			for i in private_keys:
				if i['subkeys']: 
					listoflistindict = i['subkeys']
					dictofsubkeyinfo = i['subkey_info']
					for ii in listoflistindict:
						if ii:
							subkinfo = ii[0]
							capacity = dictofsubkeyinfo[subkinfo]['cap']
							if capacity == 's':
								List_fingerprints.append(subkinfo)	
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No private keys."')
		
		
		else:
			clicked.set(List_fingerprints[0])
			privatekeysavailable = True
				
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if privatekeysavailable == True:			
			Label5 = ctk.CTkLabel(my_Frame, text="Select a private key to sign with:", text_color="white", fg_color="black", font=my_font)
			Label5.place(relx=0.4, rely=0.55, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.41, rely=0.55, anchor="w")
			
			Button2 = ctk.CTkButton(my_Frame, text="Sign the public key", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_sign_key_on_USB)
			Button2.place(relx=0.61, rely=0.61, anchor="w")
		else:
			Button = ctk.CTkButton(my_Frame, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.65, anchor="center")
			Button = ctk.CTkButton(my_Frame, text="Or, import one?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.7, anchor="center")	
						
	def sign_key_on_keychain(self):
		global GPG_button_color
		def do_sign_key_on_keychain():
			global clicked_privateKey
			global clicked_publicKey
			
			clicked_privateKey = str(clicked.get())
			clicked_publicKey = str(clicked2.get())
			
			# The smaller frame
			my_Frame = ctk.CTkFrame(self, 
			width=1200, 
			height=650,
			border_width=4,
			border_color="blue"
			)
			my_Frame.place(relx=0.5, rely=0.6, anchor="center")
			
			pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
			if path_to_USB_secure == 'Secure USB folder is available':			
				completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
				try:
					with open(completeName, 'r') as file:
						csvfile = csv.reader(file)
						for lines in csvfile:
							if lines:	
								users_theme = lines[1]
								users_colors = lines[2]
				except FileNotFoundError:
					messagebox.showinfo("Information", "No settings file found.")
				if users_theme == 'Winter':
					pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
				if users_theme == 'Summer':
					pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
				if users_theme == 'Light':
					pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
				if users_theme == 'Dark':
					pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			# Sign the public key and pass argument fingerprint
			command= 'gpg --local-user ' + clicked_privateKey + ' --quick-sign-key ' + clicked_publicKey
			
			os.system(command) 
			
			tk.messagebox.showinfo('Information', 'Please check that the key on the local keychain was signed.')
			self.create_GPGmeny()
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Signing a public key on the local keychain using one of the private keys.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.25, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=15, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="(1). Select the private key to sign with. (2). Select the public key that you would like to sign.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.30, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="(Remember! If a master key is only with cerification capability, then you need to select that keys signing subkey instead)", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.35, anchor="center")

		private_keys = gpg.list_keys(True)
		public_keys = gpg.list_keys()
				
		clicked = StringVar()
		clicked2 = StringVar()
			
		List_fingerprints = []
		List_fingerprints2 = []
		
		privatekeysavailable = False

		# List the private keys that can be used for signing			
		for nkey in private_keys:
			List_fingerprints.append(nkey['fingerprint'])
			
		if private_keys:	 
			for i in private_keys:
				if i['subkeys']: 
					listoflistindict = i['subkeys']
					dictofsubkeyinfo = i['subkey_info']
					for ii in listoflistindict:
						if ii:
							subkinfo = ii[0]
							capacity = dictofsubkeyinfo[subkinfo]['cap']
							if capacity == 's':
								List_fingerprints.append(subkinfo)	
	
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No private keys."')
		else:
			clicked.set(List_fingerprints[0])
			privatekeysavailable = True
		for i2 in public_keys:
			List_fingerprints2.append(i2['fingerprint'])
		if not List_fingerprints2:	
			tk.messagebox.showinfo('Information', 'No public keys."')
		else:
			clicked2.set(List_fingerprints2[0])
				
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if privatekeysavailable == True:
			Label5 = ctk.CTkLabel(my_Frame, text="Select a private key to sign with:", text_color="white", fg_color="black", font=my_font)
			Label5.place(relx=0.4, rely=0.5, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
			drop.place(relx=0.41, rely=0.5, anchor="w")
			Label6 = ctk.CTkLabel(my_Frame, text="Select the public key you intend to sign:", text_color="white", fg_color="black", font=my_font)
			Label6.place(relx=0.4, rely=0.55, anchor="e")
			drop2 = OptionMenu(my_Frame, clicked2, *List_fingerprints2)
			drop2.place(relx=0.41, rely=0.55, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Sign the public key", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_sign_key_on_keychain)
			Button2.place(relx=0.6, rely=0.61, anchor="w")
		else:
			Button = ctk.CTkButton(my_Frame, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.65, anchor="center")
			Button = ctk.CTkButton(my_Frame, text="Or, import one?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.7, anchor="center")	
		
	def sign_document(self):
		global clicked_privateSubKey
		global outputdir
		global GPG_button_color
		
		def do_sign():
			global clicked_privateSubKey
			global outputdir
			
			clicked_privateSubKey = str(clicked.get())
	
			my_text = ctk.CTkTextbox(self, width=1200, height=650, corner_radius=1, border_width=3, border_color="green", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 15), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
			my_text.insert('end', " ")
			my_text.configure(state="disabled")
			my_text.place(relx=0.5, rely=0.6, anchor="center")
		
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			filesname = filepathSourcefile.split("/")
			
			with open(filepathSourcefile, 'rb') as f: 
					try:
						data_ = gpg.sign_file(f, keyid=clicked_privateSubKey, detach=True)
					except ValueError as ve:
						tk.messagebox.showinfo('Information', 'Wrong password.')
			f2 = open(outputdir + "/" + str(filesname[-1]) + '.sig', 'w')
			f2.write(str(data_))
			f2.close()
			
			tk.messagebox.showinfo('Information', 'Document has been signed.')
			self.create_GPGmeny()
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(self, text="Signing a document using one of your private keys.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.4, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=15, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(self, text="Select what document to sign, where to place the document after signing and what master key to sign with.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.44, anchor="center")
		
		Label2 = ctk.CTkLabel(self, text="(The output will be a detached signature (.sig) in the folder that you selected.)", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.48, anchor="center")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
		
		# List the private keys that can be used for signing			
		for i in private_keys:
			List_fingerprints.append(i['fingerprint'])
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No private keys."')
		else:
			clicked.set(List_fingerprints[0])
			privatekeysavailable = True
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if privatekeysavailable == True:
			# Ask for the path to the file to be signed and for the directory where the signature should go
			tk.messagebox.showinfo('Information', 'Select the document you want to sign."')
			time.sleep(3)
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			
			tk.messagebox.showinfo('Information', 'Select the folder where you want to save the detached signature (file) after signing."')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			Label1 = ctk.CTkLabel(self, text="Select a private key to sign with:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.4, rely=0.55, anchor="e")
			drop = OptionMenu(self, clicked, *List_fingerprints)
			drop.place(relx=0.41, rely=0.55, anchor="w")
			Button2 = ctk.CTkButton(self, text="Sign document", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_sign)
			Button2.place(relx=0.56, rely=0.61, anchor="w")
		else:
			Button = ctk.CTkButton(self, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.53, anchor="center")
			Button = ctk.CTkButton(self, text="Or, import one?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.57, anchor="center")	
						
	def decrypt_SecUSB(self):
		global path_to_USB_secure
		global filepathdestinationfolder
		global PersonalGPGKey
		global clicked_privateKey
		global timeSecUSBLastModified
		global SecUSB_button_color
		
		private_keys = []
		
		def store_selected():
			global path_to_USB_secure
			global PersonalGPGKey
			global filepathdestinationfolder
			global timeSecUSBLastModified
			clicked_privateKey = str(clicked.get())
			PersonalGPGKey = clicked_privateKey

			full_path = str(filepathdestinationfolder + "/" + clicked_privateKey + "securefolder.tar.gz.gpg")
			
			full_path = filepathdestinationfolder + '/' + clicked_privateKey + 'securefolder.tar.gz.gpg'
			if os.path.isfile(full_path):
				# Use PersonalGPGKey
				try:
					out_path = filepathdestinationfolder + "/" + clicked_privateKey + 'securefolder.tar.gz'
					data_ = gpg.decrypt_file(full_path, output=out_path)
					if data_.ok:
						tar = tarfile.open(filepathdestinationfolder + "/" + clicked_privateKey + 'securefolder.tar.gz') 
						tar.extractall(filepathdestinationfolder + "/" + 'secure')
						tar.close()		
						os.remove(filepathdestinationfolder + "/" + clicked_privateKey + "securefolder.tar.gz")
						my_Frame.place(relx=0.5, rely=0.6, anchor="center")
						Labelinf = ctk.CTkLabel(my_Frame, text="You have been logged in.", text_color="white", fg_color="black", font=my_font)
						Labelinf.place(relx=0.5, rely=0.4, anchor="center") 
						Labelinf2 = ctk.CTkLabel(my_Frame, text="Encryption: Standard: RFC 4880.", text_color="white", fg_color="black", font=my_font)
						Labelinf2.place(relx=0.5, rely=0.45, anchor="center") 
						Labelinf3 = ctk.CTkLabel(my_Frame, text="Key strenght: 4096 bits.", text_color="white", fg_color="black", font=my_font)
						Labelinf3.place(relx=0.5, rely=0.5, anchor="center") 
						time.sleep(1)
						path_to_USB_secure = 'Secure USB folder is available'
						
						timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
						self.create_meny()
					if data_.ok == False:
						messagebox.showinfo("Information", data_.status)
				except FileNotFoundError:
					messagebox.showinfo("Information", "No account found.")
			else:
				messagebox.showinfo("Information", "There is no account for the selected secret key.")			
				
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="purple"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if path_to_USB_secure == 'Secure USB folder is available':
			# Display the keys <for information> if the secure folder has already been decrypted
			Label1 = ctk.CTkLabel(my_Frame, text="You are already logged in.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.44, rely=0.4, anchor="e")
			Label11 = ctk.CTkLabel(my_Frame, text=PersonalGPGKey, text_color="white", fg_color="black", font=my_font)
			Label11.place(relx=0.45, rely=0.4, anchor="w")
			
		else:
			privatekeysavailable = False
			
			private_keys = gpg.list_keys(True)
			
			clicked = StringVar()
				
			List_fingerprints = []
			
			for i in private_keys:
				List_fingerprints.append(i['fingerprint'])
			
			if not List_fingerprints:	
				Button = ctk.CTkButton(my_Frame, text="There are no user accounts on the device. Create one now?", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font,command=self.create_getStartedmeny)
				Button.place(relx=0.5, rely=0.5, anchor="center")
			else:
				clicked.set(List_fingerprints[0])
				
				Label2 = ctk.CTkLabel(my_Frame, text="Select key for login *:", text_color="white", fg_color="black", font=my_font)
				Label2.place(relx=0.4, rely=0.4, anchor="e")

				drop = OptionMenu(my_Frame, clicked, *List_fingerprints)
				drop.place(relx=0.41, rely=0.4, anchor="w")

				Button = ctk.CTkButton(my_Frame, text="Log in", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=store_selected)
				Button.place(relx=0.63, rely=0.49, anchor="w")
				my_font = ctk.CTkFont(family="Arial", size=14, weight="bold", slant="roman", underline=False, overstrike=False)
		
				Labelinf1 = ctk.CTkLabel(my_Frame, text="* Key is used for decrypting the offline device.", text_color="white", fg_color="black", font=my_font)
				Labelinf1.place(relx=0.5, rely=0.8, anchor="center")
	
	def encrypt_SecUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="purple"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			global timeSecUSBLastModified
			full_path = str(filepathdestinationfolder) + "/secure/"
		
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			# Encrypt the tarfile and sefely remove the unencrypted tarfile (srm)
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)

			# Write the encrypted file to disk
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			Labelinf = ctk.CTkLabel(my_Frame, text="You are being logged out.", text_color="white", fg_color="black", font=my_font)
			Labelinf.place(relx=0.5, rely=0.4, anchor="center") 
			Labelinf2 = ctk.CTkLabel(my_Frame, text="The device is being encrypted. Please wait..", text_color="white", fg_color="black", font=my_font)
			Labelinf2.place(relx=0.5, rely=0.45, anchor="center") 
			Labelinf3 = ctk.CTkLabel(my_Frame, text="(Encryption: Standard: RFC 4880)", text_color="white", fg_color="black", font=my_font)
			Labelinf3.place(relx=0.5, rely=0.5, anchor="center") 

			full_path = str(filepathdestinationfolder) + "/secure"
			cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  full_path
			os.system(cmd)

			path_to_USB_secure = 'Secure USB folder is not available'
			timeSecUSBLastModified = '<Unknown>'
			self.set_colors('Varied')
			self.create_meny()
			
		else:
			Labelinf = ctk.CTkLabel(my_Frame, text="You are not logged in.", text_color="white", fg_color="black", font=my_font)
			Labelinf.place(relx=0.5, rely=0.4, anchor="center") 
			GPGButton = ctk.CTkButton(my_Frame, text="Home", text_color="white", font=my_font, border_width=2, border_color="white", fg_color=SecUSB_button_color, command=self.create_meny)
			GPGButton.place(relx=0.5, rely=0.5, anchor="center")
					
	def new_secureUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		def tPassphrase():
			if Secret_passphrasePrivateEntry.cget('show') == '':
				Secret_passphrasePrivateEntry.configure(show='*')
			else:
				Secret_passphrasePrivateEntry.configure(show='')
				
		def do_new_secureUSB():
			global path_to_USB_secure
			global PersonalGPGKey
			global filepathdestinationfolder
			global timeSecUSBLastModified
	
			if path_to_USB_secure == 'Secure USB folder is available':
				Labelinf = ctk.CTkLabel(my_Frame, text="You are already logged in.", text_color="white", fg_color="black", font=my_font)
				Labelinf.place(relx=0.5, rely=0.4, anchor="center") 
				GPGButton = ctk.CTkButton(my_Frame, text="Home", text_color="white", font=my_font, border_width=2, border_color="white", fg_color=SecUSB_button_color, command=self.create_meny)
				GPGButton.place(relx=0.5, rely=0.5, anchor="center")
			else:
				gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
				
				# Encrypt the SecUSB file and shredd the unencrypted. Send back any error message
				my_text = ctk.CTkTextbox(self, width=1200, height=650, corner_radius=1, border_width=3, border_color="purple", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 15), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
				my_text.configure(state="disabled")
				my_text.place(relx=0.5, rely=0.6, anchor="center")
				
				# Create a GPG master key for personal use, namePrivateEntry emailPrivateEntry Secret_passphrasePrivateEntry
				input_data_priv = gpg.gen_key_input(key_type='rsa', name_real=namePrivateEntry.get(), expire_date='0', key_length='4096', name_email=emailPrivateEntry.get(), passphrase=Secret_passphrasePrivateEntry.get())
				privatekey = gpg.gen_key(input_data_priv)
				
				privatekeyfilename = 'privateKey' + privatekey.fingerprint + ".gpg"
				full_path_private = filepathdestinationfolder + "/" + privatekeyfilename
			
				path_to_USB_secure = 'Secure USB folder is available'
				PersonalGPGKey = privatekey.fingerprint
				
				# Create a Secure folder
				full_path = str(filepathdestinationfolder) + "/secure/"
				full_path_wallets = str(filepathdestinationfolder) + "/secure/wallets/"
				full_path_keys = str(filepathdestinationfolder) + "/secure/keys/"
				full_path_paperwallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/"
				full_path_settings_file = str(filepathdestinationfolder) + "/secure/settings.csv"
				full_path_paperwallets_file = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
				full_path_boltcards = str(filepathdestinationfolder) + "/secure/boltcards/"
				full_path_boltcards_file = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
				full_path_FIDOKeys = str(filepathdestinationfolder) + "/secure/FIDO/"
				full_path_FIDOKeys_file = str(filepathdestinationfolder) + "/secure/FIDO/FIDOKeys.csv"
				full_path_IDs = str(filepathdestinationfolder) + "/secure/ID/"
				full_path_IDs_file = str(filepathdestinationfolder) + "/secure/ID/IDs.csv"
				
				os.makedirs(os.path.dirname(full_path))
				os.makedirs(os.path.dirname(full_path_wallets))
				os.makedirs(os.path.dirname(full_path_keys))
				os.makedirs(os.path.dirname(full_path_paperwallets))
				os.makedirs(os.path.dirname(full_path_boltcards))
				os.makedirs(os.path.dirname(full_path_FIDOKeys))
				os.makedirs(os.path.dirname(full_path_IDs))
				
				c = open(full_path + "passwords.txt", 'w')
				c.write(str("Passwords\n___________________________________\n\nYubikey\n\n   FIDO PIN:  \n\n   OpenPGP Admin PIN:  \n\n   OpenPGP PIN:  \n\n   Comment:  \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n"))
				c.close()
				c = open(full_path_wallets + "wallets.txt", 'w')
				c.write(str("Wallets\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n"))
				c.close()
				with open(full_path_settings_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['Username', 'Theme', 'Colors']
				with open(full_path_paperwallets_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['Name', 'Datecreated', 'Pubkey', 'wif', 'mnemonic', 'amount']
				with open(full_path_boltcards_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['name', 'description', 'datecreated', 'LNURLaddress', 'resetcode', 'programmingcode', 'withdrawallimit', 'dailywithdrawallimit', 'LNHublink', 'LNHubuser', 'LNHubuserpassword']	
				with open(full_path_FIDOKeys_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['name', 'description', 'services']	
				with open(full_path_IDs_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['type', 'fingerprint', 'name', 'lastname', 'address', 'address2', 'birthdate', 'sex', 'issuedate']
			
				# Export the private key and write to file in /home/user1 and to /home/user1/secure/keys
				ascii_armored_private_key = gpg.export_keys(privatekey.fingerprint, True, expect_passphrase=False)
				f2 = open(full_path_private, 'w')
				f2.write(ascii_armored_private_key)
				f2.close()

				destPriv = filepathdestinationfolder + "/secure/keys/" + privatekeyfilename
				shutil.copy(full_path_private, destPriv)
			
				# Make initial settings in settings file
				completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
				with open(completeName, 'w') as result:
					csvwriter = csv.writer(result)
					new_settings = [
									userNameEntry.get(),
									'winter',
									'Varied']

					csvwriter.writerow(new_settings)	

				iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/venvpython/images/iconopen.png"), dark_image=Image.open("/home/user1/venvpython/images/iconopen.png"), size=(30, 30))
				openlock_Label = ctk.CTkLabel(self, text="", image=iconopen_image)
				openlock_Label.place(relx=0.02, rely=0.94, anchor="w")
				
				self.create_meny()
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)

		my_font = ctk.CTkFont(family="Tahoma", size=34, weight="bold", slant="roman", underline=True, overstrike=False)
	
		Label = ctk.CTkLabel(my_Frame, text="Please provide your data:", text_color="white", fg_color="black", font=my_font)
		Label.place(relx=0.24, rely=0.2, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		# Data for the user account
		userName = ctk.CTkLabel(my_Frame, text="User name for account:", text_color="white", fg_color="black", font=my_font)
		userName.place(relx=0.34, rely=0.32, anchor="e")
		userNameEntry = ctk.CTkEntry(my_Frame, placeholder_text="Bobby", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		userNameEntry.place(relx=0.35, rely=0.32, anchor="w")
		
		namePrivate = ctk.CTkLabel(my_Frame, text="Full name:", text_color="white", fg_color="black", font=my_font)
		namePrivate.place(relx=0.34, rely=0.37, anchor="e")
		namePrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text="Bob Smith", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		namePrivateEntry.place(relx=0.35, rely=0.37, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="Email:", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.34, rely=0.42, anchor="e")
		emailPrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text="bob.smith@cyb.org", width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		emailPrivateEntry.place(relx=0.35, rely=0.42, anchor="w")
		
		LabelPassphrasePrivate = ctk.CTkLabel(my_Frame, text="Secret passphrase:", text_color="white", fg_color="black", font=my_font)
		LabelPassphrasePrivate.place(relx=0.34, rely=0.47, anchor="e")
		Secret_passphrasePrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text="*****************", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		Secret_passphrasePrivateEntry.place(relx=0.35, rely=0.47, anchor="w")
		tButton = ctk.CTkButton(my_Frame, text="Show/hide passphrase", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=tPassphrase)
		tButton.place(relx=0.7, rely=0.47, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button = ctk.CTkButton(my_Frame, text="Create new account *", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_new_secureUSB)
		Button.place(relx=0.49, rely=0.53, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		LLabel = ctk.CTkLabel(my_Frame, text="* This can take a while.. Move mouse around to create randomness...\nFollow all the instructions for the rest of the setup.", text_color="white", fg_color="black", font=my_font)
		LLabel.place(relx=0.5, rely=0.73, anchor="center")
	
	def getStartedencrypt_SecUSBs(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		if path_to_USB_secure == 'Secure USB folder is available':
			
			full_path = str(filepathdestinationfolder) + "/secure/"
		
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			# Encrypt the tarfile and remove the unencrypted tarfile
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)
			# Write the encrypted file to the offline device /home/user1-folder
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			
			full_path = str(filepathdestinationfolder) + '/secure'
			cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  full_path
			os.system(cmd)

			path_to_USB_secure = 'Secure USB folder is not available'
			timeSecUSBLastModified = '<Unknown>'
			
			# Copy the exported private key to the second USB
			messagebox.showinfo("Information", "Insert a USB-device (for making a backup) and select it.")
			localfilepathdestinationfolder = filedialog.askdirectory(initialdir='/media/user1/')
			keyfilename = 'privateKey' + PersonalGPGKey + ".gpg"
			completeName = os.path.join(filepathdestinationfolder, keyfilename)
			shutil.copy(completeName, localfilepathdestinationfolder)
			
			# Write the encrypted file to second USB-stick
			compressedoutfile = open(localfilepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			messagebox.showinfo("Information", "Backup to USB-device successfull. Please remove USB-device.")
		else:
			print("Secure folder not available")
			
	def copy_SecUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_copy_SecUSB():
			global filepathdestinationfolder
			global PersonalGPGKey
			failedExport = 0
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			if path_to_USB_secure == 'Secure USB folder is available':
				full_path = str(filepathdestinationfolder) + "/secure/"
				messagebox.showinfo("Information", "Insert USB-device and then double click to select it.")
				time.sleep(4)
				
				USBdevice = filedialog.askdirectory(initialdir='/media/user1/')
				if USBdevice == '/home' or USBdevice == '/home/user1' or USBdevice == '/home/user1/secure' or USBdevice == '/media' or USBdevice == '/media/user1':
					messagebox.showinfo("Alert!", "This is not an external USB-device. Are you sure you double clicked on the USB-device?")
					self.do_copy_SecUSB()
				else:
					Label_backg.place(x=0, y=0)
					Label22 = ctk.CTkLabel(my_Frame, text="Working on it....", text_color="white", fg_color="black", font=my_font)
					Label22.place(relx=0.5, rely=0.42, anchor="center")
					time.sleep(2)
					full_path = str(filepathdestinationfolder) + "/secure/"
					
					compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
					gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
					# Encrypt the tarfile and sefely remove the unencrypted tarfile (srm)
					encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
					cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
					os.system(cmd)

					# Write the encrypted file to the USB-device 
					archive_to_path = USBdevice + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg'
					compressedoutfile = open(archive_to_path, 'w')
					compressedoutfile.write(str(encrypted_data))
					compressedoutfile.close()
					
					# Export the private key and write to file in /home/user1 and to /home/user1/secure/keys
					privatekeyfilename = 'privateKey' + PersonalGPGKey + ".gpg"
					full_path_private = filepathdestinationfolder + "/" + privatekeyfilename
					
					ascii_armored_private_key = gpg.export_keys(PersonalGPGKey, True, expect_passphrase=False)
					f2 = open(full_path_private, 'w')
					f2.write(ascii_armored_private_key)
					f2.close()

					destPriv = filepathdestinationfolder + "/secure/keys/" + privatekeyfilename
					shutil.copy(full_path_private, USBdevice)
					self.check_SecUSB()
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			global timeSecUSBLastModified
			Label1 = ctk.CTkLabel(my_Frame, text="Backup all files and key's to a USB-device", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.1, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			
			Label2 = ctk.CTkLabel(my_Frame, text="An encrypted backup of the device will be stored on the USB-device, together with a copy of the accounts login key (for decrypting).", text_color="white", fg_color="black", font=my_font)
			Label2.place(relx=0.5, rely=0.2, anchor="center")
			
			Label3 = ctk.CTkLabel(my_Frame, text="(Make sure that any changes on the local keychain has been backed up before proceeding.)", text_color="white", fg_color="black", font=my_font)
			Label3.place(relx=0.5, rely=0.3, anchor="center")
			
			theButton = ctk.CTkButton(my_Frame, text="Make a backup!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_copy_SecUSB)
			theButton.place(relx=0.5, rely=0.38, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
		
			Label4 = ctk.CTkLabel(my_Frame, text="Clone the system", text_color="white", fg_color="black", font=my_font)
			Label4.place(relx=0.5, rely=0.5, anchor="center")
				
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			Labelinf = ctk.CTkLabel(my_Frame, text="Cloning the device requires a microSD-card with minimum 32 GB. Use a USB-to-microSD adapter to connect *.", text_color="white", fg_color="black", font=my_font)
			Labelinf.place(relx=0.5, rely=0.6, anchor="center") 
			
			copySDButton = ctk.CTkButton(my_Frame, text="Clone the microSD card", text_color="white", font=my_font, border_width=2, border_color="white", fg_color=SecUSB_button_color, command=self.cloneSDcard)
			copySDButton.place(relx=0.5, rely=0.7, anchor="center")
			
			Label2inf = ctk.CTkLabel(my_Frame, text="(* Follow the instructions in the pop-up window. Make sure to check the tick-box \"New partition UUIDs\")", text_color="white", fg_color="black", font=my_font)
			Label2inf.place(relx=0.5, rely=0.8, anchor="center")
			
	def cloneSDcard( self):
		global path_to_USB_secure
		global SecUSB_button_color
		global filepathdestinationfolder
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="purple"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			answer = messagebox.askquestion('Information!', 'Before cloning the system you will be logged out (all changes will be saved first). Insert the SD-card with adaptor now. From device is /dev/mmcblk0. Check the tick-box for new partition UUIDs. Are you SURE you want to proceed?')
			if answer == 'yes':
				full_path = str(filepathdestinationfolder) + "/secure/"
				
				gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
				
				compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
				# Encrypt the tarfile and remove the unencrypted tarfile
				encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
				
				cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
				os.system(cmd)

				# Write the encrypted file to disk
				compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
				compressedoutfile.write(str(encrypted_data))
				compressedoutfile.close()
				full_path = str(filepathdestinationfolder) + "/secure"
				cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
				os.system(cmd)
				cmd = 'rm -r ' +  full_path
				os.system(cmd)
				path_to_USB_secure = 'Secure USB folder is not available'
				
				cmd = 'env SUDO_ASKPASS=/usr/lib/piclone/pwdpic.sh sudo -AE dbus-launch piclone'
				os.system(cmd)
				homeButton = ctk.CTkButton(my_Frame, text="Home", text_color="white", font=my_font, border_width=2, border_color="white", fg_color=SecUSB_button_color, command=self.create_meny)
				homeButton.place(relx=0.5, rely=0.6, anchor="center")
			else:
				messagebox.showinfo("Information", "OK. Cloning process aborted.")
				self.check_SecUSB()
						
	def restoreFromencrypted_SecUSB(self):
		# Restore from a SecUSB encrypted USB-device 
		global filepathdestinationfolder
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_Frame.focus_set()
		my_Frame.focus_force()			
		
		def do_restoreFromencrypted_SecUSB():
			global filepathdestinationfolder
			key_fingerprint = ''
			# Set the date and time
			thedate = cal.get_date()
			thetime = time_picker.time()
			
			thedatestr = str('sudo date -s \'' + str(thedate) + ' ' + str(thetime[0]) + ':' + str(thetime[1]) + ':00\'')			
			os.system(thedatestr)
			thestr = 'sudo hwclock -w'	
			os.system(thestr)
			os.system(thestr)
			
			# Select the file with the private key and scan it for fingerprint
			messagebox.showinfo("Information", "Insert the USB-device with the backup data and press OK.")
			time.sleep(2)
			messagebox.showinfo("Information", "Select the key for the account (filename starts with \"privateKey\" and ends with \".gpg\").")
			time.sleep(2)
			filepathkeyfile = filedialog.askopenfilename(initialdir='/media/user1')	
			
			keys = gpg.scan_keys(filepathkeyfile)
			key_fingerprint = str(keys.fingerprints[0])
			
			# Restore private key
			full_path = filepathdestinationfolder + '/privateKey' + key_fingerprint + '.gpg'
			if os.path.isfile(full_path):
				answer = messagebox.askquestion('WARNING!', 'WARNING! There\'s already a key with that fingerprint on the offline device! Are you SURE you want to proceed?')
				if answer == 'yes':
					# Copy over the encrypted private key
					shutil.copy(filepathkeyfile, filepathdestinationfolder)
					import_result = gpg.import_keys_file(filepathkeyfile)
		
					gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
				else:
					messagebox.showinfo("Information", "OK. Keeping the existing key on the offline device.")
			else:
				shutil.copy(filepathkeyfile, filepathdestinationfolder)
				import_result = gpg.import_keys_file(filepathkeyfile)
				gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
			
			time.sleep(2)
			messagebox.showinfo("Information", "Now select the encrypted backup archive (filename starts with the key's fingerprint and ends with \".securefolder.tar.gz.gpg\").")
			time.sleep(3)
			filepatharchivefile = filedialog.askopenfilename(initialdir='/media/user1')		
			# Copy secure archive file
			full_path_device = filepathdestinationfolder + '/' + key_fingerprint + 'securefolder.tar.gz.gpg'
			if os.path.isfile(full_path_device):
				answer = messagebox.askquestion('WARNING!', 'WARNING! There already a secure archive on the offline device for that specific key! Are you SURE you want to proceed?')
				if answer == 'yes':
					# Copy over the encrypted archive
					shutil.copy(filepatharchivefile, filepathdestinationfolder)
					messagebox.showinfo("Information", "The device has been restored from backup. Make sure to also restore/import all relevant key's from your Secure archive.")
				else:
					messagebox.showinfo("Information", "OK. Keeping the existing secure archive on the offline device.")
			else:
				shutil.copy(filepatharchivefile, filepathdestinationfolder)
				time.sleep(2)
				messagebox.showinfo("Information", "The device has been restored from backup. Make sure to also restore/import all relevant key's from your Secure archive.")
			self.decrypt_SecUSB()
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Important! Make sure to set the correct date and time:", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.1, anchor="center")

		time_picker = AnalogPicker(my_Frame, type=constants.HOURS24)
		time_picker.setHours(datetime.now().hour)
		time_picker.setMinutes(datetime.now().minute)
		time_picker.place(relx=0.65, rely=0.45, anchor="e")
		
		theme = AnalogThemes(time_picker)
		theme.setNavyBlue()
		time_picker.configAnalog(textcolor="#ffffff", bg="#0a0832", bdColor="#000000", headbdcolor="#000000")
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2024)
		cal.place(relx=0.65, rely=0.73, anchor="e")
			
		Button = ctk.CTkButton(my_Frame, text="Start restoring from backup!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_restoreFromencrypted_SecUSB)
		Button.place(relx=0.5, rely=0.86, anchor="center")
				
	def check_SecUSB(self):
		global filepathdestinationfolder
		global SecUSB_button_color
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200,                                                                                                                                                                                                                                                                        
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_text = ctk.CTkTextbox(my_Frame, width=1200, height=650, corner_radius=1, border_width=1, border_color="purple", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
		
		if path_to_USB_secure == 'Secure USB folder is available':
			my_text.insert('end', "\n\n\n" + "\n")
			my_text.insert('end', "Secure archive" + "\n")
			my_text.insert('end', "======================================================================" + "\n")
			my_text.insert('end', "Encryption: Standard: RFC 4880" + "\n")
			my_text.insert('end', "Key strenght: 4096 bits" + "\n")
			my_text.insert('end', "======================================================================" + "\n")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Button2 = ctk.CTkButton(my_Frame, text="Add file", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.addfile_SecUSB)
			Button2.place(relx=0.05, rely=0.05, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Remove file", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.removefile_SecUSB)
			Button2.place(relx=0.2, rely=0.05, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Add directory", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.add_directory_SecUSB)
			Button2.place(relx=0.35, rely=0.05, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Remove directory", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.remove_directory)
			Button2.place(relx=0.5, rely=0.05, anchor="w")
			Button3 = ctk.CTkButton(my_Frame, text="Copy a file from archive to USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=280, height=28, font=my_font, command=self.copyfile_SecUSB)
			Button3.place(relx=0.85, rely=0.05, anchor="center")
			Button3 = ctk.CTkButton(my_Frame, text="Copy the help files to USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=280, height=28, font=my_font, command=self.copyhelpfiles_SecUSB)
			Button3.place(relx=0.85, rely=0.11, anchor="center")
			Button3 = ctk.CTkButton(my_Frame, text="Copy a seed template to USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=280, height=28, font=my_font, command=self.copyseedtemplate_SecUSB)
			Button3.place(relx=0.85, rely=0.17, anchor="center")
			Button3 = ctk.CTkButton(my_Frame, text="Copy passwords template to USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=280, height=28, font=my_font, command=self.copypasswordstemplate_SecUSB)
			Button3.place(relx=0.85, rely=0.23, anchor="center")
			
			my_text.insert('end', "\n" + "All files in the secure archive (")
			size = 0.0
			
			secure_folder_path = filepathdestinationfolder + '/secure'
			the_dir = Path(secure_folder_path)
			size = sum(f.stat().st_size for f in the_dir.glob('**/*') if f.is_file())
			size_kb = size / 1024
			size_mb = size_kb / 1024
			answer = str(round(size_mb, 2))
			my_text.insert('end', answer + " MB):" + "\n")
			my_text.insert('end', "-------------------------------------" + "\n")
			full_path = str(filepathdestinationfolder) + "/secure/**/*"
			# List the file on the Secure USB
			for name in glob.glob(full_path, recursive=True): 
				my_text.insert('end', name + '\n')
		else:
			my_text.insert('end', '\n\n\n\n                                                                                            You are not logged in.' + "\n") 
		
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
	
	def copypasswordstemplate_SecUSB(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Insert USB-device. Select destination folder for the helpfiles by double clicking on it.")
		filepathdestinationfolderfull = filedialog.askdirectory(initialdir='/media/user1')
		time.sleep(3)
		if filepathdestinationfolderfull == '/media/user1':
			messagebox.showinfo("Information", "Make sure you DOUBLE CLICK on the destination folder to select it.")
		else:
			shutil.copy(filepathdestinationfolder + '/Documents/Password template.pdf', filepathdestinationfolderfull)
			messagebox.showinfo("Information", "File has been copied to USB.")
		self.check_SecUSB()
		
	def copyseedtemplate_SecUSB(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Insert USB-device. Select destination folder for the helpfiles by double clicking on it.")
		filepathdestinationfolderfull = filedialog.askdirectory(initialdir='/media/user1')
		time.sleep(3)
		if filepathdestinationfolderfull == '/media/user1':
			messagebox.showinfo("Information", "Make sure you DOUBLE CLICK on the destination folder to select it.")
		else:
			shutil.copy(filepathdestinationfolder + '/Documents/Seed templates.pdf', filepathdestinationfolderfull)
			messagebox.showinfo("Information", "File has been copied to USB.")
		self.check_SecUSB()
		
	def copyhelpfiles_SecUSB(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Insert USB-device. Select destination folder for the helpfiles by double clicking on it.")
		filepathdestinationfolderfull = filedialog.askdirectory(initialdir='/media/user1')
		time.sleep(3)
		if filepathdestinationfolderfull == '/media/user1':
			messagebox.showinfo("Information", "Make sure you DOUBLE CLICK on the destination folder to select it.")
		else:
			shutil.copy(filepathdestinationfolder + '/venvpython/help/digitalIDHelp.txt', filepathdestinationfolderfull)
			shutil.copy(filepathdestinationfolder + '/venvpython/help/securearchiveHelp.txt', filepathdestinationfolderfull)
			shutil.copy(filepathdestinationfolder + '/venvpython/help/getstartedHelp.txt', filepathdestinationfolderfull)
			shutil.copy(filepathdestinationfolder + '/venvpython/help/boltcardHelp.txt', filepathdestinationfolderfull)
			shutil.copy(filepathdestinationfolder + '/venvpython/help/gpgHelp.txt', filepathdestinationfolderfull)
			shutil.copy(filepathdestinationfolder + '/venvpython/help/yubikeyHelp.txt', filepathdestinationfolderfull)
			messagebox.showinfo("Information", "Files has been copied to USB.")
		self.check_SecUSB()
	
	def copyfile_SecUSB(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Select a file to copy to USB.")
		filepathtocopy = filedialog.askopenfilename(initialdir='/home/user1/secure')
		messagebox.showinfo("Information", "Select destination folder by double clicking on it.")
		
		filepathdestinationfolderfull = filedialog.askdirectory(initialdir='/media/user1')
		
		if filepathdestinationfolderfull == '/media/user1':
			messagebox.showinfo("Information", "Make sure you DOUBLE CLICK on the destination folder to select it.")
		else:
			shutil.copy(filepathtocopy, filepathdestinationfolderfull)
		self.check_SecUSB()
			
	def addfile_SecUSB(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Select a file to add.")
		filepathtocopy = filedialog.askopenfilename(initialdir='/media/user1')
		messagebox.showinfo("Information", "Select destination folder.")
		full_path = filepathdestinationfolder + '/secure'
		filepathdestinationfolderfull = filedialog.askdirectory(initialdir=full_path)
		shutil.copy(filepathtocopy, filepathdestinationfolderfull)
		self.check_SecUSB()
	
	def add_directory_SecUSB(self):
		global filepathdestinationfolder
		
		USER_INP = simpledialog.askstring(title="Input required!", prompt="Name of new directory:")
		messagebox.showinfo("Information", "Select where to place directory (under \"/home/user1/secure\").")
		
		newfoldername = filedialog.askdirectory(initialdir='/home/user1/secure')

		path = os.path.join(newfoldername, USER_INP)
		os.makedirs(path)
		self.check_SecUSB()					
						
	def removefile_SecUSB(self):
		global filepathdestinationfolder
		global PersonalGPGKey
		keyfilepath = '/home/user1/privateKey' + PersonalGPGKey + ".gpg"
		messagebox.showinfo("Information", "Select the file you want to remove.")
		full_path = filepathdestinationfolder + '/secure'
		filepathtoremove = filedialog.askopenfilename(initialdir=full_path)
		if filepathtoremove == keyfilepath or filepathtoremove == '/home/user1/secure/settings.csv' or filepathtoremove == '/home/user1/secure/passwords.txt' or filepathtoremove == '/home/user1/secure/boltcards/boltcards.csv' or filepathtoremove == '/home/user1/secure/wallets/wallets.txt' or filepathtoremove == '/home/user1/secure/wallets/paperwallets/paperwallets.csv' or filepathtoremove == '/home/user1/secure/FIDO/FIDOKeys.csv' or filepathtoremove == '/home/user1/secure/ID/IDs.csv':
			 messagebox.showinfo("Alert!", "This is a systems file. It can't be removed.")
			 self.removefile_SecUSB()
		else:
			os.remove(filepathtoremove)
		self.check_SecUSB()
		
	def remove_directory(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Select the directory you want to remove.")
		full_path = filepathdestinationfolder + '/secure'
		removefolderpath = filedialog.askdirectory(initialdir=full_path)
		if removefolderpath == '/home' or removefolderpath == '/home/user1' or removefolderpath == '/home/user1/secure' or removefolderpath == '/home/user1/secure/keys' or removefolderpath == '/home/user1/secure/boltcards' or removefolderpath == '/home/user1/secure/wallets' or removefolderpath == '/home/user1/secure/wallets/paperwallets' or removefolderpath == '/home/user1/secure/FIDO' or removefolderpath == '/home/user1/secure/ID':
			 messagebox.showinfo("Alert!", "This is a systems directory. It can't be removed.")
			 self.remove_directory()
		else:
			thetext = 'Are you sure you want to remove the directory ' + str(removefolderpath)
			answer = messagebox.askquestion('Warning!', thetext)
							
			if answer == 'yes':
				shutil.rmtree(removefolderpath, ignore_errors=True)
			else:
				messagebox.showinfo("Information", "OK. Keeping the directory.")
		self.check_SecUSB()
			
	def scan_Yubikey(self):
		try:
			backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
			dev = usb.core.find(..., backend=backend)
			yubikey = yubico.find_yubikey(debug=False)
			output = subprocess.getoutput("ykman info")
			thebox = self.msg_box_textbox(output, '300', '370')
		except yubico.yubico_exception.YubicoError as e:
			messagebox.showinfo("Yubikey", e.reason)	

	def scan_Yubikey_openpgp(self):
		try:
			backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
			dev = usb.core.find(..., backend=backend)
			yubikey = yubico.find_yubikey(debug=False)
			output = subprocess.getoutput("ykman openpgp info")
			self.msg_box_textbox(output, '330', '350')
		except yubico.yubico_exception.YubicoError as e:
			messagebox.showinfo("Yubikey", e.reason)		
		
	def scan_Yubikey_credentials(self):
		try:
			backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
			dev = usb.core.find(..., backend=backend)
			yubikey = yubico.find_yubikey(debug=False)
			output = subprocess.getoutput("gpg --card-status")
			self.msg_box_textbox(output, '800', '720')
		except yubico.yubico_exception.YubicoError as e:
			messagebox.showinfo("Yubikey", e.reason)
	
	def create_Bitcointextbox(self, theFlag):
		global filepathdestinationfolder
		global SecUSB_button_color
		path_to_wallets = filepathdestinationfolder + "/secure/wallets/paperwallets/paperwallets.csv"

		def setFlagAll():
			theFlag = 'all'
			self.create_Bitcointextbox(theFlag)
		def setFlagCreated():
			theFlag = 'Created'
			self.create_Bitcointextbox(theFlag)
		def setFlagActive():
			theFlag = 'Active'
			self.create_Bitcointextbox(theFlag)
		def setFlagNonKYC():
			theFlag = 'Non KYC'
			self.create_Bitcointextbox(theFlag)
		def setFlagSpent():
			theFlag = 'Spent'
			self.create_Bitcointextbox(theFlag)
		
		# scrolleable frame
		my_Frame = ctk.CTkScrollableFrame(self, 
		width=1174, 
		height=636,
		orientation="vertical",
		border_width=3,
		border_color="black",
		fg_color="gray1"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
				
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		dotLabel = ctk.CTkLabel(my_Frame, text=".", text_color="black", font=("Helvetica", 15), fg_color="black")
		dotLabel.place(relx=0.1, rely=0.99, anchor="w")
		# Make the buttons on the top of the frame on the frame
		if path_to_USB_secure == 'Secure USB folder is available':
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
			filter_all_Button = ctk.CTkButton(my_Frame, text="All wallets", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=setFlagAll)
			filter_all_Button.place(relx=0.1, y=50, anchor="center")
			
			filter_Created_Button = ctk.CTkButton(my_Frame, text="Created", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=setFlagCreated)
			filter_Created_Button.place(relx=0.25, y=50, anchor="center")
			
			filter_Active_Button = ctk.CTkButton(my_Frame, text="Active - with KYC", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=setFlagActive)
			filter_Active_Button.place(relx=0.4, y=50, anchor="center")
			
			filter_NonKYC_Button = ctk.CTkButton(my_Frame, text="Active - Non KYC", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=setFlagNonKYC)
			filter_NonKYC_Button.place(relx=0.55, y=50, anchor="center")
			
			filter_Spent_Button = ctk.CTkButton(my_Frame, text="Spent", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=setFlagSpent)
			filter_Spent_Button.place(relx=0.7, y=50, anchor="center")
			
			addButton = ctk.CTkButton(my_Frame, text="Add new", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.do_new_Bitcoinwallet)
			addButton.place(relx=0.88, y=50, anchor="center")
			
			amount = 0.0 
			amount_round = 0.0
			loopcount = 0
			try:
				with open(path_to_wallets, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							if loopcount ==0:
								Labelbuff = ctk.CTkLabel(my_Frame, text=" ", text_color="white", fg_color="black").pack(pady=50)
							if lines[0] == 'Created' and (theFlag == 'Created' or theFlag == 'all'):
								content = lines[0] + " wallet" +'                                               Created: ' + lines[1] + '     Amount: ' + lines[5] + '\n\n' + 'Address: ' + lines[2] + '\nWIF: ' + lines[3] + '\n'
								button5 = ctk.CTkButton(my_Frame, text=content, anchor='ne', text_color="black", fg_color="orange", border_width=2, border_color="white", font=my_font, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								button5.pack(pady=6)
								amount = amount + float(lines[5])
								
							if lines[0] == 'Active' and (theFlag == 'Active' or theFlag == 'all'):
								content = lines[0] + " wallet" +'                                               Created: ' + lines[1] + '     Amount: ' + lines[5] + '\n\n' + 'Address: ' + lines[2] + '\nWIF: ' + lines[3] + '\n'
								button5 = ctk.CTkButton(my_Frame, text=content, anchor='ne', text_color="black", fg_color="spring green", border_width=2, border_color="white", font=my_font, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								button5.pack(pady=6)
								amount = amount + float(lines[5])
								
							if lines[0] == 'Spent' and (theFlag == 'Spent' or theFlag == 'all'):
								content = lines[0] + " wallet" +'                                               Created: ' + lines[1] + '     Amount: ' + lines[5] + '\n\n' + 'Address: ' + lines[2] + '\nWIF: ' + lines[3] + '\n'
								button5 = ctk.CTkButton(my_Frame, text=content, anchor='ne', text_color="black", fg_color="light grey", border_width=2, border_color="white", font=my_font, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								button5.pack(pady=6)
								
							if lines[0] == 'Non KYC' and (theFlag == 'Non KYC' or theFlag == 'all'):
								content = lines[0] + " wallet" +'                                               Created: ' + lines[1] + '     Amount: ' + lines[5] + '\n\n' + 'Address: ' + lines[2] + '\nWIF: ' + lines[3] + '\n'
								button5 = ctk.CTkButton(my_Frame, text=content, anchor='ne', text_color="black", fg_color="green", border_width=2, border_color="white", font=my_font, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								button5.pack(pady=6)
								amount = amount + float(lines[5])
							loopcount = loopcount + 1
			except FileNotFoundError:
				messagebox.showinfo("Information", "No paper wallet file found.")
			amount_round = round(amount, 7)			
			if loopcount == 0:
				Labelbuff = ctk.CTkLabel(my_Frame, text=" ", text_color="white", fg_color="black").pack(pady=50)
			if theFlag == 'all':
				Label = ctk.CTkLabel(my_Frame, text="Total amount:  " + str(amount_round) + ' BTC in ' + theFlag + ' wallets (amount in spent wallets excluded).', text_color="white", font=("Arial", 18), fg_color="black")
				Label.pack(pady=20)
			if theFlag == 'Created' or theFlag == 'Active' or theFlag == 'Non KYC':
				Label = ctk.CTkLabel(my_Frame, text="Total amount:  " + str(amount_round) + ' BTC in ' + theFlag + ' wallets.', text_color="white", font=("Arial", 18), fg_color="black", underline=True)
				Label.pack(pady=20)
		else:
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Button = ctk.CTkButton(my_Frame, text="You are not logged in. Paper wallets can\'t be displayed.", font=my_font, text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.create_SecUSBmeny)
			Button.pack(pady=240)
			Label = ctk.CTkLabel(my_Frame, text=' ', text_color="white", font=("Arial", 18), fg_color="black", underline=True)
			Label.pack(pady=300)
	
	def do_edit_Bitcoinwallets(self, bechaddr):
		global filepathdestinationfolder
		global SecUSB_button_color
		amount_round = 0.0
		path_to_wallets = filepathdestinationfolder + "/secure/wallets/paperwallets/paperwallets.csv"
		notset_str = 'all'	
		the_status = ' '
		the_dt_string_short = ' '
		the_wif_private_key = ' '
		the_words = ' '
		the_amount = 0.0
		
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="black"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)

		try:
			with open(path_to_wallets, 'r') as file:
				csvfile = csv.reader(file)
				for row in csvfile:
					try:
						if row[2] == bechaddr:
							the_status = row[0]
							the_dt_string_short = row[1]
							the_wif_private_key = row[3]
							the_words = row[4]
							the_amount = row[5]
					except:
						continue
		except FileNotFoundError:
				messagebox.showinfo("Information", "No paper wallet file found.")
		amount_round = round(float(the_amount), 7)	
		# Generate QR-codes for Public address and WIF-address and read them to display on screen
		qr_public_address = qrcode.make(bechaddr, version=1)
		qr_wif_private_key = qrcode.make(the_wif_private_key, version=1)
		
		resize_qr_public_address = qr_public_address.resize((200, 200))
		resize_qr_wif_private_key = qr_wif_private_key.resize((200, 200))
		pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
		pathtowif = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/wif.png"
		
		resize_qr_public_address.save(pathtopublic)
		resize_qr_wif_private_key.save(pathtowif)

		publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(200, 200))

		wifimg = ctk.CTkImage(light_image=Image.open(pathtowif), dark_image=Image.open(pathtowif), size=(200, 200))
		
		pubLabel = ctk.CTkLabel(my_Frame, text="Load", text_color="white", font=("Arial", 28), fg_color="black")
		pubLabel.place(relx=0.15, rely=0.18, anchor="center")
		Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = publicimg)
		Labelpublicimg.place(relx=0.15, rely=0.4, anchor="center")
		
		dotLabel = ctk.CTkLabel(my_Frame, text=".", text_color="black", font=("Helvetica", 15), fg_color="black")
		dotLabel.place(relx=0.1, rely=0.99, anchor="w")
		
		wifLabel = ctk.CTkLabel(my_Frame, text="Spend (Legacy)", text_color="white", font=("Arial", 28), fg_color="black")
		wifLabel.place(relx=0.83, rely=0.18, anchor="center")
		Labelwifimg = ctk.CTkLabel(my_Frame, text = "", image = wifimg)
		Labelwifimg.place(relx=0.83, rely=0.4, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		Label1 = ctk.CTkLabel(my_Frame, text=bechaddr, text_color="white", font=("Helvetica", 20), fg_color="black")
		Label1.place(relx=0.5, rely=0.15, anchor="center")	
		Label2 = ctk.CTkLabel(my_Frame, text='Created: ' + the_dt_string_short, text_color="white", font=("Helvetica", 15), fg_color="black")
		Label2.place(relx=0.5, rely=0.3, anchor="center")	
		Label3 = ctk.CTkLabel(my_Frame, text='WIF: ' + the_wif_private_key, text_color="white", font=("Helvetica", 15), fg_color="black")
		Label3.place(relx=0.5, rely=0.4, anchor="center")	
		Label4 = ctk.CTkLabel(my_Frame, text='Amount: ' + str(amount_round) + ' BTC', text_color="white", font=my_font, fg_color="black")
		Label4.place(relx=0.5, rely=0.5, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		if (str(the_status) == "Active") or (str(the_status) == 'Created') or (str(the_status) == 'Non KYC'):
			if (str(the_amount) == '0') or (str(the_amount) == '0.0'):
				button1 = ctk.CTkButton(my_Frame, text="Add BTC", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.add_AmountToBitcoinwallet, bechaddr))
				button1.place(relx=0.5, rely=0.57, anchor="center")	
		if str(the_status) == 'Created':
			button2 = ctk.CTkButton(my_Frame, text="Change status to Active", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Active, bechaddr))
			button2.place(relx=0.5, rely=0.62, anchor="center")	
		if str(the_status) == 'Active' or str(the_status) == 'Non KYC':
			button3 = ctk.CTkButton(my_Frame, text="Change status to Spent", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Spent, bechaddr))
			button3.place(relx=0.5, rely=0.62, anchor="center")	
		button4 = ctk.CTkButton(my_Frame, text="Delete", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.do_deleteBitcoinwallet, bechaddr))
		button4.place(relx=0.5, rely=0.67, anchor="center")	
		button5 = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.create_Bitcointextbox, notset_str))
		button5.place(relx=0.5, rely=0.88, anchor="center")		
	
	def add_AmountToBitcoinwallet(self, bechaddr):
		global filepathdestinationfolder
		
		notset_str = 'all'
		path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
		updated_path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/updatedpaperwallets.csv"
		with open(path_to_wallets, 'r') as source, open(updated_path_to_wallets, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[2] == bechaddr: # Its the line to change status for
						new_paperwallet = [
										row[0],
										row[1],
										row[2],
										row[3],
										row[4],
										row[5]]
										
						USER_INP = simpledialog.askfloat(title="Add amount!", prompt="Input the amount intended for the paper wallet (optional)", initialvalue=0.0)

						new_paperwallet[5] = USER_INP
						
						answer = messagebox.askquestion('Important!', 'Are the Bitcoin you intend to load to this wallet Non KYC?')
						
						if answer == 'yes':
							new_paperwallet[0] = 'Non KYC'
							csvwriter.writerow(new_paperwallet)
						else:
							new_paperwallet[0] = 'Active'
							csvwriter.writerow(new_paperwallet)	
					else:					
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_wallets, path_to_wallets)
		os.remove(updated_path_to_wallets)	
		self.create_Bitcointextbox(notset_str)
		
	def changeStatusForBitcoinwallet_to_Spent(self, bechaddr):
		global filepathdestinationfolder
		notset_str = 'all'
		path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
		updated_path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/updatedpaperwallets.csv"
		with open(path_to_wallets, 'r') as source, open(updated_path_to_wallets, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[2] == bechaddr: 
						new_paperwallet = [
										row[0],
										row[1],
										row[2],
										row[3],
										row[4],
										row[5]]
						answer = messagebox.askquestion('Important!', 'Are you sure you want to change this wallet to spent?')
						if answer == 'yes':
							new_paperwallet[0] = 'Spent'
							csvwriter.writerow(new_paperwallet)
						else:
							csvwriter.writerow(new_paperwallet)
					else:

						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_wallets, path_to_wallets)
		os.remove(updated_path_to_wallets)	
		self.create_Bitcointextbox(notset_str)
	
	def changeStatusForBitcoinwallet_to_Active(self, bechaddr):
		global filepathdestinationfolder
		notset_str = 'all'
		path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
		updated_path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/updatedpaperwallets.csv"
		with open(path_to_wallets, 'r') as source, open(updated_path_to_wallets, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[2] == bechaddr:
						new_paperwallet = [
										row[0],
										row[1],
										row[2],
										row[3],
										row[4],
										row[5]]
						answer = messagebox.askquestion('Privacy matter!', 'Are the Bitcoin you intend to load this wallet with non KYC?')
						if answer == 'yes':
							new_paperwallet[0] = 'Non KYC'
							csvwriter.writerow(new_paperwallet)
						else:
							new_paperwallet[0] = 'Active'
							csvwriter.writerow(new_paperwallet)	
					else:

						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_wallets, path_to_wallets)
		os.remove(updated_path_to_wallets)	
		self.create_Bitcointextbox(notset_str)
			
	def do_deleteBitcoinwallet(self, bechaddr):
		global filepathdestinationfolder
		notset_str = 'all'
		path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
		updated_path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/updatedpaperwallets.csv"
		with open(path_to_wallets, 'r') as source, open(updated_path_to_wallets, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[2] == bechaddr:
						answer = messagebox.askquestion('Important!', 'Are you sure you want to delete the wallet?')
						if answer == 'yes':
							print("Not sure")
						else:
							csvwriter.writerow(row)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_wallets, path_to_wallets)
		os.remove(updated_path_to_wallets)	
		self.create_Bitcointextbox(notset_str)
	
	def do_new_Bitcoinwallet(self):
		global filepathdestinationfolder
		notset_str = 'all'
		new_Bitcoin_wallet_status = 'Created'
		# The smaller frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="black"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/venvpython/images/bluebackground.jpg"
		if path_to_USB_secure == 'Secure USB folder is available':			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							users_theme = lines[1]
							users_colors = lines[2]
			except FileNotFoundError:
				messagebox.showinfo("Information", "No settings file found.")
			if users_theme == 'Winter':
				pathtobackg = "/home/user1/venvpython/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/venvpython/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/venvpython/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/venvpython/images/darkbackgroundmid.jpg"	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
			
		USER_INP = simpledialog.askfloat(title="Add amount!", prompt="Input the amount intended for the paper wallet (optional)", initialvalue=0.0)
		
		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		dt_string_short = now.strftime("%Y-%m-%d")
		
		seed = wallet.generate_mnemonic()
		w = wallet.create_wallet(network="BTC", seed=seed, children=1)
		
		new_paperwallet = [
							new_Bitcoin_wallet_status,
							dt_string_short,
							w.get("address"),
							w.get("wif").decode("utf-8"),
							w.get("seed"),
							USER_INP]
							
		if USER_INP != 0.0:
			answer = messagebox.askquestion('Privacy matter!', 'Are the Bitcoin you intend to load this wallet with non KYC?')
			if answer == 'yes':
				new_paperwallet[0] = 'Non KYC'
			else:
				new_paperwallet[0] = 'Active'

		with open(path_to_wallets, 'a') as f:
			writer = csv.writer(f)
			writer.writerow(new_paperwallet)
		self.create_Bitcointextbox(notset_str)
App()
