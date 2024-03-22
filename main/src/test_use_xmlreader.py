from read_xml import xml_reader 

def main():
    cxml = xml_reader("/home/dyjung/amr_ws/ml/project/src/workingorder.xml")
    print(cxml.get_order_count())
    print(cxml.get_order_list())

if __name__ == "__main__":
    main()