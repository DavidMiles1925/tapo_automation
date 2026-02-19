# Tapo Automation

This project was put together in an effort to give my family control over our tapo plugs without having to use the app on the phone.

## Features

Currently, the app is in its infancy, and is being used to disable some cameras for privacy. I have some cat cameras I use to keep an eye on my cats while I am travelling, but I like for the family members who come over to check on the cats to feel they can have their privacy. This project allows them to simply press a button and shut the cameras down for an hour.

## Pi Automation (main.py)

### Dependencies

For Raspberry Pi:

From your project directory:

cd ~/tapo_automation

### 1️⃣ Make sure venv support is installed

```bash
sudo apt install python3-full -y
```

### 2️⃣ Create a virtual environment

```bash
python3 -m venv venv
```

This creates:

~/tapo_automation/venv/

### 3️⃣ Activate it

```bash
source venv/bin/activate
```

Your prompt should change to:

(venv) voltorb@voltorb:~/tapo_automation $

### 4️⃣ Install dependencies inside the venv

Install within venv:

```bash
sudo apt install tapo
```

```bash
sudo apt install aiohttp
```

```bash
sudo apt install pytube
```

```bash
sudo apt install tk
```

**Raspberry Pi Only:**

```bash
sudo apt install gpiozero
```

You must install `swig` to install `lgpio`

```bash
sudo apt install swig
```

```bash
sudo apt install liblgpio-dev
```

```bash
sudo apt install lgpio
```

### 5️⃣ Run your script

```bash
python main.py
```

**NEW GUI!**

```bash
python lightswitch.py
```

## Creating a Service to Run at Startup

```bash
sudo nano /etc/systemd/system/myapp.service
```

Be sure to point to the virtual environment python!

```bash
[Unit]
Description=Tapo Plug Automation
After=network.target

[Service]
Type=simple
User=pi_name
WorkingDirectory=/home/pi_name/git_repo
ExecStart=/home/pi_name/tapo_automation/venv/bin/python /home/pi_name/git_repo/myapp.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

## Configure the Program

**BE SURE to CREATE `config.py` TO CONTAIN YOUR SECRETS!**

Copy and paste the following into the file. Be sure to fill in _your own information_ before running.

```python
LOG_DIRECTORY_PATH = "/home/pi_name/tapo_automations/logs/"

TAPO_USERNAME = "your_tapo_account_email"
TAPO_PASSWORD = "your_tapo_account_password"

NTFY_URL = "https://ntfy.sh/your_topic"

PLUG_IP = "192.168.1.200"
```

## Light Switch Program (lightswitch.py)

### Description

This is a program used to control the on/off state of Tapo plugs and bulbs. (I may expand funtionallity to include Kasa devices in the future.) I developed it as a solution for my diabled son to be able to turn lights on and off in his bedroom without having to dig his cell phone out to operate the smart plugs and/or bulbs.

The program contains a simple list of devices that are displayed with a description and the device IP address. Devices can easily be added or removed with the click of a button.

### Dependencies

This program is designed to run from a desktop computer or a Raspberry Pi running a full Desbian installation.

You must have Python fully installed

- For Windows, Mac, or desktop Linux use the python installer from their website.
- For Raspberry Pi:

```bash
sudo apt install python3-full -y
```

**Install Required Libraries:**

For Raspberry Pi, replace `pip` with `sudo apt`.

```bash
pip install tapo
```

```bash
pip install aiohttp
```

```bash
pip install pytube
```

```bash
pip install tk
```

### Installation

From the command line or terminal, clone the repository:

```bash
git clone https://github.com/DavidMiles1925/tapo_automation
```

### Setting Credentials

#### Option 1 - Use `config.py` File (recommended for debugging only):

Within the same directory as `lightswitch.py`, create a file called `config.py`. If you have already done this using the instructions in the Dependencies section, you can re-use this file.

```python
TAPO_USERNAME = "your_tapo_account_email"
TAPO_PASSWORD = "your_tapo_account_password"
```

**_Add the `config.py` file to your .gitignore to prevent it from being committed to source control._**

Replace _your_tapo_account_email_ and _your_tapo_account_password_ with your true values.

#### Option 2 - Use Environment Variables (more secure)

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

If credentials are not able to be imported from config.py and there are no environment variables set, the program will ask you to manually enter credentials.

### Using the Program

#### Add a Plug

- Click the "Add Plug" button to add a device to the list. Enter a description (can be anything) and the device's IP address.
- Duplicate entries are allowed, but not recommended for obvious reasons.

> Note: The list of devices stored in the user's home directory within a file called `.tapo_plugs.json`

#### ON and OFF

- Clicking either button sends a command to the plug and awaits a response. If there is an authentication error, the user will recieve a pop-up warning.
- The button that was clicked/pressed last will be highlighted. This is not a reliable indicator of the device's status, and is only influenced by the last press.

#### Edit

- This feature allows a device's properties to be edited.
- Once edited, changes cannot be undone.

#### Remove

- This will remove a device from the list.
- You will receive a confirmation pop-up.
- This action cannot be undone.

#### Save List

- This feature is a bit redundant, as the list is saved by default when an item is added or deleted. It exists for debugging purposes.
