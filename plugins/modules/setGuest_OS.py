#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess
import os, sys

def os_present(vm_name):
    try:
        output = subprocess.check_output(['vboxmanage guestproperty get "' + vm_name + '" "/VirtualBox/GuestInfo/OS/Product"'], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e: 
        return False

def mount_iso(vm_name, iso, iso_sata_port):
    try:
        output = subprocess.check_output(['VBoxManage storageattach "' + vm_name + '" --storagectl "SATA Controller" --port ' + str(iso_sata_port) + ' --device 0 --type dvddrive --medium "' + iso + '" '], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)

def configure_unattend(vm_name, iso, user_account, user_fullname, user_password, timezone):
    try:
        output = subprocess.check_output(['VBoxManage unattended install "' + vm_name + '" --iso "' + iso + '" --user="' + user_account + '" --full-user-name="' + user_fullname + '" --password "' + user_password + '" --install-additions --time-zone="' + timezone + '"'], shell=True)
        return True, output
    except subprocess.CalledProcessError as e: 
        return False, str(e)

def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
            iso=dict(type='str', required=True),
            iso_sata_port=dict(type='int', required=True),
            user_account=dict(type='str', required=True),
            user_password=dict(type='str', required=True),
            user_fullname=dict(type='str', required=True),
            timezone=dict(type='str', required=True),
        )
    )

    vm_name = module.params['vm_name']
    iso = module.params['iso']
    iso_sata_port = module.params['iso_sata_port']
    user_account = module.params['user_account']
    user_password = module.params['user_password']
    user_fullname = module.params['user_fullname']
    timezone = module.params['timezone']
    

    if os_present(vm_name):
        module.exit_json(changed=False, msg="Operating system present")
    
    message=""

    success, output = mount_iso(vm_name, iso, iso_sata_port)

    if success:
        message=iso + " mounted. "
        
    else:
        module.fail_json(msg="Failed to mount iso", stderr=output)

    success, output = configure_unattend(vm_name, iso, user_account, user_fullname, user_password, timezone)

    if success:
        message=message + "unattend configured. "
        module.exit_json(changed=True, msg=message)
        
    else:
        module.fail_json(msg="Failed to install guest os", stderr=output)   

if __name__ == '__main__':
    main()
