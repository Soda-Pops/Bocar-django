# **BOCAR DJANGO**

## **Avisos importantes**

>[!NOTE]
>
> Por cuestiones de facilidad al desarrollar he decido dejar la configuracion par ahacer un archivo ``.sqlite3``, no afecta nada en diseño, en cuanto se cambien `settings.py` a una instacia de mysql todo seguira funcionando normal

>[!NOTE]
>
> Queda pendiente reincoorporar archivo ``environmente.yml`` para ambiente virtual

>[!NOTE]
>
>Se esta considerando usar docker pero para todo el proyecto, aun no es nada seguro, pero esto se esta pensando para tener mayor facilidad de desarrollo, sin tener tantas bases de datos aisladas.

## **Rutas de navegacion del proyecto**

Hemos implentado **Swagger** como medio estandar de documetacion de **APIs**, asi mismo para un maneho de pruebas y al mismo tiempo, para poder vizualizar los endpoints de mejor manera, sin embargo hay dos rutas con las que ustedes navegaran en django.

### **API docs with swagger**  
[http://127.0.0.1:8000/schema/swagger/](http://127.0.0.1:8000/schema/swagger/)


### **Admin panel**
[http://127.0.0.1:8000/schema/swagger/](http://127.0.0.1:8000/schema/swagger/)

>[!IMPORTANT]
>
> Como no se esta subiendo el archivo de tipo ``.sqlite3``, no hay un usuario, es importante que lo creen ustedes mismo con el comando

```bash
python manage.py createsuperuser
```


