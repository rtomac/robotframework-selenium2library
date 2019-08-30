*** Settings ***
Documentation    Can be deleted when minimum Selenium version 4.0
Library          SeleniumLibrary     event_firing_webdriver=${CURDIR}/MyListener.py
Resource         resource_event_firing_webdriver.robot
Suite Setup       Open Browser    ${FRONT PAGE}    ${BROWSER}    alias=event_firing_webdriver
...                   remote_url=${REMOTE_URL}    desired_capabilities=${DESIRED_CAPABILITIES}

*** Test Cases ***
Selenium move_to workaround Click Element At Coordinates
    Click Element At Coordinates    id:some_id    4    4

