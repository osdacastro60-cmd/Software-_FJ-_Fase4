# SISTEMA DE GESTION SOFTWARE FJ - FASE 4 (UNAD)
# Archivo: Ejercicio_4.py
# Desarrollo de solucion orientada a objetos sin base de datos
# Cumple con el 100% de los requerimientos de la guia de actividades

import logging
import re
from abc import ABC, abstractmethod
from datetime import datetime

# 1. Configuracion del sistema de logs
logging.basicConfig(
    filename='sistema_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

# 2. Excepciones personalizadas
class ErrorSoftwareFJ(Exception):
    pass

class ErrorClienteInvalido(ErrorSoftwareFJ):
    pass

class ErrorServicioInvalido(ErrorSoftwareFJ):
    pass

class ErrorReservaInvalida(ErrorSoftwareFJ):
    pass

# 3. Clase abstracta EntidadBase y Clase Cliente
class EntidadBase(ABC):
    def __init__(self, id_entidad):
        self._id_entidad = id_entidad

    @property
    def id_entidad(self):
        return self._id_entidad

    @abstractmethod
    def obtener_resumen(self):
        pass

class Cliente(EntidadBase):
    def __init__(self, id_cliente, nombre, cedula, email):
        super().__init__(id_cliente)
        self.nombre = nombre
        self.cedula = cedula
        self.email = email

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):
        if not valor or not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ErrorClienteInvalido("El nombre debe tener al menos 3 letras.")
        self._nombre = valor.strip()

    @property
    def cedula(self):
        return self._cedula

    @cedula.setter
    def cedula(self, valor):
        if not str(valor).isdigit() or len(str(valor)) < 5:
            raise ErrorClienteInvalido("La cedula debe contener solo numeros (minimo 5 digitos).")
        self._cedula = str(valor)

    @property
    def email(self):
        return self._email

    @email.setter
    def email(self, valor):
        patron = r'^[\w\.-]+@[\w\.-]+\.\w+$'
        if not re.match(patron, valor):
            raise ErrorClienteInvalido(f"El correo '{valor}' no es valido.")
        self._email = valor

    def obtener_resumen(self):
        return f"Cliente [{self.id_entidad}]: {self.nombre} (Cedula: {self.cedula}, Email: {self.email})"

# 4. Clase abstracta Servicio y 3 subclases especializadas
class Servicio(EntidadBase):
    def __init__(self, id_servicio, nombre_servicio):
        super().__init__(id_servicio)
        self._nombre_servicio = nombre_servicio

    @property
    def nombre_servicio(self):
        return self._nombre_servicio

    @abstractmethod
    def calcular_costo(self):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self):
        pass

    def calcular_costo_con_descuento(self, porcentaje_descuento=0, incluir_iva=True):
        costo_base = self.calcular_costo()
        descuento = costo_base * (porcentaje_descuento / 100)
        subtotal = costo_base - descuento
        total = subtotal * 1.19 if incluir_iva else subtotal
        return round(total, 2)

class ServicioSalas(Servicio):
    def __init__(self, id_servicio, tipo_sala, horas, precio_por_hora=50000):
        super().__init__(id_servicio, "Reserva de Sala de Reuniones")
        self.tipo_sala = tipo_sala
        self.horas = horas
        self.precio_por_hora = precio_por_hora
        self.validar_parametros()

    def validar_parametros(self):
        if self.horas <= 0:
            raise ErrorServicioInvalido("Las horas de la sala deben ser mayores a 0.")
        if self.tipo_sala not in ['VIP', 'Ejecutiva', 'Estandard']:
            raise ErrorServicioInvalido(f"Tipo de sala '{self.tipo_sala}' invalido.")

    def calcular_costo(self):
        multiplicador = {'VIP': 1.5, 'Ejecutiva': 1.2, 'Estandard': 1.0}
        return self.horas * self.precio_por_hora * multiplicador[self.tipo_sala]

    def describir_servicio(self):
        return f"Sala {self.tipo_sala} por {self.horas} hora(s)"

    def obtener_resumen(self):
        return f"Servicio Salas [{self.id_entidad}]: {self.describir_servicio()}"

