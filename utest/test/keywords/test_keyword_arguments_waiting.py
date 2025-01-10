import pytest
from mockito import mock, unstub, when

from SeleniumLibrary.keywords import WaitingKeywords

TIMEOUT = 0.01


@pytest.fixture(scope="module")
def waiting():
    ctx = mock()
    ctx.driver = mock()
    ctx.timeout = TIMEOUT
    return WaitingKeywords(ctx)


def teardown_module():
    unstub()


def test_wait_for_condition(waiting):
    condition = 'return document.getElementById("intro")'
    error = "did not become true"
    with pytest.raises(AssertionError) as error:
        waiting.wait_for_condition(condition)
    assert "did not become true" in str(error.value)

    with pytest.raises(AssertionError) as error:
        waiting.wait_for_condition(condition, None, "foobar")
    assert "foobar" in str(error.value)


def test_wait_until_page_contains(waiting):
    text = "text"
    when(waiting).is_text_present(text).thenReturn(None)
    with pytest.raises(AssertionError) as error:
        waiting.wait_until_page_contains(text)
    assert "Text 'text' did not" in str(error.value)

    with pytest.raises(AssertionError) as error:
        waiting.wait_until_page_contains(text, None, "error")
    assert "error" in str(error.value)


def test_wait_until_textarea_contains(waiting):
    locator = "//textarea"
    element = mock()
    when(waiting).find_element(locator, "text area").thenReturn(element)
    when(element).get_attribute("value").thenReturn("no")
    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_contains(locator, "value")
    assert "did not get text" in str(error.value)

    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_contains(locator, "value", None, "foobar error")
    assert "foobar error" in str(error.value)


def test_wait_until_textarea_does_not_contain(waiting):
    locator = "//textarea"
    element = mock()
    when(waiting).find_element(locator, "text area").thenReturn(element)
    when(element).get_attribute("value").thenReturn("value")
    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_does_not_contain(locator, "value")
    assert "still had text" in str(error.value)

    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_does_not_contain(locator, "value", None, "foobar error")
    assert "foobar error" in str(error.value)


def test_wait_until_textarea_value_is(waiting):
    locator = "//textarea"
    element = mock()
    when(waiting).find_element(locator, "text area").thenReturn(element)
    when(element).get_attribute("value").thenReturn("no")
    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_value_is(locator, "value")
    assert "did not get text" in str(error.value)

    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_value_is(locator, "value", None, "foobar error")
    assert "foobar error" in str(error.value)


def test_wait_until_textarea_value_is_not(waiting):
    locator = "//textarea"
    element = mock()
    when(waiting).find_element(locator, "text area").thenReturn(element)
    when(element).get_attribute("value").thenReturn("value")
    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_value_is_not(locator, "value")
    assert "still had text" in str(error.value)

    with pytest.raises(AssertionError) as error:
        waiting.wait_until_textarea_value_is_not(locator, "value", None, "foobar error")
    assert "foobar error" in str(error.value)
