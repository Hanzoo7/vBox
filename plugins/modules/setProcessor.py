#!/usr/bin/python
from ansible.module_utils.basic import AnsibleModule
import subprocess

def cpu_correct(vm_name, nb_processors):
    try:
        output = subprocess.check_output(['vboxmanage showvminfo ' + vm_name + ' | grep -e "^Number\sof\sCPUs:\s*' + str(nb_processors) + '"'], shell=True)
        return output.decode('utf-8')
    except subprocess.CalledProcessError:
        return False

def modify_cpu(vm_name, nb_processors):
    try:
        output = subprocess.check_output(['VBoxManage modifyvm ' + vm_name + ' --cpus ' + str(nb_processors)], shell=True)
        return True, output
    except subprocess.CalledProcessError as e:
        return False, str(e)
    
def main():
    module = AnsibleModule(
        argument_spec=dict(
            vm_name=dict(type='str', required=True),
            nb_processors=dict(type='int', required=True)
        )
    )

    vm_name = module.params['vm_name']
    nb_processors = module.params['nb_processors']
    
    if cpu_correct(vm_name, nb_processors):
        module.exit_json(changed=False, msg=f"no change")
    
    success, output = modify_cpu(vm_name, nb_processors)

    if success:
        module.exit_json(changed=True, msg=f"CPU modified to {str(nb_processors)}")
    else:
        module.fail_json(msg=f"Failed to set cpu count '{vm_name}'", stderr=output)

if __name__ == '__main__':
    main()
