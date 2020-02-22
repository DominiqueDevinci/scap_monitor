import openscap_api as oscap
import sys
from Dispatcher.Syslog import Syslog

syslog = Syslog.getInstance()

''' TODO: monitor potential oval variables changes '''

def fetch_benchmark_profile(benchmark_path, profile_name):
    benchmark_comp = oscap.xccdf.init(benchmark_path)


    ''' oval relationships associate a test (or more exactly test objects)
    to its linked definitions ex: {'oval:obj1': ['oval:def:2', 'oval:def:3']}
    '''
    oval_objects_relationships = {}

    '''
    associate object ids to object instances
    we don't use directly objects insance during the parsing because
    the underlying SWIG api doesn't provide unique instance for each id

    so we use id for ensuring unicity during the parsing and then
    relink these id to an equivalent object instance
    '''
    oval_objects = {}

    policy_model = benchmark_comp['policy_model']
    benchmark = policy_model.get_benchmark()

    for model in benchmark_comp['def_models']:
        if model.object == 'oval_definition_model':
            for defin in model.get_definitions():
                fetch_oval_objects_relationships(defin.get_criteria(), oval_objects_relationships, [defin.get_id()])
                oval_objects.update(fetch_oval_objects(model))

    profile = None
    for p in benchmark.get_profiles():
        if p.get_id() == profile_name:
            profile = p

    if profile is None:
        for p in benchmark.get_profiles():
            sys.stderr.write("- {0}\n".format(p.get_id()))
        raise Exception("profile {0} not exists.\nAvailable profiles: ".format(profile_name))

    else:
        syslog.log(Syslog.LOG_DEBUG, "Profile {0} found.".format(profile_name))

    policy = oscap.xccdf.policy_new(policy_model, profile)

    selected_rules=list()
    for r in policy.get_selected_rules():
        selected_rules.append(r.get_item())

    syslog.log(Syslog.LOG_INFO, "{0} rules selected to be monitored ...".format(len(selected_rules)))

    xccdf_def_relationships={}
    for c in benchmark.get_content():
        parse_xccdf_ovdef(c, selected_rules, xccdf_def_relationships)

    objects_rules_relationships = {}
    for obj_id, linked_defs in oval_objects_relationships.items():
        obj = oval_objects.get(obj_id)

        if obj is not None:
            objects_rules_relationships[obj_id]={'instance': obj, 'rules': set([])}
            for defin in linked_defs:
                if defin not in xccdf_def_relationships:
                    syslog.log(Syslog.LOG_DEBUG, "def {0} isn't used by this benchmark profile.".format(defin))
                else:
                    objects_rules_relationships[obj_id]['rules'].update(xccdf_def_relationships[defin])

            if len(objects_rules_relationships[obj_id]['rules']) == 0:
                del objects_rules_relationships[obj_id]
                syslog.log(Syslog.LOG_DEBUG, "obj {0} isn't used by this benchmark profile".format(obj_id))
        else:
            syslog.log(Syslog.LOG_NOTICE, "no instance of object {0} found !".format(obj_id))

    return objects_rules_relationships

''' associate each def to the related rules in order to know which
rule result can change if this result of this single test changes.

Ex: {oval1: [rule_1, rule_2, rule_3]}
It needs to recursively parse items.
'''
def parse_xccdf_ovdef(item, selected_rules, relationships={}):
    if item.get_type() == oscap.xccdf.XCCDF_GROUP:
        for c in item.to_group().get_content():
            parse_xccdf_ovdef(c, selected_rules, relationships)

    elif item.get_type() == oscap.xccdf.XCCDF_RULE:
        rule = item.to_rule()

        ''' TODO: implement multichecks and complex checks '''
        if rule.get_id() in selected_rules:
            syslog.log(Syslog.LOG_DEBUG, "Analysing dependencies of rule {0} ..."
                                           .format(rule.get_id()))

            for check in rule.get_checks():
                for check_ref in check.get_content_refs():
                    ovdef_name=check_ref.get_name()
                    if relationships.get(ovdef_name) is None:
                        relationships[ovdef_name]=set([])
                    relationships[ovdef_name].add(rule.get_id())
        else:
            syslog.log(Syslog.LOG_DEBUG, "Rule {0} skipped because not selected by current profile"
                  .format(rule.get_id()))
    else:
        syslog.log(Syslog.LOG_NOTICE, "Item type {0} is not supported !".format(item.get_type()))


'''
fetch recursively an oval def, first call must pass the root criteria node
and then this function will call itself in order to browse children and complete
the relationships dictionarry given in third argument
'''
def fetch_oval_objects_relationships(crit_node, oval_objects_relationships, tmp_relationships):
    if crit_node.get_type() == oscap.oval.OVAL_NODETYPE_CRITERIA:
        for c in crit_node.get_subnodes():
            fetch_oval_objects_relationships(c, oval_objects_relationships, tmp_relationships)

    elif crit_node.get_type() == oscap.oval.OVAL_NODETYPE_CRITERION:
        obj=crit_node.get_test().get_object()

        if oval_objects_relationships.get(obj.get_id()) is None:
            oval_objects_relationships[obj.get_id()]=set([])

        oval_objects_relationships[obj.get_id()].update(tmp_relationships)

    elif crit_node.get_type() == oscap.oval.OVAL_NODETYPE_EXTENDDEF:  # !!! TODO !!!
        # and extended criterion refer to another oval def, so we can add it
        # in the list of linked defs
        ext_def_id = crit_node.get_definition().get_id()
        tmp_relationships.append(ext_def_id)

        # fetching extended relationship ...
        fetch_oval_objects_relationships(crit_node.get_definition().get_criteria(),
            oval_objects_relationships, tmp_relationships)

        # remove this extended relationship when the recursion on this def ended.
        tmp_relationships.remove(ext_def_id)

    else:
        syslog.log(Syslog.LOG_NOTICE, "Unknown criteria_node_type ({0}) in definition {1}\,"
                         .format(crit_node.get_type(), crit_node.get_definition().get_id()))


def fetch_oval_objects(oval_model):
    objects={}

    for obj in oval_model.get_objects():
        if objects.get(obj.get_id()) is None:
            objects[obj.get_id()]=obj

    return objects
