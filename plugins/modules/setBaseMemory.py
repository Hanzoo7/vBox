#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess

def mem_correct(vm_name, base_memory_MB):
    try:
        output = subprocess.check_output(['vboxmanage showvminfo ' + vm_name + ' | grep -e "^Memory\ssize:\s*' + str(base_memory_MB) + 'MB$"'], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        return False

def modify_mem(vm_name, base_memory_MB):
    try:
        output = subprocess.check_output(['VBoxManage modifyvm ' + vm_name + ' --memory ' + str(base_memory_MB)], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)
    
def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
            base_memory_MB=dict(type='int', required=True)
        )
    )

    vm_name = module.params['vm_name']
    base_memory_MB = module.params['base_memory_MB']

    if mem_correct(vm_name, base_memory_MB):
        module.exit_json(changed=False, msg=f"no change")
    
    success, output = modify_mem(vm_name, base_memory_MB)

    if success:
        module.exit_json(changed=True, msg=f"CPU modified to {str(base_memory_MB)}")
    else:
        module.fail_json(msg=f"Failed to set cpu count '{vm_name}'", stderr=output)

if __name__ == '__main__':
    main()
