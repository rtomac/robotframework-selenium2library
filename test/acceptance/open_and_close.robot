*** Settings ***
Documentation     Opening and closing browsers
Suite Teardown    Close All Browsers
Resource          resource.robot

*** Test Cases ***
Browser Should Open And Close
    [Documentation]    Opens and closes browser
    Open Browser To Start Page Without Testing Default Options
    Close Browser

Browser Open With Implicit Wait Should Not Override Default
    [Documentation]    Opens browser with implicit wait
    Open Browser To Start Page And Test Implicit Wait    10
    Close Browser

There Should Be A Good Error Message If Browser Is Not Opened
    [Documentation]    Tests error message
    Run Keyword And Expect Error    No browser is open    Title Should Be    foo

Close Browser Does Nothing When No Browser Is Opened
    [Documentation]    Close already closed browser
    Close Browser

Browser Open With Not Well-Formed URL Should Close
    [Documentation]    Verify after incomplete 'Open Browser' browser closes
    ...    LOG 1.1:10 DEBUG STARTS: Opened browser with session id
    ...    LOG 1.1:10 DEBUG REGEXP: .*but failed to open url.*
    ...    LOG 2:2 DEBUG STARTS: DELETE
    ...    LOG 2:3 DEBUG Finished Request
    Run Keyword And Expect Error    *    Open Browser    bad.url.bad    ${BROWSER}
    Close All Browsers

Switch to closed browser is possible
    Open Browser    ${ROOT}/forms/prefilled_email_form.html    ${BROWSER}    Browser 1
    ...    remote_url=${REMOTE_URL}    desired_capabilities=${DESIRED_CAPABILITIES}
    Open Browser    ${ROOT}/forms/prefilled_email_form.html    ${BROWSER}    Browser 2
    ...    remote_url=${REMOTE_URL}    desired_capabilities=${DESIRED_CAPABILITIES}
    Open Browser    ${ROOT}/forms/prefilled_email_form.html    ${BROWSER}    Browser 3
    ...    remote_url=${REMOTE_URL}    desired_capabilities=${DESIRED_CAPABILITIES}
    Switch Browser    Browser 1
    Switch Browser    Browser 2
    Close Browser
    Switch Browser    Browser 3
    Page Should Contain    Name:
    Switch Browser    Browser 2
    ${error} =    Run Keyword And Expect Error
    ...    *
    ...    Page Should Contain    Name:
    # Regexp is required because Linux and Windows raises different errors
    Should Match Regexp    ${error}    error: \\[Errno 111\\] Connection refused|ConnectionRefusedError: \\[WinError 10061\\] No connection could be made because the target machine actively refused it
    Close All Browsers

Closing all browsers clears cache
    Open Browser    ${ROOT}/forms/prefilled_email_form.html    ${BROWSER}    Browser 1
    ...    remote_url=${REMOTE_URL}    desired_capabilities=${DESIRED_CAPABILITIES}
    Open Browser    ${ROOT}/forms/prefilled_email_form.html    ${BROWSER}    Browser 2
    ...    remote_url=${REMOTE_URL}    desired_capabilities=${DESIRED_CAPABILITIES}
    Switch Browser    Browser 1
    Switch Browser    Browser 2
    Close All Browsers
    Run Keyword And Expect Error
    ...    No browser with index or alias 'Browser 1' found.
    ...    Switch Browser    Browser 1
    Run Keyword And Expect Error
    ...    No browser with index or alias 'Browser 2' found.
    ...    Switch Browser    Browser 2
