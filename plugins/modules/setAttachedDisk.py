#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess
import os, sys

def controller_exists(vm_name):
    try:
        output = subprocess.check_output(['vboxmanage showvminfo "' + vm_name + '" | grep -e "SATA Controller.*Instance:\s0"'], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e: 
        return False


def create_controller(vm_name):
    try:
        output = subprocess.check_output(['VBoxManage storagectl "' + vm_name + '" --name "SATA Controller" --add sata'], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)

def verify_attach(vm_name, disk_path):
    try:
        output = subprocess.check_output(['vboxmanage showmediuminfo "' + disk_path + '" | grep -e "^In\suse\sby\sVMs:\s*' + vm_name + '"'], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e: 
        return False

def create_attach(vm_name, disk_path, sata_port):
    try:
        output = subprocess.check_output(['VBoxManage storageattach "' + vm_name + '" --storagectl "SATA Controller" --port ' + str(sata_port) + ' --device 0 --type hdd --medium "' + disk_path + '"'], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
            disk_path=dict(type='str', required=True),
            sata_port=dict(type='int', required=True),
        )
    )

    vm_name = module.params['vm_name']
    disk_path = module.params['disk_path']
    sata_port = module.params['sata_port']
    
    message=""

    if not controller_exists(vm_name):
        success, output = create_controller(vm_name)
        
        if not success:
            module.fail_json(msg="Failed to create controller", stderr=output)

        message="Controller created successfully to '" + vm_name + "'. "


    if verify_attach(vm_name, disk_path):
        module.exit_json(changed=False, msg="Controller already exists and Disk are already attached")
    
    success, output = create_attach(vm_name, disk_path, sata_port)

    if success:
        module.exit_json(changed=True, msg=message+"Disk attached successfully to '" + vm_name + "'")
    else:
        module.fail_json(msg="Failed to attach disk", stderr=output)

if __name__ == '__main__':
    main()
