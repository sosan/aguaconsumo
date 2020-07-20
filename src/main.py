# -*- coding: utf-8 -*-
"""
APLICACION WEB DONDE CONTADOR DE AGUA

"""
import os
# configuracion de puertos, path, etc...
import settings

from datetime import datetime, timedelta
import calendar

from flask import Flask
from flask_cors import CORS
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
from flask import session

# logica app
from ModuloLogica.ManagerLogica import ManagerLogica

# instanciaciones e inicializciones web
app = Flask(__name__)
app.secret_key = os.urandom(42)
CORS(app)
managerlogica = ManagerLogica()


# ruta home
@app.route("/", methods=["get"])
def home():
    return render_template("index.html")


@app.route("/", methods=["post"])
def recibir_login():
    if "usuario" and "password" in request.form:
        ok = managerlogica.comprobar_existencia_usuario_db(
            request.form["usuario"], request.form["password"])
        if ok == True:
            # existe usuario
            # devuelve dict con usuario, password, nombre
            datosusuario = managerlogica.getusuario(request.form["usuario"], request.form["password"])

            session["usuario"] = request.form["usuario"]
            session["password"] = request.form["password"]
            if "nombre" in datosusuario:
                session["nombre"] = datosusuario["nombre"]
            return redirect(url_for("profile"))

    return redirect(url_for("home"))


@app.route("/profile", methods=["get"])
def profile():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    listado_datos, datos_informes, delta_date, num_limite_datos, labels = managerlogica.getlastdays(
        session["usuario"], 6)

    return render_template("profile.html", informes=datos_informes, datos=listado_datos, labels=labels,
                           fecha_actual=datetime.utcnow(), fecha_delta=delta_date,
                           num_limite_datos=num_limite_datos, titulo="Entrada")


@app.route("/introduciragua", methods=["get"])
def introduciragua_get():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    listado_conceptos = managerlogica.getlistado_conceptos(session["usuario"])

    if "mensaje" in session:
        mensaje = session.pop("mensaje")
        return render_template("registro_agua.html", fecha_actual=datetime.utcnow(), mensaje=mensaje,
                               listado_conceptos=listado_conceptos, titulo="Entrada")

    return render_template("registro_agua.html", fecha_actual=datetime.utcnow(), listado_conceptos=listado_conceptos,
                           titulo="Registro")


@app.route("/introduciragua", methods=["post"])
def introduciragua_post():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    if "valor" and "fecha" in request.form:
        if request.form["concepto"] == "" or request.form["concepto"] == " ":
            return redirect(url_for("introduciragua_get"))
        try:
            print("fecha=", request.form["fecha"])
            # datetime.strptime(request.form["fecha"], '%Y-%m-%d %H:%M:%S')

            session["mensaje"] = managerlogica.nuevo_registro_agua(request.form["fecha"],
                                                                   request.form["valor"],
                                                                   request.form["concepto"],
                                                                   session["usuario"])

            return redirect(url_for("introduciragua_get"))

        except ValueError:
            raise Exception("conversion no posible")


@app.route("/informes", methods=["get"])
def informes_get():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    if "informes" in session:
        informes = session.pop("informes")
        informes_con_datos = session.pop("informes_con_datos")
        return render_template("informe.html", anyo_actual=datetime.utcnow().year,
                               mes_actual=datetime.utcnow().month, informes=informes,
                               informes_con_datos=informes_con_datos, titulo="Informes")

    return render_template("informe.html", anyo_actual=datetime.utcnow().year,
                           mes_actual=datetime.utcnow().month, informes=None, titulo="Informes")


