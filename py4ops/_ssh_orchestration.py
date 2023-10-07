"""SSH Orchestration module."""

import subprocess
import asyncio
import os
from typing import Union, List
import yaml

import paramiko
import asyncssh

from ._checkers import is_valid_ip_address, is_valid_ipv4_address, is_valid_ipv6_address, check_ssh


def reverse_dict(d: dict) -> dict:
    """Reverse a dictionary."""
    
    return dict((v, k) for k, v in d.items())

def get_all_hosts_from_yaml(inv: str) -> dict:
    """Get all the hosts from a YAML file."""
    
    if not (inv.endswith(".yml") or inv.endswith(".yaml")):
        raise TypeError("The YAML file must be a dictionary.")
    
    with open(inv, "r") as stream:
        try:
            f = yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            raise exc
        
    if not isinstance(f, dict):
        raise TypeError("The YAML file must be a dictionary.")
    
    # Get all the keys in the YAML file
    all_yaml_keys = f.keys()

    # Get all the hosts in the YAML file
    all_hosts = {}
    for host_key in all_yaml_keys:
        host_list = f[host_key]["hosts"]
        all_hosts.update(host_list)
        
    r_all_hosts = dict((v, k) for k, v in all_hosts.items())
    if all({is_valid_ip_address(ip) for ip in all_hosts}):
        return all_hosts
    
    elif all({is_valid_ip_address(ip) for ip in r_all_hosts}):
        return reverse_dict(r_all_hosts)

def get_all_hosts_from_yaml_list(yaml_list: list) -> dict:
    
    merged_all_hosts = {}
    
    for inv in yaml_list:
        if not (inv.endswith(".yml") or inv.endswith(".yaml")):
            raise TypeError("The YAML file must be a dictionary.")
        
        with open(inv, "r") as stream:
            try:
                f = yaml.safe_load(stream)
            except yaml.YAMLError as exc:
                raise exc
        
        if not isinstance(f, dict):
            raise TypeError("The YAML file must be a dictionary.")

        # Get all the keys in the YAML file
        all_yaml_keys = f.keys()

        # Get all the hosts in the YAML file
        all_hosts = {}
        for host_key in all_yaml_keys:
            host_list = f[host_key]["hosts"]
            all_hosts.update(host_list)
            
        r_all_hosts = dict((v, k) for k, v in all_hosts.items())
        if all({is_valid_ip_address(ip) for ip in all_hosts}):
            merged_all_hosts.update(all_hosts)

        elif all({is_valid_ip_address(ip) for ip in r_all_hosts}):
            merged_all_hosts.update(reverse_dict(r_all_hosts))
            
    return merged_all_hosts

def inv_import(inv: Union[str, dict, list, object]):
    """Retrieve the type of the inventory and Return Inventory for operations."""
    
    # Check if the inventory is a string
    if isinstance(inv, str):
        
        # Check if the inventory is a file
        if inv.endswith(".yml") or inv.endswith(".yaml"):
            return get_all_hosts_from_yaml(inv)
            
            #elif all({check_ssh(ip) for ip in all_hosts}):
            #    pass
                    
        # Check if the inventory is a valid IP address
        elif is_valid_ip_address(inv):
            return inv
    
    # Check if the inventory is a list
    elif isinstance(inv, list):
        is_all_yaml = all([i.endswith(".yml") or i.endswith(".yaml") for i in inv])
        is_all_valid_ip = all([is_valid_ipv4_address(i) or is_valid_ipv6_address(i) for i in inv])
        is_all_list_of_dicts = all([isinstance(i, dict) for i in inv])
        
        # Check if the list is a list of YAML files
        if is_all_yaml:
            return get_all_hosts_from_yaml_list(inv)
            
        # Check if the list is a list of IP addresses
        if is_all_valid_ip:
            return inv
        
        # Check if the list is a list of dictionaries as host: ip or ip: host
        if is_all_list_of_dicts:
            merged_all_hosts = {}
            for d in inv:
                merged_all_hosts.update(d)
                
            r_merged_all_hosts = reverse_dict(merged_all_hosts)
            if all({is_valid_ip_address(ip) for ip in merged_all_hosts}):
                return merged_all_hosts
        
            elif all({is_valid_ip_address(ip) for ip in r_merged_all_hosts}):
                return reverse_dict(r_merged_all_hosts)
            
            else:
                raise TypeError("The dictionary must contain only IP addresses.")
        
    # Check if the inventory is a dictionary as host: ip or ip: host
    elif isinstance(inv, dict):
        r_inv = reverse_dict(inv)
        if all({is_valid_ip_address(ip) for ip in inv}):
            return inv
    
        elif all({is_valid_ip_address(ip) for ip in r_inv}):
            return reverse_dict(r_inv)
        
        else:
            raise TypeError("The dictionary must contain only IP addresses.")
            
    else:
        raise TypeError("The inventory must be a dictionary, a list or a string.")
    
