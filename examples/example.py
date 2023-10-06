from py4ops import inv_import, exec_sync_main_pipeline, exec_async_main_pipeline
from config import ALL_INVENTORY_PATH, OCR_32C_64G_INVENTORY_PATH, OCR_32C_32G_INVENTORY_PATH, DB_INVENTORY_PATH, OCR_ALL_INVENTORY_PATH
import asyncio

INV_LIST = [OCR_32C_64G_INVENTORY_PATH,DB_INVENTORY_PATH]

inv = inv_import(["192.168.1.2", "192.168.1.3"])
inv = inv_import({"asd": "193.168.1.4"})
inv = inv_import(OCR_32C_32G_INVENTORY_PATH)
inv = inv_import(INV_LIST)


#exec_sync_main_pipeline(inv, "ubuntu", ["ls", "pwd"], strict=True, check_ssh_conn=True)

asyncio.run(exec_async_main_pipeline(inv, "ubuntu", ["ls", "pwd"], strict=True, check_ssh_conn=True))