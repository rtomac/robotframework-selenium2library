*** Settings ***
Resource          table_resource.robot

*** Test Cases ***
Should Find Text In Specific Column
    [Template]    Table Column Should Contain With CSS And XPath Locators
    simpleTable              2    simpleTable_B2
    simpleWithNested         2    nestedTable_A1
    nestedTable              3    nestedTable_C1
    tableWithSingleHeader    1    tableWithSingleHeader_A1
    tableWithSingleHeader    1    tableWithSingleHeader_A3
    tableWithTwoHeaders      2    tableWithTwoHeaders_B2

Should Give Error Message When Content Not Found In Table Column
    Run Keyword And Expect Error
    ...    Table 'id:simpleTable' column 2 did not contain text 'simpleTable_C3'.
    ...    Table Column Should Contain    id:simpleTable    2    simpleTable_C3

Should Give Error Message When Column Number Out Of Bounds
    Run Keyword And Expect Error
    ...    Table '//*[@id="simpleTable"]' column 20 did not contain text 'simpleTable_B3'.
    ...    Table Column Should Contain    //*[@id="simpleTable"]    20    simpleTable_B3

*** Keywords ***
Table Column Should Contain With CSS And XPath Locators
    [Documentation]    Table Column Should Contain With CSS And XPath Locators
    [Arguments]    ${table id}    ${col}    ${expected}
    Run Table Keyword With CSS And XPath Locators
    ...    Table Column Should Contain    ${table id}    ${col}    ${expected}
