try:
    import inspect

    is_awaitable = inspect.isawaitable
except ImportError:
    # MicroPython
    def is_awaitable(val):
        is_awaitable = True
        try:
            return getattr(val, "__await__")
        except:
            try:
                getattr(val, "__next__")
            except:
                is_awaitable = False
        return is_awaitable


async def enter_supplier(data, scope):
    if data.id != data.payload["payload"]["id"]:
        raise ValueError("Unauthorised")

    data.portal("guest", data.payload["sender"])

    public_children = [
        child
        for child in data.env.descriptor["children"]
        if not child.get("private", False)
    ]

    env_descriptor = data.env.descriptor.copy()
    env_descriptor["children"] = public_children

    return {
        "id": data.id,
        "envDescriptor": env_descriptor,
    }


def local_supplier(data, scope):
    raise NotImplementedError(f"{scope.type} suppliers not implemented")


async def local_get_supplier(data, scope):
    env = data.env
    payload = data.payload["payload"]
    key = payload["key"]
    sender = data.payload.get("sender", None)
    next_ = data.payload.get("next", None)

    return env.get(key, sender, next_)


async def local_set_supplier(data, scope):
    env = data.env
    payload = data.payload["payload"]
    key = payload["key"]
    value = payload["value"]
    sender = data.payload.get("sender", None)

    return env.set(key, value, sender)


async def local_call_supplier(data, scope):
    env = data.env
    payload = data.payload["payload"]
    key = payload["key"]
    value = payload["value"]
    sender = data.payload.get("sender", None)

    res = env.get(key, sender)(value, env, sender)

    if is_awaitable(res):
        return await res

    return res


local = {
    "local.enter": enter_supplier,
    "local.leave": local_supplier,
    "local.get": local_get_supplier,
    "local.set": local_set_supplier,
    "local.call": local_call_supplier,
}
