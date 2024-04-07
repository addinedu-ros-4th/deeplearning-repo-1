from read_xml import Cxml_reader 

def main():

    #xml_reader 클래스를 생성한다. 생성시 불러올 xml 주소를 인자로 넘겨준다
    cxml = Cxml_reader("workingorder.xml", "dog_light")
    
    #xml안에 들어 있는 작업 순서 갯수 출력 
    print(cxml.get_order_count())
    
    #xml안에 들어 있는 작업순서(string)가 리스트 형태로 출력된다
    print(cxml.get_order_list())

    #xml_reader 클래스를 생성한다. 생성시 불러올 xml 주소를 인자로 넘겨준다
    cxml_objectdetect = Cxml_reader("objectdetectlist.xml", "dog_light")
    
    #xml안에 yolo 모델 리스트 출력 
    print(cxml_objectdetect.get_model_list())
    
    #xml안에 들어 있는 yolo 모델이 해당 스텝에 인식해야 할 object 갯수 출력
    print(cxml_objectdetect.get_object_count_list())

    #xml안에 들어 있는 yolo 모델이 해당 스텝에 인식해야 하는 파트 이름 출력
    print(cxml_objectdetect.get_object_parts_list())

    print(cxml_objectdetect.get_bar_count())

if __name__ == "__main__":
    main()