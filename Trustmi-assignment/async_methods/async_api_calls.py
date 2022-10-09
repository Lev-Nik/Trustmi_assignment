import json
import threading
from multiprocessing import Manager, Pool, cpu_count
from process_methods.process_functions import handle_vm, process_rules

lock = threading.Lock()

''' async function for returning the requests stats.
    requests_num: number of requests
    total_time: the total time of processing all requests
    num_vms: the number of vms in the system
    returns: JSON of the system stats
'''
async def return_Data_stats_async(requests_num, total_time, num_vms):
    res = {
        'vm_count': num_vms,
        'requests_count': requests_num,
        'avarge_request_time': total_time/requests_num
    }
    return json.dumps(res)

''' sync function for finding vms that can attack the requested vm
    vm_id: the requested vm id
    rules: dictionary of the firewall rules
    vms_cache: a dictionary of vm and vms that can attack it
    env_data: json of all the vms and firewalls
    returns: json list of the vms that can attack a requested vm
'''
async def find_vms_async(vm_id, rules, vms_cache, env_data):
    # checking if a vm is allready in the cache
    if vm_id not in vms_cache:
        vm = None
        # finding the requested vm
        for vm_data in env_data['vms']:
            if vm_data['vm_id'] == vm_id:
                vm = vm_data
        # if the vm wasnt found returning an error message
        if vm == None:
            return json.dumps("error! vm not found") 
        #  if the list of tags is empty returning an empty json list
        if len(vm['tags']) == 0:
            vms_cache[vm_id] = []
        else:
            # getting the number of processes in the system
            n_proc = cpu_count()
            with Manager() as manager:
                # creating a process safe list
                total_vms = manager.list()
                tags_length = len(vm['tags'])
                # setting the number of wanted processes
                n = tags_length%n_proc
                if n == 0: n = n_proc 
                # creating a processes pool
                pool = Pool(processes=n)
                for i in range(n):
                    # sending a diffrent part of the tags list to diffrent processes for faster calculation
                    pool.apply_async(handle_vm, args=(vm['vm_id'], vm['tags'][(i*(tags_length//n)):((i + 1)*((tags_length//n)))],
                                                        rules, total_vms, env_data['vms']))
                pool.close()
                pool.join()
                print(total_vms)
                # locking the vm cache to avoid deadlock
                lock.acquire()
                # adding to the cache
                vms_cache[vm_id] = total_vms._getvalue()
                lock.release()
    return json.dumps(vms_cache[vm_id])