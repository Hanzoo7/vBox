#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess

def test_powerstate(vm_name, power):
    try:
        output = subprocess.check_output(['vboxmanage showvminfo "' + vm_name + '" | grep -e "^State:\s*' + power +'.*$"'], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        return False

def set_powerstate(vm_name, power):
    try:
        output=None

        if power=="powered off":
            output = subprocess.check_output(['VBoxManage controlvm "' + vm_name + '" poweroff'], shell=True)
        
        elif power=="running":
            output = subprocess.check_output(['VBoxManage startvm "' + vm_name + '"'], shell=True)
        #else:
        #    return False, output
        
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)
    
def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
            power=dict(type='str', required=True)
        )
    )

    vm_name = module.params['vm_name']
    power = module.params['power']
    
    if test_powerstate(vm_name, power):
        module.exit_json(changed=False, msg=f"Already " + power)
    
    success, output = set_powerstate(vm_name, power)

    if success:
        module.exit_json(changed=True, msg=f"Execute {power}")
    else:
        module.fail_json(msg=f"Failed to execute {power}", stderr=output)

if __name__ == '__main__':
    main()
