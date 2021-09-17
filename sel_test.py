import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time

from selenium.webdriver.common.action_chains import ActionChains

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
        self.translate_value = "translate(., 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"
        self.translate_value_text = "translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz')"

        self.search_values_list = []

        self.previous_clicked = {}

        self.reclick_q = []

        return

    def goto_url(self, url):
        self.driver.get(url)
        self.last_url = self.driver.current_url
        return
    

    def get_clickables(self, topic_elements, value_list, anti_value_list, any_input=False):
        # ANTI
        all_elements_dups_anti = []
        all_elements_ids_anti = {}
        for topic_element in topic_elements:
            for value in anti_value_list:
                buttons = []
                if not any_input:
                    buttons += topic_element.find_elements_by_xpath(".//button[contains({},'{}')]".format(self.translate_value, value))
                    buttons += topic_element.find_elements_by_xpath(".//input[@value[contains({},'{}')]]".format(self.translate_value, value))
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
                    buttons += topic_element.find_elements_by_xpath(".//button[contains({},'{}')]".format(self.translate_value, value))
                    buttons += topic_element.find_elements_by_xpath(".//input[@value[contains({},'{}')]]".format(self.translate_value, value))
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


    def parent_clickables(self, topic_elements, value_list, anti_value_list, depth=1):
        # If topic_exists and not els_exist:
        parent = None
        print('-'*depth)
        if depth <= 0:
            return []
        # --
        all_els = []
        for topic_element in topic_elements:
            parent = topic_element.find_element_by_xpath("./parent::*[last()]")
            parent_clickable_els = self.get_clickables([parent], value_list, anti_value_list, True)#True
            all_els += parent_clickable_els
            if len(parent_clickable_els) > 0:
                return parent_clickable_els
        if len(all_els) > 0:
            return all_els
        if parent:
            return self.parent_clickables([parent], value_list, anti_value_list, depth - 1)
    # --

    

    def popup_handler(self, url, process_depth=2):
        #self.driver.get(url)

        # All input with attrib -> type button and attrib -> value
        #"//input[@type='button'][@value]"
        #"//input[@type='button'][@value[contains(.,'accept')]]"
        # Any element that has text() that talks about cookie
        #"//*[contains(text(),'Cookie')]"
        
        

        time.sleep(2)


        click_order_all = []


        for search_values in self.search_values_list:

            topic_value = search_values['topic_value']
            value_list = search_values['value_list']
            anti_value_list = search_values['anti_value_list']

            topic_elements = self.driver.find_elements_by_xpath("//*[contains({},'{}')]".format(self.translate_value_text, topic_value))

            all_els = self.get_clickables(topic_elements, value_list, anti_value_list)

            #[print(x.get_attribute("innerHTML")) for x in all_els]

            # If elements with text or other value elements with topic exist
            topic_exists = len(topic_elements) != 0
            if topic_exists:
                print(topic_value)
            # --

            

            els_exist = len(all_els) != 0

            clickable_els = []
            search_depth = 1

            if topic_exists and not els_exist:
                while len(clickable_els) <= 0 and search_depth <= 8:
                    #print("AGAIN")
                    clickable_els = self.parent_clickables(topic_elements, value_list, anti_value_list, search_depth)
                    search_depth += 1
            # --

            '''
            print("\n -- clickable_els -- \n")
            print("--Value--")
            [print(x.get_attribute("value")) for x in clickable_els]
            print("--innerHTML--")
            [print(x.get_attribute("innerHTML")) for x in clickable_els]
            print("--text--")
            [print(x.get_attribute("text")) for x in clickable_els]
            #'''

            click_els = []

            #click_order = []
            #for i in range(len(value_list)):
            #    click_order.append([])

            #for idx, val in enumerate(value_list):
            
            click_order = [[] for x in value_list]

            for clickable_el in clickable_els:
                #print("click ready")
                try:
                    click_volume_el = clickable_el

                    skip_el = False

                    detected_value = None
                    detected_val_idx = 0

                    # Check for antis
                    at_val = click_volume_el.get_attribute("value")
                    at_html = click_volume_el.get_attribute("innerHTML")
                    at_txt = click_volume_el.get_attribute("text")

                    if not at_val:
                        at_val = " "
                    if not at_html:
                        at_html = " "
                    if not at_txt:
                        at_txt = " "

                    for ant_val in anti_value_list:
                        if at_val.find(ant_val) != -1 or at_html.find(ant_val) != -1 or at_txt.find(ant_val) != -1:
                            #print('FOUND anti')
                            #print('v: ', at_val, at_html, at_txt)
                            skip_el = True
                            break
                    if skip_el:
                        continue

                    for idx, pos_val in enumerate(value_list):
                        if at_val.find(pos_val) != -1 or at_html.find(pos_val) != -1 or at_txt.find(pos_val) != -1:
                            detected_value = pos_val
                            detected_val_idx = idx

                    # Check for actually existing location (actiually moveable to)
                    while click_volume_el.location['x'] == 0 and click_volume_el.location['y'] == 0:
                        click_volume_el = click_volume_el.find_element_by_xpath("./parent::*[last()]")
                        # Check for antis
                        at_val = click_volume_el.get_attribute("value")
                        at_html = click_volume_el.get_attribute("innerHTML")
                        at_txt = click_volume_el.get_attribute("text")

                        if not at_val:
                            at_val = " "
                        if not at_html:
                            at_html = " "
                        if not at_txt:
                            at_txt = " "

                        for ant_val in anti_value_list:
                            if at_val.find(ant_val) != -1 or at_html.find(ant_val) != -1 or at_txt.find(ant_val) != -1:
                                #print('FOUND anti')
                                #print('v: ', at_val, at_html, at_txt)
                                skip_el = True
                                break
                        if skip_el:
                            break

                        # If pos
                        for idx, pos_val in enumerate(value_list):
                            if at_val.find(pos_val) != -1 or at_html.find(pos_val) != -1 or at_txt.find(pos_val) != -1:
                                if detected_value == None:
                                    detected_value = pos_val
                                    detected_val_idx = idx
                    # --
                    if skip_el:
                        continue

                    click_order[detected_val_idx].append((click_volume_el, detected_value))

                except:
                    print("element location failure")

            #print(len(clickable_els))

            for idx, val in enumerate(click_order):
                if len(click_order_all) - 1 < idx:
                    click_order_all.append([])
                click_order_all[idx] += val




        [[print(i) for i in x] for x in click_order_all]

        for click_list in click_order_all:
            for click_vals in click_list:
                click_el = click_vals[0]
                try:
                    print(click_vals[1])
                    yeah = click_el.get_attribute("data-drupal-selector") == "edit-submit"
                    if yeah:
                        print("u9289fu94hfhnruigbn93bgubrui9bgui9bngbrbuaeitbnauiebhguibgne9v934uv 923459g 94h9ghgh495hvb9h92h9gh9cthuiwhingirbuiweibipwertbgibeiwbgib\n\n\n\n\n\n\n\n\nu9hwAR9GH9ERH")
                    if click_el.id in self.previous_clicked:
                        print('Previous')
                        continue
                    actions = ActionChains(self.driver)
                    h_x = click_el.size['width']
                    h_y = click_el.size['height']
                    actions.move_to_element_with_offset(click_el, h_x/2, h_y/2)
                    actions.click()
                    actions.perform()
                    time.sleep(0.2)
                    self.previous_clicked[click_el.id] = True
                except:
                    print("click failed")

        time.sleep(1)
        
        self.previous_clicked = {}
        
        #time.sleep(1000)

        # If needs to run again
        if self.last_url == self.driver.current_url and process_depth > 0:
            self.popup_handler(url, process_depth = process_depth - 1)
        else:
            #time.sleep(1000)
            self.goto_url(url)

        return
