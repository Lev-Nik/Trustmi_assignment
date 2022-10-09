import json
from loader.loader_abstract import loader
from multiprocessing import Manager, Pool, cpu_count
from process_methods.process_functions import process_rules

''' class for loading json surface data from a file  '''
class json_file_loader(loader):
    ''' function for loading the data
        env_data: dictionary of all the vms and fws
        num_vms: number of vms in the '''
    def load_cloudenv_data(self, env_data, num_vms):
        print('please insert the full path of the json file:')
        #  getting the user input
        input_path = input()
        # opening the json file
        try:
            with open(input_path) as env_file:
                env_data = json.load(env_file)
        except:
            print('file not found please enter a vaild path:')
            input_path = input()
            with open(input_path) as env_file:
                env_data = json.load(env_file)
        print("processing file...")
        # setting the number of vms
        num_vms = len(env_data["vms"])
        # using manager to manage all proceses writngs
        with Manager() as manager:
            # creating a process safe dictionary
            rules = manager.dict()
            # getting the cpu count on the computer
            n_proc = cpu_count()
            # setting the number of processes
            if len(env_data['fw_rules'])/n_proc > 1:
                n = n_proc
            else:
                n = len(env_data['fw_rules'])%n_proc
            # setting a processes pool
            pool = Pool(processes=n)
            # creating a processes to process the env data rules and build dictionary of tag and tags that can access that tag
            for i in range(n): 
                # sending a diffrent part of the firewall list to diffrent processes for faster calculations
                pool.apply_async(process_rules, args=(env_data['fw_rules']
                [i*(len(env_data['fw_rules'])//n): (i + 1)*(len(env_data['fw_rules'])//n)], rules))
            pool.close()
            pool.join()
            return rules._getvalue(), env_data, num_vms