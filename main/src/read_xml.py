import xml.etree.ElementTree as ET

class xml_reader:
    def __init__(self, path, workingname):
        self.xml_path = path
        self.workingname = workingname
        self.xml_open()

    def xml_open(self):
        file = open(self.xml_path, "r", encoding="utf-8")
        self.xml_string = file.read()
        self.xml_root = ET.fromstring(self.xml_string)

    def get_order_count(self):

        result = 0

        if self.xml_root.attrib.get('name') == self.workingname:
            orders = [step.attrib.get('order') for step in self.xml_root.findall('./instructions/step')]
            result = len(orders)
        
        return result
    
    def get_order_list(self):

        result = []

        if self.xml_root.attrib.get('name') == self.workingname:
            descriptions = [step.find('description').text for step in self.xml_root.findall('./instructions/step')]
            result = descriptions[:]
        
        return result 


    
