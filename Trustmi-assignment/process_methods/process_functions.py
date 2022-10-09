''' function to find all the vms that can access the tags
    vm_id: the id of the desired vm to find access points to
    tags: the tags that the vm has
    rules: the rules given to us by the enviroment rules
    vm_list: list of all vm ids that can attack the vm
    all_vms: list of all the vms in the system
 '''
def handle_vm(vm_id, tags, rules, vm_list, all_vms):
    for tag in tags:
        if tag in rules:
            # getting the tags that have access to the destination tag
            source_tags = rules[tag]
            for vm in all_vms:
                # checking if the vm has at least one of the tags
                if any(tag in source_tags for tag in vm['tags']) and vm['vm_id'] != vm_id:
                    vm_list.append(vm['vm_id'])


''' function to process all the rules of the systm
    env_data: json of all the vms and fws
    rules: dictionary of a destination tag and all the tags that can access it
 '''
def process_rules(env_data, rules):
    for fw in env_data:
        # checking if the destination tag exicts
        if fw['dest_tag'] not in rules:
            rules[fw['dest_tag']] = [fw['source_tag']]
        else:
            # checking if the source tag allready exicts in the destination tag
            if fw['source_tag'] not in rules[fw['dest_tag']]:
                # getting the list of tags
                temp = rules[fw['dest_tag']]
                # adding to the list of tags
                temp.append(fw['source_tag'])
                # updating the rules
                rules[fw['dest_tag']] = temp