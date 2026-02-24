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
