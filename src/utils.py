import openscap_api as oscap


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
