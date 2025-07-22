import asyncio

from ..micro_future import MicroFuture


def create_queue_suppliers(settings=None):
    futures = {}

    async def queue_out(data, scope):
        sender = data.id
        entry = data.payload
        portal = data.portal

        recipient = entry["recipient"]
        action = entry["action"]

        persistence = scope.demand({"type": "persistence"})
        crypto = scope.demand({"type": "crypto"})

        recipient_state_entry = await persistence.get(sender + "<>" + recipient) or {}
        state = recipient_state_entry.get("value", {"queue": []})
        queue = state.get("queue", [])
        # print("Current state:", state)

        entry_index = state.get("out_index", 0) + 1
        entry_uuid = crypto["random_uuid"]()
        entry_id = entry_uuid
        # entry_id = json.dumps(
        #     [
        #         sender,
        #         recipient,
        #         action,
        #         entry_index,
        #         entry_uuid,
        #     ]
        # )

        future = MicroFuture()
        futures[entry_id] = future

        queue_entry = {
            "id": entry_id,
            "index": entry_index,
            "sender": sender,
            "recipient": recipient,
            "action": action,
            "payload": entry["payload"],
        }

        queue.append(queue_entry)
        state["out_index"] = entry_index
        # print("New state:", state)
        await persistence.set(sender + "<>" + recipient, dict(state))

        asyncio.create_task(portal("queue.dispatch", {"recipient": recipient}))

        return await future.wait()

    async def queue_in(data, scope):
        payload = data.payload["payload"]
        persistence = scope.demand({"type": "persistence"})

        sender = data.payload["sender"]
        sender_state_entry = await persistence.get(data.id + "<>" + sender) or {}
        state = sender_state_entry.get("value", {"queue": []})
        in_index = state.get("in_index", 0)
        init_id = state.get("init_id", None)
        out_queue = state.get("queue", [])

        sync = payload["sync"]
        in_queue = payload["queue"]
        ids_to_remove = []

        for out_entry in out_queue:
            if out_entry["recipient"] != sender:
                continue

            if out_entry["index"] <= sync:
                if out_entry["action"] == "resolve":
                    ids_to_remove.append(out_entry["id"])
                continue
            else:
                break

        new_in_index = in_index
        for in_entry in in_queue:
            if in_entry["recipient"] != data.id:
                continue

            index = in_entry["index"]
            if index <= in_index:
                continue

            if index == 0 and sync == 0:
                init_id = in_entry["id"]

            new_in_index = index
            await queue_in_entry(in_entry, ids_to_remove, data.portal)

        out_queue = [entry for entry in out_queue if entry["id"] not in ids_to_remove]

        state["queue"] = out_queue
        state["in_index"] = new_in_index
        state["init_id"] = init_id
        await persistence.set(data.id + "<>" + sender, dict(state))

        return None

    async def queue_in_entry(entry, ids_to_remove, portal):
        sender = entry["sender"]
        action = entry["action"]
        payload = entry["payload"]

        if action == "resolve":
            resolve_id = payload["id"]
            ids_to_remove.append(resolve_id)

            if resolve_id in futures:
                future = futures.pop(resolve_id, None)
                if future and not future.done():
                    if ("error" in payload) and payload["error"]:
                        future.set_exception(Exception(payload["error"]))
                    else:
                        future.set_result(payload["value"])
        else:
            res = None
            error = None
            try:
                res = await portal(
                    "local." + action,
                    {"sender": sender, "payload": payload},
                )
            except Exception as e:
                error = str(e)

            asyncio.create_task(
                portal(
                    "queue.out",
                    {
                        "recipient": sender,
                        "action": "resolve",
                        "payload": {"id": entry["id"], "value": res, "error": error},
                    },
                )
            )

    async def queue_dispatch(data, scope):
        persistence = scope.demand({"type": "persistence"})

        recipient = data.payload["recipient"]

        recipient_state_entry = await persistence.get(data.id + "<>" + recipient) or {}
        state = recipient_state_entry.get("value", {"queue": []})
        queue = state.get("queue", [])
        in_index = state.get("in_index", 0)

        data.portal(
            "send",
            {"recipient": recipient, "payload": {"sync": in_index, "queue": queue}},
        )

        return None

    return {
        "queue.in": queue_in,
        "queue.out": queue_out,
        "queue.dispatch": queue_dispatch,
    }
