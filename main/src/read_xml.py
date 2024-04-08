import xml.etree.ElementTree as ET

class Cxml_reader:
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
    
    def get_model_list(self):

        result = []

        if self.xml_root.attrib.get('name') == self.workingname:
            model_list = [step.find('model').text for step in self.xml_root.findall('./instructions/step')]
            result = model_list[:]
        
        return result  
    
    def get_object_count_list(self):

        result = []

        if self.xml_root.attrib.get('name') == self.workingname:
            object_count_list = [step.find('count').text for step in self.xml_root.findall('./instructions/step')]
            result = object_count_list[:]
        
        return result  
    
    def get_object_parts_list(self):

        result = []

        for step in self.xml_root.findall('.//step'):
            parts = step.find('parts')
            if parts is not None:
                tmp_part_list =[]
                for part in parts.findall('part'):
                    tmp_part_list.append(part.text)
                result.append(tmp_part_list)
        
        return result 
    
    def get_bar_count(self):

        result = []

        barcount_text = self.xml_root.find('./instructions/step/parts/barcount').text

        barcount_list = barcount_text.split(',')

        for count in barcount_list:
            result.append(int(count))


        return result  
        


    
