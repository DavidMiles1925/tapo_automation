# Tapo Automation

This project was put together in an effort to give my family control over our tapo plugs without having to use the app on the phone.

## Dependencies

```bash
pip install tapo
```

## Configure the Program

Be sure to fill in your own information before running.

**BE SURE to CREATE `config.py` TO CONTAIN YOUR SECRETS!**

```python
TAPO_USERNAME = "your_tapo_account_email"
TAPO_PASSWORD = "your_tapo_account_password"
PLUG_IP = "192.168.1.200"
```
