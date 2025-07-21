def not_implemented_supplier(data, scope):
    raise NotImplementedError(f"{scope.type} not implemented")


ether = {
    "ether.attach": not_implemented_supplier,
    "ether.send": not_implemented_supplier,
    "ether.detach": not_implemented_supplier,
}
