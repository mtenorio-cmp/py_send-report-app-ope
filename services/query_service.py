import pandas as pd
import logging

from datetime import date, datetime as dt

from interfaces.database_interface import IDatabaseConnection

logger = logging.getLogger(__name__)


class SafeQueryService:
    """Servicio para ejecutar consultas seguras predefinidas"""

    def __init__(self, db_connection: IDatabaseConnection):
        self.db_connection = db_connection

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

        query = """
           SELECT
                    d.id AS doc_id,
                    d.Empresa AS doc_emp,
                    CONCAT(d.SerieGR, ' - ', d.NumeroGR) AS doc_num_gr,
                    CONCAT(d.SerieFactura, ' - ', d.NumeroFactura) AS doc_num_fac,
                    d.createAt AS doc_fec_crea, -- formato DATETIME nativo
                    DATE(d.FechaEntregaGR) AS doc_fec_ent_gr, -- formato DATE
                    DATE(d.FechaProgramadaGR) AS doc_fec_prog_gr,
                    DATE(rd.fechaProgramada) AS rd_fec_prog,
                    d.RazonSocial AS doc_raz_soc,
                    d.CondicionPago AS doc_con_pag,
                    d.AgenciaTransporte AS doc_ag_trans,
                    d.Vendedor AS doc_vend,
                    d.ImporteME AS doc_imp_me,
                    d.PesoTotal AS doc_peso_tot,
                    rd.horaLlegada AS rd_hora_lleg,
                    rd.horaSalida AS rd_hora_sal,
                    d.Excepcion AS doc_excep,
                    r.id AS rut_id,
                    v.placa AS veh_placa,
                    estado.descripcion AS est_desc,
                    DATE(r.fechaProgramada) AS rut_fec_prog,
                    r.fechaInicio AS rut_fec_ini,
                    r.fechaRetorno AS rut_fec_ret,
                    CONCAT(chofer.displayName, ' ', chofer.lastName) AS chofer_nom_comp,
                    rd.observacion AS rd_obs,
                    d.Motivo AS doc_mot,
                    d.CantidadBultos AS doc_cant_bult
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
            WHERE
                DATE(d.createAt) BETWEEN %(start_date)s AND %(end_date)s 
                AND d.Motivo IN ("VENTA", "VENTA TRANSITO", "TRASLADO E/ESTABLECIMIENTOS")
        """
        # AND rd.horaSalida IS NOT NULL

        params = {
            "start_date": start_date,
            "end_date": end_date,
            # "motivos": ",".join(f"'{m}'" for m in motivos_list),
        }

        logger.info(
            f"==>Obteniendo documentos de entrega del {start_date} al {end_date}"
        )
        return self.db_connection.execute_query_dataframe(query, params)

    def get_programados_del_dia(
        self,
        date_programs: date,
    ) -> pd.DataFrame:
        """
        Obtiene documentos de entrega y detalles de ruta filtrados por rango de fecha de entrega.
        """

        # Asegurar que siempre sean strings YYYY-MM-DD
        if isinstance(date_programs, (date, dt)):
            date_programs = date_programs.isoformat()

        query = """
           SELECT
                    d.id AS doc_id,
                    d.Empresa AS doc_emp,
                    CONCAT(d.SerieGR, ' - ', d.NumeroGR) AS doc_num_gr,
                    CONCAT(d.SerieFactura, ' - ', d.NumeroFactura) AS doc_num_fac,
                    d.createAt AS doc_fec_crea, -- formato DATETIME nativo
                    DATE(d.FechaEntregaGR) AS doc_fec_ent_gr, -- formato DATE
                    DATE(d.FechaProgramadaGR) AS doc_fec_prog_gr,
                    DATE(rd.fechaProgramada) AS rd_fec_prog,
                    d.RazonSocial AS doc_raz_soc,
                    d.CondicionPago AS doc_con_pag,
                    d.AgenciaTransporte AS doc_ag_trans,
                    d.Vendedor AS doc_vend,
                    d.ImporteME AS doc_imp_me,
                    d.PesoTotal AS doc_peso_tot,
                    rd.horaLlegada AS rd_hora_lleg,
                    rd.horaSalida AS rd_hora_sal,
                    d.Excepcion AS doc_excep,
                    r.id AS rut_id,
                    v.placa AS veh_placa,
                    estado.descripcion AS est_desc,
                    DATE(r.fechaProgramada) AS rut_fec_prog,
                    r.fechaInicio AS rut_fec_ini,
                    r.fechaRetorno AS rut_fec_ret,
                    CONCAT(chofer.displayName, ' ', chofer.lastName) AS chofer_nom_comp,
                    rd.observacion AS rd_obs,
                    d.Motivo AS doc_mot,
                    d.CantidadBultos AS doc_cant_bult
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
            WHERE
                DATE(r.fechaProgramada) = %(date_programs)s 
        """
       

        params = {
            "date_programs": date_programs,
        }

        logger.info(f"==>Obteniendo documentos de {date_programs} ")
        return self.db_connection.execute_query_dataframe(query, params)
