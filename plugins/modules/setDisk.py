#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess
import os, sys

def disk_exists(disk_path):
    try:
        if os.path.exists(disk_path):
            return True
        else:
            return False
    except:
        return False, str(sys.exc_info()[1])

def create_disk(disk_path, disk_size):
    try:
        output = subprocess.check_output(['VBoxManage createhd --filename "' + disk_path + '" --size ' + str(disk_size)], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)

def verify_disk_size(disk_path, disk_size):
    try:
        output = subprocess.check_output(['VBoxManage showmediuminfo "' + disk_path + '" | grep -e "^Capacity:\s*' + str(disk_size) + '\sMBytes$"' ], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError as e: 
        return False


def modify_disk_size(disk_path, disk_size):
    try:
        output = subprocess.check_output(['VBoxManage modifymedium disk "' + disk_path + '" --resize ' + str(disk_size)], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            disk_path=dict(type='str', required=True),
            disk_size=dict(type='int', required=True)
        )
    )

    disk_path = module.params['disk_path']
    disk_size = module.params['disk_size']

    if disk_exists(disk_path): 
        if verify_disk_size(disk_path, disk_size):
            module.exit_json(changed=False, msg="Disk already exists in compliant size")
        
        success, output = modify_disk_size(disk_path, disk_size)
        
        if success:
            module.exit_json(changed=True, msg="Disk size modified successfully to '" + str(disk_size) + "MB'")
        else:
            module.fail_json(msg="Failed to modify disk", stderr=output)

    success, output = create_disk(disk_path, disk_size)

    if success:
        module.exit_json(changed=True, msg="Disk created successfully '" + disk_path + "'")
    else:
        module.fail_json(msg="Failed to create disk", stderr=output)

if __name__ == '__main__':
    main()
