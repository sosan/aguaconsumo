import os
import locale
import uuid

from pymongo import MongoClient
from bson.objectid import ObjectId

from datetime import datetime
from datetime import timedelta
from pymongo.collection import Collection, ReturnDocument
from pymongo.database import Database
from pymongo.errors import ConnectionFailure

#todo: agrupar en uno sola clase
class Errores:
    def __init__(self):
        self.correcto = 1
        self.duplicado = 2
        self.fallodb = 3
        self.noexiste = 4
        self.noactualizado = 5


class ManagerMongo:
    def __init__(self):

        self.MONGO_URL = "mongodb+srv://{0}:{1}@{2}"
        self.cliente: MongoClient = None
        self.db: Database = None
        self.coleccion_usuario: Collection = None
        self.coleccion_admin: Collection = None
        self.errores = Errores()

    def conectDB(self, usuario, password, host, db, coleccion_user, coleccion_admin):
        try:
            self.cliente = MongoClient(self.MONGO_URL.format(
                usuario, password, host), ssl_cert_reqs=False)
            self.db = self.cliente[db]
            self.coleccion_usuario = self.db[coleccion_user]
            self.coleccion_admin = self.db[coleccion_admin]

        except ConnectionFailure:
            raise Exception("Servidor no disponible")

    def comprobarusuario(self, usuario, password):
        try:
            resultado = self.coleccion_admin.find_one(
                {"usuario": usuario, "password": password})
            if resultado != None:
                if len(resultado) > 0:
                    return True
            return False
        except ConnectionFailure:
            raise Exception("Servidor no disponible")

    def get_data_usuario(self, usuario, password):
        try:
            datos = self.coleccion_admin.find_one(
                {"usuario": usuario, "password": password})
            if datos != None:
                if len(datos) > 0:
                    return datos
            return None
        except ConnectionFailure:
            raise Exception("Servidor no disponible")


    def registrarusuario(self, usuario, password, nombre):
        try:
            registro = self.coleccion_admin.insert_one(
                {"usuario": usuario, "password": password, "nombre": nombre})
            if registro.inserted_id != None:
                return True
            return False
        except ConnectionFailure:
            raise Exception("Servidor no disponible")

    def nuevo_registro_agua(self, usuario, fecha, concepto, valor):
        registrar = self.coleccion_usuario.insert_one({
            "usuario": usuario,
            "fecha": fecha,
            "concepto": concepto,
            "valor": valor
        })

        if registrar.inserted_id != None:
            return "Evento registrado con éxito"
        else:
            return "No posible registro"
    
    def getinforme(self, usuario, fecha_inicio_informe, fecha_fin_informe):
        historico = list(self.coleccion_usuario.find(
            {
                "usuario": usuario,
                "fecha": {
                    "$gte": fecha_inicio_informe,
                    "$lte": fecha_fin_informe
                }
            }, {"_id": False}).sort("fecha", 1))

        return historico

    def getvalores(self, usuario):
        resultado = list(self.coleccion_usuario.find({"usuario": usuario}))
        return resultado
    
    def getlistado_conceptos(self, usuario):
        listadoconceptos = self.coleccion_usuario.find_one(
            {"conceptos_usuario": usuario}, {"_id": False})

        if not listadoconceptos:
            resultado = self.insert_default_conceptos(usuario)
            if resultado == True:
                listadoconceptos = self.coleccion_usuario.find_one(
                    {"conceptos_usuario": usuario}, {"_id": False})
                return listadoconceptos["conceptos"]
            else:
                raise Exception("No se ha podido introducir agua")
        else:
            return listadoconceptos["conceptos"]

    def insertar_nuevo_concepto(self, usuario, concepto):
        # primero miramos si existe el concepto:
        datos = self.coleccion_usuario.find_one(
            {"conceptos_usuario": usuario})
        if "conceptos" in datos:
            if concepto in datos["conceptos"]:
                # existe el concepto
                return self.errores.duplicado

        resultado = self.coleccion_usuario.update_one(
            {"conceptos_usuario": usuario},
            {"$push": {
                "conceptos": concepto
            }}
        )

        if resultado.modified_count > 0:
            return self.errores.correcto
        return self.errores.fallodb

    def renombrar_concepto(self, usuario, concepto_antiguo, concepto_nuevo):

        datos = self.coleccion_usuario.find_one(
            {"conceptos_usuario": usuario})
        if concepto_antiguo in datos["conceptos"]:
            for i in range(0, len(datos["conceptos"])):
                if datos["conceptos"][i] == concepto_antiguo:
                    datos["conceptos"][i] = concepto_nuevo
        else:
            return self.errores.noexiste

        resultado_concepto_actualizado = self.coleccion_usuario.update_one(
            { "conceptos_usuario": usuario },
            {
                "$set":
                {
                    "conceptos": datos["conceptos"]
                }
            }
        )

        ## quizas no sea necesario que haya un update para todos
        # numeroactualizaciones = self.coleccion_usuario.count_documents(
        #     {"usuario": usuario, "concepto": concepto_antiguo})

        # resultado__actualizacion_coleccion = self.coleccion_usuario.update_many(
        #     {
        #         "usuario": usuario,
        #         "concepto": concepto_antiguo
        #     },
        #     {
        #         "$set":
        #         {
        #             "concepto": concepto_nuevo
        #         }
        #     }
        # )

        if resultado_concepto_actualizado.modified_count > 0:
            return self.errores.correcto
        else:
            return self.errores.noactualizado

    def insert_default_conceptos(self, usuario):
        resultado = self.coleccion_usuario.insert_one(
            {
                "conceptos_usuario": usuario,
                "conceptos": [
                    "Agua Natural",
                    "Agua grifo",
                    "Agua FontVella",
                    "Agua Solan de Cabras",
                    "Fontecabras"
                ]

            }
        )

        if resultado.inserted_id != None:
            return True
        return False


# todo: mejorar, colocarlo en .env
mongo_user = os.environ.get("MONGO_USER", "pepito")
mongo_password = os.environ.get("MONGO_PASSWORD", "pepito")
mongo_uri = os.environ.get("MONGO_URI", "cluster0-6oq5a.gcp.mongodb.net")
mongo_db = os.environ.get("MONGO_DB", "practicasinem")
mongo_collection_user = os.environ.get("MONGO_COLLECTION_USER", "aguastats")
mongo_collection_admin = os.environ.get("MONGO_COLLECTION_ADMIN", "admin")

managermongo = ManagerMongo()
managermongo.conectDB(mongo_user, mongo_password, mongo_uri,
                    db=mongo_db, coleccion_user=mongo_collection_user, coleccion_admin=mongo_collection_admin)
