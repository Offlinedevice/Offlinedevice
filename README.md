
# Offline device
<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/bac3ae3b1d51cccb709c672649967c02344d325c/OfflineDevice3D.gif"></p>

Offline device is a hardware device that runs on a Raspberry OS (Linux based) operating system. It can be built with standard components found in the Internet and all the plastic parts can be printed on a 3D-printer.

The Graphical User Interface is written in Python 3 (GUIApp.py).

Follow on Nostr: [npub1srsejseljs22kg580hvcqs3uj3l0fwh8tamhaumdu2gfn3sxs3lskp3chs](https://primal.net/p/npub1srsejseljs22kg580hvcqs3uj3l0fwh8tamhaumdu2gfn3sxs3lskp3chs)

## Features

- [x] Create strong encryption keys offline (GnuPG)
- [x] Manage your keys and do backups/export or add subkeys etc
- [x] Sign and validate keys and documents in a secure way
- [x] Fully open source (APGLv2)
- [x] Manage your Yubikey 5C, including loading subkeys
- [x] Secure archive of files that can be encrypted and backed-up (RSA encryption acc. to RFC 4880)
- [x] Encrypt and sign files or messages 
- [x] Decrypt files or messages and check its signature (GnuPG)
- [x] Backup and restore function including complete system cloning
- [x] Generate Bitcoin keys offline and store/access through graphical interface
- [x] Add Bitcoin wallets created from Jade hardware wallet or others with Air-gapped transaction signing etc (Native Segwit supported, BIP84)
- [x] Create new Bitcoin wallets using the Offline device and with Air-gapped function 
- [x] Sign Bitcoin transactions offline and Air-gapped (PSBT, according to BIP174)
- [x] Create and manage wallet transactions statements (NEW from version 0.3.8)
- [x] Sign Bitcoin wallet messages to prove ovnership of wallet (NEW from version 0.3.8)
- [x] Encrypted password storage
- [x] Encrypted bitcoin wallet storage (seed's words, LNURLs etc) 
- [x] Generate and manage your own digital ID's (Web of Trust, OpenPGP)
- [x] Generate your own Nostr Keys
- [x] Transfer a Nostr private Key to a Nostr Signing Device
- [x] Export IDs as image or as file (for upload to the "web-of-trust")
- [x] Validate others digital ID's (standard (RFC 4880)
- [x] Store Bolt cards data for accessing load links (lighning Bitcoin), programming and resetting cards
- [x] Read and program Bolt cards with a connected Smart card reader
- [x] Customize your user settings with theme and colors
- [x] Include support for Real Time Clock (battery powered hardware clock) 

## Using the Offine device

Connect the Offline device with cables to a monitor, a keyboard and a mouse. It supports multiple account on the same device. Import or generate GPG keys without being connected to the Internet. During setup a backup USB- device is created. The Offline device facilitates complete privacy and unbreakable encryption for sensitive data and also provides a mechanism for securely send and receive data over the Internet. Others features include Bitcoin wallet generation/storage and transaction signing.

### Guides

* [Getting started guide](https://github.com/Offlinedevice/Offlinedevice/blob/057806e96a671aa06b3eac34bdbc17a77e54d67b/help/getstartedHelp.txt)
* [GPG guide](https://github.com/Offlinedevice/Offlinedevice/blob/e34fb841eac5e7634a74db3f75f62b0f8ab91fca/help/gpgHelp.txt)
* [Yubikey guide](https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/help/yubikeyHelp.txt)
* [Secure archive guide](https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/help/securearchiveHelp.txt)
* [Digital ID guide](https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/help/digitalIDHelp.txt)
* [Bolt card guide](https://github.com/Offlinedevice/Offlinedevice/blob/e34fb841eac5e7634a74db3f75f62b0f8ab91fca/help/boltcardHelp.txt)

## Start here
### Build hardware
Build the Offline device using common parts. See [Getting started guide](https://github.com/Offlinedevice/Offlinedevice/blob/057806e96a671aa06b3eac34bdbc17a77e54d67b/help/getstartedHelp.txt)

### 3D- print parts 
Print the plastic parts you need.
* [Base part](https://github.com/Offlinedevice/Offlinedevice/blob/c830ffdbb2a946e84a4a98436ece2bb4b4ff8ee4/3D/PIzerobox/PIzeroBoxRoundedwithCamera.stl)
* [Lid for build with camera model 1/2](https://github.com/Offlinedevice/Offlinedevice/blob/c830ffdbb2a946e84a4a98436ece2bb4b4ff8ee4/3D/PIzerobox/LidPIzeroBoxwithCameraModel_1_and_2.stl)
* [Alt. lid for camera model 3 (12 MP and auto focus lens)](https://github.com/Offlinedevice/Offlinedevice/blob/c830ffdbb2a946e84a4a98436ece2bb4b4ff8ee4/3D/PIzerobox/LidPIzeroBoxwithCameraModel3.stl)
* [LED guide](https://github.com/Offlinedevice/Offlinedevice/blob/c830ffdbb2a946e84a4a98436ece2bb4b4ff8ee4/3D/PIzerobox/LEDguide.stl)

See also folder "3D" for other featured parts.

### Download and burn image
Download [the latest image](https://www.mediafire.com/file/oeg9oge68onxg3i/OfflineDevice_0_3_9_Pi2W.img.gz/file) and burn it to a microSD-card (min 32 gb) with balenaEtcher (recommended) or Raspberry Pi Imager. Please note that it might be necessary to restart the device after initial power on for it to start.

To check the signature of the latest image use [the signature file](https://www.mediafire.com/file/guwynmvpg3qd70k/OfflineDevice_0_3_9_Pi2W.img.gz.sig/file). First make sure you have the correct public key (see below) imported to your local keychain. Then place the two downloaded files (the signature and the image) in the same directory and run command: gpg --verify signature_files_name.sig image_files_name.img.gz (insert the real name for the files..).

To run the Offline device with GUIApp version 0.3.9, and later, it's necessary to first burn the relevant/latest Image to the microSD-card (see above):

<p align="center"><img src="https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/balenaEtcher_screenshot.PNG"></p>

<p align="center"><img src="https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/Raspberry_Pi_imager.PNG"></p>

<p align="center"><img src="https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/Raspberry_Pi_imager_Use_custom.PNG"></p>

### Install the software yourself
You can choose to install the operating system, programs and libraries yourself. See details in the "Getting started"- document. 

## Many accounts
Multiple people can share the same device. 

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/24983000ea314ff8c1ae10c5c0f86ceefee5acb8/Multiple_accounts.JPG"></p>

## Personalized settings
Change look and feel of your account. 

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/7a977ce4c080ca685e4d9f3b3a0b47ce3544cad8/Settings_screenshot.png"></p>

## Manage encryption keys
Manage the encryption keys on the local keychain. 

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/24983000ea314ff8c1ae10c5c0f86ceefee5acb8/Encr_keys.JPG"></p>

## Add and create Bitcoin wallets
A wallet can be generated by a trusted hardware wallet such as Blockstream Jade and then inported to get air-gapped functionality while the keys are encrypted on the Offline device. 

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/67f4b982cd9f29e2814f1f9446354b705cd52dd5/example_wallet_with_statement.jpg"></p>

## Statement for each Bitcoin wallet
A statement for each Bitcoin wallet. Transactions signed by the Offline Device are added automatically. Good for reporting and managing KYC questions. You can interact with each client/employer/exchange etc with an unique wallet (and statement).  

<p align="center"><img src="https://github.com/Offlinedevice/Offlinedevice/blob/67f4b982cd9f29e2814f1f9446354b705cd52dd5/Example_wallet_statement.jpg"></p>

## Digital IDs
Controlling your own digital ID is as important as controlling your own digital money. The Offline device gives an easy way to create IDs and encrypted files that can be uploaded to public keyservers around the word. Including picture ID/key. 

One for personal use:
<p align="center"><img src="https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/ID_personal_demo.png"></p>

And maybe one for epic gamer ID:
<p align="center"><img src="https://github.com/Offlinedevice/project/blob/291037e6e33de97521e22a7abb742123ab7c2843/ID_gamer_demo.png"></p>

### Update GUI
Make sure you are running the latest graphical interface, GUIApp.py. Download the latest tar- file from the download section and select "settings -> Update software" on the Offline device. 

## Locales

Using a Raspberry Pi keyboard and mouse supports in getting the Locales (correct layout of keys etc.). Always set the correct time and date before staring to use the device. This is important for encryption key generation and date/time stamps. 

## Release + Commit Verification

All releases and commits as of June 28, 2024 are signed by key `BEF873B4691EB2C24E399445FE86F26704C3F74A` (offlinedevice@cyb.org).

### Past Keys
None.

## Donations
If you'd like to help us with the cost of running the Offline device project you can send a payment to us via our BTC address bc1qyufesfamy2qvuc0twce3xsqh8nwrs48placp6f.

Thank you.

## License

Distributed under the GNU Affero General Public License (AGPL v2). See [LICENSE file](LICENSE).
