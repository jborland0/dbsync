import copy
import re


def merge(config0, config1):
    # make copy of config1 so we can modify it
    config1_copy = copy.deepcopy(config1)

    # remove "hosts" entry from config1
    config1_hosts = config1_copy.pop('hosts', [])

    # merge remaining config1 into config0
    config = {**config0, **config1_copy}

    # for each host in config1
    unfound_hosts = []
    for config1_host in config1_hosts:
        host_found = False
        # for each host in config0
        for config0_host in config['hosts']:
            if config1_host['id'] == config0_host['id']:
                # update config0 with config1 entries
                config0_host.update(config1_host)
                host_found = True
                break

        # if we did not find a matching host
        if not host_found:
            # add to the list of unfound hosts
            unfound_hosts.append(config0_host)

    # add all the unfound hosts to the new config
    for unfound_host in unfound_hosts:
        config['hosts'].append(unfound_host)
    return config


def unformat(string, pattern):
    pattern = pattern.replace("{}", "(.+)")
    return re.search(pattern, string).groups()[0]


class Config:
    strings = None
