"""SSH Orchestration module."""

import subprocess
import asyncio
import os
from typing import Union, List
import yaml

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
    user: str,
    ip: str,
    cmd: Union[str, List[str]],
    strict=True,
    check_ssh_conn=True,
    vm_name=None
    ):
    """Execute a command synchronously."""
    
    if check_ssh_conn:
        if check_ssh(ip) is False:
            if strict:
                raise ConnectionError(f"Cannot connect to {ip}")
            else:
                print(f"Cannot connect to {ip}, skipping...")
                return
        
    if isinstance(cmd, str):
        try:
            print("Executing commands for", ip)
            subprocess.run(
                f"ssh {user}@{ip} {cmd}",
                check=True,
                shell=True
                )
        except subprocess.CalledProcessError as e:
            print(f"Error executing command: {e}")
            print(f"{ip}")
            if strict:
                raise e
        except Exception as e:
            print(e)
            if strict:
                raise e
            
    elif isinstance(cmd, list):
        for c in cmd:
            try:
                print("Executing commands for", ip)
                subprocess.run(
                    f"ssh {user}@{ip} {c}",
                    check=True,
                    shell=True
                    )
            except subprocess.CalledProcessError as e:
                print(f"Error executing command: {e}")
                print(f"{ip}")
                if strict:
                    raise e
            except Exception as e:
                print(e)
                if strict:
                    raise e
    else:
        raise TypeError("The command must be a string or a list of strings.")
    
async def async_cmd_exec(
    user: str,
    ip: str,
    cmd: Union[str, List[str]],
    strict=True,
    check_ssh_conn=True,
    vm_name=None
    ):
    """Execute a command asynchronously."""
    
    if check_ssh_conn:
        if check_ssh(ip) is False:
            if strict:
                raise ConnectionError(f"Cannot connect to {ip}")
            else:
                print(f"Cannot connect to {ip}, skipping...")
                return
            
    if isinstance(cmd, str):
        
        try:
            print("Executing commands for", ip)
            result = await asyncio.create_subprocess_shell(
                f"ssh {user}@{ip} {cmd}",
                shell=True,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await result.communicate()
            if result.returncode == 0:
                print(f"Command success for -> {ip} - {vm_name}")
                print(stdout.decode())
                print(stderr.decode())
                #with open("success_commands.txt", "a") as success_file:
                    #success_file.write(f"Docker user added -> {ip} - {vm_name}\n")
            else:
                print(f"Error executing command for {ip} - {vm_name}:")
                print("STDOUT:")
                print(stdout.decode())
                print("STDERR:")
                print(stderr.decode())
                #with open("error_commands.txt", "a") as error_file:
                    #error_file.write(f"Error for {ip} - {vm_name}\n")
        except Exception as e:
            print(f"Exception for {ip}: {e}")
            
            
    if isinstance(cmd, list):
        
        for c in cmd:
            try:
                print("Executing commands for", ip)
                result = await asyncio.create_subprocess_shell(
                    f"ssh {user}@{ip} {c}",
                    shell=True,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                stdout, stderr = await result.communicate()
                if result.returncode == 0:
                    print(f"Command success for -> {ip} - {vm_name}")
                    print(stdout.decode())
                    #print(stderr.decode())
                    #with open("success_commands.txt", "a") as success_file:
                        #success_file.write(f"Docker user added -> {ip} - {vm_name}\n")
                else:
                    print(f"Error executing command for {ip} - {vm_name}:")
                    print("STDOUT:")
                    print(stdout.decode())
                    print("STDERR:")
                    print(stderr.decode())
                    #with open("error_commands.txt", "a") as error_file:
                        #error_file.write(f"Error for {ip} - {vm_name}\n")

            except Exception as e:
                print(f"Exception for {ip}: {e}")
                
async def async_gather_executor(
    user: str,
    ip: str,
    cmd: Union[str, List[str]],
    strict=True,
    vm_name=None
):
    tasks = []
    cmd_list = ["command1", "command2", "command3"] 
    ip = "example_ip"
    user = "example_user"
    vm_name = "example_vm_name"
    
    for cmd in cmd_list:
        task = exec_async_main_pipeline(ip, user, cmd, vm_name)
        tasks.append(task)

    await asyncio.gather(*tasks)
        
    
def exec_sync_main_pipeline(
    inv: Union[str, dict, list],
    user: str,
    cmd_list: Union[str, List[str]],
    strict=True,
    check_ssh_conn=True
    ):
    """Run the commands synchronously."""
    
    if isinstance(inv, dict):  
        for vm_name, ip in inv.items():
            sync_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn, vm_name)
                
    elif isinstance(inv, list):
        for ip in inv:
            sync_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn)
                
    elif isinstance(inv, str):
        ip = inv
        sync_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn)
        
    else:
        raise TypeError(f"The inventory must be a dictionary, a list or a string. Found: {type(inv)}")
    
async def exec_async_main_pipeline(
    inv: Union[str, dict, list],
    user: str,
    cmd_list: Union[str, List[str]],
    strict=True,
    check_ssh_conn=True
    ):
    """Run the commands synchronously."""
    
    tasks = []
    
    if isinstance(inv, dict):  
        for vm_name, ip in inv.items():
            tasks.append(async_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn, vm_name))
            # await async_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn, vm_name)
        await asyncio.gather(*tasks)
                
    elif isinstance(inv, list):
        for ip in inv:
            tasks.append(async_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn))
            # await async_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn)
        await asyncio.gather(*tasks)
                
    elif isinstance(inv, str):
        ip = inv
        tasks = [async_cmd_exec(user, ip, cmd_list, strict, check_ssh_conn)]
        await asyncio.gather(*tasks)
        
    else:
        raise TypeError(f"The inventory must be a dictionary, a list or a string. Found: {type(inv)}")
    
    
