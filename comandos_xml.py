import xml.etree.ElementTree as ET

class ComandosXML:
    def __init__(self):
        self.xml_file = r"files\comandos_xml.xml"
        self.tree = ET.parse(self.xml_file)
        self.root = self.tree.getroot()

    #buscar etiquetas por ruta
    def lst_tags_por_ruta(self, path:str):
        etiquetas = []
        for elem in self.root.findall(path):
            etiquetas.append(elem.tag)
        return etiquetas
    
    def lst_attr_por_ruta(self, path:str):
        atributos = []
        lst_tags = self.lst_tags_por_ruta(path)

        for elem in lst_tags:
            for item in self.root.findall(f"{path}/{elem}"):
                atributos.append(item.attrib.keys())
                
        return atributos
    
    #valor de las tags por ruta
    def lst_valor_por_ruta(self, path:str):
        valores = []
        for elem in self.root.findall(path):
            valores.append(elem.text)
        return valores


    #crear diccionario con el valor de las tags y sus atributos
    def dict_comandos(self, path:str):
        comandos_dict = {}
        lst_tags = self.lst_tags_por_ruta(path)

        for elem in lst_tags:
            for item in self.root.findall(f"{path}/{elem}"):
                comandos_dict[item.text] = item.attrib
        
        return comandos_dict