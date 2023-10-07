#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function, absolute_import

import click
import asyncio

from ._ssh_orchestration import inv_import, exec_sync_main_pipeline, exec_async_main_pipeline
from ._custom_dtypes import list_or_str

import click_completion
click_completion.init(complete_options=True)


@click.group()
def py4ops():
    """
    Py4ops is a python package for orchestration of remote servers using ssh and containers using docker.
    """
        
    pass

@py4ops.command(help="Run tasks on remote servers.")
@click.option("-i", "--inventory", help="Path to Inventory file to use or single host to connect to", type=str, required=True)
@click.option("-u", "--user", help="User to connect as", type=str, required=False)
@click.option("-p", "--password", help="Password to use for authentication", type=str, required=False, hide_input=True) # TODO add password prompt
@click.option("-cl", "--cmd-list", help="List of commands to execute", type=str, required=True)
@click.option("-s", "--strict", help="Exit if any command fails", is_flag=True)
@click.option("-c", "--check-ssh-conn", help="Check ssh connection before executing commands", is_flag=True)
@click.option("-ct", "--conn-timeout", help="Timeout for ssh connection", type=int, default=None)
@click.option("-et", "--exec-timeout", help="Timeout for ssh command", type=int, default=None)
@click.option("-ltc", "--log-to-console", help="Log to console", is_flag=True)
@click.option("-ltf", "--log-to-file", help="Log to file", is_flag=True)
@click.option("-a", "--asyncronous", help="Execute commands asynchronously", is_flag=True)
def run(
    inventory,
    user,
    password, 
    conn_timeout,
    exec_timeout,
    cmd_list,
    strict,
    check_ssh_conn,
    log_to_console,
    log_to_file,
    asyncronous,
    ):
    """
    Run tasks on remote servers.
    """
    
    inv_data = inv_import(inventory)
    
    if asyncronous:
        asyncio.run(exec_async_main_pipeline(
            inv=inv_data,
            user=user,
            password=password,
            conn_timeout=conn_timeout,
            exec_timeout=exec_timeout,
            cmd_list=cmd_list,
            strict=strict,
            check_ssh_conn=check_ssh_conn,
            log_to_console=log_to_console,
            log_to_file=log_to_file
            )
        )
    else:
        exec_sync_main_pipeline(            
            inv=inv_data,
            user=user,
            password=password,
            conn_timeout=conn_timeout,
            exec_timeout=exec_timeout,
            cmd_list=cmd_list,
            strict=strict,
            check_ssh_conn=check_ssh_conn,
            log_to_console=log_to_console,
            log_to_file=log_to_file
            )

@py4ops.command()
def list():
    """
    List available tasks or servers.
    """

    pass


if __name__ == "__main__":
    py4ops()
        