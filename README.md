# Tapo Automation

This project was put together in an effort to give my family control over our tapo plugs without having to use the app on the phone.

## Dependencies

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
pip install tapo
```

```bash
pip install gpiozero
```

You must install `swig` to install `lgpio`

```bash
sudo apt install swig
```

```bash
sudo apt install liblgpio-dev
```

```bash
pip install lgpio
```

```bash
pip install aiohttp
```

### 5️⃣ Run your script

```bash
python main.py
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
User=voltorb
WorkingDirectory=/home/pi_name/git_repo
ExecStart=/home/voltorb/tapo_automation/venv/bin/python /home/pi_name/git_repo/myapp.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

## Configure the Program

**BE SURE to CREATE `config.py` TO CONTAIN YOUR SECRETS!**

Copy and paste the following into the file. Be sure to fill in _your own information_ before running.

```python
LOG_DIRECTORY_PATH = "/home/voltorb/tapo_automations/logs/"

TAPO_USERNAME = "your_tapo_account_email"
TAPO_PASSWORD = "your_tapo_account_password"

NTFY_URL = "https://ntfy.sh/your_topic"

PLUG_IP = "192.168.1.200"
```
