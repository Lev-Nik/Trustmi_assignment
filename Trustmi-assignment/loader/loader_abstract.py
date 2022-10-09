from abc import ABC, abstractclassmethod

''' an abstract class that defines all data loaders '''
class loader(ABC):
    ''' abstract method for loading thr data
    env_data: dictionary of all the vms and fws
    num_vms: number of vms in the '''
    @abstractclassmethod
    def load_cloudenv_data(self, env_data, num_vms):
        pass