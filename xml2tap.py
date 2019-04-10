
import xml.etree.ElementTree as ET
import os

tree = ET.parse(${PATH_TESTPLAN})
#tree = ET.parse('/opt/qa/acceptance/out/demo_testplan.xml')
root = tree.getroot()
fileName = os.path.splitext(os.path.basename(${TESTPLAN_NAME}))
#fileName = os.path.splitext(os.path.basename("demo_testplan.xml"))
print (fileName)


# get each atribute from xml
#
lchild={}
taplist={}


prev_tap = None
# Caught all http requests
for httpSample in root:
    label = httpSample.attrib['lb']
    # Label starts with [TC-] IS a new testcase
    if label.startswith('[TC-'):
        current_tap = label.split(']')[0] + "]"
        test_priority = label.split(']')[1].strip('[')
        current_test = label.split(']')[2].strip('-')
    else:
        current_tap = ''
        current_test = httpSample.attrib['lb']
    lchild = {}
    asserts_list = []
    print ("current_tap -> " + current_tap)
    print ("current_test -> " + current_test)
    # All http request in lchild.test and lchil.priority
    lchild['test'] = current_test
    lchild['priority'] = test_priority
    # If http request has asserts, caught them
    for assertionResult in httpSample:
        assert_child = {}
        for elto in assertionResult:
            # Generate the dic with each line of test
            try:
                assert_child[elto.tag] = elto.text
                #assert_child[elto.tag] = elto.text.replace("'"," ")
            except AttributeError:
                pass
        asserts_list.append(assert_child)
    if asserts_list:
        lchild['asserts'] = asserts_list

    # Add test_list to taplist dictionary, which has the test tag
    if label.startswith('[TC-'):
        prev_tap = current_tap
        test_list=[]
        test_list.append(lchild)
        taplist[current_tap]=test_list
    else:
        test_list.append(lchild)
        taplist[prev_tap]=test_list


for elto in taplist:
    # Create .tap file and write header with number of steps
    target = open(${PATH_OUTPUTDIR} + fileName[0] + elto + ".tap", 'w')
    # target = open("/opt/qa/acceptance/out/" + fileName[0] + elto + ".tap", 'w')
    target.write("Tap version 13\n")
    target.write("1.." + str(len(taplist[elto])) + "\n")
    hasFailed = 0
    cont = 1
    for testArg in taplist[elto]:
        try:
            # Only 1 assert
            if len(testArg['asserts']) == 1:
                if (testArg['asserts'][0]['failure'].lower() == 'true' or testArg['asserts'][0]['error'].lower() == 'true'):
                    target.write("not ok " + str(cont) + " - " + testArg['test'] + ("\n"))
                    target.write("  ---" + ("\n"))
                    target.write("  message: '"  + testArg['asserts'][0]['failureMessage'])
                    target.write(("'\n") + "  priority: '" + testArg['priority'] + ("'\n"))
                    target.write("  ..." + ("\n"))
                    hasFailed=1
                else:
                    target.write("ok " + str(cont) + " - " + testArg['test'] + ("\n"))
            # More than 1 assert
            else:
                for assertArg in testArg['asserts']:
                    if (assertArg['failure'].lower() == 'true' or assertArg['error'].lower() == 'true'):
                        # Writes for the first failed assert
                        if testArg['asserts'][0] == assertArg:
                            target.write("not ok " + str(cont) + " - " + testArg['test'] + ("\n"))
                            target.write("  ---" + ("\n"))
                            target.write("  message: '" + assertArg['failureMessage']+ ("\n"))
                            hasFailed=1
                        # Writes for the last failed assert
                        elif testArg['asserts'][len(testArg['asserts']) - 1] == assertArg:
                            target.write("           - " + assertArg['failureMessage'])
                            target.write(("'\n") +"  priority: '" + testArg['priority'] + ("'\n"))
                            target.write("  ..." + ("\n"))
                        # Writes for the intermediate asserts
                        else:
                            target.write("           - " + assertArg['failureMessage'] + ("\n"))
                    # Writes the priority for the last passed assert but thers have failed before
                    elif (testArg['asserts'][len(testArg['asserts']) - 1] == assertArg) and (hasFailed == 1):
                        target.write(("'\n") + "  priority: '" + testArg['priority'] + ("'\n"))
                        target.write("  ..." + ("\n"))
        # Write ok when a no asserts request
        except:
            target.write("ok " + str(cont) + " - " + testArg['test'] + ("\n"))
        cont += 1
    target.close()
