#coding=utf-8
import codecs

DISPLERY_POSTFIX =  "_displayer_config"

class DisplayerFactory(object):
    _instance = None

    @classmethod
    def get_instance(cls):
        if (not cls._instance):
            cls._instance = DisplayerFactory()
        return  cls._instance

    def __init__(self):
        cls = self.__class__
        if (cls._instance):
            raise Exception("only one instance can be created!")

        self.displayer_map = {}
        for name, entity in globals().items():
            if (name.endswith(DISPLERY_POSTFIX) and callable(entity) ):
                displayer_config = entity
                displayer_config(self)



    def register_displayer(self, displayer_name, field_names_map, language="en"):
        if self.displayer_map.get(displayer_name) is None :
            self.displayer_map[displayer_name] = {language: field_names_map}
        else:
            self.displayer_map[displayer_name][language] = field_names_map


    def get_displayer(self, displayer_name, language="en", encode="utf-8"):
        displayer = self.displayer_map.get(displayer_name)
        candidate = (displayer and displayer.get(language)) or None

        if (candidate):
            encoder = codecs.getincrementalencoder(encode)()
            encoded_displayer = {}
            for k,v in candidate.items():
                encoded_displayer[k] = encoder.encode(v)

            candidate = encoded_displayer

        return candidate



#### convention: name_DISPLERY_POSTFIX, will be loaded in DisplayFactory.__init__()
def customer_info_displayer_config( factory ):
    if (type (factory) != DisplayerFactory ):
        return False

    displayer_name = "customer_info"
    en_displayer = {
        "id"  : u"ID",
        "name" : u"Name",
        "customer_no": u"Customer No.",
        "branch_name": u"Branch Name",
        "card_no":  u"Card No.",
        "mobile": u"Phone No.",
        "service_count": u"Service Count",
    }

    cn_displayer = {
        "id"  : u"ID",
        "name" : u"姓名",
        "customer_no": u"客户号",
        "branch_name": u"分行名称",
        "card_no":  u"卡号",
        "mobile": u"手机号",
        "service_count": u"充值点数",
    }

    factory.register_displayer(displayer_name, en_displayer, "en")
    factory.register_displayer(displayer_name, cn_displayer, "cn")
    return True