def sync_cmd_exec(
    ip: str,
    cmd: Union[str, List[str]],
    user: Union[str, None] = None,
    password: Union[str, None]=None,
    conn_timeout: Union[int, None]=None,
    exec_timeout: Union[int, None]=None,
    strict=True,
    check_ssh_conn=True,
    vm_name=None,
    log_to_console=True,
    log_to_file=False,
    ):
    """Execute a command synchronously."""
    
    if check_ssh_conn:
         if check_ssh(server_ip=ip, timeout=conn_timeout) is False:
             if strict:
                 raise ConnectionError(f"Cannot connect to {ip}")
             else:
                 print(f"Cannot connect to {ip}, skipping...")
                 return
        
    if isinstance(cmd, str):
        try:
            with paramiko.SSHClient() as client:
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                client.load_system_host_keys()
                client.connect(hostname=ip, username=user, password=password, timeout=conn_timeout)
                print("Executing commands for", ip)
                (stdin, stdout, stderr) = client.exec_command(cmd, timeout=exec_timeout)
                
                if log_to_console:
                    output = stdout.read()
                    print(str(output, 'utf8'))
        except Exception as e:
            print(f"Error executing command on {ip}: {e}")
            if strict:
                raise e
            
    elif isinstance(cmd, list):
        for c in cmd:
            try:
                with paramiko.SSHClient() as client:
                    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                    client.load_system_host_keys()
                    client.connect(hostname=ip, username=user, password=password)
                    print("Executing commands for", ip)
                    (stdin, stdout, stderr) = client.exec_command(c, timeout=exec_timeout)
                    
                    if log_to_console:
                        output = stdout.read()
                        print(str(output, 'utf8'))
            except Exception as e:
                print(f"Error executing command on {ip}: {e}")
                if strict:
                    raise e
    else:
        print(cmd)
        raise TypeError("The command must be a string or a list of strings.")
    
async def async_cmd_exec(
    ip: str,
    cmd: Union[str, List[str]],
    user: Union[str, None]=None,
    password: Union[str, None]=None,
    conn_timeout: Union[int, None]=None,
    exec_timeout: Union[int, None]=None,
    strict=True,
    check_ssh_conn=True,
    vm_name=None,
    log_to_console=True,
    log_to_file=False,
    ):
    """Execute a command asynchronously."""
    
    if check_ssh_conn:
        if check_ssh(server_ip=ip, timeout=conn_timeout) is False:
            if strict:
                raise ConnectionError(f"Cannot connect to {ip}")
            else:
                print(f"Cannot connect to {ip}, skipping...")
                return
            
    if isinstance(cmd, str):
        
        try:
            async with asyncssh.connect(host=ip, username=user, password=password) as client:
                print("Executing commands for", ip)
                result = await client.run(cmd, check=True, timeout=exec_timeout)
                stdout, stderr = result.stdout, result.stderr
                if result.returncode == 0:
                    print(f"Command success for -> {ip} - {vm_name}")
                    if log_to_console:
                        print(stdout)
                        # print(stderr)
                    #with open("success_commands.txt", "a") as success_file:
                        #success_file.write(f"Docker user added -> {ip} - {vm_name}\n")
                else:
                    print(f"Error executing command for {ip} - {vm_name}:")
                    # print("STDOUT:")
                    # print(stdout)
                    # print("STDERR:")
                    # print(stderr)
                    #with open("error_commands.txt", "a") as error_file:
                        #error_file.write(f"Error for {ip} - {vm_name}\n")
        except Exception as e:
            print(f"Exception for {ip}: {e}")
            
            
    if isinstance(cmd, list):
        
        for c in cmd:
            try:
                async with asyncssh.connect(host=ip, username=user, password=password) as client:
                    print("Executing commands for", ip)
                    result = await client.run(c, check=True, timeout=exec_timeout)
                    stdout, stderr = result.stdout, result.stderr
                if result.returncode == 0:
                    print(f"Command success for -> {ip} - {vm_name}")
                    if log_to_console:
                        print(stdout)
                        # print(stderr)
                    #with open("success_commands.txt", "a") as success_file:
                        #success_file.write(f"Docker user added -> {ip} - {vm_name}\n")
                else:
                    print(f"Error executing command for {ip} - {vm_name}:")
                    # print("STDOUT:")
                    # print(stdout)
                    # print("STDERR:")
                    # print(stderr)
                    #with open("error_commands.txt", "a") as error_file:
                        #error_file.write(f"Error for {ip} - {vm_name}\n")

            except Exception as e:
                print(f"Exception for {ip}: {e}")
                
    
