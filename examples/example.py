from py4ops import inv_import, exec_sync_main_pipeline, exec_async_main_pipeline
import asyncio

inv = inv_import("192.168.1.20")

exec_sync_main_pipeline(inv, "user", ["ls", "pwd"], strict=True, check_ssh_conn=True)
asyncio.run(exec_async_main_pipeline(inv, "ctolon", ["ls", "pwd"], strict=True, check_ssh_conn=True))