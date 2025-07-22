from .portals_lib import create_portal

import asyncio


def get_timeout_from_attempts(num_attempts):
    return min(1000 * num_attempts, 10000)  # milliseconds


def create_client_ether(send, strategy=None):
    _portals = {}
    active_requests = [0]  # Mutable for nested update
    is_detached = [True]
    signal = [{}]

    async def ether_attach(data, scope):
        _portals[data.id] = data.portal
        is_detached[0] = False

    async def ether_send(data, scope):
        if signal[0].get("on_abort"):
            signal[0]["on_abort"]()
        signal[0] = {}
        if is_detached[0]:
            return False

        payload = data.payload
        portal = data.portal
        msg_data = payload["payload"]
        recipient = payload["recipient"]
        num_attempts = 0

        async def _send():
            if is_detached[0]:
                return None

            nonlocal num_attempts
            num_attempts += 1
            try:
                res = await send(msg_data, signal[0])
                signal[0] = {}
                if is_detached[0]:
                    return False
                return res
            except Exception as e:
                print(f"Client ether send error: {e}")
                abort_name = getattr(e, "name", "") or getattr(e, "args", [""])[0]
                if is_detached[0] or abort_name == "AbortError":
                    return False
                delay = get_timeout_from_attempts(num_attempts)
                await asyncio.sleep(delay)
                return await _send()

        active_requests[0] += 1
        received_data = await _send()
        active_requests[0] -= 1

        if received_data:
            await portal("receive", received_data)
        # if (
        #     strategy == "poll"
        #     and active_requests[0] == 0
        #     and received_data is not False
        # ):
        #     await portal("queue", ["dispatch", recipient])

    async def ether_detach(data, scope):
        is_detached[0] = True
        if signal[0].get("on_abort"):
            signal[0]["on_abort"]()
        signal[0] = {}

    return {
        "ether.attach": ether_attach,
        "ether.send": ether_send,
        "ether.detach": ether_detach,
    }


def create_client_portal(
    env,
    send,
    strategy=None,
    middleware=None,
):
    return create_portal(env, [create_client_ether(send, strategy), middleware])
