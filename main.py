import asyncio
from tapo import ApiClient
import aiohttp
from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
from config import TAPO_USERNAME, TAPO_PASSWORD, NTFY_URL, PLUG_IP_1, PLUG_IP_2
from logger import write_to_log

button = Button(23, pull_up=True, pin_factory=LGPIOFactory())

tapo_username = TAPO_USERNAME
tapo_password = TAPO_PASSWORD
plug_ip_1 = PLUG_IP_1
plug_ip_2 = PLUG_IP_2

# Prevent overlapping runs if button is spammed
running = False


async def power_cycle(plug, off_time=5, retries=3):
    try:
        print(f"Turning plug {plug.host} OFF")
        await plug.off()
        await send_ntfy(f"Plug OFF: {plug.host}")
        write_to_log(message=f"Plug OFF: {plug.host}")

        await asyncio.sleep(off_time)

        print(f"Turning plug {plug} ON")
        for attempt in range(1, retries + 1):
            try:
                await plug.on()
                print("Plug turned ON")
                await send_ntfy(f"Plug ON: {plug.host}")
                write_to_log(message=f"Plug ON: {plug.host}")

                return
            except Exception as e:
                print(f"ON attempt {attempt} failed: {e}")
                write_to_log(message=f"ON attempt {attempt} failed: {e}")
                await asyncio.sleep(2)

    except Exception as e:
        print(f"Power cycle failed early: {e}")
        write_to_log(message=f"Power cycle failed for {plug.host}: {e}")
        await send_ntfy(f"Power cycle failed for {plug.host}: {e}")


async def send_ntfy(message, title="Tapo Power Cycle"):
    try:
        async with aiohttp.ClientSession() as session:
            await session.post(
                NTFY_URL,
                data=message.encode("utf-8"),
                headers={
                    "Title": title,
                    "Priority": "2"
                }
            )
    except Exception as e:
        print(f"Failed to send ntfy notification: {e}")


async def main():
    global running
    if running:
        print("Power cycle already running, ignoring button press")
        write_to_log(message="Power cycle already running, ignoring button press")
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
        write_to_log(message=f"Top level exception: {e}")
        await send_ntfy(f"Top level exception: {e}")
    finally:
        running = False


def on_button_pressed():
    print("Button pressed!")
    asyncio.run(main())


# Attach button handler
button.when_pressed = on_button_pressed

print("Waiting for button press on GPIO 23...")
try:
    pause()
except KeyboardInterrupt:
    print("\nShutting down cleanly")