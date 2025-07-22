import asyncio


def create_send_supplier():
    def send(data, scope):
        data_to_pack = dict(data.payload)
        data_to_pack["sender"] = data.id
        del data_to_pack["recipient"]

        send_payload = data.portal("packager.pack", data_to_pack)

        asyncio.create_task(
            data.portal(
                "ether.send",
                {"recipient": data.payload["recipient"], "payload": send_payload},
            )
        )

        return None

    return send
