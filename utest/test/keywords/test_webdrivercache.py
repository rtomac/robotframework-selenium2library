import unittest

from mockito import mock, verify

from SeleniumLibrary.keywords import WebDriverCache


class WebDriverCacheTests(unittest.TestCase):

    def test_no_current_message(self):
        cache = WebDriverCache()
        try:
            self.assertRaises(RuntimeError, cache.current.anyMember())
        except RuntimeError as e:
            self.assertEqual(str(e), "No current browser")

    def test_browsers_property(self):
        cache = WebDriverCache()

        driver1 = mock()
        driver2 = mock()
        driver3 = mock()

        index1 = cache.register(driver1)
        index2 = cache.register(driver2)
        index3 = cache.register(driver3)

        self.assertEqual(len(cache.drivers), 3)
        self.assertEqual(cache.drivers[0], driver1)
        self.assertEqual(cache.drivers[1], driver2)
        self.assertEqual(cache.drivers[2], driver3)
        self.assertEqual(index1, 1)
        self.assertEqual(index2, 2)
        self.assertEqual(index3, 3)

    def test_get_open_browsers(self):
        cache = WebDriverCache()

        driver1 = mock()
        driver2 = mock()
        driver3 = mock()

        cache.register(driver1)
        cache.register(driver2)
        cache.register(driver3)

        drivers = cache.active_drivers
        self.assertEqual(len(drivers), 3)
        self.assertEqual(drivers[0], driver1)
        self.assertEqual(drivers[1], driver2)
        self.assertEqual(drivers[2], driver3)

        cache.close()
        drivers = cache.active_drivers
        self.assertEqual(len(drivers), 2)
        self.assertEqual(drivers[0], driver1)
        self.assertEqual(drivers[1], driver2)

    def test_close(self):
        cache = WebDriverCache()
        browser = mock()
        cache.register(browser)

        verify(browser, times=0).quit()  # sanity check
        cache.close()
        verify(browser, times=1).quit()

    def test_close_only_called_once(self):
        cache = WebDriverCache()

        browser1 = mock()
        browser2 = mock()
        browser3 = mock()

        cache.register(browser1)
        cache.register(browser2)
        cache.register(browser3)

        cache.close()
        verify(browser3, times=1).quit()

        cache.close_all()
        verify(browser1, times=1).quit()
        verify(browser2, times=1).quit()
        verify(browser3, times=1).quit()


    def test_resolve_alias_or_index(self):
        cache = WebDriverCache()

        cache.register(mock(), 'foo')
        cache.register(mock())
        cache.register(mock())

        index = cache.get_index('foo')
        self.assertEqual(index, 1)

        index = cache.get_index(1)
        self.assertEqual(index, 1)

        index = cache.get_index(3)
        self.assertEqual(index, 3)

        index = cache.get_index(None)
        self.assertEqual(index, None)

        index = cache.get_index('None')
        self.assertEqual(index, None)

    def test_resolve_alias_or_index_with_none(self):
        cache = WebDriverCache()

        cache.register(mock(), 'foo')
        cache.register(mock(), 'None')

        index = cache.get_index('foo')
        self.assertEqual(index, 1)

        index = cache.get_index(1)
        self.assertEqual(index, 1)

        index = cache.get_index(None)
        self.assertEqual(index, None)

        index = cache.get_index('None')
        self.assertEqual(index, None)

        index = cache.get_index('NoNe')
        self.assertEqual(index, None)

    def test_resolve_alias_or_index_error(self):
        cache = WebDriverCache()

        cache.register(mock(), 'foo')
        cache.register(mock())

        index = cache.get_index('bar')
        self.assertEqual(index, None)

        index = cache.get_index(12)
        self.assertEqual(index, None)

        index = cache.get_index(-1)
        self.assertEqual(index, None)

    def test_close_and_same_alias(self):
        cache = WebDriverCache()

        cache.register(mock(), 'foo')
        cache.register(mock(), 'bar')
        cache.close()
        index = cache.get_index('bar')
        self.assertEqual(index, None)

    def test_same_alias_new_browser(self):
        cache = WebDriverCache()
        cache.close()
        index = cache.get_index('bar')
        self.assertEqual(index, None)
