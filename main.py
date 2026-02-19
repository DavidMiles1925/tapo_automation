import asyncio
import threading
from datetime import datetime
from tapo import ApiClient
import aiohttp
from gpiozero import Button
from gpiozero.pins.lgpio import LGPIOFactory
from signal import pause
from config import TAPO_USERNAME, TAPO_PASSWORD, NTFY_URL, PLUG_IP_1, PLUG_IP_2
from logger import write_to_log

# -------------------------------
# GLOBALS
# -------------------------------
running = False  # prevents overlapping runs
PLUGS = [
    ("Camera - Living Room", PLUG_IP_1),
    ("Camera - Office", PLUG_IP_2),
]

# -------------------------------
# ASYNC LOOP SETUP
# -------------------------------
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

# Start the loop in a background thread
threading.Thread(target=loop.run_forever, daemon=True).start()

# -------------------------------
# BUTTON SETUP
# -------------------------------
button = Button(
    23,
    pull_up=True,
    bounce_time=0.15,  # 150ms debounce
    pin_factory=LGPIOFactory()
)

# -------------------------------
# NTFY NOTIFICATIONS
# -------------------------------
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

# -------------------------------
# POWER CYCLE FUNCTION
# -------------------------------
async def power_cycle(name, plug, off_time=5, retries=3):
    try:
        # OFF
        print(f"Turning plug {name} OFF")
        await plug.off()
        write_to_log(message=f"Plug OFF: {name}")
        await send_ntfy(f"Plug OFF: {name}")

        # Wait
        await asyncio.sleep(off_time)

        # ON
        print(f"Turning plug {name} ON")
        for attempt in range(1, retries + 1):
            try:
                await plug.on()
                write_to_log(message=f"Plug ON: {name}")
                await send_ntfy(f"Plug ON: {name}")
                print(f"Plug {name} turned ON")
                return
            except Exception as e:
                print(f"ON attempt {attempt} failed: {e}")
                write_to_log(message=f"ON attempt {attempt} failed: {e}")
                await asyncio.sleep(2)

    except Exception as e:
        print(f"Power cycle failed early: {e}")
        write_to_log(message=f"Power cycle failed for {name}: {e}")
        await send_ntfy(f"Power cycle failed for {name}: {e}")

# -------------------------------
# MAIN TASK
# -------------------------------
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
        client = ApiClient(TAPO_USERNAME, TAPO_PASSWORD)

        plug_handlers = []
        for name, ip in PLUGS:
            plug = await client.p100(ip)
            plug_handlers.append((name, plug))

        # Run power cycles concurrently
        await asyncio.gather(
            *(power_cycle(name, plug, off_time=5) for name, plug in plug_handlers)
        )

    except Exception as e:
        print(f"Top level exception: {e}")
        write_to_log(message=f"Top level exception: {e}")
        await send_ntfy(f"Top level exception: {e}")
    finally:
        running = False

# -------------------------------
# BUTTON CALLBACK
# -------------------------------
def on_button_pressed():
    print("Button pressed!")
    asyncio.run_coroutine_threadsafe(main(), loop)

button.when_pressed = on_button_pressed

# -------------------------------
# START
# -------------------------------
print("Waiting for button press on GPIO 23...")
try:
    pause()  # keeps main thread alive
except KeyboardInterrupt:
    print("\nShutting down cleanly")
