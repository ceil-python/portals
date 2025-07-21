from microenv import microenv


async def enter(data, scope):
    await data.portal("ether.attach")

    enter_data = await data.portal("remote.enter", {"id": data.payload})

    def remote_get(key, env, caller=None, next_=False):
        descriptor = env.descriptor
        property_descriptor = next(
            (child for child in descriptor["children"] if child["key"] == key), None
        )

        if (property_descriptor["type"] == "function") or (
            isinstance(property_descriptor["type"], dict)
            and property_descriptor["type"].get("extends") == "function"
        ):
            return lambda payload: data.portal(
                "remote.call",
                {"recipient": enter_data["id"], "key": key, "value": payload},
            )

        return data.portal(
            "remote.get",
            {"recipient": enter_data["id"], "key": key, "next": next_},
        )

    def remote_set(key, value, env, caller=None):
        descriptor = env.descriptor
        property_descriptor = next(
            (child for child in descriptor["children"] if child["key"] == key), None
        )

        if (property_descriptor["type"] == "function") or (
            isinstance(property_descriptor["type"], dict)
            and property_descriptor["type"].get("extends") == "function"
        ):
            raise ValueError("Cannot set function type")

        return data.portal(
            "remote.set",
            {
                "recipient": enter_data["id"],
                "key": key,
                "value": value,
            },
        )

    remote_env = microenv(
        {},
        enter_data["envDescriptor"],
        {
            "get": remote_get,
            "set": remote_set,
        },
    )

    return remote_env
