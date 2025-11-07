# src/domain/value_objects/enums.py
from enum import Enum

class Rol(str, Enum):
    ALUMNO = "alumno"
    DOCENTE = "docente" 

class Entorno(str, Enum):
    CASA = "casa"
    PRIMARIA = "primaria"
    SECUNDARIA = "secundaria"
    PREESCOLAR = "preescolar"
    PREPARATORIA = "preparatoria"
    UNIVERSIDAD = "universidad"
    CENTRO_REHABILITACION = "centro_rehabilitacion"


class NivelEducativo(str, Enum):
    # Niveles especiales
    NINGUNO = "ninguno"
    ANALFABETA = "analfabeta"
    
    # Educación Básica
    EDUCACION_INICIAL = "educacion_inicial"
    PREESCOLAR = "preescolar"
    PRIMARIA = "primaria"
    SECUNDARIA = "secundaria"
    
    # Educación Media Superior
    BACHILLERATO_GENERAL = "bachillerato_general"
    BACHILLERATO_TECNICO = "bachillerato_tecnico"
    BACHILLERATO_PROFESIONAL = "bachillerato_profesional"
    
    # Educación Superior - Licenciatura
    LICENCIATURA = "licenciatura"
    
    # Educación Superior - Posgrado
    ESPECIALIDAD = "especialidad"
    MAESTRIA = "maestria"
    DOCTORADO = "doctorado"
    
    # Otras modalidades
    TECNICO_SUPERIOR_UNIVERSITARIO = "tecnico_superior_universitario"
    PROFESIONAL_ASOCIADO = "profesional_asociado"
    EDUCACION_NORMAL = "educacion_normal"
    ALFABETIZACION_ADULTOS = "alfabetizacion_adultos"
    PRIMARIA_ADULTOS = "primaria_adultos"
    SECUNDARIA_ADULTOS = "secundaria_adultos"
