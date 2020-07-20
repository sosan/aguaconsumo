import re
import math

from datetime import datetime
from datetime import timedelta
from flask import session

from ModuloMongo.ManagerMongo import managermongo


# import calendar

# todo: agrupar en uno sola clase
class Errores:
    def __init__(self):
        self.correcto = 1
        self.duplicado = 2
        self.fallodb = 3
        self.noexiste = 4
        self.noactualizado = 5


class ManagerLogica():
    def __init__(self):
        self.managermongo = managermongo
        self.errores = Errores()

    def comprobarusuario(self, usuario, password, nombre):
        # metodo donde comprobamos si los datos del usuario son correctos y si existe el usuario
        # devuelve una tupla de bools
        datos_correctos = False
        existe_usuario = False

        if (len(usuario) > 12):
            return datos_correctos, existe_usuario

        datos_correctos = self.comprobar_datos_usuario(usuario, password, nombre)
        if (datos_correctos == False):
            return datos_correctos, existe_usuario

        existe_usuario = self.managermongo.comprobarusuario(usuario, password)
        return datos_correctos, existe_usuario

    def comprobar_datos_usuario(self, usuario, password, nombre):
        # metodo donde comprueba los datos introducidos tienen algun
        # error.
        # regex comprueba si tiene al menos: 1 elemento en mayusculas, 1 digito, 1 caracter especial, tambien comprueba
        # longitud que sea de al menos 8 caracteres {8,}
        if (usuario == "" or password == "" or nombre == ""):
            return False

        reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{8,}$"
        pattern = re.compile(reg)
        if re.search(pattern, password):
            return True

        return False

    def comprobar_existencia_usuario_db(self, usuario, password):
        existe_usuario = self.managermongo.comprobarusuario(
            usuario, password)
        return existe_usuario

    def getusuario(self, usuario, password):
        datos = self.managermongo.get_data_usuario(usuario, password)
        return datos

    def registrarusuario(self, usuario, password, nombre):
        ok = self.managermongo.registrarusuario(usuario, password, nombre)
        return ok

    def nuevo_registro_agua(self, txt_fecha, txt_valor, txt_concepto, usuario):
        try:
            trozos_fecha = txt_fecha.split("-")
            anyo = int(trozos_fecha[0])
            mes = int(trozos_fecha[1])
            dia = int(trozos_fecha[2])
            time_actual = datetime.utcnow()
            fecha_convertida = datetime(
                anyo, mes, dia, time_actual.hour, time_actual.minute, time_actual.second)

            valor = float(txt_valor)
            valor = self.truncar(valor, -1)
            mensaje = self.managermongo.nuevo_registro_agua(
                usuario, fecha_convertida, txt_concepto, valor)
            return mensaje
        except ValueError:
            raise Exception("No posible conversion")

    def truncar(self, numero, decimales):
        if numero.is_integer():
            return math.trunc(numero)
        # todos los decimales
        if decimales == -1:
            return numero

        # si no es -1 truncamos al numero de decimales
        factor = 10.0 ** decimales
        return math.trunc(numero * factor) / factor

    def getinforme(self, usuario, fecha_start, fecha_end):
        datos = self.managermongo.getinforme(usuario, fecha_start, fecha_end)
        return datos

    def getlistado_conceptos(self, usuario):
        listado_conceptos = self.managermongo.getlistado_conceptos(usuario)
        return listado_conceptos

    def getlastdays(self, usuario, cantidad_dias):
        end_date = datetime.utcnow()
        delta_date = end_date - timedelta(days=cantidad_dias)

        # labels = []
        # for o in range(delta_date.day, end_date.day + 1):
        #     labels.append("{}".format(o))

        datos_raw = self.managermongo.getinforme(usuario, delta_date, end_date)
        listado_conceptos = self.getlistado_conceptos(usuario)

        num_limite_datos = 10
        if len(datos_raw) < 10:
            num_limite_datos = len(datos_raw)

        listado_datos, datos_procesados = self.procesar_datoschart(datos_raw, listado_conceptos)

        return listado_datos, datos_procesados, delta_date, num_limite_datos

    def procesar_datoschart(self, datos, listado_conceptos):
        """
        _id: 5f0e0c67a130ea8176834961
        usuario: "h@h.com"
        fecha: 2020-07-16T23:02:40.000+00:00
        concepto: "Agua Natural"
        valor: 5

        """
        datos_procesados = []
        listado_datos = []
        for o in range(0, len(listado_conceptos)):
            templist = []
            for i in range(0, len(datos)):
                if len(datos_procesados) < len(datos):
                    datos_procesados.append(
                        {"fecha": datos[i]["fecha"], "concepto": datos[i]["concepto"], "valor": datos[i]["valor"]})

                if datos[i]["concepto"] == listado_conceptos[o]:
                    acumulado_valor = 0
                    for x in range(0, len(datos)):
                        if datos[x]["concepto"] == listado_conceptos[o]:
                            # todo: si no es igual continue
                            if ((datos[i]["fecha"].day == datos[x]["fecha"].day) and (datos[i]["fecha"].month ==  datos[x]["fecha"].month)):
                                acumulado_valor = acumulado_valor + datos[x]["valor"]
                    if len(templist) > 0:
                        if (templist[-1][0].day != datos[i]["fecha"].day) and (templist[-1][0].month != datos[i]["fecha"].month):
                            if acumulado_valor != 0:
                                templist.append([datos[i]["fecha"], acumulado_valor])
                            else:
                                templist.append([datos[i]["fecha"], datos[i]["valor"]])
                        if (templist[-1][0].day != datos[i]["fecha"].day) and (templist[-1][0].month == datos[i]["fecha"].month):
                            if acumulado_valor != 0:
                                templist.append([datos[i]["fecha"], acumulado_valor])
                            else:
                                templist.append([datos[i]["fecha"], datos[i]["valor"]])
                    else:
                        if acumulado_valor != 0:
                            templist.append([datos[i]["fecha"], acumulado_valor])
                        else:
                            templist.append([datos[i]["fecha"], datos[i]["valor"]])
            if len(templist) > 0:
                listado_datos.append(templist)

        return listado_datos, datos_procesados

    def insertar_nuevo_concepto(self, usuario, concepto):
        resultado = self.managermongo.insertar_nuevo_concepto(usuario, concepto)

        if resultado == self.errores.correcto:
            return True
        elif resultado == self.errores.duplicado:
            session["errorinsertadoconcepto"] = "Concepto Duplicado"
        else:
            session["errorinsertadoconcepto"] = "Fallo db"

        return False

    def renombrar_concepto(self, usuario, concepto_antiguo, concepto_nuevo):
        errores = self.managermongo.renombrar_concepto(usuario, concepto_antiguo, concepto_nuevo)
