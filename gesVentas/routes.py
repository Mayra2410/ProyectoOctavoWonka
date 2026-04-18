from flask import render_template, request, redirect, url_for, flash, session
from . import gesVentas
from models import (
    db,
    Producto,
    Venta,
    OrdenProduccion,
    Cliente,
    PagoProveedor,
    DetalleVenta,
)
from datetime import datetime
from sqlalchemy import func
from utils import login_required

import subprocess
import os
from flask import send_file 
import csv
from io import StringIO
from flask import Response


@gesVentas.route("/gestion-ventas", methods=["GET", "POST"])
@login_required
def mostrar_ventas():
    hoy = datetime.now().date()

    ventas_pendientes = Venta.query.filter(Venta.estado == "PENDIENTE").all()
    for v in ventas_pendientes:
        quendan_ordenes = OrdenProduccion.query.filter(
            OrdenProduccion.lote.like(f"AUTO-{v.id_venta}-%"),
            OrdenProduccion.estado != "COMPLETADA",
        ).first()

        if not quendan_ordenes:
            v.estado = "COMPLETADA"

    db.session.commit()

    query = request.args.get("q")
    if query and query.isdigit():
        ventas = Venta.query.filter(Venta.id_venta == int(query)).all()
    else:
        ventas = Venta.query.order_by(Venta.fecha_venta.desc()).all()

    ingresos = (
        db.session.query(func.sum(Venta.total))
        .filter(
            func.date(Venta.fecha_venta) == hoy,
            Venta.estado.in_(["COMPLETADA", "ENTREGADA"]),
        )
        .scalar()
        or 0
    )

    egresos = (
        db.session.query(func.sum(PagoProveedor.monto))
        .filter(func.date(PagoProveedor.fecha_pago) == hoy)
        .scalar()
        or 0
    )

    utilidad = ingresos - egresos

    return render_template(
        "gesVentas/gestVentas.html",
        ventas=ventas,
        ingresos=ingresos,
        egresos=egresos,
        utilidad=utilidad,
        hoy=hoy,
    )


@gesVentas.route("/entregar-venta/<int:id>")
@login_required
def entregar_venta(id):
    venta = Venta.query.get_or_404(id)
    if venta.estado == "COMPLETADA":
        venta.estado = "ENTREGADA"  
        db.session.commit()
        flash(f"Venta #{id} marcada como ENTREGADA al cliente.", "success")
    else:
        flash(
            "No se puede entregar un producto que no ha terminado producción.",
            "warning",
        )
    return redirect(url_for("gesVentas.mostrar_ventas"))


@gesVentas.route("/cancelar-venta/<int:id>")
@login_required
def cancelar_venta(id):
    venta = Venta.query.get_or_404(id)
    OrdenProduccion.query.filter(OrdenProduccion.lote.like(f"AUTO-{id}-%")).delete(
        synchronize_session=False
    )

    venta.estado = "CANCELADA"
    db.session.commit()
    flash(f"Venta #{id} cancelada y logística revertida.", "warning")
    return redirect(url_for("gesVentas.mostrar_ventas"))


@gesVentas.route("/ver-ticket/<int:id>")
@login_required
def ver_ticket(id):
    venta = Venta.query.get_or_404(id)

    from models import OrdenProduccion

    orden = OrdenProduccion.query.filter(
        OrdenProduccion.lote.like(f"AUTO-{id}-%")
    ).first()

    productos_ticket = session.get("ultimo_carrito", [])

    if not productos_ticket:
        detalles = DetalleVenta.query.filter_by(venta_id=id).all()
        for d in detalles:
            prod = Producto.query.get(d.producto_id)
            productos_ticket.append(
                {
                    "nombre": prod.nombre,
                    "cantidad_cajas": d.cantidad,
                    "presentacion": getattr(prod, "presentacion", "Pieza"),
                    "subtotal": d.subtotal,
                }
            )

    ahorro = request.args.get("ahorro", 0)

    return render_template(
        "gesVentas/ticket.html",
        venta=venta,
        productos=productos_ticket,
        ahorro=ahorro,
        orden=orden,
    )