@app.route("/informes", methods=["post"])
def informes_post():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    try:
        mes = int(request.form["mesinfo"])
        anyo = int(request.form["anoinfo"])

        fecha_inicio_informe = datetime(anyo, mes, 1)
        fecha_fin_informe = datetime(
            anyo, mes, calendar.monthrange(anyo, mes)[1])

        session["informes"] = managerlogica.getinforme(session["usuario"],
                                                       fecha_inicio_informe, fecha_fin_informe)
        print("len informes=", len(session["informes"]))
        if len(session["informes"]) > 0:
            session["informes_con_datos"] = True
        else:
            session["informes_con_datos"] = False

        return redirect(url_for("informes_get"))
    except ValueError:
        raise Exception("Conversion no valida")


@app.route("/registro", methods=["get"])
def registro_usuario_get():
    if "errores" in session:
        errores = session.pop("errores")
        return render_template("registro_usuario.html", errores=errores)

    return render_template("registro_usuario.html")


@app.route("/registro", methods=["post"])
def registro_usuario_post():
    if "usuario" and "password" and "nombre" in request.form:
        datos_correctos, existe_usuario = managerlogica.comprobar_existencia_usuario(
            request.form["usuario"],
            request.form["password"],
            request.form["nombre"]
        )

        if datos_correctos == False:
            session["errores"] = "Password debe contener al menos 1 caracter mayusculas, 1 digito, 1 caracter " \
                                 "especial (@$!%*#) y al menos longitud de 8 caracteres "
            return redirect(url_for("registro_usuario_get"))

        if existe_usuario == True:
            session["usuario"] = request.form["usuario"]
            session["password"] = request.form["password"]
            session["nombre"] = request.form["nombre"]
            return redirect(url_for("profile"))
        else:
            registro = managerlogica.registrarusuario(request.form["usuario"], request.form["password"],
                                                      request.form["nombre"])
            if registro == True:
                session["usuario"] = request.form["usuario"]
                session["password"] = request.form["password"]
                session["nombre"] = request.form["nombre"]
                return redirect(url_for("profile"))

    return redirect(url_for("registro_usuario_get"))


@app.route("/nuevoconcepto", methods=["post"])
def nuevo_concepto_post():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    if "txt_concepto" in request.form:
        if request.form["txt_concepto"] == "":
            return redirect(url_for("introduciragua_get"))

        resultado = managerlogica.insertar_nuevo_concepto(
            session["usuario"], request.form["txt_concepto"])

    return redirect(url_for("introduciragua_get"))


@app.route("/nuevoconcepto", methods=["get"])
def nuevo_concepto_get():
    return redirect(url_for("introduciragua_get"))


@app.route("/renombrarconcepto", methods=["get"])
def renombrar_concepto_get():
    return redirect(url_for("introduciragua_get"))


@app.route("/renombrarconcepto", methods=["post"])
def renombrar_concepto():
    redirection = check_usuario_password()
    if redirection == True:
        return redirect(url_for("home"))

    if "txt_renombrar_concepto" in request.form:
        if request.form["txt_renombrar_concepto"] == "":
            return redirect(url_for("introduciragua_get"))

        resultado = managerlogica.renombrar_concepto(
            session["usuario"], request.form["concepto"], request.form["txt_renombrar_concepto"])

    return redirect(url_for("introduciragua_get"))


# todo: borrar conceptos
@app.route("/borrarconceptos", methods=["post"])
def borrar_conceptos():
    pass


@app.route("/profile/desconexion", methods=["get"])
def desconexion_perfil():
    session.clear()
    return redirect(url_for("home"))


def check_usuario_password():
    """
    comprobamos si tenemos que redireccionar el usuario al login
    si no existe su session
    """
    redirect = False
    if "usuario" and "password" in session:
        exite_usuario = managerlogica.comprobar_existencia_usuario_db(
            session["usuario"], session["password"])
        if exite_usuario == False:
            session.clear()
            redirect = True
            return redirect
        else:
            return redirect
    else:
        redirect = True
        return redirect


if __name__ == "__main__":
    settings.readconfig()
    env_port = int(os.getenv("PORT", 5000))
    env_debug = os.getenv("FLASK_DEBUG", True)
    app.run(host="127.0.0.1", port=env_port, debug=env_debug)
