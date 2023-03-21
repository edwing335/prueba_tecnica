#!/usr/bin/env python

from dbus_next.aio import MessageBus
import asyncio


async def main():

    try:
        bus = await MessageBus().connect()


        # datos de conexion al servicio
        nombre_bus="com.monitoreointeligente.retotecnico"
        nombre_path="/com/monitoreointeligente/retotecnico"
        nombre_interface="com.monitoreointeligente.retotecnico"

        introspection = await bus.introspect(nombre_bus,nombre_path)
        obj = bus.get_proxy_object(nombre_bus,nombre_path,introspection)
        interface = obj.get_interface(nombre_interface)

        # codigos para llamados de metodos
        # usar la sintaxis call_[METHOD]

        # lista_checksum
        print('dato1')
        salida = await interface.call_lista_checksum()
        
        print(salida)

        # calcular
        print('dato2')
        salida2 = await interface.call_calcular('/home/edw/Downloads/download.jpeg','md5')
        print(salida2)

        # codigos para llamados de signal
        # agregar una funcion de llamado
        # usar la sintaxis on_[SIGNAL]
        def changed_notify(new_value):
            print(f'The new value is: {new_value}')

        print('dato3')
        interface.on_terminado(changed_notify)
        

        # codigos para properties
        # usar la sintaxis get_[PROPERTY] y set_[PROPERTY] 

        # leer
        print('dato4')
        solicitudesactivas = await interface.get_solicitudesactivas()
        print(solicitudesactivas)

        # escribir
        print('dato5')
        await interface.set_solicitudesactivas(12)
        
        await asyncio.sleep(2)
        await bus.wait_for_disconnect()
        
    except:
        # detener el ciclo asyncio
        print("cerrando el ciclo")
        await asyncio.sleep(10)
        asyncio.get_event_loop().stop()
        

asyncio.run(main())


