import openscap_api as oscap
from pprint import pprint
import sys

def fetch_benchmark_profile(benchmark_path, profile_name):
    benchmark_comp = oscap.xccdf.init(benchmark_path)
    policy_model = benchmark_comp['policy_model']
    
    benchmark = policy_model.get_benchmark()
    
    profile = None
    for p in benchmark.get_profiles():
        if p.get_id() == profile_name:
            profile = p
    
    if profile is None:
        for p in benchmark.get_profiles():
            sys.stderr.write("- {0}\n".format(p.get_id()))
        raise Exception("profile {0} not exists.\nAvailable profiles: ".format(profile_name))
        
    else:
        print("Profile {0} found.".format(profile_name))
        
    policy = oscap.xccdf.policy_new(policy_model, profile)
    
    '''for s in profile.get_selects():
        pprint(s.get_item())
    '''
    
    for c in benchmark.get_content():
        print(benchmark.introspect_constants(c.get_type()))
    
