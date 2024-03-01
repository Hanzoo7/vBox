#!/usr/bin/python 
# -*- coding: utf-8 -*-

from ansible.module_utils.basic import AnsibleModule  
import sys, re
import virtualbox
from subprocess import Popen, PIPE

def main(): 
    #region params and output
    
    module_args = dict( 
        vm_name = dict(required=True, type='str'), 
        verified = dict(required=False, type='bool')
        ) 
    
    module = AnsibleModule(
        argument_spec=module_args,
        supports_check_mode=True
    )   
    vm_name_local = module.params.get('vm_name')
    verified_local=module.params.get('verified')
    
    result = dict(
        changed=False,
        message=vm_name_local + '[BOOTDHCP] : ' + 'missed',
        skipped=False
    )

    if module.check_mode:
        module.exit_json(**result)
    #endregion

    if verified_local:

        #region get
        vbox = virtualbox.VirtualBox()
        bootNetwork=vbox.find_machine(vm_name_local).get_boot_order(1)
        result['changed'] = False
        result['message'] = vm_name_local + '[BOOTDHCP] : ' + str(bootNetwork)
        #endregion

        #region set
        if str(bootNetwork) != 'Network':
            command = 'VBoxManage modifyvm "' + vm_name_local + '" --boot1 net'
            process=  Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()

            if stderr:
                raise Exception(stderr)
        
            result['changed'] = True
            result['message'] = vm_name_local + ' boot DHCP setted'
        #endregion
    
    else:
        result['skipped'] = True

    module.exit_json(**result)

if __name__ == '__main__':
    main()






    

