from .portals_lib import create_portal

import asyncio


def create_server_ether():
    resolvers_by_recipient = {}
    is_attached = [False]

    def middleware(super_methods):
        async def ether_attach(data, scope):
            is_attached[0] = True

        async def ether_detach(data, scope):
            is_attached[0] = False

        async def receive(data, scope):
            if not is_attached[0]:
                print("Server Ether -> tried to receive when detached")
                return

            portal = data.portal
            payload = data.payload

            receive_res = await portal("$super_receive", payload)

            sender = receive_res.get("sender") if receive_res else None
            if not sender:
                return

            loop = asyncio.get_event_loop()
            fut = loop.create_future()
            old_resolver = resolvers_by_recipient.get(sender)
            if old_resolver:
                old_resolver["resolve"](None)
            resolvers_by_recipient[sender] = {
                "resolve": fut.set_result,
                "reject": fut.set_exception,
            }

            return await fut

        async def ether_send(data, scope):
            if not is_attached[0]:
                print('Server Ether -> tried to "ether.send" when detached')
                return
            payload = data.payload
            recipient = payload["recipient"]
            payload_to_send = payload["payload"]
            resolver = resolvers_by_recipient.get(recipient)

            if resolver:
                resolvers_by_recipient.pop(recipient, None)
                resolver["resolve"](payload_to_send)

        return {
            "ether.attach": ether_attach,
            "ether.detach": ether_detach,
            "receive": receive,
            "ether.send": ether_send,
            "$super_receive": super_methods["receive"],
        }

    return middleware


def create_server_portal(
    env,
    middleware=None,
):
    return create_portal(env, [create_server_ether(), middleware])