# --








def test_run():

    url_string_list = [
        "https://www.macquarieim.com/",
        "https://www.4dinfra.com/",
        "https://www.schroders.com/en/au/advisers/",
        "https://www.schroders.com/en/au/advisers/",
        "https://www.macquarieim.com/",
        "https://plato.com.au/",
        "https://www.pimco.com.au/en-au/",
        "https://www.macquarieim.com/",
    ]


    new_sel = SeleniumMiddleware()


    """
    search_values = {
        'topic_value': "cookie",
        'value_list': [
            'accept',
            'agree',
            'continue',
            'confirm',
        ],
        'anti_value_list': [
            'dont',
            'disagree',
            'refuse',
        ]
    }
    """

    new_sel.search_values_list = [
        {
            'topic_value': "cookie",
            'value_list': [
                'agree',
                'accept',
                'continue',
                'confirm',
                'submit',
            ],
            'anti_value_list': [
                'dont',
                'disagree',
                'refuse',
            ]
        },
        {
            'topic_value': "adviser",
            'value_list': [
                'adviser',
                'financial intermediary',
                'agree',
                'accept',
                'continue',
                'confirm',
                'submit',
            ],
            'anti_value_list': [
                'dont',
                'disagree',
                'refuse',
            ]
        },
        {
            'topic_value': "agree",
            'value_list': [
                'agree',
                'accept',
                'continue',
                'confirm',
                'submit',
            ],
            'anti_value_list': [
                'dont',
                'disagree',
                'refuse',
            ]
        },
        {
            'topic_value': "submit",
            'value_list': [
                'agree',
                'accept',
                'continue',
                'confirm',
                'submit',
            ],
            'anti_value_list': [
                'dont',
                'disagree',
                'refuse',
            ]
        },
    ]

    for url_string in url_string_list:
        print(f'\n\n\n -- NEW URL {url_string} -- \n\n\n')
        new_sel.goto_url(url_string)

        new_sel.popup_handler(url_string)
    return
# --


test_run()






# --