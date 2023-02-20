# Copyright 2008-2011 Nokia Networks
# Copyright 2011-2016 Ryan Tomac, Ed Manlove and contributors
# Copyright 2016-     Robot Framework Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from collections import namedtuple
from typing import List, Optional, Tuple, Union

from SeleniumLibrary.utils import is_noney
from SeleniumLibrary.utils.events.event import _unwrap_eventfiring_element
from robot.utils import plural_or_not, is_truthy
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webelement import WebElement
from selenium.common.exceptions import MoveTargetOutOfBoundsException
from SeleniumLibrary.base import LibraryComponent, keyword
from SeleniumLibrary.errors import ElementNotFound
from SeleniumLibrary.utils.types import type_converter


class ElementKeywords(LibraryComponent):
    @keyword(name="Get WebElement")
    def get_webelement(self, locator: Union[WebElement, str]) -> WebElement:
        """Returns the first WebElement matching the given ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        return self.find_element(locator)

    @keyword(name="Get WebElements")
    def get_webelements(self, locator: Union[WebElement, str]) -> List[WebElement]:
        """Returns a list of WebElement objects matching the ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        Starting from SeleniumLibrary 3.0, the keyword returns an empty
        list if there are no matching elements. In previous releases, the
        keyword failed in this case.
        """
        return self.find_elements(locator)

    @keyword
    def element_should_contain(
        self,
        locator: Union[WebElement, str],
        expected: Union[None, str],
        message: Optional[str] = None,
        ignore_case: bool = False,
    ):
        """Verifies that element ``locator`` contains text ``expected``.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``message`` argument can be used to override the default error
        message.

        The ``ignore_case`` argument can be set to True to compare case
        insensitive, default is False. New in SeleniumLibrary 3.1.

        ``ignore_case`` argument is new in SeleniumLibrary 3.1.

        Use `Element Text Should Be` if you want to match the exact text,
        not a substring.
        """
        actual = actual_before = self.find_element(locator).text
        expected_before = expected
        if ignore_case:
            actual = actual.lower()
            expected = expected.lower()
        if expected not in actual:
            if message is None:
                message = (
                    f"Element '{locator}' should have contained text '{expected_before}' but "
                    f"its text was '{actual_before}'."
                )
            raise AssertionError(message)
        self.info(f"Element '{locator}' contains text '{expected_before}'.")

    @keyword
    def element_should_not_contain(
        self,
        locator: Union[WebElement, str],
        expected: Union[None, str],
        message: Optional[str] = None,
        ignore_case: bool = False,
    ):
        """Verifies that element ``locator`` does not contain text ``expected``.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``message`` argument can be used to override the default error
        message.

        The ``ignore_case`` argument can be set to True to compare case
        insensitive, default is False.

        ``ignore_case`` argument new in SeleniumLibrary 3.1.
        """
        actual = self.find_element(locator).text
        expected_before = expected
        if ignore_case:
            actual = actual.lower()
            expected = expected.lower()
        if expected in actual:
            if message is None:
                message = (
                    f"Element '{locator}' should not contain text '{expected_before}' but "
                    "it did."
                )
            raise AssertionError(message)
        self.info(f"Element '{locator}' does not contain text '{expected_before}'.")

    @keyword
    def page_should_contain(self, text: str, loglevel: str = "TRACE"):
        """Verifies that current page contains ``text``.

        If this keyword fails, it automatically logs the page source
        using the log level specified with the optional ``loglevel``
        argument. Valid log levels are ``DEBUG``, ``INFO`` (default),
        ``WARN``, and ``NONE``. If the log level is ``NONE`` or below
        the current active log level the source will not be logged.
        """
        if not self._page_contains(text):
            self.ctx.log_source(loglevel)
            raise AssertionError(
                f"Page should have contained text '{text}' but did not."
            )
        self.info(f"Current page contains text '{text}'.")

    @keyword
    def page_should_contain_element(
        self,
        locator: Union[WebElement, str],
        message: Optional[str] = None,
        loglevel: str = "TRACE",
        limit: Optional[int] = None,
    ):
        """Verifies that element ``locator`` is found on the current page.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``message`` argument can be used to override the default error
        message.

        The ``limit`` argument can used to define how many elements the
        page should contain. When ``limit`` is ``None`` (default) page can
        contain one or more elements. When limit is a number, page must
        contain same number of elements.

        See `Page Should Contain` for an explanation about the ``loglevel``
        argument.

        Examples assumes that locator matches to two elements.
        | `Page Should Contain Element` | div_name | limit=1    | # Keyword fails.                  |
        | `Page Should Contain Element` | div_name | limit=2    | # Keyword passes.                 |
        | `Page Should Contain Element` | div_name | limit=none | # None is considered one or more. |
        | `Page Should Contain Element` | div_name |            | # Same as above.                  |

        The ``limit`` argument is new in SeleniumLibrary 3.0.
        """
        if limit is None:
            return self.assert_page_contains(
                locator, message=message, loglevel=loglevel
            )
        count = len(self.find_elements(locator))
        if count == limit:
            self.info(f"Current page contains {count} element(s).")
        else:
            if message is None:
                message = (
                    f'Page should have contained "{limit}" element(s), '
                    f'but it did contain "{count}" element(s).'
                )
            self.ctx.log_source(loglevel)
            raise AssertionError(message)

    @keyword
    def page_should_not_contain(self, text: str, loglevel: str = "TRACE"):
        """Verifies the current page does not contain ``text``.

        See `Page Should Contain` for an explanation about the ``loglevel``
        argument.
        """
        if self._page_contains(text):
            self.ctx.log_source(loglevel)
            raise AssertionError(f"Page should not have contained text '{text}'.")
        self.info(f"Current page does not contain text '{text}'.")

    @keyword
    def page_should_not_contain_element(
        self,
        locator: Union[WebElement, str],
        message: Optional[str] = None,
        loglevel: str = "TRACE",
    ):
        """Verifies that element ``locator`` is not found on the current page.

        See the `Locating elements` section for details about the locator
        syntax.

        See `Page Should Contain` for an explanation about ``message`` and
        ``loglevel`` arguments.
        """
        self.assert_page_not_contains(locator, message=message, loglevel=loglevel)

    @keyword
    def assign_id_to_element(self, locator: Union[WebElement, str], id: str):
        """Assigns a temporary ``id`` to the element specified by ``locator``.

        This is mainly useful if the locator is complicated and/or slow XPath
        expression and it is needed multiple times. Identifier expires when
        the page is reloaded.

        See the `Locating elements` section for details about the locator
        syntax.

        Example:
        | `Assign ID to Element` | //ul[@class='example' and ./li[contains(., 'Stuff')]] | my id |
        | `Page Should Contain Element` | my id |
        """
        self.info(f"Assigning temporary id '{id}' to element '{locator}'.")
        element = self.find_element(locator)
        self.driver.execute_script(f"arguments[0].id = '{id}';", element)

    @keyword
    def element_should_be_disabled(self, locator: Union[WebElement, str]):
        """Verifies that element identified by ``locator`` is disabled.

        This keyword considers also elements that are read-only to be
        disabled.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        if self.is_element_enabled(locator):
            raise AssertionError(f"Element '{locator}' is enabled.")

    @keyword
    def element_should_be_enabled(self, locator: Union[WebElement, str]):
        """Verifies that element identified by ``locator`` is enabled.

        This keyword considers also elements that are read-only to be
        disabled.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        if not self.is_element_enabled(locator):
            raise AssertionError(f"Element '{locator}' is disabled.")

    @keyword
    def element_should_be_focused(self, locator: Union[WebElement, str]):
        """Verifies that element identified by ``locator`` is focused.

        See the `Locating elements` section for details about the locator
        syntax.

        New in SeleniumLibrary 3.0.
        """
        element = self.find_element(locator)
        focused = self.driver.switch_to.active_element
        # Selenium 3.6.0 with Firefox return dict which contains the selenium WebElement
        if isinstance(focused, dict):
            focused = focused["value"]
        if element != focused:
            raise AssertionError(f"Element '{locator}' does not have focus.")

    @keyword
    def element_should_be_visible(
        self, locator: Union[WebElement, str], message: Optional[str] = None
    ):
        """Verifies that the element identified by ``locator`` is visible.

        Herein, visible means that the element is logically visible, not
        optically visible in the current browser viewport. For example,
        an element that carries ``display:none`` is not logically visible,
        so using this keyword on that element would fail.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``message`` argument can be used to override the default error
        message.
        """
        if not self.find_element(locator).is_displayed():
            if message is None:
                message = f"The element '{locator}' should be visible, but it is not."
            raise AssertionError(message)
        self.info(f"Element '{locator}' is displayed.")

    @keyword
    def element_should_not_be_visible(
        self, locator: Union[WebElement, str], message: Optional[str] = None
    ):
        """Verifies that the element identified by ``locator`` is NOT visible.

        Passes if the element does not exists. See `Element Should Be Visible`
        for more information about visibility and supported arguments.
        """
        element = self.find_element(locator, required=False)
        if element is None:
            self.info(f"Element '{locator}' did not exist.")
        elif not element.is_displayed():
            self.info(f"Element '{locator}' exists but is not displayed.")
        else:
            if message is None:
                message = f"The element '{locator}' should not be visible, but it is."
            raise AssertionError(message)

    @keyword
    def element_text_should_be(
        self,
        locator: Union[WebElement, str],
        expected: Union[None, str],
        message: Optional[str] = None,
        ignore_case: bool = False,
    ):
        """Verifies that element ``locator`` contains exact the text ``expected``.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``message`` argument can be used to override the default error
        message.

        The ``ignore_case`` argument can be set to True to compare case
        insensitive, default is False.

        ``ignore_case`` argument is new in SeleniumLibrary 3.1.

        Use `Element Should Contain` if a substring match is desired.
        """
        self.info(f"Verifying element '{locator}' contains exact text '{expected}'.")
        text = before_text = self.find_element(locator).text
        if ignore_case:
            text = text.lower()
            expected = expected.lower()
        if text != expected:
            if message is None:
                message = (
                    f"The text of element '{locator}' should have been '{expected}' "
                    f"but it was '{before_text}'."
                )
            raise AssertionError(message)

    @keyword
    def element_text_should_not_be(
        self,
        locator: Union[WebElement, str],
        not_expected: Union[None, str],
        message: Optional[str] = None,
        ignore_case: bool = False,
    ):
        """Verifies that element ``locator`` does not contain exact the text ``not_expected``.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``message`` argument can be used to override the default error
        message.

        The ``ignore_case`` argument can be set to True to compare case
        insensitive, default is False.

        New in SeleniumLibrary 3.1.1
        """
        self.info(
            f"Verifying element '{locator}' does not contain exact text '{not_expected}'."
        )
        text = self.find_element(locator).text
        before_not_expected = not_expected
        if ignore_case:
            text = text.lower()
            not_expected = not_expected.lower()
        if text == not_expected:
            if message is None:
                message = f"The text of element '{locator}' was not supposed to be '{before_not_expected}'."
            raise AssertionError(message)

    @keyword
    def get_element_attribute(
        self, locator: Union[WebElement, str], attribute: str
    ) -> str:
        """Returns the value of ``attribute`` from the element ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        Example:
        | ${id}= | `Get Element Attribute` | css:h1 | id |

        Passing attribute name as part of the ``locator`` was removed
        in SeleniumLibrary 3.2. The explicit ``attribute`` argument
        should be used instead.
        """
        return self.find_element(locator).get_attribute(attribute)

    @keyword
    def element_attribute_value_should_be(
        self,
        locator: Union[WebElement, str],
        attribute: str,
        expected: Union[None, str],
        message: Optional[str] = None,
    ):
        """Verifies element identified by ``locator`` contains expected attribute value.

        See the `Locating elements` section for details about the locator
        syntax.

        Example:
        `Element Attribute Value Should Be` | css:img | href | value

        New in SeleniumLibrary 3.2.
        """
        current_expected = self.find_element(locator).get_attribute(attribute)
        if current_expected != expected:
            if message is None:
                message = (
                    f"Element '{locator}' attribute should have value '{expected}' "
                    f"({type_converter(expected)}) but its value was '{current_expected}' "
                    f"({type_converter(current_expected)})."
                )
            raise AssertionError(message)
        self.info(
            f"Element '{locator}' attribute '{attribute}' contains value '{expected}'."
        )

    @keyword
    def get_horizontal_position(self, locator: Union[WebElement, str]) -> int:
        """Returns the horizontal position of the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        The position is returned in pixels off the left side of the page,
        as an integer.

        See also `Get Vertical Position`.
        """
        return self.find_element(locator).location["x"]

    @keyword
    def get_element_size(self, locator: Union[WebElement, str]) -> Tuple[int, int]:
        """Returns width and height of the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        Both width and height are returned as integers.

        Example:
        | ${width} | ${height} = | `Get Element Size` | css:div#container |
        """
        element = self.find_element(locator)
        return element.size["width"], element.size["height"]

    @keyword
    def cover_element(self, locator: Union[WebElement, str]):
        """Will cover elements identified by ``locator`` with a blue div without breaking page layout.

        See the `Locating elements` section for details about the locator
        syntax.

        New in SeleniumLibrary 3.3.0

        Example:
        |`Cover Element` | css:div#container |
        """
        elements = self.find_elements(locator)
        if not elements:
            raise ElementNotFound(f"No element with locator '{locator}' found.")
        for element in elements:
            script = """
