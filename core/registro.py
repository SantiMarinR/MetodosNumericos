import importlib
import inspect
import pkgutil

import metodos
from core.metodo_base import MetodoNumerico


def obtener_metodos():
    lista_metodos = []

    for _, nombre_modulo, _ in pkgutil.walk_packages(
        metodos.__path__,
        metodos.__name__ + "."
    ):
        modulo = importlib.import_module(nombre_modulo)

        for _, clase in inspect.getmembers(modulo, inspect.isclass):
            if (
                issubclass(clase, MetodoNumerico)
                and clase is not MetodoNumerico
                and clase.__module__ == modulo.__name__
            ):
                lista_metodos.append(clase)

    lista_metodos.sort(key=lambda clase: (clase.categoria, clase.nombre))
    return lista_metodos
