import asyncio
from tapo import ApiClient
from config import TAPO_USERNAME, TAPO_PASSWORD, PLUG_IP

# Replace these with your actual info
tapo_username = TAPO_USERNAME
tapo_password = TAPO_PASSWORD
plug_ip = PLUG_IP

async def main():
    # Create the API client
    print("Creaiting Client")
    client = ApiClient(tapo_username, tapo_password)

    # Connect to the plug
    print("await...")
    print(plug_ip)
    plug = await client.p115(plug_ip)

    # Turn the plug ON
    print("Turning plug ON")
    await plug.on()

    # Wait 5 seconds
    await asyncio.sleep(5)

    # Turn the plug OFF
    print("Turning plug OFF")
    await plug.off()

# Run the async program
asyncio.run(main())
