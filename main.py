import asyncio
from tapo import ApiClient
from gpiozero import Device
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
from config import TAPO_USERNAME, TAPO_PASSWORD, PLUG_IP_1, PLUG_IP_2

button = Button(23, pull_up=True, pin_factory=LGPIOFactory())

tapo_username = TAPO_USERNAME
tapo_password = TAPO_PASSWORD
plug_ip_1 = PLUG_IP_1
plug_ip_2 = PLUG_IP_2

# Prevent overlapping runs if button is spammed
running = False


async def power_cycle(plug, off_time=5, retries=3):
    try:
        print(f"Turning plug {plug} OFF")
        await plug.off()

        await asyncio.sleep(off_time)

        print(f"Turning plug {plug} ON")
        for attempt in range(1, retries + 1):
            try:
                await plug.on()
                print("Plug turned ON")
                return
            except Exception as e:
                print(f"ON attempt {attempt} failed: {e}")
                await asyncio.sleep(2)

    except Exception as e:
        print(f"Power cycle failed early: {e}")


async def main():
    global running
    if running:
        print("Power cycle already running, ignoring button press")
        return

    running = True
    try:
        print("Starting Tapo client")
        client = ApiClient(tapo_username, tapo_password)

        plug_1 = await client.p100(plug_ip_1)
        plug_2 = await client.p100(plug_ip_2)

        await asyncio.gather(
            power_cycle(plug_1, off_time=5),
            power_cycle(plug_2, off_time=5),
        )

    except Exception as e:
        print(f"Top level exception: {e}")
    finally:
        running = False


def on_button_pressed():
    print("Button pressed!")
    asyncio.run(main())


# Attach button handler
button.when_pressed = on_button_pressed

print("Waiting for button press on GPIO 23...")
pause()  # Keeps the program running
