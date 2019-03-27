*** Settings ***
Documentation    Suite description
Suite Teardown    Close All Browsers
Resource          ../resource.robot

*** Test Cases ***
Browser Open With Implicit Wait Should Not Override Default
    Open Browser To Start Page And Test Implicit Wait    10
    [Teardown]    Close Browser

Browser Open With Implicit Wait And Test Wating
    Open Browser To Start Page
    ${old_value} =     Set Selenium Implicit Wait    3
    ${start_time} =    Get Current Date    result_format=epoch    exclude_millis=yes
    Run Keyword And Ignore Error  Wait Until Page Contains Element       //not_here    1
    ${end_time} =      Get Current Date    result_format=epoch    exclude_millis=yes
    Should Be True     ${start_time + 3} <= ${end_time}
    [Teardown]    Set Selenium Implicit Wait    ${old_value}


Implicit Wait And New Window
    ${old_value} =     Set Selenium Implicit Wait    3
    Execute Javascript    window.open("about:blank")
    Select Window      NEW
    ${start_time} =    Get Current Date    result_format=epoch    exclude_millis=yes
    Run Keyword And Ignore Error  Wait Until Page Contains Element       //not_here    1
    ${end_time} =      Get Current Date    result_format=epoch    exclude_millis=yes
    Should Be True     ${start_time + 3} <= ${end_time}
    [Teardown]    Set Selenium Implicit Wait    ${old_value}

Implicit Wait And Back To Main Window
    ${old_value} =     Set Selenium Implicit Wait    3
    Execute Javascript    window.open("about:blank")
    Select Window      NEW
    Select Window      MAIN
    ${start_time} =    Get Current Date    result_format=epoch    exclude_millis=yes
    Run Keyword And Ignore Error  Wait Until Page Contains Element       //not_here    1
    ${end_time} =      Get Current Date    result_format=epoch    exclude_millis=yes
    Should Be True     ${start_time + 3} <= ${end_time}
    [Teardown]    Set Selenium Implicit Wait    ${old_value}