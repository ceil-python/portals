import unittest

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from microenv import microenv

from portals_lib import (
    create_client_portal,
    create_server_portal,
)


class TestPortals(unittest.TestCase):
    def test_tmp(
        self,
    ):
        def debug(data, scope):
            return
            # print(*data)

        async def test():
            async def test_func(param, _ref=None, caller=None, next_=False):
                return (
                    {
                        "msg": "test_func called",
                        "param": param,
                    },
                )

            env_a = microenv(
                {"foo": "bar", "test_func": test_func},
                {"id": "envA"},
            )
            env_b = microenv({"foo": "not bar"}, {"id": "envB"})

            portal1 = create_server_portal(
                env_a,
                {"debug": debug},
            )
            portal2 = create_client_portal(
                env_b,
                lambda data, signal=None: portal1("receive", data),
                None,
                {"debug": debug},
            )

            # local_ether_middleware = create_local_ether()
            # portal1 = create_portal(env_a, {**local_ether_middleware, "debug": debug})
            # portal2 = create_portal(env_b, {**local_ether_middleware, "debug": debug})

            await portal1("open")
            env_a_via_portal = await portal2("enter", "envA")
            print("env_a_via_porta:", env_a_via_portal.descriptor)

            env_a_foo = await env_a_via_portal.face["foo"]
            print("env_a_foo:", env_a_foo)

            await env_a_via_portal.set("foo", "baz")
            env_a_foo2 = await env_a_via_portal.face["foo"]
            print("env_a_foo2:", env_a_foo2)

            print(
                "test_func call result:",
                await env_a_via_portal.face["test_func"]("test_param"),
            )

            self.assertIsNot(env_a_via_portal, None)

        asyncio.run(test())


if __name__ == "__main__":
    unittest.main()
