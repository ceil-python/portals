try:
    import ujson as json
except ImportError:
    import json


def packager_pack(data, scope):
    return json.dumps(data.payload)


def packager_unpack(data, scope):
    return json.loads(data.payload)


json_packager = {
    "packager.pack": packager_pack,
    "packager.unpack": packager_unpack,
}