@gesVentas.route("/corte-caja")
@login_required
def corte_caja():
    hoy_dt = datetime.now()
    inicio_defecto = hoy_dt.replace(day=1).strftime("%Y-%m-%d")
    fin_defecto = hoy_dt.strftime("%Y-%m-%d")

    fecha_inicio = request.args.get("fecha_inicio", inicio_defecto)
    fecha_fin = request.args.get("fecha_fin", fin_defecto)

    ingresos = (
        db.session.query(func.sum(Venta.total))
        .filter(
            func.date(Venta.fecha_venta).between(fecha_inicio, fecha_fin),
            Venta.estado.in_(["COMPLETADA", "ENTREGADA"]),  # <--- SUMAMOS AMBOS ESTADOS
        )
        .scalar()
        or 0
    )

    egresos = (
        db.session.query(func.sum(PagoProveedor.monto))
        .filter(func.date(PagoProveedor.fecha_pago).between(fecha_inicio, fecha_fin))
        .scalar()
        or 0
    )

    reserva = float(ingresos) * 0.20
    utilidad = float(ingresos) - float(egresos) - reserva

    top_productos = (
        db.session.query(
            Producto.nombre, func.count(Venta.id_venta).label("total_ventas")
        )
        .join(DetalleVenta, Producto.id_producto == DetalleVenta.producto_id)
        .join(Venta, DetalleVenta.venta_id == Venta.id_venta)
        .filter(
            func.date(Venta.fecha_venta).between(fecha_inicio, fecha_fin),
            Venta.estado.in_(
                ["COMPLETADA", "ENTREGADA"]
            ),  
        )
        .group_by(Producto.nombre)
        .order_by(func.count(Venta.id_venta).desc())
        .limit(5)
        .all()
    )

    labels_prod = [p[0] for p in top_productos]
    values_prod = [int(p[1]) for p in top_productos]

    ventas_rango = (
        db.session.query(
            func.date(Venta.fecha_venta).label("dia"), func.sum(Venta.total)
        )
        .filter(
            func.date(Venta.fecha_venta).between(fecha_inicio, fecha_fin),
            Venta.estado.in_(
                ["COMPLETADA", "ENTREGADA"]
            ),  
        )
        .group_by(func.date(Venta.fecha_venta))
        .order_by(func.date(Venta.fecha_venta))
        .all()
    )

    labels_dias = [v[0].strftime("%d/%m") for v in ventas_rango]
    values_dias = [float(v[1]) for v in ventas_rango]

    labels_rating, values_rating = [], []
    try:
        from clientes.routesC import get_mongo_db

        db_mongo = get_mongo_db()
        pipeline = [
            {
                "$group": {
                    "_id": "$nombre_producto",
                    "promedio": {"$avg": "$calificacion"},
                }
            },
            {"$sort": {"promedio": -1}},
        ]
        stats = list(db_mongo.resenas_productos.aggregate(pipeline))
        labels_rating = [s["_id"] for s in stats]
        values_rating = [round(s["promedio"], 2) for s in stats]
    except:
        pass

    historial_cortes = []
    try:
        historial_cortes = db.session.execute(
            db.text("SELECT * FROM cortes_caja ORDER BY fecha_registro DESC LIMIT 10")
        ).all()
    except:
        pass

    return render_template(
        "gesVentas/corte.html",
        ingresos=ingresos,
        egresos=egresos,
        reserva=reserva,
        utilidad=utilidad,
        hoy=hoy_dt.strftime("%d/%m/%Y"),
        fecha_inicio=fecha_inicio,
        fecha_fin=fecha_fin,
        labels_prod=labels_prod,
        values_prod=values_prod,
        labels_dias=labels_dias,
        values_dias=values_dias,
        labels_rating=labels_rating,
        values_rating=values_rating,
        historial_cortes=historial_cortes,
    )


@gesVentas.route("/guardar-corte", methods=["POST"])
@login_required
def guardar_corte():
    try:
        sql = """INSERT INTO cortes_caja (fecha_inicio, fecha_fin, total_ingresos, total_egresos, monto_reserva, utilidad_neta)
                 VALUES (:fi, :ff, :ing, :egr, :res, :util)"""
        db.session.execute(
            db.text(sql),
            {
                "fi": request.form.get("f_inicio"),
                "ff": request.form.get("f_fin"),
                "ing": request.form.get("ingresos"),
                "egr": request.form.get("egresos"),
                "res": request.form.get("reserva"),
                "util": request.form.get("utilidad"),
            },
        )
        db.session.commit()
        flash("¡Ciclo financiero archivado con éxito!", "success")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al archivar: {e}", "danger")
    return redirect(url_for("gesVentas.corte_caja"))


@gesVentas.route("/respaldar-db", methods=["POST"])
@login_required
def respaldar_db():
    db_user = "wonka_app"
    db_pass = "Wonka2026*"
    db_name = "wonka"
    db_host = "127.0.0.1"

    ruta_mysql = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"

    fecha_str = datetime.now().strftime('%Y%m%d_%H%M%S')
    nombre_archivo = f"backup_wonka_{fecha_str}.sql"
    ruta_backups = os.path.join(os.getcwd(), 'backups')
    
    if not os.path.exists(ruta_backups):
        os.makedirs(ruta_backups)
        
    ruta_completa = os.path.join(ruta_backups, nombre_archivo)

    try:
        comando = f'"{ruta_mysql}" -h {db_host} -u {db_user} -p"{db_pass}" {db_name} > "{ruta_completa}"'
        
        subprocess.run(comando, shell=True, check=True, capture_output=True, text=True)

        flash(f"¡Éxito! Respaldo guardado en la carpeta del proyecto.", "success")
        
    except subprocess.CalledProcessError as e:
        flash(f"Error de ejecución: Asegúrate de que la ruta '{ruta_mysql}' sea correcta en tu PC.", "danger")
    except Exception as e:
        flash(f"Error inesperado: {str(e)}", "danger")

    return redirect(url_for("gesVentas.corte_caja"))



@gesVentas.route("/exportar-cortes")
@login_required
def exportar_cortes():
    # 1. Consultar los datos del historial (igual que en tu vista de corte)
    sql = "SELECT fecha_inicio, fecha_fin, total_ingresos, total_egresos, monto_reserva, utilidad_neta, fecha_registro FROM cortes_caja ORDER BY fecha_registro DESC"
    resultado = db.session.execute(db.text(sql)).all()

    # 2. Crear el archivo CSV en memoria
    def generate():
        data = StringIO()
        writer = csv.writer(data)
        
        # Escribir encabezados
        writer.writerow(['Fecha Inicio', 'Fecha Fin', 'Ingresos', 'Egresos', 'Reserva', 'Utilidad Neta', 'Fecha Registro'])
        yield data.getvalue()
        data.seek(0)
        data.truncate(0)

        # Escribir filas de datos
        for fila in resultado:
            writer.writerow([
                fila[0], fila[1], fila[2], fila[3], fila[4], fila[5], fila[6]
            ])
            yield data.getvalue()
            data.seek(0)
            data.truncate(0)

    # 3. Retornar el archivo como una descarga
    nombre_archivo = f"reporte_wonka_{datetime.now().strftime('%Y%m%d')}.csv"
    return Response(
        generate(),
        mimetype='text/csv',
        headers={"Content-disposition": f"attachment; filename={nombre_archivo}"}
    )