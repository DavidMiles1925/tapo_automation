import asyncio
from tapo import ApiClient
from config import TAPO_USERNAME, TAPO_PASSWORD, PLUG_IP_1, PLUG_IP_2

# Replace these with your actual info
tapo_username = TAPO_USERNAME
tapo_password = TAPO_PASSWORD
plug_ip_1 = PLUG_IP_1
plug_ip_2 = PLUG_IP_2


async def power_cycle(plug, off_time=5, retries=3):
    """
    Turns the plug off, waits, then turns it back on.
    """
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
    try:
        print("starting client")
        client = ApiClient(tapo_username, tapo_password)

        # Use p100 for most Tapo plugs (P100 / P110 / P115)
        plug_1 = await client.p100(plug_ip_1)
        plug_2 = await client.p100(plug_ip_2)

        await asyncio.gather(
            power_cycle(plug_1, off_time=5),
            power_cycle(plug_2, off_time=5),
        )
    except Exception as e:
        print(f"Top level exception: {e}")

asyncio.run(main())