old_element = arguments[0];
let newDiv = document.createElement('div');
newDiv.setAttribute("name", "covered");
newDiv.style.backgroundColor = 'blue';
newDiv.style.zIndex = '999';
newDiv.style.top = old_element.offsetTop + 'px';
newDiv.style.left = old_element.offsetLeft + 'px';
newDiv.style.height = old_element.offsetHeight + 'px';
newDiv.style.width = old_element.offsetWidth + 'px';
old_element.parentNode.insertBefore(newDiv, old_element);
old_element.remove();
newDiv.parentNode.style.overflow = 'hidden';
        """
            self.driver.execute_script(script, element)

    @keyword
    def get_value(self, locator: Union[WebElement, str]) -> str:
        """Returns the value attribute of the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        return self.get_element_attribute(locator, "value")

    @keyword
    def get_text(self, locator: Union[WebElement, str]) -> str:
        """Returns the text value of the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        return self.find_element(locator).text

    @keyword
    def clear_element_text(self, locator: Union[WebElement, str]):
        """Clears the value of the text-input-element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        self.find_element(locator).clear()

    @keyword
    def get_vertical_position(self, locator: Union[WebElement, str]) -> int:
        """Returns the vertical position of the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        The position is returned in pixels off the top of the page,
        as an integer.

        See also `Get Horizontal Position`.
        """
        return self.find_element(locator).location["y"]

    @keyword
    def click_button(
        self, locator: Union[WebElement, str], modifier: Union[bool, str] = False
    ):
        """Clicks the button identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, buttons are
        searched using ``id``, ``name``, and ``value``.

        See the `Click Element` keyword for details about the
        ``modifier`` argument.

        The ``modifier`` argument is new in SeleniumLibrary 3.3
        """
        if not modifier:
            self.info(f"Clicking button '{locator}'.")
            element = self.find_element(locator, tag="input", required=False)
            if not element:
                element = self.find_element(locator, tag="button")
            element.click()
        else:
            self._click_with_modifier(locator, ["button", "input"], modifier)

    @keyword
    def click_image(
        self, locator: Union[WebElement, str], modifier: Union[bool, str] = False
    ):
        """Clicks an image identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, images are searched
        using ``id``, ``name``, ``src`` and ``alt``.

        See the `Click Element` keyword for details about the
        ``modifier`` argument.

        The ``modifier`` argument is new in SeleniumLibrary 3.3
        """
        if not modifier:
            self.info(f"Clicking image '{locator}'.")
            element = self.find_element(locator, tag="image", required=False)
            if not element:
                # A form may have an image as it's submit trigger.
                element = self.find_element(locator, tag="input")
            element.click()
        else:
            self._click_with_modifier(locator, ["image", "input"], modifier)

    @keyword
    def click_link(
        self, locator: Union[WebElement, str], modifier: Union[bool, str] = False
    ):
        """Clicks a link identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, links are searched
        using ``id``, ``name``, ``href`` and the link text.

        See the `Click Element` keyword for details about the
        ``modifier`` argument.

        The ``modifier`` argument is new in SeleniumLibrary 3.3
        """
        if not modifier:
            self.info(f"Clicking link '{locator}'.")
            self.find_element(locator, tag="link").click()
        else:
            self._click_with_modifier(locator, ["link", "link"], modifier)

    @keyword
    def click_element(
        self,
        locator: Union[WebElement, str],
        modifier: Union[bool, str] = False,
        action_chain: bool = False,
    ):
        """Click the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        The ``modifier`` argument can be used to pass
        [https://seleniumhq.github.io/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html#selenium.webdriver.common.keys.Keys|Selenium Keys]
        when clicking the element. The `+` can be used as a separator
        for different Selenium Keys. The `CTRL` is internally translated to
        the `CONTROL` key. The ``modifier`` is space and case insensitive, example
        "alt" and " aLt " are supported formats to
        [https://seleniumhq.github.io/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html#selenium.webdriver.common.keys.Keys.ALT|ALT key]
        . If ``modifier`` does not match to Selenium Keys, keyword fails.

        If ``action_chain`` argument is true, see `Boolean arguments` for more
        details on how to set boolean argument, then keyword uses ActionChain
        based click instead of the <web_element>.click() function. If both
        ``action_chain`` and ``modifier`` are defined, the click will be
        performed using ``modifier`` and ``action_chain`` will be ignored.

        Example:
        | Click Element | id:button |                   | # Would click element without any modifiers.               |
        | Click Element | id:button | CTRL              | # Would click element with CTLR key pressed down.          |
        | Click Element | id:button | CTRL+ALT          | # Would click element with CTLR and ALT keys pressed down. |
        | Click Element | id:button | action_chain=True | # Clicks the button using an Selenium  ActionChains        |

        The ``modifier`` argument is new in SeleniumLibrary 3.2
        The ``action_chain`` argument is new in SeleniumLibrary 4.1
        """
        if is_truthy(modifier):
            self._click_with_modifier(locator, [None, None], modifier)
        elif action_chain:
            self._click_with_action_chain(locator)
        else:
            self.info(f"Clicking element '{locator}'.")
            self.find_element(locator).click()

    def _click_with_action_chain(self, locator: Union[WebElement, str]):
        self.info(f"Clicking '{locator}' using an action chain.")
        action = ActionChains(self.driver)
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action.move_to_element(element)
        action.click()
        action.perform()

    def _click_with_modifier(self, locator, tag, modifier):
        self.info(
            f"Clicking {tag if tag[0] else 'element'} '{locator}' with {modifier}."
        )
        modifier = self.parse_modifier(modifier)
        action = ActionChains(self.driver)
        for item in modifier:
            action.key_down(item)
        element = self.find_element(locator, tag=tag[0], required=False)
        if not element:
            element = self.find_element(locator, tag=tag[1])
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action.click(element)
        for item in modifier:
            action.key_up(item)
        action.perform()

    @keyword
    def click_element_at_coordinates(
        self, locator: Union[WebElement, str], xoffset: int, yoffset: int
    ):
        """Click the element ``locator`` at ``xoffset/yoffset``.

        The Cursor is moved and the center of the element and x/y coordinates are
        calculated from that point.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        self.info(
            f"Clicking element '{locator}' at coordinates x={xoffset}, y={yoffset}."
        )
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.move_to_element(element)
        action.move_by_offset(xoffset, yoffset)
        action.click()
        action.perform()

    @keyword
    def double_click_element(self, locator: Union[WebElement, str]):
        """Double clicks the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        self.info(f"Double clicking element '{locator}'.")
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.double_click(element).perform()

    @keyword
    def set_focus_to_element(self, locator: Union[WebElement, str]):
        """Sets the focus to the element identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        Prior to SeleniumLibrary 3.0 this keyword was named `Focus`.
        """
        element = self.find_element(locator)
        self.driver.execute_script("arguments[0].focus();", element)

    @keyword
    def scroll_element_into_view(self, locator: Union[WebElement, str]):
        """Scrolls the element identified by ``locator`` into view.

        See the `Locating elements` section for details about the locator
        syntax.

        New in SeleniumLibrary 3.2.0
        """
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        try:
            ActionChains(self.driver).move_to_element(element).perform()
        except MoveTargetOutOfBoundsException as e:
            self.debug(f"Move to element with error: {e}.")
            self.driver.execute_script("arguments[0].scrollIntoView(true);", element)

    @keyword
    def drag_and_drop(
        self, locator: Union[WebElement, str], target: Union[WebElement, str]
    ):
        """Drags the element identified by ``locator`` into the ``target`` element.

        The ``locator`` argument is the locator of the dragged element
        and the ``target`` is the locator of the target. See the
        `Locating elements` section for details about the locator syntax.

        Example:
        | `Drag And Drop` | css:div#element | css:div.target |
        """
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        target = self.find_element(target)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        target = _unwrap_eventfiring_element(target)
        action = ActionChains(self.driver)
        action.drag_and_drop(element, target).perform()

    @keyword
    def drag_and_drop_by_offset(
        self, locator: Union[WebElement, str], xoffset: int, yoffset: int
    ):
        """Drags the element identified with ``locator`` by ``xoffset/yoffset``.

        See the `Locating elements` section for details about the locator
        syntax.

        The element will be moved by ``xoffset`` and ``yoffset``, each of which
        is a negative or positive number specifying the offset.

        Example:
        | `Drag And Drop By Offset` | myElem | 50 | -35 | # Move myElem 50px right and 35px down |
        """
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.drag_and_drop_by_offset(element, xoffset, yoffset)
        action.perform()

    @keyword
    def mouse_down(self, locator: Union[WebElement, str]):
        """Simulates pressing the left mouse button on the element ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.

        The element is pressed without releasing the mouse button.

        See also the more specific keywords `Mouse Down On Image` and
        `Mouse Down On Link`.
        """
        self.info(f"Simulating Mouse Down on element '{locator}'.")
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.click_and_hold(element).perform()

    @keyword
    def mouse_out(self, locator: Union[WebElement, str]):
        """Simulates moving the mouse away from the element ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        self.info(f"Simulating Mouse Out on element '{locator}'.")
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        size = element.size
        offsetx = (size["width"] / 2) + 1
        offsety = (size["height"] / 2) + 1
        action = ActionChains(self.driver)
        action.move_to_element(element)
        action.move_by_offset(offsetx, offsety)
        action.perform()

    @keyword
    def mouse_over(self, locator: Union[WebElement, str]):
        """Simulates hovering the mouse over the element ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        self.info(f"Simulating Mouse Over on element '{locator}'.")
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.move_to_element(element).perform()

    @keyword
    def mouse_up(self, locator: Union[WebElement, str]):
        """Simulates releasing the left mouse button on the element ``locator``.

        See the `Locating elements` section for details about the locator
        syntax.
        """
        self.info(f"Simulating Mouse Up on element '{locator}'.")
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        ActionChains(self.driver).release(element).perform()

    @keyword
    def open_context_menu(self, locator: Union[WebElement, str]):
        """Opens the context menu on the element identified by ``locator``."""
        element = self.find_element(locator)
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.context_click(element).perform()

    @keyword
    def simulate_event(self, locator: Union[WebElement, str], event: str):
        """Simulates ``event`` on the element identified by ``locator``.

        This keyword is useful if element has ``OnEvent`` handler that
        needs to be explicitly invoked.

        See the `Locating elements` section for details about the locator
        syntax.

        Prior to SeleniumLibrary 3.0 this keyword was named `Simulate`.
        """
        element = self.find_element(locator)
        script = """
element = arguments[0];
eventName = arguments[1];
if (document.createEventObject) { // IE
    return element.fireEvent('on' + eventName, document.createEventObject());
}
var evt = document.createEvent("HTMLEvents");
evt.initEvent(eventName, true, true);
return !element.dispatchEvent(evt);
        """
        self.driver.execute_script(script, element, event)

    @keyword
    def press_key(self, locator: Union[WebElement, str], key: str):
        """*DEPRECATED in SeleniumLibrary 4.0.* use `Press Keys` instead."""
        if key.startswith("\\") and len(key) > 1:
            key = self._map_ascii_key_code_to_key(int(key[1:]))
        element = self.find_element(locator)
        element.send_keys(key)

    @keyword
    def press_keys(self, locator: Union[WebElement, None, str] = None, *keys: str):
        """Simulates the user pressing key(s) to an element or on the active browser.

        If ``locator`` evaluates as false, see `Boolean arguments` for more
        details, then the ``keys`` are sent to the currently active browser.
        Otherwise element is searched and ``keys`` are send to the element
        identified by the ``locator``. In later case, keyword fails if element
        is not found. See the `Locating elements` section for details about
        the locator syntax.

        ``keys`` arguments can contain one or many strings, but it can not
        be empty. ``keys`` can also be a combination of
        [https://seleniumhq.github.io/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html|Selenium Keys]
        and strings or a single Selenium Key. If Selenium Key is combined
        with strings, Selenium key and strings must be separated by the
        `+` character, like in `CONTROL+c`. Selenium Keys
        are space and case sensitive and Selenium Keys are not parsed
        inside of the string. Example AALTO, would send string `AALTO`
        and `ALT` not parsed inside of the string. But `A+ALT+O` would
        found Selenium ALT key from the ``keys`` argument. It also possible
        to press many Selenium Keys down at the same time, example
        'ALT+ARROW_DOWN`.

        If Selenium Keys are detected in the ``keys`` argument, keyword
        will press the Selenium Key down, send the strings and
         then release the Selenium Key. If keyword needs to send a Selenium
        Key as a string, then each character must be separated with
        `+` character, example `E+N+D`.

        `CTRL` is alias for
        [https://seleniumhq.github.io/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html#selenium.webdriver.common.keys.Keys.CONTROL|Selenium CONTROL]
        and ESC is alias for
        [https://seleniumhq.github.io/selenium/docs/api/py/webdriver/selenium.webdriver.common.keys.html#selenium.webdriver.common.keys.Keys.ESCAPE|Selenium ESCAPE]

        New in SeleniumLibrary 3.3

        Examples:
        | `Press Keys` | text_field | AAAAA          |            | # Sends string "AAAAA" to element.                                                |
        | `Press Keys` | None       | BBBBB          |            | # Sends string "BBBBB" to currently active browser.                               |
        | `Press Keys` | text_field | E+N+D          |            | # Sends string "END" to element.                                                  |
        | `Press Keys` | text_field | XXX            | YY         | # Sends strings "XXX" and "YY" to element.                                        |
        | `Press Keys` | text_field | XXX+YY         |            | # Same as above.                                                                  |
        | `Press Keys` | text_field | ALT+ARROW_DOWN |            | # Pressing "ALT" key down, then pressing ARROW_DOWN and then releasing both keys. |
        | `Press Keys` | text_field | ALT            | ARROW_DOWN | # Pressing "ALT" key and then pressing ARROW_DOWN.                                |
        | `Press Keys` | text_field | CTRL+c         |            | # Pressing CTRL key down, sends string "c" and then releases CTRL key.            |
        | `Press Keys` | button     | RETURN         |            | # Pressing "ENTER" key to element.                                                |
        """
        parsed_keys = self._parse_keys(*keys)
        if not is_noney(locator):
            self.info(f"Sending key(s) {keys} to {locator} element.")
            element = self.find_element(locator)
            # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
            element = _unwrap_eventfiring_element(element)
            ActionChains(self.driver).click(element).perform()
        else:
            self.info(f"Sending key(s) {keys} to page.")
            element = None
        for parsed_key in parsed_keys:
            actions = ActionChains(self.driver)
            for key in parsed_key:
                if key.special:
                    self._press_keys_special_keys(actions, element, parsed_key, key)
                else:
                    self._press_keys_normal_keys(actions, key)
            self._special_key_up(actions, parsed_key)
            actions.perform()

    def _press_keys_normal_keys(self, actions, key):
        self.info(f"Sending key{plural_or_not(key.converted)} {key.converted}")
        actions.send_keys(key.converted)

    def _press_keys_special_keys(self, actions, element, parsed_key, key):
        if len(parsed_key) == 1 and element:
            self.info(f"Pressing special key {key.original} to element.")
            actions.send_keys(key.converted)
        elif len(parsed_key) == 1 and not element:
            self.info(f"Pressing special key {key.original} to browser.")
            actions.send_keys(key.converted)
        else:
            self.info(f"Pressing special key {key.original} down.")
            actions.key_down(key.converted)

    def _special_key_up(self, actions, parsed_key):
        for key in parsed_key:
            if key.special:
                self.info(f"Releasing special key {key.original}.")
                actions.key_up(key.converted)

    @keyword
    def get_all_links(self) -> List[str]:
        """Returns a list containing ids of all links found in current page.

        If a link has no id, an empty string will be in the list instead.
        """
        links = self.find_elements("tag=a")
        return [link.get_attribute("id") for link in links]

    @keyword
    def mouse_down_on_link(self, locator: Union[WebElement, str]):
        """Simulates a mouse down event on a link identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, links are searched
        using ``id``, ``name``, ``href`` and the link text.
        """
        element = self.find_element(locator, tag="link")
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.click_and_hold(element).perform()

    @keyword
    def page_should_contain_link(
        self,
        locator: Union[WebElement, str],
        message: Optional[str] = None,
        loglevel: str = "TRACE",
    ):
        """Verifies link identified by ``locator`` is found from current page.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, links are searched
        using ``id``, ``name``, ``href`` and the link text.

        See `Page Should Contain Element` for an explanation about ``message``
        and ``loglevel`` arguments.
        """
        self.assert_page_contains(locator, "link", message, loglevel)

    @keyword
    def page_should_not_contain_link(
        self,
        locator: Union[WebElement, str],
        message: Optional[str] = None,
        loglevel: str = "TRACE",
    ):
        """Verifies link identified by ``locator`` is not found from current page.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, links are searched
        using ``id``, ``name``, ``href`` and the link text.

        See `Page Should Contain Element` for an explanation about ``message``
        and ``loglevel`` arguments.
        """
        self.assert_page_not_contains(locator, "link", message, loglevel)

    @keyword
    def mouse_down_on_image(self, locator: Union[WebElement, str]):
        """Simulates a mouse down event on an image identified by ``locator``.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, images are searched
        using ``id``, ``name``, ``src`` and ``alt``.
        """
        element = self.find_element(locator, tag="image")
        # _unwrap_eventfiring_element can be removed when minimum required Selenium is 4.0 or greater.
        element = _unwrap_eventfiring_element(element)
        action = ActionChains(self.driver)
        action.click_and_hold(element).perform()

    @keyword
    def page_should_contain_image(
        self,
        locator: Union[WebElement, str],
        message: Optional[str] = None,
        loglevel: str = "TRACE",
    ):
        """Verifies image identified by ``locator`` is found from current page.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, images are searched
        using ``id``, ``name``, ``src`` and ``alt``.

        See `Page Should Contain Element` for an explanation about ``message``
        and ``loglevel`` arguments.
        """
        self.assert_page_contains(locator, "image", message, loglevel)

    @keyword
    def page_should_not_contain_image(
        self,
        locator: Union[WebElement, str],
        message: Optional[str] = None,
        loglevel: str = "TRACE",
    ):
        """Verifies image identified by ``locator`` is not found from current page.

        See the `Locating elements` section for details about the locator
        syntax. When using the default locator strategy, images are searched
        using ``id``, ``name``, ``src`` and ``alt``.

        See `Page Should Contain Element` for an explanation about ``message``
        and ``loglevel`` arguments.
        """
        self.assert_page_not_contains(locator, "image", message, loglevel)

    @keyword
    def get_element_count(self, locator: Union[WebElement, str]) -> int:
        """Returns the number of elements matching ``locator``.

        If you wish to assert the number of matching elements, use
        `Page Should Contain Element` with ``limit`` argument. Keyword will
        always return an integer.

        Example:
        | ${count} =       | `Get Element Count` | name:div_name  |
        | `Should Be True` | ${count} > 2        |                |

        New in SeleniumLibrary 3.0.
        """
        return len(self.find_elements(locator))

    @keyword
    def add_location_strategy(
        self, strategy_name: str, strategy_keyword: str, persist: bool = False
    ):
        """Adds a custom location strategy.

        See `Custom locators` for information on how to create and use
        custom strategies. `Remove Location Strategy` can be used to
        remove a registered strategy.

        Location strategies are automatically removed after leaving the
        current scope by default. Setting ``persist`` to a true value (see
        `Boolean arguments`) will cause the location strategy to stay
        registered throughout the life of the test.
        """
        self.element_finder.register(strategy_name, strategy_keyword, persist)

    @keyword
    def remove_location_strategy(self, strategy_name: str):
        """Removes a previously added custom location strategy.

        See `Custom locators` for information on how to create and use
        custom strategies.
        """
        self.element_finder.unregister(strategy_name)

    def _map_ascii_key_code_to_key(self, key_code):
        map = {
            0: Keys.NULL,
            8: Keys.BACK_SPACE,
            9: Keys.TAB,
            10: Keys.RETURN,
            13: Keys.ENTER,
            24: Keys.CANCEL,
            27: Keys.ESCAPE,
            32: Keys.SPACE,
            42: Keys.MULTIPLY,
            43: Keys.ADD,
            44: Keys.SEPARATOR,
            45: Keys.SUBTRACT,
            56: Keys.DECIMAL,
            57: Keys.DIVIDE,
            59: Keys.SEMICOLON,
            61: Keys.EQUALS,
            127: Keys.DELETE,
        }
        key = map.get(key_code)
        if key is None:
            key = chr(key_code)
        return key

    def _map_named_key_code_to_special_key(self, key_name):
        try:
            return getattr(Keys, key_name)
        except AttributeError:
            message = f"Unknown key named '{key_name}'."
            self.debug(message)
            raise ValueError(message)

    def _page_contains(self, text):
        self.driver.switch_to.default_content()

        if self.is_text_present(text):
            return True

        subframes = self.find_elements("xpath://frame|//iframe")
        self.debug(f"Current frame has {len(subframes)} subframes.")
        for frame in subframes:
            self.driver.switch_to.frame(frame)
            found_text = self.is_text_present(text)
            self.driver.switch_to.default_content()
            if found_text:
                return True
        return False

    def parse_modifier(self, modifier):
        modifier = modifier.upper()
        modifiers = modifier.split("+")
        keys = []
        for item in modifiers:
            item = item.strip()
            item = self._parse_aliases(item)
            if hasattr(Keys, item):
                keys.append(getattr(Keys, item))
            else:
                raise ValueError(f"'{item}' modifier does not match to Selenium Keys")
        return keys

    def _parse_keys(self, *keys):
        if not keys:
            raise AssertionError('"keys" argument can not be empty.')
        list_keys = []
        for key in keys:
            separate_keys = self._separate_key(key)
            separate_keys = self._convert_special_keys(separate_keys)
            list_keys.append(separate_keys)
        return list_keys

    def _parse_aliases(self, key):
        if key == "CTRL":
            return "CONTROL"
        if key == "ESC":
            return "ESCAPE"
        return key

    def _separate_key(self, key):
        one_key = ""
        list_keys = []
        for char in key:
            if char == "+" and one_key != "":
                list_keys.append(one_key)
                one_key = ""
            else:
                one_key += char
        if one_key:
            list_keys.append(one_key)
        return list_keys

    def _convert_special_keys(self, keys):
        KeysRecord = namedtuple("KeysRecord", "converted, original special")
        converted_keys = []
        for key in keys:
            key = self._parse_aliases(key)
            if self._selenium_keys_has_attr(key):
                converted_keys.append(KeysRecord(getattr(Keys, key), key, True))
            else:
                converted_keys.append(KeysRecord(key, key, False))
        return converted_keys

    def _selenium_keys_has_attr(self, key):
        return hasattr(Keys, key)
