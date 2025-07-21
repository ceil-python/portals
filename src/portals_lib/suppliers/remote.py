from microenv import microenv


async def remote_enter_supplier(data, scope):
    remoteId = data.payload["id"]

    return await data.portal(
        "queue.out",
        {
            "recipient": remoteId,
            "action": "enter",
            "payload": {"id": remoteId},
        },
    )


async def remote_supplier(data, scope):
    action = scope.type.split(".")[1]
    recipient = data.payload["recipient"]
    payload = data.payload.copy()
    del payload["recipient"]

    return await data.portal(
        "queue.out",
        {
            "recipient": recipient,
            "action": action,
            "payload": payload,
        },
    )


remote = {
    "remote.enter": remote_enter_supplier,
    "remote.leave": remote_supplier,
    "remote.resolve": remote_supplier,
    "remote.get": remote_supplier,
    "remote.set": remote_supplier,
    "remote.call": remote_supplier,
}
