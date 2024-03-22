from read_xml import xml_reader 

def main():

    #xml_reader 클래스를 생성한다. 생성시 불러올 xml 주소를 인자로 넘겨준다
    cxml = xml_reader("/home/dyjung/amr_ws/ml/project/src/workingorder.xml")
    
    #xml안에 들어 있는 작업 순서 갯수 출력 
    print(cxml.get_order_count())
    
    #xml안에 들어 있는 작업순서(string)가 리스트 형태로 출력된다
    print(cxml.get_order_list())

if __name__ == "__main__":
    main()