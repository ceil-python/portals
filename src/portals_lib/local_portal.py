from .portals_lib import create_portal

import asyncio


def create_local_ether():
    _portals = {}

    async def ether_attach(data, scope):
        _portals[data.id] = data.portal

    async def ether_send(data, scope):
        payload = data.payload
        recipient = payload["recipient"]
        payload_to_receive = payload["payload"]

        while True:
            remote_portal = _portals.get(recipient)
            if not remote_portal:
                await asyncio.sleep(1)
                continue
            await remote_portal("receive", payload_to_receive)
            break

    async def ether_detach(data, scope):
        _portals.pop(data.id, None)

    return {
        "ether.attach": ether_attach,
        "ether.send": ether_send,
        "ether.detach": ether_detach,
    }


def create_local_portal(
    env,
    local_ether,
    middleware=None,
):
    return create_portal(env, [local_ether, middleware])
