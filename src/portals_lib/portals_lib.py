from supply_demand import supply_demand
from layered_persistence import LayeredPersistence, RuntimeLayer

from .with_middleware import with_middleware
from .suppliers import (
    init_supplier,
    ether_suppliers,
    local_suppliers,
    remote_suppliers,
    open_supplier,
    close_supplier,
    enter_supplier,
    leave_supplier,
    guest_supplier,
    crypto_supplier,
    json_packager,
    create_send_supplier,
    receive_supplier,
    create_queue_suppliers,
)


def create_portal(env, middleware=None):
    portal_id = env.descriptor.get("id", None)
    if not portal_id:
        raise ValueError("create_portal: given env has no id in descriptor")

    suppliers = {
        "init": init_supplier,
        "open": open_supplier,
        "close": close_supplier,
        "enter": enter_supplier,
        "leave": leave_supplier,
        "guest": guest_supplier,
        "send": create_send_supplier(),
        "receive": receive_supplier,
        "crypto": crypto_supplier,
    }

    suppliers.update(ether_suppliers)
    suppliers.update(local_suppliers)
    suppliers.update(remote_suppliers)
    suppliers.update(json_packager)
    suppliers.update(create_queue_suppliers({"outgoing_buffer_ms": 200}))

    # Apply middleware overrides
    suppliers = with_middleware(suppliers, middleware)

    # Ensure persistence supplier is present
    if "persistence" not in suppliers:
        persistence = LayeredPersistence([RuntimeLayer()])

        def persistenceSupplier(d, s):
            return persistence

        suppliers["persistence"] = persistenceSupplier

    def root_supplier(data, scope):
        # Invoke init supplier to establish portal
        return scope.demand(
            {
                "type": "init",
                "data": {"id": portal_id, "env": env},
            }
        )

    # Build portal method using supply_demand
    return supply_demand(root_supplier, suppliers)
