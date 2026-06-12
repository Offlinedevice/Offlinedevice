## Hardware key for Offline device:
Key contains:
 - NTAG210q or similar NFC-chip (max dimentions 12 x 19 mm)
 - LED-chip with antenna for luminate when in proximity to RF-field.

## Using the HW-key to unlock account
Select add HW-key during account creation (or later on). Create the new account with a truly random base58 password (select "use strong password" and follwo the instructions). 
Then create a truly random salt (secret) also select a easy to remember PIN. Hold the key over the device to write the salt/secret to NTAG-memory. 
Now when the account is encrypted (during shudown/logout) both the HW-keys and the "strong password" will be use to encrypt your secret data. 
So during next login you can use the password (more difficult) or you can use one of your HW-keys by holding it close to the reader and type in your PIN (if any).  

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/92371ded54371d12cc685f8800c4793bc1a88a83/Pictures/HW_key.JPG"></p>
