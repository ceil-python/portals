from portals_lib import create_client_ether

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio


def create_fetch_ether(endpoint, fetch_method):
    async def send(data, signal):
        # print("Fetch Ether > send:", endpoint, data)

        if not isinstance(data, str):
            print(
                "fetch ether > send: unsupported data format. Only supporting 'string' at the moment."
            )
            return None

            # abort_controller = asyncio.Event()

            # def on_abort():
            #     abort_controller.set()

            # signal["on_abort"] = on_abort

        res = fetch_method(endpoint, data)

        if res.ok:
            return res.text
        else:
            raise Exception(
                f"Fetch Ether > send: request failed with status {res.status_code}"
            )

    return create_client_ether(send)
