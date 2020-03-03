import openscap_api as oscap
from Dispatcher.Syslog import Syslog
from Persistence.Db import Db

syslog = Syslog.getInstance()
db = Db.getInstance()

'''
Return the string corresponding to the oscap result (PASS, FAIL etc.)
'''
def result2str(result):
    if result == oscap.xccdf.XCCDF_RESULT_PASS:
        return "PASS"
    elif result == oscap.xccdf.XCCDF_RESULT_FAIL:
        return "FAIL"
    elif result == oscap.xccdf.XCCDF_RESULT_ERROR:
        return "ERROR"
    elif result == oscap.xccdf.XCCDF_RESULT_UNKNOWN:
        return "UNKNOWN"
    elif result == oscap.xccdf.XCCDF_RESULT_NOT_APPLICABLE:
        return "NOT_APPLICABLE"
    elif result == oscap.xccdf.XCCDF_RESULT_NOT_CHECKED:
        return "NOT_CHECKED"
    elif result == oscap.xccdf.XCCDF_RESULT_NOT_SELECTED:
        return "NOT_SELECTED"
    elif result == oscap.xccdf.XCCDF_RESULT_INFORMATIONAL:
        return "INFORMATIONAL"
    elif result == oscap.xccdf.XCCDF_RESULT_FIXED:
        return "FIXED"

def load_xccdf_session(xccdf_path, profile, cpe = None):
    syslog.log(Syslog.LOG_INFO, "Loading xccdf session {0} ...".format(xccdf_path))
    xccdf_session=oscap.xccdf.session_new(xccdf_path)
    if cpe is not None:
        syslog.log(Syslog.LOG_INFO, "Loading user CPE {0} ...".format(cpe))
        xccdf_session.set_user_cpe(cpe)

    xccdf_session.load()

    syslog.log(Syslog.LOG_INFO, "Using profile {0} ...".format(profile))
    xccdf_session.set_profile_id(profile)

    return xccdf_session

def initial_scan(xccdf_session):
    res = xccdf_session.evaluate()
    if not res == 0:
        syslog.log(Syslog.LOG_WARNING, "Initial scan failed.")
    else:
        cur = db.get_cursor()
        syslog.log(Syslog.LOG_INFO, "Base score for initial scan : {0}".format(xccdf_session.get_base_score()))
        for rs in xccdf_session.get_xccdf_policy().get_results():
            for rr in rs.get_rule_results():
                cur.execute("INSERT INTO rule_results(rule_name, rule_result, trigger, rule_date) \
                VALUES('{0}', '{1}', 0, datetime('now'));"
                            .format(rr.get_idref(), rr.get_result()))
                syslog.log(Syslog.LOG_DEBUG, "Rule {0} evaluated as {1}"
                    .format(rr.get_idref(), result2str(rr.get_result())))

        db.commit()
