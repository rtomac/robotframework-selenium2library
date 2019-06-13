import inspect
import unittest
import os

from mockito import mock, when, unstub, ANY
from robot.utils import JYTHON
from selenium import webdriver

try:
    from approvaltests.approvals import verify_all
    from approvaltests.reporters.generic_diff_reporter_factory import GenericDiffReporterFactory
except ImportError:
    if JYTHON:
        verify = None
        GenericDiffReporterFactory = None
    else:
        raise

from SeleniumLibrary.keywords.webdrivertools import SeleniumOptions, WebDriverCreator


class SeleniumOptionsParserTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.options = SeleniumOptions()

    def setUp(self):
        path = os.path.dirname(__file__)
        reporter_json = os.path.abspath(os.path.join(path, '..', 'approvals_reporters.json'))
        factory = GenericDiffReporterFactory()
        factory.load(reporter_json)
        self.reporter = factory.get_first_working()
        self.results = []

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_parse_options_string(self):
        self.results.append(self.options._parse('method:arg1'))
        self.results.append(self.options._parse('method:arg1:arg2'))
        self.results.append(self.options._parse('method:arg1,method:arg2'))
        self.results.append(self.options._parse('method'))
        self.results.append(self.options._parse('method1,method2'))
        self.results.append(self.options._parse('method,method'))
        self.results.append(self.options._parse('add_argument:--disable-dev-shm-usage'))
        self.results.append(self.options._parse(r'add_argument:--proxy-server=66.97.38.58\:80'))
        self.results.append(self.options._parse(r'add_argument:--arg_with_\_one_time'))
        self.results.append(self.options._parse(r'add_argument:--arg_with_\\_two_times'))
        verify_all('Selenium options string to dict', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_parse_options_other_types(self):
        self.results.append(self.options._parse('None'))
        self.results.append(self.options._parse(None))
        self.results.append(self.options._parse(False))
        self.results.append(self.options._parse('False'))
        options = [{'add_argument': ['--disable-dev-shm-usage']}]
        self.results.append(self.options._parse(options))
        self.results.append(self.options._parse([]))
        verify_all('Selenium options other types to dict', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_options_escape(self):
        self.results.append(self.options._options_escape(r'--proxy-server=66.97.38.58\:80'.split(':')))
        self.results.append(self.options._options_escape('arg1:arg2'.split(':')))
        self.results.append(self.options._options_escape('arg1'.split(':')))
        verify_all('Selenium options escape string to dict', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_options_create(self):
        options = [{'add_argument': ['--disable-dev-shm-usage']}]
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.arguments)

        options.append({'add_argument': ['--headless']})
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.arguments)

        options.append({'add_argument': ['--proxy-server=66.97.38.58:80']})
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.arguments)

        options.append({'binary_location': ['too', 'many', 'args']})
        try:
            self.options.create('chrome', options)
        except Exception as error:
            self.results.append(error)

        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument('--disable-dev-shm-usage')
        sel_options = self.options.create('chrome', chrome_options)
        self.results.append(sel_options.arguments)

        verify_all('Selenium options', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_options_create_many_args(self):
        options = [{'add_experimental_option': ['profile.default_content_settings.popups', 0]}]
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.experimental_options)

        verify_all('Selenium options', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_options_create_attribute(self):
        options = [{'headless': [True]}]
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.arguments)

        sel_options = self.options.create('headless_chrome', options)
        self.results.append(sel_options.arguments)

        options.append({'binary_location': ['chromedriver']})
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.binary_location)

        options.append({'not_here': ['tidii']})
        try:
            self.options.create('chrome', options)
        except AttributeError as error:
            self.results.append(error)

        verify_all('Selenium options attribute', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_get_options(self):
        options = r'add_argument:--proxy-server=66.97.38.58\:80'
        sel_options = self.options.create('chrome', options)
        self.results.append(sel_options.arguments)

        verify_all('Selenium options with string.', self.results, reporter=self.reporter)

    @unittest.skipIf(JYTHON, 'ApprovalTest does not work with Jython')
    def test_importer(self):
        self.results.append(self.options._import_options('firefox'))
        self.results.append(self.options._import_options('headless_firefox'))
        self.results.append(self.options._import_options('chrome'))
        self.results.append(self.options._import_options('headless_chrome'))
        self.results.append(self.options._import_options('ie'))
        self.results.append(self.options._import_options('opera'))
        self.results.append(self.options._import_options('edge'))
        self.results.append(self.error_formatter(self.options._import_options, 'phantomjs'))
        self.results.append(self.error_formatter(self.options._import_options, 'safari'))
        self.results.append(self.error_formatter(self.options._import_options, 'htmlunit'))
        self.results.append(self.error_formatter(self.options._import_options, 'htmlunit_with_js'))
        self.results.append(self.error_formatter(self.options._import_options, 'android'))
        self.results.append(self.error_formatter(self.options._import_options, 'iphone'))
        verify_all('Selenium options import', self.results, reporter=self.reporter)

    def error_formatter(self, method, arg):
        try:
            method(arg)
        except Exception as error:
            return '%s %s' % (arg, error.__str__()[:15])


class UsingSeleniumOptionsTests(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        cls.output_dir = os.path.abspath(
            os.path.join(curr_dir, '..', '..', 'output_dir'))
        cls.creator = WebDriverCreator(cls.output_dir)

    def tearDown(self):
        unstub()

    def test_create_chrome_with_options(self):
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Chrome(service_log_path=None, options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_chrome({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_chrome_with_options_and_remote_url(self):
        url = 'http://localhost:4444/wd/hub'
        caps = webdriver.DesiredCapabilities.CHROME.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor=url,
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_chrome({}, url, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_headless_chrome_with_options(self):
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Chrome(service_log_path=None, options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_headless_chrome({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_firefox_with_options(self):
        log_file = os.path.join(self.output_dir, 'geckodriver-1.log')
        options = mock()
        profile = mock()
        expected_webdriver = mock()
        when(webdriver).FirefoxProfile().thenReturn(profile)
        when(webdriver).Firefox(options=options, firefox_profile=profile,
                                service_log_path=log_file).thenReturn(expected_webdriver)
        driver = self.creator.create_firefox({}, None, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_firefox_with_options_and_remote_url(self):
        url = 'http://localhost:4444/wd/hub'
        profile = mock()
        when(webdriver).FirefoxProfile().thenReturn(profile)
        caps = webdriver.DesiredCapabilities.FIREFOX.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor=url,
                               desired_capabilities=caps,
                               browser_profile=profile,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_firefox({}, url, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_headless_firefox_with_options(self):
        log_file = os.path.join(self.output_dir, 'geckodriver-1.log')
        options = mock()
        profile = mock()
        expected_webdriver = mock()
        when(webdriver).FirefoxProfile().thenReturn(profile)
        when(webdriver).Firefox(options=options, firefox_profile=profile,
                                service_log_path=log_file).thenReturn(expected_webdriver)
        driver = self.creator.create_headless_firefox({}, None, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_ie_with_options(self):
        options = mock()
        expected_webdriver = mock()
        when(self.creator)._has_service_log_path(ANY).thenReturn(True)
        when(self.creator)._has_options(ANY).thenReturn(True)
        when(webdriver).Ie(service_log_path=None, options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_ie({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_ie_with_options_and_remote_url(self):
        url = 'http://localhost:4444/wd/hub'
        caps = webdriver.DesiredCapabilities.INTERNETEXPLORER.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor=url,
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_ie({}, url, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_ie_with_options_and_log_path(self):
        options = mock()
        expected_webdriver = mock()
        when(self.creator)._has_service_log_path(ANY).thenReturn(False)
        when(self.creator)._has_options(ANY).thenReturn(True)
        when(webdriver).Ie(options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_ie({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_has_options(self):
        self.assertTrue(self.creator._has_options(webdriver.Chrome))
        self.assertTrue(self.creator._has_options(webdriver.Firefox))
        self.assertTrue(self.creator._has_options(webdriver.Ie))
        self.assertFalse(self.creator._has_options(webdriver.Edge))
        self.assertTrue(self.creator._has_options(webdriver.Opera))
        self.assertFalse(self.creator._has_options(webdriver.Safari))

    @unittest.skipIf('options' not in inspect.getargspec(webdriver.Edge.__init__), "Requires Selenium 4.0.")
    def test_create_edge_with_options(self):
        # TODO: This test requires Selenium 4.0 in Travis
        options = mock()
        expected_webdriver = mock()
        when(self.creator)._has_service_log_path(ANY).thenReturn(True)
        when(self.creator)._has_options(ANY).thenReturn(True)
        when(webdriver).Edge(service_log_path=None, options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_edge({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_opera_with_options(self):
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Opera(options=options, service_log_path=None).thenReturn(expected_webdriver)
        driver = self.creator.create_opera({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_opera_with_options_and_remote_url(self):
        url = 'http://localhost:4444/wd/hub'
        caps = webdriver.DesiredCapabilities.OPERA.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor=url,
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_opera({}, url, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_safari_no_options_support(self):
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Safari().thenReturn(expected_webdriver)
        driver = self.creator.create_safari({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_phantomjs_no_options_support(self):
        options = mock()
        expected_webdriver = mock()
        when(webdriver).PhantomJS(service_log_path=None).thenReturn(expected_webdriver)
        driver = self.creator.create_phantomjs({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_htmlunit_no_options_support(self):
        caps = webdriver.DesiredCapabilities.HTMLUNIT.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor='None',
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_htmlunit({'desired_capabilities': caps}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_create_htmlunit_with_js_no_options_support(self):
        caps = webdriver.DesiredCapabilities.HTMLUNITWITHJS.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor='None',
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_htmlunit_with_js({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_android_options_support(self):
        caps = webdriver.DesiredCapabilities.ANDROID.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor='None',
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_android({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)

    def test_iphone_options_support(self):
        caps = webdriver.DesiredCapabilities.IPHONE.copy()
        options = mock()
        expected_webdriver = mock()
        when(webdriver).Remote(command_executor='None',
                               desired_capabilities=caps,
                               browser_profile=None,
                               options=options).thenReturn(expected_webdriver)
        driver = self.creator.create_iphone({}, None, options=options)
        self.assertEqual(driver, expected_webdriver)
