from Browser import Browser

from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
import time

proquant_url = "https://app.proquant.com"

class ProQuant:
    def __init__(self,enable_headless_mode = True):
        self.browser = Browser(enable_headless_mode=enable_headless_mode)
        self.loggedIn = False

    def login(self,username, password):
        """

        :param username: string, username of ProQuant account
        :param password: string, password of ProQuant account

        :return: bool if login was successful
        """

        self.browser.driver.get(proquant_url)

        self.browser.wait_for_page_load('Log in')

        self.browser.driver.find_element_by_xpath("//*[text()='Log in']").click()

        username_field = self.browser.driver.find_element_by_xpath("//input[@placeholder='Username or email']")
        username_field.send_keys(username)

        password_field = self.browser.driver.find_element_by_xpath("//input[@placeholder='Password']")
        password_field.send_keys(password)

        password_field.send_keys(Keys.ENTER)

        self.browser.wait_for_page_load('My Strategies')

        errors = ["Error" in self.browser.driver.page_source, "Something went wrong" in self.browser.driver.page_source,
                  "Incorrect username or password" in self.browser.driver.page_source]

        # Alternative to check for successful login
        # self.browser.driver.find_element_by_class_name("main-tab-bar")

        if True in errors:
            return False
        else:
            self.loggedIn = True
            return True

    def __parse_strategy_page(self):
        def iterate_visible_buttons(class_name):
            indicators = []
            for condition in self.browser.driver.find_elements_by_css_selector("[class=\""+class_name+"\"]"):
                condition.click()
                time.sleep(0.4)

                indicatorParams = self.browser.driver.find_element_by_css_selector("[class=\"" + "css-1dbjc4n r-1kihuf0 r-14lw9ot r-1f0042m r-1ik5qf4 r-13qz1uu" + "\"]").text

                indicators.append(condition.text)
                indicators.append(indicatorParams)

                actions = ActionChains(self.browser.driver)
                actions.move_by_offset(50, 50).click().perform()

            return indicators

        def format_rule_params(rule_list):
            rule_params = {}
            for i in range(0, len(rule_list)):
                line = rule_list[i]

                if "PARAMETERS" in line:
                    indicator_name = rule_list[i - 1]
                    indicator_split = line.split('\n')
                    indicator_param_desc = indicator_split[2]

                    rule_params[indicator_name] = {}
                    rule_params[indicator_name]['desc'] = indicator_param_desc

                    indicator_params = indicator_split[3:]
                    for j in range(0, len(indicator_params), 2):
                        param_name = indicator_params[j]
                        param_value = indicator_params[j + 1]
                        rule_params[indicator_name][param_name] = param_value

            return rule_params

        def finalize_rule_format(rule_format, rule_params):
            rules = {}

            rule_type = rule_format[0]
            rules[rule_type] = {}
            rules[rule_type]['desc'] = rule_format[1]
            for i in range(2, len(rule_format), 3):
                rule_name = rule_format[i]
                rule_desc = rule_format[i + 1]

                rules[rule_type][rule_name] = {}
                rules[rule_type][rule_name]['desc'] = rule_desc
                rules[rule_type][rule_name]['params'] = rule_params[rule_name]

            return rules

        def extract_text_from_element(selenium_element):
            return selenium_element.text

        self.browser.wait_for_page_load("CONDITIONS")

        if "Entry/exit rules hidden by owner" in self.browser.driver.page_source:
            return False

        strategy_name = 'TBD'
        strategy_market = 'TBD'
        conditional_desc = self.browser.driver.find_element_by_css_selector("[class=\"css-901oao r-1niwhzg r-80ss5y r-98loyc r-1b43r93 r-16dba41 r-10yl4k\"]").text

        strategy_rules = {'name': strategy_name,'market': strategy_market}
        strategy_rules['conditional_statement'] = conditional_desc

        long_indicator_button = self.browser.driver.find_elements_by_css_selector("[aria-label=\"label.long\"]")
        short_indicator_button = self.browser.driver.find_elements_by_css_selector("[aria-label=\"label.short\"]")

        has_short_rules = len(short_indicator_button) == 1
        has_long_rules = len(short_indicator_button) == 1

        if has_long_rules:
            long_indicator_button = long_indicator_button[0]

            long_desc = list(map(extract_text_from_element, self.browser.driver.find_elements_by_css_selector("[class=\"" + 'css-1dbjc4n r-1f4vckg r-qklmqi r-d9fdf6 r-1sxzll1' + "\"]")[:2]))
            long_rules = iterate_visible_buttons('css-901oao r-1niwhzg r-jwli3a r-98loyc r-ubezar r-b88u0q r-135wba7 r-zl2h9q')
            long_rules = format_rule_params(long_rules)

            long_entry_rules = finalize_rule_format(long_desc[0].split('\n'), long_rules)
            long_exit_rules = finalize_rule_format(long_desc[1].split('\n'), long_rules)
            strategy_rules.update(long_entry_rules)
            strategy_rules.update(long_exit_rules)

        if has_short_rules:
            short_indicator_button = short_indicator_button[0]
            if has_long_rules:
                short_indicator_button.click()
                time.sleep(1)

            short_desc = list(map(extract_text_from_element, self.browser.driver.find_elements_by_css_selector("[class=\"" + 'css-1dbjc4n r-1f4vckg r-qklmqi r-d9fdf6 r-1sxzll1' + "\"]")[-2:]))
            short_rules = iterate_visible_buttons('css-901oao r-1niwhzg r-cqee49 r-98loyc r-ubezar r-b88u0q r-135wba7 r-zl2h9q')
            short_rules = format_rule_params(short_rules)

            short_entry_rules = finalize_rule_format(short_desc[0].split('\n'), short_rules)
            short_exit_rules = finalize_rule_format(short_desc[1].split('\n'), short_rules)
            strategy_rules.update(short_entry_rules)
            strategy_rules.update(short_exit_rules)

        return strategy_rules


    def get_strategy_by_link(self,link):
        """Get strategy info by link
        https://app.proquant.com/shared/strategy/3a0669e4-2c56-4c11-bf4e-50a13efa5979
        """

        self.browser.driver.get(link)

        return self.__parse_strategy_page()


        '''
        def waitForPageLoad(driver,keywordToFind):
            while True:
                if keywordToFind in driver.page_source:
                    break
                    
        allCSS = self.browser.driver.find_elements_by_class_name('css-901oao')
        i=0
        # element.text
        # Long - long button - Start
        # Short - short button
        # Long entry - long entry text
        # +1 - conditional
        # +1 - First Condition
        # +3 - second condition
        # +3 - Long exit to signify conditional end
        # +1 - conditional
        # +1 - First Conditional
        # +3 - blank text signifies end
        
        longConditions = {}
        longEntryIndex = 0
        longExitIndex = 0
        longEndIndex = 0
        longExitFound = True

        for element in allCSS:
            #print(i)
            print(element.text)
            print("=======")

            if element.text == "Long entry":
                longEntryIndex = i
            elif element.text == "Long exit":
                longExitIndex = i
                longExitFound = True

            if longExitFound and element.text == "":
                longEndIndex = i
                longExitFound = False
                print("LONG EXIT INDEX " + str(longExitIndex))
            i+=1

        numOfLongConditions = (longExitIndex-(longEntryIndex+2))/3
        for i in range(longEntryIndex+2, longExitIndex, 3):
            indicatorName = allCSS[i].text
            indicatorDesc = allCSS[i+1].text
            indicatorButton = allCSS[i]

            indicatorButton.click()
            time.sleep(1)

            actions = ActionChains(self.browser.driver)
            actions.move_by_offset(50, 50).click().perform()

        for i in range(longExitIndex+2, longEndIndex, 3):
            indicatorName = allCSS[i].text
            indicatorDesc = allCSS[i + 1].text
            indicatorButton = allCSS[i]

            indicatorButton.click()
            time.sleep(1)

            actions = ActionChains(self.browser.driver)
            actions.move_by_offset(50, 50).click().perform()

        time.sleep(1)
        shortButton.click()

        #print(longConditions)
        #actions = ActionChains(self.browser.driver)
        #actions.move_to_element(like[130]).perform()
        #like[130].click()
        #1 short button
        '''