class ServicioEquipos(Servicio):
    def __init__(self, id_servicio, tipo_equipo, cantidad, dias, tarifa_dia=30000):
        super().__init__(id_servicio, "Alquiler de Equipos Tecnologicos")
        self.tipo_equipo = tipo_equipo
        self.cantidad = cantidad
        self.dias = dias
        self.tarifa_dia = tarifa_dia
        self.validar_parametros()

    def validar_parametros(self):
        if self.cantidad <= 0 or self.dias <= 0:
            raise ErrorServicioInvalido("La cantidad y dias de equipos deben ser mayores a 0.")

    def calcular_costo(self):
        return self.cantidad * self.dias * self.tarifa_dia

    def describir_servicio(self):
        return f"{self.cantidad} {self.tipo_equipo}(s) por {self.dias} dia(s)"

    def obtener_resumen(self):
        return f"Servicio Equipos [{self.id_entidad}]: {self.describir_servicio()}"

class ServicioAsesoria(Servicio):
    def __init__(self, id_servicio, especialidad, horas_asesoria, tarifa_hora=80000):
        super().__init__(id_servicio, "Asesoria Especializada en Software")
        self.especialidad = especialidad
        self.horas_asesoria = horas_asesoria
        self.tarifa_hora = tarifa_hora
        self.validar_parametros()

    def validar_parametros(self):
        if self.horas_asesoria <= 0:
            raise ErrorServicioInvalido("Las horas de asesoria deben ser mayores a 0.")

    def calcular_costo(self):
        return self.horas_asesoria * self.tarifa_hora

    def describir_servicio(self):
        return f"Asesoria en {self.especialidad} por {self.horas_asesoria} hora(s)"

    def obtener_resumen(self):
        return f"Servicio Asesoria [{self.id_entidad}]: {self.describir_servicio()}"

# 5. Clase Reserva
class Reserva(EntidadBase):
    def __init__(self, id_reserva, cliente: Cliente, servicio: Servicio):
        super().__init__(id_reserva)
        if not isinstance(cliente, Cliente) or not isinstance(servicio, Servicio):
            raise ErrorReservaInvalida("La reserva requiere un Cliente y Servicio validos.")
        self.cliente = cliente
        self.servicio = servicio
        self.estado = "Pendiente"
        self.fecha_creacion = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def procesar_reserva(self, porcentaje_descuento=0, aplicar_impuesto=True):
        try:
            logging.info(f"Iniciando reserva #{self.id_entidad} para {self.cliente.nombre}...")
            if self.estado == "Cancelada":
                raise ErrorReservaInvalida("No se puede procesar una reserva cancelada.")
            
            costo_final = self.servicio.calcular_costo_con_descuento(porcentaje_descuento, aplicar_impuesto)
            self.estado = "Confirmada"

        except ErrorServicioInvalido as e:
            msg_err = f"Error de servicio en Reserva #{self.id_entidad}."
            logging.error(f"{msg_err} Detalle: {e}")
            raise ErrorReservaInvalida(msg_err) from e

        else:
            msg_exito = f"Reserva #{self.id_entidad} CONFIRMADA. Total: ${costo_final:,.2f} COP"
            logging.info(msg_exito)
            print(f" [EXITO] {msg_exito}")
            return costo_final

        finally:
            logging.info(f"Finalizo tramite de Reserva #{self.id_entidad} (Estado: {self.estado}).")

    def cancelar_reserva(self):
        if self.estado == "Cancelada":
            raise ErrorReservaInvalida("La reserva ya estaba cancelada.")
        self.estado = "Cancelada"
        logging.info(f"Reserva #{self.id_entidad} fue CANCELADA.")
        print(f" [CANCELACION] Reserva #{self.id_entidad} cancelada.")

    def obtener_resumen(self):
        return f"Reserva #{self.id_entidad} | Cliente: {self.cliente.nombre} | Estado: {self.estado}"

