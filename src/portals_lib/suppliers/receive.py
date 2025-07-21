async def receive(data, scope):
    received_data = data.portal("packager.unpack", data.payload)

    sender = received_data["sender"]

    await data.portal("queue.in", received_data)

    return {"sender": sender}
