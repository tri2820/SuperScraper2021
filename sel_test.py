import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

'''
Testing in progress (:

'''





class SeleniumMiddleware:

    def __init__(self):
        options = Options()
        options.headless = False
        options.add_argument("--log-level=3")
        options.add_argument("--disable-logging")
        options.add_argument("--disable-gpu")
        options.add_argument("start-maximized")
        self.chrome_options=options
        self.driver = webdriver.Chrome(executable_path = "../chromedriver.exe", options=options)

    def process_request(self, url):
        self.driver.get(url)
        # All input with attrib -> type button and attrib -> value
        #"//input[@type='button'][@value]"
        #"//input[@type='button'][@value[contains(.,'accept')]]"
        # Any element that has text() that talks about cookie
        #"//*[contains(text(),'Cookie')]"

        translate_value = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
        translate_value_text = "translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
        
        
        def get_clickables(topic_elements, value_list, anti_value_list, any_input=False):
            # ANTI
            all_elements_dups_anti = []
            all_elements_ids_anti = {}
            for topic_element in topic_elements:
                for value in anti_value_list:
                    buttons = []
                    if not any_input:
                        buttons += topic_element.find_elements_by_xpath(".//button[contains({},'{}')]".format(translate_value, value))
                        buttons += topic_element.find_elements_by_xpath(".//input[@value[contains({},'{}')]]".format(translate_value, value))
                    #buttons += topic_element.find_elements_by_xpath(".//script")
                    all_elements_dups_anti += buttons
                # --
            # --
            all_elements_anti = []
            for all_element in all_elements_dups_anti:
                if all_element.id in all_elements_ids_anti:
                    continue
                all_elements_ids_anti[all_element.id] = True
                all_elements_anti.append(all_element)
            # --
            
            # NORMAL
            all_elements_dups = []
            all_elements_ids = {}
            for topic_element in topic_elements:
                for value in value_list:
                    buttons = []
                    if not any_input:
                        buttons += topic_element.find_elements_by_xpath(".//button[contains({},'{}')]".format(translate_value, value))
                        buttons += topic_element.find_elements_by_xpath(".//input[@value[contains({},'{}')]]".format(translate_value, value))
                    elif any_input:
                        buttons += topic_element.find_elements_by_xpath(".//button")
                        buttons += topic_element.find_elements_by_xpath(".//input")
                    all_elements_dups += buttons
                # --
            # --
            all_elements = []
            for all_element in all_elements_dups:
                if all_element.id in all_elements_ids or all_element.id in all_elements_ids_anti:
                    continue
                all_elements_ids[all_element.id] = True
                all_elements.append(all_element)
            # --

            #[print(x.get_attribute("innerHTML")) for x in all_elements]
            return all_elements
        # --
        
        #if topic_exists and not els_exist:
        def parent_clickables(topic_elements, depth=1):
            parent = None
            print('-'*depth)
            if depth <= 0:
                return []
            # --
            all_els = []
            for topic_element in topic_elements:
                parent = topic_element.find_element_by_xpath("./parent::*[last()]")
                parent_clickable_els = get_clickables([parent], value_list, anti_value_list, True)
                all_els += parent_clickable_els
                if len(parent_clickable_els) > 0:
                    return parent_clickable_els
            if len(all_els) > 0:
                return all_els
            if parent:
                return parent_clickables([parent], depth - 1)
        # --

        topic_value = "cookie"
        value_list = [
            'accept',
            'agree',
            'continue',
            'confirm',
        ]

        anti_value_list = [
            'dont',
            'disagree',
            'refuse',
        ]

        topic_value = "adviser"
        value_list = [
            'accept',
            'agree',
            'continue',
            'financial intermediary',
            'adviser'
        ]

        anti_value_list = [
            'dont',
            'disagree',
            'refuse',
        ]

        time.sleep(2)

        topic_elements = self.driver.find_elements_by_xpath("//*[contains({},'{}')]".format(translate_value_text, topic_value))

        all_els = get_clickables(topic_elements, value_list, anti_value_list)

        [print(x.get_attribute("value")) for x in all_els]
        [print(x.get_attribute("innerHTML")) for x in all_els]
        [print(x.get_attribute("text")) for x in all_els]

        topic_exists = len(topic_elements) != 0
        if topic_exists:
            print(topic_value)
        # --

        

        els_exist = len(all_els) != 0

        clickable_els = []
        search_depth = 1

        if topic_exists and not els_exist:
            while len(clickable_els) <= 0 and search_depth <= 8:
                print("AGAIN")
                clickable_els = parent_clickables(topic_elements, search_depth)
                search_depth += 1
        # --

        [print(x.get_attribute("value")) for x in clickable_els]
        [print(x.get_attribute("innerHTML")) for x in clickable_els]
        [print(x.get_attribute("text")) for x in clickable_els]


        topic_value = "cookie"
        value_list = [
            'accept',
            'agree',
            'continue',
            'confirm',
        ]

        anti_value_list = [
            'dont',
            'disagree',
            'refuse',
        ]



        topic_elements = self.driver.find_elements_by_xpath("//*[contains({},'{}')]".format(translate_value_text, topic_value))

        all_els = get_clickables(topic_elements, value_list, anti_value_list)

        [print(x.get_attribute("innerHTML")) for x in all_els]

        topic_exists = len(topic_elements) != 0
        if topic_exists:
            print(topic_value)
        # --

        

        els_exist = len(all_els) != 0

        clickable_els = []
        search_depth = 1

        if topic_exists and not els_exist:
            while len(clickable_els) <= 0 and search_depth <= 8:
                print("AGAIN")
                clickable_els = parent_clickables(topic_elements, search_depth)
                search_depth += 1
        # --

        [print(x.get_attribute("value")) for x in clickable_els]
        [print(x.get_attribute("innerHTML")) for x in clickable_els]
        [print(x.get_attribute("text")) for x in clickable_els]

        return




url_string = "https://www.schroders.com/en/au/advisers/"
url_string = "https://www.schroders.com/en/au/advisers/"
url_string = "https://www.macquarieim.com/"
url_string = "https://plato.com.au/"
#url_string = "https://www.pimco.com.au/en-au/"




new_sel = SeleniumMiddleware()


new_sel.process_request(url_string)



















# --