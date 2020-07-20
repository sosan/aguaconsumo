# con slim-buster suponemos que en la 3.8.X no habra muchos cambios
FROM python:3.8-slim-buster

# la imagen alpine mas pequeña pero no tiene glib, empaqueta musl
# https://wiki.musl-libc.org/functional-differences-from-glibc.html
# FROM python:3.8.1-alpine3.11


# copiamos lugar volatil requirements
COPY requirements.txt /tmp/

RUN pip install --upgrade pip && \
        pip install -r /tmp/requirements.txt

# copiamos el shell a bin para comprobar si
# estmaos en entorno de desarrollo o produccion
COPY /testing.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/testing.sh
#&&\
#ln -s /usr/local/bin/testing.sh /

# creamos usuario para no ser root
# para alpine
# # RUN adduser -D usuarioapp

# para slim-buster
RUN useradd --create-home usuarioapp
WORKDIR /home/usuarioapp

# creamos el arbol de directorios
# COPY /src /home/usuarioapp/src

# copiamos todo dentro de usuarioapp
# estamos copiando los dockerfile y docker-compose, etc..
# preguntar en el examen si lso dockerfile tienen que
# en la imagen.
COPY . /home/usuarioapp

USER usuarioapp

# cambiamos directorio a SRC
WORKDIR /home/usuarioapp/src

# bin en PATH
ENV PATH="/home/usuarioapp/.local/bin:${PATH}"

# por si acaso no esta en requirements. memorion 2 veces al dia XD
RUN pip install gunicorn

# abierto puerto -- cambiar por otro puerto --
EXPOSE 5000
ENV PORT=5000

# argumentos y varibles de entorno para flask --  cambiar development/production . devolopment=hot reloads ----
# BUILD.... docker build -t dados:latest -t dados:v1 . --build-arg FLASK_ENV="development"
# RUN ..... docker run ........ -e "FLASK_ENV=production"
ARG FLASK_ENV="development"
ENV FLASK_ENV="${FLASK_ENV}" \
        FLASK_DEBUG=1 \
        FLASK_APP=main.py:app \
        PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1

# pequeño echo para saber si por defecto estamos en producion o development
# RUN set -ex; \
#     if [ "${FLASK_ENV}" = "development" ]; then \
#         echo "FLASK_ENV POR DEFECTO: development"; \
#     else \
#         echo "FLASK_ENV POR DEFECTO: production"; \
#     fi

ENTRYPOINT [ "/usr/local/bin/testing.sh" ]
# si estamos en produccion, no aconsejan a flask como servidor.
# aconsejan nginx + gunicorn
CMD ["python", "main.py"]