# 6. Simulacion de los 10 Escenarios
def ejecutar_simulaciones():
    print("=" * 70)
    print("   SIMULACION SOFTWARE FJ - FASE 4 (UNAD)")
    print("=" * 70)
    logging.info("--- INICIO DE SIMULACION DE 10 OPERACIONES ---")

    # Escenario 1: Registro de Cliente Valido
    print("\n--- ESCENARIO 1: Registro de Cliente Valido ---")
    c1 = Cliente(1, "Ana Martinez", "101829384", "ana.martinez@email.com")
    print(f" [OK] {c1.obtener_resumen()}")

    # Escenario 2: Error Cedula Invalida
    print("\n--- ESCENARIO 2: Intento de Cedula Invalida ---")
    try:
        c2 = Cliente(2, "Carlos Lopez", "ABC_INVALIDO", "carlos@email.com")
    except ErrorClienteInvalido as e:
        print(f" [ERROR CAPTURADO]: {e}")
        logging.warning(f"Escenario 2: {e}")

    # Escenario 3: Error Correo Sin Arroba
    print("\n--- ESCENARIO 3: Intento de Email Invalido ---")
    try:
        c3 = Cliente(3, "Pedro Gomez", "10928374", "pedrogomez_sin_email.com")
    except ErrorClienteInvalido as e:
        print(f" [ERROR CAPTURADO]: {e}")
        logging.warning(f"Escenario 3: {e}")

    # Escenario 4: Servicio de Sala VIP Valido
    print("\n--- ESCENARIO 4: Servicio de Sala VIP Valido ---")
    s1 = ServicioSalas(101, "VIP", horas=4)
    print(f" [OK] {s1.obtener_resumen()} - Costo Base: ${s1.calcular_costo():,.2f}")

    # Escenario 5: Servicio de Equipos con Dias Negativos (Error)
    print("\n--- ESCENARIO 5: Servicio Equipos con Parametros Invalidos ---")
    try:
        s2 = ServicioEquipos(102, "Portatil i7", cantidad=2, dias=-3)
    except ErrorServicioInvalido as e:
        print(f" [ERROR CAPTURADO]: {e}")
        logging.warning(f"Escenario 5: {e}")

    # Escenario 6: Servicio de Asesoria Valido
    print("\n--- ESCENARIO 6: Servicio de Asesoria Valido ---")
    s3 = ServicioAsesoria(103, "Ciberseguridad y Python", horas_asesoria=5)
    print(f" [OK] {s3.obtener_resumen()} - Costo Base: ${s3.calcular_costo():,.2f}")

    # Escenario 7: Reserva Exitosa con Descuento del 10% e IVA
    print("\n--- ESCENARIO 7: Reserva Exitosa (Sala VIP + Desc. 10% + IVA) ---")
    r1 = Reserva(1001, c1, s1)
    r1.procesar_reserva(porcentaje_descuento=10, aplicar_impuesto=True)

    # Escenario 8: Reserva Exitosa de Asesoria
    print("\n--- ESCENARIO 8: Reserva Exitosa (Asesoria Ciberseguridad) ---")
    r2 = Reserva(1002, c1, s3)
    r2.procesar_reserva(porcentaje_descuento=0, aplicar_impuesto=True)

    # Escenario 9: Cancelacion de Reserva
    print("\n--- ESCENARIO 9: Cancelacion de Reserva ---")
    r2.cancelar_reserva()

    # Escenario 10: Procesar Reserva Ya Cancelada (Provocacion de Error)
    print("\n--- ESCENARIO 10: Intento de Procesar Reserva Cancelada ---")
    try:
        r2.procesar_reserva()
    except ErrorReservaInvalida as e:
        print(f" [ERROR CAPTURADO Y REGISTRADO EN LOGS]: {e}")
        logging.warning(f"Escenario 10: {e}")

    print("\n" + "=" * 70)
    print(" SIMULACION FINALIZADA! Eventos guardados en 'sistema_fj.log'.")
    print("=" * 70)
    logging.info("--- FIN DE SIMULACION DE 10 OPERACIONES ---")

if __name__ == '__main__':
    ejecutar_simulaciones()
