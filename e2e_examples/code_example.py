from py4ops import inv_import, exec_sync_main_pipeline, exec_async_main_pipeline
import asyncio

inv = inv_import("192.168.3.106")

run_sync = True

def main():

    if run_sync:
        exec_sync_main_pipeline(
            inv,
            "ctolon",
            None,
            conn_timeout=10,
            exec_timeout=10,
            cmd_list=["ls", "pwd"],
            strict=True,
            check_ssh_conn=True
            )
        return
    
    
    asyncio.run(exec_async_main_pipeline(
        inv,
        "ctolon",
        None,
        conn_timeout=10,
        exec_timeout=10,
        cmd_list=["ls", "pwd"],
        strict=True,
        check_ssh_conn=True
        )
    )
    
if __name__ == "__main__":
    main()