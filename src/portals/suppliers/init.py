class MiddlewareInput:
    def __init__(self, id, env, portal, payload):
        self.id = id
        self.env = env
        self.portal = portal
        self.payload = payload


def init(data, scope):
    id_ = data["id"]
    env = data["env"]
    demand = scope.demand

    has_debug = "debug" in scope.available_supplier_types
    depth = [1]

    def portal(action, payload=None):
        if has_debug:
            demand(
                {
                    "key": "debug",
                    "type": "debug",
                    "data": [f"[portal {id_}]", "··" * depth[0], action, payload],
                }
            )

            depth[0] += 1

            result = demand(
                {
                    "key": action,
                    "type": action,
                    "data": MiddlewareInput(
                        id_,
                        env,
                        portal,
                        payload,
                    ),
                }
            )

            depth[0] -= 1

            demand(
                {
                    "key": "debug",
                    "type": "debug",
                    "data": [
                        f"[portal {id_}]",
                        "··" * depth[0],
                        action,
                        "resolved as",
                        result,
                    ],
                }
            )
            return result
        else:
            return demand(
                {
                    "key": action,
                    "type": action,
                    "data": MiddlewareInput(
                        id_,
                        env,
                        portal,
                        payload,
                    ),
                }
            )

    return portal
