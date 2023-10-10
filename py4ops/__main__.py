#!/usr/bin/env python
# -*- coding: utf-8 -*-


from __future__ import print_function, absolute_import
import argparse
import asyncio

from ._ssh_orchestration import inv_import, exec_sync_main_pipeline, exec_async_main_pipeline, call_check_ssh


def run(args):
    """
    Run tasks on remote servers.
    """
    inv_data = inv_import(args.inventory)

    if args.asyncronous:
        asyncio.run(exec_async_main_pipeline(
            inv=inv_data,
            user=args.user,
            password=args.password,
            conn_timeout=args.conn_timeout,
            exec_timeout=args.exec_timeout,
            cmd_list=args.cmd_list,
            strict=args.strict,
            check_ssh_conn=args.check_ssh_conn,
            log_to_console=args.log_to_console,
            log_to_file=args.log_to_file
            )
        )
    else:
        exec_sync_main_pipeline(
            inv=inv_data,
            user=args.user,
            password=args.password,
            conn_timeout=args.conn_timeout,
            exec_timeout=args.exec_timeout,
            cmd_list=args.cmd_list,
            strict=args.strict,
            check_ssh_conn=args.check_ssh_conn,
            log_to_console=args.log_to_console,
            log_to_file=args.log_to_file
            )
        
def ssh_check(args):
    """
    Check ssh connection to remote servers.
    """
    inv_data = inv_import(args.inventory)
    
    if isinstance(inv_data, dict):
        res_list = [] 
        for vm_name, ip in inv_data.items():
            result = call_check_ssh(
                ip=ip,
                strict=args.strict,
                conn_timeout=args.conn_timeout,
                only_error=args.only_errors,
                show_info=args.show_info
            )
            res_list.append(result)
            
        if all(res_list):
            print("All ssh connections are ok.")
            
            
    elif isinstance(inv_data, list):
        res_list = []
        for ip in inv_data:
            result = call_check_ssh(
                ip=ip,
                strict=args.strict,
                conn_timeout=args.conn_timeout,
                only_error=args.only_errors,
                show_info=args.show_info
            )
        if all(res_list):
            print("All ssh connections are ok.")
    
    elif isinstance(inv_data, str):
        result = call_check_ssh(
            ip=inv_data,
            strict=args.strict,
            conn_timeout=args.conn_timeout,
            only_error=args.only_errors,
            show_info=args.show_info
        )
        
        if result:
            print("All ssh connections are ok.")
        
    else:
        raise TypeError(f"The inventory must be a dictionary, a list or a string. Found: {type(inv_data)}")
    
    

def py4ops():
    parser = argparse.ArgumentParser(description="Py4ops is a python package for orchestration of remote servers using ssh and containers using docker.")
    subparsers = parser.add_subparsers()

    run_parser = subparsers.add_parser("run", help="Run tasks on remote servers.")
    run_parser.add_argument("-i", "--inventory", help="Path to Inventory file to use or single host to connect to", type=str, required=True)
    run_parser.add_argument("-u", "--user", help="User to connect as", type=str, required=False)
    run_parser.add_argument("-p", "--password", help="Password to use for authentication", type=str, required=False)
    run_parser.add_argument("-cl", "--cmd-list", help="List of commands to execute", type=str, required=True, nargs="*")
    run_parser.add_argument("-s", "--strict", help="Exit if any command fails", action="store_true")
    run_parser.add_argument("-c", "--check-ssh-conn", help="Check ssh connection before executing commands", action="store_true")
    run_parser.add_argument("-ct", "--conn-timeout", help="Timeout for ssh connection", type=int, default=None)
    run_parser.add_argument("-et", "--exec-timeout", help="Timeout for ssh command", type=int, default=None)
    run_parser.add_argument("-ltc", "--log-to-console", help="Log to console", action="store_true")
    run_parser.add_argument("-ltf", "--log-to-file", help="Log to file", action="store_true")
    run_parser.add_argument("-a", "--asyncronous", help="Execute commands asynchronously", action="store_true")
    run_parser.set_defaults(func=run)
    
    ssh_check_parser = subparsers.add_parser("ssh-check", help="Path to Inventory file to use or single host to connect to")
    ssh_check_parser.add_argument("-i", "--inventory", help="IP address of remote server", type=str, required=True)
    ssh_check_parser.add_argument("-s", "--strict", help="Exit if ssh connection fails", action="store_true")
    ssh_check_parser.add_argument("-ct", "--conn-timeout", help="Timeout for ssh connection", type=int, default=5, required=True)
    ssh_check_parser.add_argument("-oe", "--only-errors", help="Only print errors", action="store_true")
    ssh_check_parser.add_argument("-si", "--show-info", help="Show info", action="store", type=bool, default=True)
    ssh_check_parser.set_defaults(func=ssh_check)

    list_parser = subparsers.add_parser("list", help="List available tasks or servers.")
    list_parser.set_defaults(func=lambda args: print("List not implemented yet."))

    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    py4ops()
        