def exec_sync_main_pipeline(
    inv: Union[str, dict, list],
    user: str,
    password: str,
    conn_timeout: Union[int, None],
    exec_timeout: Union[int, None],
    cmd_list: Union[str, List[str]],
    strict=True,
    check_ssh_conn=True,
    log_to_console=True,
    log_to_file=False,
    ):
    """Run the commands synchronously."""
    
    if isinstance(inv, dict):  
        for vm_name, ip in inv.items():
            sync_cmd_exec(
                ip,
                cmd_list,
                user,
                password,
                conn_timeout,
                exec_timeout,
                strict,
                check_ssh_conn,
                vm_name,
                log_to_console=True,
                log_to_file=False
                )
                
    elif isinstance(inv, list):
        for ip in inv:
            sync_cmd_exec(
                ip,
                cmd_list,
                user,
                password,
                conn_timeout,
                exec_timeout,
                strict,
                check_ssh_conn,
                log_to_console,
                log_to_file,
                )
                
    elif isinstance(inv, str):
        ip = inv
        sync_cmd_exec(
            ip,
            cmd_list,
            user,
            password,
            conn_timeout,
            exec_timeout,
            strict,
            check_ssh_conn,
            log_to_console=True,
            log_to_file=False
            )
        
    else:
        raise TypeError(f"The inventory must be a dictionary, a list or a string. Found: {type(inv)}")
    
async def exec_async_main_pipeline(
    inv: Union[str, dict, list],
    user: str,
    password: str,
    conn_timeout: Union[int, None],
    exec_timeout: Union[int, None],
    cmd_list: Union[str, List[str]],
    strict=True,
    check_ssh_conn=True,
    log_to_console=True,
    log_to_file=False,
    ):
    """Run the commands synchronously."""
    
    tasks = []
    
    if isinstance(inv, dict):  
        for vm_name, ip in inv.items():
            tasks.append(
                async_cmd_exec(
                    ip,
                    cmd_list,
                    user,
                    password,
                    conn_timeout,
                    exec_timeout,
                    strict,
                    check_ssh_conn,
                    vm_name,
                    log_to_console=True,
                    log_to_file=False
                    )
                )
        await asyncio.gather(*tasks)
                
    elif isinstance(inv, list):
        for ip in inv:
            tasks.append(
                async_cmd_exec(
                    ip,
                    cmd_list,
                    user,
                    password,
                    conn_timeout,
                    exec_timeout,
                    strict,
                    check_ssh_conn,
                    log_to_console=True,
                    log_to_file=False
                    )
                )
            # await async_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn)
        await asyncio.gather(*tasks)
                
    elif isinstance(inv, str):
        ip = inv
        tasks = [async_cmd_exec(
                    ip,
                    cmd_list,
                    user,
                    password,
                    conn_timeout,
                    exec_timeout,
                    strict,
                    check_ssh_conn,
                    log_to_console=True,
                    log_to_file=False
                )
            ]
        await asyncio.gather(*tasks)
        
    else:
        raise TypeError(f"The inventory must be a dictionary, a list or a string. Found: {type(inv)}")
    
    
