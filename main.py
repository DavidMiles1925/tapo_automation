import asyncio
from tapo import ApiClient
import aiohttp
from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
from config import TAPO_USERNAME, TAPO_PASSWORD, NTFY_URL, PLUG_IP_1, PLUG_IP_2
from logger import write_to_log

button = Button(
    23,
    pull_up=True,
    bounce_time=0.5,   # 500ms debounce
    pin_factory=LGPIOFactory()
)


tapo_username = TAPO_USERNAME
tapo_password = TAPO_PASSWORD

PLUGS = [
    ("Camera - Living Room", PLUG_IP_1),
    ("Camera - Office", PLUG_IP_2),
]

# Prevent overlapping runs if button is spammed
running = False


async def power_cycle(name, plug, off_time=5, retries=3):
    try:
        print(f"Turning plug {name} OFF")
        await plug.off()
        await send_ntfy(f"Plug OFF: {name}")
        write_to_log(message=f"Plug OFF: {name}")

        await asyncio.sleep(off_time)

        print(f"Turning plug {plug} ON")
        for attempt in range(1, retries + 1):
            try:
                await plug.on()
                print("Plug turned ON")
                await send_ntfy(f"Plug ON: {name}")
                write_to_log(message=f"Plug ON: {name}")

                return
            except Exception as e:
                print(f"ON attempt {attempt} failed: {e}")
                write_to_log(message=f"ON attempt {attempt} failed: {e}")
                await asyncio.sleep(2)

    except Exception as e:
        print(f"Power cycle failed early: {e}")
        write_to_log(message=f"Power cycle failed for {name}: {e}")
        await send_ntfy(f"Power cycle failed for {name}: {e}")


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
        write_to_log(message="Starting Tapo client")
        client = ApiClient(tapo_username, tapo_password)

        plug_handlers = []

        for name, ip in PLUGS:
            plug = await client.p100(ip)
            plug_handlers.append((name, plug))

        await asyncio.gather(
            *(power_cycle(name, plug, off_time=3600) for name, plug in plug_handlers)
        )

    except Exception as e:
        print(f"Top level exception: {e}")
        write_to_log(message=f"Top level exception: {e}")
        await send_ntfy(f"Top level exception: {e}")
    finally:
        running = False


def on_button_pressed():
    global running

    if running:
        return

    print("Button pressed!")
    button.when_pressed = None  # temporarily disable
    asyncio.run(main())
    button.when_pressed = on_button_pressed  # re-enable
    

print("Waiting for button press on GPIO 23...")
try:
    pause()
except KeyboardInterrupt:
    print("\nShutting down cleanly")