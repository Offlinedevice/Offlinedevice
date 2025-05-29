#!/usr/bin/env python3
#
#  GUIApp.py
#  Version:0.3.7
#  Git repo: https://github.com/Offlinedevice
#  Offline Device for:
#     Managing GPG local keychain.
#     Storing passwords, digital wallets and files.
#     Managing Yubikey 5 NFC. OpenPGP and FIDO2.
#     Encrypting and/or signing files. 
#     Decrypting and/or verifying messages and files.
#     Generating offline Bitcoin wallets.
#     Generating and managing private digital ID's.
#     Generating and managing private Nostr ID's (Npub and Nsec).
#     Transferring Nostr keys to Nostr Signing Devices (NSD).
#     Managing Bolt Cards for BTC payments.
#     Managing Passkeys (FIDO) for passwordless login.
#     Adding and creating Bitcoi wallets (with air-gapped functionality)
#     Signing Partially signed bitcoin transactions (PSBTs) using built-in camera.
#     Timestamp signaure and associated document on Bitcoin main chain (hashed transaction as proof).
#     Calculate verification timestamp transaction for document hash (sha256) or for combined signature and document (or only document). 
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
import os.path
import glob
import tarfile
import yubico
import usb.core
import usb.backend.libusb1
import subprocess
from subprocess import check_output
import time
import math
import nostr
from seedsigner.models.psbt_parser import PSBTParser
from seedsigner.models.decode_qr import DecodeQR
from seedsigner.models.seed import Seed
from seedsigner.helpers.embit_utils import sign_message, parse_derivation_path
from seedsigner.helpers.ur2.ur import UR
from seedsigner.helpers.ur2.ur_encoder import UREncoder
from seedsigner.models.encode_qr import UrPsbtQrEncoder
from seedsigner.models.encode_qr import BaseStaticQrEncoder
from seedsigner.models.settings import SettingsConstants
from seedsigner.helpers.cbor_helper import make_message_ur
from embit import psbt
from embit import bip32
from embit import bip39
from embit.networks import NETWORKS
from seedsigner.urtypes.crypto.psbt import PSBT as UR_PSBT
from seedsigner.urtypes.cbor.encoder import Encoder
from binascii import a2b_base64, b2a_base64
import threading
from datetime import date
from tkcalendar import Calendar,DateEntry 
from tktimepicker import AnalogPicker, AnalogThemes,constants
import csv
import binascii
from bip32utils import BIP32Key
from mnemonic import Mnemonic
import bech32
import base58
from datetime import datetime
from typing import Optional
import hashlib
import hashlib
from functools import partial
import qrcode
from random import SystemRandom
from pywallet import wallet
from bitcoinlib.wallets import Wallet
from bitcoinlib.keys import Address
from bitcoinlib.mnemonic import Mnemonic as bitcoinlibMnemonic
import pyscreenshot as ImageGrab
from pyzbar.pyzbar import decode
from nostr.key import PrivateKey
from bip32 import BIP32, HARDENED_INDEX
from bip39 import (
    encode_bytes,
    decode_phrase,
    phrase_to_seed,
    EncodingError,
    DecodingError,
)

check_var = ' '
my_text_buffer = ' '
path_to_USB_secure = 'Secure USB folder is not available'
PersonalGPGKey = ''
CommunicationGPGKey = ''
clicked_privateKey = ' '
clicked_privateSubKey = ' '
clicked_communicationKey = ' ' 
filepathdestinationfolder = '/home/user1'
view_btcAddr = 'none'
ext_flag = 'none'
use_filter = 'all'
use_status = 'all'
do_sort = 'none'
commkey = ' '
timeSecUSBLastModified = '<Unknown>'
softwareVersion = '0.3.7'
softwareStatus = 'Beta'
newIDflag = False
statt = True 
n_Alias = 1
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("dark-blue")

path_to_data_file = ' '
path_to_sig = ' '
		
captured_QR = False
text_file_data = ' '
s_width = 0
s_height = 0
U2F_VENDOR_FIRST = 0x40
cnt = 0
System_button_color = 'DarkBlue'
GPG_button_color = 'green'
SecUSB_button_color = 'purple'
Yubikey_button_color = 'red'
DigitalID_button_color = 'brown'
Boltcard_button_color = 'orange'
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
		
		my_image = ctk.CTkImage(light_image=Image.open('/home/user1/images/blue.jpg'), dark_image=Image.open('/home/user1/images/blue.jpg'), size=(s_width,s_height))
		
		my_label = ctk.CTkLabel(self, text="", image=my_image)
		my_label.pack()

		self.create_meny()
				
	def encryptanddestroy(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global s_width,s_height
		
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/images/black.jpg"
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
		
		if path_to_USB_secure == 'Secure USB folder is available':
			# Try to copy over a copy of any external aliases (in case a recovery is needed in the future)
			path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
			path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
			if os.path.isfile(path_to_externalAliases):
				shutil.copy(path_to_externalAliases, path_to_externalAliases_localcopy)
			full_path = str(filepathdestinationfolder) + "/secure/"
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			# Encrypt the tarfile and remove the unencrypted tarfile
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)

			# Write the encrypted file to disk and also make a recovery if not zero
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			if os.stat(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg').st_size > 1000:
				shutil.copy(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', filepathdestinationfolder + '/Documents/RecoveryFor' + PersonalGPGKey + 'securefolder.tar.gz.gpg')
			full_path = str(filepathdestinationfolder) + "/secure"
			cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  full_path
			os.system(cmd)
			os.system('sudo shutdown -h now')
		else:
			os.system('sudo shutdown -h now')
			
	def set_colors(self, color):
		global System_button_color
		global GPG_button_color
		global SecUSB_button_color
		global Yubikey_button_color
		global DigitalID_button_color
		global Boltcard_button_color
		global Help_button_color
		
		if color != 'Varied':
			if color == 'Navy blue':
				color = 'navy'
			if color == 'Gray':
				color = 'gray13'
			if color == 'Pink':
				color = 'deep pink'
			if color == 'Red':
				color = 'brown'
			System_button_color = color
			GPG_button_color = color
			SecUSB_button_color  = color
			Yubikey_button_color  = color
			DigitalID_button_color = color
			Boltcard_button_color = color
			Help_button_color = 'dark orange'
		else:
			System_button_color = 'Navy blue'
			GPG_button_color = 'green'
			SecUSB_button_color = 'purple'
			Yubikey_button_color = 'brown'
			DigitalID_button_color = 'brown'
			Boltcard_button_color = 'orange'
			Help_button_color = 'dark orange'
				
	def create_meny(self):
		global s_width,s_height
		global System_button_color
		global GPG_button_color
		global SecUSB_button_color
		global Yubikey_button_color
		global DigitalID_button_color
		global Boltcard_button_color
		global Help_button_color
		
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/images/black.jpg"
		
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
				pathtobackg = "/home/user1/images/winterbackground.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/images/summerbackground.jpg"	
			if users_theme == 'Light':
				pathtobackg = "/home/user1/images/lightbackground.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/images/darkbackground.jpg"
			self.set_colors(users_colors)
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(s_width, s_height))
		Label_backg = ctk.CTkLabel(my_big_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		Label_backg.focus_set()
		my_big_Frame.focus_set()
		my_big_Frame.focus_force()
						
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			HomeButton = ctk.CTkButton(self, text="Home", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.create_meny)
			HomeButton.place(relx=0.1, rely=0.1, anchor="center")
			
			GPGButton = ctk.CTkButton(self, text="GPG", text_color="white", border_width=2, border_color="white", fg_color=GPG_button_color, width=120, height=32, font=my_font, command=self.create_GPGmeny)
			GPGButton.place(relx=0.2, rely=0.1, anchor="center")
			
			YubikeyButton = ctk.CTkButton(self, text="Yubikey", text_color="white", border_width=2, border_color="white", fg_color=Yubikey_button_color, width=120, height=32, font=my_font, command=self.create_Yubikeymeny)
			YubikeyButton.place(relx=0.3, rely=0.1, anchor="center")
			
			secusbButton = ctk.CTkButton(self, text="Secure archive", text_color="white", border_width=2, border_color="white", fg_color=SecUSB_button_color, width=120, height=32, font=my_font, command=self.create_SecUSBmeny)
			secusbButton.place(relx=0.4, rely=0.1, anchor="center")
			
			idButton = ctk.CTkButton(self, text="Digital ID", text_color="white", border_width=2, border_color="white", fg_color=DigitalID_button_color, width=120, height=32, font=my_font, command=self.create_DigitalIDmeny)
			idButton.place(relx=0.5, rely=0.1, anchor="center")
			
			boltcardButton = ctk.CTkButton(self, text="Bitcoin", text_color="white", border_width=2, border_color="white", fg_color=Boltcard_button_color, width=120, height=32, font=my_font, command=self.create_Bitcoinmeny)
			boltcardButton.place(relx=0.6, rely=0.1, anchor="center")
			
			HelpButton = ctk.CTkButton(self, text="Help", text_color="white", border_width=2, border_color="white", fg_color=Help_button_color, width=120, height=32, font=my_font, command=self.create_helpmeny)
			HelpButton.place(relx=0.93, rely=0.05, anchor="center")
			
			settimeButton = ctk.CTkButton(self, text="Settings", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.create_getSettimetextbox)
			settimeButton.place(relx=0.93, rely=0.1, anchor="center")

		ExitButton = ctk.CTkButton(self, text="Close and exit", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.encryptanddestroy)
		ExitButton.place(relx=0.5, rely=0.95, anchor="center")

		self.create_Hometextbox()
	
	def new_user_account_selection(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		pathtobackg = "/home/user1/images/bluebackground.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is not available':
			Button7 = ctk.CTkButton(my_Frame, text="Create a new account", text_color="white", fg_color="blue", border_width=2, border_color="white", height=36, font=my_font, command=self.new_secureUSB_Pre)
			Button7.place(relx=0.5, rely=0.3, anchor="center")
			Button8 = ctk.CTkButton(my_Frame, text="Create a new account and a key for external communication", text_color="white", fg_color="blue", border_width=2, border_color="white", height=36, font=my_font, command=self.create_getStartedmeny)
			Button8.place(relx=0.5, rely=0.6, anchor="center")
			
		else:
			Label1 = ctk.CTkLabel(my_Frame, text="You are already logged in.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.44, rely=0.4, anchor="e")
			Label11 = ctk.CTkLabel(my_Frame, text=PersonalGPGKey, text_color="white", fg_color="black", font=my_font)
			Label11.place(relx=0.45, rely=0.4, anchor="w")
			
	def create_getStartedmeny(self):
		global s_width,s_height
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/images/black.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(s_width, s_height))
		Label_backg = ctk.CTkLabel(my_big_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_big_Frame.focus_set()
		my_big_Frame.focus_force()

		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		GPGButton = ctk.CTkButton(self, text="Home", text_color="white", border_width=2, border_color="white", fg_color="blue", font=my_font, command=self.create_meny)
		GPGButton.place(relx=0.1, rely=0.1, anchor="center")
		
		HelpButton = ctk.CTkButton(self, text="Help", text_color="white", border_width=2, border_color="white", fg_color="dark orange", width=120, height=32, font=my_font, command=self.create_helpmeny)
		HelpButton.place(relx=0.93, rely=0.05, anchor="center")
		
		settimeButton = ctk.CTkButton(self, text="Settings", text_color="white", border_width=2, border_color="white", fg_color="blue", width=120, height=32, font=my_font, command=self.create_getSettimetextbox)
		settimeButton.place(relx=0.93, rely=0.1, anchor="center")
		
		ExitButton = ctk.CTkButton(self, text="Close and exit", text_color="white", border_width=2, border_color="white", fg_color="blue", width=120, height=32, font=my_font, command=self.encryptanddestroy)
		ExitButton.place(relx=0.5, rely=0.95, anchor="center")
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/bluebackground.jpg"
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
		# Make sure time and date is correct before creating any new keys 
		global filepathdestinationfolder
		global SecUSB_button_color
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/images/bluebackground.jpg"
		
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
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2025)
		cal.place(relx=0.65, rely=0.73, anchor="e")
			
		Button = ctk.CTkButton(my_Frame, text="Next!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_create_getStartedmeny_Pre)
		Button.place(relx=0.5, rely=0.86, anchor="center")
		
	def create_getStartedmeny2(self):	
		global path_to_USB_secure
		global filepathdestinationfolder
		global commkey
		users_avatar_name = 'Bobby'
		new_Avatar_Entry = 'Anon'
		
		check_var = ctk.StringVar(value="off") 
		pathtobackg = "/home/user1/images/bluebackground.jpg"
		
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
		
		def show_progress(_value):
			my_font = ctk.CTkFont(family="Helvetica", size=26, weight="bold", slant="roman", underline=False, overstrike=False)
			LLabel3 = ctk.CTkLabel(my_Frame, text="Progress......... " + _value + " %", text_color="white", fg_color="black", font=my_font)
			LLabel3.place(relx=0.5, rely=0.71, anchor="center")
			
		def getStarted_pre():
			time.sleep(1)
			show_progress('5')
			tk.messagebox.showinfo('Information', 'Now we will generate the Offline device key. Move mouse around for randomness.')
			getStarted()
			
		def getStarted():
			global path_to_USB_secure
			global PersonalGPGKey
			global filepathdestinationfolder
			global commkey
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')

			full_path = str(filepathdestinationfolder) + "/secure"
			cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
			os.system(cmd)
			cmd = 'rm -r ' +  full_path
			os.system(cmd)
			
			# Create a GPG master key for personal use
			input_data_priv = gpg.gen_key_input(key_type='rsa', name_real=namePrivateEntry.get(), expire_date='0', key_length='4096', name_email=emailPrivateEntry.get(), passphrase=Secret_passphrasePrivateEntry.get())
			privatekey = gpg.gen_key(input_data_priv)
			
			PersonalGPGKey = str(privatekey.fingerprint)
			
			show_progress('15')
			tk.messagebox.showinfo('Information', 'Generating a communication key. Keep moving the mouse around.\n\n      Press \"OK\" to start.')
			getStarted2()
			
		def getStarted2():	
			global commkey
			global communicationkey
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			# Create a GPG master key 
			input_data_comm = gpg.gen_key_input(key_type='rsa',  key_usage='sign', name_real=nameCommunicationEntry.get(), expire_date='0', key_length='4096', name_email=emailCommunicationEntry.get(), passphrase=Secret_passphraseCommunicationEntry.get())
			communicationkey = gpg.gen_key(input_data_comm)
			
			commkey = str(communicationkey.fingerprint)	
			show_progress('25')
			tk.messagebox.showinfo('Information', 'Adding (3) subkeys to the communication key.')
			
			getStarted3()
			
		def getStarted3():
			global filepathdestinationfolder
			global communicationkey
			global PersonalGPGKey
			global commkey
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
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
			
			self.new_Alias_real_name(PersonalGPGKey, "Offline device Key")
			self.new_Alias_real_name(commkey, nameCommunicationEntry.get())
			
			# Add an entry in External alias file for avatar login (if less than 4 already)	
			new_Avatar_Entry = namePrivateEntry.get()	
			new_external_alias = [PersonalGPGKey, users_avatar_name_var.get(), 'Anon']

			# Make local copy for external alias (in case of recovery on new device)
			path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
			with open(path_to_externalAliases_localcopy, 'w') as f:
				writer = csv.writer(f)
				writer.writerow(new_external_alias)
			
			self.new_Alias_real_name(PersonalGPGKey, "Offline device Key")
			
			path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
			if not os.path.isfile(path_to_externalAliases):
				f = open(path_to_externalAliases, 'w')
				writer = csv.writer(f)
				writer.writerow(new_external_alias)
				f.close()
			else:
				try:
					with open(path_to_externalAliases) as f:
						nr_avatars = sum(1 for line in f)
				except FileNotFoundError:
					messagebox.showinfo("Information", "No Alias file found.")
				if nr_avatars < 4:
					with open(path_to_externalAliases, 'a') as f:
						writer = csv.writer(f)
						writer.writerow(new_external_alias)
							
			c = open(full_path + "passwords.txt", 'w')
			c.write(str("Passwords\n___________________________________\n\nYubikey\n\n   OpenPGP Admin PIN:  \n\n   OpenPGP PIN:  \n\n   Comment:  \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n"))
			c.close()
			c = open(full_path_wallets + "wallets.txt", 'w')
			c.write(str("Wallets\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n"))
			c.close()
			with open(full_path_settings_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['Username', 'Theme', 'Colors']
			with open(full_path_paperwallets_file, 'w', newline='') as file:
				writer = csv.writer(file)
				field = ['Name', 'Datecreated', 'Pubkey', 'wif', 'mnemonic', 'amount', 'Category']
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
			show_progress('50')
			tk.messagebox.showinfo('Information', 'Storing the keys in the secure archive.')
			
			getStarted4()
			
		def getStarted4():	
			global filepathdestinationfolder
			global PersonalGPGKey
			global commkey	
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
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
			
			getStarted5()
			
		def getStarted5():
			global filepathdestinationfolder
			global PersonalGPGKey
			
			privatekeyfilename = 'privateKey' + PersonalGPGKey + ".gpg"
			full_path_private = filepathdestinationfolder + "/" + privatekeyfilename
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
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
			show_progress('72')
			answer = messagebox.askquestion('Important!', 'Do you want to create a backup on a USB-device now?')
			if answer == 'yes':
				tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
				time.sleep(2)
				show_progress('75')
				messagebox.showinfo("Information", "Select the folder where to store the backup.")
				time.sleep(2)
				localfilepathdestinationfolder = filedialog.askdirectory(initialdir='/media/user1/')
				
				if localfilepathdestinationfolder == '/media/user1':
					messagebox.showinfo("Information", "You need to double click on the USB-device to select it!")
					time.sleep(2)
					localfilepathdestinationfolder = filedialog.askdirectory(initialdir='/media/user1/')
					if localfilepathdestinationfolder == '/media/user1':
						messagebox.showinfo("Information", "No USB-device selected. Backup will not be stored!")
					else:
						shutil.copy(full_path_private, localfilepathdestinationfolder)
						# Write the encrypted file to backup USB-stick
						compressedoutfile = open(localfilepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
						compressedoutfile.write(str(encrypted_data))
						compressedoutfile.close()
						show_progress('90')
						messagebox.showinfo("Information", "Encrypted archive file and key written to the USB-device successfully. Please remove USB-device.")
				else:
					shutil.copy(full_path_private, localfilepathdestinationfolder)
					# Write the encrypted file to backup USB-stick
					compressedoutfile = open(localfilepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
					compressedoutfile.write(str(encrypted_data))
					compressedoutfile.close()
					show_progress('90')
					messagebox.showinfo("Information", "Encrypted archive file and key written to the USB-device successfully. Please remove USB-device.")
			getStarted6()
		
		def getStarted6():
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
		
		users_avatar_name_var = StringVar()
		
		def limitSizeAvatarname(*args):
			value = users_avatar_name_var.get()
			if len(value) > 17: users_avatar_name_var.set(value[:17])
							
		users_avatar_name_var = ctk.StringVar(value=users_avatar_name)
		users_avatar_name_var.trace('w', limitSizeAvatarname)
		
		Label = ctk.CTkLabel(my_Frame, text="Please provide your data:", text_color="white", fg_color="black", font=my_font)
		Label.place(relx=0.3, rely=0.1, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		# Data for the private key
		Labelprivate = ctk.CTkLabel(my_Frame, text="Private key*:", text_color="white", fg_color="black", font=my_font)
		Labelprivate.place(relx=0.3, rely=0.17, anchor="w")
		namePrivate = ctk.CTkLabel(my_Frame, text="Full name:", text_color="white", fg_color="black", font=my_font)
		namePrivate.place(relx=0.34, rely=0.22, anchor="e")
		namePrivateEntry = ctk.CTkEntry(my_Frame, placeholder_text=users_avatar_name, textvariable=users_avatar_name_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
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
		
		checkbox = ctk.CTkCheckBox(my_Frame, text="I have a Yubikey 5 NFC.", variable=check_var, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		checkbox.place(relx=0.35, rely=0.58, anchor="w")
		
		goButton = ctk.CTkButton(my_Frame, text="Lets Go! ***", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=getStarted_pre)
		goButton.place(relx=0.5, rely=0.66, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		LLabel3 = ctk.CTkLabel(my_Frame, text="*** This can take a while.. Move mouse around to create randomness...\nFollow all the instructions for the rest of the setup.", text_color="white", fg_color="black", font=my_font)
		LLabel3.place(relx=0.5, rely=0.77, anchor="center")
		my_font = ctk.CTkFont(family="Helvetica", size=15, weight="normal", slant="roman", underline=False, overstrike=False)
		Labelinf1 = ctk.CTkLabel(my_Frame, text="* Private key is for private use (like encrypting the secure archive on the offline device etc).", text_color="white", fg_color="black", font=my_font)
		Labelinf1.place(relx=0.05, rely=0.85, anchor="w")
		Labelinf2 = ctk.CTkLabel(my_Frame, text="** Communication key is used for signing other public keys, encrypting emails etc. Subkeys should be on a Yubikey (for safe use with computers/smartphones).", text_color="white", fg_color="black", font=my_font)
		Labelinf2.place(relx=0.05, rely=0.91, anchor="w")
			
	def getStartedfinnished(self):
		global path_to_USB_secure
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/bluebackground.jpg"
		
		path_to_USB_secure = 'Secure USB folder is available'
		
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
		Label5 = ctk.CTkLabel(my_Frame, text="(3). A backup USB-stick in case the offline device breaks or there is a fire or theft etc (optional).", text_color="white", fg_color="black", font=my_font)
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
		
		mainHelpButton = ctk.CTkButton(self, text="Help", text_color="white", border_width=2, border_color="white", fg_color="dark orange",  width=120, height=32, font=my_font, command=self.create_helpmeny)
		mainHelpButton.place(relx=0.93, rely=0.05, anchor="center")
		
		Button1 = ctk.CTkButton(self, text="Getting started", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_abouthelptextbox)
		Button1.place(relx=0.1, rely=0.2, anchor="center")
		
		Button2 = ctk.CTkButton(self, text="GPG", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_gpghelptextbox)
		Button2.place(relx=0.25, rely=0.2, anchor="center")
		
		Button3 = ctk.CTkButton(self, text="Yubikey", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_yubikeyhelptextbox)
		Button3.place(relx=0.4, rely=0.2, anchor="center")
		
		Button4 = ctk.CTkButton(self, text="Secure archive", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_secusbhelptextbox)
		Button4.place(relx=0.55, rely=0.2, anchor="center")
		
		Button5 = ctk.CTkButton(self, text="Digital ID\'s", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_digitalIDhelptextbox)
		Button5.place(relx=0.7, rely=0.2, anchor="center")
		
		Button6 = ctk.CTkButton(self, text="Bitcoin", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_boltcardhelptextbox)
		Button6.place(relx=0.85, rely=0.2, anchor="center")
	
	def create_GPGmeny(self):
		global GPG_button_color
		self.get_GnuPGKeys_compact()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		CheckGPGButton = ctk.CTkButton(self, text="Check local keys", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.get_GnuPGKeys_compact)
		CheckGPGButton.place(relx=0.1, rely=0.2, anchor="center")
		
		AddkeyButton = ctk.CTkButton(self, text="Add/remove key", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.newGPGFull_Key)
		AddkeyButton.place(relx=0.25, rely=0.2, anchor="center")
		
		AddsubkeyButton = ctk.CTkButton(self, text="Add subkeys", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.newGPG_Subkey)
		AddsubkeyButton.place(relx=0.4, rely=0.2, anchor="center")
		
		BackupkeysButton = ctk.CTkButton(self, text="Backup keys", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.backupGPG_Keys)
		BackupkeysButton.place(relx=0.55, rely=0.2, anchor="center")
		
		ImportkeyButton = ctk.CTkButton(self, text="Import/export", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.import_or_export)
		ImportkeyButton.place(relx=0.7, rely=0.2, anchor="center")
		
		SignkeyButton = ctk.CTkButton(self, text="Encrypt/Sign/check", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.select_what_to_sign)
		SignkeyButton.place(relx=0.85, rely=0.2, anchor="center")
	
	def create_SecUSBmeny(self):
		global SecUSB_button_color
		global path_to_USB_secure
		
		self.create_secusbtextbox()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button1 = ctk.CTkButton(self, text="Secure archive", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.check_SecUSB, "none"))
		Button1.place(relx=0.1, rely=0.2, anchor="center")
		
		Button2 = ctk.CTkButton(self, text="Encrypt/view a text", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.encrypt_message)
		Button2.place(relx=0.25, rely=0.2, anchor="center")
		
		Button3 = ctk.CTkButton(self, text="Decrypt a textfile", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_message)
		Button3.place(relx=0.4, rely=0.2, anchor="center")
		
		Button4 = ctk.CTkButton(self, text="Make a backup", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.copy_SecUSB)
		Button4.place(relx=0.55, rely=0.2, anchor="center")
		
		Button5 = ctk.CTkButton(self, text="Clone the system", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.clone_microSD)
		Button5.place(relx=0.7, rely=0.2, anchor="center")
		
		Button6 = ctk.CTkButton(self, text="Restore from USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.restore_SecUSB)
		Button6.place(relx=0.85, rely=0.2, anchor="center")
		
		if path_to_USB_secure == 'Secure USB folder is not available':
			Button8 = ctk.CTkButton(self, text="Log in", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			Button8.place(relx=0.5, rely=0.5, anchor="center")
			Label = ctk.CTkLabel(self, text="Or", text_color="white", font=("Helvetica", 18), fg_color="black")
			Label.place(relx=0.5, rely=0.55, anchor="center")
			Button7 = ctk.CTkButton(self, text="Create new user account", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.new_secureUSB_Pre)
			Button7.place(relx=0.5, rely=0.6, anchor="center")
	
	def create_DigitalIDmeny(self):
		global DigitalID_button_color
		global path_to_USB_secure
		
		self.create_DigitalIDbox()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button1 = ctk.CTkButton(self, text="Digital ID", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_DigitalIDmeny)
		Button1.place(relx=0.1, rely=0.2, anchor="center")
		
		Button2 = ctk.CTkButton(self, text="Nostr", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.Nostr_main)
		Button2.place(relx=0.25, rely=0.2, anchor="center")
		
		Button3 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_DigitalIDmeny)
		Button3.place(relx=0.4, rely=0.2, anchor="center")
		
		Button4 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_DigitalIDmeny)
		Button4.place(relx=0.55, rely=0.2, anchor="center")
		
		Button5 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_DigitalIDmeny)
		Button5.place(relx=0.7, rely=0.2, anchor="center")
		
		Button6 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_DigitalIDmeny)
		Button6.place(relx=0.85, rely=0.2, anchor="center")
	
	def create_Bitcoinmeny(self):
		global Boltcard_button_color
		global path_to_USB_secure
		
		self.create_BitcoinWalletmeny()
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button1 = ctk.CTkButton(self, text="Bitcoin wallets", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_BitcoinWalletmeny)
		Button1.place(relx=0.1, rely=0.2, anchor="center")
		
		Button2 = ctk.CTkButton(self, text="BTC single wallets", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
		Button2.place(relx=0.25, rely=0.2, anchor="center")
		
		Button3 = ctk.CTkButton(self, text="Bolt cards", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Boltcardmeny)
		Button3.place(relx=0.4, rely=0.2, anchor="center")
		
		Button4 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Bitcoinmeny)
		Button4.place(relx=0.55, rely=0.2, anchor="center")
		
		Button5 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Bitcoinmeny)
		Button5.place(relx=0.7, rely=0.2, anchor="center")
		
		Button6 = ctk.CTkButton(self, text=" ", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Bitcoinmeny)
		Button6.place(relx=0.85, rely=0.2, anchor="center")
				
	def create_FIDOmeny(self):
		global FIDO_button_color
		global filepathdestinationfolder
		
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
		
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
		
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
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoIDimage = str(filepathdestinationfolder) + "/images/Yubikey5CBackground.JPG"

			IDimagebutton = ctk.CTkImage(light_image=Image.open(pathtoIDimage), dark_image=Image.open(pathtoIDimage), size=(230, 100))
			completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
			my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			counter = 0
			Buttonnew = ctk.CTkButton(right_Frame, text="New Passkey", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=25, font=my_font, command=self.newFIDO)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			
			infoLabel = ctk.CTkLabel(right_Frame, text="Add new Passkey:", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.1, rely=0.15, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			
			infoLabel = ctk.CTkLabel(right_Frame, text="1. Use a hardware key with FIDO2 (Passkey) support (ex. Yubikey 5 or similar).", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.1, rely=0.21, anchor="w")
			infoLabel2 = ctk.CTkLabel(right_Frame, text="   - Reset the key using an offline device (this will remove factory keys and generate new keys).", text_color="white", font=my_font, fg_color="black")
			infoLabel2.place(relx=0.1, rely=0.26, anchor="w")
			infoLabel3 = ctk.CTkLabel(right_Frame, text="2. - Register the Passkey online at all services that the specific key should work with.", text_color="white", font=my_font, fg_color="black")
			infoLabel3.place(relx=0.1, rely=0.32, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="3. Remember to have at minimum two keys registered for each service, as one key could get lost/stolen or break.", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.1, rely=0.41, anchor="w")
			infoLabel5 = ctk.CTkLabel(right_Frame, text="4. Add a new Passkey entry on the offline device (this device) by clicking \"New Passkey\".", text_color="white", font=my_font, fg_color="black")
			infoLabel5.place(relx=0.1, rely=0.46, anchor="w")
			infoLabel6 = ctk.CTkLabel(right_Frame, text="   - Give the Passkey a name. Its good practice to include the keys printed serial number or similar", text_color="white", font=my_font, fg_color="black")
			infoLabel6.place(relx=0.1, rely=0.51, anchor="w")
			infoLabel7 = ctk.CTkLabel(right_Frame, text="   - Give the Passkey a description.", text_color="white", font=my_font, fg_color="black")
			infoLabel7.place(relx=0.1, rely=0.56, anchor="w")
			infoLabel8 = ctk.CTkLabel(right_Frame, text="5. After created a Passkey entry click on it and click \"Edit\" and enter services that it is registered at.", text_color="white", font=my_font, fg_color="black")
			infoLabel8.place(relx=0.1, rely=0.61, anchor="w")
			infoLabel9 = ctk.CTkLabel(right_Frame, text="   - This information is only to help in remembering what key is used for what.", text_color="white", font=my_font, fg_color="black")
			infoLabel9.place(relx=0.1, rely=0.66, anchor="w")
			infoLabel10 = ctk.CTkLabel(right_Frame, text="6. Keep the extra Passkey(s) safe.", text_color="white", font=my_font, fg_color="black")
			infoLabel10.place(relx=0.1, rely=0.71, anchor="w")
			
			proLabel = ctk.CTkLabel(right_Frame, text="(Tip: Passkeys are more secure as there is no password/username sent over the Internet to access an account.)", text_color="white", font=my_font, fg_color="black")
			proLabel.place(relx=0.1, rely=0.85, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)								
			cardLabel = ctk.CTkLabel(left_Frame, text="Passkeys", text_color="white", font=my_font, fg_color="black").pack(padx=10, pady=8, side= TOP, anchor="center")
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
				messagebox.showinfo("Information", "No Passkeys found.")
		else:
			notOKButton = ctk.CTkButton(right_Frame, text="You are not logged in.", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def showFIDO(self, FIDOname):
		global filepathdestinationfolder
		
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
		
		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
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
		
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoicon = str(filepathdestinationfolder) + "/images/Yubikey5CBackground.JPG"

			iconimage = ctk.CTkImage(light_image=Image.open(pathtoicon), dark_image=Image.open(pathtoicon), size=(230, 100))
			
			completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"
			my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)								
			cardLabel = ctk.CTkLabel(left_Frame, text="Passkeys", text_color="white", font=my_font, fg_color="black").pack(padx=10, pady=8, side= TOP, anchor="center")
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
				messagebox.showinfo("Information", "No Passkeys found.")
			Buttonnew = ctk.CTkButton(right_Frame, text="New Passkey", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newFIDO)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:

						if lines[0] == FIDOname:								
							my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=True, overstrike=False)
							nameheadLabel = ctk.CTkLabel(right_Frame, text="Name of Passkey:", text_color="white", font=my_font, fg_color="black")
							nameheadLabel.place(relx=0.05, rely=0.18, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)								
							nameLabel = ctk.CTkLabel(right_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							nameLabel.place(relx=0.05, rely=0.22, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
							descrheadLabel = ctk.CTkLabel(right_Frame, text="Description:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.05, rely=0.27, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)								
							descrLabel = ctk.CTkLabel(right_Frame, text=lines[1], text_color="white", font=my_font, fg_color="black")
							descrLabel.place(relx=0.05, rely=0.31, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
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
				messagebox.showinfo("Information", "No Passkeys file found.")
		else:
			notOKButton = ctk.CTkButton(my_Frame, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")

	def editFIDO(self, FIDOname):
		global SecUSB_button_color
		global filepathdestinationfolder
		
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
		
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
		
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
							my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
							nameheadLabel = ctk.CTkLabel(my_Frame, text="Name of Passkey:", text_color="white", font=my_font, fg_color="black")
							nameheadLabel.place(relx=0.2, rely=0.18, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)								
							
							the_name_var = ctk.StringVar(value=lines[0])
		
							nameEntry = ctk.CTkEntry(my_Frame, placeholder_text=lines[0], textvariable=the_name_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
							nameEntry.place(relx=0.2, rely=0.24, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
							
							descrheadLabel = ctk.CTkLabel(my_Frame, text="Description:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.2, rely=0.29, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)								
							
							the_description_var = ctk.StringVar(value=lines[1])
							
							descriptionEntry = ctk.CTkEntry(my_Frame, placeholder_text=lines[1], textvariable=the_description_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
							descriptionEntry.place(relx=0.2, rely=0.33, anchor="w")
							
							my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
							descrheadLabel = ctk.CTkLabel(my_Frame, text="Used for services:", text_color="white", font=my_font, fg_color="black")
							descrheadLabel.place(relx=0.2, rely=0.38, anchor="w")
							
							self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 16), wrap = 'word', undo = True)
							self.textBox.insert("1.0", lines[2])
							self.textBox.place(relx=0.2, rely=0.42, height=220, width=600, anchor="nw")
							self.textBox.focus_set()
							self.textBox.focus_force()
							theinput = self.textBox.get("1.0",'end-1c')
							my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
								
							backButton = ctk.CTkButton(my_Frame, text="Save", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=do_edit_FIDO)
							backButton.place(relx=0.5, rely=0.85, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Passkeys file found.")
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
						answer = messagebox.askquestion('Important!', 'Are you sure you want to delete the Passkey?')
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
		now = datetime.now() # current date and time
		timeStamp = now.strftime("%m%d%Y%H%M%S")
		
		# Create a new card. Details and pictures from USB-drive
		USER_INP = simpledialog.askstring(title="Name required!", prompt="Enter name for new Passkey:")
		
		if USER_INP == "" or USER_INP == " ":
			USER_INP = "Passkey" + timeStamp
		
		USER_INP_tr = USER_INP[:100] if len(USER_INP) > 100 else USER_INP
		
		USER_INP2 = simpledialog.askstring(title="Description.", prompt="Description for the new Passkey (optional):")
		
		if USER_INP2 == "" or USER_INP2 == " ":
			USER_INP2 = "-"
		
		USER_INP2_tr = USER_INP2[:100] if len(USER_INP2) > 100 else USER_INP2
		
		new_FIDOkey = [USER_INP_tr, USER_INP2_tr, '<Empty>']
		
		completeName = str(filepathdestinationfolder) + "/secure/FIDO/FIDOkeys.csv"	
		
		try:
			f = open(completeName, 'a')
			writer = csv.writer(f)
			writer.writerow(new_FIDOkey)
			f.close()
		except FileNotFoundError:
			messagebox.showinfo("Information", "No Passkeys file found.")
		self.add_history("Added new Passkey: " + USER_INP_tr + " (" + USER_INP2_tr + ")")
		self.create_FIDOmeny()
	
	def new_Alias_real_name(self, fingerprint, pref_Alias):
		global filepathdestinationfolder
		already_there = False
		global n_Alias
		
		def try_again():
			global n_Alias
			n_Alias = n_Alias + 1
			pref_Alias_n = pref_Alias + ' ' + str(n_Alias)
			self.new_Alias_real_name(fingerprint, pref_Alias_n)
			
		pref_Alias = pref_Alias[:38]

		new_Alias = [fingerprint, pref_Alias]
		file_ = filepathdestinationfolder + "/secure/Alias.csv"	
			
		# Check if alias file exists. If not create it
		if not os.path.isfile(file_):
			f = open(file_, 'w')
			writer = csv.writer(f)
			writer.writerow(new_Alias)
			f.close()
		else:
			try:
				f = open(file_, 'r')
				for row in csv.reader(f):
					if row[1] == pref_Alias:
						already_there = True
						try_again()
				f.close()
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Alias file found.")
			if not already_there:
				try:
					f = open(file_, 'a')
					writer = csv.writer(f)
					writer.writerow(new_Alias)
					f.close()
				except FileNotFoundError:
					messagebox.showinfo("Information", "No Alias file found.")
		return True
		
	def new_Alias(self, fingerprint):
		global filepathdestinationfolder
		already_there = False
		
		def try_again():
			messagebox.showinfo("Information", "The alias can be max 42 characters.")
			self.new_Alias(fingerprint)
			
		# Create a new alias.
		USER_INP = simpledialog.askstring(title="Information!", prompt="Enter alias for key:")
		input_size = len(USER_INP)
		if input_size > 42:
			try_again()
		new_Alias = [fingerprint, USER_INP]
		file_ = filepathdestinationfolder + "/secure/Alias.csv"	
			
		# Check if alias file exists. If not create it
		if not os.path.isfile(file_):
			f = open(file_, 'w')
			writer = csv.writer(f)
			writer.writerow(new_Alias)
			f.close()
		else:
			try:
				f = open(file_, 'r')
				for row in csv.reader(f):
					if row[1] == USER_INP:
						already_there = True
						messagebox.showinfo("Information", "Alias already exists!")
				f.close()
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Alias file found.")
			if not already_there:
				try:
					f = open(file_, 'a')
					writer = csv.writer(f)
					writer.writerow(new_Alias)
					f.close()
					self.add_history("Added new alias: " + USER_INP + ", for key " + fingerprint)
				except FileNotFoundError:
					messagebox.showinfo("Information", "No Alias file found.")
		self.get_GnuPGKeys()
	
	def lookup_Alias(self, fingerprint):
		global filepathdestinationfolder
		file_ = filepathdestinationfolder + "/secure/Alias.csv"
		if os.path.isfile(file_):
			try:
				f = open(file_, 'r')
				for row in csv.reader(f):
					if row[0] == fingerprint:
						the_Alias = row[1]
						return the_Alias	
				f.close()
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Alias file found.")
		return fingerprint
	
	def lookup_Alias_absolut(self, fingerprint):
		global filepathdestinationfolder
		not_found = "None"
		file_ = filepathdestinationfolder + "/secure/Alias.csv"
		if os.path.isfile(file_):
			try:
				f = open(file_, 'r')
				for row in csv.reader(f):
					if row[0] == fingerprint:
						the_Alias = row[1]
						return the_Alias	
				f.close()
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Alias file found.")
		return not_found
	
	def lookup_fingerprint(self, alias):
		global filepathdestinationfolder
		file_ = filepathdestinationfolder + "/secure/Alias.csv"
		if os.path.isfile(file_):
			try:
				f = open(file_, 'r')
				for row in csv.reader(f):
					if row[1] == alias:
						the_Fingerprint = row[0]
						return the_Fingerprint
				f.close()
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Alias file found.")
		return alias
		
	def get_Aliases(self, list_of_fingerprints):
		global filepathdestinationfolder
		List_fingerprints_and_aliases = []

		file_ = filepathdestinationfolder + "/secure/Alias.csv"
		# For each row in the list of fingerprints check if there is an alias. If not add the fingerprint in both locations
		if os.path.isfile(file_):
			for nkey in list_of_fingerprints:
				found_fingerprint = False
				try:
					f = open(file_, 'r')
					for row in csv.reader(f):
						if row[0] == nkey:
							List_fingerprints_and_aliases.append(row[1])
							found_fingerprint = True	
					f.close()
				except FileNotFoundError:
					messagebox.showinfo("Information", "No Alias file found.")
				if not found_fingerprint:
					List_fingerprints_and_aliases.append(nkey)
		else:
			return list_of_fingerprints
		return List_fingerprints_and_aliases	
		
	def remove_Alias(self, fingerprint):
		global filepathdestinationfolder
		file_ = filepathdestinationfolder + "/secure/Alias.csv"
		temp_file_ = filepathdestinationfolder + "/secure/temp_Alias.csv"
		if os.path.isfile(file_):
			with open(file_, 'r') as inp, open(temp_file_, 'w') as out:
				writer = csv.writer(out)
				for row in csv.reader(inp):
					if row[0] != fingerprint:
						writer.writerow(row)	
			shutil.copy(temp_file_, file_)
		self.get_GnuPGKeys()
			
	def create_Boltcardmeny(self):
		global Boltcard_button_color
		global filepathdestinationfolder
		
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
		
		pathtobackg = self.get_background_image()
		
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
		pathtobackg = "/home/user1/images/boltcardbackground.JPG"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoIDimage = str(filepathdestinationfolder) + "/images/boltcardicon.JPG"

			IDimagebutton = ctk.CTkImage(light_image=Image.open(pathtoIDimage), dark_image=Image.open(pathtoIDimage), size=(230, 100))
			completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			counter = 0
			Buttonnew = ctk.CTkButton(right_Frame, text="New card", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newcard)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			
			readButton = ctk.CTkButton(right_Frame, text="Read UID/URI", text_color="white", fg_color=Boltcard_button_color, border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.readUUID_with_NFC)
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
			
			proLabel = ctk.CTkLabel(right_Frame, text="Pro tip1: You can get the file sent to you. Made with your Boltcard UID and encypted with your public key.", text_color="white", font=my_font, fg_color="black")
			proLabel.place(relx=0.1, rely=0.8, anchor="w")
			proLabel2 = ctk.CTkLabel(right_Frame, text="Pro tip2: Using https://ff.io or https://boltz.exchange/swap with swap from Liquid-BTC (l-BTC) will save on fees.", text_color="white", font=my_font, fg_color="black")
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
							my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
							if Counting == 0:	
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showcard, lines[0]))
								Button1.pack(padx=10, pady=18, side= TOP, anchor="w")
								Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
								Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							else:
								Button1 = ctk.CTkButton(left_Frame, text="", image = IDimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showcard, lines[0]))
								Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
								Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
								Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							Counting += 1
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Bolt cards file found.")
		else:
			notOKButton = ctk.CTkButton(right_Frame, text="You are not logged in.", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def showcard(self, cardname):
		global filepathdestinationfolder
		global pathtoloadaddress
		httpaddress = ''
		username = ''
		password = ''
		
		def show_LNHubdata():
			LNHubdata = 'Login details LN Hub:\n\n' + httpaddress + '\n\nUser name: ' + username + '\n  Password: ' + password  
			messagebox.showinfo("LN Hub login", LNHubdata)
			
		def save_load_QR():
			tk.messagebox.showinfo('Information', 'Insert the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select where to save the image with the load- address."')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			pathtopic = outputdir + '/Boltcard_load_address.png'
			shutil.copy(pathtoloadaddress, pathtopic)
			
			if os.path.isfile(pathtopic):
				tk.messagebox.showinfo('Information', 'QR image has been saved."')
			
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
		
		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=644,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=2, anchor="nw")
		
		pathtobackg = "/home/user1/images/boltcardbackground.JPG"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoboltcardicon = str(filepathdestinationfolder) + "/images/boltcardicon.JPG"

			boltcardiconimage = ctk.CTkImage(light_image=Image.open(pathtoboltcardicon), dark_image=Image.open(pathtoboltcardicon), size=(230, 100))
			
			completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:	
							my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
							Button1 = ctk.CTkButton(left_Frame, text="", image = boltcardiconimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showcard, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No Bolt cards file found.")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Buttonnew = ctk.CTkButton(right_Frame, text="New card", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.newcard)
			Buttonnew.place(relx=0.9, rely=0.05, anchor="center")
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						try:
							if lines[0] == cardname:
								httpaddress = lines[8]
								username = lines[9]
								password = lines[10]
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
								
								LNHubButton = ctk.CTkButton(right_Frame, text="Show LN Hub login", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=show_LNHubdata)
								LNHubButton.place(relx=0.49, rely=0.66, anchor="center")
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
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		
		pathtobackg = self.get_background_image()
		
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
		completeName = str(filepathdestinationfolder) + "/secure/boltcards/boltcards.csv"
		updatedcompleteName = str(filepathdestinationfolder) + "/secure/boltcards/updatedboltcards.csv"
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		
		pathtobackg = self.get_background_image()
		
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
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		
		pathtobackg = self.get_background_image()
		
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
							self.add_history("Deleted Bolt card: " + cardname)
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
		now = datetime.now() # current date and time
		timeStamp = now.strftime("%m%d%Y%H%M%S")
		# Create a new card. Details and pictures from USB-drive
		USER_INP = simpledialog.askstring(title="Name required.", prompt="Name for the new Bolt card:")
		
		if USER_INP == "" or USER_INP == " ":
			USER_INP = "Boltcard" + timeStamp
		
		USER_INP_tr = USER_INP[:22] if len(USER_INP) > 22 else USER_INP
		
		USER_INP2 = simpledialog.askstring(title="Description.", prompt="Description for the new Bolt card:")
		
		if USER_INP2 == "" or USER_INP2 == " ":
			USER_INP2 = "-"
			
		USER_INP2_tr = USER_INP2[:22] if len(USER_INP2) > 22 else USER_INP2
		
		answer = messagebox.askquestion('Information!', 'Is the file containing the Bolt card data without encryption?')
			
		if answer == 'no':
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

							new_boltcard = [USER_INP_tr, USER_INP2_tr, thedate, lines[0], lines[1], lines[2], lines[3], lines[4], lines[5], lines[6], lines[7]]
							
							f = open(completeName, 'a')
							writer = csv.writer(f)
							writer.writerow(new_boltcard)
							f.close()
							messagebox.showinfo("Information", "Success! Signature (Key ID: " + data_.key_id + ") is good. New Bolt card added.")
							self.add_history("Added Boltcard: " + USER_INP_tr + " (" + USER_INP2_tr + ")")
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

				new_boltcard = [USER_INP_tr, USER_INP2_tr, thedate, lines[0],lines[1],lines[2],lines[3], lines[4], lines[5],lines[6],lines[7]]
				
				f = open(completeName, 'a')
				writer = csv.writer(f)
				writer.writerow(new_boltcard)
				f.close()
				self.add_history("Added Boltcard: " + USER_INP_tr + " (" + USER_INP2_tr + ")")
			else:
				messagebox.showinfo("Information", "There was a problem reading the file! \nMake sure there is exactly eight lines with the required data in the file?")
			
		self.create_Boltcardmeny()
	
	def create_BitcoinWalletmeny(self):
		global filepathdestinationfolder
		
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
		
		pathtobackg = self.get_background_image()
		
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
		pathtobackg = "/home/user1/images/seedsignerbackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		def create_bitcointextbox():
			try:
				f = open("/home/user1/help/boltcardHelp.txt", "r")
				file_content = f.read()
				f.close()
				my_text = ctk.CTkTextbox(right_Frame, width=896, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
				my_text.insert('end', file_content)
			except OSError:
				my_text = ctk.CTkTextbox(right_Frame, width=896, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
				my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
			my_text.configure(state="disabled")
			my_text.place(relx=0.5, rely=0.5, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			
			backButton = ctk.CTkButton(right_Frame, text="Back", text_color="white", fg_color="dark orange", border_width=2, border_color="white", width=90, height=20, font=my_font, command=self.create_BitcoinWalletmeny)
			backButton.place(relx=0.93, rely=0.96, anchor="center")
								
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoWalletimage = str(filepathdestinationfolder) + "/images/btc_wallet_icon.jpg"

			walletimagebutton = ctk.CTkImage(light_image=Image.open(pathtoWalletimage), dark_image=Image.open(pathtoWalletimage), size=(230, 100))
			completeName = str(filepathdestinationfolder) + "/secure/wallets/bitconwallets.csv"
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			counter = 0
			Buttonadd = ctk.CTkButton(right_Frame, text="Add Bitcoin Wallet", text_color="black", fg_color="orange", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.addnewBitcoinwallet)
			Buttonadd.place(relx=0.9, rely=0.05, anchor="center")
			Buttoncreate = ctk.CTkButton(right_Frame, text="Create new Wallet", text_color="black", fg_color="orange", border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.createnewBitcoinwallet)
			Buttoncreate.place(relx=0.9, rely=0.10, anchor="center")
			Buttonmoreinfo = ctk.CTkButton(right_Frame, text="More info", text_color="black", fg_color="dark orange", border_width=2, border_color="white", width=90, height=20, font=my_font, command=create_bitcointextbox)
			Buttonmoreinfo.place(relx=0.93, rely=0.96, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=28, slant="roman", underline=True, overstrike=False)
			infoLabel = ctk.CTkLabel(right_Frame, text="Air-gapped Bitcoin wallets *.", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.03, rely=0.06, anchor="w")
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=True, overstrike=False)
			infoLabel = ctk.CTkLabel(right_Frame, text="Offline device has two options for Bitcoin wallets with SeedQR and air-gapped signing features:", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.03, rely=0.15, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			infoLabel = ctk.CTkLabel(right_Frame, text="1. Add a wallet that's created by a seperate hardware wallet (such as Blockstream Jade):", text_color="white", font=my_font, fg_color="black")
			infoLabel.place(relx=0.03, rely=0.2, anchor="w")
			infoLabel2 = ctk.CTkLabel(right_Frame, text="  - Select \"Setup Jade\" -> \"Advanced setup\" -> \"Create New Wallet\". Select 12 or 24 words.", text_color="white", font=my_font, fg_color="black")
			infoLabel2.place(relx=0.03, rely=0.24, anchor="w")
			infoLabel3 = ctk.CTkLabel(right_Frame, text="  - In the Offline device select \"Add new wallet\" and type in the words Jade gives you. Exact spelling!", text_color="white", font=my_font, fg_color="black")
			infoLabel3.place(relx=0.03, rely=0.28, anchor="w")
			infoLabel4 = ctk.CTkLabel(right_Frame, text="  - Select \"Export CompactSeedQR\". Select \"Draw the CompactSeedQR\". Click past it without drawing it", text_color="white", font=my_font, fg_color="black")
			infoLabel4.place(relx=0.03, rely=0.32, anchor="w")
			infoLabel5 = ctk.CTkLabel(right_Frame, text="   (as it will be auto generated by the Offline device). Choose if you like to add a Passphrase (not recommended).", text_color="white", font=my_font, fg_color="black")
			infoLabel5.place(relx=0.03, rely=0.36, anchor="w")
			infoLabel6 = ctk.CTkLabel(right_Frame, text="  - Select connection type \"QR\". Select \"SeedQR\" to scan a SeedQR every session. Press \"Continue\".", text_color="white", font=my_font, fg_color="black")
			infoLabel6.place(relx=0.03, rely=0.4, anchor="w")
			infoLabel7 = ctk.CTkLabel(right_Frame, text="  - Install Green wallet or Nunchuck wallet etc on your mobile device and/or computer. Make sure there's a camera.", text_color="white", font=my_font, fg_color="black")
			infoLabel7.place(relx=0.03, rely=0.44, anchor="w")
			infoLabel8 = ctk.CTkLabel(right_Frame, text="  - From Jade or Offline device select Show/Export Xpub. Scan or save it and import it to your online device **.", text_color="white", font=my_font, fg_color="black")
			infoLabel8.place(relx=0.03, rely=0.48, anchor="w")
			infoLabel9 = ctk.CTkLabel(right_Frame, text="  - Scan the \"SeedQR\" from the Offline device to import it into Jade. If signing with Offline device then no need.", text_color="white", font=my_font, fg_color="black")
			infoLabel9.place(relx=0.03, rely=0.52, anchor="w")
			infoLabel10 = ctk.CTkLabel(right_Frame, text="2. Create a new wallet on the Offline device. This could have less randomness and be less secure!", text_color="white", font=my_font, fg_color="black")
			infoLabel10.place(relx=0.03, rely=0.6, anchor="w")
			infoLabel11 = ctk.CTkLabel(right_Frame, text="  - Select \"Create new wallet\" in the top right corner. Give the wallet a name and a description.", text_color="white", font=my_font, fg_color="black")
			infoLabel11.place(relx=0.03, rely=0.64, anchor="w")
			infoLabel12 = ctk.CTkLabel(right_Frame, text="  - Click on the new wallet and select \"Show Xpub\". Scan QR or save to file and import to a node connected device **.", text_color="white", font=my_font, fg_color="black")
			infoLabel12.place(relx=0.03, rely=0.68, anchor="w")
			infoLabel13 = ctk.CTkLabel(right_Frame, text="  - Scan the \"SeedQR\" from the Offline device to import it into Jade. If signing with Offline device then no need.", text_color="white", font=my_font, fg_color="black")
			infoLabel13.place(relx=0.03, rely=0.72, anchor="w")
			infoLabel14 = ctk.CTkLabel(right_Frame, text="Scan transaction QR with Jade or Offline device and sign it. Scan signature with node connected device and broadcast it.", text_color="white", font=my_font, fg_color="black")
			infoLabel14.place(relx=0.03, rely=0.76, anchor="w")
			
			proLabel = ctk.CTkLabel(right_Frame, text="* Support Xpub export and transaction signing for Native Segwit and derivation path m/84'/0'/0' (such as Blockstream Jade).", text_color="white", font=my_font, fg_color="black")
			proLabel.place(relx=0.03, rely=0.85, anchor="w")
			proLabel2 = ctk.CTkLabel(right_Frame, text="** A \"node connected device\" is a seperate device that can be without Internet conection and only", text_color="white", font=my_font, fg_color="black")
			proLabel2.place(relx=0.03, rely=0.9, anchor="w")
			proLabel3 = ctk.CTkLabel(right_Frame, text="   have a local network connection to your own node (protects your privacy).", text_color="white", font=my_font, fg_color="black")
			proLabel3.place(relx=0.03, rely=0.95, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)								
			cardLabel = ctk.CTkLabel(left_Frame, text="Bitcoin wallets", text_color="white", font=my_font, fg_color="black").pack(padx=10, pady=8, side= TOP, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			Counting = 0
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
							if Counting == 0:	
								Button1 = ctk.CTkButton(left_Frame, text="", image = walletimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
								Button1.pack(padx=10, pady=10, side= TOP, anchor="w")
								Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
								Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							else:
								Button1 = ctk.CTkButton(left_Frame, text="", image = walletimagebutton, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="brown", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
								Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
								Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
								Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							Counting += 1
			except FileNotFoundError:
				messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		else:
			notOKButton = ctk.CTkButton(right_Frame, text="You are not logged in.", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def addnewBitcoinwallet(self):
		global filepathdestinationfolder
        
		seed_size = "12"
		now = datetime.now() # current date and time
		timeStamp = now.strftime("%m%d%Y%H%M%S")
		
		USER_INP = simpledialog.askstring(title="Name required.", prompt="Name for the new Bitcoin wallet:")
		
		if USER_INP == "" or USER_INP == " ":
			USER_INP = "Wallet" + timeStamp
		
		USER_INP_tr = USER_INP[:30] if len(USER_INP) > 30 else USER_INP
		
		USER_INP2 = simpledialog.askstring(title="Description.", prompt="Description for the new Bicoin wallet (optional):")
		
		if USER_INP2 == "" or USER_INP2 == " ":
			USER_INP2 = "-"
		
		USER_INP2_tr = USER_INP2[:100] if len(USER_INP2) > 100 else USER_INP2
		
		answer = messagebox.askquestion('Question!', 'Is the new wallet with a 12 word seed phrase (answer \"No\" will ask you to insert 24 words).')
		
		if answer == 'yes':
			USER_INP_WORD1 = simpledialog.askstring(title="Seed word 1!", prompt="Enter seed word number 1 (use only small letters):")
			USER_INP_WORD2 = simpledialog.askstring(title="Seed word 2!", prompt="Enter seed word number 2:")
			USER_INP_WORD3 = simpledialog.askstring(title="Seed word 3!", prompt="Enter seed word number 3:")
			USER_INP_WORD4 = simpledialog.askstring(title="Seed word 4!", prompt="Enter seed word number 4:")
			USER_INP_WORD5 = simpledialog.askstring(title="Seed word 5!", prompt="Enter seed word number 5:")
			USER_INP_WORD6 = simpledialog.askstring(title="Seed word 6!", prompt="Enter seed word number 6:")
			USER_INP_WORD7 = simpledialog.askstring(title="Seed word 7!", prompt="Enter seed word number 7:")
			USER_INP_WORD8 = simpledialog.askstring(title="Seed word 8!", prompt="Enter seed word number 8:")
			USER_INP_WORD9 = simpledialog.askstring(title="Seed word 9!", prompt="Enter seed word number 9:")
			USER_INP_WORD10 = simpledialog.askstring(title="Seed word 10!", prompt="Enter seed word number 10:")
			USER_INP_WORD11 = simpledialog.askstring(title="Seed word 11!", prompt="Enter seed word number 11:")
			USER_INP_WORD12 = simpledialog.askstring(title="Seed word 12!", prompt="Enter seed word number 12:")
		else:
			seed_size = "24"
			USER_INP_WORD1 = simpledialog.askstring(title="Seed word 1!", prompt="Enter seed word number 1 (use only small letters):")
			USER_INP_WORD2 = simpledialog.askstring(title="Seed word 2!", prompt="Enter seed word number 2:")
			USER_INP_WORD3 = simpledialog.askstring(title="Seed word 3!", prompt="Enter seed word number 3:")
			USER_INP_WORD4 = simpledialog.askstring(title="Seed word 4!", prompt="Enter seed word number 4:")
			USER_INP_WORD5 = simpledialog.askstring(title="Seed word 5!", prompt="Enter seed word number 5:")
			USER_INP_WORD6 = simpledialog.askstring(title="Seed word 6!", prompt="Enter seed word number 6:")
			USER_INP_WORD7 = simpledialog.askstring(title="Seed word 7!", prompt="Enter seed word number 7:")
			USER_INP_WORD8 = simpledialog.askstring(title="Seed word 8!", prompt="Enter seed word number 8:")
			USER_INP_WORD9 = simpledialog.askstring(title="Seed word 9!", prompt="Enter seed word number 9:")
			USER_INP_WORD10 = simpledialog.askstring(title="Seed word 10!", prompt="Enter seed word number 10:")
			USER_INP_WORD11 = simpledialog.askstring(title="Seed word 11!", prompt="Enter seed word number 11:")
			USER_INP_WORD12 = simpledialog.askstring(title="Seed word 12!", prompt="Enter seed word number 12:")
			USER_INP_WORD13 = simpledialog.askstring(title="Seed word 13!", prompt="Enter seed word number 13:")
			USER_INP_WORD14 = simpledialog.askstring(title="Seed word 14!", prompt="Enter seed word number 14:")
			USER_INP_WORD15 = simpledialog.askstring(title="Seed word 15!", prompt="Enter seed word number 15:")
			USER_INP_WORD16 = simpledialog.askstring(title="Seed word 16!", prompt="Enter seed word number 16:")
			USER_INP_WORD17 = simpledialog.askstring(title="Seed word 17!", prompt="Enter seed word number 17:")
			USER_INP_WORD18 = simpledialog.askstring(title="Seed word 18!", prompt="Enter seed word number 18:")
			USER_INP_WORD19 = simpledialog.askstring(title="Seed word 19!", prompt="Enter seed word number 19:")
			USER_INP_WORD20 = simpledialog.askstring(title="Seed word 20!", prompt="Enter seed word number 20:")
			USER_INP_WORD21 = simpledialog.askstring(title="Seed word 21!", prompt="Enter seed word number 21:")
			USER_INP_WORD22 = simpledialog.askstring(title="Seed word 22!", prompt="Enter seed word number 22:")
			USER_INP_WORD23 = simpledialog.askstring(title="Seed word 23!", prompt="Enter seed word number 23:")
			USER_INP_WORD24 = simpledialog.askstring(title="Seed word 24!", prompt="Enter seed word number 24:")
		
		if seed_size == "12":
			seed_words = USER_INP_WORD1 + ' ' + USER_INP_WORD2 + ' ' + USER_INP_WORD3 + ' ' + USER_INP_WORD4 + ' ' + USER_INP_WORD5 + ' ' + USER_INP_WORD6 + ' ' + USER_INP_WORD7 + ' ' + USER_INP_WORD8 + ' ' + USER_INP_WORD9 + ' ' + USER_INP_WORD10 + ' ' + USER_INP_WORD11 + ' ' + USER_INP_WORD12
		else:
			seed_words = USER_INP_WORD1 + ' ' + USER_INP_WORD2 + ' ' + USER_INP_WORD3 + ' ' + USER_INP_WORD4 + ' ' + USER_INP_WORD5 + ' ' + USER_INP_WORD6 + ' ' + USER_INP_WORD7 + ' ' + USER_INP_WORD8 + ' ' + USER_INP_WORD9 + ' ' + USER_INP_WORD10 + ' ' + USER_INP_WORD11 + ' ' + USER_INP_WORD12 + ' ' + USER_INP_WORD13 + ' ' + USER_INP_WORD14 + ' ' + USER_INP_WORD15 + ' ' + USER_INP_WORD16 + ' ' + USER_INP_WORD17 + ' ' + USER_INP_WORD18 + ' ' + USER_INP_WORD19 + ' ' + USER_INP_WORD20 + ' ' + USER_INP_WORD21 + ' ' + USER_INP_WORD22 + ' ' + USER_INP_WORD23 + ' ' + USER_INP_WORD24
		
		mnemo = Mnemonic("english")
		isValid = mnemo.check(seed_words) # returns a boolean
		password_bool = False
		password = "none"
		answer2 = messagebox.askquestion('Question!', 'Should wallet be without a password (recommended)?')
		if answer2 == 'no':
			password = simpledialog.askstring(title="Password", prompt="Enter password:")
			password_bool = True
					
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		thedate = str(date.today())
		
		if isValid:
			new_bitcoinwallet = [USER_INP_tr, USER_INP2_tr, thedate, seed_words, seed_size, password_bool, password]
			
			if not os.path.isfile(completeName):
				f = open(completeName, 'w')
				writer = csv.writer(f)
				writer.writerow(new_bitcoinwallet)
				f.close()
			else:
				f = open(completeName, 'a')
				writer = csv.writer(f)
				writer.writerow(new_bitcoinwallet)
				f.close()
			
			completeName = str(filepathdestinationfolder) + "/secure/wallets/wallets.txt"
			f2 = open(completeName, 'a')
			
			if password_bool:
				f2.write("\n___________________________________\n\nName: " + USER_INP_tr + "\n\n   Seed words/key: " + seed_words + "\n\n   Password: " + password + "\n\n   Comment: " + USER_INP2_tr + "\n___________________________________")
			else:
				f2.write("\n___________________________________\n\nName: " + USER_INP_tr + "\n\n   Seed words/key: " + seed_words + "\n\n   Comment: " + USER_INP2_tr + "\n___________________________________")
			
			f2.close()
			USER_INP
			self.add_history("Added a new Bitcoin wallet " + USER_INP_tr + " (" + USER_INP2_tr + ")")
		else:
			messagebox.showinfo("Information", "There was a problem with the words.\n\nIt is not a valid Bitcoin wallet seed.\n\n        Please try again.")
		self.create_BitcoinWalletmeny()
	
	def createnewBitcoinwallet(self):
		global filepathdestinationfolder
		
		password_bool = False
		seed_size = "12"
		password = "none"
		USER_INP = " "
		USER_INP2 = "-"
		
		now = datetime.now() # current date and time
		timeStamp = now.strftime("%m%d%Y%H%M%S")
		
		USER_INP = simpledialog.askstring(title="Name required!", prompt="Name for the new Bitcoin wallet:")
		
		if USER_INP == "" or USER_INP == " ":
			USER_INP = "Wallet" + timeStamp
		
		USER_INP_tr = USER_INP[:30] if len(USER_INP) > 30 else USER_INP
		
		USER_INP2 = simpledialog.askstring(title="Description.", prompt="Description for the new Bicoin wallet (optional):")
		
		if USER_INP2 == "" or USER_INP2 == " ":
			USER_INP2 = "-"
		
		USER_INP2_tr = USER_INP[:100] if len(USER_INP2) > 100 else USER_INP2
		
		# Generate mnemonic from bitconlib.mnemonic module 
		mnemgenerator = bitcoinlibMnemonic()
		seed_words = bitcoinlibMnemonic().generate()
		
		answer2 = messagebox.askquestion('Question!', 'Should wallet be without a password (recommended)?')
		if answer2 == 'no':
			password = simpledialog.askstring(title="Password", prompt="Enter password:")
			password_bool = True
					
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		thedate = str(date.today())
		
		new_bitcoinwallet = [USER_INP_tr, USER_INP2_tr, thedate, seed_words, seed_size, password_bool, password]
		
		if not os.path.isfile(completeName):
			f = open(completeName, 'w')
			writer = csv.writer(f)
			writer.writerow(new_bitcoinwallet)
			f.close()
		else:
			f = open(completeName, 'a')
			writer = csv.writer(f)
			writer.writerow(new_bitcoinwallet)
			f.close()
		
		completeName = str(filepathdestinationfolder) + "/secure/wallets/wallets.txt"
		f2 = open(completeName, 'a')
		
		if password_bool:
			f2.write("\n___________________________________\n\nName: " + USER_INP_tr + "\n\n   Seed words/key: " + seed_words + "\n\n   Password: " + password + "\n\n   Comment: " + USER_INP2_tr + "\n___________________________________")
		else:
			f2.write("\n___________________________________\n\nName: " + USER_INP_tr + "\n\n   Seed words/key: " + seed_words + "\n\n   Comment: " + USER_INP2_tr + "\n___________________________________")
		
		f2.close()
		self.add_history("Created new Bitcoin wallet " + USER_INP_tr + " (" + USER_INP2_tr + ")")
		self.create_BitcoinWalletmeny()
		
	def deleteBitcoinwallet(self, cardname):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/wallets/bitconwallets.csv"
		updatedcompleteName = str(filepathdestinationfolder) + "/secure/wallets/updatedbitconwallets.csv"
		with open(completeName, 'r') as source, open(updatedcompleteName, 'w') as result:
			csvreader = csv.reader(source)
			csvwriter = csv.writer(result)
			for row in csv.reader(source):
				try:
					if row[0] == cardname:
						answer = messagebox.askquestion('Important!', 'Are you sure you want to delete this Bitcoin wallet?')
						if answer == 'yes':
							self.add_history("Deleted Bitcoin wallet " + cardname)
						else:
							csvwriter.writerow(row)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updatedcompleteName, completeName)
		os.remove(updatedcompleteName)	
		self.create_BitcoinWalletmeny()
	
	def Save_xPub_to_USB(self, walletname):
		global filepathdestinationfolder
		
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		
		try:
			with open(completeName, 'r') as file:
				csvfile = csv.reader(file)
				for lines in csvfile:
					if lines[0] == walletname:	
						mnemo = Mnemonic("english")
						if lines[5] == "False":
							seed = mnemo.to_seed(lines[3], passphrase="")
						else:
							seed = mnemo.to_seed(lines[3], passphrase=lines[6])
						
						bip32key = BIP32.from_seed(seed)
						#xpub_from_path = bip32key.get_xpub_from_path("m/84h/0h/0h")
						xpub_from_path = bip32key.get_xpub_from_path("m/84'/0'/0'")
						root_xprv = bip32key.get_fingerprint().hex()
						full_Xpub = "[" + str(root_xprv) + "/" + "84'/0'/0']" + xpub_from_path
						
						tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
						time.sleep(2)
						tk.messagebox.showinfo('Information', 'Select the directory for the file.')
						time.sleep(2)
						outputdir = filedialog.askdirectory(initialdir='/media/user1')
						USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt\" will be added automatically):")
						
						c = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
						c.write(full_Xpub)
						c.close()
						messagebox.showinfo('Information', 'File \"' +USER_INP + '.txt\"' + ' has been saved to the USB-device')						
		except FileNotFoundError:
			messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		self.showBitcoinwallet(walletname)
	
	def readQRfromCamera(self, walletname):
		global filepathdestinationfolder
		completeNameQRfile = str(filepathdestinationfolder) + "/secure/wallets/transactiondatafile.psbt"
		if os.path.isfile(completeNameQRfile):
			os.remove(completeNameQRfile)
		subprocess.run(['python scanQR.py'], shell=True)
		self.decodeQRfromCamera(walletname)
	
	def readQRfromCameraToSign(self, fingerprint):
		global filepathdestinationfolder
		completeNameQRfile = str(filepathdestinationfolder) + "/secure/QRsignaturefile.txt"
		if os.path.isfile(completeNameQRfile):
			os.remove(completeNameQRfile)
		subprocess.run(['python scanQRforSigning.py'], shell=True)
		self.signQRfromCamera(fingerprint)
		
	def decodeQRfromCamera(self, walletname):
		global filepathdestinationfolder
		global pathtoloadaddress
		file_content = ''
		transactionfileOK = True
		transactiondatoavailable = False
							
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

		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=644,
		border_width=2,
		border_color="brown",
		fg_color="black"
		)
		right_Frame.place(x=300, y=2, anchor="nw")

		pathtobackg = "/home/user1/images/seedsignerbackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)

		QR_Frame = ctk.CTkFrame(right_Frame, 
		width=400, 
		height=400,
		border_width=2,
		border_color="black",
		fg_color="black"
		)
		QR_Frame.place(x=450, y=300, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		if path_to_USB_secure == 'Secure USB folder is available':
			
			pathtoWalletIconimage = str(filepathdestinationfolder) + "/images/btc_wallet_icon.jpg"
			walleticonimage = ctk.CTkImage(light_image=Image.open(pathtoWalletIconimage), dark_image=Image.open(pathtoWalletIconimage), size=(230, 100))
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[0] == walletname:	
							Button1 = ctk.CTkButton(left_Frame, text="", image = walleticonimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
							Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							
							mnemo = Mnemonic("english")
							if lines[5] == "False":
								mnemonic = lines[3].split()
								passphrase = ""
								ss = Seed(mnemonic=mnemonic, passphrase=passphrase)
							else:
								mnemonic = lines[3].split()
								passphrase = str(lines[6])
								ss = Seed(mnemonic=mnemonic, passphrase=passphrase)
							
							link_to_signature_data = "/home/user1/secure/wallets/transactiondatafile.psbt"
							try:
								f = open(link_to_signature_data, "r")
								file_content = f.read()
								f.close()
								transactiondatoavailable = True
							except OSError:
								print("No file")
							
							if transactiondatoavailable and file_content != "Empty":
								transactionfileOK = True
								
								d = DecodeQR()
								d.add_data(file_content)
								tx = d.get_psbt()
								pp = PSBTParser(p=tx, seed=ss, network="main")
								
								my_font = ctk.CTkFont(family="Arial", size=32, weight="bold", slant="roman", underline=True, overstrike=False)
								mainLabel = ctk.CTkLabel(right_Frame, text="Transaction details:", text_color="orange", font=my_font, fg_color="black")
								mainLabel.place(relx=0.5, rely=0.12, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=26, slant="roman", underline=False, overstrike=False)
								amountLabel = ctk.CTkLabel(right_Frame, text="Total amount:", text_color="white", font=my_font, fg_color="black")
								amountLabel.place(relx=0.36, rely=0.22, anchor="e")
								amountvLabel = ctk.CTkLabel(right_Frame, text=pp.spend_amount, text_color="white", font=my_font, fg_color="black")
								amountvLabel.place(relx=0.7, rely=0.22, anchor="e")
								satsLabel = ctk.CTkLabel(right_Frame, text="sats", text_color="white", font=my_font, fg_color="black")
								satsLabel.place(relx=0.71, rely=0.22, anchor="w")
								feeLabel = ctk.CTkLabel(right_Frame, text="Fee:", text_color="white", font=my_font, fg_color="black")
								feeLabel.place(relx=0.36, rely=0.28, anchor="e")
								feevLabel = ctk.CTkLabel(right_Frame, text=pp.fee_amount, text_color="white", font=my_font, fg_color="black")
								feevLabel.place(relx=0.7, rely=0.28, anchor="e")
								sats2Label = ctk.CTkLabel(right_Frame, text="sats", text_color="white", font=my_font, fg_color="black")
								sats2Label.place(relx=0.71, rely=0.28, anchor="w")
								my_font = ctk.CTkFont(family="Arial", size=26, slant="roman", underline=True, overstrike=False)
								addrLabel = ctk.CTkLabel(right_Frame, text="Receiving address:", text_color="white", font=my_font, fg_color="black")
								addrLabel.place(relx=0.36, rely=0.36, anchor="e")
								my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=False, overstrike=False)
								addrvLabel = ctk.CTkLabel(right_Frame, text=pp.destination_addresses[0], text_color="white", font=my_font, fg_color="black")
								addrvLabel.place(relx=0.76, rely=0.44, anchor="e")
								my_font = ctk.CTkFont(family="Arial Black", size=28, weight="bold", slant="roman", underline=False, overstrike=False)
								signQRButton = ctk.CTkButton(right_Frame, text="SIGN", text_color="white", fg_color="orange", border_width=2, border_color="white", width=200, height=34, font=my_font, command=partial(self.decodeQRfromCamera_step2, walletname))
								signQRButton.place(relx=0.5, rely=0.65, anchor="center")
							else:
								my_font = ctk.CTkFont(family="Arial", size=28, slant="roman", underline=False, overstrike=False)
								pubLabel = ctk.CTkLabel(right_Frame, text="Could not read QR-code", text_color="white", font=my_font, fg_color="black")
								pubLabel.place(relx=0.5, rely=0.46, anchor="center")
							my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
							backButton = ctk.CTkButton(right_Frame, text="Back", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.showBitcoinwallet, walletname))
							backButton.place(relx=0.5, rely=0.96, anchor="center")
							if lines[5] == "True":
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
							else:
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
			except FileNotFoundError:
				messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def decodeQRfromCamera_step2(self, walletname):
		global filepathdestinationfolder
		global pathtoloadaddress
		global cnt
		file_content = ''
		transactionfileOK = True
		transactiondatoavailable = False
		
		def save_signature_to_USB():
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the signature file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (file type \".psbt\" will be added automatically):")
				
			c = open(outputdir + '/' + USER_INP + '.psbt', 'w', encoding='utf-8')
			c.write(file_content)
			c.close()
			messagebox.showinfo('Information', 'Signature file \"' +USER_INP + '.psbt\"' + ' has been saved.')
			self.showBitcoinwallet(walletname)
							
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

		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=644,
		border_width=2,
		border_color="brown",
		fg_color="black"
		)
		right_Frame.place(x=300, y=2, anchor="nw")

		pathtobackg = "/home/user1/images/seedsignerbackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)

		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		if path_to_USB_secure == 'Secure USB folder is available':
			
			pathtoWalletIconimage = str(filepathdestinationfolder) + "/images/btc_wallet_icon.jpg"
			walleticonimage = ctk.CTkImage(light_image=Image.open(pathtoWalletIconimage), dark_image=Image.open(pathtoWalletIconimage), size=(230, 100))
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[0] == walletname:	
							Button1 = ctk.CTkButton(left_Frame, text="", image = walleticonimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
							Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							
							mnemo = Mnemonic("english")
							if lines[5] == "False":
								mnemonic = lines[3]
								password = ""
							else:
								mnemonic = lines[3]
								password = str(lines[6])
							
							link_to_signature_data = "/home/user1/secure/wallets/transactiondatafile.psbt"
							try:
								f = open(link_to_signature_data, "r")
								file_content = f.read()
								f.close()
								transactiondatoavailable = True
							except OSError:
								print("No file")
							
							onemoreButton = ctk.CTkButton(right_Frame, text="Sign another", text_color="black", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.readQRfromCamera, walletname))
							onemoreButton.place(relx=0.5, rely=0.89, anchor="center")
							backButton = ctk.CTkButton(right_Frame, text="Back", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.showBitcoinwallet, walletname))
							backButton.place(relx=0.5, rely=0.96, anchor="center")
							if lines[5] == "True":
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
							else:
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
								
							if transactiondatoavailable and file_content != "Empty":
								transactionfileOK = True
								
								d = DecodeQR()
								
								d.add_data(file_content)
								tx_str = str(d.get_psbt())
								
								seed = bip39.mnemonic_to_seed(mnemonic, password=password)
								root = bip32.HDKey.from_seed(seed, version=NETWORKS["main"]["xprv"])
								
								raw = a2b_base64(tx_str)
								tx2 = psbt.PSBT.parse(raw)
								
								tx2.sign_with(root)
								raw = tx2.serialize()
								
								b64_psbt = b2a_base64(raw)
								
								if b64_psbt[-1:] == b"\n":
									b64_psbt = b64_psbt[:-1]
								
								signed_psbt = b64_psbt.decode("utf-8")
								
								tx_e = psbt.PSBT.parse(a2b_base64(signed_psbt))
								
								e = UrPsbtQrEncoder(psbt=tx_e, qr_density=SettingsConstants.DENSITY__HIGH)
								
								ar_signed_psbt = a2b_base64(signed_psbt)
								ur = make_message_ur(380, ar_signed_psbt)
								encoded_ur = UREncoder.encode(ur)
								
								my_font = ctk.CTkFont(family="Arial", size=28, slant="roman", underline=True, overstrike=False)
								pubLabel = ctk.CTkLabel(right_Frame, text="Signature:", text_color="white", font=my_font, fg_color="black")
								pubLabel.place(relx=0.5, rely=0.06, anchor="center")
									
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
								saveQRButton = ctk.CTkButton(right_Frame, text="Save signature to USB", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=save_signature_to_USB)
								saveQRButton.place(relx=0.5, rely=0.8, anchor="center")
								
								cnt = 0
								# Now to QR encode it for animated QR display
								self.QR_slides(right_Frame, e, walletname)
	
							else:
								my_font = ctk.CTkFont(family="Arial", size=28, slant="roman", underline=False, overstrike=False)
								pubLabel = ctk.CTkLabel(right_Frame, text="Could not read QR-code", text_color="white", font=my_font, fg_color="black")
								pubLabel.place(relx=0.5, rely=0.46, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def QR_slides(self, right_Frame, e, walletname):
		global cnt
		
		QR_Frame = ctk.CTkFrame(right_Frame, 
		width=400, 
		height=400,
		border_width=2,
		border_color="black",
		fg_color="black"
		)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
										
		if cnt <= 30:
			QR_Frame.place(x=450, y=300, anchor="center")
			
			fragment = e.next_part()
			
			pathtosignature = qrcode.make(fragment)
			resize_pathtosignature = pathtosignature.resize((396, 396))
			link_pathtosignature = str(filepathdestinationfolder) + "/secure/wallets/signature.png"
			
			resize_pathtosignature.save(link_pathtosignature)
			
			loadimg = ctk.CTkImage(light_image=Image.open(link_pathtosignature), dark_image=Image.open(link_pathtosignature), size=(396, 396))
			
			Labelpublicimg = ctk.CTkLabel(QR_Frame,  text = "", image = loadimg)
			
			Labelpublicimg.place(relx=0.5, rely=0.49, anchor="center")
			
			cnt += 1
			
			self.update_idletasks()
			time.sleep(0.4)
			self.after(30, self.QR_slides(right_Frame, e, walletname))
		else:
			QR_Frame.place(x=450, y=300, anchor="center")
			
			backButton = ctk.CTkButton(QR_Frame, text="Try Again", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.decodeQRfromCamera_step2, walletname))
			backButton.place(relx=0.5, rely=0.48, anchor="center")
							
	def showXpub(self, walletname):
		global filepathdestinationfolder
		global pathtoloadaddress
						
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
		
		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=644,
		border_width=2,
		border_color="brown",
		fg_color="black"
		)
		right_Frame.place(x=300, y=2, anchor="nw")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoWalletIconimage = str(filepathdestinationfolder) + "/images/btc_wallet_icon.jpg"
			walleticonimage = ctk.CTkImage(light_image=Image.open(pathtoWalletIconimage), dark_image=Image.open(pathtoWalletIconimage), size=(230, 100))
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[0] == walletname:	
							Button1 = ctk.CTkButton(left_Frame, text="", image = walleticonimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
							Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							
							mnemo = Mnemonic("english")
							if lines[5] == "False":
								seed = mnemo.to_seed(lines[3], passphrase="")
							else:
								seed = mnemo.to_seed(lines[3], passphrase=lines[6])
							
							bip32key = BIP32.from_seed(seed)
							#xpub_from_path = bip32key.get_xpub_from_path("m/84h/0h/0h")
							xpub_from_path = bip32key.get_xpub_from_path("m/84'/0'/0'")
							root_xprv = bip32key.get_fingerprint().hex()
							full_Xpub = "[" + str(root_xprv) + "/" + "84'/0'/0']" + xpub_from_path
							load_address = qrcode.make(full_Xpub)
							
							resize_load_address = load_address.resize((300, 300))
							pathtoloadaddress = str(filepathdestinationfolder) + "/secure/wallets/walletseed.png"
							
							resize_load_address.save(pathtoloadaddress)
							
							loadimg = ctk.CTkImage(light_image=Image.open(pathtoloadaddress), dark_image=Image.open(pathtoloadaddress), size=(300, 300))
									
							my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
							nameLabel = ctk.CTkLabel(right_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							nameLabel.place(relx=0.5, rely=0.08, anchor="center")
							
							my_font = ctk.CTkFont(family="Arial", size=24, slant="roman", underline=True, overstrike=False)
							pubLabel = ctk.CTkLabel(right_Frame, text="Xpub:", text_color="white", font=my_font, fg_color="black")
							pubLabel.place(relx=0.5, rely=0.14, anchor="center")
							Labelpublicimg = ctk.CTkLabel(right_Frame,  text = "", image = loadimg)
							Labelpublicimg.place(relx=0.5, rely=0.45, anchor="center")
							
							my_font = ctk.CTkFont(family="Arial", size=12, slant="roman", underline=False, overstrike=False)								
							descrLabel = ctk.CTkLabel(right_Frame, text=xpub_from_path, text_color="white", font=my_font, fg_color="black")
							descrLabel.place(relx=0.5, rely=0.75, anchor="center")
							
							my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
							derivationLabel = ctk.CTkLabel(right_Frame, text="Derivation path: m/84'/0'/0' (native segwit/singlesig)", text_color="white", font=my_font, fg_color="black")
							derivationLabel.place(relx=0.5, rely=0.8, anchor="center")
							
							my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
							saveQRButton = ctk.CTkButton(right_Frame, text="Save Xpub to USB", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.Save_xPub_to_USB, walletname))
							saveQRButton.place(relx=0.5, rely=0.86, anchor="center")
							backButton = ctk.CTkButton(right_Frame, text="Back", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.showBitcoinwallet, walletname))
							backButton.place(relx=0.5, rely=0.94, anchor="center")
							
							if lines[5] == "True":
								my_font = ctk.CTkFont(family="Arial", size=14, weight="bold", slant="roman", underline=True, overstrike=False)
								passwordLabel3 = ctk.CTkLabel(right_Frame, text="External Seed signers need option to ask for passphrase activated!", text_color="orange", font=my_font, fg_color="black")
								passwordLabel3.place(relx=0.5, rely=0.02, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
							else:
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
			except FileNotFoundError:
				messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def showWalletSeed(self, walletname):
		global filepathdestinationfolder
		global pathtoloadaddress
						
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
		
		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=644,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=2, anchor="nw")
		
		pathtobackg = "/home/user1/images/seedsignerbackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoWalletIconimage = str(filepathdestinationfolder) + "/images/btc_wallet_icon.jpg"

			walleticonimage = ctk.CTkImage(light_image=Image.open(pathtoWalletIconimage), dark_image=Image.open(pathtoWalletIconimage), size=(230, 100))
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[0] == walletname:	
							my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
							nameLabel = ctk.CTkLabel(right_Frame, text="Seed for " + lines[0], text_color="white", font=my_font, fg_color="black")
							nameLabel.place(relx=0.5, rely=0.1, anchor="center")
							
							if lines[5] != "False":
								my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
								passwordLabel = ctk.CTkLabel(right_Frame, text="BIP39 Passphrase:", text_color="white", font=my_font, fg_color="black")
								passwordLabel.place(relx=0.84, rely=0.14, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
								passwordLabel2 = ctk.CTkLabel(right_Frame, text=lines[6], text_color="white", font=my_font, fg_color="black")
								passwordLabel2.place(relx=0.84, rely=0.18, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								passwordLabel3 = ctk.CTkLabel(right_Frame, text="External Seed signers need option to ask for passphrase activated!", text_color="orange", font=my_font, fg_color="black")
								passwordLabel3.place(relx=0.5, rely=0.02, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
								
								secret_words = lines[3] + ' ' + lines[6]
								mnemonic_list = secret_words.split()
							else:
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
								bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
								bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
								bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
								bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
								bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
								mnemonic_list = lines[3].split()
								
							Button1 = ctk.CTkButton(left_Frame, text="", image = walleticonimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
							Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							
							# Print out the seed words
							my_font = ctk.CTkFont(family="Arial", size=26, slant="roman", underline=False, overstrike=False)
							if lines[4] == "12":
								seed1 = ctk.CTkLabel(right_Frame, text=mnemonic_list[0], text_color="white", font=my_font, fg_color="black")
								seed1.place(relx=0.36, rely=0.26, anchor="center")
								seed2 = ctk.CTkLabel(right_Frame, text=mnemonic_list[1], text_color="white", font=my_font, fg_color="black")
								seed2.place(relx=0.36, rely=0.34, anchor="center")
								seed3 = ctk.CTkLabel(right_Frame, text=mnemonic_list[2], text_color="white", font=my_font, fg_color="black")
								seed3.place(relx=0.36, rely=0.42, anchor="center")
								seed4 = ctk.CTkLabel(right_Frame, text=mnemonic_list[3], text_color="white", font=my_font, fg_color="black")
								seed4.place(relx=0.36, rely=0.5, anchor="center")
								seed5 = ctk.CTkLabel(right_Frame, text=mnemonic_list[4], text_color="white", font=my_font, fg_color="black")
								seed5.place(relx=0.36, rely=0.58, anchor="center")
								seed6 = ctk.CTkLabel(right_Frame, text=mnemonic_list[5], text_color="white", font=my_font, fg_color="black")
								seed6.place(relx=0.36, rely=0.66, anchor="center")
								
								seed7 = ctk.CTkLabel(right_Frame, text=mnemonic_list[6], text_color="white", font=my_font, fg_color="black")
								seed7.place(relx=0.64, rely=0.26, anchor="center")
								seed8 = ctk.CTkLabel(right_Frame, text=mnemonic_list[7], text_color="white", font=my_font, fg_color="black")
								seed8.place(relx=0.64, rely=0.34, anchor="center")
								seed9 = ctk.CTkLabel(right_Frame, text=mnemonic_list[8], text_color="white", font=my_font, fg_color="black")
								seed9.place(relx=0.64, rely=0.42, anchor="center")
								seed10 = ctk.CTkLabel(right_Frame, text=mnemonic_list[9], text_color="white", font=my_font, fg_color="black")
								seed10.place(relx=0.64, rely=0.5, anchor="center")
								seed11 = ctk.CTkLabel(right_Frame, text=mnemonic_list[10], text_color="white", font=my_font, fg_color="black")
								seed11.place(relx=0.64, rely=0.58, anchor="center")
								seed12 = ctk.CTkLabel(right_Frame, text=mnemonic_list[11], text_color="white", font=my_font, fg_color="black")
								seed12.place(relx=0.64, rely=0.66, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
								backButton = ctk.CTkButton(right_Frame, text="Close", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
								backButton.place(relx=0.5, rely=0.82, anchor="center")
							else:
								seed1 = ctk.CTkLabel(right_Frame, text=mnemonic_list[0], text_color="white", font=my_font, fg_color="black")
								seed1.place(relx=0.36, rely=0.16, anchor="center")
								seed2 = ctk.CTkLabel(right_Frame, text=mnemonic_list[1], text_color="white", font=my_font, fg_color="black")
								seed2.place(relx=0.36, rely=0.22, anchor="center")
								seed3 = ctk.CTkLabel(right_Frame, text=mnemonic_list[2], text_color="white", font=my_font, fg_color="black")
								seed3.place(relx=0.36, rely=0.28, anchor="center")
								seed4 = ctk.CTkLabel(right_Frame, text=mnemonic_list[3], text_color="white", font=my_font, fg_color="black")
								seed4.place(relx=0.36, rely=0.34, anchor="center")
								seed5 = ctk.CTkLabel(right_Frame, text=mnemonic_list[4], text_color="white", font=my_font, fg_color="black")
								seed5.place(relx=0.36, rely=0.4, anchor="center")
								seed6 = ctk.CTkLabel(right_Frame, text=mnemonic_list[5], text_color="white", font=my_font, fg_color="black")
								seed6.place(relx=0.36, rely=0.46, anchor="center")
								
								seed7 = ctk.CTkLabel(right_Frame, text=mnemonic_list[6], text_color="white", font=my_font, fg_color="black")
								seed7.place(relx=0.36, rely=0.52, anchor="center")
								seed8 = ctk.CTkLabel(right_Frame, text=mnemonic_list[7], text_color="white", font=my_font, fg_color="black")
								seed8.place(relx=0.36, rely=0.58, anchor="center")
								seed9 = ctk.CTkLabel(right_Frame, text=mnemonic_list[8], text_color="white", font=my_font, fg_color="black")
								seed9.place(relx=0.36, rely=0.64, anchor="center")
								seed10 = ctk.CTkLabel(right_Frame, text=mnemonic_list[9], text_color="white", font=my_font, fg_color="black")
								seed10.place(relx=0.36, rely=0.7, anchor="center")
								seed11 = ctk.CTkLabel(right_Frame, text=mnemonic_list[10], text_color="white", font=my_font, fg_color="black")
								seed11.place(relx=0.36, rely=0.76, anchor="center")
								seed12 = ctk.CTkLabel(right_Frame, text=mnemonic_list[11], text_color="white", font=my_font, fg_color="black")
								seed12.place(relx=0.36, rely=0.82, anchor="center")
								
								seed13 = ctk.CTkLabel(right_Frame, text=mnemonic_list[12], text_color="white", font=my_font, fg_color="black")
								seed13.place(relx=0.64, rely=0.16, anchor="center")
								seed14 = ctk.CTkLabel(right_Frame, text=mnemonic_list[13], text_color="white", font=my_font, fg_color="black")
								seed14.place(relx=0.64, rely=0.22, anchor="center")
								seed15 = ctk.CTkLabel(right_Frame, text=mnemonic_list[14], text_color="white", font=my_font, fg_color="black")
								seed15.place(relx=0.64, rely=0.28, anchor="center")
								seed16 = ctk.CTkLabel(right_Frame, text=mnemonic_list[15], text_color="white", font=my_font, fg_color="black")
								seed16.place(relx=0.64, rely=0.34, anchor="center")
								seed17 = ctk.CTkLabel(right_Frame, text=mnemonic_list[16], text_color="white", font=my_font, fg_color="black")
								seed17.place(relx=0.64, rely=0.4, anchor="center")
								seed18 = ctk.CTkLabel(right_Frame, text=mnemonic_list[17], text_color="white", font=my_font, fg_color="black")
								seed18.place(relx=0.64, rely=0.46, anchor="center")
								
								seed19 = ctk.CTkLabel(right_Frame, text=mnemonic_list[18], text_color="white", font=my_font, fg_color="black")
								seed19.place(relx=0.64, rely=0.52, anchor="center")
								seed20 = ctk.CTkLabel(right_Frame, text=mnemonic_list[19], text_color="white", font=my_font, fg_color="black")
								seed20.place(relx=0.64, rely=0.58, anchor="center")
								seed21 = ctk.CTkLabel(right_Frame, text=mnemonic_list[20], text_color="white", font=my_font, fg_color="black")
								seed21.place(relx=0.64, rely=0.64, anchor="center")
								seed22 = ctk.CTkLabel(right_Frame, text=mnemonic_list[21], text_color="white", font=my_font, fg_color="black")
								seed22.place(relx=0.64, rely=0.7, anchor="center")
								seed23 = ctk.CTkLabel(right_Frame, text=mnemonic_list[22], text_color="white", font=my_font, fg_color="black")
								seed23.place(relx=0.64, rely=0.76, anchor="center")
								seed24 = ctk.CTkLabel(right_Frame, text=mnemonic_list[23], text_color="white", font=my_font, fg_color="black")
								seed24.place(relx=0.64, rely=0.82, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
								backButton = ctk.CTkButton(right_Frame, text="Close", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
								backButton.place(relx=0.5, rely=0.96, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def showBitcoinwallet(self, walletname):
		global filepathdestinationfolder
		global pathtoloadaddress
		
		def mnemonic_seed_to_binary(seedphrase):
			index = decode_phrase(seedphrase)
			return index
						
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
		
		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(260, 630))
		Label_backg = ctk.CTkLabel(left_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		right_Frame = ctk.CTkFrame(my_Frame, 
		width=900, 
		height=644,
		border_width=2,
		border_color="brown"
		)
		right_Frame.place(x=300, y=2, anchor="nw")
		
		pathtobackg = "/home/user1/images/seedsignerbackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
		
		if path_to_USB_secure == 'Secure USB folder is available':
			pathtoWalletIconimage = str(filepathdestinationfolder) + "/images/btc_wallet_icon.jpg"

			walleticonimage = ctk.CTkImage(light_image=Image.open(pathtoWalletIconimage), dark_image=Image.open(pathtoWalletIconimage), size=(230, 100))
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines[0] == walletname:	
							Button1 = ctk.CTkButton(left_Frame, text="", image = walleticonimage, anchor='center', text_color="white", fg_color="brown", border_width=2, border_color="white", width=220, height=100, font=my_font, command=partial(self.showBitcoinwallet, lines[0]))
							Button1.pack(padx=10, pady=8, side= TOP, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
							Llabel1 = ctk.CTkLabel(left_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
							Llabel1.pack(padx=1, pady=0, side= TOP, anchor="center")
							
							mnemo = Mnemonic("english")
							isValid = mnemo.check(lines[3]) # returns a boolean
							
							if isValid:
								load_address = qrcode.make(mnemonic_seed_to_binary(lines[3]))
								
								resize_load_address = load_address.resize((270, 270))
								pathtoloadaddress = str(filepathdestinationfolder) + "/secure/wallets/walletseed.png"
								
								resize_load_address.save(pathtoloadaddress)
								
								loadimg = ctk.CTkImage(light_image=Image.open(pathtoloadaddress), dark_image=Image.open(pathtoloadaddress), size=(270, 270))
								
								my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
								nameLabel = ctk.CTkLabel(right_Frame, text=lines[0], text_color="white", font=my_font, fg_color="black")
								nameLabel.place(relx=0.5, rely=0.07, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
								pubLabel = ctk.CTkLabel(right_Frame, text="SeedQR:", text_color="white", font=my_font, fg_color="black")
								pubLabel.place(relx=0.5, rely=0.11, anchor="center")
								Labelpublicimg = ctk.CTkLabel(right_Frame,  text = "", image = loadimg)
								Labelpublicimg.place(relx=0.5, rely=0.37, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)

								my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
								warningLabel1 = ctk.CTkLabel(right_Frame, text="!!! ONLY SCAN", text_color="white", font=my_font, fg_color="black")
								warningLabel1.place(relx=0.2, rely=0.30, anchor="center")
								warningLabel2 = ctk.CTkLabel(right_Frame, text="WITH AIR-GAPPED", text_color="white", font=my_font, fg_color="black")
								warningLabel2.place(relx=0.2, rely=0.35, anchor="center")
								warningLabel3 = ctk.CTkLabel(right_Frame, text="SIGNING DEVICE !!!", text_color="white", font=my_font, fg_color="black")
								warningLabel3.place(relx=0.2, rely=0.40, anchor="center")
								warningLabel11 = ctk.CTkLabel(right_Frame, text="!!! ONLY SCAN", text_color="white", font=my_font, fg_color="black")
								warningLabel11.place(relx=0.8, rely=0.30, anchor="center")
								warningLabel22 = ctk.CTkLabel(right_Frame, text="WITH AIR-GAPPED", text_color="white", font=my_font, fg_color="black")
								warningLabel22.place(relx=0.8, rely=0.35, anchor="center")
								warningLabel33 = ctk.CTkLabel(right_Frame, text="SIGNING DEVICE !!!", text_color="white", font=my_font, fg_color="black")
								warningLabel33.place(relx=0.8, rely=0.40, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
								showQRButton = ctk.CTkButton(right_Frame, text="!!!!!   Show Seed   !!!!!", text_color="black", fg_color="dark orange", border_width=2, border_color="white", width=260, height=32, font=my_font, command=partial(self.showWalletSeed, walletname))
								showQRButton.place(relx=0.5, rely=0.62, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=True, overstrike=False)
								dateheadLabel = ctk.CTkLabel(right_Frame, text="Description:", text_color="white", font=my_font, fg_color="black")
								dateheadLabel.place(relx=0.5, rely=0.68, anchor="center")
								my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=False, overstrike=False)								
								descrLabel = ctk.CTkLabel(right_Frame, text=lines[1], text_color="white", font=my_font, fg_color="black")
								descrLabel.place(relx=0.5, rely=0.73, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=False, overstrike=False)
								dateheadLabel = ctk.CTkLabel(right_Frame, text="Created:  " + lines[2], text_color="white", font=my_font, fg_color="black")
								dateheadLabel.place(relx=0.5, rely=0.78, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
								delButton = ctk.CTkButton(right_Frame, text="Delete Wallet", text_color="white", fg_color="brown", border_width=2, border_color="white", width=200, height=34, font=my_font, command=partial(self.deleteBitcoinwallet, walletname))
								delButton.place(relx=0.25, rely=0.86, anchor="center")
								showQRButton = ctk.CTkButton(right_Frame, text="Show Xpub", text_color="black", fg_color="orange", border_width=2, border_color="white", width=200, height=34, font=my_font, command=partial(self.showXpub, walletname))
								showQRButton.place(relx=0.5, rely=0.86, anchor="center")
								# Check if camera is available?
								signQRButton = ctk.CTkButton(right_Frame, text="Sign a transaction", text_color="black", fg_color="dark orange", border_width=2, border_color="white", width=200, height=32, font=my_font, command=partial(self.readQRfromCamera, walletname))
								signQRButton.place(relx=0.75, rely=0.86, anchor="center")
								
								backButton = ctk.CTkButton(right_Frame, text="Back", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_BitcoinWalletmeny)
								backButton.place(relx=0.5, rely=0.94, anchor="center")
								if lines[5] == "True":
									my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
									bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
									bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
									bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
									bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="BIP39 wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
								else:
									my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=True, overstrike=False)
									bitcoinLabel1 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel1.place(relx=0.05, rely=0.03, anchor="w")
									bitcoinLabel2 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel2.place(relx=0.05, rely=0.97, anchor="w")
									bitcoinLabel3 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel3.place(relx=0.95, rely=0.03, anchor="e")
									bitcoinLabel4 = ctk.CTkLabel(right_Frame, text="Bitcoin wallet", text_color="orange", font=my_font, fg_color="black")
									bitcoinLabel4.place(relx=0.95, rely=0.97, anchor="e")
							else:
								my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
								notcorrectLabel = ctk.CTkLabel(right_Frame, text="The wallet is not correct!", text_color="white", font=my_font, fg_color="black")
								notcorrectLabel.place(relx=0.5, rely=0.5, anchor="center")
								
								my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
								backButton = ctk.CTkButton(right_Frame, text="Back", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_BitcoinWalletmeny)
								backButton.place(relx=0.5, rely=0.94, anchor="center")
			except FileNotFoundError:
				messagebox.showinfo("Information", "There are no Bitcoin wallets here yet.")
		else:
			notOKButton = ctk.CTkButton(self, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
														
	def create_DigitalIDbox(self):
		global DigitalID_button_color
		global filepathdestinationfolder
		
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
		
		pathtobackg = self.get_background_image()
		
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
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(896, 646))
		Label_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		pathtoIDimage = str(filepathdestinationfolder) + "/images/DemoID.JPG"

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
		
			emptyButton = ctk.CTkButton(right_Frame, text="There are no digital ID's.", text_color="white", fg_color=DigitalID_button_color, border_width=2, border_color="white", width=150, height=20, font=my_font, command=self.create_DigitalIDmeny)
			emptyButton.place(relx=0.5, rely=0.45, anchor="center")	
	
	def showID(self, IDfingerprint):
		global newIDflag
		global filepathdestinationfolder
		global bg_img
		global resize_QR_address_img
		global IDPhotoImage
		
		newIDflag = False
		non_dup = True
		
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
		
		pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"
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
		
		pathtobackg = "/home/user1/images/vectorIDart.jpg"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(716, 456))
		Label_backg = ctk.CTkLabel(ID_Frame, image=backg, text = "")
		Label_backg.place(relx=0, rely=0, anchor="nw")
		
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
			pathtotemppic2 = filepathdestinationfolder + '/ID.jpg'
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
				
		pathtobackg = "/home/user1/images/vectorIDart.jpg"
		
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
							bg_img = PhotoImage(file=r'/home/user1/images/ID_map.png')
							
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
							
							canvas_map.create_text(30,395, text="(Encryption standard RFC 4880, RSA. Key size 4096 bits)", anchor="nw", font=my_font)							
							
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
							exportKeyButton = ctk.CTkButton(right_Frame, text="Export public ID Key", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=export_key)
							exportKeyButton.place(relx=0.12, rely=0.03, anchor="center")
							exportButton = ctk.CTkButton(right_Frame, text="Export image", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=export_image)
							exportButton.place(relx=0.32, rely=0.03, anchor="center")
							exportButton = ctk.CTkButton(right_Frame, text="Add validation", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=add_validation)
							exportButton.place(relx=0.52, rely=0.03, anchor="center")
							deleteButton = ctk.CTkButton(right_Frame, text="Delete ID", text_color="white", fg_color="brown", border_width=2, border_color="white", width=150, height=32, font=my_font, command=partial(self.do_deleteID, IDfingerprint))
							deleteButton.place(relx=0.72, rely=0.03, anchor="center")
							my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
							valiLabel = ctk.CTkLabel(right_Frame, text="Validating signatures: ", text_color="black", font=my_font, fg_color="old lace")
							valiLabel.place(x=80, y=500, anchor="nw")
							
							gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
							# Get sigs for the selected key
							public_keys = gpg.list_keys(sigs=True)
							
							if newIDflag:
								messagebox.showinfo("Information", "In the terminal window that will open, type \"addphoto\" and hit Enter. Enter name of photo as \"ID.jpg\" and hit Enter. Follow the instructions. Type \"quit\" when finished. To close the terminal window type \"exit\" and hit Enter.")
								pathtopic = filepathdestinationfolder + "/secure/ID/picture" + IDfingerprint + ".jpg"
								pathtotemppic = filepathdestinationfolder + '/ID.jpg'
								pathtotemppic2 = filepathdestinationfolder + '/ID.jpg'
								shutil.copy(pathtopic, pathtotemppic)
								shutil.copy(pathtopic, pathtotemppic2)
								command= 'gpg --edit-key ' + IDfingerprint
								os.system("lxterminal -e 'bash -c \""+command+";bash\"'") 
								ID_Frame.lift()	
								messagebox.showinfo("Information", "In the terminal window that will open, type \"addphoto\" and hit Enter. Enter name of photo as \"ID.jpg\" and hit Enter. Follow the instructions. Type \"quit\" when finished. To close the terminal window type \"exit\" and hit Enter.")
								nextButton = ctk.CTkButton(right_Frame, text="CLICK TO COMPLETE ID!", text_color="white", fg_color="brown", border_width=2, border_color="white", width=180, height=32, font=my_font, command=create_ICON)
								nextButton.place(relx=0.5, rely=0.8, anchor="center")
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
			
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			
			messagebox.showinfo("Information", "Select your picture (.jpg format) for the ID.")
			pathpic = filedialog.askopenfilename(initialdir='/media/user1')
			pathdest = filepathdestinationfolder + "/secure/ID/picture" + decoded_fingerprint + ".jpg"
			shutil.copy(pathpic, pathdest)
			
			new_ID = [
								'Standard ID',
								decoded_fingerprint,
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
						if lines[1] == decoded_fingerprint:
							alreadyThere = True
			if not alreadyThere:
				with open(completeName, 'a') as result:
					csvwriter = csv.writer(result)
					csvwriter.writerow(new_ID)
				newIDflag = True
				self.add_history("Made new ID linked to key: " + decoded_fingerprint)
				self.showID(decoded_fingerprint)
			else:
				tk.messagebox.showinfo('Information', 'There already exists an ID for the selected key."')
				self.create_DigitalIDmeny()
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = self.get_background_image()
				
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
		private_fingerprints_and_aliases = []
		
		for i in private_keys:
			List_fingerprints.append(i['fingerprint'])
							
		List_Sex = ['Male', 'Female']
		
		clicked = StringVar()
		clicked2 = StringVar()
		
		private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
		clicked.set(private_fingerprints_and_aliases[0])
		privatekeysavailable = True
			
		clicked.set(private_fingerprints_and_aliases[0])
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
		
		drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
		drop.config(width=45)
		drop.place(relx=0.66, rely=0.52, anchor="e")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Select birth date:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.28, rely=0.6, anchor="e")
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2025)
		cal.place(relx=0.66, rely=0.6, anchor="e")
		
		Label1 = ctk.CTkLabel(my_Frame, text="Select sex:", font=my_font, text_color="white", fg_color="black")
		Label1.place(relx=0.28, rely=0.68, anchor="e")
		
		drop2 = OptionMenu(my_Frame, clicked2, *List_Sex)
		drop2.place(relx=0.66, rely=0.68, anchor="e")
		
		Button = ctk.CTkButton(my_Frame, text="Create new ID", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=do_newID)
		Button.place(relx=0.55, rely=0.78, anchor="w")
		
	def create_getSettimetextbox(self):
		global PersonalGPGKey
		global filepathdestinationfolder
		global path_to_USB_secure
		global timeSecUSBLastModified
		global System_button_color
		global users_avatar_icon
		global users_avatar_name
		logged_in_user = '< Not logged in >'
		users_theme = 'Standard'
		users_colors = 'Varied'
		users_avatar_name = 'Anon'
		users_avatar_icon = 'Male'
		
		def setdateandtime():
			thedate = cal.get_date()
			thetime = time_picker.time()
			
			thedatestr = str('sudo date -s \'' + str(thedate) + ' ' + str(thetime[0]) + ':' + str(thetime[1]) + ':00\'')			
			os.system(thedatestr)
			thestr = 'sudo hwclock -w'	
			os.system(thestr)
			os.system(thestr)
			self.create_Hometextbox()

		def delete_account():
			global path_to_USB_secure
			global timeSecUSBLastModified
			answer = messagebox.askquestion('WARNING!', 'WARNING! You are about to delete the account! Are you SURE you want to permanently delete it?')
			
			# Delete files and go to start menu
			if answer == 'yes':
				# Delete the personal GPG-key both on local keychain and the file
				path_personalGPGkey = filepathdestinationfolder + '/privateKey' + PersonalGPGKey + '.gpg' 
				cmd = 'shred -zu -n7 ' + path_personalGPGkey
				os.system(cmd)
				
				gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
				# Delete the private key
				try:
					key = gpg.delete_keys(PersonalGPGKey, True, expect_passphrase=False) 
				except ValueError as ve:
					messagebox.showinfo('Information', 'Something went wrong.')
				# Delete the public key
				try:
					key = gpg.delete_keys(PersonalGPGKey) 
				except ValueError as ve:
					messagebox.showinfo('Information', 'Something went wrong.')
					
				# Delete reference in external alias file (if any)
				path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
				updated_path_to_aliases = str(filepathdestinationfolder) + "/Documents/updatedexternalAliases.csv"
				new_alias_data = []
				with open(path_to_externalAliases, 'r') as source, open(updated_path_to_aliases, 'w') as result:
					csvreader = csv.reader(source)
					csvwriter = csv.writer(result)
					for row in csv.reader(source):
						if row[0] != PersonalGPGKey:
							new_alias_data = [
											row[0],
											row[1],
											row[2]]
							csvwriter.writerow(new_alias_data)
				shutil.copy(updated_path_to_aliases, path_to_externalAliases)
				os.remove(updated_path_to_aliases)	
				
				# Delete the secure (unencrypted) folder and the encrypted data file
				path_encrypted_archive = filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg'
				
				full_path = filepathdestinationfolder + "/secure"
				cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
				os.system(cmd)
				cmd = 'rm -r ' +  full_path
				os.system(cmd)
				cmd = 'shred -zu -n7 ' + path_encrypted_archive
				os.system(cmd)
				
				messagebox.showinfo("Information", "The account has been deleted and the personal GPG-key removed from the local keychain.")

				path_to_USB_secure = 'Secure USB folder is not available'
				timeSecUSBLastModified = '<Unknown>'
				self.set_colors('Varied')
				self.create_meny()
			
		def update_account():
			my_Frame.focus_set()
			my_Frame.focus_force()
			
			Updated_Username = nameEntry.get()
			clicked_Theme = clicked.get()
			clicked_Color = clicked2.get()
			clicked_Avatar = clicked3.get()
			new_Avatar_Entry = avatarEntry.get()
			
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
			with open(completeName, 'w') as result:
				csvwriter = csv.writer(result)
				new_settings = [
								Updated_Username,
								clicked_Theme,
								clicked_Color]

				csvwriter.writerow(new_settings)
			self.set_colors(clicked_Color)

			if checkbox.get() == "on":					
				# Make local copy for external alias (in case of recovery on new device)
				new_external_alias = [PersonalGPGKey, new_Avatar_Entry, clicked_Avatar]
				path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
				
				# Check if alias file exists. If not create it
				if not os.path.isfile(path_to_externalAliases):
					if clicked_Avatar == 'Upload my own':
						tk.messagebox.showinfo('Information', 'Connect the USB-device with the avatar picture and click \"OK\".')
						time.sleep(2)
						messagebox.showinfo("Information", "Select the picture for your avatar (\".png\" format)")
						time.sleep(2)
						pathtopicture = filedialog.askopenfilename(initialdir='/media/user1')
						newpicturename = PersonalGPGKey + '.png'
						pathtopicturelocation = filepathdestinationfolder + "/Documents/" + PersonalGPGKey + '.png'
						pathtopicturearchivelocation = filepathdestinationfolder + "/secure/" + PersonalGPGKey + '.png'
						shutil.copy(pathtopicture, pathtopicturelocation)
						shutil.copy(pathtopicture, pathtopicturearchivelocation)
						
						new_external_alias = [PersonalGPGKey, new_Avatar_Entry, newpicturename]
					else:
						new_external_alias = [PersonalGPGKey, new_Avatar_Entry, clicked_Avatar]
					
					f = open(path_to_externalAliases, 'w')
					writer = csv.writer(f)
					writer.writerow(new_external_alias)
					f.close()
					
					with open(path_to_externalAliases_localcopy, 'w') as f:
						writer = csv.writer(f)
						writer.writerow(new_external_alias)
				else:
					updated_path_to_aliases = str(filepathdestinationfolder) + "/Documents/updatedexternalAliases.csv"
					
					if clicked_Avatar == 'Upload my own':
						tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
						time.sleep(2)
						messagebox.showinfo("Information", "Select the picture for your avatar (\".png\" format)")
						time.sleep(2)
						pathtopicture = filedialog.askopenfilename(initialdir='/media/user1')
						newpicturename = PersonalGPGKey + '.png'
						pathtopicturelocation = filepathdestinationfolder + "/Documents/" + PersonalGPGKey + '.png'
						pathtopicturearchivelocation = filepathdestinationfolder + "/secure/" + PersonalGPGKey + '.png'
						shutil.copy(pathtopicture, pathtopicturelocation)
						shutil.copy(pathtopicture, pathtopicturearchivelocation)
						new_external_alias = [PersonalGPGKey, new_Avatar_Entry, newpicturename]
						foundentry = False
						with open(path_to_externalAliases, 'r') as source, open(updated_path_to_aliases, 'w') as result:
							csvreader = csv.reader(source)
							csvwriter = csv.writer(result)
							for row in csv.reader(source):
								if row[0] == PersonalGPGKey:
									csvwriter.writerow(new_external_alias)
									foundentry = True
								else:
									new_alias_data = [
													row[0],
													row[1],
													row[2]]
									csvwriter.writerow(new_alias_data)
						shutil.copy(updated_path_to_aliases, path_to_externalAliases)
						os.remove(updated_path_to_aliases)
						if foundentry == False:
							with open(path_to_externalAliases, 'a') as result:
								csvwriter = csv.writer(result)
								csvwriter.writerow(new_external_alias)
						with open(path_to_externalAliases_localcopy, 'w') as f:
							writer = csv.writer(f)
							writer.writerow(new_external_alias)
					else:
						new_external_alias = [PersonalGPGKey, new_Avatar_Entry, clicked_Avatar]
						foundentry = False
						with open(path_to_externalAliases, 'r') as source, open(updated_path_to_aliases, 'w') as result:
							csvreader = csv.reader(source)
							csvwriter = csv.writer(result)
							for row in csv.reader(source):
								if row[0] == PersonalGPGKey:
									csvwriter.writerow(new_external_alias)
									foundentry = True
								else:
									new_alias_data = [
													row[0],
													row[1],
													row[2]]
									csvwriter.writerow(new_alias_data)
						shutil.copy(updated_path_to_aliases, path_to_externalAliases)
						os.remove(updated_path_to_aliases)
						if foundentry == False:
							with open(path_to_externalAliases, 'a') as result:
								csvwriter = csv.writer(result)
								csvwriter.writerow(new_external_alias)
						with open(path_to_externalAliases_localcopy, 'w') as f:
							writer = csv.writer(f)
							writer.writerow(new_external_alias)
			else:
				updated_path_to_aliases = str(filepathdestinationfolder) + "/Documents/updatedexternalAliases.csv"
				new_alias_data = []
				with open(path_to_externalAliases, 'r') as source, open(updated_path_to_aliases, 'w') as result:
					csvreader = csv.reader(source)
					csvwriter = csv.writer(result)
					for row in csv.reader(source):
						if row[0] != PersonalGPGKey:
							new_alias_data = [
											row[0],
											row[1],
											row[2]]
							csvwriter.writerow(new_alias_data)
				shutil.copy(updated_path_to_aliases, path_to_externalAliases)
				os.remove(updated_path_to_aliases)
			self.create_meny()
		
		def get_avatar_data_if_any():
			global users_avatar_icon
			global users_avatar_name
			external_alias_file = filepathdestinationfolder + "/Documents/externalAliases.csv"	

			# Check if alias file exists.
			if not os.path.isfile(external_alias_file):
				return False
			else:
				try:
					f = open(external_alias_file, 'r')
					for row in csv.reader(f):
						if row[0] == PersonalGPGKey:
							users_avatar_name = row[1]
							users_avatar_icon = row[2]
							return True
					f.close()
				except FileNotFoundError:
					messagebox.showinfo("Information", "No Alias file found.")
			return True
		
		def testCamera():
			subprocess.run(['python testCamera.py'], shell=True)
			
		def checkForCamera():
			# model version 1, 2 and 3
			cmd = 'libcamera-hello --list-cameras | grep -c ov5647'
			result = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE) 
			numberis = int(result.stdout)

			if numberis > 0:
				LabelCam = ctk.CTkLabel(my_Frame, text="Connected camera:", text_color="white", fg_color="black", font=my_font)
				LabelCam.place(relx=0.07, rely=0.81, anchor="w")
				LabelCam2 = ctk.CTkLabel(my_Frame, text="Model:              ov5647", text_color="white", fg_color="black", font=my_font)
				LabelCam2.place(relx=0.07, rely=0.85, anchor="w")
				LabelCam3 = ctk.CTkLabel(my_Frame, text="Resolution:         5 MP", text_color="white", fg_color="black", font=my_font)
				LabelCam3.place(relx=0.07, rely=0.89, anchor="w")
				testButton = ctk.CTkButton(my_Frame, text="Test camera (10 sec)", text_color="white", border_width=2, border_color="white", fg_color="dark green", width=120, height=32, font=my_font, command=testCamera)
				testButton.place(relx=0.07, rely=0.94, anchor="w")
			else:
				cmd = 'libcamera-hello --list-cameras | grep -c imx219'
				result = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE) 
				numberis = int(result.stdout)

				if numberis > 0:
					LabelCam = ctk.CTkLabel(my_Frame, text="Connected camera:", text_color="white", fg_color="black", font=my_font)
					LabelCam.place(relx=0.07, rely=0.81, anchor="w")
					LabelCam2 = ctk.CTkLabel(my_Frame, text="Model:              imx219", text_color="white", fg_color="black", font=my_font)
					LabelCam2.place(relx=0.07, rely=0.85, anchor="w")
					LabelCam3 = ctk.CTkLabel(my_Frame, text="Resolution:         8 MP", text_color="white", fg_color="black", font=my_font)
					LabelCam3.place(relx=0.07, rely=0.89, anchor="w")
					testButton = ctk.CTkButton(my_Frame, text="Test camera (10 sec)", text_color="white", border_width=2, border_color="white", fg_color="dark green", width=120, height=32, font=my_font, command=testCamera)
					testButton.place(relx=0.07, rely=0.94, anchor="w")
				else:
					cmd = 'libcamera-hello --list-cameras | grep -c imx708'
					result = subprocess.run(cmd, shell=True, encoding='utf-8', stdout=subprocess.PIPE) 
					numberis = int(result.stdout)

					if numberis > 0:
						LabelCam = ctk.CTkLabel(my_Frame, text="Connected camera:", text_color="white", fg_color="black", font=my_font)
						LabelCam.place(relx=0.07, rely=0.81, anchor="w")
						LabelCam2 = ctk.CTkLabel(my_Frame, text="Model:               imx708", text_color="white", fg_color="black", font=my_font)
						LabelCam2.place(relx=0.07, rely=0.85, anchor="w")
						LabelCam3 = ctk.CTkLabel(my_Frame, text="Resolution:         12 MP", text_color="white", fg_color="black", font=my_font)
						LabelCam3.place(relx=0.07, rely=0.89, anchor="w")
						testButton = ctk.CTkButton(my_Frame, text="Test camera (10 sec)", text_color="white", border_width=2, border_color="white", fg_color="dark green", width=120, height=32, font=my_font, command=testCamera)
						testButton.place(relx=0.07, rely=0.94, anchor="w")
					else:
						LabelCam = ctk.CTkLabel(my_Frame, text="No camera found.", text_color="white", fg_color="black", font=my_font)
						LabelCam.place(relx=0.07, rely=0.85, anchor="w")
					
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = self.get_background_image()
				
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
		List_Colors = ['Varied', 'Navy blue', 'Green', 'Gray', 'Purple', 'Red', 'Pink']
		List_Avatars = ['Anon', 'Male', 'Woman', 'Boy', 'Girl', 'Yin Yang', 'Skull', 'Upload my own']
		
		clicked = StringVar()
		clicked2 = StringVar()
		clicked3 = StringVar()
		users_avatar = "Male"
		
		clicked.set(users_theme)
		clicked2.set(users_colors)
		clicked3.set(users_avatar)
		check_var = ctk.StringVar(value="on")
		
		def limitSizeAvatarname(*args):
			value = users_avatar_name_var.get()
			if len(value) > 17: users_avatar_name_var.set(value[:17])
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Update account settings:", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.3, rely=0.1, anchor="e")
		
		nameLabel = ctk.CTkLabel(my_Frame, text="User name:", text_color="white", fg_color="black", font=my_font)
		nameLabel.place(relx=0.18, rely=0.24, anchor="e")
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		thelogged_in_user = ctk.StringVar(value=logged_in_user)
		
		nameEntry = ctk.CTkEntry(my_Frame, placeholder_text=logged_in_user, textvariable=thelogged_in_user, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		nameEntry.place(relx=0.2, rely=0.24, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="Select theme:", font=my_font, text_color="white", fg_color="black")
		Label2.place(relx=0.18, rely=0.31, anchor="e")
		
		drop = OptionMenu(my_Frame, clicked, *List_Themes)
		drop.place(relx=0.46, rely=0.31, anchor="e")

		Label3 = ctk.CTkLabel(my_Frame, text="Select color:", font=my_font, text_color="white", fg_color="black")
		Label3.place(relx=0.17, rely=0.38, anchor="e")
		drop2 = OptionMenu(my_Frame, clicked2, *List_Colors)
		drop2.place(relx=0.46, rely=0.38, anchor="e")
		
		checkbox = ctk.CTkCheckBox(my_Frame, text="Add user name to login screen.", font=my_font, variable=check_var, onvalue="on", offvalue="off", text_color="white", fg_color="black")
		checkbox.place(relx=0.34, rely=0.45, anchor="e")
		
		# Get the current avatar name (if any)
		avatars = get_avatar_data_if_any()
		
		clicked3 = ctk.StringVar(value=users_avatar_icon)
		
		Label4 = ctk.CTkLabel(my_Frame, text="Select avatar:", font=my_font, text_color="white", fg_color="black")
		Label4.place(relx=0.18, rely=0.52, anchor="e")
		
		drop = OptionMenu(my_Frame, clicked3, *List_Avatars)
		drop.place(relx=0.46, rely=0.58, anchor="e")
		
		avatarLabel = ctk.CTkLabel(my_Frame, text="Avatar name (used for login):", text_color="white", fg_color="black", font=my_font)
		avatarLabel.place(relx=0.3, rely=0.64, anchor="e")
		
		users_avatar_name_var = ctk.StringVar(value=users_avatar_name)
		users_avatar_name_var.trace('w', limitSizeAvatarname)
						
		avatarEntry = ctk.CTkEntry(my_Frame, placeholder_text=users_avatar_name, textvariable=users_avatar_name_var, width=150, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		avatarEntry.place(relx=0.34, rely=0.64, anchor="w")
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':	
			updateButton = ctk.CTkButton(my_Frame, text="Update account", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=update_account)
			updateButton.place(relx=0.33, rely=0.74, anchor="w")
			deleteButton = ctk.CTkButton(my_Frame, text="Delete account!", text_color="black", fg_color="red", border_width=3, border_color="white", font=my_font, command=delete_account)
			deleteButton.place(relx=0.84, rely=0.91, anchor="e")
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
				
		setLabel = ctk.CTkLabel(my_Frame, text="Set time and date:", text_color="white", fg_color="black", font=my_font)
		setLabel.place(relx=0.68, rely=0.1, anchor="e")
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		time_picker = AnalogPicker(my_Frame, type=constants.HOURS24)
		time_picker.setHours(datetime.now().hour)
		time_picker.setMinutes(datetime.now().minute)
		time_picker.place(relx=0.84, rely=0.21, anchor="ne")
		
		theme = AnalogThemes(time_picker)
		theme.setNavyBlue()
		time_picker.configAnalog(textcolor="#ffffff", bg="#0a0832", bdColor="#000000", headbdcolor="#000000")
		
		year = time.strftime("%Y")
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=int(year))
		cal.place(relx=0.84, rely=0.76, anchor="e")
			
		setButton = ctk.CTkButton(my_Frame, text="Set time/date", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=setdateandtime) 
		setButton.place(relx=0.84, rely=0.84, anchor="e")
			
		softwareButton = ctk.CTkButton(my_Frame, text=" (Update software)", text_color="white", fg_color="black", border_width=2, border_color="black", font=my_font, command=self.updateSoftware) 
		softwareButton.place(relx=0.5, rely=0.86, anchor="center")
		
		HomeButton = ctk.CTkButton(my_Frame, text="Home", text_color="white", border_width=2, border_color="white", fg_color=System_button_color, width=120, height=32, font=my_font, command=self.create_meny)
		HomeButton.place(relx=0.5, rely=0.92, anchor="center")
		
		# Check for cameras
		camButton = ctk.CTkButton(my_Frame, text="Check for camera", text_color="white", fg_color="dark grey", border_width=2, border_color="white", font=my_font, command=checkForCamera) 
		camButton.place(relx=0.07, rely=0.76, anchor="w")
	
	def updateReboot(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global s_width,s_height
		
		my_big_Frame = ctk.CTkFrame(self, 
		width=s_width, 
		height=s_height,
		border_width=1,
		border_color="blue"
		)
		my_big_Frame.place(relx=0.5, rely=0.5, anchor="center")
		
		pathtobackg = "/home/user1/images/black.jpg"
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
			pathupdatescript = pathtempfolder + 'Updatefiles/Update_script.py'
			exec_updatescript = 'python ' + pathupdatescript
			App_source_File = pathtempfolder + '/GUIApp.py'
			App_dest_File = '/home/user1/GUIApp.py'
			
			# Select tar-file with software update
			messagebox.showinfo("Information", "Insert the USB-device with the updated software and then press \"OK\".")
			time.sleep(2)
			messagebox.showinfo("Information", "Select the file with the software update.")
			time.sleep(2)
			pathSoftwarefile = filedialog.askopenfilename(initialdir='/media/user1')
			
			# Open tar-archive and write to temporary directory
			try:
				tar = tarfile.open(pathSoftwarefile) 
				tar.extractall(pathtempfolder)
				tar.close()
				
				if os.path.isfile(pathupdatescript):
					os.system(exec_updatescript)
					self.add_history("Software updated.")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No file found.")
			
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
		
		pathtobackg = self.get_background_image()	
				
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
	
	def get_total_BTC_amount(self):
		completeName = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		amount = 0.0
		SATs_value = 0.0
		try:
			with open(completeName, 'r') as file:
				csvfile = csv.reader(file)
				for lines in csvfile:
					if lines:
						if lines[0] != 'Spent' and lines[0] != 'Timestamp':
							amount = amount + float(lines[5])
		except FileNotFoundError:
			messagebox.showinfo("Information", "No paper wallet file found.")
		
		amount = round(amount, 8)
		
		if amount < 0.01:
			SATs_value = amount * 100000000
			SATs_value_rounded = round(SATs_value, 8)
			
			return SATs_value_rounded
		else:
			
			BTC_value_rounded = round(SATs_value, 8)
			return amount
				
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
			year = time.strftime("%Y")
			
			dateLabel.config(text=weekday + " the " + dayofmonth + " of " + month + ' ' + year)
			dateLabel.after(1000, date)
		def update():
			timeLabel.config(text="New Text")	
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = self.get_background_image()	
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
		
		def display_personal_avatar():		
			# Check if alias file exists.
			foundit = False
			if os.path.isfile(path_to_externalAliases_localcopy):
				with open(path_to_externalAliases_localcopy) as f:
					for row in csv.reader(f):
						if row[0] == PersonalGPGKey:
							if row[2] == 'Anon':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/user_anon.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							elif row[2] == 'Male':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_man.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							elif row[2] == 'Woman':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_woman.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							elif row[2] == 'Boy':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_boy.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							elif row[2] == 'Girl':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_girl.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							elif row[2] == 'Yin Yang':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/user_yinyang.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							elif row[2] == 'Skull':
								pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/user_skull.png"
								avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(100, 100))
								foundit = True
							else:
								pathtoavataricon = str(filepathdestinationfolder) + "/Documents/" + row[2]
								if os.path.isfile(pathtoavataricon):
									avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
									foundit = True
			if foundit:
				avatarButtonpic = ctk.CTkButton(my_Frame, text="", image = avatariconimage, anchor='center', text_color="white", fg_color="black", corner_radius=0, border_width=0, border_color="black", width=80, height=60, font=my_font, command=self.create_getSettimetextbox)
				avatarButtonpic.place(relx=0.92, rely=0.1, anchor='center')
		
		external_alias_file = filepathdestinationfolder + "/Documents/externalAliases.csv"
				
		def display_login_avatars():
			# Check if alias file exists.
			if not os.path.isfile(external_alias_file):
				return False
			else:
				my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
				try:
					with open(external_alias_file) as f:
						nr_avatars = sum(1 for line in f)
				except FileNotFoundError:
					messagebox.showinfo("Information", "No Alias file found.")
				offset2 = 0.35
				offset3 = 0.25
				offset4 = 0.15
				cc = 0
				with open(external_alias_file) as f:
					for row in csv.reader(f):
						if row[2] == 'Anon':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/user_anon.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						elif row[2] == 'Male':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_man.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						elif row[2] == 'Woman':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_woman.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						elif row[2] == 'Boy':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_boy.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						elif row[2] == 'Girl':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/AI_girl.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						elif row[2] == 'Yin Yang':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/user_yinyang.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						elif row[2] == 'Skull':
							pathtoavataricon = str(filepathdestinationfolder) + "/Pictures/user_skull.png"
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
						else:
							pathtoavataricon = str(filepathdestinationfolder) + "/Documents/" + row[2]
							avatariconimage = ctk.CTkImage(light_image=Image.open(pathtoavataricon), dark_image=Image.open(pathtoavataricon), size=(140, 140))
							
						if nr_avatars == 1:
							Buttonpic = ctk.CTkButton(my_Frame, text=row[1], image = avatariconimage, compound=TOP, anchor='center', text_color="white", fg_color="black", corner_radius=0, border_width=0, border_color="black", width=80, height=60, font=my_font, command=partial(self.avatar_decrypt_SecUSB, row[0]))	
							Buttonpic.place(relx=0.5, rely=0.28, anchor='center')
						elif nr_avatars == 2:
							Buttonpic = ctk.CTkButton(my_Frame, text=row[1], image = avatariconimage, compound=TOP, anchor='center', text_color="white", fg_color="black", corner_radius=0, border_width=0, border_color="black", width=80, height=60, font=my_font, command=partial(self.avatar_decrypt_SecUSB, row[0]))	
							Buttonpic.place(relx=offset2, rely=0.28, anchor='center')
							offset2 += 0.3
						elif nr_avatars == 3:
							Buttonpic = ctk.CTkButton(my_Frame, text=row[1], image = avatariconimage, compound=TOP, anchor='center', text_color="white", fg_color="black", corner_radius=0, border_width=0, border_color="black", width=80, height=60, font=my_font, command=partial(self.avatar_decrypt_SecUSB, row[0]))	
							Buttonpic.place(relx=offset3, rely=0.28, anchor='center')
							offset3 += 0.25
						elif nr_avatars > 3 and cc < 4:
							Buttonpic = ctk.CTkButton(my_Frame, text=row[1], image = avatariconimage, compound=TOP, anchor='center', text_color="white", fg_color="black", corner_radius=0, border_width=0, border_color="black", width=80, height=60, font=my_font, command=partial(self.avatar_decrypt_SecUSB, row[0]))	
							Buttonpic.place(relx=offset4, rely=0.28, anchor='center')
							offset4 += 0.23
							cc += 1
				return True		
			
		timeLabel = tk.Label(self, text="", font=("Helvetica", 16), fg="white", bg=main_frame_bg)
		dateLabel = tk.Label(self, text="", font=("Helvetica", 16), fg="white", bg=main_frame_bg)
		
		clock()
		date()
		
		timeLabel.place(relx=0.95, rely=0.94, anchor="e")
		dateLabel.place(relx=0.95, rely=0.97, anchor="e")
		
		if path_to_USB_secure == 'Secure USB folder is available':
		 
			total_amount_BTC = self.get_total_BTC_amount()
			
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
			systemLabel = ctk.CTkLabel(self, text="----------------------------------------------------------------------- System overview ----------------------------------------------------------------------- ", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			systemLabel.place(relx=0.5, rely=0.42, anchor="center")
			Label1 = ctk.CTkLabel(self, text="Bitcoin wallets:", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label1.place(relx=0.47, rely=0.45, anchor="e")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			completeName = filepathdestinationfolder + "/secure/wallets/bitconwallets.csv"
			Counting = 0
			try:
				with open(completeName, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						Counting += 1
						walletname = lines[0]
					if Counting == 1:
						Button1 = ctk.CTkButton(self, text= str(Counting) + "  Bitcoin wallet available", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=partial(self.showBitcoinwallet, walletname))
						Button1.place(relx=0.48, rely=0.45, anchor="w")
					else:
						Button1 = ctk.CTkButton(self, text= str(Counting) + "  Bitcoin wallets available", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=self.create_Bitcoinmeny)
						Button1.place(relx=0.48, rely=0.45, anchor="w")
			except FileNotFoundError:
				Button1 = ctk.CTkButton(self, text= "No wallets added", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=self.create_BitcoinWalletmeny)
				Button1.place(relx=0.48, rely=0.45, anchor="w")
			
			BTCLabel = ctk.CTkLabel(self, text="Bitcoin in singel address wallets:", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			BTCLabel.place(relx=0.47, rely=0.48, anchor="e")
			if total_amount_BTC > 100:
				amountButton = ctk.CTkButton(self, text=str(int(total_amount_BTC)) + ' sats', text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
				amountButton.place(relx=0.48, rely=0.48, anchor="w")
			else:
				amountButton = ctk.CTkButton(self, text=str(total_amount_BTC) + ' BTC', text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
				amountButton.place(relx=0.48, rely=0.48, anchor="w")
		
			Label3 = ctk.CTkLabel(self, text="Secure archive:", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label3.place(relx=0.47, rely=0.51, anchor="e")
			
			Button4 = ctk.CTkButton(self, text="Available", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=self.create_SecUSBmeny)
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
			Button3 = ctk.CTkButton(self, text=answer, text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=partial(self.check_SecUSB, "none"))
			Button3.place(relx=0.48, rely=0.54, anchor="w")
			
			Label5 = ctk.CTkLabel(self, text="Latest modification (history):", text_color="white", fg_color=main_frame_bg_mid, font=my_font)
			Label5.place(relx=0.47, rely=0.57, anchor="e")
			Button5 = ctk.CTkButton(self, text=timeSecUSBLastModified, text_color="white", fg_color=System_button_color, border_width=2, border_color="white", width=250, height=32, font=my_font, command=self.create_historytextbox)
			Button5.place(relx=0.48, rely=0.57, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=44, weight="bold", slant="roman", underline=False, overstrike=False)
			
			iconlock_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconlocked.png"), dark_image=Image.open("/home/user1/images/iconlocked.png"), size=(35, 35))
			iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconopen.png"), dark_image=Image.open("/home/user1/images/iconopen.png"), size=(35, 35))

			LoginButton = ctk.CTkButton(my_Frame, image=iconlock_image, text=" Logout", compound="left", corner_radius=25, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=my_font, command=self.encrypt_SecUSB)
			LoginButton.place(relx=0.5, rely=0.7, anchor="center")
			iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconopen.png"), dark_image=Image.open("/home/user1/images/iconopen.png"), size=(30, 30))
			openlock_Label = ctk.CTkLabel(self, text="", image=iconopen_image, fg_color=main_frame_bg)
			openlock_Label.place(relx=0.02, rely=0.94, anchor="w")
			
			display_personal_avatar()			
		else:
			iconlock_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconlocked.png"), dark_image=Image.open("/home/user1/images/iconlocked.png"), size=(35, 35))
			iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconopen.png"), dark_image=Image.open("/home/user1/images/iconopen.png"), size=(35, 35))
			
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
				if not display_login_avatars():
					LoginButton = ctk.CTkButton(my_Frame, image=iconopen_image, text=" Login", compound="left", corner_radius=25, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=my_font, command=self.decrypt_SecUSB)
					LoginButton.place(relx=0.5, rely=0.35, anchor="center")
				else:
					my_font = ctk.CTkFont(family="Tahoma", size=16, weight="normal", slant="roman", underline=False, overstrike=False)
					otherLoginButton = ctk.CTkButton(my_Frame, text="Other key Login", corner_radius=8, text_color="white", fg_color="black", border_width=1, border_color="white", font=my_font, command=self.decrypt_SecUSB)
					otherLoginButton.place(relx=0.5, rely=0.58, anchor="center")
				
				my_font = ctk.CTkFont(family="Tahoma", size=20, weight="normal", slant="roman", underline=False, overstrike=False)
				LoginButton = ctk.CTkButton(my_Frame, text=" Create new account", corner_radius=15, text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=("Arial", 18), command=self.new_user_account_selection)
				LoginButton.place(relx=0.5, rely=0.51, anchor="center")
				
				iconlock_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconlocked.png"), dark_image=Image.open("/home/user1/images/iconlocked.png"), size=(30, 30))
				closedlock_Label = ctk.CTkLabel(self, text="", image=iconlock_image, fg_color=main_frame_bg)
				closedlock_Label.place(relx=0.02, rely=0.94, anchor="w")
				
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)	
			LoginButton = ctk.CTkButton(my_Frame, text="(Restore from backup)", text_color="white", fg_color='black', corner_radius=0, border_width=3, border_color="black", font=my_font, command=self.restoreFromencrypted_SecUSB)
			LoginButton.place(relx=0.5, rely=0.68, anchor="center")
			
			pathsettingsicon = str(filepathdestinationfolder) + "/images/settings_icon.jpg"
			settingsimage = ctk.CTkImage(light_image=Image.open(pathsettingsicon), dark_image=Image.open(pathsettingsicon), size=(22, 22))
								
			settingspicbutton = ctk.CTkButton(self, text="", image = settingsimage, anchor='center', text_color="black", fg_color="black", corner_radius=0, border_width=0, border_color="black", width=80, height=60, font=my_font, command=self.create_getSettimetextbox)
			settingspicbutton.place(relx=0.98, rely=0.96, anchor='center')
				
	
	def GnuPG_Home(self):		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
		Label_l12 = ctk.CTkLabel(l3_Frame, text="Add subkeys to an existing key.\nIt will create three subkeys at once. Encrypt, sign\nand authenticate.", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		# The first right box
		Label_l1 = ctk.CTkLabel(r1_Frame, text="Backup keys", text_color="light green", fg_color="black", font=my_font)
		Label_l1.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r1_Frame, text="Backup a selected private key and all\nthe public keys on the local keychain to the\ninternal secure archive.", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
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
		Label5 = ctk.CTkLabel(r3_Frame, text="Encrypt/Sign/check", text_color="light green", fg_color="black", font=my_font)
		Label5.place(relx=0.5, rely=0.14, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label_l12 = ctk.CTkLabel(r3_Frame, text="Encrypt files, decrypt files and sign keys or files with\none of the private keys on the local keychain.\nSigning a file will generate a \"detached signature\".", text_color="light green", fg_color="black", anchor="nw", justify=LEFT, font=my_font)
		Label_l12.place(x=7, y=27)
		
	def get_GnuPGKeys(self):		
		my_Frame = ctk.CTkScrollableFrame(self, 
		width=1176, 
		height=634,
		border_width=2,
		border_color="green",
		fg_color="gray1"
		)

		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Key's on the local keychain:", text_color="light green", fg_color="black", font=my_font)
		Label1.pack(padx=25, pady=2, side= TOP, anchor="w")
		
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=True, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="(Encryption standard: RFC 4880. Key size: 4096 bits.)", text_color="light green", fg_color="black", font=my_font)
		Label2.pack(padx=25, pady=2, side= TOP, anchor="w")
		
		Label5 = ctk.CTkLabel(my_Frame, text="Private key's", text_color="light green", fg_color="black", font=my_font)
		Label5.pack(padx=25, pady=5, side= TOP, anchor="w")
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		public_keys = []
		private_keys = []
		
		public_keys = gpg.list_keys()
		private_keys = gpg.list_keys(True)
		mapp = private_keys.key_map

		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		compact_Button = ctk.CTkButton(my_Frame, text="Compact view", text_color="white", fg_color="dark green", border_width=2, border_color="white", height=30, font=my_font, command=self.get_GnuPGKeys_compact)
		compact_Button.place(x=950, y=40, anchor="nw")
		
		if private_keys:	 
			for i in private_keys:
				if self.lookup_Alias_absolut(i['fingerprint']) != "None":			
					my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
					Label = ctk.CTkLabel(my_Frame, text=str(i['uids']) + ' ' + str(i['fingerprint']) + '  (Alias=' + self.lookup_Alias(i['fingerprint']) + ')' + '\n', text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=25, pady=2, side= TOP, anchor="w")
					my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
					remove_Button = ctk.CTkButton(my_Frame, text="Remove alias", text_color="white", fg_color="green", border_width=2, border_color="white", height=30, font=my_font, command=partial(self.remove_Alias, i['fingerprint']))
					remove_Button.pack(pady=0, fill=X, padx=(910,70))
				else:
					my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
					Label = ctk.CTkLabel(my_Frame, text=str(i['uids']) + ' ' + str(i['fingerprint']) + '\n', text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=25, pady=2, side= TOP, anchor="w")
					my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
					add_Button = ctk.CTkButton(my_Frame, text="Add alias", text_color="white", fg_color="green", border_width=2, border_color="white", height=30, font=my_font, command=partial(self.new_Alias, i['fingerprint']))
					add_Button.pack(pady=0, fill=X, padx=(910,70))
						
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

		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=True, overstrike=False)
		
		Label7 = ctk.CTkLabel(my_Frame, text="Public key's", text_color="light green", fg_color="black", font=my_font)
		Label7.pack(padx=25, pady=5, side= TOP, anchor="w")

		if public_keys:
			for i2 in public_keys:
				if self.lookup_Alias_absolut(i2['fingerprint']) != "None":
					if i2['expires']:
						dictofsubkeyinfo2 = int(i2.get("expires")) 
						dateexp2 = int(dictofsubkeyinfo2)
						dt_dateexp2 = datetime.fromtimestamp(dateexp2)
						dt_dateexp_form2  = dt_dateexp2.strftime('%Y-%m-%d')
						my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
						Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']) + ' ' + str(i2['fingerprint']) + ' Expires: ' + dt_dateexp_form2 + '  (Alias=' + self.lookup_Alias(i2['fingerprint']) + ')', text_color="light green", fg_color="black", font=my_font)
						Label.pack(padx=25, pady=2, side= TOP, anchor="w")
						my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
						remove_Button = ctk.CTkButton(my_Frame, text="Remove alias", text_color="white", fg_color="green", border_width=2, border_color="white", height=30, font=my_font, command=partial(self.remove_Alias, i2['fingerprint']))
						remove_Button.pack(pady=0, fill=X, padx=(910,70))
					else:
						my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
						Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']) + ' ' + str(i2['fingerprint']) + ' Expires: <unknown>' + ' (Alias=' + self.lookup_Alias(i2['fingerprint']) + ')', text_color="light green", fg_color="black", font=my_font)
						Label.pack(padx=25, pady=2, side= TOP, anchor="w")
						my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
						remove_Button = ctk.CTkButton(my_Frame, text="Remove alias", text_color="white", fg_color="green", border_width=2, border_color="white", height=30, font=my_font, command=partial(self.remove_Alias, i2['fingerprint']))
						remove_Button.pack(pady=0, fill=X, padx=(910,70))
				else:
					if i2['expires']:
						dictofsubkeyinfo2 = int(i2.get("expires")) 
						dateexp2 = int(dictofsubkeyinfo2)
						dt_dateexp2 = datetime.fromtimestamp(dateexp2)
						dt_dateexp_form2  = dt_dateexp2.strftime('%Y-%m-%d')
						
						my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
						Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']) + ' ' + str(i2['fingerprint']) + ' Expires: ' + dt_dateexp_form2, text_color="light green", fg_color="black", font=my_font)
						Label.pack(padx=25, pady=2, side= TOP, anchor="w")
						my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
						add_Button = ctk.CTkButton(my_Frame, text="Add alias", text_color="white", fg_color="green", border_width=2, border_color="white", height=30, font=my_font, command=partial(self.new_Alias, i2['fingerprint']))
						add_Button.pack(pady=0, fill=X, padx=(910,70))
					else:
						my_font = ctk.CTkFont(family="Arial", size=14, slant="roman", underline=False, overstrike=False)
						Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']) + ' ' + str(i2['fingerprint']) + '  Expires: <unknown>', text_color="light green", fg_color="black", font=my_font)
						Label.pack(padx=25, pady=2, side= TOP, anchor="w")
						my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
						add_Button = ctk.CTkButton(my_Frame, text="Add alias", text_color="white", fg_color="green", border_width=2, border_color="white", height=30, font=my_font, command=partial(self.new_Alias, i2['fingerprint']))
						add_Button.pack(pady=0, fill=X, padx=(910,70))
		else:
			Label = ctk.CTkLabel(my_Frame, text='<empty>', text_color="light green", fg_color="black", font=my_font)
			Label.pack(padx=25, pady=2, side= TOP, anchor="w")
	
	def get_GnuPGKeys_compact(self):		
		my_Frame = ctk.CTkScrollableFrame(self, 
		width=1176, 
		height=634,
		border_width=2,
		border_color="green",
		fg_color="gray1"
		)

		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Key's on the local keychain:", text_color="light green", fg_color="black", font=my_font)
		Label1.pack(padx=5, pady=2, side= TOP, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=True, overstrike=False)
		Label5 = ctk.CTkLabel(my_Frame, text="Private key's", text_color="light green", fg_color="black", font=my_font)
		Label5.pack(padx=5, pady=5, side= TOP, anchor="w")
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		public_keys = []
		private_keys = []
		
		public_keys = gpg.list_keys()
		private_keys = gpg.list_keys(True)
		mapp = private_keys.key_map
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		detailed_Button = ctk.CTkButton(my_Frame, text="Detailed view*", text_color="white", fg_color="dark green", border_width=2, border_color="white", height=30, font=my_font, command=self.get_GnuPGKeys)
		detailed_Button.place(x=950, y=40, anchor="nw")
		
		my_font = ctk.CTkFont(family="Arial", size=14, weight="bold", slant="roman", underline=False, overstrike=False)
		# Info explained
		infoLabel = ctk.CTkLabel(my_Frame,text="* To add and remove aliases etc.", text_color="white", fg_color="black", font=my_font)
		infoLabel.place(x=950, y=80, anchor="nw")
		
		if private_keys:	 
			for i in private_keys:
				my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
				if self.lookup_Alias_absolut(i['fingerprint']) != "None":			
					Label = ctk.CTkLabel(my_Frame, text=self.lookup_Alias(i['fingerprint']), text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=5, pady=2, side= TOP, anchor="w")
				else:
					Label = ctk.CTkLabel(my_Frame, text=str(i['uids']), text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=5, pady=1, side= TOP, anchor="w")
						
				if i['subkeys']: 
					my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			
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
									Label = ctk.CTkLabel(my_Frame, text= '         ' + capacity + '. Expires: ' + dt_dateexp_form + ' (Moved to a Yubikey).', text_color="light green", fg_color="black", font=my_font)
									Label.pack(padx=5, pady=1, side= TOP, anchor="w")
								else:
									Label = ctk.CTkLabel(my_Frame, text= '         ' + capacity + '. Expires: ' + dt_dateexp_form + ' (' + keytype + ').', text_color="light green", fg_color="black", font=my_font)
									Label.pack(padx=5, pady=1, side= TOP, anchor="w")
		else:
			Label = ctk.CTkLabel(my_Frame, text='<empty>', text_color="light green", fg_color="black", font=my_font)
			Label.pack(padx=5, pady=2, side= TOP, anchor="w") 

		my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=True, overstrike=False)
		Label7 = ctk.CTkLabel(my_Frame, text="Public key's", text_color="light green", fg_color="black", font=my_font)
		Label7.pack(padx=5, pady=3, side= TOP, anchor="w")

		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		if public_keys:
			for i2 in public_keys:
				if self.lookup_Alias_absolut(i2['fingerprint']) != "None":
					Label = ctk.CTkLabel(my_Frame, text=self.lookup_Alias(i2['fingerprint']), text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=5, pady=1, side= TOP, anchor="w")
				else:
					Label = ctk.CTkLabel(my_Frame, text=str(i2['uids']), text_color="light green", fg_color="black", font=my_font)
					Label.pack(padx=5, pady=1, side= TOP, anchor="w")
		else:
			Label = ctk.CTkLabel(my_Frame, text='<empty>', text_color="light green", fg_color="black", font=my_font)
			Label.pack(padx=5, pady=1, side= TOP, anchor="w")
			
	def export_subkey(self):
		global clicked_privateKey
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		def do_export_subkey():
			global clicked_privateKey
			
			clicked_privateKey = str(clicked.get())

			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory where you want to save the subkey that will be exported from the local keychain.')
			time.sleep(2)
			
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			command= 'gpg -a -o ' + outputdir + '/privatesubkey' + clicked_privateKey + '.gpg --export-secret-subkeys ' + clicked_privateKey
			os.system(command) 
			tk.messagebox.showinfo('Information', 'Key has been exported.')
			self.add_history("Subkeys exported: " + clicked_privateKey)
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
			Button2.place(relx=0.62, rely=0.5, anchor="w")
		else:
			Label1 = ctk.CTkLabel(my_Frame, text="There are no subkey's to export.", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
						
	def backupGPG_Keys(self):
		global filepathdestinationfolder
		global GPG_button_color
		global PersonalGPGKey
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		def do_backupGPG_Keys():
			clicked_privateKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			
			my_Frame = ctk.CTkFrame(self, 
			width=1200, 
			height=650,
			border_width=4,
			border_color="green"
			)
			my_Frame.place(relx=0.5, rely=0.6, anchor="center")
			
			pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
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
				the_alias = self.lookup_Alias(i['fingerprint'])
				Label = ctk.CTkLabel(my_Frame, text=the_alias, text_color="light green", fg_color="black", font=my_font)
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
			alias_value = self.lookup_Alias(decoded_fingerprint)
			Label = ctk.CTkLabel(my_Frame, text=alias_value, text_color="light green", fg_color="black", font=my_font)
			Label.place(relx=0.05, rely=the_y_value, anchor="w")
			
			ascii_armored_private_key = gpg.export_keys(decoded_fingerprint, True, expect_passphrase=False)
			completeName = filepathdestinationfolder + '/secure/keys/' + 'privateKey' + decoded_fingerprint + '.gpg' 
			f2 = open(completeName, 'w')
			f2.write(ascii_armored_private_key)
			f2.close()
			self.add_history("Made backup for private key: " + decoded_fingerprint)
			if decoded_fingerprint == PersonalGPGKey:
				shutil.copy(completeName, filepathdestinationfolder)
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')	
		private_keys = gpg.list_keys(True)
					
		clicked = StringVar()
			
		List_fingerprints = []
		private_fingerprints_and_aliases = []
		for i in private_keys:
			if i['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(i['fingerprint'])
	
		if path_to_USB_secure == 'Secure USB folder is available' and List_fingerprints:					
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			
			clicked.set(private_fingerprints_and_aliases[0])
			
			my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
			
			Label1 = ctk.CTkLabel(my_Frame, text="Backup a private key and all the public keys on your local keychain to the Secure archive", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.18, anchor="center")	
			
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			Label1 = ctk.CTkLabel(my_Frame, text="Each private key needs to be backup-up seperately.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.24, anchor="center")	
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Label1 = ctk.CTkLabel(my_Frame, text="Select what private key to backup:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.42, rely=0.48, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.43, rely=0.48, anchor="w")
			
			Button = ctk.CTkButton(my_Frame, text="Backup key\'s to the secure archive", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_backupGPG_Keys)
			Button.place(relx=0.57, rely=0.54, anchor="w")
		else:
			Button8 = ctk.CTkButton(self, text="There are no privat keys available. Backup not possible. Add a private key now?", text_color="white", fg_color="green", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.newGPGFull_Key)
			Button8.place(relx=0.5, rely=0.5, anchor="center")
	
	def import_or_export(self):
		global GPG_button_color
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)

		Button6 = ctk.CTkButton(my_Frame, text="Export public key from local keychain to file", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=385, height=35, font=my_font, command=self.exportGPGmypublic)
		Button6.place(relx=0.3, rely=0.2, anchor="center")
		Button7 = ctk.CTkButton(my_Frame, text="Export private key from local keychain to file", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=385, height=35, font=my_font, command=self.exportGPG)
		Button7.place(relx=0.3, rely=0.35, anchor="center")
		Button8 = ctk.CTkButton(my_Frame, text="Export private subkey from local keychain to file", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=385, height=35, font=my_font, command=self.export_subkey)
		Button8.place(relx=0.3, rely=0.5, anchor="center")
		
		Button9 = ctk.CTkButton(my_Frame, text="Import key from file on USB-device", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=385, height=35, font=my_font, command=self.importGPG_Key)
		Button9.place(relx=0.7, rely=0.2, anchor="center")
		Button10 = ctk.CTkButton(my_Frame, text="Import key from file in the Secure archive, e.g\nafter recovering an account from a backup", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=385, height=60, font=my_font, command=self.importGPG_Key_from_archive)
		Button10.place(relx=0.7, rely=0.35, anchor="center")
		
	def newGPGFull_Key(self):
		global PersonalGPGKey
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
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
				self.new_Alias_real_name(key.fingerprint, Real_name.get())
			else:
				input_data = gpg.gen_key_input(key_type='rsa', name_real=Real_name.get(), expire_date='0', key_length='4096', name_email=Name_email.get(), passphrase=Secret_passphrase.get())
				key = gpg.gen_key(input_data)
				self.new_Alias_real_name(key.fingerprint, Real_name.get())
			self.add_history("Added new key: " + Real_name.get() + ", " + key.fingerprint)
			tk.messagebox.showinfo('Information', 'Key has been created.')
			self.get_GnuPGKeys()
			
		def do_deleteGPGkey():
			global clicked_privateKey
			global GPG_button_color
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			clicked_privateKey = clicked.get()
			answer = messagebox.askquestion('WARNING!', 'WARNING! You are about to delete a private key! Are you SURE you want to delete it?')
			
			# Get back from Alias if needed
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			if answer == 'yes':
				try:
					key = gpg.delete_keys(decoded_fingerprint, True, expect_passphrase=False) 
				except ValueError as ve:
					messagebox.showinfo('Information', 'Something went wrong.')

				messagebox.showinfo('Information', 'Private key has been removed.')
				self.add_history("Deleted private key: " + decoded_fingerprint)
				self.get_GnuPGKeys()
			else:
				messagebox.showinfo("Information", "OK. Keeping the private key.")
				self.get_GnuPGKeys()
		
		def do_deletepublicGPGkey():			
			clicked_publicKey = str(clicked2.get())
			# Get back from Alias if needed
			decoded_fingerprint = self.lookup_fingerprint(clicked_publicKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			key = gpg.delete_keys(decoded_fingerprint)
			
			tk.messagebox.showinfo('Information', 'Public key has been removed.')
			self.add_history("Deleted public key: " + decoded_fingerprint)
			self.get_GnuPGKeys()
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
		Label1 = ctk.CTkLabel(my_Frame, text="Add a private key to the local keychain, or remove a public key.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.06, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="The \"Only certify\"-checkbox for a new key should only be checked if it is intended to be used with a Yubikey*.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Remember to make a backup (to the secure archive) for any new private key added to the local keychain!", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.17, anchor="w")
		
		Label4 = ctk.CTkLabel(my_Frame, text="* This will require you to add subkeys afterwards (adding subkeys are found under the \"GPG\"-menu).", text_color="white", fg_color="black", font=my_font)
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
		private_fingerprints_and_aliases = []
		public_fingerprints_and_aliases = []
		
		privatekeysavailable = False
		publickeysavailable = False		
		
		# Extract a list of fingerprints from list from GPG.list keys 
		for nkey in private_keys:
			if nkey['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(nkey['fingerprint'])
			
		if List_fingerprints:
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
					
		for i2 in public_keys:
			if i2['fingerprint'] != PersonalGPGKey:
				List_publicfingerprints.append(i2['fingerprint'])
		
		if List_publicfingerprints:
			public_fingerprints_and_aliases = self.get_Aliases(List_publicfingerprints)
			clicked2.set(public_fingerprints_and_aliases[0])
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
		tButton.place(relx=0.7, rely=0.4, anchor="center")
		checkbox = ctk.CTkCheckBox(my_Frame, text="Only certify *", font=my_font, variable=check_var, onvalue="on", offvalue="off", text_color="white", fg_color="black")
		checkbox.place(relx=0.35, rely=0.46, anchor="w")
		Button = ctk.CTkButton(my_Frame, text="Create new GPG key", font=my_font, text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", command=do_newGPGFull)
		Button.place(relx=0.48, rely=0.51, anchor="w")
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select private key to remove:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.58, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.35, rely=0.58, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Remove private key**", font=my_font, text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", command=do_deleteGPGkey)
			Button2.place(relx=0.58, rely=0.63, anchor="w")
			Label1 = ctk.CTkLabel(my_Frame, text="**Always remove the private key first in a private/public keypair", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.5, rely=0.69, anchor="center")
		if publickeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select public key to remove:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.76, anchor="e")
			drop2 = OptionMenu(my_Frame, clicked2, *public_fingerprints_and_aliases)
			drop2.config(width=45)
			drop2.place(relx=0.35, rely=0.76, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Remove public key**", font=my_font, text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", command=do_deletepublicGPGkey)
			Button2.place(relx=0.59, rely=0.81, anchor="w")
	
	def Nostr_showQR(self, info):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		# Generate QR-code and display on screen
		QR_pic = qrcode.make(info, version=1)
		resize_QR_pic = QR_pic.resize((300, 300))
		pathtoQR_pic = str(filepathdestinationfolder) + "/secure/ID/nostr.png"
		resize_QR_pic.save(pathtoQR_pic)
		loadimg = ctk.CTkImage(light_image=Image.open(pathtoQR_pic), dark_image=Image.open(pathtoQR_pic), size=(300, 300))
		
		Label_info = ctk.CTkLabel(my_Frame, text=info, text_color="white", fg_color="black", font=my_font)
		Label_info.place(relx=0.5, rely=0.1, anchor="center")
		
		Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = loadimg)
		Labelpublicimg.place(relx=0.5, rely=0.4, anchor="center")
		
		back_button = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.Nostr_main)
		back_button.place(relx=0.5, rely=0.88, anchor="center")
	
	def Nostr_Export_Key(self, info):
		global filepathdestinationfolder
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		# Export to USB
		Label_info = ctk.CTkLabel(my_Frame, text="The selected Nostr key will be exported to a file named \"" + info + ".txt\" on the USB-device.", text_color="white", fg_color="black", font=my_font)
		Label_info.place(relx=0.5, rely=0.12, anchor="center")
		
		path_Pri = filepathdestinationfolder + "/secure/ID/" + info + ".txt"
		
		tk.messagebox.showinfo('Information', 'Insert the USB-device and then click \"OK\"."')
		time.sleep(2)
		tk.messagebox.showinfo('Information', 'Select the folder where you want to save the key. MAKE SURE TO DOUBLE CLICK ON THE CONNECTED USB DEVICE."')
		time.sleep(2)
		outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
		shutil.copy(path_Pri, outputdir)
		
		self.add_history("Exported Nostr key: " + info)
		
		back_button = ctk.CTkButton(my_Frame, text="Done!", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.Nostr_main)
		back_button.place(relx=0.5, rely=0.88, anchor="center")
	
	def Export_text_to_file(self, info):
		tk.messagebox.showinfo('Information', 'Insert the USB-device and then click \"OK\"."')
		time.sleep(2)
		tk.messagebox.showinfo('Information', 'Select the folder where you want to save the file. Make sure to double click on the USB-device to select it. Then press \"OK\""')
		time.sleep(2)
		outputdir = filedialog.askdirectory(initialdir='/media/user1')
		full_path = outputdir + '/ChromeExtensionLink.txt'
		
		with open(full_path, 'w') as file:
			file.write(info)
		
		self.Nostr_main()	
		
	def Nostr_New_Pri_Key(self):
		global filepathdestinationfolder
		
		# Generate a new key pair
		nsec = PrivateKey()
		nsec_hex = nsec.hex()
		nsec_bech32 = nsec.bech32()
		npub = nsec.public_key
		
		npub_bech32 = npub.bech32()
		
		def search_and_replace(file_path, search_word, replace_word):
			originals_file_path_device = filepathdestinationfolder + "/Documents/NSD_Nostr_Signing_Device_v2.html"
			originals_file_path_user = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_v2.html"
			originals_dir_path_device = filepathdestinationfolder + "/Documents/NSD Nostr Signing Device v2_files"
			user_dir = filepathdestinationfolder + "/secure/ID/NSD Nostr Signing Device v2_files" 
			
			# First check if this is really the first Nostr key and relevant files needs to be copied to the users secure-folder
			if not os.path.isfile(originals_file_path_user):
				shutil.copy(originals_file_path_device, originals_file_path_user)
				shutil.copytree(originals_dir_path_device, user_dir, dirs_exist_ok=True)
			
			shutil.copy(originals_file_path_user, file_path)
			with open(file_path, 'r') as file:
				file_contents = file.read()

				updated_contents = file_contents.replace(search_word, replace_word)
			with open(file_path, 'w') as file:
				file.write(updated_contents)
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		# Ask for keypair description (optional).
		USER_INP = simpledialog.askstring(title="Optional!", prompt="Enter a description for the public/private keypair:")
		input_size = len(USER_INP)
		if input_size > 42:
			messagebox.showinfo("Information", "The description can be max 42 characters.")
			self.Nostr_New_Pri_Key()
		else:
			c = open(filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key_desciption.txt", 'w')
			c.write(USER_INP)
			c.close()	

		# Create new key pair
		Label_info = ctk.CTkLabel(my_Frame, text="A new primary Nostr key has been created. \nThe key consists of a public key (Npub) and a private key (Nsec):", text_color="white", fg_color="black", font=my_font)
		Label_info.place(relx=0.5, rely=0.12, anchor="center")
		Label_info2 = ctk.CTkLabel(my_Frame, text="The new public key (npub) is:", text_color="white", fg_color="black", font=my_font)
		Label_info2.place(relx=0.5, rely=0.24, anchor="center")
		Label_info3 = ctk.CTkLabel(my_Frame, text=npub_bech32, text_color="white", fg_color="black", font=my_font)
		Label_info3.place(relx=0.5, rely=0.28, anchor="center")
		Label_info4 = ctk.CTkLabel(my_Frame, text="The new private key (nsec) is:", text_color="white", fg_color="black", font=my_font)
		Label_info4.place(relx=0.5, rely=0.36, anchor="center")
		Label_info5 = ctk.CTkLabel(my_Frame, text=nsec_bech32, text_color="white", fg_color="black", font=my_font)
		Label_info5.place(relx=0.5, rely=0.4, anchor="center")
		
		npub_data = str(npub_bech32)
		c = open(filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key.txt", 'w')
		c.write(npub_data)
		c.close()
		nsec_data = str(nsec_hex) + '\n' + str(nsec_bech32)
		c = open(filepathdestinationfolder + "/secure/ID/Nostr_Primary_Nsec_Key.txt", 'w')
		c.write(nsec_data)
		c.close()
		self.add_history("New Nostr key added")
		# Make a new NSD file from template (so it is with correct private HEX-key)
			
		file_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_pri_v2.html"
		search_and_replace(file_path, "hex_key", str(nsec_hex))
			
		back_button = ctk.CTkButton(my_Frame, text="Next", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.Nostr_main)
		back_button.place(relx=0.5, rely=0.88, anchor="center")

	def Nostr_New_Sec_Key(self):
		global filepathdestinationfolder
		
		# Generate a new key pair
		nsec = PrivateKey()
		nsec_hex = nsec.hex()
		nsec_bech32 = nsec.bech32()
		npub = nsec.public_key
		npub_bech32 = npub.bech32()
		
		def search_and_replace(file_path, search_word, replace_word):
			originals_file_path_device = filepathdestinationfolder + "/Documents/NSD_Nostr_Signing_Device_v2.html"
			originals_file_path_user = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_v2.html"
			originals_dir_path_device = filepathdestinationfolder + "/Documents/NSD Nostr Signing Device v2_files"
			user_dir = filepathdestinationfolder + "/secure/ID/NSD Nostr Signing Device v2_files" 
			
			# First check if this is really the first Nostr key and relevant files needs to be copied to the users secure-folder
			if not os.path.isfile(originals_file_path_user):
				shutil.copy(originals_file_path_device, originals_file_path_user)
				shutil.copytree(originals_dir_path_device, user_dir, dirs_exist_ok=True)
			
			shutil.copy(originals_file_path_user, file_path)
			with open(file_path, 'r') as file:
				file_contents = file.read()

				updated_contents = file_contents.replace(search_word, replace_word)
			with open(file_path, 'w') as file:
				file.write(updated_contents)
				
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		# Ask for keypair description (optional).
		USER_INP = simpledialog.askstring(title="Optional!", prompt="Enter a description for the public/private keypair:")
		input_size = len(USER_INP)
		if input_size > 42:
			messagebox.showinfo("Information", "The description can be max 42 characters.")
			self.Nostr_New_Pri_Key()
		else:
			c = open(filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key_desciption.txt", 'w')
			c.write(USER_INP)
			c.close()
			
		# Create new key pair
		Label_info = ctk.CTkLabel(my_Frame, text="A new Secondary Nostr key has been created. \nThe key consists of a public key (Npub) and a private key (Nsec):", text_color="white", fg_color="black", font=my_font)
		Label_info.place(relx=0.5, rely=0.12, anchor="center")
		Label_info2 = ctk.CTkLabel(my_Frame, text="The new public key (npub) is:", text_color="white", fg_color="black", font=my_font)
		Label_info2.place(relx=0.5, rely=0.24, anchor="center")
		Label_info3 = ctk.CTkLabel(my_Frame, text=npub_bech32, text_color="white", fg_color="black", font=my_font)
		Label_info3.place(relx=0.5, rely=0.28, anchor="center")
		Label_info4 = ctk.CTkLabel(my_Frame, text="The new private key (nsec) is:", text_color="white", fg_color="black", font=my_font)
		Label_info4.place(relx=0.5, rely=0.36, anchor="center")
		Label_info5 = ctk.CTkLabel(my_Frame, text=nsec_bech32, text_color="white", fg_color="black", font=my_font)
		Label_info5.place(relx=0.5, rely=0.4, anchor="center")
		
		npub_data = str(npub_bech32)
		c = open(filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key.txt", 'w')
		c.write(npub_data)
		c.close()
		nsec_data = str(nsec_hex) + '\n' + str(nsec_bech32)
		c = open(filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Nsec_Key.txt", 'w')
		c.write(nsec_data)
		c.close()
		self.add_history("New Nostr key added")
		# Make a new NSD file from template (so it is with correct private HEX-key)
			
		file_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_sec_v2.html"
		search_and_replace(file_path, "hex_key", str(nsec_hex))
		
		back_button = ctk.CTkButton(my_Frame, text="Next", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.Nostr_main)
		back_button.place(relx=0.5, rely=0.88, anchor="center")
	
	def Import_Nostr_key(self, key):
		global filepathdestinationfolder
		hex_value = "0x40"
		
		def search_and_replace(file_path, search_word, replace_word):
			originals_file_path_device = filepathdestinationfolder + "/Documents/NSD_Nostr_Signing_Device_v2.html"
			originals_file_path_user = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_v2.html"
			originals_dir_path_device = filepathdestinationfolder + "/Documents/NSD Nostr Signing Device v2_files"
			user_dir = filepathdestinationfolder + "/secure/ID/NSD Nostr Signing Device v2_files" 
			
			# First check if this is really the first Nostr key and relevant files needs to be copied to the users secure-folder
			if not os.path.isfile(originals_file_path_user):
				shutil.copy(originals_file_path_device, originals_file_path_user)
				shutil.copytree(originals_dir_path_device, user_dir, dirs_exist_ok=True)
			
			shutil.copy(originals_file_path_user, file_path)
			with open(file_path, 'r') as file:
				file_contents = file.read()

				updated_contents = file_contents.replace(search_word, replace_word)
			with open(file_path, 'w') as file:
				file.write(updated_contents)
				
		messagebox.showinfo("Information", "Connect the USB-device with the Nostr key.")
		time.sleep(3)
		messagebox.showinfo("Information", "Select key file. It has to be a text file with exactly two lines:\n\nLine 1: the Public key (Npub).\nLine 2: the Private key (Nsec).")
		time.sleep(3)
		filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			
		try:
			lines = open(filepathSourcefile).read().splitlines()
		except IOError:
			messagebox.showinfo("Information", "There was a problem reading the file!")
		if len(lines) == 2:
			npub_value = lines[0]
			nsec_value = lines[1]
			try:
				hex_value = PrivateKey.from_nsec(nsec_value).hex()
			except Exception:
				messagebox.showinfo("Alert", "This not valid Nostr keys!")
				return
			# Ask for keypair description (optional).
			USER_INP = simpledialog.askstring(title="Optional!", prompt="Enter a description for the public/private keypair:")
			input_size = len(USER_INP)
			if input_size > 42:
				messagebox.showinfo("Information", "The description can be max 42 characters.")
				self.Import_Nostr_key(key)

			if key == "Primary":
				# Also include the Hex code to the Nsec (for NSD device)
				c = open(filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key.txt", 'w')
				c.write(npub_value)
				c.close()
				c = open(filepathdestinationfolder + "/secure/ID/Nostr_Primary_Nsec_Key.txt", 'w')
				c.write(str(hex_value) + '\n' + nsec_value)
				c.close()
				c = open(filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key_desciption.txt", 'w')
				c.write(USER_INP)
				c.close()
				# Make a new NSD file from template (so it is with correct private HEX-key)
				file_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_pri_v2.html"
				search_and_replace(file_path, "hex_key", str(hex_value))
		
			if key == "Secondary":
				c = open(filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key.txt", 'w')
				c.write(npub_value)
				c.close()
				c = open(filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Nsec_Key.txt", 'w')
				c.write(str(hex_value) + '\n' + nsec_value)
				c.close()
				c = open(filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key_desciption.txt", 'w')
				c.write(USER_INP)
				c.close()
				# Make a new NSD file from template (so it is with correct private HEX-key)
				file_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_sec_v2.html"
				search_and_replace(file_path, "hex_key", str(hex_value))
		else:
			messagebox.showinfo("Information", "There was a problem reading the file!")
		self.Nostr_main()
	
	def open_webpage_pri(self):
		global filepathdestinationfolder
		file_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_pri_v2.html"
		webbrowser.open_new_tab(file_path)
						
	def open_webpage_sec(self):
		global filepathdestinationfolder
		file_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_sec_v2.html"
		webbrowser.open_new_tab(file_path)
		
	def Nostr_main(self):
		global filepathdestinationfolder
		
		# Read in the value (if any)
		Pri_npub_value = "< Missing >"
		Pri_nsec_value = "< Missing >"
		Sec_npub_value = "< Missing >"
		Sec_nsec_value = "< Missing >"
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
			
		def do_deleteNostrPriKeys():
			answer = messagebox.askquestion('WARNING!', 'WARNING! You are about to delete the Nostr Primary key! Are you SURE you want to delete it?')
			
			if answer == 'yes':
				pri_path = filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key.txt"
				os.remove(pri_path) 
				pri_path = filepathdestinationfolder + "/secure/ID/Nostr_Primary_Nsec_Key.txt"
				os.remove(pri_path)
				pri_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_pri_v2.html"
				os.remove(pri_path)
				pri_path = filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key_desciption.txt"
				if os.path.isfile(pri_path):
					os.remove(pri_path)
				messagebox.showinfo('Information', 'Primary Nostr key has been removed.')
				self.Nostr_main()
			else:
				messagebox.showinfo("Information", "OK. Keeping the private key.")
				self.Nostr_main()
		
		def do_deleteNostrSecKeys():
			answer = messagebox.askquestion('WARNING!', 'WARNING! You are about to delete the Nostr Secondary key! Are you SURE you want to delete it?')
			 
			if answer == 'yes':
				sec_path = filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key.txt"
				os.remove(sec_path) 
				sec_path = filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Nsec_Key.txt"
				os.remove(sec_path)
				sec_path = filepathdestinationfolder + "/secure/ID/NSD_Nostr_Signing_Device_sec_v2.html"
				os.remove(sec_path)
				sec_path = filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key_desciption.txt"
				if os.path.isfile(sec_path):
					os.remove(sec_path)
				messagebox.showinfo('Information', 'Secondary Nostr key has been removed.')
				self.Nostr_main()
			else:
				messagebox.showinfo("Information", "OK. Keeping the private key.")
				self.Nostr_main()
				
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
		Label1 = ctk.CTkLabel(my_Frame, text="Create, import or export Nostr public/private keys.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		Label2 = ctk.CTkLabel(my_Frame, text="Store two seperate Nostr key pairs.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Exporting the public/private key, can be done using QR-code or a USB-device. The private key can also be exported to a NSD *.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.17, anchor="w")
		
		Label4 = ctk.CTkLabel(my_Frame, text="!!! Use caution when handling the private key !!!", text_color="red", fg_color="black", font=my_font)
		Label4.place(relx=0.05, rely=0.22, anchor="w")
		
		Label_footer = ctk.CTkLabel(my_Frame, text="* NSD = Nostr Signing Device. A hardware key that can sign Nostr events. See www.github.com/lnbits/nostr-signing-device.", text_color="white", fg_color="black", font=my_font)
		Label_footer.place(relx=0.1, rely=0.72, anchor="w")
		Label_footer2 = ctk.CTkLabel(my_Frame, text=" Works with Chrome browser running Nostr web clients such as www.Iris.to, www.coracle.social or www.snort.social etc.", text_color="white", fg_color="black", font=my_font)
		Label_footer2.place(relx=0.1, rely=0.78, anchor="w")
		Label_footer3 = ctk.CTkLabel(my_Frame, text=" Browser needs to have the following plugin installed:", text_color="white", fg_color="black", font=my_font)
		Label_footer3.place(relx=0.1, rely=0.84, anchor="w")
		Label_footer4 = ctk.CTkLabel(my_Frame, text="https://chromewebstore.google.com/detail/horse/ogdjeglchjlenflecdcoonkngmmipcoe.", text_color="white", fg_color="black", font=my_font)
		Label_footer4.place(relx=0.14, rely=0.91, anchor="w")
		Export_file_Button = ctk.CTkButton(my_Frame, text="Export Link", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Export_text_to_file, "https://chromewebstore.google.com/detail/horse/ogdjeglchjlenflecdcoonkngmmipcoe"))
		Export_file_Button.place(relx=0.8, rely=0.9, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Pri_Label = ctk.CTkLabel(my_Frame, text="Key description:", font=my_font, text_color="white", fg_color="black")
		Pri_Label.place(relx=0.19, rely=0.29, anchor="e")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="normal", slant="roman", underline=False, overstrike=False)
		Pri_Label2 = ctk.CTkLabel(my_Frame, text="Primary Nostr key (npub):", font=my_font, text_color="white", fg_color="black")
		Pri_Label2.place(relx=0.2, rely=0.35, anchor="e")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Sec_Label = ctk.CTkLabel(my_Frame, text="Key description:", font=my_font, text_color="white", fg_color="black")
		Sec_Label.place(relx=0.19, rely=0.49, anchor="e")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="normal", slant="roman", underline=False, overstrike=False)
		
		Sec_Label2 = ctk.CTkLabel(my_Frame, text="Secondary Nostr key (npub):", font=my_font, text_color="white", fg_color="black")
		Sec_Label2.place(relx=0.2, rely=0.55, anchor="e")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="normal", slant="roman", underline=False, overstrike=False)
		
		# If Nostr primary file is available
		pathtopri_Npub = filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key.txt"
		pathtopri_Npub_description = filepathdestinationfolder + "/secure/ID/Nostr_Primary_Npub_Key_desciption.txt"
		pathtopri_Nsec = filepathdestinationfolder + "/secure/ID/Nostr_Primary_Nsec_Key.txt"
		if os.path.isfile(pathtopri_Npub):
			Pri_npub_description = ' '
			try:
				lines = open(pathtopri_Npub_description).read().splitlines()
				if len(lines) == 1:
					Pri_npub_description = lines[0]
				else:
					print("There was a problem reading the Nostr key description file!")
			except IOError:
				print("There was a problem reading the Nostr key description file!")
			
			try:
				lines = open(pathtopri_Npub).read().splitlines()
				if len(lines) == 1:
					Pri_npub_value = lines[0]
				else:
					messagebox.showinfo("Information", "There was a problem reading the file!")	
			except IOError:
				messagebox.showinfo("Information", "There was a problem reading the file!")
			
			try:
				lines = open(pathtopri_Nsec).read().splitlines()
				if len(lines) == 2:
					Pri_nsec_hexvalue = lines[0]
					Pri_nsec_value = lines[1]
				else:
					messagebox.showinfo("Information", "There was a problem reading the file!")
			except IOError:
				messagebox.showinfo("Information", "There was a problem reading the file!")
			
			my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)		
			Pri_npub_button_descr = ctk.CTkButton(my_Frame, text=Pri_npub_description, font=my_font, anchor="w", width=580, height=25, text_color="white", fg_color="black", border_color="black", border_width=3, command=partial(self.Nostr_showQR, Pri_npub_value))
			Pri_npub_button_descr.place(relx=0.2, rely=0.29, anchor="w")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="normal", slant="roman", underline=False, overstrike=False)
			Pri_npub_button = ctk.CTkButton(my_Frame, text=Pri_npub_value, font=my_font, width=580, height=25, text_color="white", fg_color="blue", border_color="white", border_width=3, command=partial(self.Nostr_showQR, Pri_npub_value))
			Pri_npub_button.place(relx=0.21, rely=0.35, anchor="w")
			
			QR_Button_pri = ctk.CTkButton(my_Frame, text="QR", font=my_font, text_color="white", fg_color="green", width=85, border_width=2, border_color="white", command=partial(self.Nostr_showQR, Pri_npub_value))
			QR_Button_pri.place(relx=0.75, rely=0.35, anchor="center")
			Export_Button_pri = ctk.CTkButton(my_Frame, text="Export", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Nostr_Export_Key, "Nostr_Primary_Npub_Key"))
			Export_Button_pri.place(relx=0.83, rely=0.35, anchor="center")
			Delete_Button_pri = ctk.CTkButton(my_Frame, text="Delete", font=my_font, text_color="white", fg_color="red", width=85, border_width=2, border_color="white", command=do_deleteNostrPriKeys)
			Delete_Button_pri.place(relx=0.91, rely=0.35, anchor="center")
			
			Label = ctk.CTkLabel(my_Frame, text="Secret key (nsec):", font=my_font, text_color="white", fg_color="black")
			Label.place(relx=0.2, rely=0.4, anchor="e")
			Pri_npub_button = ctk.CTkButton(my_Frame, text=Pri_nsec_value, font=my_font, width=580, height=25, text_color="light grey", fg_color="blue", border_color="white", border_width=3, command=partial(self.Nostr_showQR, Pri_nsec_value))
			Pri_npub_button.place(relx=0.21, rely=0.4, anchor="w")
			QR_Button_pri_nsec = ctk.CTkButton(my_Frame, text="QR", font=my_font, text_color="white", fg_color="green", width=85, border_width=2, border_color="white", command=partial(self.Nostr_showQR, Pri_nsec_value))
			QR_Button_pri_nsec.place(relx=0.75, rely=0.4, anchor="center")
			Export_Button_pri_nsec = ctk.CTkButton(my_Frame, text="Export", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Nostr_Export_Key, "Nostr_Primary_Nsec_Key"))
			Export_Button_pri_nsec.place(relx=0.83, rely=0.4, anchor="center")
			if Pri_nsec_hexvalue != "missing":
				NSD_Button_pri = ctk.CTkButton(my_Frame, text="NSD *", font=my_font, text_color="white", fg_color="red", width=85, border_width=2, border_color="white", command=self.open_webpage_pri)
				NSD_Button_pri.place(relx=0.91, rely=0.4, anchor="center")
		else:	
			# If Nostr Primary files are not available
			Pri_npub_button = ctk.CTkButton(my_Frame, text=Pri_npub_value, font=my_font, width=580, height=25, text_color="white", fg_color="blue", border_color="white", border_width=3, command=self.Nostr_New_Pri_Key)
			Pri_npub_button.place(relx=0.21, rely=0.35, anchor="w")
			Export_Button_pri = ctk.CTkButton(my_Frame, text="Create new", font=my_font, text_color="white", fg_color="green", width=85, border_width=2, border_color="white", command=self.Nostr_New_Pri_Key)
			Export_Button_pri.place(relx=0.75, rely=0.35, anchor="center")
			Delete_Button_pri = ctk.CTkButton(my_Frame, text="Import", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Import_Nostr_key, "Primary"))
			Delete_Button_pri.place(relx=0.83, rely=0.35, anchor="center")
		
		pathtosec_Npub = filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key.txt"
		pathtosec_Npub_description = filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Npub_Key_desciption.txt"
		pathtosec_Nsec = filepathdestinationfolder + "/secure/ID/Nostr_Secondary_Nsec_Key.txt"
		
		if os.path.isfile(pathtosec_Npub):
			Sec_npub_description = ''
			try:
				lines = open(pathtosec_Npub_description).read().splitlines()
				if len(lines) == 1:
					Sec_npub_description = lines[0]
				else:
					print("There was a problem reading the Nostr key description file!")
			except IOError:
				print("There was a problem reading the Nostr key description file!")
			try:
				lines = open(pathtosec_Npub).read().splitlines()
				if len(lines) == 1:
					Sec_npub_value = lines[0]
				else:
					messagebox.showinfo("Information", "There was a problem reading the file!")
			except IOError:
				messagebox.showinfo("Information", "There was a problem reading the file!")
			try:
				lines = open(pathtosec_Nsec).read().splitlines()
				if len(lines) == 2:
					Sec_nsec_hexvalue = lines[0]
					Sec_nsec_value = lines[1]
				else:
					messagebox.showinfo("Information", "There was a problem reading the file!")
			except IOError:
				messagebox.showinfo("Information", "There was a problem reading the file!")
			
			my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=True, overstrike=False)	
			Sec_npub_button_descr = ctk.CTkButton(my_Frame, text=Sec_npub_description, font=my_font, anchor="w", width=580, height=25, text_color="white", fg_color="black", border_color="black", border_width=3, command=partial(self.Nostr_showQR, Sec_npub_value))
			Sec_npub_button_descr.place(relx=0.2, rely=0.49, anchor="w")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="normal", slant="roman", underline=False, overstrike=False)
			Sec_npub_button = ctk.CTkButton(my_Frame, text=Sec_npub_value, font=my_font, width=580, height=25, text_color="white", fg_color="blue", border_color="white", border_width=3, command=partial(self.Nostr_showQR, Sec_npub_value))
			Sec_npub_button.place(relx=0.21, rely=0.55, anchor="w")
			
			QR_Button_sec = ctk.CTkButton(my_Frame, text="QR", font=my_font, text_color="white", fg_color="green", width=85, border_width=2, border_color="white", command=partial(self.Nostr_showQR, Sec_npub_value))
			QR_Button_sec.place(relx=0.75, rely=0.55, anchor="center")
			Export_Button_sec = ctk.CTkButton(my_Frame, text="Export", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Nostr_Export_Key, "Nostr_Secondary_Npub_Key"))
			Export_Button_sec.place(relx=0.83, rely=0.55, anchor="center")
			Delete_Button_sec = ctk.CTkButton(my_Frame, text="Delete", font=my_font, text_color="white", fg_color="red", width=85, border_width=2, border_color="white", command=do_deleteNostrSecKeys)
			Delete_Button_sec.place(relx=0.91, rely=0.55, anchor="center")
			
			Label = ctk.CTkLabel(my_Frame, text="Secret key (nsec):", font=my_font, text_color="white", fg_color="black")
			Label.place(relx=0.2, rely=0.6, anchor="e")
			Sec_npub_button = ctk.CTkButton(my_Frame, text=Sec_nsec_value, font=my_font, width=580, height=25, text_color="light grey", fg_color="blue", border_color="white", border_width=3, command=partial(self.Nostr_showQR, Sec_nsec_value))
			Sec_npub_button.place(relx=0.21, rely=0.6, anchor="w")
			QR_Button_sec_nsec = ctk.CTkButton(my_Frame, text="QR", font=my_font, text_color="white", fg_color="green", width=85, border_width=2, border_color="white", command=partial(self.Nostr_showQR, Sec_nsec_value))
			QR_Button_sec_nsec.place(relx=0.75, rely=0.6, anchor="center")
			Export_Button_sec_nsec = ctk.CTkButton(my_Frame, text="Export", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Nostr_Export_Key, "Nostr_Secondary_Nsec_Key"))
			Export_Button_sec_nsec.place(relx=0.83, rely=0.6, anchor="center")
			if Sec_nsec_hexvalue != "missing":
				NSD_Button_sec = ctk.CTkButton(my_Frame, text="NSD *", font=my_font, text_color="white", fg_color="red", width=85, border_width=2, border_color="white", command=self.open_webpage_sec)
				NSD_Button_sec.place(relx=0.91, rely=0.6, anchor="center")	
		else:	
			# If Nostr Secondary files are not available
			Sec_npub_button = ctk.CTkButton(my_Frame, text=Sec_npub_value, font=my_font, width=580, height=25, text_color="white", fg_color="blue", border_color="white", border_width=3, command=self.Nostr_New_Pri_Key)
			Sec_npub_button.place(relx=0.21, rely=0.55, anchor="w")
			Export_Button_sec = ctk.CTkButton(my_Frame, text="Create new", font=my_font, text_color="white", fg_color="green", width=85, border_width=2, border_color="white", command=self.Nostr_New_Sec_Key)
			Export_Button_sec.place(relx=0.75, rely=0.55, anchor="center")
			Delete_Button_sec = ctk.CTkButton(my_Frame, text="Import", font=my_font, text_color="white", fg_color="blue", width=85, border_width=2, border_color="white", command=partial(self.Import_Nostr_key, "Secondary"))
			Delete_Button_sec.place(relx=0.83, rely=0.55, anchor="center")	
			
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
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
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
			
			Button3 = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="black", border_width=2, border_color="white", font=my_font, command=self.setup_Yubikey_v2)
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
		
		Label2 = ctk.CTkLabel(my_Frame, text="Make sure that your Yubikey 5 NFC is connected.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.12, anchor="w")
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button1 = ctk.CTkButton(my_Frame, text="Reset OpenPGP", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=resetOpenPGPYubikey)
		Button1.place(relx=0.5, rely=0.25, anchor="center")
		
		Button2 = ctk.CTkButton(my_Frame, text="Reset Passkey", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=resetFIDOYubikey)
		Button2.place(relx=0.5, rely=0.3, anchor="center")
		
		Button3 = ctk.CTkButton(my_Frame, text="Change name", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changeNameYubikey)
		Button3.place(relx=0.5, rely=0.35, anchor="center")
		
		Button4 = ctk.CTkButton(my_Frame, text="Change PINs OpenPGP", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changePINsopenpgpYubikey)
		Button4.place(relx=0.5, rely=0.4, anchor="center")
		
		FIDOLabel = ctk.CTkLabel(my_Frame, text="New Passkey PIN (min 6 digits):", text_color="white", fg_color="black", font=my_font)
		FIDOLabel.place(relx=0.15, rely=0.45, anchor="w")
		
		NEWPINLabel = ctk.CTkLabel(my_Frame, text="New PIN:", text_color="white", fg_color="black", font=my_font)
		NEWPINLabel.place(relx=0.35, rely=0.5, anchor="e")
		
		newFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8,font=my_font)
		newFIDOPIN.place(relx=0.35, rely=0.5, anchor="w")
		
		newPINButton = ctk.CTkButton(my_Frame, text="New Passkey PIN", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=newPINFIDOYubikey)
		newPINButton.place(relx=0.55, rely=0.55, anchor="center")

		FIDOLabel_ = ctk.CTkLabel(my_Frame, text="Change Passkey PIN (min 6 digits, default PIN 123456):", text_color="white", fg_color="black", font=my_font)
		FIDOLabel_.place(relx=0.15, rely=0.6, anchor="w")
		
		FIDOLabel2 = ctk.CTkLabel(my_Frame, text="Current PIN:", text_color="white", fg_color="black", font=my_font)
		FIDOLabel2.place(relx=0.34, rely=0.65, anchor="e")
		
		currentFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		currentFIDOPIN.place(relx=0.35, rely=0.65, anchor="w")
		
		CHANGEDPINLabel = ctk.CTkLabel(my_Frame, text="New PIN:", text_color="white", fg_color="black", font=my_font)
		CHANGEDPINLabel.place(relx=0.34, rely=0.7, anchor="e")
		
		changedFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		changedFIDOPIN.place(relx=0.35, rely=0.7, anchor="w")
		
		tPINButton = ctk.CTkButton(my_Frame, text="Change Passkey PIN", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changePINFIDOYubikey)
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
	
	def setup_Yubikey_v2(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
		autPolicy = ctk.StringVar(value="off")
		encPolicy = ctk.StringVar(value="off")
		sigPolicy = ctk.StringVar(value="off")
		
		config_data_textbox = ctk.CTkTextbox(my_Frame, width=500, height=160, corner_radius=1, border_width=3, border_color="red", border_spacing=10, fg_color="white", text_color="black", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="purple", scrollbar_button_hover_color="red")
		OpenPGP_configuration_data_textbox = ctk.CTkTextbox(my_Frame, width=500, height=160, corner_radius=1, border_width=3, border_color="red", border_spacing=10, fg_color="white", text_color="black", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="purple", scrollbar_button_hover_color="red")
		OpenPGP_credential_data_textbox = ctk.CTkTextbox(my_Frame, width=800, height=190, corner_radius=1, border_width=3, border_color="red", border_spacing=10, fg_color="white", text_color="black", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="purple", scrollbar_button_hover_color="red")

		def resetFIDOYubikey():
			# Reset the FIDO on the Yubikey
			tk.messagebox.showinfo('Information', 'Warning! A Passkey cant be restored. Make sure you have another Passkey registered at relevant services in order to not be locked out of accounts.\n\nConnect the Yubikey and then press "OK"')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			command= 'ykman fido reset'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
		
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
			
			goButton = ctk.CTkButton(my_Frame, text="Finish", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.setup_Yubikey_v2)
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
			
			goButton = ctk.CTkButton(my_Frame, text="Finish", text_color="black", fg_color="pink", border_width=2, border_color="white", font=my_font, command=self.setup_Yubikey_v2)
			goButton.place(relx=0.5, rely=0.8, anchor="center")
			
		def setautTouchYubikey():
			# Set aut touch policy on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window that will open.\n\nAfter resetting the OpenPGP on the Yubikey type "exit" and hit enter to close the terminal window.')
			if autPolicyCheckBox.get() == 'on':
				command= 'ykman openpgp keys set-touch aut on'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			else:
				command= 'ykman openpgp keys set-touch aut off'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
			
		def setencTouchYubikey():
			# Set enc touch policy on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			if encPolicyCheckBox.get() == 'on':
				command= 'ykman openpgp keys set-touch enc on'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			else:
				command= 'ykman openpgp keys set-touch enc off'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
			
		def setsigTouchYubikey():
			# Set sig touch policy on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'Follow the instructions in the terminal window.\n\nType "exit" and hit enter to close the terminal window.')
			if sigPolicyCheckBox.get() == 'on':
				command= 'ykman openpgp keys set-touch sig on'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			else:
				command= 'ykman openpgp keys set-touch sig off'
				os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
				
		def changeNameYubikey():
			# Set the PINs, name and email on the Yubikey
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			my_font = ctk.CTkFont(family="Tahoma", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
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
			
			Button3 = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="black", border_width=2, border_color="white", font=my_font, command=self.setup_Yubikey_v2)
			Button3.place(relx=0.5, rely=0.55, anchor="center")
		
		def enableUSB():
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'See terminal window for information.\n\nType "exit" and hit enter to close the terminal window.')
			
			command= 'ykman config usb --enable-all'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
			
		def enableNFC():
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'See terminal window for information.\n\nType "exit" and hit enter to close the terminal window.')
			
			command= 'ykman config nfc --enable-all'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
			
		def disableNFC():
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'See terminal window for information.\n\nType "exit" and hit enter to close the terminal window.')
			
			command= 'ykman config nfc --disable-all'
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
			
		def changePINFIDOYubikey():
			# Reset the FIDO on the Yubikey
			tk.messagebox.showinfo('Information', 'Connect the Yubikey and then press "OK". If already connected, first remove and re-connect the Yubikey.')
			time.sleep(3)
			tk.messagebox.showinfo('Information', 'See terminal window for information.\n\nType "exit" and hit enter to close the terminal window.')
			
			command= 'ykman fido access change-pin --pin ' +  currentFIDOPIN.get() + ' --new-pin ' + changedFIDOPIN.get()
			os.system("lxterminal -e 'bash -c \""+command+";bash\"'")
			self.setup_Yubikey_v2()
		
		def get_config_data():
			try:
				backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
				dev = usb.core.find(..., backend=backend)
				yubikey = yubico.find_yubikey(debug=False)
				config_data = subprocess.getoutput("ykman info")
				return config_data
			except yubico.yubico_exception.YubicoError as e:
				return e.reason
				
		def get_OpenPGP_configuration_data():
			try:
				backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
				dev = usb.core.find(..., backend=backend)
				yubikey = yubico.find_yubikey(debug=False)
				OpenPGP_configuration_data = subprocess.getoutput("ykman openpgp info")
				return OpenPGP_configuration_data
			except yubico.yubico_exception.YubicoError as e:
				return e.reason
				
		def get_OpenPGP_credential_data():
			try:
				backend = usb.backend.libusb1.get_backend(find_library=lambda x: "/usr/lib/libusb-1.0.so")
				dev = usb.core.find(..., backend=backend)
				yubikey = yubico.find_yubikey(debug=False)
				OpenPGP_credential_data = subprocess.getoutput("gpg --card-status")
				return OpenPGP_credential_data
			except yubico.yubico_exception.YubicoError as e:
				return e.reason
				
		def refreshData():
			config_data_textbox.configure(state="normal")
			OpenPGP_configuration_data_textbox.configure(state="normal")
			OpenPGP_credential_data_textbox.configure(state="normal")
			config_data_textbox.delete('1.0', END)
			config_data_textbox.insert('end', get_config_data())
			OpenPGP_configuration_data_textbox.delete('1.0', END)
			OpenPGP_configuration_data_textbox.insert('end', get_OpenPGP_configuration_data())
			OpenPGP_credential_data_textbox.delete('1.0', END)
			OpenPGP_credential_data_textbox.insert('end', get_OpenPGP_credential_data())
			config_data_textbox.configure(state="disabled")
			OpenPGP_configuration_data_textbox.configure(state="disabled")
			OpenPGP_credential_data_textbox.configure(state="disabled")
			
			config_data_textbox.place(relx=0.94, rely=0.1, anchor="ne")
			OpenPGP_configuration_data_textbox.place(relx=0.94, rely=0.4, anchor="ne")
			OpenPGP_credential_data_textbox.place(relx=0.94, rely=0.7, anchor="ne")
		
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
				
		Label1 = ctk.CTkLabel(my_Frame, text="Setup Yubikey.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.04, rely=0.04, anchor="w")
		
		Label2 = ctk.CTkLabel(my_Frame, text="Make sure that your Yubikey 5 NFC is connected.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.04, rely=0.09, anchor="w")
		
		refreshButton = ctk.CTkButton(my_Frame, text="Refresh", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=self.setup_Yubikey_v2)
		refreshButton.place(relx=0.88, rely=0.05, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		usbButton = ctk.CTkButton(my_Frame, text="Enable USB", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=enableUSB)
		usbButton.place(relx=0.26, rely=0.14, anchor="center")
		nfcEnableButton = ctk.CTkButton(my_Frame, text="Enable NFC", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=enableNFC)
		nfcEnableButton.place(relx=0.35, rely=0.14, anchor="w")
		nfcDisableButton = ctk.CTkButton(my_Frame, text="Disable NFC", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=disableNFC)
		nfcDisableButton.place(relx=0.35, rely=0.19, anchor="w")
		
		Labelconfig = ctk.CTkLabel(my_Frame, text="Yubikey config.:", text_color="white", fg_color="black", font=my_font)
		Labelconfig.place(relx=0.52, rely=0.05, anchor="nw")
		LabelOpenPGPconfig = ctk.CTkLabel(my_Frame, text="OpenPGP config.:", text_color="white", fg_color="black", font=my_font)
		LabelOpenPGPconfig.place(relx=0.52, rely=0.35, anchor="nw")
		Labelconfig = ctk.CTkLabel(my_Frame, text="Credentials for OpenPGP:", text_color="white", fg_color="black", font=my_font)
		Labelconfig.place(relx=0.52, rely=0.65, anchor="nw")
		
		refreshData()
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
		OpenPGPLabel = ctk.CTkLabel(my_Frame, text="Passkey:", text_color="white", fg_color="black", font=my_font)
		OpenPGPLabel.place(relx=0.05, rely=0.23, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		FIDOLabel_ = ctk.CTkLabel(my_Frame, text="Passkey PIN (min 6 digits, default PIN 123456):", text_color="white", fg_color="black", font=my_font)
		FIDOLabel_.place(relx=0.05, rely=0.28, anchor="w")
		
		FIDOLabel2 = ctk.CTkLabel(my_Frame, text="Current PIN:", text_color="white", fg_color="black", font=my_font)
		FIDOLabel2.place(relx=0.2, rely=0.32, anchor="e")
		
		currentFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		currentFIDOPIN.place(relx=0.21, rely=0.32, anchor="w")
		
		CHANGEDPINLabel = ctk.CTkLabel(my_Frame, text="New PIN:", text_color="white", fg_color="black", font=my_font)
		CHANGEDPINLabel.place(relx=0.2, rely=0.37, anchor="e")
		
		changedFIDOPIN = ctk.CTkEntry(my_Frame, placeholder_text="******", show='*', width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
		changedFIDOPIN.place(relx=0.21, rely=0.37, anchor="w")
		
		Button2 = ctk.CTkButton(my_Frame, text="Reset Passkey", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=resetFIDOYubikey)
		Button2.place(relx=0.26, rely=0.43, anchor="center")
		
		tPINButton = ctk.CTkButton(my_Frame, text="Change Passkey PIN", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changePINFIDOYubikey)
		tPINButton.place(relx=0.48, rely=0.43, anchor="e")
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
		OpenPGPLabel = ctk.CTkLabel(my_Frame, text="OpenPGP:", text_color="white", fg_color="black", font=my_font)
		OpenPGPLabel.place(relx=0.05, rely=0.51, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		autPolicyCheckBox = ctk.CTkCheckBox(my_Frame, text="Touch policy for Auth (uncheck = policy Off):", variable=autPolicy, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		autPolicyCheckBox.place(relx=0.05, rely=0.56, anchor="w")
		autButton = ctk.CTkButton(my_Frame, text="Set policy", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=setautTouchYubikey)
		autButton.place(relx=0.48, rely=0.56, anchor="e")
		
		encPolicyCheckBox = ctk.CTkCheckBox(my_Frame, text="Touch policy for Encr (uncheck = policy Off):", variable=encPolicy, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		encPolicyCheckBox.place(relx=0.05, rely=0.6, anchor="w")
		encButton = ctk.CTkButton(my_Frame, text="Set policy", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=setencTouchYubikey)
		encButton.place(relx=0.48, rely=0.6, anchor="e")
		
		sigPolicyCheckBox = ctk.CTkCheckBox(my_Frame, text="Touch policy for Sign (uncheck = policy Off):", variable=sigPolicy, onvalue="on", offvalue="off", text_color="white", fg_color="black", font=my_font)
		sigPolicyCheckBox.place(relx=0.05, rely=0.64, anchor="w")
		sigButton = ctk.CTkButton(my_Frame, text="Set policy", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=setsigTouchYubikey)
		sigButton.place(relx=0.48, rely=0.64, anchor="e")
		
		Button3 = ctk.CTkButton(my_Frame, text="Change OpenPGP name", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changeNameYubikey)
		Button3.place(relx=0.06, rely=0.77, anchor="w")
		
		Button4 = ctk.CTkButton(my_Frame, text="Change PINs OpenPGP", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=changePINsopenpgpYubikey)
		Button4.place(relx=0.06, rely=0.83, anchor="w")
		
		Button1 = ctk.CTkButton(my_Frame, text="Reset OpenPGP appli.", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=resetOpenPGPYubikey)
		Button1.place(relx=0.06, rely=0.89, anchor="w")
			
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
		
		pathtobackg = "/home/user1/images/Yubikey5CBackground.JPG"
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
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			
			# Make a backup of the key before moving the subkeys			
			# Export the private key and write to file in /home/user1/secure/keys
			key_file_path = filepathdestinationfolder + '/secure/keys/privateKey' + decoded_fingerprint + '.gpg'
			ascii_armored_private_key = gpg.export_keys(decoded_fingerprint, True, expect_passphrase=False)
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
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			
			command= 'gpg --edit-key ' + decoded_fingerprint
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
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			# Delete the secret key with snubbed (moved) subkeys from the local keychain
			key = gpg.delete_keys(decoded_fingerprint, True, expect_passphrase=False)
			file_path = filepathdestinationfolder + '/secure/keys/privateKey' + decoded_fingerprint + '.gpg'
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
			Button7 = ctk.CTkButton(self, text="Create a new user account", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.new_secureUSB_Pre)
			Button7.place(relx=0.5, rely=0.6, anchor="center")
		else:	
			Label1 = ctk.CTkLabel(my_Frame, text="Add subkeys to a Yubikey. IMPORTANT. Make sure there is a backup available for the secret key before moving the subkeys.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.05, rely=0.07, anchor="w")
			
			Label2 = ctk.CTkLabel(my_Frame, text="Select from what key to move subkey's.", text_color="white", fg_color="black", font=my_font)
			Label2.place(relx=0.05, rely=0.12, anchor="w")
			
			Label2 = ctk.CTkLabel(my_Frame, text="There are three subkeys that will be moved to the Yubikey. Password is needed for each.", text_color="white", fg_color="black", font=my_font)
			Label2.place(relx=0.05, rely=0.17, anchor="w")
			
			Label2 = ctk.CTkLabel(my_Frame, text="Toggle a key on (and off) with command \"Key 1\" and \"Key 2\" etc and then \"Encryption\", \"Signature\" and \"Authentication\".", text_color="white", fg_color="black", font=my_font)
			Label2.place(relx=0.05, rely=0.22, anchor="w")
			
			private_keys = gpg.list_keys(True)
					
			clicked = StringVar()
				
			List_fingerprints = []
			private_fingerprints_and_aliases = []
				
			for i in private_keys:
				List_fingerprints.append(i['fingerprint'])
				
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)	
			
			clicked.set(private_fingerprints_and_aliases[0])
			
			my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
			
			Label1 = ctk.CTkLabel(my_Frame, text="Make sure your Yubikey is connected.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.38, anchor="center")	
			
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Label1 = ctk.CTkLabel(my_Frame, text="Select what key to move subkey\'s from:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.42, rely=0.48, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.43, rely=0.48, anchor="w")
			
			Button = ctk.CTkButton(my_Frame, text="Move subkey\'s to Yubikey", text_color="white", fg_color="brown", border_width=2, border_color="white", font=my_font, command=do_add_subkey_Yubikey)
			Button.place(relx=0.63, rely=0.54, anchor="w")
							
	def newGPG_Subkey(self):		
		global PersonalGPGKey
		global GPG_button_color
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_newGPGSubkey():
			global clicked_privateSubKey
			
			clicked_privateSubKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateSubKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			key = gpg.add_subkey(decoded_fingerprint, algorithm='rsa4096', usage='sign', expire=combo.get())
			key = gpg.add_subkey(decoded_fingerprint, algorithm='rsa4096', usage='encrypt', expire=combo.get())
			key = gpg.add_subkey(decoded_fingerprint, algorithm='rsa4096', usage='auth', expire=combo.get())
			
			# Make a backup with the new supkeys
			privatekeyfilename = 'privateKey' + clicked_privateSubKey + ".gpg"
			full_path_private = "/home/user1/secure/keys/" + privatekeyfilename
			
			ascii_armored_private_key = gpg.export_keys(clicked_privateSubKey, True, expect_passphrase=False)
			
			f2 = open(full_path_private, 'w')
			f2.write(ascii_armored_private_key)
			f2.close()
			
			tk.messagebox.showinfo('Information', 'Subkey\'s has been added to local keychain.\nA new backup of the key has been placed in the secure archive.')
			self.add_history("Added new subkeys to key: " + decoded_fingerprint)
			self.get_GnuPGKeys()
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Create subkeys.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.1, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="\"Encryption\", \"Signature\" and \"Authentication\"- subkeys will all be created all at once.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.16, anchor="w")
		Label3 = ctk.CTkLabel(my_Frame, text="The subkeys will be RSA-type and 4096 in length. Three years (\"3y\") is a good validity period for subkey\'s.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.21, anchor="w")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		private_fingerprints_and_aliases = []
		
		privatekeysavailable = False
			
		for nkey in private_keys:
				if nkey['fingerprint'] != PersonalGPGKey:
					List_fingerprints.append(nkey['fingerprint'])
		
		if List_fingerprints:
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)	
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select a key to add subkey\'s to:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.4, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.41, rely=0.4, anchor="w")

			Label5 = ctk.CTkLabel(my_Frame, text="Select expiry date for subkey\'s:", font=my_font, text_color="white", fg_color="black")
			Label5.place(relx=0.4, rely=0.48, anchor="e")
			combo = ttk.Combobox(my_Frame, values = ["1y","3y"], justify='right')
			combo.current(1)
			combo.place(relx=0.62, rely=0.48, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Add subkeys", text_color="white", fg_color=GPG_button_color, font=my_font, border_width=2, border_color="white", command=do_newGPGSubkey)
			Button2.place(relx=0.67, rely=0.54, anchor="w")
		else:
			Button = ctk.CTkButton(my_Frame, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.5, anchor="center")
			Button = ctk.CTkButton(my_Frame, text="Or, import one?", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.55, anchor="center")
			
	def create_Yubikeymeny(self):
		global Yubikey_button_color
		self.setup_Yubikey_v2()
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		AddkeysYubikeyButton = ctk.CTkButton(self, text="My Yubikey", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.setup_Yubikey_v2)
		AddkeysYubikeyButton.place(relx=0.1, rely=0.2, anchor="center")
		
		RemovekeysYubikeyButton = ctk.CTkButton(self, text="Transfer subkeys", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.add_subkey_Yubikey)
		RemovekeysYubikeyButton.place(relx=0.25, rely=0.2, anchor="center")
		
		ImportkeyButton = ctk.CTkButton(self, text="Passkeys", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_FIDOmeny)
		ImportkeyButton.place(relx=0.4, rely=0.2, anchor="center")
		
		CheckYubikeyButton = ctk.CTkButton(self, text="", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Yubikeymeny)
		CheckYubikeyButton.place(relx=0.55, rely=0.2, anchor="center")
		
		EditYubikeyButton = ctk.CTkButton(self, text="", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Yubikeymeny)
		EditYubikeyButton.place(relx=0.7, rely=0.2, anchor="center")
		
		SetupYubikeyButton = ctk.CTkButton(self, text="", text_color="white", fg_color=Yubikey_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.create_Yubikeymeny)
		SetupYubikeyButton.place(relx=0.85, rely=0.2, anchor="center")
		
	def create_abouthelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="dark orange"
		)
		
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		try:
			f = open("/home/user1/help/getstartedHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_gpghelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="dark orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/help/gpgHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_yubikeyhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="dark orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/help/yubikeyHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_secusbhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="dark orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/help/securearchiveHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
	
	def create_digitalIDhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="dark orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			f = open("/home/user1/help/digitalIDHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
		
	def create_boltcardhelptextbox(self):
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="dark orange"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		try:
			f = open("/home/user1/help/boltcardHelp.txt", "r")
			file_content = f.read()
			f.close()
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', file_content)
		except OSError:
			my_text = ctk.CTkTextbox(my_Frame, width=1194, height=644, corner_radius=1, border_width=0, border_color="dark orange", border_spacing=2, fg_color="black", text_color="white", font=("Arial", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey75", scrollbar_button_hover_color="white")
			my_text.insert('end', '\n\n\nThere was a problem opening the helpfile')
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
			
	def create_secusbtextbox(self):
		global path_to_USB_secure
		global filepathdestinationfolder
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		
		pathtobackg = self.get_background_image()
		
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
			my_font = ctk.CTkFont(family="Arial", size=18, weight="normal", slant="roman", underline=False, overstrike=False)
			
			Button1 = ctk.CTkButton(my_Frame, text="Edit", text_color="white", font=my_font, fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.create_editpasswordssecusbtextbox)
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
			my_font = ctk.CTkFont(family="Arial", size=18, weight="normal", slant="roman", underline=False, overstrike=False)
			
			Button1 = ctk.CTkButton(my_Frame, text="Edit", text_color="white", font=my_font, fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.create_editwalletssecusbtextbox)
			Button1.place(relx=0.75, rely=0.92, anchor="center")
			my_wallets.configure(state="disabled")
			my_wallets.place(relx=0.52, rely=0.48, anchor="w")
	
	def create_historytextbox(self):
		global path_to_USB_secure
		global filepathdestinationfolder
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="blue"
		)
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		my_font = ctk.CTkFont(family="Courier", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if path_to_USB_secure == 'Secure USB folder is available':
			my_historyTextbox = ctk.CTkTextbox(my_Frame, width=1170, height=550, corner_radius=1, border_width=3, border_color="blue", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 22), wrap="word", activate_scrollbars = True, scrollbar_button_color="grey", scrollbar_button_hover_color="navy blue")
		
			completeName = str(filepathdestinationfolder) + "/secure/log.txt"
			
			# Check if there is a log file. If not create one.
			if not os.path.isfile(completeName):
				f = open(completeName, 'w')
				f.write("Activity log:\n\n")
				f.close()
				
			f1 = open(completeName, "r")
			my_historyContent = f1.read()
			f1.close()
			my_historyTextbox.insert('end', my_historyContent)
			my_font = ctk.CTkFont(family="Arial", size=20, weight="normal", slant="roman", underline=False, overstrike=False)
			
			backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color=System_button_color, border_width=2, border_color="white", font=my_font, command=self.create_meny) 
			backButton.place(relx=0.5, rely=0.93, anchor="center")
		
			deleteButton = ctk.CTkButton(my_Frame, text="Delete log", text_color="white", font=my_font, fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.delete_history)
			deleteButton.place(relx=0.86, rely=0.93, anchor="w")
			my_historyTextbox.configure(state="disabled")
			my_historyTextbox.place(relx=0.01, rely=0.02, anchor="nw")
	
	def add_history(self, newEntry):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/log.txt"
		
		# Check if there is a log file. If not create one.
		if not os.path.isfile(completeName):
			f = open(completeName, 'w')
			f.write("Activity log:\n\n")
			f.close()
			
		now = datetime.now() # current date and time
		timeStamp = now.strftime("%m/%d/%Y %H:%M")
		fullEntry = timeStamp + ': ' + newEntry + '\n'
		f2 = open(completeName, 'a')
		f2.write(fullEntry)
		return True
		
	def delete_history(self):
		global filepathdestinationfolder
		completeName = str(filepathdestinationfolder) + "/secure/log.txt"
			
		answer = messagebox.askquestion('WARNING!', 'WARNING! Are you sure you want to delete the activity log?')
		if answer == 'yes':
			os.remove(completeName)
		self.create_historytextbox()
					
	def create_editpasswordssecusbtextbox(self):
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
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
			my_font = ctk.CTkFont(family="Arial", size=18, weight="normal", slant="roman", underline=False, overstrike=False)
			
			Button22 = ctk.CTkButton(my_Frame, text="Save", text_color="white", font=my_font, fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.do_edit_passwords)
			Button22.place(relx=0.5, rely=0.92, anchor="center")
		else:
			my_textbox.insert('end', 'You are not logged in. Passwords can\'t be displayed.')
		
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
		
		pathtobackg = self.get_background_image()
		
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
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			time.sleep(2)
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
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			clicked_publicKey = str(clicked2.get())
			decoded_publicfingerprint = self.lookup_fingerprint(clicked_publicKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			encrypted_data = gpg.encrypt(self.textBox.get('1.0', 'end'), decoded_publicfingerprint, sign=decoded_fingerprint) 
			
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type will be added automatically):")
			
			# Write the encrypted file to disk
			c = open(outputdir + '/' + USER_INP + '.asc', 'w')
			c.write(str(encrypted_data))
			c.close()
			if encrypted_data.ok:
				messagebox.showinfo('Information', 'Message has been encrypted and stored at '+ outputdir)
			else:
				messagebox.showinfo('Information', "That didn't work!\nMaybe the recipients key don't have the correct trust level or encryption capabilities?")	
			self.create_SecUSBmeny()
		
		def do_insert_from_clipboard():
			self.textBox.insert(CURRENT, self.clipboard_get())
				
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		if path_to_USB_secure == 'Secure USB folder is available':
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			# Select file with message to decrypt
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select textfile to decrypt.')
			time.sleep(2)
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
					private_fingerprints_and_aliases = []
					public_fingerprints_and_aliases = []
					
					privatekeysavailable = False
					publickeysavailable = False
					
					# Dont display the private key that is only intended for Offline device encryption/decryption
					for nkey in private_keys:
						if nkey['fingerprint'] != PersonalGPGKey:
							List_fingerprints.append(nkey['fingerprint'])
						
					if private_keys:
						private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
						clicked.set(private_fingerprints_and_aliases[0])
						privatekeysavailable = True
								
					for i2 in public_keys:
						if i2['fingerprint'] != PersonalGPGKey:
							List_publicfingerprints.append(i2['fingerprint'])
						
					if List_publicfingerprints:
						public_fingerprints_and_aliases = self.get_Aliases(List_publicfingerprints)
						clicked2.set(public_fingerprints_and_aliases[0])
						publickeysavailable = True
					
					if not List_fingerprints:	
						Button = ctk.CTkButton(my_Frame, text="There are no public keys on the device.", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.newGPGFull_Key)
						Button.place(relx=0.5, rely=0.5, anchor="center")
					else:
						Label1 = ctk.CTkLabel(my_Frame, text="Select private key to sign message (FROM):", text_color="white", fg_color="black", font=my_font)
						Label1.place(relx=0.59, rely=0.82, anchor="e")

						drop1 = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
						drop1.config(width=42)
						drop1.place(relx=0.6, rely=0.82, anchor="w")

						Label2 = ctk.CTkLabel(my_Frame, text="Select public key to encrypt message (TO):", text_color="white", fg_color="black", font=my_font)
						Label2.place(relx=0.59, rely=0.87, anchor="e")

						drop2 = OptionMenu(my_Frame, clicked2, *public_fingerprints_and_aliases)
						drop2.config(width=42)
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
						
						Button33 = ctk.CTkButton(my_Frame, text="Paste from clipboard", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_insert_from_clipboard)
						Button33.place(relx=0.06, rely=0.81, anchor="w")
						
						my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", weight="bold", underline=False, overstrike=False)
						
						if data_.trust_level is not None and data_.trust_level >= data_.TRUST_FULLY and self.lookup_Alias_absolut(data_.fingerprint) != "None":
							Labelv = ctk.CTkLabel(my_Frame, text="Signed by: " + self.lookup_Alias(data_.fingerprint), text_color="light green", fg_color="black", font=my_font)
							Labelv.place(relx=0.06, rely=0.86, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", weight="bold", underline=False, overstrike=False)
							Labelv = ctk.CTkLabel(my_Frame, text="Key ID :" + data_.key_id, text_color="light green", fg_color="black", font=my_font)
							Labelv.place(relx=0.06, rely=0.90, anchor="w")
							my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", weight="bold", underline=False, overstrike=False)
							Labelv2 = ctk.CTkLabel(my_Frame, text="Signature is good!", text_color="light green", fg_color="black", font=my_font)
							Labelv2.place(relx=0.06, rely=0.96, anchor="w")
						elif data_.trust_level is not None and data_.trust_level >= data_.TRUST_FULLY:
							Labelv = ctk.CTkLabel(my_Frame, text="Key ID :" + data_.key_id, text_color="light green", fg_color="black", font=my_font)
							Labelv.place(relx=0.06, rely=0.87, anchor="w")
							Labelv2 = ctk.CTkLabel(my_Frame, text="Signature is good!", text_color="light green", fg_color="black", font=my_font)
							Labelv2.place(relx=0.06, rely=0.92, anchor="w")
						else:
							Labelv = ctk.CTkLabel(my_Frame, text="Signature could not be verified!", text_color="pink", fg_color="black", font=my_font)
							Labelv.place(relx=0.05, rely=0.92, anchor="w")
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
			messagebox.showinfo("Information", "Connect the USB-device and then click \"OK\".")
			time.sleep(2)
			messagebox.showinfo("Information", "Select the file to load text from.")
			time.sleep(2)
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
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			clicked_publicKey = str(clicked2.get())
			decoded_publicfingerprint = self.lookup_fingerprint(clicked_publicKey)

			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			encrypted_data = gpg.encrypt(self.textBox.get('1.0', 'end'), decoded_publicfingerprint, sign=decoded_fingerprint) 

			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory where you want to save the signed and encrypted file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".asc\" will be added automatically):")
			
			# Write the encrypted file to disk
			c = open(outputdir + '/' + USER_INP + '.txt.gpg', 'w')
			c.write(str(encrypted_data))
			c.close()
			if encrypted_data.ok:
				messagebox.showinfo('Information', 'Message has been encrypted and stored at '+ outputdir)
			else:
				messagebox.showinfo('Information', "That didn't work!\nMaybe the recipients key don't have the correct trust level or encryption capabilities?")	
			self.create_SecUSBmeny()
		
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
			
		def do_insert_from_clipboard():
			self.textBox.insert(CURRENT, self.clipboard_get())
			
		pathtobackg = self.get_background_image()	
		
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
			private_fingerprints_and_aliases = []
			public_fingerprints_and_aliases = []
			
			privatekeysavailable = False
			publickeysavailable = False
			
			for nkey in private_keys:
				if nkey['fingerprint'] != PersonalGPGKey:
					List_fingerprints.append(nkey['fingerprint'])
				
			if private_keys:
				private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
				clicked.set(private_fingerprints_and_aliases[0])
				privatekeysavailable = True
						
			for i2 in public_keys:
				if i2['fingerprint'] != PersonalGPGKey:
					List_publicfingerprints.append(i2['fingerprint'])
				
			if List_publicfingerprints:
				public_fingerprints_and_aliases = self.get_Aliases(List_publicfingerprints)
				clicked2.set(public_fingerprints_and_aliases[0])
				publickeysavailable = True
			
			if not List_fingerprints:	
				Button = ctk.CTkButton(my_Frame, text="There are no private keys on the device.", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.newGPGFull_Key)
				Button.place(relx=0.5, rely=0.5, anchor="center")
			else:
				clicked.set(private_fingerprints_and_aliases[0])
				
				Label1 = ctk.CTkLabel(my_Frame, text="Select private key to sign message (FROM):", text_color="white", fg_color="black", font=my_font)
				Label1.place(relx=0.59, rely=0.82, anchor="e")

				drop1 = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
				drop1.config(width=42)
				drop1.place(relx=0.6, rely=0.82, anchor="w")
				
				Label2 = ctk.CTkLabel(my_Frame, text="Select key to encrypt message (TO):", text_color="white", fg_color="black", font=my_font)
				Label2.place(relx=0.59, rely=0.87, anchor="e")

				drop2 = OptionMenu(my_Frame, clicked2, *public_fingerprints_and_aliases)
				drop2.config(width=42)
				drop2.place(relx=0.6, rely=0.87, anchor="w")

				# Type content in textbox and select key before encrypting
				self.textBox = Text(my_Frame, bg = "white", fg = "black", bd = 4, font=("Helvetica", 16), wrap = 'word', undo = True)
				self.textBox.insert("1.0", '\nFrom: \nTo: \nDate: \n\nMessage: \n-------------------------------------------------------\n')
				self.textBox.place(relx=0.5, rely=0.39, height=500, width=1050, anchor="center")
				theinput = self.textBox.get("1.0",'end-1c')
				self.textBox.focus_set()
				self.textBox.focus_force()
				Button10 = ctk.CTkButton(my_Frame, text="Save to Secure archive", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=save_to_archive)
				Button10.place(relx=0.38, rely=0.94, anchor="center")	
				Button11 = ctk.CTkButton(my_Frame, text="Load from Secure archive", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=load_message_to_encrypt)
				Button11.place(relx=0.56, rely=0.94, anchor="center")	
				Button11 = ctk.CTkButton(my_Frame, text="Load from USB-file", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=load_message_to_encrypt_USB)
				Button11.place(relx=0.73, rely=0.94, anchor="center")	
				Button22 = ctk.CTkButton(my_Frame, text="Encrypt and Sign", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_encrypt_message)
				Button22.place(relx=0.88, rely=0.94, anchor="center")
				Button33 = ctk.CTkButton(my_Frame, text="Paste from clipboard", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_insert_from_clipboard)
				Button33.place(relx=0.06, rely=0.81, anchor="w")
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
		
		pathtobackg = self.get_background_image()
		
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
			my_font = ctk.CTkFont(family="Arial", size=18, weight="normal", slant="roman", underline=False, overstrike=False)
			Button22 = ctk.CTkButton(my_Frame, text="Save", text_color="white", font=my_font, fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.do_edit_wallets)
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
		global path_to_USB_secure
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Importing a private or public key from a USB-device to the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.15, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=15, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Select a file with the key you like to import. For importing a private key a password might be required.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.23, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="(Don't forget to make a backup of the local keychain to the secure archive after importing a new key.)", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.28, anchor="center")
		
		tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
		time.sleep(2)
		tk.messagebox.showinfo('Information', 'Select the GPG-key you like to import from the USB-device.')
		time.sleep(2)
		filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
		
		import_result = gpg.import_keys_file(filepathSourcefile)
		tk.messagebox.showinfo('Information', import_result.results[0]['text'] + '\n\nTips: A new key can be given an Alias under \"GPG -> Check local keys\".\n\n Also, don\'t forget to make a backup of any new key to the secure archive.')
		#if import_result.
		gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
		
		self.import_or_export()
	
	def importGPG_Key_from_archive(self):
		global path_to_USB_secure
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Importing a private or public key from the secure archive to the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.15, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=15, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Importing keys from the secure archive to the local keychain needs to be done after restoring from a backup*.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.23, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="* Each public and private key needs to be restored from the secure archive to the new devices local keychain.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.3, anchor="center")
		
		tk.messagebox.showinfo('Information', 'Select the GPG-key you like to import from the secure archive to the local keychain.')
		time.sleep(2)
		
		filepathSourcefile = filedialog.askopenfilename(initialdir='/home/user1/secure/keys')
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		import_result = gpg.import_keys_file(filepathSourcefile)
		
		gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
	
		self.import_or_export()
		
	def exportGPGmypublic(self):
		global clicked_publicKey
		global PersonalGPGKey
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_exportGPGmypublic():
			global clicked_publicKey
			global GPG_button_color
				
			clicked_publicKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_publicKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			ascii_armoured_public_key = gpg.export_keys(decoded_fingerprint)
			
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select folder where to place the public key by double clicking on it.')
			time.sleep(2)
			
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			# Ask for name for file (optional).
			USER_INP = simpledialog.askstring(title="Information!", prompt="Enter a name for the public key file:")
			input_size = len(USER_INP)
			if input_size > 42:
				messagebox.showinfo("Information", "The filename can be max 42 characters.")
				self.exportGPGmypublic()
			else:
				if USER_INP != '':
					c = open(outputdir + '/' + USER_INP + '.asc', 'w')
					c.write(ascii_armoured_public_key)
					c.close()
					tk.messagebox.showinfo('Information', 'Key has been exported to file\n' + USER_INP + '.asc')	
				else:
					c = open(outputdir + '/publickey' + decoded_fingerprint + '.asc', 'w')
					c.write(ascii_armoured_public_key)
					c.close()
					tk.messagebox.showinfo('Information', 'Key has been exported to file\n' + '/publickey' + decoded_fingerprint + '.asc')
			self.create_GPGmeny()
		
		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Export a public key from the local keychain to a file.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="The public key can be shared to others so that they can encrypt emails, files or messages.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.14, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Only the corresponding private key are able to decrypt it.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.19, anchor="w")
		
		Label4 = ctk.CTkLabel(my_Frame, text="Public key\s can also be signed by others, see \"Web of trust\" online for more information", text_color="white", fg_color="black", font=my_font)
		Label4.place(relx=0.05, rely=0.24, anchor="w")

		public_keys = gpg.list_keys()
				
		clicked = StringVar()
			
		List_publicfingerprints = []
		public_fingerprints_and_aliases = []
		
		publickeysavailable = False
			
		for i in public_keys:
			if i['fingerprint'] != PersonalGPGKey:
				List_publicfingerprints.append(i['fingerprint'])
				
		if List_publicfingerprints:	
			public_fingerprints_and_aliases = self.get_Aliases(List_publicfingerprints)
			clicked.set(public_fingerprints_and_aliases[0])
			publickeysavailable = True

		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			
		if publickeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select the public key to export:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *public_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.35, rely=0.4, anchor="w")
			
			Button2 = ctk.CTkButton(my_Frame, text="Export key", text_color="white", fg_color=GPG_button_color, font=my_font, border_width=2, border_color="white", command=do_exportGPGmypublic)
			Button2.place(relx=0.61, rely=0.47, anchor="w")
		else:
			print("No public key")
	
	def exportGPG(self):
		global GPG_button_color
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_exportGPG():
			global clicked_privateKey
			
			clicked_privateKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory where you want to save the signed and encrypted private keys file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			ascii_armoured_private_key = gpg.export_keys(decoded_fingerprint, True, expect_passphrase=False) 
			c = open(outputdir + '/privatekey' + decoded_fingerprint + '.gpg', 'w')
			c.write(ascii_armoured_private_key)
			c.close()
			tk.messagebox.showinfo('Information', 'Key has been exported.')
			self.create_GPGmeny()
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Export a private key from the local keychain to a file.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.07, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="The private key should be handled and stored in a safe manner.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.14, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="The private key's can be backed up in the secure archive where they will be encrypted.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.19, anchor="w")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		private_fingerprints_and_aliases = []
		
		privatekeysavailable = False
			
		for i in private_keys:
			if i['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(i['fingerprint'])
		
		if List_fingerprints:	
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
			
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select key to export:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.34, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.35, rely=0.4, anchor="w")
			
			Button2 = ctk.CTkButton(my_Frame, text="Export key", text_color="white", fg_color=GPG_button_color, font=my_font, border_width=2, border_color="white", command=do_exportGPG)
			Button2.place(relx=0.61, rely=0.47, anchor="w")
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
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Button = ctk.CTkButton(my_Frame, text="Encrypt a document on a USB-device", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.encrypt_file)
		Button.place(relx=0.3, rely=0.1, anchor="center")
		
		Button4 = ctk.CTkButton(my_Frame, text="Encrypt and sign a document on a USB-device", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.encrypt_and_sign_file)
		Button4.place(relx=0.7, rely=0.1, anchor="center")
		
		Button7 = ctk.CTkButton(my_Frame, text="Decrypt a document on a USB-device", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.decrypt_fle)
		Button7.place(relx=0.3, rely=0.25, anchor="center")
		
		Button5 = ctk.CTkButton(my_Frame, text="Check a signed document on a USB-device *", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.check_document)
		Button5.place(relx=0.7, rely=0.25, anchor="center")
		
		Button2 = ctk.CTkButton(my_Frame, text="Sign a document on a USB-device **", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.sign_document)
		Button2.place(relx=0.3, rely=0.4, anchor="center")
		
		Button3 = ctk.CTkButton(my_Frame, text="Sign/validate a public key on the local keychain", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.sign_key_on_keychain)
		Button3.place(relx=0.7, rely=0.4, anchor="center")
		
		Button12 = ctk.CTkButton(my_Frame, text="Sign QR-code information from camera ***", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.sign_QR)
		Button12.place(relx=0.3, rely=0.55, anchor="center")
		
		Button16 = ctk.CTkButton(my_Frame, text="List signatures for a key on the local keychain", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.list_sigs_on_key)
		Button16.place(relx=0.7, rely=0.55, anchor="center")
		
		Button8 = ctk.CTkButton(my_Frame, text="Check/make Timestamp address for a file on USB-device", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", width=370, height=35, font=my_font, command=self.BTC_timestamp)
		Button8.place(relx=0.5, rely=0.68, anchor="center")
		
		LabelaboutQR = ctk.CTkLabel(my_Frame, text="*** The output will be a detached signature (.sig) that can be saved or scanned as a QR-code.)", text_color="white", fg_color="black", font=my_font)
		LabelaboutQR.place(relx=0.15, rely=0.91, anchor="w")
			
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Labelinfo = ctk.CTkLabel(my_Frame, text="* Checking a document with a detached signature. To check an encrypted document (that are signed) you need to decrypt it.", text_color="white", fg_color="black", font=my_font)
		Labelinfo.place(relx=0.15, rely=0.79, anchor="w")
		Labelinfo2 = ctk.CTkLabel(my_Frame, text="** Signing by creating a detached signature, using a private key on your local keychain.", text_color="white", fg_color="black", font=my_font)
		Labelinfo2.place(relx=0.15, rely=0.85, anchor="w")
	
	def BTC_timestamp(self):
		global filepathdestinationfolder
		global path_to_data_file
		global path_to_sig
		
		the_blockchain_link = ' '
		
		def save_to_USB():
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt\" will be added automatically):")
			c = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
			c.write(the_blockchain_link)
			c.close()
			messagebox.showinfo('Information', 'File \"' +USER_INP + '.txt\"' + ' has been saved to the USB-device')
			self.select_what_to_sign()
			
		def sha256Hex(filename):
			BUF_SIZE = 65536
			
			sha256 = hashlib.sha256()
			
			with open(filename, 'rb') as f:
				while True:
					data = f.read(BUF_SIZE)
					if not data:
						break
					sha256.update(data)
					
			return sha256.hexdigest()
		
		tk.messagebox.showinfo("Information", "Insert USB-device and then click \"OK\".")
		time.sleep(2)
		tk.messagebox.showinfo('Information', 'Select the document to calculate BTC Timestamp address for.')
		time.sleep(2)
		filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		path_to_data_file = filepathSourcefile
		
		# Make hash for document
		totalHash = sha256Hex(filepathSourcefile)
		
		# Hash a Bitcoin address from the hash
		addr = Address(totalHash, encoding='bech32', script_type='p2wsh')
		
		btcAddress = addr.address
		
		# Generate QR-codes for bitcoin address 
		qr_public_address = qrcode.make(btcAddress)
		resize_qr_public_address = qr_public_address.resize((160, 160))
		pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
		resize_qr_public_address.save(pathtopublic)
		publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(160, 160))
		Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = publicimg)
		Labelpublicimg.place(relx=0.2, rely=0.68, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=26, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Check if a document has been Timestamped on the Bitcoin blockchain", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.1, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="The below bitcoin address is derived from the documents unique footpint (hash).", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.2, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Scan the below QR with a Blockchain link to check if there are any sats sent to it (bech32, Native Segwit).\nOr, make a Timestamp yourself by sending 1100 sats to a pay-link.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.29, anchor="center")
		
		pubLabel = ctk.CTkLabel(my_Frame, text="BTC address", text_color="white", font=my_font, fg_color="black")
		pubLabel.place(relx=0.2, rely=0.52, anchor="center")
		
		# Generate QR-codes for Blockchain search 
		the_blockchain_link = "www.mempool.space/address/" + str(btcAddress)
		qr_blockchain_address = qrcode.make(the_blockchain_link)
		resize_qr_blockchain_address = qr_blockchain_address.resize((200, 200))
		pathtoblockchain = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
		resize_qr_blockchain_address.save(pathtoblockchain)
		blockchainimg = ctk.CTkImage(light_image=Image.open(pathtoblockchain), dark_image=Image.open(pathtoblockchain), size=(200, 200))
		Labelblockchainimg = ctk.CTkLabel(my_Frame,  text = "", image = blockchainimg)
		Labelblockchainimg.place(relx=0.8, rely=0.63, anchor="center")
		
		pubLabel = ctk.CTkLabel(my_Frame, text="Blockchain link *:", text_color="white", font=my_font, fg_color="black")
		pubLabel.place(relx=0.8, rely=0.44, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		saveButton = ctk.CTkButton(my_Frame, text="Save to USB-device", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=save_to_USB)
		saveButton.place(relx=0.8, rely=0.82, anchor="center")
		
		timestampbutton = ctk.CTkButton(my_Frame, text="Create pay-link (1100 sats)", text_color="white", fg_color="dark green", border_width=2, border_color="white", font=my_font, command=partial(self.create_paylink, my_Frame))
		timestampbutton.place(relx=0.5, rely=0.38, anchor="center")
								
		infoLabel = ctk.CTkLabel(my_Frame, text="* Use Blockchain link to check if a timestamped transaction has been made to the BTC address.", text_color="white", font=my_font, fg_color="black")
		infoLabel.place(relx=0.18, rely=0.88, anchor="w")
		back_button = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.select_what_to_sign)
		back_button.place(relx=0.5, rely=0.94, anchor="center")
	
	def create_paylink(self, frame_):
		global filepathdestinationfolder
		global path_to_data_file
		global path_to_sig
		
		transaction_payload = ' '
		
		def do_new_Bitcoinwallet(TimestampAddress, totalHash, outputfilesname, filename):
		
			path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
			
			now = datetime.now()
			dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
			dt_string_short = now.strftime("%Y-%m-%d")
					
			new_paperwallet = [
								"Timestamp",
								dt_string_short,
								TimestampAddress,
								totalHash,
								filename,
								outputfilesname,
								"Not payed"]

			with open(path_to_wallets, 'a') as f:
				writer = csv.writer(f)
				writer.writerow(new_paperwallet)
				
		def save_to_USB():
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt\" will be added automatically):")
			c = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
			c.write(transaction_payload)
			c.close()
			messagebox.showinfo('Information', 'File \"' +USER_INP + '.txt\"' + ' has been saved to the USB-device')
			self.select_what_to_sign()
			
		def sha256Hex(filename):
			BUF_SIZE = 65536
			
			sha256 = hashlib.sha256()
			
			with open(filename, 'rb') as f:
				while True:
					data = f.read(BUF_SIZE)
					if not data:
						break
					sha256.update(data)
					
			return sha256.hexdigest()
			
		# Make hash for document
		totalHash = sha256Hex(path_to_data_file)
		
		# Hash a Bitcoin address from the hash
		addr = Address(totalHash, encoding='bech32', script_type='p2wsh')
		
		btcAddress = addr.address
		
		transaction_payload = "bitcoin:" + btcAddress + '?amount=0.00001100'
		
		filename_list = path_to_data_file.split("/")
		filename_ = str(filename_list[-1])
			
		do_new_Bitcoinwallet(btcAddress, totalHash, "None", filename_)
					
		# Generate QR-codes for bitcoin payment 
		qr_public_address = qrcode.make(transaction_payload)
		resize_qr_public_address = qr_public_address.resize((160, 160))
		pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
		resize_qr_public_address.save(pathtopublic)
		publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(160, 160))
		Labelpublicimg = ctk.CTkLabel(frame_,  text = "", image = publicimg)
		Labelpublicimg.place(relx=0.5, rely=0.61, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
	
		pubLabel = ctk.CTkLabel(frame_, text="Paylink:", text_color="white", font=my_font, fg_color="black")
		pubLabel.place(relx=0.5, rely=0.45, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		detailsButton = ctk.CTkButton(frame_, text="Details", text_color="white", fg_color="black", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.do_edit_Bitcoinwallets, btcAddress))
		detailsButton.place(relx=0.5, rely=0.77, anchor="center")
		saveButton = ctk.CTkButton(frame_, text="Save Pay-link to USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=save_to_USB)
		saveButton.place(relx=0.5, rely=0.82, anchor="center")
			
	def decrypt_fle(self):
		global filepathdestinationfolder
		global path_to_USB_secure
		global SecUSB_button_color
		global theinput 
		global clicked_publicKey
		global PersonalGPGKey
		main_fingerprint = ' '
		
		def get_main_fingerprint_from_subkeyID(key_ID_tag):
			found_ = "no"
			# Get list of public keys
			public_keys = gpg.list_keys()

			# Loop through and display look for any containing a sign subkey
			if public_keys:
				for i in public_keys:
					subkey_lists = i['subkeys']
					# Loop though the subkeys lists 
					for ii in subkey_lists:
						if ii[1] == 's' and ii[0] == key_ID_tag: # If the subkey is signing key and the key ID match
							found_ = i['fingerprint']
				return found_
								
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
				
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Decrypt and check signature for a file on a USB-device using keys on the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.1, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Decryption will be done with private key. Output file can be placed on the USB-device or in the secure archive.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.16, anchor="w")
		
		if path_to_USB_secure == 'Secure USB folder is available':
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			# Select file with message to decrypt
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the file to decrypt.')
			time.sleep(2)
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			stream = open(filepathSourcefile, 'rb')
			
			tk.messagebox.showinfo('Information', 'Select the directory for the output file.')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (with correct extension):")
			output_path = outputdir + '/' + USER_INP		
			try:
				data_ = gpg.decrypt_file(stream, output=output_path)
				if data_.ok:
					if get_main_fingerprint_from_subkeyID(data_.key_id) != "no":
						main_fingerprint = get_main_fingerprint_from_subkeyID(data_.key_id)
					else:
						main_fingerprint = data_.fingerprint
					
					if data_.trust_level is not None and data_.trust_level >= data_.TRUST_FULLY and self.lookup_Alias_absolut(main_fingerprint) != "None":
						Labelv = ctk.CTkLabel(my_Frame, text="Signed by:", text_color="light green", fg_color="black", font=my_font)
						Labelv.place(relx=0.5, rely=0.32, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=24, slant="roman", weight="bold", underline=False, overstrike=False)
						Labelv1 = ctk.CTkLabel(my_Frame, text=self.lookup_Alias(main_fingerprint), text_color="light green", fg_color="black", font=my_font)
						Labelv1.place(relx=0.5, rely=0.38, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", weight="normal", underline=False, overstrike=False)
						Labelv2 = ctk.CTkLabel(my_Frame, text="Key ID :" + data_.key_id, text_color="light green", fg_color="black", font=my_font)
						Labelv2.place(relx=0.5, rely=0.45, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", weight="bold", underline=False, overstrike=False)
						Labelv3 = ctk.CTkLabel(my_Frame, text="Signature is good!", text_color="light green", fg_color="black", font=my_font)
						Labelv3.place(relx=0.5, rely=0.52, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
						Labelv4 = ctk.CTkLabel(my_Frame, text="Decrypted file has been saved as:", text_color="white", fg_color="black", font=my_font)
						Labelv4.place(relx=0.5, rely=0.62, anchor="center")
						Labelv5 = ctk.CTkLabel(my_Frame, text=output_path, text_color="white", fg_color="black", font=my_font)
						Labelv5.place(relx=0.5, rely=0.7, anchor="center")
					elif data_.trust_level is not None and data_.trust_level >= data_.TRUST_FULLY:
						Labelv = ctk.CTkLabel(my_Frame, text="Signed by:", text_color="light green", fg_color="black", font=my_font)
						Labelv.place(relx=0.5, rely=0.32, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=24, slant="roman", weight="bold", underline=False, overstrike=False)
						Labelv1 = ctk.CTkLabel(my_Frame, text=main_fingerprint, text_color="light green", fg_color="black", font=my_font)
						Labelv1.place(relx=0.5, rely=0.38, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", weight="normal", underline=False, overstrike=False)
						Labelv2 = ctk.CTkLabel(my_Frame, text="Key ID :" + data_.key_id, text_color="light green", fg_color="black", font=my_font)
						Labelv2.place(relx=0.5, rely=0.45, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", weight="bold", underline=False, overstrike=False)
						Labelv3 = ctk.CTkLabel(my_Frame, text="Signature is good!", text_color="light green", fg_color="black", font=my_font)
						Labelv3.place(relx=0.5, rely=0.52, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
						Labelv4 = ctk.CTkLabel(my_Frame, text="Decrypted file has been saved as:", text_color="white", fg_color="black", font=my_font)
						Labelv4.place(relx=0.5, rely=0.62, anchor="center")
						Labelv5 = ctk.CTkLabel(my_Frame, text=output_path, text_color="white", fg_color="black", font=my_font)
						Labelv5.place(relx=0.5, rely=0.7, anchor="center")
					else:
						my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", weight="bold", underline=False, overstrike=False)
						Labelv = ctk.CTkLabel(my_Frame, text="Signature could not be verified!", text_color="pink", fg_color="black", font=my_font)
						Labelv.place(relx=0.5, rely=0.52, anchor="center")
						my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
						Labelv4 = ctk.CTkLabel(my_Frame, text="Decrypted file has been saved as:", text_color="white", fg_color="black", font=my_font)
						Labelv4.place(relx=0.5, rely=0.62, anchor="center")
						Labelv5 = ctk.CTkLabel(my_Frame, text=output_path, text_color="white", fg_color="black", font=my_font)
						Labelv5.place(relx=0.5, rely=0.7, anchor="center")
				else:
					messagebox.showinfo('Information', data_.status)
					self.select_what_to_sign()
			except FileNotFoundError:
					messagebox.showinfo("Information", "No settings file found.")
		else:
			notOKButton = ctk.CTkButton(my_Frame, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
			
	def encrypt_and_sign_file(self):
		global clicked_publicKey
		global clicked_privateKey
		global PersonalGPGKey
		global GPG_button_color
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_encrypt_and_sign_file():
			global clicked_publicKey
			global clicked_privateKey
			
			clicked_privateKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			clicked_publicKey = str(clicked2.get())
			decoded_publicfingerprint = self.lookup_fingerprint(clicked_publicKey)
			
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the file you want to encrypt.')
			time.sleep(2)
			file_path = filedialog.askopenfilename(initialdir='/media/user1')
			
			# Read the file
			stream = open(file_path, 'rb')
				
			# Encrypt the file
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			encrypted_data = gpg.encrypt_file(stream, decoded_publicfingerprint, sign=decoded_fingerprint, always_trust=True) 

			# Write the encrypted file to disk
			c = open(file_path + '.asc', 'w')
			c.write(str(encrypted_data))
			c.close()
			
			if encrypted_data.ok:
				messagebox.showinfo('Information', 'File has been encrypted and stored as:\n'+ file_path + '.asc')
			else:
				messagebox.showinfo('Information', "That didn't work!\nMaybe the recipients key don't have the correct trust level or encryption capabilities?")

			self.select_what_to_sign()
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Encrypt and sign a file on a USB-device using one of the public keys on the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.1, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Encryption with a recipients public key and signing with selected private key.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.16, anchor="w")
		
		Label3 = ctk.CTkLabel(my_Frame, text="Output file (.asc) will be placed in the same directory as the original file.", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.05, rely=0.21, anchor="w")
				
		private_keys = gpg.list_keys(True)
		public_keys = gpg.list_keys()
				
		clicked = StringVar()
		clicked2 = StringVar()
	
		List_fingerprints = []
		List_publicfingerprints = []
		private_fingerprints_and_aliases = []
		public_fingerprints_and_aliases = []
		
		privatekeysavailable = False
		publickeysavailable = False
		
		# Dont display the private key that is only intended for Offline device encryption/decryption
		for nkey in private_keys:
			if nkey['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(nkey['fingerprint'])
			
		if List_fingerprints:
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
					
		for i2 in public_keys:
			if i2['fingerprint'] != PersonalGPGKey:
				List_publicfingerprints.append(i2['fingerprint'])
			
		if List_publicfingerprints:
			public_fingerprints_and_aliases = self.get_Aliases(List_publicfingerprints)
			clicked2.set(public_fingerprints_and_aliases[0])
			publickeysavailable = True
		
		if not List_fingerprints:	
			Button = ctk.CTkButton(my_Frame, text="There are no private keys on the device.", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.5, anchor="center")
		else:
			Label1 = ctk.CTkLabel(my_Frame, text="Select private key to sign message with (FROM):", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.45, rely=0.4, anchor="e")

			drop1 = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop1.config(width=45)
			drop1.place(relx=0.46, rely=0.4, anchor="w")
						
		if publickeysavailable == True:
			Label11 = ctk.CTkLabel(my_Frame, text="Select a public key to encrypt the file with (TO):", font=my_font, text_color="white", fg_color="black")
			Label11.place(relx=0.45, rely=0.46, anchor="e")
			drop2 = OptionMenu(my_Frame, clicked2, *public_fingerprints_and_aliases)
			drop2.config(width=45)
			drop2.place(relx=0.46, rely=0.46, anchor="w")

			Button2 = ctk.CTkButton(my_Frame, text="Continue", text_color="white", fg_color=GPG_button_color, font=my_font, border_width=2, border_color="white", command=do_encrypt_and_sign_file)
			Button2.place(relx=0.72, rely=0.54, anchor="w")
		else:
			Button3 = ctk.CTkButton(my_Frame, text="There are no public keys on the keychain. Create one now?", font=my_font, text_color="white", fg_color="green", border_width=2, border_color="white", command=self.importGPG_Key)
			Button3.place(relx=0.5, rely=0.55, anchor="center")
			
	def encrypt_file(self):
		global clicked_publicKey
		global PersonalGPGKey
		global GPG_button_color
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_encrypt_file():
			global clicked_publicKey
			
			clicked_publicKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_publicKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the file you want to encrypt.')
			time.sleep(2)
			file_path = filedialog.askopenfilename(initialdir='/media/user1')
			
			# Read the file
			stream = open(file_path, 'rb')
				
			# Encrypt the file
			encrypted_data = gpg.encrypt_file(stream, decoded_fingerprint, always_trust=True)

			# Write the encrypted file to disk
			c = open(file_path + '.asc', 'w')
			c.write(str(encrypted_data))
			c.close()
			
			if encrypted_data.ok:
				messagebox.showinfo('Information', 'File has been encrypted and stored as:\n'+ file_path + '.asc')
			else:
				messagebox.showinfo('Information', "That didn't work!\nMaybe the recipients key don't have the correct trust level or encryption capabilities?")

			self.select_what_to_sign()
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Encrypt a file on a USB-device using one of the public keys on the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.05, rely=0.1, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Encryption will be done with the recipients public key. Output file (.asc) will be placed in same directory as the original file.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.05, rely=0.16, anchor="w")
		
		public_keys = gpg.list_keys()
				
		clicked = StringVar()
			
		List_fingerprints = []
		public_fingerprints_and_aliases = []
		
		publickeysavailable = False
			
		for nkey in public_keys:
			if nkey['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(nkey['fingerprint'])
		
		if List_fingerprints:
			public_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)	
			clicked.set(public_fingerprints_and_aliases[0])
			publickeysavailable = True
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			
		if publickeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select a public key to encrypt the file with:", font=my_font, text_color="white", fg_color="black")
			Label1.place(relx=0.4, rely=0.4, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *public_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.41, rely=0.4, anchor="w")

			Button2 = ctk.CTkButton(my_Frame, text="Continue", text_color="white", fg_color=GPG_button_color, font=my_font, border_width=2, border_color="white", command=do_encrypt_file)
			Button2.place(relx=0.67, rely=0.48, anchor="w")
		else:
			Button = ctk.CTkButton(my_Frame, text="There are no public keys on the keychain. Create one now?", font=my_font, text_color="white", fg_color="green", border_width=2, border_color="white", command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.5, anchor="center")
			
	def list_sigs_on_key(self):
		global GPG_button_color
		global PersonalGPGKey
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="green"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		pathtobackg = "/home/user1/images/GnuPGbackground.JPG"
		
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
			decoded_fingerprint = self.lookup_fingerprint(clicked_publicKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
			
			# Get sigs for the selected key
			public_keys = gpg.list_keys(sigs=True)

			# Loop through and display sigs
			if public_keys:
				for i in public_keys:
					if i['fingerprint'] == decoded_fingerprint and i['sigs']: 
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
		public_fingerprints_and_aliases = []
		
		pubickeysavailable = False
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)

		# List the private keys that can be used for signing			
		for i in public_keys:
			if i['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(i['fingerprint'])
				
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No public keys."')
			
		else:
			public_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(public_fingerprints_and_aliases[0])
			pubickeysavailable = True
				
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if pubickeysavailable == True:			
			Label5 = ctk.CTkLabel(top_Frame, text="Select a public key to list signatures for:", text_color="white", fg_color="black", font=my_font)
			Label5.place(relx=0.4, rely=0.3, anchor="e")
			drop = OptionMenu(top_Frame, clicked, *public_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.41, rely=0.3, anchor="w")
			
			Button2 = ctk.CTkButton(top_Frame, text="List signatures", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_list_sigs_on_key)
			Button2.place(relx=0.67, rely=0.6, anchor="w")
		else:
			Button = ctk.CTkButton(top_Frame, text="There are no public keys on the keychain.", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.1, anchor="center")
						
	def sign_key_on_keychain(self):
		global GPG_button_color
		def do_sign_key_on_keychain():
			global clicked_privateKey
			global clicked_publicKey
			
			clicked_privateKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			clicked_publicKey = str(clicked2.get())
			decoded_publifingerprint = self.lookup_fingerprint(clicked_publicKey)
			my_Frame = ctk.CTkFrame(self, 
			width=1200, 
			height=650,
			border_width=4,
			border_color="blue"
			)
			my_Frame.place(relx=0.5, rely=0.6, anchor="center")
			
			pathtobackg = self.get_background_image()
		
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
			Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
			Label_backg.place(x=0, y=0)
			
			# Sign the public key and pass argument fingerprint
			command= 'gpg --local-user ' + decoded_fingerprint + ' --quick-sign-key ' + decoded_publifingerprint
			
			os.system(command) 
			
			tk.messagebox.showinfo('Information', 'Please check that the key on the local keychain was signed.')
			self.create_GPGmeny()
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Signing a public key on the local keychain using one of the private keys.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.22, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="(1). Select the private key to sign with.  (2). Select the public key that you would like to sign.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.30, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="(If a master key is only with cerification capability, then you need to select that keys signing subkey instead).", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.35, anchor="center")

		private_keys = gpg.list_keys(True)
		public_keys = gpg.list_keys()
				
		clicked = StringVar()
		clicked2 = StringVar()
			
		List_fingerprints = []
		List_fingerprints2 = []
		private_fingerprints_and_aliases = []
		public_fingerprints_and_aliases = []
		
		privatekeysavailable = False

		# List the private keys that can be used for signing			
		for nkey in private_keys:
			if nkey['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(nkey['fingerprint'])
			
		if List_fingerprints:	 
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
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
		for i2 in public_keys:
			if i2['fingerprint'] != PersonalGPGKey:
				List_fingerprints2.append(i2['fingerprint'])
		
		if not List_fingerprints2:	
			tk.messagebox.showinfo('Information', 'No public keys."')
		else:
			public_fingerprints_and_aliases = self.get_Aliases(List_fingerprints2)
			clicked2.set(public_fingerprints_and_aliases[0])
			publickeysavailable = True
				
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if privatekeysavailable == True:
			Label5 = ctk.CTkLabel(my_Frame, text="Select a private key to sign with:", text_color="white", fg_color="black", font=my_font)
			Label5.place(relx=0.4, rely=0.5, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.41, rely=0.5, anchor="w")
			Label6 = ctk.CTkLabel(my_Frame, text="Select the public key you intend to sign:", text_color="white", fg_color="black", font=my_font)
			Label6.place(relx=0.4, rely=0.55, anchor="e")
			drop2 = OptionMenu(my_Frame, clicked2, *public_fingerprints_and_aliases)
			drop2.config(width=45)
			drop2.place(relx=0.41, rely=0.55, anchor="w")
			Button2 = ctk.CTkButton(my_Frame, text="Sign the public key", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_sign_key_on_keychain)
			Button2.place(relx=0.65, rely=0.61, anchor="w")
		else:
			Button = ctk.CTkButton(my_Frame, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=self.newGPGFull_Key)
			Button.place(relx=0.5, rely=0.65, anchor="center")
			Button = ctk.CTkButton(my_Frame, text="Or, import one?", text_color="white", fg_color="green", font=my_font, border_width=2, border_color="white", command=self.importGPG_Key)
			Button.place(relx=0.5, rely=0.72, anchor="center")	
	
	def get_background_image(self):
		pathtobackg = "/home/user1/images/blackbackground.jpg"
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
				pathtobackg = "/home/user1/images/winterbackgroundmid.jpg"
			if users_theme == 'Summer':
				pathtobackg = "/home/user1/images/summerbackgroundmid.jpg"
			if users_theme == 'Light':
				pathtobackg = "/home/user1/images/lightbackgroundmid.jpg"
			if users_theme == 'Dark':
				pathtobackg = "/home/user1/images/darkbackgroundmid.jpg"	
		return pathtobackg
							
	def sign_document(self):
		global clicked_privateSubKey 
		#global outputdir
		global GPG_button_color
		
		def start_do_sign():
			tk.messagebox.showinfo("Information", "Insert USB-device and then click \"OK\".")
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the document to sign.')
			time.sleep(2)
			filepathSourcefile = filedialog.askopenfilename(initialdir='/media/user1')
			tk.messagebox.showinfo('Information', 'Select the output folder for the detached signature by double clicking on it.')
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			do_sign(filepathSourcefile, outputdir)
		
		def do_new_Bitcoinwallet(TimestampAddress, totalHash, outputfilesname, filename):
		
			path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
			
			now = datetime.now()
			dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
			dt_string_short = now.strftime("%Y-%m-%d")
					
			new_paperwallet = [
								"Timestamp",
								dt_string_short,
								TimestampAddress,
								totalHash,
								filename,
								outputfilesname,
								"Not payed"]

			with open(path_to_wallets, 'a') as f:
				writer = csv.writer(f)
				writer.writerow(new_paperwallet)
		
		def sha256Hex(filename):
			BUF_SIZE = 65536
			
			sha256 = hashlib.sha256()
			
			with open(filename, 'rb') as f:
				while True:
					data = f.read(BUF_SIZE)
					if not data:
						break
					sha256.update(data)
					
			return sha256.hexdigest()
						
		def do_sign(filepathSourcefile, outputdir):
			global clicked_privateSubKey
			
			clicked_privateKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			filename_list = filepathSourcefile.split("/")
			filename_ = str(filename_list[-1])
			sigfilename = filename_ + '.sig'
			outputfilesname = outputdir + "/" + sigfilename
			
			with open(filepathSourcefile, 'rb') as f: 
				try:
					data_ = gpg.sign_file(f, keyid=decoded_fingerprint, detach=True)
					f2 = open(outputfilesname, 'w')
					f2.write(str(data_))
					f2.close()
				except ValueError as ve:
					tk.messagebox.showinfo('Information', 'Something went wrong in signing!')
			pathtobackg = self.get_background_image()
			my_font = ctk.CTkFont(family="Arial", size=28, weight="bold", slant="roman", underline=True, overstrike=False)
			if data_.status == "signature created":
				if checkbox.get() == "on":
					# Create a timestamp Bitcoin address by hashing a combining of hashes from both signature file and document file
					# After sending sats to this new address it is prof that BOTH the signature and the signed data existed at the time the transaction was included in a block on the Bitcoin blockchain 
					
					# Make hash for document
					hashForDocument = sha256Hex(filepathSourcefile)
					
					# Make hash for signature
					hashForSignature = sha256Hex(outputfilesname)
					
					# Make combined hash for combination of document and signature hashes
					totalHash = hashForSignature + hashForDocument
					
					# Hash a Bitcoin address from the combined hash
					addr = Address(totalHash, encoding='bech32', script_type='p2wsh')
					
					signatureAddress = addr.address
					
					# Generate a Bitcoin transaction including amount of 1100 sats to the newly hashed address
					transaction_payload = "bitcoin:" + signatureAddress + '?amount=0.00001100'
					
					# Clear screen and re-fill
					backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
					Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
					Label_backg.place(x=0, y=0)
		
					Label1 = ctk.CTkLabel(my_Frame, text="Signing a document using one of your private keys", text_color="white", fg_color="black", font=my_font)
					Label1.place(relx=0.5, rely=0.1, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
					
					Label2 = ctk.CTkLabel(my_Frame, text="The signature file and the document together has created below QR- transaction.", text_color="white", fg_color="black", font=my_font)
					Label2.place(relx=0.5, rely=0.2, anchor="center")
					
					Label3 = ctk.CTkLabel(my_Frame, text="Scan the transaction QR-code and pay it and thereby making a proof on the Bicoin blockchain.", text_color="white", fg_color="black", font=my_font)
					Label3.place(relx=0.5, rely=0.25, anchor="center")
					
					# Create a QR-code for the transaction
					pathtosignature = qrcode.make(transaction_payload)
					resize_pathtosignature = pathtosignature.resize((280, 280))
					pathtotransactionsignature = str(filepathdestinationfolder) + "/secure/transactionsignature.png"
					resize_pathtosignature.save(pathtotransactionsignature)
					loadimg = ctk.CTkImage(light_image=Image.open(pathtotransactionsignature), dark_image=Image.open(pathtotransactionsignature), size=(280, 280))
					Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = loadimg)
					Labelpublicimg.place(relx=0.72, rely=0.56, anchor="center")
					
					# Add the signatures transaction in the paper wallets CSV-file
					do_new_Bitcoinwallet(signatureAddress, totalHash, sigfilename, filename_)
					
					my_font = ctk.CTkFont(family="Arial", size=36, weight="bold", slant="roman", underline=False, overstrike=False)
					pubLabel = ctk.CTkLabel(my_Frame, text="Success!", text_color="light green", font=my_font, fg_color="black")
					pubLabel.place(relx=0.35, rely=0.46, anchor="center")
					
					my_font = ctk.CTkFont(family="Arial", size=34, weight="bold", slant="roman", underline=False, overstrike=False)
					pubLabel = ctk.CTkLabel(my_Frame, text="Signature created!", text_color="white", font=my_font, fg_color="black")
					pubLabel.place(relx=0.35, rely=0.55, anchor="center")
					
					my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
					outLabel = ctk.CTkLabel(my_Frame, text="Output file:", text_color="white", font=my_font, fg_color="black")
					outLabel.place(relx=0.35, rely=0.64, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=False, overstrike=False)
					pubLabel = ctk.CTkLabel(my_Frame, text=sigfilename, text_color="white", font=my_font, fg_color="black")
					pubLabel.place(relx=0.35, rely=0.7, anchor="center")
					scanLabel = ctk.CTkLabel(my_Frame, text="Pay address *:", text_color="white", fg_color="black", font=my_font)
					scanLabel.place(relx=0.72, rely=0.31, anchor="center")
					
					detailsButton = ctk.CTkButton(my_Frame, text="Details", text_color="white", fg_color="black", border_width=2, border_color="white", width=170, height=32, font=my_font, command=partial(self.do_edit_Bitcoinwallets, signatureAddress))
					detailsButton.place(relx=0.72, rely=0.82, anchor="center")
					
					my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
					
					Label11 = ctk.CTkLabel(my_Frame, text="* Sending bitcoin to the stated address records the event (hashed proof) on the Bitcoin Blockchain.", text_color="white", fg_color="black", font=my_font)
					Label11.place(relx=0.05, rely=0.88, anchor="w")
					backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="black", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.select_what_to_sign)
					backButton.place(relx=0.5, rely=0.94, anchor="center")
				else:
					backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
					Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
					Label_backg.place(x=0, y=0)
					
					Label1 = ctk.CTkLabel(my_Frame, text="Signing a document using one of your private keys", text_color="white", fg_color="black", font=my_font)
					Label1.place(relx=0.5, rely=0.1, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
					
					Label2 = ctk.CTkLabel(my_Frame, text="The signature file has been created.", text_color="white", fg_color="black", font=my_font)
					Label2.place(relx=0.5, rely=0.2, anchor="center")
					
					Label3 = ctk.CTkLabel(my_Frame, text="Keep the signature file and the document file in the same directory.", text_color="white", fg_color="black", font=my_font)
					Label3.place(relx=0.5, rely=0.25, anchor="center")
					
					my_font = ctk.CTkFont(family="Arial", size=36, weight="bold", slant="roman", underline=False, overstrike=False)
					pubLabel = ctk.CTkLabel(my_Frame, text="Signature created!", text_color="white", font=my_font, fg_color="black")
					pubLabel.place(relx=0.5, rely=0.5, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=24, slant="roman", underline=False, overstrike=False)
					pubLabel = ctk.CTkLabel(my_Frame, text="(" + sigfilename + ")", text_color="white", font=my_font, fg_color="black")
					pubLabel.place(relx=0.5, rely=0.62, anchor="center")
					backButton = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="black", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.select_what_to_sign)
					backButton.place(relx=0.5, rely=0.9, anchor="center")
			else:
				tk.messagebox.showinfo('Alert!', 'Something went wrong!')	
				self.select_what_to_sign()
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
		private_fingerprints_and_aliases = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=28, weight="bold", slant="roman", underline=True, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Signing a document using one of your private keys", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.1, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label2 = ctk.CTkLabel(my_Frame, text="Select what document to sign, where to place the document after signing and what private key to sign with.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.2, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="(The output will be a detached signature (.sig) in the folder that you selected.)", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.25, anchor="center")

		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
		
		# List the private keys that can be used for signing (exclude the Offline device own encryption key)			
		for i in private_keys:
			if i['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(i['fingerprint'])
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No private keys."')
		else:
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
			
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
		
		check_var = ctk.StringVar(value="off")
		
		checkbox = ctk.CTkCheckBox(my_Frame, text="Create timestamp *", font=my_font, variable=check_var, onvalue="on", offvalue="off", text_color="white", fg_color="black")
		checkbox.place(relx=0.74, rely=0.57, anchor="w")
		
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(my_Frame, text="Select a private key to sign with:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.54, rely=0.5, anchor="e")
			drop = OptionMenu(my_Frame, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.72, rely=0.57, anchor="e")
			Button = ctk.CTkButton(my_Frame, text="Start", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=start_do_sign)
			Button.place(relx=0.72, rely=0.64, anchor="e")
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
			Label11 = ctk.CTkLabel(my_Frame, text="* A Bitcoin transaction is needed to timestamp the document/signature combo.", text_color="white", fg_color="black", font=my_font)
			Label11.place(relx=0.2, rely=0.92, anchor="w")
			
		else:
			Button2 = ctk.CTkButton(my_Frame, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button2.place(relx=0.5, rely=0.65, anchor="center")
			Button3 = ctk.CTkButton(my_Frame, text="Or, import one?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=self.importGPG_Key)
			Button3.place(relx=0.5, rely=0.72, anchor="center")	
	
	def signQRfromCamera(self, fingerprint):
		global clicked_privateSubKey
		
		def save_to_USB():
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt.sig\" will be added automatically):")
			c = open(outputdir + '/' + USER_INP + '.txt.sig', 'w', encoding='utf-8')
			c.write(str(signed_data))
			c.close()
			c2 = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
			c2.write(file_content)
			c2.close()
			messagebox.showinfo('Information', 'Signature file \"' +USER_INP + '.sig\" and data file \".txt\" has been saved to the USB-device')
			self.select_what_to_sign()
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=1,
		border_color="brown"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		
				
		if path_to_USB_secure == 'Secure USB folder is available':			
			link_to_signature_data = "/home/user1/secure/QRsignaturefile.txt"
			
			if os.path.isfile(link_to_signature_data):
				try:
					f = open(link_to_signature_data, "r")
					file_content = f.read()
					f.close()
					transactiondatoavailable = True
				except OSError:
					print("No file")
				signed_data = gpg.sign(file_content, keyid=fingerprint, detach=True)
				
				signed_data_address = qrcode.make(signed_data)
									
				resize_signed_data_address = signed_data_address.resize((390, 390))
				pathtoQRsignature = str(filepathdestinationfolder) + "/secure/signatureQRmessage.png"
				
				resize_signed_data_address.save(pathtoQRsignature)
				
				loadimg = ctk.CTkImage(light_image=Image.open(pathtoQRsignature), dark_image=Image.open(pathtoQRsignature), size=(390, 390))
				
				my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
				
				my_font = ctk.CTkFont(family="Arial", size=24, slant="roman", underline=True, overstrike=False)
				pubLabel = ctk.CTkLabel(my_Frame, text="Signature:", text_color="white", font=my_font, fg_color="black")
				pubLabel.place(relx=0.5, rely=0.1, anchor="center")
				Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = loadimg)
				Labelpublicimg.place(relx=0.5, rely=0.45, anchor="center")
				
				my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
				saveQRButton = ctk.CTkButton(my_Frame, text="Save signature to USB", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=save_to_USB)
				saveQRButton.place(relx=0.5, rely=0.8, anchor="center")
				onemoreButton = ctk.CTkButton(my_Frame, text="Sign another", text_color="black", fg_color="dark orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.sign_QR)
				onemoreButton.place(relx=0.5, rely=0.89, anchor="center")
				backButton = ctk.CTkButton(my_Frame, text="Back", text_color="black", fg_color="orange", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.select_what_to_sign)
				backButton.place(relx=0.5, rely=0.96, anchor="center")
			else:
				my_font = ctk.CTkFont(family="Arial", size=28, slant="roman", underline=False, overstrike=False)
				pubLabel = ctk.CTkLabel(my_Frame, text="Could not read QR-data", text_color="white", font=my_font, fg_color="black")
				pubLabel.place(relx=0.5, rely=0.46, anchor="center")
		else:
			notOKButton = ctk.CTkButton(my_Frame, text="You are not logged in. Log in now?", text_color="white", fg_color="purple", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
		
	def sign_QR(self):
		global clicked_privateSubKey
		global outputdir
		global GPG_button_color
		
		def do_scan():
			global clicked_privateSubKey
			global outputdir
			
			clicked_privateKey = str(clicked.get())
			decoded_fingerprint = self.lookup_fingerprint(clicked_privateKey)
			self.readQRfromCameraToSign(decoded_fingerprint)
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
		private_fingerprints_and_aliases = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Scan a QR-code with the camera and sign the information with your private key", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.18, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		Label11 = ctk.CTkLabel(my_Frame, text="This could be a hash (checksum) from a large file or a Bitcoin address etc.", text_color="white", fg_color="black", font=my_font)
		Label11.place(relx=0.5, rely=0.25, anchor="center")
		
		Label2 = ctk.CTkLabel(my_Frame, text="Select a private key to sign with and then press \"Start camera\" to start scanning.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.35, anchor="center")
		
		Label3 = ctk.CTkLabel(my_Frame, text="You will get an option if you like to save the detached signature as a file (.sig) or scan it via a QR-code", text_color="white", fg_color="black", font=my_font)
		Label3.place(relx=0.5, rely=0.41, anchor="center")
		
		private_keys = gpg.list_keys(True)
				
		clicked = StringVar()
			
		List_fingerprints = []
		
		privatekeysavailable = False
		
		# List the private keys that can be used for signing (exclude the Offline device own encryption key)			
		for i in private_keys:
			if i['fingerprint'] != PersonalGPGKey:
				List_fingerprints.append(i['fingerprint'])
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No private keys."')
		else:
			private_fingerprints_and_aliases = self.get_Aliases(List_fingerprints)
			clicked.set(private_fingerprints_and_aliases[0])
			privatekeysavailable = True
			
		# Get input on what key to use	
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if privatekeysavailable == True:
			Label1 = ctk.CTkLabel(self, text="Select a private key to sign with:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.4, rely=0.65, anchor="e")
			drop = OptionMenu(self, clicked, *private_fingerprints_and_aliases)
			drop.config(width=45)
			drop.place(relx=0.41, rely=0.65, anchor="w")
			my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
		
			startButton = ctk.CTkButton(self, text="Start camera", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=do_scan)
			startButton.place(relx=0.5, rely=0.75, anchor="center")
			
		else:
			Button2 = ctk.CTkButton(self, text="There are no private keys on the keychain. Create one now?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.newGPGFull_Key)
			Button2.place(relx=0.5, rely=0.65, anchor="center")
			Button3 = ctk.CTkButton(self, text="Or, import one?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font, command=self.importGPG_Key)
			Button3.place(relx=0.5, rely=0.72, anchor="center")	
	
	def show_timestamp(self, frame_):
		global filepathdestinationfolder
		global path_to_data_file
		global path_to_sig
		
		the_blockchain_link = ' '
		
		def save_to_USB():
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the directory for the file.')
			time.sleep(2)
			outputdir = filedialog.askdirectory(initialdir='/media/user1')
			USER_INP = simpledialog.askstring(title="Required!", prompt="Name for file (the file type \".txt\" will be added automatically):")
			c = open(outputdir + '/' + USER_INP + '.txt', 'w', encoding='utf-8')
			c.write(the_blockchain_link)
			c.close()
			messagebox.showinfo('Information', 'File \"' +USER_INP + '.txt\"' + ' has been saved to the USB-device')
			self.select_what_to_sign()
			
		def sha256Hex(filename):
			BUF_SIZE = 65536
			
			sha256 = hashlib.sha256()
			
			with open(filename, 'rb') as f:
				while True:
					data = f.read(BUF_SIZE)
					if not data:
						break
					sha256.update(data)
					
			return sha256.hexdigest()
			
		# Make hash for document
		hashForDocument = sha256Hex(path_to_data_file)
		
		# Make hash for signature
		hashForSignature = sha256Hex(path_to_sig)
		
		# Make combined hash for combination of document and signature hashes
		totalHash = hashForSignature + hashForDocument
		
		# Hash a Bitcoin address from the combined hash
		addr = Address(totalHash, encoding='bech32', script_type='p2wsh')
		
		btcAddress = addr.address
		
		# Generate QR-codes for bitcoin address 
		qr_public_address = qrcode.make(btcAddress)
		resize_qr_public_address = qr_public_address.resize((160, 160))
		pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
		resize_qr_public_address.save(pathtopublic)
		publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(160, 160))
		Labelpublicimg = ctk.CTkLabel(frame_,  text = "", image = publicimg)
		Labelpublicimg.place(relx=0.2, rely=0.68, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
	
		pubLabel = ctk.CTkLabel(frame_, text="BTC address", text_color="white", font=my_font, fg_color="black")
		pubLabel.place(relx=0.2, rely=0.52, anchor="center")
		
		# Generate QR-codes for Blockchain search 
		the_blockchain_link = "www.mempool.space/address/" + str(btcAddress)
		qr_blockchain_address = qrcode.make(the_blockchain_link)
		resize_qr_blockchain_address = qr_blockchain_address.resize((200, 200))
		pathtoblockchain = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
		resize_qr_blockchain_address.save(pathtoblockchain)
		blockchainimg = ctk.CTkImage(light_image=Image.open(pathtoblockchain), dark_image=Image.open(pathtoblockchain), size=(200, 200))
		Labelblockchainimg = ctk.CTkLabel(frame_,  text = "", image = blockchainimg)
		Labelblockchainimg.place(relx=0.8, rely=0.65, anchor="center")
		
		pubLabel = ctk.CTkLabel(frame_, text="Blockchain link *:", text_color="white", font=my_font, fg_color="black")
		pubLabel.place(relx=0.8, rely=0.46, anchor="center")
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		saveButton = ctk.CTkButton(frame_, text="Save to USB-device", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=save_to_USB)
		saveButton.place(relx=0.8, rely=0.83, anchor="center")
		infoLabel = ctk.CTkLabel(frame_, text="* Use Blockchain link to check if a timestamped transaction has been made to the BTC address.", text_color="white", font=my_font, fg_color="black")
		infoLabel.place(relx=0.18, rely=0.88, anchor="w")
					
	def check_document(self):
		global outputdir
		global GPG_button_color
		global path_to_data_file
		global path_to_sig
		
		def get_main_fingerprint_from_subkeyID(key_ID_tag):
			found_ = "no"
			# Get list of public keys
			public_keys = gpg.list_keys()

			# Loop through and display look for any containing a sign subkey
			if public_keys:
				for i in public_keys:
					subkey_lists = i['subkeys']
					# Loop though the subkeys lists 
					for ii in subkey_lists:
						if ii[1] == 's' and ii[0] == key_ID_tag: # If the subkey is signing key and the key ID match
							found_ = i['fingerprint']
				return found_
			
		asc_file_found = False		# If signed or clearsigned
		sig_file_found = False		# If detached signature
		manual_file_found = False
		file_found = False
		name_of_file = " "
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		public_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
		
		Label1 = ctk.CTkLabel(my_Frame, text="Checking a signed file with a public key on the local keychain.", text_color="white", fg_color="black", font=my_font)
		Label1.place(relx=0.5, rely=0.15, anchor="center")
		
		Label2 = ctk.CTkLabel(my_Frame, text="If the signature is detached, the file and the signature should be in the same directory.", text_color="white", fg_color="black", font=my_font)
		Label2.place(relx=0.5, rely=0.2, anchor="center")

		public_keys = gpg.list_keys()
			
		List_fingerprints = []
		
		publickeysavailable = False
		
		# List the public keys that can be used for checking			
		for i in public_keys:
			List_fingerprints.append(i['fingerprint'])
		if not List_fingerprints:	
			tk.messagebox.showinfo('Information', 'No public keys."')
		else:
			publickeysavailable = True

		if publickeysavailable == True:
			tk.messagebox.showinfo('Information', 'Connect the USB-device and then click \"OK\".')
			time.sleep(2)
			tk.messagebox.showinfo('Information', 'Select the file/document you want to check.')
			time.sleep(2)
			path_to_data_file = filedialog.askopenfilename(initialdir='/media/user1')
			name_of_file = os.path.basename(path_to_data_file)
			# Try checking with signature in the same document
			try:
				open_stream = open(path_to_data_file, 'rb')
				file_found = True
			except FileNotFoundError:
				print("No file_found")
				
			if file_found:
				verified = gpg.verify_file(open_stream)
			else:
				verified = False
				
			if verified and verified.key_status == None:	
				Label11 = ctk.CTkLabel(my_Frame, text="The signature in file:\n", text_color="white", fg_color="black", font=my_font)
				Label11.place(relx=0.5, rely=0.55, anchor="center")
				Label22 = ctk.CTkLabel(my_Frame, text=name_of_file, text_color="white", fg_color="black", font=my_font)
				Label22.place(relx=0.5, my_Frame=0.6, anchor="center")
				my_font = ctk.CTkFont(family="Arial", size=38, weight="bold", slant="roman", underline=True, overstrike=False)
				Label33 = ctk.CTkLabel(my_Frame, text="Is GOOD!", text_color="green", fg_color="black", font=my_font)
				Label33.place(relx=0.5, rely=0.7, anchor="center")
			else:
				# Try checking file/document with a file in same catalog and same name but with added .asc or .sig to the complete file name
				path_to_asc = path_to_data_file + '.asc'
				path_to_sig = path_to_data_file + '.sig'	
				try:
					open_stream = open(path_to_asc, 'rb')
					asc_file_found = True
					path_to_sig = path_to_asc
				except FileNotFoundError:
					print("No .asc file_found")
				if not asc_file_found:	
					try:
						open_stream = open(path_to_sig, 'rb')
						sig_file_found = True
					except FileNotFoundError:
							print("No .asc or .sig file_found")
						
				# If there was no .asc or .pgp signature files found
				if not asc_file_found and not sig_file_found:
					tk.messagebox.showinfo('Information', 'No signature file with extension .asc or .sig found!\nManually select the signature file.\n')
					path_to_signature = filedialog.askopenfilename(initialdir='/media/user1')
					try:
						open_stream = open(path_to_signature, 'rb')
						path_to_sig = path_to_signature
						manual_file_found = True
					except FileNotFoundError:
						print("Failed to open manually selected signature file")
				
				if asc_file_found or sig_file_found or manual_file_found:	
					verified = gpg.verify_file(open_stream, path_to_data_file)
				
				if verified:
					if get_main_fingerprint_from_subkeyID(verified.key_id) != "no":
						main_fingerprint = get_main_fingerprint_from_subkeyID(verified.key_id)
					else:
						main_fingerprint = verified.fingerprint
							
				if ((asc_file_found and verified) or (sig_file_found and verified) or (manual_file_found and verified)) and verified.key_status == None:
					my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", weight="bold", underline=False, overstrike=False)
					Labelv = ctk.CTkLabel(my_Frame, text="The file \"" + name_of_file + "\" was signed by:", text_color="light green", fg_color="black", font=my_font)
					Labelv.place(relx=0.5, rely=0.32, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=24, slant="roman", weight="bold", underline=False, overstrike=False)
					Labelv1 = ctk.CTkLabel(my_Frame, text=self.lookup_Alias(main_fingerprint), text_color="light green", fg_color="black", font=my_font)
					Labelv1.place(relx=0.5, rely=0.42, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", weight="normal", underline=False, overstrike=False)
					Labelv2 = ctk.CTkLabel(my_Frame, text="Key ID :" + verified.key_id, text_color="light green", fg_color="black", font=my_font)
					Labelv2.place(relx=0.5, rely=0.48, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=28, slant="roman", weight="bold", underline=False, overstrike=False)
					Labelv3 = ctk.CTkLabel(my_Frame, text="Signature is good!", text_color="light green", fg_color="black", font=my_font)
					Labelv3.place(relx=0.5, rely=0.58, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", weight="bold", underline=False, overstrike=False)
					timestampbutton = ctk.CTkButton(my_Frame, text="Check Timestamp", text_color="white", fg_color="dark green", border_width=2, border_color="white", font=my_font, command=partial(self.show_timestamp, my_Frame))
					timestampbutton.place(relx=0.5, rely=0.65, anchor="center")
					
					my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
				elif (asc_file_found and not verified) or (sig_file_found and not verified) or (manual_file_found and not verified):
					my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", weight="normal", underline=False, overstrike=False)
					Label111 = ctk.CTkLabel(my_Frame, text="The signature for file:\n", text_color="white", fg_color="black", font=my_font)
					Label111.place(relx=0.5, rely=0.4, anchor="center")
					my_font = ctk.CTkFont(family="Verdana", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
					Label222 = ctk.CTkLabel(my_Frame, text=name_of_file, text_color="white", fg_color="black", font=my_font)
					Label222.place(relx=0.5, rely=0.5, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=28, weight="bold", slant="roman", underline=True, overstrike=False)
					Label333 = ctk.CTkLabel(my_Frame, text="Is BAD!", text_color="red", fg_color="black", font=my_font)
					Label333.place(relx=0.5, rely=0.6, anchor="center")
				else:
					Label111 = ctk.CTkLabel(my_Frame, text="The signature for:\n", text_color="white", fg_color="black", font=my_font)
					Label111.place(relx=0.5, rely=0.55, anchor="center")
					my_font = ctk.CTkFont(family="Verdana", size=24, weight="bold", slant="roman", underline=False, overstrike=False)
					Label222 = ctk.CTkLabel(my_Frame, text=name_of_file, text_color="white", fg_color="black", font=my_font)
					Label222.place(relx=0.5, rely=0.6, anchor="center")
					my_font = ctk.CTkFont(family="Arial", size=38, weight="bold", slant="roman", underline=True, overstrike=False)
					Label333 = ctk.CTkLabel(my_Frame, text="Could not be verified!", text_color="red", fg_color="black", font=my_font)
					Label333.place(relx=0.5, rely=0.7, anchor="center")
					
			my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
			back_button = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.select_what_to_sign)
			back_button.place(relx=0.5, rely=0.94, anchor="center")
			
		else:
			Button3 = ctk.CTkButton(self, text="There are no public keys on the keychain. Import one now?", text_color="white", fg_color=GPG_button_color, border_width=2, border_color="white", font=my_font,command=self.importGPG_Key)
			Button3.place(relx=0.5, rely=0.53, anchor="center")
			back_button = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color="blue", border_width=2, border_color="white", font=my_font, command=self.select_what_to_sign)
			back_button.place(relx=0.5, rely=0.88, anchor="center")
	
	def avatar_decrypt_SecUSB(self, fingerprint):
		global path_to_USB_secure
		global PersonalGPGKey
		global filepathdestinationfolder
		global timeSecUSBLastModified
		PersonalGPGKey = fingerprint
		
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		full_path = filepathdestinationfolder + '/' + fingerprint + 'securefolder.tar.gz.gpg'
		if os.path.isfile(full_path):
			try:
				out_path = filepathdestinationfolder + "/" + fingerprint + 'securefolder.tar.gz'
				data_ = gpg.decrypt_file(full_path, output=out_path)
				if data_.ok:
					tar = tarfile.open(filepathdestinationfolder + "/" + fingerprint + 'securefolder.tar.gz') 
					tar.extractall(filepathdestinationfolder + "/" + 'secure')
					tar.close()		
					os.remove(filepathdestinationfolder + "/" + fingerprint + "securefolder.tar.gz")

					path_to_USB_secure = 'Secure USB folder is available'
					
					timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
					self.create_meny()
				if data_.ok == False:
					messagebox.showinfo("Information", data_.status)
					messagebox.showinfo("Information", "Trying to recover from previous session.")
					full_path_recover = filepathdestinationfolder + '/Documents/RecoveryFor' + PersonalGPGKey + 'securefolder.tar.gz.gpg'
					data_ = gpg.decrypt_file(full_path_recover, output=out_path)
					if data_.ok:
						tar = tarfile.open(filepathdestinationfolder + "/" + fingerprint + 'securefolder.tar.gz') 
						tar.extractall(filepathdestinationfolder + "/" + 'secure')
						tar.close()		
						os.remove(filepathdestinationfolder + "/" + fingerprint + "securefolder.tar.gz")

						path_to_USB_secure = 'Secure USB folder is available'
						
						timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
						self.create_meny()
						if data_.ok == False:
							messagebox.showinfo("Information", data_.status)
							messagebox.showinfo("Information", "Automatic recovery failed. Please use a backup to restore your account.")
			except FileNotFoundError:
				messagebox.showinfo("Information", "No account found.")
		else:
			messagebox.showinfo("Information", "There is no account for the selected secret key.")		
						
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
						Labelinf2 = ctk.CTkLabel(my_Frame, text="Encryption standard: RFC 4880.", text_color="white", fg_color="black", font=my_font)
						Labelinf2.place(relx=0.5, rely=0.45, anchor="center") 
						Labelinf3 = ctk.CTkLabel(my_Frame, text="Key size: 4096 bits.", text_color="white", fg_color="black", font=my_font)
						Labelinf3.place(relx=0.5, rely=0.5, anchor="center") 
						time.sleep(1)
						path_to_USB_secure = 'Secure USB folder is available'
						
						timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
						self.create_meny()
					if data_.ok == False:
						messagebox.showinfo("Information", data_.status)
						messagebox.showinfo("Information", "Trying to recover from previous session.")
						full_path_recover = filepathdestinationfolder + '/Documents/RecoveryFor' + PersonalGPGKey + 'securefolder.tar.gz.gpg'
						data_ = gpg.decrypt_file(full_path_recover, output=out_path)
						if data_.ok:
							tar = tarfile.open(filepathdestinationfolder + "/" + fingerprint + 'securefolder.tar.gz') 
							tar.extractall(filepathdestinationfolder + "/" + 'secure')
							tar.close()		
							os.remove(filepathdestinationfolder + "/" + fingerprint + "securefolder.tar.gz")

							path_to_USB_secure = 'Secure USB folder is available'
							
							timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
							self.create_meny()
							if data_.ok == False:
								messagebox.showinfo("Information", data_.status)
								messagebox.showinfo("Information", "Automatic recovery failed. Please use a backup to restore your account.")
				except FileNotFoundError:
					messagebox.showinfo("Information", "No account found.")
			else:
				messagebox.showinfo("Information", "There is no account for the selected secret key.")			
				
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="purple"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
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

				Button2 = ctk.CTkButton(my_Frame, text="Log in **", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=store_selected)
				Button2.place(relx=0.63, rely=0.49, anchor="w")
				my_font = ctk.CTkFont(family="Arial", size=14, weight="bold", slant="roman", underline=False, overstrike=False)
		
				Labelinf1 = ctk.CTkLabel(my_Frame, text="* Key is used for decrypting the offline device.", text_color="white", fg_color="black", font=my_font)
				Labelinf1.place(relx=0.5, rely=0.8, anchor="center")
				Labelinf2 = ctk.CTkLabel(my_Frame, text="** Correct operation is only possible if time and date is set correcty. If the time/date can't be stored the internal battery needs to be replaced.", text_color="white", fg_color="black", font=my_font)
				Labelinf2.place(relx=0.5, rely=0.84, anchor="center")
				Button3 = ctk.CTkButton(my_Frame, text="Update time/date", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.create_getSettimetextbox)
				Button3.place(relx=0.5, rely=0.9, anchor="center")
	
	def encrypt_SecUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="purple"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		private_keys = []
			
		gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
		
		my_font = ctk.CTkFont(family="Arial", size=18, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			global timeSecUSBLastModified
			# Try to copy over a copy of any external aliases (in case a recovery is needed in the future)
			path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
			path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
			if os.path.isfile(path_to_externalAliases):
				shutil.copy(path_to_externalAliases, path_to_externalAliases_localcopy)
				
			full_path = str(filepathdestinationfolder) + "/secure/"
		
			compressed_file = shutil.make_archive(full_path, 'gztar', full_path)
			# Encrypt the tarfile and sefely remove the unencrypted tarfile (srm)
			encrypted_data = gpg.encrypt_file(compressed_file, PersonalGPGKey, always_trust=True) 
			cmd = 'shred -zu -n7 ' + filepathdestinationfolder + "/" + "secure.tar.gz"
			os.system(cmd)

			# Write the encrypted file to disk and also write to recovery if file is not zero
			compressedoutfile = open(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', 'w')
			compressedoutfile.write(str(encrypted_data))
			compressedoutfile.close()
			if os.stat(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg').st_size > 1000:
				shutil.copy(filepathdestinationfolder + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg', filepathdestinationfolder + '/Documents/RecoveryFor' + PersonalGPGKey + 'securefolder.tar.gz.gpg')
			Labelinf = ctk.CTkLabel(my_Frame, text="You are being logged out.", text_color="white", fg_color="black", font=my_font)
			Labelinf.place(relx=0.5, rely=0.4, anchor="center") 
			Labelinf2 = ctk.CTkLabel(my_Frame, text="The device is being encrypted. Please wait..", text_color="white", fg_color="black", font=my_font)
			Labelinf2.place(relx=0.5, rely=0.45, anchor="center") 
			Labelinf3 = ctk.CTkLabel(my_Frame, text="(Encryption standard: RFC 4880)", text_color="white", fg_color="black", font=my_font)
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
	
	def new_secureUSB_Pre(self):
		# Make sure time and date is correct before creating any new keys 
		global filepathdestinationfolder
		global SecUSB_button_color
			
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		pathtobackg = "/home/user1/images/bluebackground.jpg"
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_Frame.focus_set()
		my_Frame.focus_force()			
		
		def do_new_secureUSB_Pre():
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
			self.new_secureUSB()
			
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
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2025)
		cal.place(relx=0.65, rely=0.73, anchor="e")
			
		Button = ctk.CTkButton(my_Frame, text="Next!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_new_secureUSB_Pre)
		Button.place(relx=0.5, rely=0.86, anchor="center")
						
	def new_secureUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		users_avatar_name = 'Bobby'
		new_Avatar_Entry = 'Anon'
		
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
		
		def show_progress(_value):
			my_font = ctk.CTkFont(family="Helvetica", size=26, weight="bold", slant="roman", underline=False, overstrike=False)
			LLabel3 = ctk.CTkLabel(my_Frame, text="Progress......... " + _value + " %", text_color="white", fg_color="black", font=my_font)
			LLabel3.place(relx=0.5, rely=0.71, anchor="center")
		
		def do_new_secureUSB_pre():
			time.sleep(3)
			show_progress('25')
			tk.messagebox.showinfo('Information', 'Now we will generate the Offline device key. Move mouse around for randomness.')
			do_new_secureUSB()
					
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
				nr_avatars = 0
				
				# Make sure folder secure is not already available
				full_path = str(filepathdestinationfolder) + "/secure"
				cmd = 'find ' +  full_path + ' -type f -exec shred -zu {} \\;'
				os.system(cmd)
				cmd = 'rm -r ' +  full_path
				os.system(cmd)
			
				# Create a GPG master key for personal use, namePrivateEntry emailPrivateEntry Secret_passphrasePrivateEntry
				input_data_priv = gpg.gen_key_input(key_type='rsa', name_real=namePrivateEntry.get(), expire_date='0', key_length='4096', name_email=emailPrivateEntry.get(), passphrase=Secret_passphrasePrivateEntry.get())
				privatekey = gpg.gen_key(input_data_priv)
				
				privatekeyfilename = 'privateKey' + privatekey.fingerprint + ".gpg"
				full_path_private = filepathdestinationfolder + "/" + privatekeyfilename
			
				path_to_USB_secure = 'Secure USB folder is available'
				PersonalGPGKey = privatekey.fingerprint
				
				new_external_alias = [PersonalGPGKey, users_avatar_name_var.get(), new_Avatar_Entry]
				# Add an entry in External alias file for avatar login (if less than 4 already)		
				path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
				if not os.path.isfile(path_to_externalAliases):
					f = open(path_to_externalAliases, 'w')
					writer = csv.writer(f)
					writer.writerow(new_external_alias)
					f.close()
				else:
					try:
						with open(path_to_externalAliases) as f:
							nr_avatars = sum(1 for line in f)
					except FileNotFoundError:
						messagebox.showinfo("Information", "No Alias file found.")
					if nr_avatars < 4:
						with open(path_to_externalAliases, 'a') as f:
							writer = csv.writer(f)
							writer.writerow(new_external_alias)
							
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
				
				# Make local copy for external alias (in case of recovery on new device)
				path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
				with open(path_to_externalAliases_localcopy, 'w') as f:
					writer = csv.writer(f)
					writer.writerow(new_external_alias)
					
				self.new_Alias_real_name(privatekey.fingerprint, "Offline device Key")
				
				c = open(full_path + "passwords.txt", 'w')
				c.write(str("Passwords\n___________________________________\n\nYubikey\n\n   OpenPGP Admin PIN:  \n\n   OpenPGP PIN:  \n\n   Comment:  \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n\nUser/account: \n\n   Password: \n\n   Comment: \n\n___________________________________\n"))
				c.close()
				c = open(full_path_wallets + "wallets.txt", 'w')
				c.write(str("Wallets\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n\n___________________________________\n\nName: \n\n   Seed words/key: \n\n   Comment: \n"))
				c.close()
				with open(full_path_settings_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['Username', 'Theme', 'Colors']
				with open(full_path_paperwallets_file, 'w', newline='') as file:
					writer = csv.writer(file)
					field = ['Name', 'Datecreated', 'Pubkey', 'wif', 'mnemonic', 'amount', 'Category']
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

				iconopen_image = ctk.CTkImage(light_image=Image.open("/home/user1/images/iconopen.png"), dark_image=Image.open("/home/user1/images/iconopen.png"), size=(30, 30))
				openlock_Label = ctk.CTkLabel(self, text="", image=iconopen_image)
				openlock_Label.place(relx=0.02, rely=0.94, anchor="w")

				self.create_meny()
		
		pathtobackg = self.get_background_image()
		
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
		
		users_avatar_name_var = StringVar()
		
		def limitSizeAvatarname(*args):
			value = users_avatar_name_var.get()
			if len(value) > 17: users_avatar_name_var.set(value[:17])
							
		users_avatar_name_var = ctk.StringVar(value=users_avatar_name)
		users_avatar_name_var.trace('w', limitSizeAvatarname)
		
		userNameEntry = ctk.CTkEntry(my_Frame, placeholder_text=users_avatar_name, textvariable=users_avatar_name_var, width=320, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
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
		
		Button = ctk.CTkButton(my_Frame, text="Create new account *", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_new_secureUSB_pre)
		Button.place(relx=0.49, rely=0.53, anchor="w")
		my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
		LLabel = ctk.CTkLabel(my_Frame, text="* This can take a while.. Move mouse around to create randomness...\nFollow all the instructions for the rest of the setup.", text_color="white", fg_color="black", font=my_font)
		LLabel.place(relx=0.5, rely=0.78, anchor="center")
	
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
			self.add_history("Account backup made to external storage media.")
			messagebox.showinfo("Information", "Backup to USB-device successfull. Please remove USB-device.")
		else:
			print("Secure folder not available")
			
	def copy_SecUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		def do_copy_SecUSB():
			global filepathdestinationfolder
			global PersonalGPGKey
			failedExport = 0
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			if path_to_USB_secure == 'Secure USB folder is available':
				# Try to copy over a copy of any external aliases (in case a recovery is needed in the future)
				path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
				path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
				if os.path.isfile(path_to_externalAliases):
					shutil.copy(path_to_externalAliases, path_to_externalAliases_localcopy)
				full_path = str(filepathdestinationfolder) + "/secure/"
				# Ask the user if the private keys on the local keychain really has been backed-up to the secure archive
				answer = messagebox.askquestion('Important!', 'Has all the private keys been backed-up to the secure archive?')
				if answer == 'yes':
					messagebox.showinfo("Information", "Insert the USB-device and then click \"OK\".")
					time.sleep(2)
					messagebox.showinfo("Information", "Double click to select the USB-device and then select the directory where to place the backup.")
					time.sleep(2)
					USBdevice = filedialog.askdirectory(initialdir='/media/user1/')
					if USBdevice == '/home' or USBdevice == '/home/user1' or USBdevice == '/home/user1/secure' or USBdevice == '/media' or USBdevice == '/media/user1':
						messagebox.showinfo("Alert!", "This is not an external USB-device. Are you sure you double-clicked on the USB-device?")
						self.do_copy_SecUSB()
					else:
						path_to_privatekeyfile = USBdevice + "/" + 'privateKey' + PersonalGPGKey + '.gpg'
						path_to_archive = USBdevice + "/" + PersonalGPGKey + 'securefolder.tar.gz.gpg'
						
						USER_INP = simpledialog.askstring(title="Input required!", prompt="Name for Backup files (optional):")
						
						if USER_INP != '':
							path_to_privatekeyfile = USBdevice + "/" + USER_INP + ".gpg"
							path_to_archive = USBdevice + "/" + USER_INP + 'securefolder.tar.gz.gpg'
						
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
						compressedoutfile = open(path_to_archive, 'w')
						compressedoutfile.write(str(encrypted_data))
						compressedoutfile.close()
						
						# Export the private key and write file to USB-device
						ascii_armored_private_key = gpg.export_keys(PersonalGPGKey, True, expect_passphrase=False)
						f2 = open(path_to_privatekeyfile, 'w')
						f2.write(ascii_armored_private_key)
						f2.close()
						
						if os.path.isfile(path_to_archive):
							if os.path.isfile(path_to_privatekeyfile):
								messagebox.showinfo("Information", "Backup files has been written to the USB-device!")
								self.add_history("Account backup made to an USB-device!")
							else:
								messagebox.showinfo("Information", "That didn't work!\n\nBackup file for private key could not be written to the USB-device!")
						else:
							messagebox.showinfo("Information", "That didn't work!\n\nBackup file for secure archive could not be written to the USB-device!")
						self.check_SecUSB("none")
				else:
					messagebox.showinfo("Information", "Please backup the private keys from the local keychain to your Secure archive before backing up the account (under menu \"GPG -> Backup keys\").")
	
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			global timeSecUSBLastModified
			Label1 = ctk.CTkLabel(my_Frame, text="Backup all files and key's to a USB-device.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.1, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			
			Label2 = ctk.CTkLabel(my_Frame, text="An encrypted backup of the device will be stored on the USB-device, together with a copy of the accounts login key (for decrypting).", text_color="white", fg_color="black", font=my_font)
			Label2.place(relx=0.5, rely=0.18, anchor="center")
			
			Label22 = ctk.CTkLabel(my_Frame, text="You can give the backup files a name or let the system name the two files. The files should be kept in the same folder.", text_color="white", fg_color="black", font=my_font)
			Label22.place(relx=0.5, rely=0.24, anchor="center")
			
			Label3 = ctk.CTkLabel(my_Frame, text="(Make sure that any changes on the local keychain has been backed up before proceeding.)", text_color="white", fg_color="black", font=my_font)
			Label3.place(relx=0.5, rely=0.3, anchor="center")
			
			theButton = ctk.CTkButton(my_Frame, text="Make a backup!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_copy_SecUSB)
			theButton.place(relx=0.5, rely=0.38, anchor="center")
	
	def clone_microSD(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			Label1 = ctk.CTkLabel(my_Frame, text="Clone the system to a new microSD-card", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.1, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
				
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			Labelinf = ctk.CTkLabel(my_Frame, text="Cloning the device requires a microSD-card with minimum 32 GB.", text_color="white", fg_color="black", font=my_font)
			Labelinf.place(relx=0.5, rely=0.18, anchor="center") 

			Label2inf = ctk.CTkLabel(my_Frame, text="Use a USB-to-microSD adapter to connect the microSD-card.", text_color="white", fg_color="black", font=my_font)
			Label2inf.place(relx=0.5, rely=0.24, anchor="center")
						
			copySDButton = ctk.CTkButton(my_Frame, text="Clone the microSD card", text_color="white", font=my_font, border_width=2, border_color="white", fg_color=SecUSB_button_color, command=self.cloneSDcard)
			copySDButton.place(relx=0.5, rely=0.38, anchor="center")
			
	def restore_SecUSB(self):
		global path_to_USB_secure
		global timeSecUSBLastModified
		global filepathdestinationfolder
		global PersonalGPGKey
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()	
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			Label1 = ctk.CTkLabel(my_Frame, text="Restore an account from a backup on a USB-device.", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.5, rely=0.1, anchor="center")
			
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
				
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			Labelinf = ctk.CTkLabel(my_Frame, text="Connect a USB-device that has both the encrypted file and the correct key to decrypt it.", text_color="white", fg_color="black", font=my_font)
			Labelinf.place(relx=0.5, rely=0.18, anchor="center") 

			Label2inf = ctk.CTkLabel(my_Frame, text="After restoration has completed you need to manually restore keys to the new local keychain.", text_color="white", fg_color="black", font=my_font)
			Label2inf.place(relx=0.5, rely=0.24, anchor="center")
			
			ButtonRestore= ctk.CTkButton(my_Frame, text="Restore from USB", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.restoreFromencrypted_SecUSB)
			ButtonRestore.place(relx=0.5, rely=0.38, anchor="center")
					
	def cloneSDcard( self):
		global path_to_USB_secure
		global SecUSB_button_color
		global filepathdestinationfolder
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=4,
		border_color="purple"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
		
		if path_to_USB_secure == 'Secure USB folder is available':
			answer = messagebox.askquestion('Information!', 'Before cloning the system you will be logged out (all changes will be saved first). Insert the SD-card with adaptor now. From device is /dev/mmcblk0. Check the tick-box for new partition UUIDs. Are you SURE you want to proceed?')
			if answer == 'yes':
				full_path = str(filepathdestinationfolder) + "/secure/"
				self.add_history("System cloned to external storage media.")
				
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
				self.check_SecUSB("none")
						
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
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_Frame.focus_set()
		my_Frame.focus_force()			
		
		def avatar_decrypt_SecUSB_and_restore(fingerprint):
			global path_to_USB_secure
			global PersonalGPGKey
			global filepathdestinationfolder
			global timeSecUSBLastModified
			PersonalGPGKey = fingerprint
			new_Avatar_Entry = "Recovered account"
			recovered_external_alias = [fingerprint, new_Avatar_Entry, 'Anon']
			gpg = gnupg.GPG(gnupghome='/home/user1/.gnupg/')
			
			full_path = filepathdestinationfolder + '/' + fingerprint + 'securefolder.tar.gz.gpg'
			out_path = filepathdestinationfolder + '/' + fingerprint + 'securefolder.tar.gz'
			# Decrypt with a selected avatar
			if os.path.isfile(full_path):
				# Decrypt and recover external alias from user secure archive 
				data_ = gpg.decrypt_file(full_path, output=out_path)
				if data_.ok:
					tar = tarfile.open(filepathdestinationfolder + "/" + fingerprint + 'securefolder.tar.gz') 
					tar.extractall(filepathdestinationfolder + '/secure')
					tar.close()		
					os.remove(filepathdestinationfolder + "/" + fingerprint + "securefolder.tar.gz")
					
					# Restore external alias from local copy (if any)
					path_to_externalAliases_localcopy = str(filepathdestinationfolder) + "/secure/externalAliases_localcopy.csv"
					
					if os.path.isfile(path_to_externalAliases_localcopy):
						with open(path_to_externalAliases_localcopy, 'r') as file:
							csvfile = csv.reader(file)
							for row in csvfile:
								if row[0] == fingerprint:
									recovered_external_alias = [fingerprint, row[1], row[2]]
					
					# If own avatar in secure archive copy over to device
					if recovered_external_alias[2] != 'Anon' and recovered_external_alias[2] != 'Male' and recovered_external_alias[2] != 'Woman' and recovered_external_alias[2] != 'Boy' and recovered_external_alias[2] != 'Girl' and recovered_external_alias[2] != 'Yin Yang' and recovered_external_alias[2] != 'Skull':
						pathtopicturearchivelocation = filepathdestinationfolder + "/secure/" + PersonalGPGKey + '.png'
						pathtopicturelocation = filepathdestinationfolder + "/Documents/" + PersonalGPGKey + '.png'
						if os.path.isfile(pathtopicturearchivelocation):
							shutil.copy(pathtopicturearchivelocation, pathtopicturelocation)
						else:
							# Pic file not found in secure folder so set external avatar to anon again
							recovered_external_alias[2] = 'Anon'
					 
					# Add an entry in External alias file for avatar login (if less than 4 already)
					path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
					if not os.path.isfile(path_to_externalAliases):
						f = open(path_to_externalAliases, 'w')
						writer = csv.writer(f)
						writer.writerow(recovered_external_alias)
						f.close()
					else:
						with open(path_to_externalAliases) as f:
							nr_avatars = sum(1 for line in f)
						
						if nr_avatars < 4:
							with open(path_to_externalAliases, 'a') as f:
								writer = csv.writer(f)
								writer.writerow(recovered_external_alias)
						
					path_to_USB_secure = 'Secure USB folder is available'
					
					timeSecUSBLastModified = str(time.ctime(os.path.getmtime(full_path)))
					return True
				if data_.ok == False:
					messagebox.showinfo("Information", data_.status)
					return False
				return False	
				
		def do_restoreFromencrypted_SecUSB():
			global filepathdestinationfolder
			key_fingerprint = ''
			
			def decrypt_and_restore():
				# Add an entry in External alias file for avatar login (if less than 4 already)
				new_Avatar_Entry = "Recovered account"
				recoveredPersonalGPGKey = import_result.fingerprints[0]	
				new_external_alias = [recoveredPersonalGPGKey, new_Avatar_Entry, 'Anon']
				path_to_externalAliases = str(filepathdestinationfolder) + "/Documents/externalAliases.csv"
				if not os.path.isfile(path_to_externalAliases):
					f = open(path_to_externalAliases, 'w')
					writer = csv.writer(f)
					writer.writerow(new_external_alias)
					f.close()
				else:
					try:
						with open(path_to_externalAliases) as f:
							nr_avatars = sum(1 for line in f)
					except FileNotFoundError:
						messagebox.showinfo("Information", "No Alias file found.")
					if nr_avatars < 4:
						with open(path_to_externalAliases, 'a') as f:
							writer = csv.writer(f)
							writer.writerow(new_external_alias)
							
			# Set the date and time
			thedate = cal.get_date()
			thetime = time_picker.time()
			
			thedatestr = str('sudo date -s \'' + str(thedate) + ' ' + str(thetime[0]) + ':' + str(thetime[1]) + ':00\'')			
			os.system(thedatestr)
			thestr = 'sudo hwclock -w'	
			os.system(thestr)
			os.system(thestr)
			
			# Select the file with the private key and scan it for fingerprint
			messagebox.showinfo("Information", "Insert the USB-device with the backup data and click \"OK\".")
			time.sleep(2)
			messagebox.showinfo("Information", "Select the key for the account (could start with \"privateKey\" and ends with \".gpg\" or be with a custom name).")
			time.sleep(2)
			
			filepathkeyfile = filedialog.askopenfilename(initialdir='/media/user1')	
			directory_path = os.path.dirname(os.path.abspath(filepathkeyfile))
			#base_name = os.path.basename(filepathkeyfile)
			file_name = Path(filepathkeyfile).stem
			
			keys = gpg.scan_keys(filepathkeyfile)
			key_fingerprint = str(keys.fingerprints[0])
			
			# Restore private key
			full_path = filepathdestinationfolder + '/privateKey' + key_fingerprint + '.gpg'
			# Check if the private key already is in the /user/home directory
			if os.path.isfile(full_path):
				answer = messagebox.askquestion('WARNING!', 'WARNING! There\'s already a key with that fingerprint on the offline device! Are you SURE you want to proceed?')
				if answer == 'yes':
					# Copy over the encrypted private key
					shutil.copy(filepathkeyfile, full_path)
					import_result = gpg.import_keys_file(full_path)
					gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
				else:
					messagebox.showinfo("Information", "OK. Keeping the existing key on the offline device.")
			else:
				# Copy over the encrypted private key
				shutil.copy(filepathkeyfile, full_path)
				import_result = gpg.import_keys_file(full_path)
				gpg.trust_keys(import_result.fingerprints, trustlevel='TRUST_ULTIMATE')
			
			# Copy over the archive file
			archive_path = directory_path + '/' + key_fingerprint + 'securefolder.tar.gz.gpg'
			archive_path_custom = directory_path + '/' + file_name + 'securefolder.tar.gz.gpg' 
			
			# Copy secure archive file
			full_path_archive = filepathdestinationfolder + '/' + key_fingerprint + 'securefolder.tar.gz.gpg'
			if os.path.isfile(full_path_archive):
				answer = messagebox.askquestion('WARNING!', 'WARNING! There already a secure archive on the offline device for that specific key! Are you SURE you want to proceed?')
				if answer == 'yes':
					# Try to automatically copy over a file with custom or proper name
					if os.path.isfile(directory_path + '/' + file_name + 'securefolder.tar.gz.gpg'):
						shutil.copy(directory_path + '/' + file_name + 'securefolder.tar.gz.gpg', full_path_archive)
					elif os.path.isfile(directory_path + '/' + key_fingerprint + 'securefolder.tar.gz.gpg'):
						shutil.copy(directory_path + '/' + key_fingerprint + 'securefolder.tar.gz.gpg', full_path_archive)
					else:
						messagebox.showinfo("Information", "Now select the encrypted backup archive (could starts with the key's fingerprint and ends with \".securefolder.tar.gz.gpg\").")
						time.sleep(2)
						filepatharchivefile = filedialog.askopenfilename(initialdir='/media/user1')	
						shutil.copy(filepatharchivefile, full_path_archive)
					
					# Decrypt and cover any external alias information
					result = avatar_decrypt_SecUSB_and_restore(key_fingerprint)
					if result:
						messagebox.showinfo("Information", "The device has been restored from backup. Make sure to also restore/import all relevant key's from your Secure archive.")
					else:
						messagebox.showinfo("Information", "That didn't work!") 
				else:
					messagebox.showinfo("Information", "OK. Keeping the existing secure archive on the offline device.")
			else:
				# Try to automatically copy over a file with custom or proper name
				if os.path.isfile(directory_path + '/' + file_name + 'securefolder.tar.gz.gpg'):
					shutil.copy(directory_path + '/' + file_name + 'securefolder.tar.gz.gpg', full_path_archive)
				elif os.path.isfile(directory_path + '/' + key_fingerprint + 'securefolder.tar.gz.gpg'):
					shutil.copy(directory_path + '/' + key_fingerprint + 'securefolder.tar.gz.gpg', full_path_archive)
				else:
					messagebox.showinfo("Information", "Now select the encrypted backup archive (could starts with the key's fingerprint and ends with \".securefolder.tar.gz.gpg\").")
					time.sleep(2)
					filepatharchivefile = filedialog.askopenfilename(initialdir='/media/user1')	
					shutil.copy(filepatharchivefile, full_path_archive)
				result = avatar_decrypt_SecUSB_and_restore(key_fingerprint)
				if result:
					messagebox.showinfo("Information", "The device has been restored from backup. Make sure to also restore/import all relevant key's from your Secure archive.")
				else:
					messagebox.showinfo("Information", "That didn't work!")
			self.encrypt_SecUSB()
			
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
		
		cal = DateEntry(my_Frame, width=20, text_color="white", bg="darkblue", fg="black", year=2025)
		cal.place(relx=0.65, rely=0.73, anchor="e")
			
		Button = ctk.CTkButton(my_Frame, text="Start restoring from backup!", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=do_restoreFromencrypted_SecUSB)
		Button.place(relx=0.5, rely=0.86, anchor="center")
				
	def check_SecUSB(self, key):
		global filepathdestinationfolder
		global SecUSB_button_color
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200,                                                                                                                                                                                                                                                                        
		height=650,
		border_width=4,
		border_color="blue"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		pathtobackg = self.get_background_image()
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		
		my_text = ctk.CTkTextbox(my_Frame, width=1200, height=650, corner_radius=1, border_width=1, border_color="purple", border_spacing=10, fg_color="black", text_color="white", font=("Helvetica", 18), wrap="word", activate_scrollbars = True, scrollbar_button_color="blue", scrollbar_button_hover_color="red")
		
		if path_to_USB_secure == 'Secure USB folder is available':
			my_text.insert('end', "\n\n\n" + "\n")
			my_text.insert('end', "Secure archive" + "\n")
			my_text.insert('end', "==================================================================" + "\n")
			my_text.insert('end', "Encryption standard: RFC 4880" + "\n")
			my_text.insert('end', "Key size: 4096 bits" + "\n")
			my_text.insert('end', "==================================================================" + "\n")
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
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
			filterLabel = ctk.CTkLabel(my_Frame, text="Filter on:", text_color="white", font=my_font, fg_color="black")
			filterLabel.place(relx=0.9, rely=0.2, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Button4 = ctk.CTkButton(my_Frame, text="Private keys", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=150, height=28, font=my_font, command=partial(self.check_SecUSB, "privatekeys"))
			Button4.place(relx=0.9, rely=0.25, anchor="center")
			Button5 = ctk.CTkButton(my_Frame, text="Public keys", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=150, height=28, font=my_font, command=partial(self.check_SecUSB, "publickeys"))
			Button5.place(relx=0.9, rely=0.3, anchor="center")
			Button6 = ctk.CTkButton(my_Frame, text="Wallets", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=150, height=28, font=my_font, command=partial(self.check_SecUSB, "wallets"))
			Button6.place(relx=0.9, rely=0.35, anchor="center")
			Button7 = ctk.CTkButton(my_Frame, text="ID's", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=150, height=28, font=my_font, command=partial(self.check_SecUSB, "ids"))
			Button7.place(relx=0.9, rely=0.4, anchor="center")
			Button8 = ctk.CTkButton(my_Frame, text="No filter", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=150, height=28, font=my_font, command=partial(self.check_SecUSB, "none"))
			Button8.place(relx=0.9, rely=0.45, anchor="center")

			if key == 'privatekeys':
				my_text.insert('end', "\n" + "All private keys in the secure archive:\n")
				my_text.insert('end', "------------------------------------------------------" + "\n")
				full_path = str(filepathdestinationfolder) + "/secure/keys/privateKey*"
				# List the SELECTED file on the Secure USB
				for name in glob.glob(full_path, recursive=True): 
					my_text.insert('end', name + '\n')
			elif key == 'publickeys':
				my_text.insert('end', "\n" + "All public keys in the secure archive:\n")
				my_text.insert('end', "------------------------------------------------------" + "\n")
				full_path = str(filepathdestinationfolder) + "/secure/keys/publicKey*"
				# List the SELECTED file on the Secure USB
				for name in glob.glob(full_path, recursive=True): 
					my_text.insert('end', name + '\n')
			elif key == 'wallets':
				my_text.insert('end', "\n" + "All wallets files in the secure archive:\n")
				my_text.insert('end', "------------------------------------------------------" + "\n")
				full_path = str(filepathdestinationfolder) + "/secure/wallets/**/*"
				# List the SELECTED file on the Secure USB
				for name in glob.glob(full_path, recursive=True): 
					my_text.insert('end', name + '\n')
			elif key == 'ids':
				my_text.insert('end', "\n" + "All ID's in the secure archive:\n")
				my_text.insert('end', "------------------------------------------------------" + "\n")
				full_path = str(filepathdestinationfolder) + "/secure/ID/ICON*"
				# List the SELECTED file on the Secure USB
				for name in glob.glob(full_path, recursive=True): 
					my_text.insert('end', name + '\n')
			else:
				my_text.insert('end', "\n" + "All files in the secure archive. (")
				size = 0.0
				
				secure_folder_path = filepathdestinationfolder + '/secure'
				the_dir = Path(secure_folder_path)
				size = sum(f.stat().st_size for f in the_dir.glob('**/*') if f.is_file())
				size_kb = size / 1024
				size_mb = size_kb / 1024
				answer = str(round(size_mb, 2))
				my_text.insert('end', answer + " MB):" + "\n")
				my_text.insert('end', "------------------------------------------------------" + "\n")
				full_path = str(filepathdestinationfolder) + "/secure/**/*"
				# List the file on the Secure USB
				for name in glob.glob(full_path, recursive=True): 
					my_text.insert('end', name + '\n')
		else:
			my_text.insert('end', '\n\n\n\n                                                                                            You are not logged in.' + "\n") 
		
		my_text.configure(state="disabled")
		my_text.place(relx=0.5, rely=0.5, anchor="center")
	
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
		self.create_secusbtextbox()
			
	def addfile_SecUSB(self):
		global filepathdestinationfolder
		messagebox.showinfo("Information", "Insert USB-device.") 
		time.sleep(2)
		messagebox.showinfo("Information", "Select the file to add to the secure archive.")
		time.sleep(2)
		filepathtocopy = filedialog.askopenfilename(initialdir='/media/user1')
		messagebox.showinfo("Information", "Select destination folder.")
		full_path = filepathdestinationfolder + '/secure'
		filepathdestinationfolderfull = filedialog.askdirectory(initialdir=full_path)
		shutil.copy(filepathtocopy, filepathdestinationfolderfull)
		messagebox.showinfo("Information", "File has been added.")
		self.create_secusbtextbox()
	
	def add_directory_SecUSB(self):
		global filepathdestinationfolder
		
		USER_INP = simpledialog.askstring(title="Input required!", prompt="Name of new directory:")
		messagebox.showinfo("Information", "Select where to place directory (under \"/home/user1/secure\").")
		
		newfoldername = filedialog.askdirectory(initialdir='/home/user1/secure')

		path = os.path.join(newfoldername, USER_INP)
		os.makedirs(path)
		self.create_secusbtextbox()					
						
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
		self.create_secusbtextbox()
		
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
		self.create_secusbtextbox()
	
	def create_Bitcointextbox(self, theFlag):
		global filepathdestinationfolder
		global SecUSB_button_color
		global view_btcAddr
		global use_filter
		global use_status
		
		view_btcAddr = 'none'
		SATs_value = 0.0
		
		if theFlag == 'all':
			use_filter = 'all'
			use_status = 'all'
			
		path_to_wallets = filepathdestinationfolder + "/secure/wallets/paperwallets/paperwallets.csv"

		def setFlagAll():
			global use_filter
			global use_status
			use_status = 'all'
			view_btcAddr = 'none'
			self.do_show_Bitcoinwallets(theFlag)
		def setFlagCreated():
			global use_filter
			global use_status
			use_status = 'Timestamp'
			view_btcAddr = 'none'
			self.do_show_Bitcoinwallets(theFlag)
		def setFlagActive():
			global use_filter
			global use_status
			use_status = 'Active'
			view_btcAddr = 'none'
			self.do_show_Bitcoinwallets(theFlag)
		def setFlagNonKYC():
			global use_filter
			global use_status
			use_status = 'Non KYC'
			view_btcAddr = 'none'
			self.do_show_Bitcoinwallets(theFlag)
		def setFlagSpent():
			global use_filter
			global use_status
			use_status = 'Spent'
			view_btcAddr = 'none'
			self.do_show_Bitcoinwallets(theFlag)
		
		# scrolleable frame
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="black",
		fg_color="black"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
		
		bottom_Frame = ctk.CTkScrollableFrame(my_Frame, 
		width=1150, 
		height=570,
		orientation="vertical",
		border_width=2,
		border_color="white",
		fg_color="black"
		)
		bottom_Frame._scrollbar.configure(height=0)
		bottom_Frame.place(x=10, y=60, anchor="nw")
		
		# Make the buttons on the top of the frame on the frame
		if path_to_USB_secure == 'Secure USB folder is available':
			# Fix_csv to 6 collumns
			fix_csv = self.fix_csvfile()
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
			filter_all_Button = ctk.CTkButton(my_Frame, text="All wallets", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
			filter_all_Button.place(relx=0.1, y=30, anchor="center")
			
			filter_Button = ctk.CTkButton(my_Frame, text="Use wallet filter", fg_color="dark orange", text_color="black", border_width=2, border_color="white", font=my_font, command=self.do_show_Bitcoinwallets_start)
			filter_Button.place(relx=0.25, y=30, anchor="center")
			
			total_amount_BTC = self.get_total_BTC_amount()
			
			if total_amount_BTC > 100:
				BTCLabel = ctk.CTkLabel(my_Frame, text="Bitcoin total amount: " + str(int(total_amount_BTC)) + ' sats', text_color="white", fg_color="black", font=my_font)
				BTCLabel.place(relx=0.45, y=30, anchor="w")
			else:
				BTCLabel = ctk.CTkLabel(my_Frame, text="Bitcoin total amount: " + str(total_amount_BTC) + ' BTC', text_color="white", fg_color="black", font=my_font)
				BTCLabel.place(relx=0.45, y=30, anchor="w")
			addButton = ctk.CTkButton(my_Frame, text="Add new wallet", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.do_new_Bitcoinwallet)
			addButton.place(relx=0.9, y=30, anchor="center")
			
			amount = 0.0 
			amount_round = 0.0
			loopcount = 0
			row_count = 0
			col_count = 0
			
			try:
				with open(path_to_wallets, 'r') as file:
					csvfile = csv.reader(file)
					for lines in csvfile:
						if lines:
							my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
							if lines[0] == 'Timestamp' and (theFlag == 'Timestamp' or theFlag == 'all'):
								if lines[5] == 'None':
									my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n' + 'Timestamp\n Document', anchor='center', text_color="white", fg_color="purple", border_width=4, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								else:
									my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n' + 'Timestamp\nSignature + Document', anchor='center', text_color="white", fg_color="purple", border_width=4, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								Button5.grid(row = row_count, column = col_count, sticky = W, padx = 30, pady = 10)
								col_count = col_count + 1
								if col_count == 4:
									col_count = 0
									row_count = row_count + 1
								
							if lines[0] == 'Active' and (theFlag == 'Active' or theFlag == 'all'):
								if float(lines[5]) < 0.01:
									SATs_value = float(lines[5]) * 100000000
									SATs_value_rounded = round(SATs_value, 7)
									SATs_value_int = int(SATs_value_rounded)
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n\n' + str(SATs_value_int) + ' sats', anchor='nc', text_color="white", fg_color="green4", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								else:
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n\n' + lines[5] + ' BTC', anchor='center', text_color="white", fg_color="green4", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								
								Button5.grid(row = row_count, column = col_count, sticky = W, padx = 30, pady = 10)
								col_count = col_count + 1
								if col_count == 4:
									col_count = 0
									row_count = row_count + 1
								amount = amount + float(lines[5])
								
							if lines[0] == 'Spent' and (theFlag == 'Spent' or theFlag == 'all'):
								if float(lines[5]) < 0.01:
									SATs_value = float(lines[5]) * 100000000
									SATs_value_rounded = round(SATs_value, 7)
									SATs_value_int = int(SATs_value_rounded)
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n\n' + str(SATs_value_int) + ' sats', anchor='nc', text_color="black", fg_color="grey", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								else:
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n\n' + lines[5] + ' BTC', anchor='center', text_color="black", fg_color="grey", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								
								Button5.grid(row = row_count, column = col_count, sticky = W, padx = 30, pady = 10)
								col_count = col_count + 1
								if col_count == 4:
									col_count = 0
									row_count = row_count + 1
								
							if lines[0] == 'Non KYC' and (theFlag == 'Non KYC' or theFlag == 'all'):
								if float(lines[5]) < 0.01:
									SATs_value = float(lines[5]) * 100000000
									SATs_value_rounded = round(SATs_value, 7)
									SATs_value_int = int(SATs_value_rounded)
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n\n' + str(SATs_value_int) + ' sats', anchor='nc', text_color="white", fg_color="dark green", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								else:
									Button5 = ctk.CTkButton(bottom_Frame, text='Created: ' + lines[1] + '\n\n' + lines[5] + ' BTC', anchor='center', text_color="white", fg_color="dark green", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.do_edit_Bitcoinwallets, lines[2]))
								
								Button5.grid(row = row_count, column = col_count, sticky = W, padx = 30, pady = 10)
								col_count = col_count + 1
								if col_count == 4:
									col_count = 0
									row_count = row_count + 1

								amount = amount + float(lines[5])
							loopcount = loopcount + 1
							
			except FileNotFoundError:
				messagebox.showinfo("Information", "No paper wallet file found.")
			amount_round = round(amount, 7)	
			row_count = row_count + 1
			
		else:
			my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
			Button = ctk.CTkButton(my_Frame, text="You are not logged in. Paper wallets can\'t be displayed.", font=my_font, text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", command=self.create_SecUSBmeny)
			Button.pack(pady=240)
			Label = ctk.CTkLabel(my_Frame, text=' ', text_color="white", font=("Arial", 18), fg_color="black", underline=True)
			Label.pack(pady=300)
	
	def copy2clip(self, txt):
		r = Tk()
		r.withdraw()
		r.clipboard_clear()
		r.clipboard_append(txt)
		r.update()
		r.destroy()
	
	def change_view_btcAddr(self, new_view_btcAddr):
		global view_btcAddr
		global ext_flag
		view_btcAddr = new_view_btcAddr
		self.do_show_Bitcoinwallets(ext_flag)
		
	def change_flag_and_reset_btcAddr(self, newFlag):
		global view_btcAddr
		global ext_flag
		ext_flag = newFlag
		view_btcAddr = 'none'
		self.do_show_Bitcoinwallets(ext_flag)
	
	def do_show_Bitcoinwallets_start(self):
		global view_btcAddr
		global use_filter
		global use_status
		use_status = 'all'
		use_filter = 'all'
		view_btcAddr = 'none'
		self.do_show_Bitcoinwallets('all')
			
	def do_show_Bitcoinwallets(self, theFlag):
		global Boltcard_button_color
		global filepathdestinationfolder
		global view_btcAddr
		global ext_flag
		global use_filter
		global use_status
		global categories_list
		global do_sort
		
		SATs_value = 0.0
		
		external_BTC_categories_file = filepathdestinationfolder + "/secure/BTC_categories.csv"	
		path_to_wallets = filepathdestinationfolder + "/secure/wallets/paperwallets/paperwallets.csv"
		pathtobackg = str(filepathdestinationfolder) + "/images/BTC_icon_black.jpg"
		
		categories_list = []
		status_list = ['Timestamp', 'Active', 'Non KYC', 'Spent']
		
		def change_sort_flag_to_date():
			global do_sort
			do_sort = 'date'
			self.do_show_Bitcoinwallets(use_status)
		
		def change_sort_flag_to_value():
			global do_sort
			do_sort = 'value'
			self.do_show_Bitcoinwallets(use_status)
			
		def change_sort_flag_to_none():
			global use_filter
			global use_status
			use_status = 'all'
			use_filter = 'all'
			self.do_show_Bitcoinwallets(use_status)
			
		def filter_on_category_and_status():
			global use_filter
			global use_status
			global view_btcAddr
			view_btcAddr = 'none'
			use_filter = clicked.get()
			use_status = clicked2.get()
			if use_filter == 'Select category':
				use_filter = 'all'
			if use_status == 'Select status':
				use_status = 'all'
			self.do_show_Bitcoinwallets(use_status)
			
		def get_categories():
			global categories_list
			with open(path_to_wallets, 'r') as file:
				csvfile = csv.reader(file)
				for row in csvfile:
					if row[6] not in categories_list and row[6] != "Not payed" and row[6] != "Payed":
						categories_list.append(row[6])
			
		main_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=2,
		border_color="black",
		fg_color="black"
		)
		main_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		top_Frame = ctk.CTkFrame(main_Frame, 
		width=1200, 
		height=60,
		border_width=2,
		border_color="black",
		fg_color="black"
		)
		top_Frame.place(x=0, y=0, anchor="nw")
		
		left_Frame = ctk.CTkFrame(main_Frame, 
		width=250, 
		height=590,
		border_width=2,
		border_color="black"
		)
		left_Frame.place(x=0, y=60, anchor="nw")
		
		left_top_Frame = ctk.CTkFrame(left_Frame, 
		width=250, 
		height=210,
		border_width=2,
		border_color="black"
		)
		left_top_Frame.place(x=0, y=0, anchor="nw")
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(248, 208))
		Label_backg = ctk.CTkLabel(left_top_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		left_mid_Frame = ctk.CTkFrame(left_Frame, 
		width=250, 
		height=200,
		border_width=2,
		border_color="black"
		)
		left_mid_Frame.place(x=0, y=210, anchor="nw")
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(248, 198))
		Label_backg = ctk.CTkLabel(left_mid_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		left_bottom_Frame = ctk.CTkFrame(left_Frame, 
		width=250, 
		height=176,
		border_width=2,
		border_color="black"
		)
		left_bottom_Frame.place(x=0, y=410, anchor="nw")
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(248, 174))
		Label_backg = ctk.CTkLabel(left_bottom_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		left_wallet_Frame = ctk.CTkScrollableFrame(main_Frame, 
		width=275, 
		height=588,
		orientation="vertical",
		border_width=2,
		border_color="black",
		fg_color="gray1"
		)
		left_wallet_Frame._scrollbar.configure(height=0)
		left_wallet_Frame.place(x=250, y=60, anchor="nw")
		
		right_Frame = ctk.CTkFrame(main_Frame, 
		width=646, 
		height=588,
		border_width=2,
		border_color="white"
		)
		right_Frame.place(x=550, y=60, anchor="nw")
		
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(642, 584))
		right_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
		right_backg.place(x=2, y=2)
		
		if view_btcAddr != 'none':
			amount_round = 0.0
			notset_str = 'all'	
			the_status = ' '
			the_dt_string_short = ' '
			the_wif_private_key = ' '
			the_words = ' '
			the_amount = 0.0
			the_category = 'N/A'
			
			try:
				with open(path_to_wallets, 'r') as file:
					csvfile = csv.reader(file)
					for row in csvfile:
						try:
							if row[2] == view_btcAddr:
								the_status = row[0]
								the_dt_string_short = row[1]
								the_wif_private_key = row[3]
								the_words = row[4]
								the_amount = row[5]
								the_category =row[6]
						except:
							continue
			except FileNotFoundError:
					messagebox.showinfo("Information", "No paper wallet file found.")
					
			backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(642, 584))
			right_backg = ctk.CTkLabel(right_Frame, image=backg, text = "")
			right_backg.place(x=2, y=2)

			if the_status == "Timestamp":
				
				
				my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=True, overstrike=False)
				headingLabel = ctk.CTkLabel(right_Frame, text='Timestamp on the Bitcoin blockchain', text_color="white", font=my_font, fg_color="black")
				headingLabel.place(relx=0.05, rely=0.08, anchor="w")
				my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
				
				if the_amount == 'None':
					filenameLabel = ctk.CTkLabel(right_Frame, text='Timestamp is for the hash of document:', text_color="white", font=my_font, fg_color="black")
					filenameLabel.place(relx=0.05, rely=0.14, anchor="w")
					my_font = ctk.CTkFont(family="Arial", size=20, slant="italic", underline=False, overstrike=False)
					filenameLabel2 = ctk.CTkLabel(right_Frame, text=the_words, text_color="white", font=my_font, fg_color="black")
					filenameLabel2.place(relx=0.05, rely=0.2, anchor="w")
				else:
					signameLabel = ctk.CTkLabel(right_Frame, text='For the combined hash of signature and document files:', text_color="white", font=my_font, fg_color="black")
					signameLabel.place(relx=0.05, rely=0.14, anchor="w")
					my_font = ctk.CTkFont(family="Arial", size=20, slant="italic", underline=False, overstrike=False)
					signameLabel2 = ctk.CTkLabel(right_Frame, text=the_amount, text_color="white", font=my_font, fg_color="black")
					signameLabel2.place(relx=0.05, rely=0.2, anchor="w")

					filenameLabel2 = ctk.CTkLabel(right_Frame, text=the_words, text_color="white", font=my_font, fg_color="black")
					filenameLabel2.place(relx=0.05, rely=0.25, anchor="w")
				
				my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
				Label22 = ctk.CTkLabel(right_Frame, text='Status:', text_color="white", font=my_font, fg_color="black")
				Label22.place(relx=0.05, rely=0.48, anchor="w")
				Label23 = ctk.CTkLabel(right_Frame, text=the_category, text_color="white", font=("Helvetica", 20), fg_color="black")
				Label23.place(relx=0.05, rely=0.53, anchor="w")
				
				Label222 = ctk.CTkLabel(right_Frame, text='Address:', text_color="white", font=my_font, fg_color="black")
				Label222.place(relx=0.05, rely=0.69, anchor="w")
				my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
				Label232 = ctk.CTkLabel(right_Frame, text=view_btcAddr, text_color="white", font=my_font, fg_color="black")
				Label232.place(relx=0.05, rely=0.73, anchor="w")
				
				my_font = ctk.CTkFont(family="Arial", size=16, slant="roman", underline=False, overstrike=False)
				
				if the_category == "Not payed":
					# Generate a Bitcoin transaction including amount of 1100 sats to the newly hashed address
					transaction_payload = 'bitcoin:' + str(view_btcAddr) + '?amount=0.00001100'
					
					# Generate QR-codes to pay transaction 
					qr_public_address = qrcode.make(transaction_payload)
					resize_qr_public_address = qr_public_address.resize((160, 160))
					pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
					resize_qr_public_address.save(pathtopublic)
					publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(160, 160))
					Labelpublicimg = ctk.CTkLabel(right_Frame,  text = "", image = publicimg)
					Labelpublicimg.place(relx=0.6, rely=0.49, anchor="center")
					
					pubLabel = ctk.CTkLabel(right_Frame, text="Pay address:", text_color="white", font=my_font, fg_color="black")
					pubLabel.place(relx=0.6, rely=0.32, anchor="center")
					
					# Generate QR-codes for Blockchain search 
					ext_link = "www.mempool.space/address/" + view_btcAddr
					qr_blockchain_address = qrcode.make(ext_link)
					resize_qr_blockchain_address = qr_blockchain_address.resize((160, 160))
					pathtoblockchain = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
					resize_qr_blockchain_address.save(pathtoblockchain)
					blockchainimg = ctk.CTkImage(light_image=Image.open(pathtoblockchain), dark_image=Image.open(pathtoblockchain), size=(160, 160))
					Labelblockchainimg = ctk.CTkLabel(right_Frame,  text = "", image = blockchainimg)
					Labelblockchainimg.place(relx=0.86, rely=0.49, anchor="center")
					
					pubLabel = ctk.CTkLabel(right_Frame, text="Blockchain link:", text_color="white", font=my_font, fg_color="black")
					pubLabel.place(relx=0.86, rely=0.32, anchor="center")
					
					copy_bechaddr_button = ctk.CTkButton(right_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=1, border_color="white", font=my_font, command=partial(self.copy2clip, ext_link))
					copy_bechaddr_button.place(relx=0.86, rely=0.67, anchor="center")
				
					button3 = ctk.CTkButton(right_Frame, text="Set to payed", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Payed2, view_btcAddr))
					button3.place(relx=0.5, rely=0.8, anchor="center")
				else:
					# Generate QR-codes for Blockchain search 
					ext_link = "www.mempool.space/address/" + view_btcAddr
					qr_public_address = qrcode.make(ext_link)
					resize_qr_public_address = qr_public_address.resize((160, 160))
					pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/blockchain.png"
					resize_qr_public_address.save(pathtopublic)
					publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(160, 160))
					Labelpublicimg = ctk.CTkLabel(right_Frame,  text = "", image = publicimg)
					Labelpublicimg.place(relx=0.82, rely=0.49, anchor="center")
					
					blockchainLabel = ctk.CTkLabel(right_Frame, text="Blockchain link:", text_color="white", font=my_font, fg_color="black")
					blockchainLabel.place(relx=0.83, rely=0.32, anchor="center")
					
					copy_blockchain_button = ctk.CTkButton(right_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=1, border_color="white", font=my_font, command=partial(self.copy2clip, ext_link))
					copy_blockchain_button.place(relx=0.82, rely=0.67, anchor="center")
				
				my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
				
				button4 = ctk.CTkButton(right_Frame, text="Delete", text_color="white", fg_color="red", border_width=2, border_color="white", font=my_font, command=partial(self.do_deleteBitcoinwallet, view_btcAddr))
				button4.place(relx=0.5, rely=0.87, anchor="center")
			else:
				# Generate QR-codes for Public address 
				qr_public_address = qrcode.make(view_btcAddr, version=1)
				resize_qr_public_address = qr_public_address.resize((200, 200))
				pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
				resize_qr_public_address.save(pathtopublic)
				publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(200, 200))
				# Generate QR-codes for WIF-address
				qr_wif_private_key = qrcode.make(the_wif_private_key, version=1)
				resize_qr_wif_private_key = qr_wif_private_key.resize((200, 200))
				pathtowif = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/wif.png"
				resize_qr_wif_private_key.save(pathtowif)
				wifimg = ctk.CTkImage(light_image=Image.open(pathtowif), dark_image=Image.open(pathtowif), size=(200, 200))
				
				my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
				
				pubLabel = ctk.CTkLabel(right_Frame, text="Load", text_color="white", font=("Arial", 28), fg_color="black")
				pubLabel.place(relx=0.15, rely=0.18, anchor="center")
				Labelpublicimg = ctk.CTkLabel(right_Frame,  text = "", image = publicimg)
				Labelpublicimg.place(relx=0.17, rely=0.4, anchor="center")
				copy_bechaddr_button = ctk.CTkButton(right_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=2, border_color="white", font=my_font, command=partial(self.copy2clip, view_btcAddr))
				copy_bechaddr_button.place(relx=0.15, rely=0.61, anchor="center")
				
				dotLabel = ctk.CTkLabel(right_Frame, text=".", text_color="black", font=("Helvetica", 15), fg_color="black")
				dotLabel.place(relx=0.1, rely=0.99, anchor="w")
				
				wifLabel = ctk.CTkLabel(right_Frame, text="Spend (Legacy)", text_color="white", font=("Arial", 28), fg_color="black")
				wifLabel.place(relx=0.83, rely=0.18, anchor="center")
				Labelwifimg = ctk.CTkLabel(right_Frame, text = "", image = wifimg)
				Labelwifimg.place(relx=0.83, rely=0.4, anchor="center")
				copy_wifaddr_button = ctk.CTkButton(right_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=2, border_color="white", font=my_font, command=partial(self.copy2clip, the_wif_private_key))
				copy_wifaddr_button.place(relx=0.83, rely=0.61, anchor="center")
				my_font = ctk.CTkFont(family="Helvetica", size=26, weight="bold", slant="roman", underline=True, overstrike=False)
				Label0 = ctk.CTkLabel(right_Frame, text=the_status + ' Bitcoin wallet', text_color="white", font=my_font, fg_color="black")
				Label0.place(relx=0.5, rely=0.05, anchor="center")	
				my_font = ctk.CTkFont(family="Arial", size=16, weight="bold", slant="roman", underline=False, overstrike=False)
				Label1 = ctk.CTkLabel(right_Frame, text=view_btcAddr, text_color="white", font=("Helvetica", 20), fg_color="black")
				Label1.place(relx=0.5, rely=0.12, anchor="center")	
				Label2 = ctk.CTkLabel(right_Frame, text='Created: ' + the_dt_string_short, text_color="white", font=("Helvetica", 18), fg_color="black")
				Label2.place(relx=0.5, rely=0.26, anchor="center")	
				Label22 = ctk.CTkLabel(right_Frame, text='Category:', text_color="white", font=("Helvetica", 18), fg_color="black")
				Label22.place(relx=0.5, rely=0.34, anchor="center")
				Label23 = ctk.CTkLabel(right_Frame, text=the_category, text_color="white", font=("Helvetica", 22), fg_color="black")
				Label23.place(relx=0.5, rely=0.4, anchor="center")
				my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
				if float(the_amount) < 0.01:
					SATs_value = float(the_amount) * 100000000
					BTC_value_rounded = round(SATs_value, 8)
					Label4 = ctk.CTkLabel(right_Frame, text='Amount:', text_color="white", font=my_font, fg_color="black")
					Label4.place(relx=0.5, rely=0.47, anchor="center")
					Label44 = ctk.CTkLabel(right_Frame, text=str(int(BTC_value_rounded)) + ' sats', text_color="white", font=("Helvetica", 22), fg_color="black")
					Label44.place(relx=0.5, rely=0.53, anchor="center")
				else:
					Label4 = ctk.CTkLabel(right_Frame, text='Amount: ' + str(the_amount) + ' BTC', text_color="white", font=my_font, fg_color="black")
					Label4.place(relx=0.5, rely=0.5, anchor="center")
				my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
				if (str(the_status) == "Active") or (str(the_status) == 'Created') or (str(the_status) == 'Non KYC'):
					if (str(the_amount) == '0') or (str(the_amount) == '0.0'):
						button1 = ctk.CTkButton(right_Frame, text="Add BTC", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.add_AmountToBitcoinwallet, view_btcAddr))
						button1.place(relx=0.5, rely=0.57, anchor="center")	
				if str(the_status) == 'Created':
					button2 = ctk.CTkButton(right_Frame, text="Change status to Active", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Active, view_btcAddr))
					button2.place(relx=0.5, rely=0.62, anchor="center")	
				if str(the_status) == 'Active' or str(the_status) == 'Non KYC':
					button3 = ctk.CTkButton(right_Frame, text="Change status to Spent", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Spent, view_btcAddr))
					button3.place(relx=0.5, rely=0.62, anchor="center")	
				button4 = ctk.CTkButton(right_Frame, text="Delete", text_color="white", fg_color="red", border_width=2, border_color="white", font=my_font, command=partial(self.do_deleteBitcoinwallet, view_btcAddr))
				button4.place(relx=0.5, rely=0.7, anchor="center")	
		
		my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
		
		clicked = StringVar()
		clicked2 = StringVar()
		
		amount = 0.0
		loopcount = 0
		SATs_value = 0.0
		
		
		if path_to_USB_secure == 'Secure USB folder is available':
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
		
			filter_all_Button = ctk.CTkButton(top_Frame, text="All wallets", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.create_Bitcointextbox, 'all'))
			filter_all_Button.place(relx=0.1, y=30, anchor="center")
			
			filter_Button = ctk.CTkButton(top_Frame, text="Use wallet filter", fg_color="dark orange", text_color="black", border_width=2, border_color="white", font=my_font, command=self.do_show_Bitcoinwallets_start)
			filter_Button.place(relx=0.25, y=30, anchor="center")
			
			addButton = ctk.CTkButton(top_Frame, text="Add new wallet", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=self.do_new_Bitcoinwallet)
			addButton.place(relx=0.9, y=30, anchor="center")
			wallets = False
			
			try:
				with open(path_to_wallets, 'r') as file:
					csvfile = csv.reader(file)
					if do_sort == 'date':
						csvfile = sorted(csvfile, key=lambda x: x[1], reverse=True)
					if do_sort == 'value':
						csvfile = sorted(csvfile, key=lambda x: x[5], reverse=True)
					for lines in csvfile:
						if lines:
							wallets = True
							my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
							if (lines[0] == 'Timestamp' and use_status == 'Timestamp' and lines[6] == use_filter) or (lines[0] == 'Timestamp' and use_status == 'all' and use_filter == 'all') or (lines[0] == 'Timestamp' and use_status == 'Timestamp' and use_filter == 'all') or (lines[0] == 'Timestamp' and use_status == 'all' and use_filter == lines[6]):
								
								if lines[5] == 'None':
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n' + 'Timestamp\n Document', anchor='center', text_color="white", fg_color="purple", border_width=4, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								else:
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n' + 'Timestamp\nSignature + Document', anchor='center', text_color="white", fg_color="purple", border_width=4, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								Button5.pack(pady = 10)
								
							if (lines[0] == 'Active' and use_status == 'Active' and lines[6] == use_filter) or (lines[0] == 'Active' and use_status == 'all' and use_filter == 'all') or (lines[0] == 'Active' and use_status == 'Active' and use_filter == 'all') or (lines[0] == 'Active' and use_status == 'all' and use_filter == lines[6]):
								if float(lines[5]) < 0.01:
									SATs_value = float(lines[5]) * 100000000
									SATs_value_rounded = round(SATs_value, 7)
									SATs_value_int = int(SATs_value_rounded)
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n\n' + str(SATs_value_int) + ' sats', anchor='nc', text_color="white", fg_color="green4", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								else:
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n\n' + lines[5] + ' BTC', anchor='center', text_color="white", fg_color="green4", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								
								Button5.pack(pady = 10)
								amount = amount + float(lines[5])
								
							if (lines[0] == 'Spent' and use_status == 'Spent' and lines[6] == use_filter) or (lines[0] == 'Spent' and use_status == 'all' and use_filter == 'all') or (lines[0] == 'Spent' and use_status == 'Spent' and use_filter == 'all') or (lines[0] == 'Spent' and use_status == 'all' and use_filter == lines[6]):
								if float(lines[5]) < 0.01:
									SATs_value = float(lines[5]) * 100000000
									SATs_value_rounded = round(SATs_value, 7)
									SATs_value_int = int(SATs_value_rounded)
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n\n' + str(SATs_value_int) + ' sats', anchor='nc', text_color="black", fg_color="grey", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								else:
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n\n' + lines[5] + ' BTC', anchor='center', text_color="black", fg_color="grey", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								
								Button5.pack(pady = 10)
								
							if (lines[0] == 'Non KYC' and use_status == 'Non KYC' and lines[6] == use_filter) or (lines[0] == 'Non KYC' and use_status == 'all' and use_filter == 'all') or (lines[0] == 'Non KYC' and use_status == 'Non KYC' and use_filter == 'all') or (lines[0] == 'Non KYC' and use_status == 'all' and use_filter == lines[6]):
								if float(lines[5]) < 0.01:
									SATs_value = float(lines[5]) * 100000000
									SATs_value_rounded = round(SATs_value, 7)
									SATs_value_int = int(SATs_value_rounded)
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n\n' + str(SATs_value_int) + ' sats', anchor='nc', text_color="white", fg_color="dark green", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								else:
									Button5 = ctk.CTkButton(left_wallet_Frame, text='Created: ' + lines[1] + '\n\n' + lines[5] + ' BTC', anchor='center', text_color="white", fg_color="dark green", border_width=2, border_color="white", font=my_font, width=220, height=100, command=partial(self.change_view_btcAddr, lines[2]))
								
								Button5.pack(pady = 10)
								amount = amount + float(lines[5])
							loopcount = loopcount + 1
							
			except FileNotFoundError:
				messagebox.showinfo("Information", "No paper wallet file found.")
			amount_round = round(amount, 7)	
			
			if wallets:
				# Get the current categories (if any)			
				get_categories()
				clicked.set("Select category")
				clicked2.set("Select status")
				
				statusLabel = ctk.CTkLabel(left_top_Frame, text="Filter on wallet type:", text_color="white", fg_color="black", font=my_font)
				statusLabel.place(x=10, y=28, anchor="w")
				drop2 = OptionMenu(left_top_Frame, clicked2, *status_list)
				drop2.config(width=18)
				drop2.place(x=234, y=62, anchor="e")
				
				categoryLabel = ctk.CTkLabel(left_top_Frame, text="Filter on wallet category:", text_color="white", fg_color="black", font=my_font)
				categoryLabel.place(x=10, y=106, anchor="w")
				drop = OptionMenu(left_top_Frame, clicked, *categories_list)
				drop.config(width=18)
				drop.place(x=234, y=140, anchor="e")
				
				selectCategoryButton = ctk.CTkButton(left_top_Frame, text="Apply", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=130, height=28, font=my_font, command=filter_on_category_and_status)
				selectCategoryButton.place(x=235, y=170, anchor="ne")
				
				sortLabel = ctk.CTkLabel(left_mid_Frame, text="Sort wallets on:", text_color="white", fg_color="black", font=my_font)
				sortLabel.place(x=10, y=20, anchor="w")
				
				sortdateButton = ctk.CTkButton(left_mid_Frame, text="Date", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=130, height=28, font=my_font, command=change_sort_flag_to_date)
				sortdateButton.place(x=235, y=45, anchor="ne")
				sortdateButton = ctk.CTkButton(left_mid_Frame, text="Value", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=130, height=28, font=my_font, command=change_sort_flag_to_value)
				sortdateButton.place(x=235, y=85, anchor="ne")
				my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=True, overstrike=False)
			
				infoLabel = ctk.CTkLabel(left_bottom_Frame, text="Applied filters:", text_color="white", fg_color="black", font=my_font)
				infoLabel.place(x=10, y=20, anchor="w")
				my_font = ctk.CTkFont(family="Arial", size=20, slant="roman", underline=False, overstrike=False)
				infoLabel2 = ctk.CTkLabel(left_bottom_Frame, text="Status: " + use_status, text_color="white", fg_color="black", font=my_font)
				infoLabel2.place(x=22, y=60, anchor="w")
				infoLabel3 = ctk.CTkLabel(left_bottom_Frame, text="Category: " + use_filter, text_color="white", fg_color="black", font=my_font)
				infoLabel3.place(x=22, y=90, anchor="w")
				removefilterButton = ctk.CTkButton(left_bottom_Frame, text="Show all", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", width=130, height=28, font=my_font, command=change_sort_flag_to_none)
				removefilterButton.place(x=235, y=120, anchor="ne")	
		else:
			notOKButton = ctk.CTkButton(top_Frame, text="You are not logged in.", text_color="white", fg_color="brown", border_width=2, border_color="white", width=170, height=32, font=my_font, command=self.decrypt_SecUSB)
			notOKButton.place(relx=0.5, rely=0.5, anchor="center")
	
	def fix_csvfile(self):
		size_header = 0
		fixed = False
		path_to_wallets = filepathdestinationfolder + "/secure/wallets/paperwallets/paperwallets.csv"
		path_to_wallets_backup = filepathdestinationfolder + "/secure/wallets/paperwallets/paperwallets_backup.csv"
		path_to_temp_wallets = filepathdestinationfolder + "/secure/wallets/paperwallets/temp_paperwallets.csv"
		
		shutil.copy(path_to_wallets, path_to_wallets_backup)
		
		with open(path_to_temp_wallets, 'w') as target:
			target_writer = csv.writer(target)
			
			with open(path_to_wallets, 'r') as source:
				source_reader = csv.reader(source)
					
				for row in source_reader:
					size_header = len(row)
					if size_header == 6:
						fixed = True
						fixed_row = row
						fixed_row.append('N/A')
						target_writer.writerow(fixed_row)
					else:
						target_writer.writerow(row)
		if fixed:		
			shutil.copy(path_to_temp_wallets, path_to_wallets)
		return True
		
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
		the_category = 'N/A'
		the_amount = 0.0
		
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=3,
		border_color="black"
		)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		
		try:
			with open(path_to_wallets, 'r') as file:
				csvfile = csv.reader(file)
				for row in csvfile:
					try:
						if row[2] == bechaddr:
							the_status = row[0]
							the_dt_string_short = row[1]
							the_addr = row[2]
							the_wif_private_key = row[3]
							the_words = row[4]
							the_amount = row[5]
							the_category = row[6]
					except:
						continue
		except FileNotFoundError:
				messagebox.showinfo("Information", "No paper wallet file found.")
				
		pathtobackg = str(filepathdestinationfolder) + "/images/BTC_icon_black.jpg"

		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1196, 646))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=2, y=2)
		
		if str(the_status) == 'Timestamp':
				
			my_font = ctk.CTkFont(family="Arial", size=26, slant="roman", underline=True, overstrike=False)
			headingLabel = ctk.CTkLabel(my_Frame, text='Timestamp on the Bitcoin blockchain', text_color="white", font=my_font, fg_color="black")
			headingLabel.place(relx=0.1, rely=0.1, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=False, overstrike=False)
			if the_amount == 'None':
				filenameLabel = ctk.CTkLabel(my_Frame, text='Timestamp is for the hash of document:', text_color="white", font=my_font, fg_color="black")
				filenameLabel.place(relx=0.1, rely=0.25, anchor="w")
				
				my_font = ctk.CTkFont(family="Arial", size=22, slant="italic", underline=False, overstrike=False)
				
				filenameLabel2 = ctk.CTkLabel(my_Frame, text=the_words, text_color="white", font=my_font, fg_color="black")
				filenameLabel2.place(relx=0.1, rely=0.3, anchor="w")
			else:
				signameLabel = ctk.CTkLabel(my_Frame, text='For the combined hash of signature and document files:', text_color="white", font=my_font, fg_color="black")
				signameLabel.place(relx=0.1, rely=0.2, anchor="w")
				
				my_font = ctk.CTkFont(family="Arial", size=22, slant="italic", underline=False, overstrike=False)
				
				signameLabel2 = ctk.CTkLabel(my_Frame, text=the_amount, text_color="white", font=my_font, fg_color="black")
				signameLabel2.place(relx=0.1, rely=0.26, anchor="w")
				
				filenameLabel2 = ctk.CTkLabel(my_Frame, text=the_words, text_color="white", font=my_font, fg_color="black")
				filenameLabel2.place(relx=0.1, rely=0.32, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=22, slant="roman", underline=False, overstrike=False)	
			Label22 = ctk.CTkLabel(my_Frame, text='Status:', text_color="white", font=my_font, fg_color="black")
			Label22.place(relx=0.1, rely=0.46, anchor="w")
			Label23 = ctk.CTkLabel(my_Frame, text=the_category, text_color="white", font=("Helvetica", 22), fg_color="black")
			Label23.place(relx=0.1, rely=0.51, anchor="w")
			
			Label222 = ctk.CTkLabel(my_Frame, text='Address:', text_color="white", font=my_font, fg_color="black")
			Label222.place(relx=0.1, rely=0.65, anchor="w")
			Label232 = ctk.CTkLabel(my_Frame, text=the_addr, text_color="white", font=("Helvetica", 22), fg_color="black")
			Label232.place(relx=0.1, rely=0.7, anchor="w")

			if the_category == "Not payed":
				# Generate a Bitcoin transaction including amount of 1100 sats to the newly hashed address
				transaction_payload = 'bitcoin:' + the_addr + '?amount=0.00001100'
					
				# Generate QR-codes for transaction address 
				qr_public_address = qrcode.make(transaction_payload)
				resize_qr_public_address = qr_public_address.resize((200, 200))
				pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
				resize_qr_public_address.save(pathtopublic)
				publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(200, 200))
				Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = publicimg)
				Labelpublicimg.place(relx=0.7, rely=0.4, anchor="center")
				
				pubLabel = ctk.CTkLabel(my_Frame, text="Pay address:", text_color="white", font=("Arial", 28), fg_color="black")
				pubLabel.place(relx=0.7, rely=0.18, anchor="center")
				
				# Generate QR-codes for Blockchain search 
				ext_link = "www.mempool.space/address/" + the_addr
				qr_blockchain_address = qrcode.make(ext_link)
				resize_qr_blockchain_address = qr_blockchain_address.resize((200, 200))
				pathtoblockchain = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/blockchain.png"
				resize_qr_blockchain_address.save(pathtoblockchain)
				blockchainimg = ctk.CTkImage(light_image=Image.open(pathtoblockchain), dark_image=Image.open(pathtoblockchain), size=(200, 200))
				Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = blockchainimg)
				Labelpublicimg.place(relx=0.9, rely=0.4, anchor="center")
				
				blockchainLabel = ctk.CTkLabel(my_Frame, text="Blockchain link:", text_color="white", font=("Arial", 28), fg_color="black")
				blockchainLabel.place(relx=0.9, rely=0.18, anchor="center")
				
				copy_blockchain_button = ctk.CTkButton(my_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=1, border_color="white", font=my_font, command=partial(self.copy2clip, ext_link))
				copy_blockchain_button.place(relx=0.9, rely=0.61, anchor="center")
				
				button3 = ctk.CTkButton(my_Frame, text="Set to payed", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Payed, the_addr))
				button3.place(relx=0.5, rely=0.76, anchor="center")
			else:
				# Generate QR-codes for Blockchain search 
				ext_link = "www.mempool.space/address/" + the_addr
				qr_blockchain_address = qrcode.make(ext_link)
				resize_qr_blockchain_address = qr_blockchain_address.resize((200, 200))
				pathtoblockchain = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/blockchain.png"
				resize_qr_blockchain_address.save(pathtoblockchain)
				blockchainimg = ctk.CTkImage(light_image=Image.open(pathtoblockchain), dark_image=Image.open(pathtoblockchain), size=(200, 200))
				Labelblockchainimg = ctk.CTkLabel(my_Frame,  text = "", image = blockchainimg)
				Labelblockchainimg.place(relx=0.8, rely=0.4, anchor="center")
				
				blockchainLabel = ctk.CTkLabel(my_Frame, text="Blockchain link:", text_color="white", font=("Arial", 28), fg_color="black")
				blockchainLabel.place(relx=0.8, rely=0.18, anchor="center")
				
				copy_blockchain_button = ctk.CTkButton(my_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=1, border_color="white", font=my_font, command=partial(self.copy2clip, ext_link))
				copy_blockchain_button.place(relx=0.8, rely=0.61, anchor="center")
			
			button4 = ctk.CTkButton(my_Frame, text="Delete", text_color="white", fg_color="red", border_width=2, border_color="white", font=my_font, command=partial(self.do_deleteBitcoinwallet, the_addr))
			button4.place(relx=0.5, rely=0.84, anchor="center")
			button5 = ctk.CTkButton(my_Frame, text="Back", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.create_Bitcointextbox, notset_str))
			button5.place(relx=0.5, rely=0.92, anchor="center")
		else:
			# Generate QR-codes for Public address and WIF-address and read them to display on screen
			qr_public_address = qrcode.make(the_addr, version=1)
			qr_wif_private_key = qrcode.make(the_wif_private_key, version=1)
			
			resize_qr_public_address = qr_public_address.resize((200, 200))
			resize_qr_wif_private_key = qr_wif_private_key.resize((200, 200))
			pathtopublic = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/public.png"
			pathtowif = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/wif.png"
			
			resize_qr_public_address.save(pathtopublic)
			resize_qr_wif_private_key.save(pathtowif)

			publicimg = ctk.CTkImage(light_image=Image.open(pathtopublic), dark_image=Image.open(pathtopublic), size=(200, 200))

			wifimg = ctk.CTkImage(light_image=Image.open(pathtowif), dark_image=Image.open(pathtowif), size=(200, 200))
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			
			pubLabel = ctk.CTkLabel(my_Frame, text="Load", text_color="white", font=("Arial", 28), fg_color="black")
			pubLabel.place(relx=0.15, rely=0.18, anchor="center")
			Labelpublicimg = ctk.CTkLabel(my_Frame,  text = "", image = publicimg)
			Labelpublicimg.place(relx=0.15, rely=0.4, anchor="center")
			copy_bechaddr_button = ctk.CTkButton(my_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=2, border_color="white", font=my_font, command=partial(self.copy2clip, the_addr))
			copy_bechaddr_button.place(relx=0.15, rely=0.61, anchor="center")
			
			dotLabel = ctk.CTkLabel(my_Frame, text=".", text_color="black", font=("Helvetica", 15), fg_color="black")
			dotLabel.place(relx=0.1, rely=0.99, anchor="w")
			
			wifLabel = ctk.CTkLabel(my_Frame, text="Spend (Legacy)", text_color="white", font=("Arial", 28), fg_color="black")
			wifLabel.place(relx=0.83, rely=0.18, anchor="center")
			Labelwifimg = ctk.CTkLabel(my_Frame, text = "", image = wifimg)
			Labelwifimg.place(relx=0.83, rely=0.4, anchor="center")
			copy_wifaddr_button = ctk.CTkButton(my_Frame, text="Copy to clipboard", text_color="white", fg_color=SecUSB_button_color, height=25, width=150, border_width=2, border_color="white", font=my_font, command=partial(self.copy2clip, the_wif_private_key))
			copy_wifaddr_button.place(relx=0.83, rely=0.61, anchor="center")
			if the_status == 'Created':
				my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
				Label0 = ctk.CTkLabel(my_Frame, text='Unused Bitcoin paper wallet:', text_color="white", font=("Helvetica", 20), fg_color="black")
				Label0.place(relx=0.5, rely=0.1, anchor="center")	
			else:	
				my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=True, overstrike=False)
				Label0 = ctk.CTkLabel(my_Frame, text=the_status + ' Bitcoin paper wallet:', text_color="white", font=("Helvetica", 20), fg_color="black")
				Label0.place(relx=0.5, rely=0.1, anchor="center")	
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			Label1 = ctk.CTkLabel(my_Frame, text=the_addr, text_color="white", font=("Helvetica", 20), fg_color="black")
			Label1.place(relx=0.5, rely=0.2, anchor="center")	
			Label2 = ctk.CTkLabel(my_Frame, text='Created: ' + the_dt_string_short, text_color="white", font=("Helvetica", 18), fg_color="black")
			Label2.place(relx=0.5, rely=0.27, anchor="center")	
			Label22 = ctk.CTkLabel(my_Frame, text='Category: ' + the_category, text_color="white", font=("Helvetica", 20), fg_color="black")
			Label22.place(relx=0.5, rely=0.33, anchor="center")
			Label3 = ctk.CTkLabel(my_Frame, text='WIF: ' + the_wif_private_key, text_color="white", font=("Helvetica", 15), fg_color="black")
			Label3.place(relx=0.5, rely=0.4, anchor="center")	
			if float(the_amount) < 0.01:
				SATs_value = float(the_amount) * 100000000
				BTC_value_rounded = round(SATs_value, 7)
				Label4 = ctk.CTkLabel(my_Frame, text='Amount: ' + str(int(BTC_value_rounded)) + ' sats', text_color="white", font=my_font, fg_color="black")
				Label4.place(relx=0.5, rely=0.5, anchor="center")
			else:
				Label4 = ctk.CTkLabel(my_Frame, text='Amount: ' + str(the_amount) + ' BTC', text_color="white", font=my_font, fg_color="black")
				Label4.place(relx=0.5, rely=0.5, anchor="center")
			my_font = ctk.CTkFont(family="Arial", size=18, slant="roman", underline=False, overstrike=False)
			if (str(the_status) == "Active") or (str(the_status) == 'Created') or (str(the_status) == 'Non KYC'):
				if (str(the_amount) == '0') or (str(the_amount) == '0.0'):
					button1 = ctk.CTkButton(my_Frame, text="Add BTC", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.add_AmountToBitcoinwallet, the_addr))
					button1.place(relx=0.5, rely=0.57, anchor="center")	
			if str(the_status) == 'Created':
				button2 = ctk.CTkButton(my_Frame, text="Change status to Active", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Active, the_addr))
				button2.place(relx=0.5, rely=0.62, anchor="center")	
			if str(the_status) == 'Active' or str(the_status) == 'Non KYC':
				button3 = ctk.CTkButton(my_Frame, text="Change status to Spent", text_color="white", fg_color=SecUSB_button_color, border_width=2, border_color="white", font=my_font, command=partial(self.changeStatusForBitcoinwallet_to_Spent, the_addr))
				button3.place(relx=0.5, rely=0.62, anchor="center")	
			button4 = ctk.CTkButton(my_Frame, text="Delete", text_color="white", fg_color="red", border_width=2, border_color="white", font=my_font, command=partial(self.do_deleteBitcoinwallet, the_addr))
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
										row[5],
										row[6]]
										
						USER_INP = simpledialog.askfloat(title="Add amount!", prompt="Input the amount intended for the paper wallet (in sats or BTC)", initialvalue=0.0)
						
						if float(USER_INP) > 100:
							SATs_value = float(USER_INP) / 100000000
							SATs_value_rounded = round(SATs_value, 7)
							SATs_value_int = int(SATs_value_rounded)
							new_paperwallet[5] = SATs_value
						else:
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
	
	def changeStatusForBitcoinwallet_to_Payed(self, bechaddr):
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
										row[5],
										row[6]]
						new_paperwallet[6] = 'Payed'
						csvwriter.writerow(new_paperwallet)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_wallets, path_to_wallets)
		os.remove(updated_path_to_wallets)	
		self.create_Bitcointextbox(notset_str)
		
	def changeStatusForBitcoinwallet_to_Payed2(self, bechaddr):
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
										row[5],
										row[6]]
						new_paperwallet[6] = 'Payed'
						csvwriter.writerow(new_paperwallet)
					else:
						csvwriter.writerow(row)						
				except:
					continue
		shutil.copy(updated_path_to_wallets, path_to_wallets)
		os.remove(updated_path_to_wallets)	
		self.do_show_Bitcoinwallets_start()
			
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
										row[5],
										row[6]]
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
										row[5],
										row[6]]
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
		global PersonalGPGKey
		global filepathdestinationfolder
		global path_to_USB_secure
		global timeSecUSBLastModified
		global System_button_color
		global categories_list
		
		new_paperwallet_amount= 0.0
		notset_str ='all'
		categories_list = []
		path_to_wallets = str(filepathdestinationfolder) + "/secure/wallets/paperwallets/paperwallets.csv"
		
		now = datetime.now()
		dt_string = now.strftime("%Y-%m-%d %H:%M:%S")
		dt_string_short = now.strftime("%Y-%m-%d")
				
		def do_new_wallet():
			KYC_or_not = checkbox.get()
			new_category_v = str(clicked.get())
			entered_value = newCategoryEntry.get()
			
			# If new category
			if new_category_v == "New category":
				new_category_v = entered_value
					
			if KYC_or_not == 'yes':
				new_Bitcoin_wallet_status = 'Non KYC'
			else:
				new_Bitcoin_wallet_status = 'Active'
				
			seed_words = bitcoinlibMnemonic().generate()
			
			w = wallet.create_wallet(network="BTC", seed=seed_words, children=1)

			new_paperwallet = [
								new_Bitcoin_wallet_status,
								dt_string_short,
								w.get("address"),
								w.get("wif"),		#.decode("utf-8")
								w.get("seed"),
								new_paperwallet_amount,
								new_category_v]

			with open(path_to_wallets, 'a') as f:
				writer = csv.writer(f)
				writer.writerow(new_paperwallet)
			self.do_edit_Bitcoinwallets(w.get("address"))
		
		def get_categories():
			global categories_list
			categories_list.append('New category')
			with open(path_to_wallets, 'r') as file:
				csvfile = csv.reader(file)
				for row in csvfile:
					if row[6] not in categories_list and row[6] != "Not payed" and row[6] != "Payed":
						categories_list.append(row[6])
				
		my_Frame = ctk.CTkFrame(self, 
		width=1200, 
		height=650,
		border_width=3,
		border_color="white"
		)
		
		pathtobackg = self.get_background_image()
				
		backg = ctk.CTkImage(light_image=Image.open(pathtobackg), dark_image=Image.open(pathtobackg), size=(1200, 650))
		Label_backg = ctk.CTkLabel(my_Frame, image=backg, text = "")
		Label_backg.place(x=0, y=0)
		my_Frame.place(relx=0.5, rely=0.6, anchor="center")
		my_Frame.focus_set()
		my_Frame.focus_force()
		
		if path_to_USB_secure == 'Secure USB folder is available':
			completeName = str(filepathdestinationfolder) + "/secure/settings.csv"
			
			USER_INP = simpledialog.askfloat(title="Add amount!", prompt="Input the amount intended for the paper wallet (in sats or BTC)", initialvalue=0.0)
		
			if float(USER_INP) > 100:
				USER_INP = int(USER_INP)
				SATs_value = float(USER_INP) / 100000000
				new_paperwallet_amount = round(SATs_value, 8)
			else:
				new_paperwallet_amount = USER_INP
			
			clicked = StringVar()
			clicked.set("Others") 
			check_var = ctk.StringVar(value="on")
			
			my_font = ctk.CTkFont(family="Arial", size=24, weight="bold", slant="roman", underline=True, overstrike=False)
			
			Label1 = ctk.CTkLabel(my_Frame, text="Create a new Bitcoin wallet:", text_color="white", fg_color="black", font=my_font)
			Label1.place(relx=0.3, rely=0.1, anchor="e")
			
			my_font = ctk.CTkFont(family="Arial", size=20, weight="bold", slant="roman", underline=False, overstrike=False)
			
			nameLabel = ctk.CTkLabel(my_Frame, text="Created:", text_color="white", fg_color="black", font=my_font)
			nameLabel.place(relx=0.18, rely=0.18, anchor="e")
			
			Label2 = ctk.CTkLabel(my_Frame, text=str(dt_string_short), font=my_font, text_color="white", fg_color="black")
			Label2.place(relx=0.28, rely=0.18, anchor="w")
			
			nameLabel = ctk.CTkLabel(my_Frame, text="Amount:", text_color="white", fg_color="black", font=my_font)
			nameLabel.place(relx=0.18, rely=0.24, anchor="e")
			
			if float(USER_INP) > 100:
				Label3 = ctk.CTkLabel(my_Frame, text=str(int(USER_INP)) + ' sats', font=my_font, text_color="white", fg_color="black")
				Label3.place(relx=0.28, rely=0.24, anchor="w")
			else:
				Label3 = ctk.CTkLabel(my_Frame, text=str(new_paperwallet_amount) + ' BTC' , font=my_font, text_color="white", fg_color="black")
				Label3.place(relx=0.28, rely=0.24, anchor="w")
			
			checkbox = ctk.CTkCheckBox(my_Frame, text="The Bitcoins are KYC free!", font=my_font, variable=check_var, onvalue="yes", offvalue="no", text_color="white", fg_color="black")
			checkbox.place(relx=0.46, rely=0.32, anchor="e")

			# Get the current cataegories (if any)			
			get_categories()
			categoryLabel = ctk.CTkLabel(my_Frame, text="Select a category:", text_color="white", fg_color="black", font=my_font)
			categoryLabel.place(relx=0.25, rely=0.5, anchor="e")
		
			drop = OptionMenu(my_Frame, clicked, *categories_list)
			drop.place(relx=0.34, rely=0.5, anchor="w")
			
			categoryLabel = ctk.CTkLabel(my_Frame, text="Create a new category:", text_color="white", fg_color="black", font=my_font)
			categoryLabel.place(relx=0.3, rely=0.6, anchor="e")
			
			def limitSizeCategoryname(*args):
				value = new_category_var.get()
				if len(value) > 17: new_category_var.set(value[:17])
			
			new_category_var = ctk.StringVar(value = "New category")
			new_category_var.trace('w', limitSizeCategoryname)
				
			newCategoryEntry = ctk.CTkEntry(my_Frame, placeholder_text="New category", textvariable=new_category_var, width=150, height=25, text_color="white", border_color="white", border_width=3, corner_radius=8, font=my_font)
			newCategoryEntry.place(relx=0.34, rely=0.6, anchor="w")
			
			my_font = ctk.CTkFont(family="Arial", size=22, weight="bold", slant="roman", underline=False, overstrike=False)
			
			updateButton = ctk.CTkButton(my_Frame, text="Create wallet!", text_color="white", fg_color=System_button_color, border_width=3, border_color="white", font=my_font, command=do_new_wallet)
			updateButton.place(relx=0.34, rely=0.74, anchor="w")
App()
