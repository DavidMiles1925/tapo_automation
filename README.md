# Tapo Automation - Light Switch Program (lightswitch.py)

This project was put together in an effort to give my family control over our tapo plugs without having to use the app on the phone. I wanted my kids to be able to turn lights on and off by themselves, especially my disabled son, but I did not want to readily give them access to all of the things on our Tapo account (i.e. cameras, locks, etc.). I also did not like that the Tapo app is only available on mobile platforms, and not on the desktop.

This program gives control tapo plugs and lights from any device. It also gives the flexibility to set up each device to contain its own deicated list of plugs, with custom names. The program contains a simple list of devices that are displayed with a description, along with the device IP address. Devices can easily be added or removed with the click of a button.

## Features

- ✅ Simple, touch-friendly GUI
  - Large, high-contrast labels and oversized ON/OFF buttons for easy use on touch screens or by kids.
  - Compact edit (Edit) and remove (X) controls for each plug.

- ✅ Per-plug controls
  - Turn individual Tapo plugs ON or OFF.
  - Edit plug name and IP, or remove a plug from the list.

- ✅ Batch operations
  - ALL ON / ALL OFF buttons to toggle every saved plug in sequence.
  - Small delay between devices to avoid hammering the network or devices.

- ✅ Non-blocking, responsive UI
  - All network I/O runs in an asyncio loop on a background thread so the Tkinter UI stays responsive during operations and batch runs.

- ✅ Easy credential handling
  - Accepts credentials from config.py, environment variables (TAPO_USERNAME / TAPO_PASSWORD), or an on-start prompt.
  - Credentials are used in-memory; they are not written to the local plug list file.

- ✅ Persistent plug list
  - Saves and loads plugs from a JSON file in the user home directory (~/.tapo_plugs.json).
  - Manual "Save List" button and an Import plugs feature that accepts a JSON file containing [{"name": "...", "ip": "..."}, ...].

- ✅ Error handling and user feedback
  - Friendly message boxes for missing dependencies, import errors, and Tapo device errors.
  - Continues batch operations if one device fails, and reports individual failures.

- ✅ Cross-platform GUI
  - Built with Tkinter — runs on Windows, macOS, and Linux (note: some Linux distros require the system package python3-tk).

- ✅ Minimal external dependencies
  - Requires the tapo client library and aiohttp for network communication; Tkinter is provided by the Python standard library (system package may be needed on some OSes).

---

## Prerequisites

### Install Python (Full)

You must have Python fully installed

- For Windows, Mac, or desktop Linux use the python installer from their website.
- For Raspberry Pi:

```bash
sudo apt install python3-full -y
```

### Install Required Libraries:

For Raspberry Pi, replace `pip` with `sudo apt`.

```bash
pip install tapo
```

```bash
pip install aiohttp
```

### Install tkinter

> Notes on tkinter installation:
>
> - tkinter is part of the Python standard library (tkinter module) and is not installed via pip. On many Linux distributions you need to install the system package (e.g. apt install python3-tk) for the GUI to work.

```bash
apt install python3-tk
```

> - If pip can't find the tapo package on PyPI (package names sometimes differ), check the library you used and substitute the correct PyPI package name (or install direct from the project’s Git repo).

### Configure Static IP addresses for Tapo Devices.

1. Log into your router's administrative tool through your web browser (usually something like 192.169.0.1)
2. Find DHCP settings (usually under Advanced settings)
3. Reserve your device's IP address

⚠️ **If you assign a new IP address to the device via your router, _POWER THE TAPO DEVICE DOWN FIRST_. Failure to do this may result in having to re-pair the device with your account.**

> Notes:
>
> - You can find your device's assigned IP address in your Tapo app under Device Info.
> - If you assign a new IP address to the device, POWER THE TAPO DEVICE DOWN FIRST. Failure to do this may result in having to re-pair the device with your account.
> - Some routers (e.g. Google Routers) do not have adequete DHCP handling, and will not be able to set static IP addresses.

---

## Program Installation

⚠️ **Please ensure you have completed all [Prerequisites](#prerequisites) prior to program installation!**

### Get the Files

From the command line or terminal, clone the repository:

```bash
git clone https://github.com/DavidMiles1925/tapo_automation
```

### Setting Credentials

You will need to provide the program with your Tapo username and password. There are three ways you can set your credentials:

#### Option 1 - Use `config.py` File (recommended for debugging or personal machines only):

**Within the same directory** as `lightswitch.py`, create a file called `config.py`. Copy and paste the following contents into the file. Replace _your_tapo_account_email_ and _your_tapo_account_password_ with your true values.

```python
TAPO_USERNAME = "your_tapo_account_email"
TAPO_PASSWORD = "your_tapo_account_password"
```

⚠️ **_Be sure that `config.py` is in your `.gitignore` file to prevent it from being committed to source control._**

#### Option 2 - Use Environment Variables (more secure, recommended for shared machines and long term use)

For managing configuration and sensitive information (like API keys and passwords) that should not be hardcoded or committed to version control, using a .env file with the python-dotenv library is a best practice.

Install the library:

```bash
pip install python-dotenv
```

Create a .env file in your project's root directory:

```yaml
# .env file
TAPO_USERNAME=your_tapo_account_email
TAPO_PASSWORD=your_tapo_account_password
```

**_Add the .env file to your .gitignore to prevent it from being committed to source control._**

Load and access the variables in your Python code:

```python
from dotenv import load_dotenv
import os
# Load variables from .env file
load_dotenv()
# Access the variables
username = os.getenv("TAPO_USERNAME")
password = os.getenv("TAPO_PASSWORD")
```

#### Option 3 - Manually Enter Credentials

If the app is not able to import credentials from `config.py` and there are no environment variables set, the program will ask you to manually enter your credentials.

---

## Using the Program

### "Add a Plug" Button

- Click the "Add Plug" button to add a device to the list. Enter a description (can be anything) and the device's IP address.
- Plugs can be named anything, it _does NOT need to match_ the name in the tapo app.
- Duplicate entries are allowed, but not recommended for obvious reasons.

> Note: The list of devices stored in the user's home directory within a file called `.tapo_plugs.json`.

### "ON" and "OFF" Buttons

- Clicking either button sends a command to the plug and awaits a response. If there is an authentication error, the user will recieve a pop-up warning.
- The button that was clicked/pressed last will be highlighted. This is not a reliable indicator of the device's status, and is only influenced by the last press.

### "ALL ON" and "ALL OFF" Buttons

- This will set the status of all devices to ON or OFF. If there is an error for a single plug, the user will recieve a pop-up warning, but it will not stop the batch process.
- The highlighted status of the button will change as each plug responds.

### "Edit" Button

- This feature allows a device's properties to be edited.
- Plugs can be named anything, it does not need to match the name in the tapo app.

### "X" (Remove) Button

- This will remove a device from the list.
- You will receive a confirmation pop-up.
- This action cannot be undone.

### "Save List" Button

- This feature is a bit redundant, as the list is saved by default when an item is added or deleted. It exists for debugging purposes.

### "Import Plugs..." Feature

- Located in the `File` menu.
- This allows a list of plugs to be imported from another JSON file, rather than entering plugs manually.

---

## Developer Notes

### Depricated Files:

These are stored in their own folder. This includes a project I did to initally explore controlling the tapo plugs externally from the app.
