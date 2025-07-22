import unittest

import asyncio

import socket
from portals_lib import create_server_portal
from microenv import microenv


class TestServer(unittest.TestCase):
    def test_server(self):
        # def debug(data, scope):
        #     print(*data)

        server_portal = create_server_portal(
            microenv({"foo": "bar"}, {"id": "test_server"}),
            # {"debug": debug},
        )

        asyncio.run(server_portal("open"))

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind(("localhost", 8000))
        server_socket.listen(1)

        print("Server is listening on port 8000...")

        try:
            while True:
                client_socket, addr = server_socket.accept()
                print(f"Connection from {addr}")

                try:
                    request = client_socket.recv(1024).decode("utf-8")
                    # print("Received request:", request)

                    if request.startswith("POST /portal"):
                        body_start = request.index("\r\n\r\n") + 4
                        body = request[body_start:]
                        print("Request body:", body)

                        async def handle_request():
                            response = await server_portal("receive", body)
                            client_socket.sendall(
                                f"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: {len(response)}\r\n\r\n{response}".encode(
                                    "utf-8"
                                )
                            )

                        asyncio.run(handle_request())
                    else:
                        client_socket.sendall(b"HTTP/1.1 404 Not Found\r\n\r\n")

                except Exception as e:
                    print(f"Error handling request: {e}")
                    client_socket.sendall(b"HTTP/1.1 500 Internal Server Error\r\n\r\n")
                finally:
                    client_socket.close()

        except KeyboardInterrupt:
            print("Server stopped by user.")
        finally:
            server_socket.close()


if __name__ == "__main__":
    unittest.main()
