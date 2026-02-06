# Tapo Automation

This project was put together in an effort to give my family control over our tapo plugs without having to use the app on the phone.

## Dependencies

```bash
pip install tapo
```

For Raspberry Pi:

From your project directory:

cd ~/tapo_automation

1️⃣ Make sure venv support is installed

```bash
sudo apt install python3-full -y
```

2️⃣ Create a virtual environment

```bash
python3 -m venv venv
```

This creates:

~/tapo_automation/venv/

3️⃣ Activate it
source venv/bin/activate

Your prompt should change to:

(venv) voltorb@voltorb:~/tapo_automation $

4️⃣ Install tapo inside the venv
pip install tapo

Install within venv:

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

5️⃣ Run your script
python main.py

Creating Service

Be sure to point to the virtual environment python!

[Unit]
Description=Tapo Plug Automation
After=network.target

[Service]
Type=simple
User=voltorb
WorkingDirectory=/home/voltorb/tapo_automation
ExecStart=/home/voltorb/tapo_automation/venv/bin/python /home/voltorb/tapo_automation/main.py
Restart=on-failure
RestartSec=5s

[Install]
WantedBy=multi-user.target

## Configure the Program

Be sure to fill in your own information before running.

**BE SURE to CREATE `config.py` TO CONTAIN YOUR SECRETS!**

```python
TAPO_USERNAME = "your_tapo_account_email"
TAPO_PASSWORD = "your_tapo_account_password"
PLUG_IP = "192.168.1.200"
```
