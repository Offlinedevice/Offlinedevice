## Hardware key for Offline device:
Key contains:
 - NTAG210q or similar NFC Forum Type 2 tag (min 48 bytes of memory and max dimensions 12 x 19 mm)
 - LED-chip with antenna for luminate when in proximity to RF-field.

## Using the HW-key to unlock account
Select add HW-key during account creation (or later on). Create the new account with a truly random base58 password (select "use strong password" and follwo the instructions). 
Then create a truly random salt (secret) also select a easy to remember PIN. Hold the key over the device to write the salt/secret to NTAG-memory. 
Now when the account is encrypted (during shudown/logout) both the HW-keys and the "strong password" will be use to encrypt your secret data. 
So during next login you can use the either the long base58 password the you you created with your own randomness (more difficult) or you can use one of your HW-keys by holding it close to the reader and type in your PIN (if any). 
The passphrase used to decrypt the account is then hashed (calculated) from the salt+keys serial number+PIN using a proof-of-work algorithm.

If using LED-chip inside key use transparent PETG-filament or similar for a nice effect.
<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/92371ded54371d12cc685f8800c4793bc1a88a83/Pictures/HW_key.JPG"></p>
<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/10cf23369970bdf614e7941f38bd6ce6d2ff6fbd/3D/HW_key/NFC_ring.JPG"></p>
