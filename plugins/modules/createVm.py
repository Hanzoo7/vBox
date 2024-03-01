#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess

def vm_exists(vm_name):
    try:
        output = subprocess.check_output(['VBoxManage list vms'], shell=True)
        return vm_name in output.decode('utf-8')
    except subprocess.CalledProcessError:
        return False

def create_vm(vm_name, os_type):
    try:
        output = subprocess.check_output(['VBoxManage createvm --name ' + vm_name + ' --ostype ' + os_type + ' --register '], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)
    
def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
            os_type=dict(type='str', required=True)
        )
    )

    vm_name = module.params['vm_name']
    os_type = module.params['os_type']

    
    if vm_exists(vm_name):
        module.exit_json(changed=False, msg=f"VM '{vm_name}' already exists")
    
    success, output = create_vm(vm_name, os_type)

    if success:
        module.exit_json(changed=True, msg=f"VM '{vm_name}' created successfully")
    else:
        module.fail_json(msg=f"Failed to create VM '{vm_name}'", stderr=output)

if __name__ == '__main__':
    main()
