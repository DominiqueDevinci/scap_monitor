from RuleParser.RuleBrowser import fetch_benchmark_profile
from pprint import pprint
from Events.FileEvents import FileEvents
from utils import result2str
import openscap_api as oscap
import sys

#TODO factorize and organize by classes ...
oval_session=None
xccdf_session=None
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

def xccdf_rule_callback(event, rules, handler):
    global xccdf_session 
    xccdf_session.load()
    for rule in rules:
        print("re-evaluation required for rule {0}".format(rule))
        xccdf_session.set_rule(rule)
        xccdf_session.evaluate()
        new_rs = xccdf_session.get_rule_result(rule)
        print("rs : {0}".format(result2str(new_rs.get_result())))
        handler(new_rs.get_idref(), new_rs.get_result())
        

def bind_text_file_content_54(objects, handler):
    '''
        TODO: implement the case where the filepath entity have the operator "match"
    '''
    fileEvents = FileEvents()
    
    for obj_id, obj_data in objects.items():
        rules = obj_data['rules'] 
        obj = obj_data['instance']
        if obj.get_subtype() == oscap.oval.OVAL_INDEPENDENT_TEXT_FILE_CONTENT_54:
            for content in obj.get_object_contents():
                if content.get_field_name() == "filepath":
                    fileEvents.add_file_listener(content.get_entity().get_value().get_text(),
                            lambda ev, rules=rules, handler=handler: xccdf_rule_callback(ev, rules, handler))

    fileEvents.start()

def bind_xccdf_profile(xccdf_path, profile, handler, cpe=None):
    global xccdf_session
        
    xccdf_session=oscap.xccdf.session_new(xccdf_path)
    if cpe is not None:
        print("Loading user CPE {0} ...".format(cpe))
        xccdf_session.set_user_cpe(cpe)

    print("Loading xccdf session ...")
    xccdf_session.load()
    xccdf_session.load_oval()
    xccdf_session.load_cpe()

    xccdf_session.set_profile_id(profile)

    objects = fetch_benchmark_profile(xccdf_path, profile)
    bind_text_file_content_54(objects, handler)

