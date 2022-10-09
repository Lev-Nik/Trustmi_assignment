import threading
import asyncio
import json
import time
from flask import Flask, request, g as app_ctx
from async_methods.async_api_calls import find_vms_async, return_Data_stats_async
from loader.load_file import json_file_loader

''' gloabal variabales  '''
app = Flask(__name__) # the API
env_data = [] # the data from the json file
vms_cache = {} # dictionary of all the vms and vms that can access them for faster return time
rules = {} # dictionary of all the tags and which tags can access them
num_vms= 0 # total number of vms in the system
requests_num = 0 # total number of requests made
total_time = 0 # total time of all the requests made
lock = threading.Lock() # lock for safe updating


''' setting up all the variables before the request '''
@app.before_request
def set_time():
    global requests_num
    # setting the start time
    app_ctx.start_time = time.perf_counter()
    # locking the counter
    lock.acquire()
    # adding to the request counter
    requests_num += 1
    lock.release()


''' handeling the stats after the request finshes '''
@app.after_request
def time_amount_calculator(responce):
    global total_time
    # locking the time counter
    lock.acquire()
    # adding tpo the time counter
    total_time += time.perf_counter() - app_ctx.start_time
    # loading the responce data
    data = json.loads(responce.get_data())
    # changing the avarge time
    if type(data) == dict:
        data['avarge_request_time'] = total_time/requests_num
        responce.data = json.dumps(data)
    elif type(data) == str:
        responce.status = '500 internal Error'
        responce.status_code = 500
    lock.release()
    return responce


''' stats route '''
@app.route("/api/v1/stats", methods=["GET"])
def get_stats():
    global requests_num
    global total_time
    global num_vms
    # setting up a new event loop 
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    # runnig the stats request asynchronously
    result = loop.run_until_complete(return_Data_stats_async(requests_num, total_time, num_vms))
    return result

''' attack route '''
@app.route("/api/v1/attack", methods=["GET"])
def handl_vm():
    global vms_cache
    #  retreving the vm id from the request args
    vm_id = request.args.get('vm_id')
    # setting up a new event loop 
    asyncio.set_event_loop(asyncio.new_event_loop())
    loop = asyncio.get_event_loop()
    # finsing all the vms that have accsess to the requested vm id asynchronously
    result = loop.run_until_complete(find_vms_async(vm_id, rules, vms_cache, env_data))
    return result

''' the main function setting up the service '''
def main():
    global rules
    global env_data
    global num_vms
    # defining the loader
    env_loader = json_file_loader()
    # retreving the rules dictionary, the enviromemnt data and number of vms
    rules, env_data, num_vms = env_loader.load_cloudenv_data(env_data, num_vms)
    # starting the service
    app.run(host="0.0.0.0", port=80, debug=False)

if __name__ == "__main__":
    main()