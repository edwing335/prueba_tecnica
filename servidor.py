#!/usr/bin/env python

import hashlib
import json
import argparse
import configparser

from dbus_next.service import ServiceInterface, method, dbus_property, signal, Variant
from dbus_next.aio import MessageBus
from dbus_next.constants import PropertyAccess

import asyncio


# funciones de suma de comprobacion
def calculo_checksum(nombre_archivo, algoritmo):

    try:
        with open(nombre_archivo, 'rb') as f:
            contenido = f.read()

            if algoritmo == 'md5':
                hash_obj = hashlib.md5()
            elif algoritmo == 'sha1':
                hash_obj = hashlib.sha1()
            elif algoritmo == 'sha224':
                hash_obj = hashlib.sha224()
            elif algoritmo == 'sha256':
                hash_obj = hashlib.sha256()
            elif algoritmo == 'sha384':
                hash_obj = hashlib.sha384()
            elif algoritmo == 'sha512':
                hash_obj = hashlib.sha512()
            elif algoritmo == 'blake2b':
                hash_obj = hashlib.blake2b()
            elif algoritmo == 'blake2s':
                hash_obj = hashlib.blake2s()
            elif algoritmo == 'sha3_224':
                hash_obj = hashlib.sha3_224()
            elif algoritmo == 'sha3_256':
                hash_obj = hashlib.sha3_256()
            elif algoritmo == 'sha3_384':
                hash_obj = hashlib.sha3_256()
            elif algoritmo == 'sha3_512':
                hash_obj = hashlib.sha3_512()
            elif algoritmo == 'shake_128':
                hash_obj = hashlib.shake_128()
            elif algoritmo == 'shake_256':
                hash_obj = hashlib.shake_256()
            else:
                print("hash no valido en la lista")
                return "", "TypeError", "Operacion no compatible"

            print("checksum terminado")
            return str(hash_obj.hexdigest()), "", ""

    except:
        return "", "FileNotFoundError", "Error al abrir el archivo"


# listado de checksum disponible
def checksum_disponible():
    var = "md5,sha1,sha224,sha256,sha384,sha512,"+"\n"
    var = var+"blake2b,blake2s,sha3_224,sha3_256,"+"\n"
    var = var+"sha3_384,sha_512,shake_128,shake_256"
    return var

# clase methods, signal, properties - interfaz dbus


class Interface(ServiceInterface):
    def __init__(self):
        super().__init__("com.monitoreointeligente.retotecnico")

        self._solicitudesactivas = 0
        self._maximoactivas = 0
        self._token = ""
        self._codigoerror = 0
        self._mensajeerror = ""
        self._data_token = ""

    def config_solicitudesactivas(self, data_solicitudesactivas):
        ########################
        # espacio para logica de configuracion de solicitudesactivas
        #
        #
        ########################
        print(data_solicitudesactivas)
        self._solicitudesactivas = data_solicitudesactivas
        return "OK"

    def config_maximoactivas(self, data_maximoactivas):
        ########################
        # espacio para logica de configuracion de maximoactivas
        #
        #
        ########################
        print(data_maximoactivas)
        self._maximoactivas = data_maximoactivas
        return "OK"

    def config_token(self, data_token):
        datos_base = {
            "Maquina": data_token[1], "Referencia": data_token[2], "Administrador": data_token[3]}
        datos_base_str = json.dumps(datos_base)

        codigo_sha256 = hashlib.sha256()
        codigo_sha256.update(datos_base_str.encode("utf-8"))
        codigo_token = codigo_sha256.hexdigest()
        try:
            self._data_token = codigo_token
        except:
            self._data_token = "A12345"
        print(codigo_token)

        return "OK"

    @method()
    def salir(self):
        print("finalizar proceso dbus")
        # raise Exception("stop process")
        asyncio.get_event_loop().stop()

    @method()
    def lista_checksum(self) -> 's':
        lista = checksum_disponible()
        print("lista checksum:"+lista)
        return lista

    @method()
    def calcular(self, ruta: 's', tiposuma: 's') -> 's':
        token, codigoerror, mensajeerror = calculo_checksum(ruta, tiposuma)
        self._token = token
        self._codigoerror = codigoerror
        self._mensajeerror = mensajeerror

        dict_salida = {"token": self._data_token,
                       "codigoerror": codigoerror, "mensajeerror": mensajeerror}

        return str(json.dumps(dict_salida))

    @signal()
    def terminado(self) -> 'suss':
        print('bandera terminado 1')
        val_token = self._token
        val_mensajeerror = self._mensajeerror

        if self._codigoerror == "TypeError":
            val_codigoerror = 10
        elif self._codigoerror == "FileNotFoundError":
            val_codigoerror = 15
        else:
            val_codigoerror = 0

        return [self._data_token, val_codigoerror, val_mensajeerror, val_token]

    @dbus_property(PropertyAccess.READ)
    def solicitudesactivas(self) -> 'q':
        return self._solicitudesactivas

    @dbus_property()
    def maximoactivas(self) -> 'q':
        return self._maximoactivas

    @maximoactivas.setter
    def maximoactivas(self, val: 'q'):
        self._maximoactivas = val


async def main(vector_init):

    # configuracion servidor Dbus
    nombre_bus = "com.monitoreointeligente.retotecnico"
    nombre_path = "/com/monitoreointeligente/retotecnico"
    nombre_interface = "com.monitoreointeligente.retotecnico"
    
    print('inicio funcion')
    bus = await MessageBus().connect()
    interface = Interface()
    interface.config_maximoactivas(int(vector_init[0]))
    interface.config_token(vector_init)
    bus.export(nombre_path, interface)

    print('inicio request')
    await bus.request_name(nombre_bus)

    await asyncio.sleep(2)

    print('inicio await')
    await bus.wait_for_disconnect()


if __name__ == '__main__':

    vector_init = []

    try:
        parser = argparse.ArgumentParser()
        parser.add_argument('-f', '--p_archivo', type=str, help='ruta archivo ini')
        args = parser.parse_args()
        print('Archivo ini: ' + str(args.p_archivo))

        config = configparser.ConfigParser()
        config.read(args.p_archivo)

        # datos por defecto
        vector_init.append(str(config['setup']['maximoactivas']))

        # datos de la maquina
        vector_init.append(str(config['setup']['maquina']))
        vector_init.append(str(config['setup']['referencia']))
        vector_init.append(str(config['setup']['administrador']))
        print(vector_init)

    except:
        print('no hay archivo ini declarado')

        # datos por defecto
        vector_init.append(int(5))

        # datos de la maquina
        vector_init.append(str("vacio"))
        vector_init.append(str("vacio"))
        vector_init.append(str("vacio"))

    try:
        print('inicio dbus')
        asyncio.run(main(vector_init))
    except:
        print("programa terminado")
