#!/usr/bin/env python3
#
#  Update script for GUIApp.py v0.4.1
#  
#  This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, 
#  version 2 of the License.

#  This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 
#  See the GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>.

#  SPDX-License-Identifier: GPL-2.0-only
#  GUIApp.py - Offline device.
#  Copyright (c) 2024 

import tkinter
import shutil
from tkinter import messagebox

answer = messagebox.askquestion('Important!', 'Before installing version 0.4.1 you first have to install version 0.4.0.\n Have you done that?')

if answer == 'yes':
	shutil.copyfile('/home/user1/tempsystem/Updatefiles/GUIApp.py', '/home/user1/GUIApp.py')
	shutil.copyfile('/home/user1/tempsystem/Updatefiles/Dices_gold_icon.jpg', '/home/user1/images/Dices_gold_icon.jpg')

else:
	messagebox.showinfo("Information", "OK. Cancelling software update process.")

