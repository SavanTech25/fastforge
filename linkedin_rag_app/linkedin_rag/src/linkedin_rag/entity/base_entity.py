from linkedin_rag.data.actions import make_crud_action, handle_file
from linkedin_rag.utils.controller import from_model_to_dict, serialize_model
from fastapi import UploadFile

class Entity:
    
    def __init__(self, model_name: str, db=None, sql_model=None):
        self.__model_name = model_name
        self.__db = db
        self.__sql_model = sql_model
    
    def getModelName(self):
        return self.__model_name
    
    def setModelName(self, model_name):
        self.__model_name = model_name
    

    def saveModel(self, document):
        return make_crud_action(self.__db, self.__sql_model, "insert_one", document=document)
    
    def saveAllModel(self, documents):
        return make_crud_action(self.__db, self.__sql_model, "insert_many", documents=documents)

    def updateModel(self, filter, update):
        return make_crud_action(self.__db, self.__sql_model, "update_one", filter=filter, update={"$set": update})
    
    def updateAllModel(self, filter, update):
        return make_crud_action(self.__db, self.__sql_model, "update_many", filter=filter, update={"$set": update})
    
    def deleteModel(self, filter):
        return make_crud_action(self.__db, self.__sql_model, "delete_one", filter=filter)
    
    def purgeModel(self, filter={}):
        return make_crud_action(self.__db, self.__sql_model, "purge", filter=filter)
    
    def getModel(self, filter):
        return make_crud_action(self.__db, self.__sql_model, "find_one", filter=filter)
    
    def getModels(self):
        return make_crud_action(self.__db, self.__sql_model, "find_all")
    
    def getModelsBy(self, filter):
        return make_crud_action(self.__db, self.__sql_model, "find_all", filter=filter)

    def deactivateAll(self):
        return self.updateAllModel({'activate': True}, {'activate': False})
    
    ######### file
    def getFileByName(self, name: str):
        return handle_file("find_one", filename=name)
    
    def getFileById(self, id):
        return handle_file("find_one", id=id)
    
    def newFile(self, file: UploadFile):
        # We can pass the file object directly for synchronous reading
        return handle_file("insert_one", file=file)
    
    def deleteFile(self, id):
        return handle_file("delete_one", id=id)


    def to_json(self, model):
        return serialize_model(from_model_to_dict(model))
    
    def setId(self, id):
        self.__id = id
    
    def getId(self):
        return self.__id