from RuleParser.RuleBrowser import fetch_benchmark_profile
from pprint import pprint
from Events.FileEvents import FileEvents
import openscap_api as oscap
import sys



def classify_objects(obj):

    objs = {}
    for obj_id, data in objects.items():
        obj=data['instance']
        obj_type = obj.get_subtype()

        #type_str=oscap.oval.introspect_constants(obj.get_subtype())
        #sys.stderr.write("[warning] object of type {0} isn't supported.\n"
        #             .format(type_str).keys()[0])
        
        if objs.get(obj_type) is None:
            objs[obj_type]=[]
        
        objs[obj_type].append({'instance': obj, 'rules': data['rules']})
    
    return objs

def xccdf_rule_callback(event, rules):
    for rule in rules:
        print("re-evaluation required for rule {0}".format(rule))


def bind_text_file_content_54(objects):

    fileEvents = FileEvents()
    
    for obj_id, obj_data in objects.items():
        rules = obj_data['rules'] 
        obj = obj_data['instance']
        if obj.get_subtype() == oscap.oval.OVAL_INDEPENDENT_TEXT_FILE_CONTENT_54:
            for content in obj.get_object_contents():
                if content.get_field_name() == "filepath":
                    fileEvents.add_file_listener(content.get_entity().get_value().get_text(),
                            lambda ev, rules=rules: xccdf_rule_callback(ev, rules))

    fileEvents.start()

def bind_xccdf_profile(xccdf_path, profile):
    objects = fetch_benchmark_profile(xccdf_path, profile)
    bind_text_file_content_54(objects)

