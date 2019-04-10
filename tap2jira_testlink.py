# Prerequisites
# sudo apt-get install -y python-dev libmysqlclient-dev
# sudo apt-get install -y python3-dev
# pip3 install mysqlclient
# pip3 install jira
# pip3 install argparse

import argparse
from os import listdir
from jira.client import JIRA
import MySQLdb
import os



def parse_arguments():
    """
    Parses commandline arguments
    :return: Parsed arguments
    """
    parser = argparse.ArgumentParser('Parameters to connect testlink and jira')
    parser.add_argument('--url_jira', '-uj', required=True, help='Jira URL')
    parser.add_argument('--user_jira', '-sj', required=True, help='User to connect to jira')
    parser.add_argument('--pass_jira', '-pj', required=True, help='Password to connect to jira')
    parser.add_argument('--url_testlink_db', '-ut', required=True, help='Testlink URL')
    parser.add_argument('--user_testlink_db', '-st', required=True, help='Testlink URL')
    parser.add_argument('--pass_testlink', '-pt', required=True, help='Password to connect to testlink')
    parser.add_argument('--db_testlink', '-dt', required=True, help='DB name of testlink')
    args = parser.parse_args()
    return args


def main():
    """
    Runner
    """
    args = parse_arguments()

    # Connect to Jira Server
    options = {'server': args.url_jira}
    jira = JIRA(options, basic_auth=(args.user_jira, args.pass_jira))

    # Connect to mysql testlink
    db = MySQLdb.connect(host=args.url_testlink_db, user=args.user_testlink_db, passwd=args.pass_testlink, db=args.db_testlink)
    cursor = db.cursor()

    taplist = []
    # Get all tap filenames
    for name in listdir(${PATH_OUTPUTDIR}):
    #for name in listdir("/opt/qa/acceptance/out/"):
        if ".tap" in name:
            taplist.append(name)

    # Read each tap file to localize a error test
    for tapname in taplist:
        tapfile = open(${PATH_OUTPUTDIR} + str(tapname), 'r').read()
        #tapfile = open("/opt/qa/acceptance/out/" + str(tapname), 'r').read()
        if tapfile.find('not ok') != -1:
            lineas = tapfile.splitlines()
            # Get error message to put in jira bug summary
            for x in lineas:
                if "message: 'Test failed:" in x:
                    errorLinea = x.replace("message: 'Test failed:", "")
                elif "message:" in x:
                    errorLinea = x[10:150]
                elif "priority:" in x:
                    prioridad = x.replace("priority: ", "")
                    if "Low" in prioridad:
                        prioridad = "Minor"
                    elif "Medium" in prioridad:
                        prioridad = "Major"
                    elif "High" in prioridad:
                        prioridad = "Blocker"
                    break
            fileName = os.path.splitext(os.path.basename(tapname))

            # Create new bug in jira with the error description
            new_issue = jira.create_issue(project='QAD', summary=fileName[0] + " - " + errorLinea, description=tapfile,
                                          issuetype={'name': 'Bug'}, priority={'name':prioridad})

            # Get last execution of tapfile
            cursor.execute(
                "select MAX(executions.id) from executions INNER JOIN cfield_design_values ON executions.tcversion_id = cfield_design_values.node_id WHERE executions.tcversion_id = (SELECT node_id FROM cfield_design_values WHERE cfield_design_values.value = '" +
                fileName[0] + "');")
            executionId = cursor.fetchone()
            # Related testcase last execution with the jira bug recently created
            cursor.execute("insert into execution_bugs (execution_id, bug_id) VALUES (" + str(
                executionId[0]) + ", '" + new_issue.key + "')");

    db.commit()

    cursor.close()
    db.close()


if __name__ == '__main__':
    main()
