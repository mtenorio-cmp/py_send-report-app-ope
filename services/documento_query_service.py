import pandas as pd
import logging

from datetime import date, datetime as dt

from interfaces.database_interface import IDatabaseConnection

logger = logging.getLogger(__name__)


class DocumentoQueryService:
    """Servicio para ejecutar consultas seguras predefinidas"""

    def __init__(self, db_connection: IDatabaseConnection):
        self.db_connection = db_connection

    _query_base = """
           SELECT
                    d.id AS doc_id,
                    d.Empresa AS doc_emp,
                    CONCAT(d.SerieGR, '-', d.NumeroGR) AS doc_num_gr,
                    CONCAT(d.SerieFactura, '-', d.NumeroFactura) AS doc_num_fac,
                    d.createAt AS doc_fec_crea, -- formato DATETIME nativo
                    DATE(d.FechaEntregaGR) AS doc_fec_ent_gr, -- formato DATE
                    DATE(d.FechaProgramadaGR) AS doc_fec_prog_gr,
                    d.RazonSocial AS doc_raz_soc,
                    d.CondicionPago AS doc_con_pag,
                    d.AgenciaTransporte AS doc_ag_trans,
                    d.Vendedor AS doc_vend,
                    d.ImporteME AS doc_imp_me,
                    d.PesoTotal AS doc_peso_tot,
                    d.Excepcion AS doc_excep,
                    d.Motivo AS doc_mot,
                    d.CantidadBultos AS doc_cant_bult,
                    
                    rd.horaLlegada AS rd_hora_lleg,
                    rd.horaSalida AS rd_hora_sal,
                    DATE(rd.fechaProgramada) AS rd_fec_prog,
                    
                    r.id AS rut_id,
                    r.fechaInicio AS rut_fec_ini,
                    r.fechaRetorno AS rut_fec_ret,
                    r.lugar_salida AS rut_lugar_sal,
                    DATE(r.fechaProgramada) AS rut_fec_prog,
                    
                    v.placa AS veh_placa,
                    
                    estado.descripcion AS est_desc,
                    
                    CONCAT(chofer.displayName, ' ', chofer.lastName) AS chofer_nom_comp
                    
            FROM documentos AS d
            LEFT JOIN ruta_detalle AS rd
                ON rd.docId = d.id
            LEFT JOIN ruta AS r
                ON r.id = rd.rutaId
            LEFT JOIN users AS chofer
                ON chofer.id = r.choferId
            LEFT JOIN enum_estado_pedido AS estado
                ON estado.id = rd.estadoId
            LEFT JOIN vehiculos AS v
                ON v.id = r.vehiculosId
            
        """
    
    # Construir WHERE dinámico a partir de filters (seguro, parametrizado)
    @staticmethod
    def _build_where(base_conditions: list, filters: dict)-> tuple[list, dict]:
        """Construye la cláusula WHERE y el diccionario de params.

        Soporta sufijos en las claves del filtro:
            - __in : lista -> columna IN %(param)s
            - __like: patrón -> columna LIKE %(param)s
            - __gt, __lt, __gte, __lte : comparadores
            - sin sufijo: igualdad
        """ 
        where_clauses = list(base_conditions) if base_conditions else []
        params = {}
        if not filters:
            return where_clauses, params

        for key, value in filters.items():
            # key puede ser 'rd.fechaProgramada' o 'doc_mot__in' etc.
            if '__' in key:
                col, op = key.rsplit('__', 1)
            else:
                col, op = key, 'eq'

            # sanear nombre de parámetro (solo letras, números y guiones bajos)
            param_base = key.replace('.', '_').replace('__', '_')
            param_base = ''.join(c for c in param_base if (c.isalnum() or c == '_'))

            if op == 'in':
                # generar parámetros individuales para MariaDB: (%(p1)s, %(p2)s, ...)
                items = list(value)
                if not items:
                    # IN () no es válido: forzar condición falsa
                    where_clauses.append('1 = 0')
                    continue

                placeholders = []
                for i, item in enumerate(items):
                    name = f"{param_base}_{i}"
                    placeholders.append(f"%({name})s")
                    params[name] = item

                placeholders_str = ', '.join(placeholders)
                where_clauses.append(f"{col} IN ({placeholders_str})")
            elif op == 'like':
                name = param_base
                where_clauses.append(f"{col} LIKE %({name})s")
                params[name] = value
            elif op in ('gt', 'lt', 'gte', 'lte'):
                op_map = {
                    'gt': '>', 
                    'lt': '<', 
                    'gte': '>=', 
                    'lte': '<='
                }
                name = param_base
                where_clauses.append(f"{col} {op_map[op]} %({name})s")
                params[name] = value
            else:  # eq
                name = param_base
                where_clauses.append(f"{col} = %({name})s")
                params[name] = value

        return where_clauses, params


    def query_documents(
        self,
        base_conditions: list = None,
        conditions: dict = None,
    ) -> pd.DataFrame:
        """Consulta documentos con condiciones dinámicas (genérica).

        Parámetros
        ----------
        conditions: dict, opcional
            Diccionario con condiciones/ filtros. Puede incluir una clave
            especial `date_programs` para filtrar por la fecha programada
            de la ruta (equivalente a DATE(r.fechaProgramada) = ...).
            Otras claves deben usar columnas SQL y pueden llevar sufijos:
              - __in, __like, __gt, __lt, __gte, __lte

        Ejemplo rápido
        --------------
        conditions = {
            'date_programs': date(2025,10,20),
            'd.Motivo__in': ['VENTA'],
            'v.placa__like': '%ABC%'
        }
        svc.query_documents(conditions)
        """

        # Preparar condiciones
        conditions = conditions or {}

        # NOTA: no convertir date_programs aquí — se usa tal cual desde conditions

        


       
        where_clauses, extra_params = self._build_where(base_conditions, conditions)

        # unir todas las cláusulas WHERE: la base (fecha) + dinámicas
        all_where = ' AND '.join(where_clauses)

        # Cortamos query_base hasta WHERE y añadimos la nueva cláusula
        query_pre_where = self._query_base.split('WHERE')[0]
        query = query_pre_where + 'WHERE\n                ' + all_where + '\n'

        logger.info(f"==>Query documentos con condiciones: {list(conditions.keys())}")
        return self.db_connection.execute_query_dataframe(query, extra_params)




    def get_delivery_documents_by_date_range(
        self,
        start_date: date,
        end_date: date,
        # motivos_list: List[str]
    ) -> pd.DataFrame:
        """
        Obtiene documentos de entrega y detalles de ruta filtrados por rango de fecha de entrega.
        """

        # Asegurar que siempre sean strings YYYY-MM-DD
        if isinstance(start_date, (date, dt)):
            start_date = start_date.isoformat()
        if isinstance(end_date, (date, dt)):
            end_date = end_date.isoformat()

        
        motivos = ["VENTA", "VENTA TRANSITO", "TRASLADO E/ESTABLECIMIENTOS"]
        conditions = {
            # Filtro de rango de fecha (se asume que _build_where traduce esto a >= y <=)
            # Si la columna d.createAt ya está disponible, la puedes usar
            'DATE(d.createAt)__gte': start_date, # Fecha de creación (mayor o igual)
            'DATE(d.createAt)__lte': end_date,   # Fecha de creación (menor o igual)
            
            # Filtro IN para Motivo
            'd.Motivo__in': motivos,
        }

        logger.info(
            f"==>Obteniendo documentos de entrega del {start_date} al {end_date}"
        )
        return self.query_documents(conditions)

    # Compatibilidad: wrapper con el nombre antiguo
    def get_programados_del_dia(self, date_programs: date = None, filters: dict = None) -> pd.DataFrame:
        """Compatibilidad: pasa `filters` directamente a `query_documents`.

        Nota: `date_programs` ya no se trata como condición especial. Si quieres
        filtrar por fecha, incluye la condición correspondiente en `filters`,
        por ejemplo: {"DATE(r.fechaProgramada)": "2025-10-20"} o
        {"DATE(r.fechaProgramada)__eq": "2025-10-20"}.
        """
        conditions = {"DATE(r.fechaProgramada)__eq": "2025-10-20"}
        return self.query_documents(conditions)
