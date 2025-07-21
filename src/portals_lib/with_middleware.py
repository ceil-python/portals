def with_middleware(suppliers, middleware=None):
    result = suppliers.copy()
    if not middleware:
        return result
    mlist = middleware if isinstance(middleware, list) else [middleware]
    for m in mlist:
        if not m:
            continue
        overrides = m(result) if callable(m) else m
        for key, val in overrides.items():
            if val is not None:
                result[key] = val
    return result
