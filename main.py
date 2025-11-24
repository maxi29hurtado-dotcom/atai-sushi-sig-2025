import sys
import pymysql
import csv 
import os 
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QWidget, QVBoxLayout, QLabel, QTableWidgetItem, QCheckBox, QFileDialog, QListWidgetItem, QPushButton
from PyQt5.uic import loadUi
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QDate, QCoreApplication, QDateTime 


# --- FUNCIÓN AUXILIAR DE CONSULTA (Reusable) ---
def ejecutar_consulta_db(conexion, query, params=None, fetch=False):
    """Función auxiliar para ejecutar consultas SQL y manejar errores."""
    cursor = None
    try:
        cursor = conexion.cursor()
        cursor.execute(query, params)
        conexion.commit()
        if fetch:
            return True, cursor.fetchall()
        return True, cursor.lastrowid
    except pymysql.MySQLError as e:
        QMessageBox.critical(None, "Error de Base de Datos", f"Operación fallida:\n{str(e)}")
        conexion.rollback()
        return False, str(e)
    except Exception as e:
        QMessageBox.critical(None, "Error General", f"Error inesperado:\n{str(e)}")
        conexion.rollback()
        return False, str(e)
    finally:
        if cursor:
            cursor.close()



class EERRWindow(QMainWindow):
    """Módulo 4.1: Reporte de Estado de Resultados (EERR)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Reporte_EERR.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("4.1 Estado de Resultados (EERR)")
        self.showMaximized()
        
        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.boton_generar_reporte.clicked.connect(self.generar_eerr)
        
        hoy = QDate.currentDate()
        self.dateEdit_inicio.setDate(QDate(hoy.year(), hoy.month(), 1))
        self.dateEdit_fin.setDate(hoy)
        
        self.tabla_eerr.setRowCount(5)
        conceptos = ["Ingresos por Ventas", "(-) Costo de Mercadería Vendida (CMV)", "(=) Margen Bruto", "(-) Gastos Operacionales Fijos", "(=) Utilidad Neta"]
        for i, concepto in enumerate(conceptos):
            item = QTableWidgetItem(concepto)
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            self.tabla_eerr.setItem(i, 0, item)
            if self.tabla_eerr.item(i, 1) is None:
                self.tabla_eerr.setItem(i, 1, QTableWidgetItem("$ 0"))
        
        self.generar_eerr()

    def volver_menu(self):
        self.parent_window.show()
        self.hide()
        
    def generar_eerr(self):
        fecha_inicio = self.dateEdit_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.dateEdit_fin.date().toString("yyyy-MM-dd")
        
        query_ingresos = "SELECT COALESCE(SUM(total_venta), 0) FROM ventas WHERE fecha_venta BETWEEN %s AND %s"
        ok_i, ingresos_data = ejecutar_consulta_db(self.conexion, query_ingresos, (fecha_inicio, fecha_fin), fetch=True)
        ingresos_totales = float(ingresos_data[0][0]) if ok_i and ingresos_data else 0

        query_cmv = "SELECT COALESCE(SUM(cantidad * costo_unitario_calculado), 0) FROM ventas WHERE fecha_venta BETWEEN %s AND %s"
        ok_cmv, cmv_data = ejecutar_consulta_db(self.conexion, query_cmv, (fecha_inicio, fecha_fin), fetch=True)
        cmv_total = float(cmv_data[0][0]) if ok_cmv and cmv_data else 0
        
        query_gastos = "SELECT COALESCE(SUM(monto), 0) FROM gastos_operativos WHERE fecha_gasto BETWEEN %s AND %s"
        ok_g, gastos_data = ejecutar_consulta_db(self.conexion, query_gastos, (fecha_inicio, fecha_fin), fetch=True)
        gastos_fijos = float(gastos_data[0][0]) if ok_g and gastos_data else 0

        margen_bruto = ingresos_totales - cmv_total
        utilidad_neta = margen_bruto - gastos_fijos

        self.tabla_eerr.item(0, 1).setText(f"${ingresos_totales:,.2f}"); self.tabla_eerr.item(0, 1).setForeground(QBrush(QColor(46, 204, 113)))
        self.tabla_eerr.item(1, 1).setText(f"${cmv_total:,.2f}"); self.tabla_eerr.item(1, 1).setForeground(QBrush(QColor(231, 76, 60)))
        self.tabla_eerr.item(2, 1).setText(f"${margen_bruto:,.2f}"); self.tabla_eerr.item(2, 1).setForeground(QBrush(QColor(52, 152, 219)))
        self.tabla_eerr.item(3, 1).setText(f"${gastos_fijos:,.2f}"); self.tabla_eerr.item(3, 1).setForeground(QBrush(QColor(231, 76, 60)))
        self.tabla_eerr.item(4, 1).setText(f"${utilidad_neta:,.2f}")
        
        if utilidad_neta < 0:
            self.tabla_eerr.item(4, 1).setBackground(QColor(255, 230, 230)); self.tabla_eerr.item(4, 1).setForeground(QBrush(QColor(231, 76, 60)))
        else:
            self.tabla_eerr.item(4, 1).setBackground(QColor(230, 255, 230)); self.tabla_eerr.item(4, 1).setForeground(QBrush(QColor(46, 204, 113)))


class MargenWindow(QMainWindow):
    """Módulo 4.2: Análisis de Margen y Top Ventas."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Reporte_Margen_Ventas.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("4.2 Análisis de Margen y Top Ventas")
        self.showMaximized()

        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.boton_generar_reporte.clicked.connect(self.generar_reporte_margen)
        
        hoy = QDate.currentDate()
        self.dateEdit_inicio.setDate(QDate(hoy.year(), hoy.month(), 1))
        self.dateEdit_fin.setDate(hoy)
        
        self.tabla_margen_ventas.setEditTriggers(self.tabla_margen_ventas.NoEditTriggers)
        self.tabla_margen_ventas.setSelectionBehavior(self.tabla_margen_ventas.SelectRows)
        
        self.generar_reporte_margen()

    def volver_menu(self):
        self.parent_window.show()
        self.hide()

    def generar_reporte_margen(self):
        fecha_inicio = self.dateEdit_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.dateEdit_fin.date().toString("yyyy-MM-dd")

        query = """
        SELECT 
            p.nombre AS Producto,
            SUM(v.cantidad) AS Unidades_Vendidas,
            SUM(v.total_venta) AS Ingreso_Total,
            SUM(v.cantidad * v.costo_unitario_calculado) AS CMV_Total
        FROM ventas v
        JOIN productos p ON v.id_producto = p.id_producto
        WHERE v.fecha_venta BETWEEN %s AND %s
        GROUP BY p.nombre
        ORDER BY Unidades_Vendidas DESC;
        """
        ok, resultados = ejecutar_consulta_db(self.conexion, query, (fecha_inicio, fecha_fin), fetch=True)
        if not ok: self.tabla_margen_ventas.setRowCount(0); return

        self.tabla_margen_ventas.setRowCount(len(resultados))
        
        for fila, datos in enumerate(resultados):
            producto, unidades, ingreso, cmv = datos
            ranking = fila + 1
            ingreso, cmv = float(ingreso), float(cmv)
            
            margen_bruto = ingreso - cmv
            margen_porcentual = (margen_bruto / ingreso) * 100 if ingreso > 0 else 0
            
            self.tabla_margen_ventas.setItem(fila, 0, QTableWidgetItem(f"#{ranking}"))
            self.tabla_margen_ventas.setItem(fila, 1, QTableWidgetItem(producto))
            self.tabla_margen_ventas.setItem(fila, 2, QTableWidgetItem(f"{unidades:,.0f}"))
            self.tabla_margen_ventas.setItem(fila, 3, QTableWidgetItem(f"${ingreso:,.0f}"))
            self.tabla_margen_ventas.setItem(fila, 4, QTableWidgetItem(f"${cmv:,.2f}"))
            
            item_margen_clp = QTableWidgetItem(f"${margen_bruto:,.2f}")
            self.tabla_margen_ventas.setItem(fila, 5, item_margen_clp)
            
            item_margen_pct = QTableWidgetItem(f"{margen_porcentual:,.1f}%")
            
            if margen_porcentual < 40:
                item_margen_pct.setBackground(QColor(255, 230, 230))
                item_margen_pct.setForeground(QBrush(QColor(231, 76, 60)))
            
            self.tabla_margen_ventas.setItem(fila, 6, item_margen_pct)

        QMessageBox.information(self, "Reporte Generado", f"Reporte de Margen y Top Ventas generado para {len(resultados)} productos.")


class KPIsWindow(QMainWindow):
    """Módulo 4.3: KPIs Operacionales (Quiebre, Rotación, Pérdida)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Reporte_KPIs.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("4.3 KPIs Operacionales de Inventario")
        self.showMaximized()

        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.boton_generar_reporte.clicked.connect(self.generar_kpis)
        
        hoy = QDate.currentDate()
        self.dateEdit_inicio.setDate(QDate(hoy.year(), hoy.month(), 1))
        self.dateEdit_fin.setDate(hoy)
        
        self.generar_kpis()

    def volver_menu(self):
        self.parent_window.show()
        self.hide()

    def generar_kpis(self):
        fecha_inicio = self.dateEdit_inicio.date().toString("yyyy-MM-dd")
        fecha_fin = self.dateEdit_fin.date().toString("yyyy-MM-dd")

        # TASA DE QUIEBRE DE STOCK 
        query_criticos = "SELECT COUNT(id_insumo) FROM insumos WHERE activo = TRUE AND stock_actual <= stock_minimo"
        ok_crit, criticos_data = ejecutar_consulta_db(self.conexion, query_criticos, fetch=True)
        criticos = float(criticos_data[0][0]) if ok_crit and criticos_data else 0

        query_total = "SELECT COUNT(id_insumo) FROM insumos WHERE activo = TRUE"
        ok_total, total_data = ejecutar_consulta_db(self.conexion, query_total, fetch=True)
        total_insumos = float(total_data[0][0]) if ok_total and total_data else 1

        tasa_quiebre = (criticos / total_insumos) * 100 if total_insumos > 0 else 0
        
        self.label_kpi_quiebre_valor.setText(f"{tasa_quiebre:,.1f}%")
        self.label_kpi_quiebre_descripcion.setText(f"Basado en {criticos:,.0f} de {total_insumos:,.0f} insumos críticos actualmente.")


        #  ROTACIÓN DE INVENTARIO 
        query_cmv = "SELECT COALESCE(SUM(cantidad * costo_unitario_calculado), 0) FROM ventas WHERE fecha_venta BETWEEN %s AND %s"
        ok_cmv, cmv_data = ejecutar_consulta_db(self.conexion, query_cmv, (fecha_inicio, fecha_fin), fetch=True)
        cmv_periodo = float(cmv_data[0][0]) if ok_cmv and cmv_data else 0

        query_inv_final = "SELECT COALESCE(SUM(stock_actual * costo_promedio), 0) FROM insumos WHERE activo = TRUE"
        ok_f, inv_final_data = ejecutar_consulta_db(self.conexion, query_inv_final, fetch=True)
        inv_final = float(inv_final_data[0][0]) if ok_f and inv_final_data else 0
        
        inv_promedio = inv_final 
        
        rotacion = cmv_periodo / inv_promedio if inv_promedio > 0 else 0
        
        self.label_kpi_rotacion_valor.setText(f"{rotacion:,.2f} veces")
        self.label_kpi_rotacion_descripcion.setText(f"Rotación calculada sobre CMV total (${cmv_periodo:,.0f}) e Inventario Final estimado (${inv_final:,.0f}).")


        #  3. PORCENTAJE DE PÉRDIDA 
        query_perdidas = """
        SELECT COALESCE(SUM(m.cantidad * i.costo_promedio), 0)
        FROM movimientos_inventario m
        JOIN insumos i ON m.id_insumo = i.id_insumo
        WHERE m.tipo_movimiento IN ('perdida', 'ajuste')
        AND m.fecha_movimiento BETWEEN %s AND %s
        """
        ok_p, perdidas_data = ejecutar_consulta_db(self.conexion, query_perdidas, (fecha_inicio, fecha_fin), fetch=True)
        valor_perdidas = float(perdidas_data[0][0]) if ok_p and perdidas_data else 0

        query_compras = """
        SELECT COALESCE(SUM(cantidad * costo_unitario), 0)
        FROM movimientos_inventario
        WHERE tipo_movimiento = 'entrada'
        AND fecha_movimiento BETWEEN %s AND %s
        """
        ok_c, compras_data = ejecutar_consulta_db(self.conexion, query_compras, (fecha_inicio, fecha_fin), fetch=True)
        valor_compras = float(compras_data[0][0]) if ok_c and compras_data else 1

        porc_perdida = (valor_perdidas / valor_compras) * 100 if valor_compras > 0 else 0
        
        self.label_kpi_perdida_valor.setText(f"{porc_perdida:,.1f}%")
        self.label_kpi_perdida_descripcion.setText(f"Pérdidas valoradas en ${valor_perdidas:,.0f} respecto a las Compras totales (${valor_compras:,.0f}).")

        QMessageBox.information(self, "Reporte Generado", "Reporte de KPIs Operacionales generado.")


class ReportesWindow(QMainWindow):
    """Módulo 4 (Submenú): Carga el Submenú de Reportes."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Submenu_Reportes.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("Módulo 4: Reportes Administrativos y Financieros")
        self.boton_estado_resultados.clicked.connect(self.ir_a_eerr)
        self.boton_analisis_margen.clicked.connect(self.ir_a_margen)
        self.boton_kpis_operacionales.clicked.connect(self.ir_a_kpis)
        self.boton_volver_menu.clicked.connect(self.volver_menu)
        self.show()

    def volver_menu(self): self.parent_window.show(); self.hide()
    def navegar_a_submodulo(self, SubmoduloClase): self.modulo_actual = SubmoduloClase(self, self.conexion); self.hide()
    def ir_a_eerr(self): self.navegar_a_submodulo(EERRWindow)
    def ir_a_margen(self): self.navegar_a_submodulo(MargenWindow)
    def ir_a_kpis(self): self.navegar_a_submodulo(KPIsWindow)




class ProveedoresWindow(QMainWindow):
    """Módulo 1.3: Gestión CRUD de la tabla Proveedores."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Proveedores.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("1.3 Gestión de Proveedores")
        self.showMaximized()
        self.proveedor_seleccionado_id = None
        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.boton_agregar.clicked.connect(self.agregar_proveedor)
        self.boton_modificar.clicked.connect(self.modificar_proveedor)
        self.boton_eliminar.clicked.connect(self.inactivar_proveedor)
        self.tabla_proveedores.cellClicked.connect(self.seleccionar_proveedor)
        self.cargar_datos_proveedores()

    def volver_menu(self): self.parent_window.show(); self.hide()
    def limpiar_campos(self):
        self.entrada_nombre.clear(); self.entrada_contacto.clear(); self.entrada_telefono.clear()
        self.checkbox_activo.setChecked(True); self.proveedor_seleccionado_id = None
        self.boton_modificar.setEnabled(False); self.boton_eliminar.setEnabled(False)
    def cargar_datos_proveedores(self):
        query = "SELECT id_proveedor, nombre, contacto, telefono, activo FROM proveedores ORDER BY activo DESC, nombre ASC"
        ok, resultados = ejecutar_consulta_db(self.conexion, query, fetch=True)
        if not ok: return
        self.tabla_proveedores.setRowCount(len(resultados)); self.tabla_proveedores.setColumnCount(5)
        self.tabla_proveedores.setHorizontalHeaderLabels(["ID", "Nombre", "Contacto", "Teléfono", "Activo"])
        for fila, datos in enumerate(resultados):
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor)); item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                if col == 4:
                    estado_texto = "🟢 Sí" if valor == 1 else "🔴 No"; item.setText(estado_texto)
                    if valor == 0: item.setBackground(QColor(255, 200, 200))
                self.tabla_proveedores.setItem(fila, col, item)
        self.limpiar_campos()
    def seleccionar_proveedor(self, fila, columna):
        try:
            self.proveedor_seleccionado_id = int(self.tabla_proveedores.item(fila, 0).text())
            self.entrada_nombre.setText(self.tabla_proveedores.item(fila, 1).text()); self.entrada_contacto.setText(self.tabla_proveedores.item(fila, 2).text())
            self.entrada_telefono.setText(self.tabla_proveedores.item(fila, 3).text())
            activo_str = self.tabla_proveedores.item(fila, 4).text(); is_activo = "Sí" in activo_str; self.checkbox_activo.setChecked(is_activo)
            self.boton_modificar.setEnabled(True); self.boton_eliminar.setEnabled(True); self.boton_eliminar.setText("🗑️ INACTIVAR" if is_activo else "🟢 ACTIVAR")
        except Exception as e: QMessageBox.critical(self, "Error de Selección", f"Error al seleccionar fila: {e}"); self.limpiar_campos()
    def agregar_proveedor(self):
        nombre = self.entrada_nombre.text().strip(); contacto = self.entrada_contacto.text().strip(); telefono = self.entrada_telefono.text().strip(); activo = self.checkbox_activo.isChecked()
        if not nombre: QMessageBox.warning(self, "Advertencia", "El nombre del proveedor es obligatorio."); return
        query = "INSERT INTO proveedores (nombre, contacto, telefono, activo) VALUES (%s, %s, %s, %s)"; ok, _ = ejecutar_consulta_db(self.conexion, query, (nombre, contacto, telefono, activo))
        if ok: QMessageBox.information(self, "Éxito", "Proveedor agregado correctamente."); self.cargar_datos_proveedores()
    def modificar_proveedor(self):
        if self.proveedor_seleccionado_id is None: QMessageBox.warning(self, "Advertencia", "Seleccione un proveedor para modificar."); return
        nombre = self.entrada_nombre.text().strip(); contacto = self.entrada_contacto.text().strip(); telefono = self.entrada_telefono.text().strip(); activo = self.checkbox_activo.isChecked()
        if not nombre: QMessageBox.warning(self, "Advertencia", "El nombre del proveedor es obligatorio."); return
        query = "UPDATE proveedores SET nombre = %s, contacto = %s, telefono = %s, activo = %s WHERE id_proveedor = %s"
        ok, _ = ejecutar_consulta_db(self.conexion, query, (nombre, contacto, telefono, activo, self.proveedor_seleccionado_id))
        if ok: QMessageBox.information(self, "Éxito", "Proveedor modificado correctamente."); self.cargar_datos_proveedores()
    def inactivar_proveedor(self):
        if self.proveedor_seleccionado_id is None: QMessageBox.warning(self, "Advertencia", "Seleccione un proveedor."); return
        estado_actual = self.checkbox_activo.isChecked(); nuevo_estado = not estado_actual
        accion = "ACTIVADO" if nuevo_estado else "INACTIVADO"
        confirmacion = QMessageBox.question(self, "Confirmar Cambio de Estado", f"¿Desea {accion.lower()} el proveedor {self.entrada_nombre.text()}?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            query = "UPDATE proveedores SET activo = %s WHERE id_proveedor = %s"; ok, _ = ejecutar_consulta_db(self.conexion, query, (nuevo_estado, self.proveedor_seleccionado_id))
            if ok: QMessageBox.information(self, "Éxito", f"Proveedor {accion} correctamente."); self.cargar_datos_proveedores()


class RecetasWindow(QMainWindow):
    """Módulo 1.2: Definición de Recetas y Cálculo de CMV Base."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Recetas.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("1.2 Definición de Recetas y CMV")
        self.showMaximized()
        self.producto_seleccionado_id = None
        self.productos_map = {}
        self.insumos_map = {}
        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.combo_productos.currentIndexChanged.connect(self.cargar_receta_y_cmv)
        self.boton_agregar_insumo.clicked.connect(self.agregar_o_modificar_insumo_receta)
        self.boton_eliminar_insumo.clicked.connect(self.eliminar_insumo_receta)
        self.cargar_comboboxes(); self.tabla_receta.setEditTriggers(self.tabla_receta.NoEditTriggers)

    def volver_menu(self): self.parent_window.show(); self.hide()

    def cargar_comboboxes(self):
        query_productos = "SELECT id_producto, nombre, precio_venta FROM productos WHERE activo = TRUE ORDER BY nombre"
        ok_p, productos = ejecutar_consulta_db(self.conexion, query_productos, fetch=True)
        if ok_p:
            self.combo_productos.clear(); self.productos_map = {}
            for id_p, nombre, precio in productos: self.productos_map[id_p] = {'nombre': nombre, 'precio': float(precio)}; self.combo_productos.addItem(f"{id_p} - {nombre}")
            if self.combo_productos.count() > 0: self.cargar_receta_y_cmv()
        query_insumos = "SELECT id_insumo, nombre, unidad_medida, costo_promedio FROM insumos WHERE activo = TRUE ORDER BY nombre"
        ok_i, insumos = ejecutar_consulta_db(self.conexion, query_insumos, fetch=True)
        if ok_i:
            self.combo_insumo_nuevo.clear(); self.insumos_map = {}
            for id_i, nombre, unidad, costo in insumos: self.insumos_map[id_i] = {'nombre': nombre, 'unidad': unidad, 'costo_promedio': float(costo)}; self.combo_insumo_nuevo.addItem(f"{id_i} - {nombre} ({unidad})")

    def calcular_cmv_y_margen(self, receta_actual):
        cmv_total = sum(float(insumo[4]) for insumo in receta_actual)
        if self.producto_seleccionado_id not in self.productos_map: return
        id_p = self.producto_seleccionado_id; precio_venta = self.productos_map[id_p]['precio']; margen = precio_venta - cmv_total
        self.label_precio_venta_valor.setText(f"Precio Venta: $ {precio_venta:,.0f}"); self.label_cmv_actual.setText(f"CMV Estimado: $ {cmv_total:,.2f}")
        self.label_margen_contribucion.setText(f"Margen Contribución: $ {margen:,.2f}")
        if margen < precio_venta * 0.40: self.label_margen_contribucion.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else: self.label_margen_contribucion.setStyleSheet("color: #2ecc71; font-weight: bold;")

    def cargar_receta_y_cmv(self):
        item_texto = self.combo_productos.currentText()
        if not item_texto: self.tabla_receta.setRowCount(0); return
        try: self.producto_seleccionado_id = int(item_texto.split(' - ')[0])
        except ValueError: self.tabla_receta.setRowCount(0); return
        query = "SELECT r.id_receta, r.id_insumo, i.nombre, r.cantidad_requerida, i.unidad_medida, i.costo_promedio FROM recetas r JOIN insumos i ON r.id_insumo = i.id_insumo WHERE r.id_producto = %s ORDER BY i.nombre"
        ok, resultados = ejecutar_consulta_db(self.conexion, query, (self.producto_seleccionado_id,), fetch=True)
        if not ok: self.tabla_receta.setRowCount(0); return
        self.tabla_receta.setRowCount(len(resultados)); receta_actual_data = [] 
        for fila, datos in enumerate(resultados):
            id_receta, id_insumo, nombre, cantidad, unidad, costo_promedio = datos
            costo_cmv = float(cantidad) * float(costo_promedio)
            self.tabla_receta.setItem(fila, 0, QTableWidgetItem(str(id_receta))); self.tabla_receta.setItem(fila, 1, QTableWidgetItem(str(id_insumo)))
            self.tabla_receta.setItem(fila, 2, QTableWidgetItem(nombre)); self.tabla_receta.setItem(fila, 3, QTableWidgetItem(f"{float(cantidad):.3f}"))
            self.tabla_receta.setItem(fila, 4, QTableWidgetItem(unidad)); self.tabla_receta.setItem(fila, 5, QTableWidgetItem(f"$ {costo_cmv:,.2f}"))
            receta_actual_data.append((id_insumo, nombre, cantidad, unidad, costo_cmv))
        self.calcular_cmv_y_margen(receta_actual_data)
    def agregar_o_modificar_insumo_receta(self):
        if self.producto_seleccionado_id is None: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un producto (Roll) primero."); return
        insumo_texto = self.combo_insumo_nuevo.currentText()
        if not insumo_texto: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un insumo."); return
        try: insumo_id = int(insumo_texto.split(' - ')[0]); cantidad_requerida = float(self.entrada_cantidad_requerida.text())
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "Cantidad debe ser un número decimal válido."); return
        if cantidad_requerida <= 0: QMessageBox.warning(self, "Advertencia", "La cantidad requerida debe ser mayor a cero."); return
        query_check = "SELECT id_receta FROM recetas WHERE id_producto = %s AND id_insumo = %s"
        ok, resultado_check = ejecutar_consulta_db(self.conexion, query_check, (self.producto_seleccionado_id, insumo_id), fetch=True)
        if not ok: return
        if resultado_check: query = "UPDATE recetas SET cantidad_requerida = %s WHERE id_receta = %s"; params = (cantidad_requerida, resultado_check[0][0]); mensaje = f"Receta actualizada: Cantidad de {self.insumos_map[insumo_id]['nombre']} modificada."
        else: query = "INSERT INTO recetas (id_producto, id_insumo, cantidad_requerida) VALUES (%s, %s, %s)"; params = (self.producto_seleccionado_id, insumo_id, cantidad_requerida); mensaje = f"Receta actualizada: {self.insumos_map[insumo_id]['nombre']} agregado."
        ok_op, _ = ejecutar_consulta_db(self.conexion, query, params)
        if ok_op: QMessageBox.information(self, "Éxito", mensaje); self.entrada_cantidad_requerida.clear(); self.cargar_receta_y_cmv()
        else: QMessageBox.critical(self, "Error de DB", "No se pudo actualizar la receta.")
    def eliminar_insumo_receta(self):
        selected_rows = self.tabla_receta.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Advertencia", "Seleccione un insumo de la receta para eliminar."); return
        fila_seleccionada = selected_rows[0].row(); id_receta = self.tabla_receta.item(fila_seleccionada, 0).text()
        nombre_insumo = self.tabla_receta.item(fila_seleccionada, 2).text()
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Desea eliminar '{nombre_insumo}' de la receta actual?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            query = "DELETE FROM recetas WHERE id_receta = %s"; ok, _ = ejecutar_consulta_db(self.conexion, query, (id_receta,))
            if ok: QMessageBox.information(self, "Éxito", f"'{nombre_insumo}' eliminado de la receta."); self.cargar_receta_y_cmv()


class ControlStockWindow(QMainWindow):
    """Módulo 1.1: Visualización y Gestión de Entradas/Salidas/Pérdidas de Stock."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Control_Stock.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("1.1 Control de Stock y Alertas")
        self.showMaximized()
        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.boton_recargar_tabla.clicked.connect(self.cargar_datos_stock)
        self.boton_registrar_compra.clicked.connect(self.registrar_compra)
        self.boton_registrar_perdida.clicked.connect(self.registrar_perdida)
        self.combo_filtro_alertas.currentIndexChanged.connect(self.cargar_datos_stock)
        self.cargar_datos_stock()

    def volver_menu(self): self.parent_window.show(); self.hide()
    
    def cargar_datos_stock(self):
        query = """
        SELECT i.id_insumo, i.nombre, i.unidad_medida, i.stock_actual, i.stock_minimo, 
               i.costo_promedio, p.nombre AS proveedor_principal, i.stock_actual <= i.stock_minimo AS es_critico
        FROM insumos i LEFT JOIN proveedores p ON i.id_proveedor_principal = p.id_proveedor
        WHERE i.activo = TRUE
        """
        filtro = self.combo_filtro_alertas.currentText()
        if 'Críticos' in filtro or 'Bajo Stock' in filtro: query += " AND i.stock_actual <= i.stock_minimo"
        elif 'Suficiente' in filtro: query += " AND i.stock_actual > i.stock_minimo"
        ok, resultados = ejecutar_consulta_db(self.conexion, query, fetch=True)
        if not ok: self.tabla_stock_insumos.setRowCount(0); return
        columnas = ["ID", "Insumo", "Unidad", "Stock Actual", "Stock Mínimo", "Costo Promedio (CLP)", "Proveedor Principal", "Estado"]
        self.tabla_stock_insumos.setRowCount(len(resultados)); self.tabla_stock_insumos.setColumnCount(len(columnas)); self.tabla_stock_insumos.setHorizontalHeaderLabels(columnas)
        self.lista_alertas.clear(); insumos_en_alerta = []; insumo_nombres = {}
        for fila, datos in enumerate(resultados):
            insumo_id, insumo_nombre, unidad, stock_actual, stock_minimo, costo_promedio, proveedor, es_critico = datos
            stock_actual, stock_minimo = float(stock_actual), float(stock_minimo)
            insumo_nombres[insumo_id] = insumo_nombre
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor)); item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                if es_critico:
                    item.setBackground(QColor(255, 230, 230))
                    if col == 7:
                        estado_texto = "🚨 SIN STOCK" if stock_actual <= 0 else "⚠️ CRÍTICO"; item.setText(estado_texto)
                        if stock_actual <= stock_minimo:
                            tipo = "SIN STOCK" if stock_actual <= 0 else "CRÍTICO"; alerta_msg = f"⚠️ {insumo_nombre} (ID {insumo_id}): {stock_actual:.2f} {unidad}. ¡{tipo}!"; insumos_en_alerta.append(alerta_msg)
                elif col == 7: item.setText("🟢 OK")
                if col == 5: item.setText(f"${float(valor):,.2f}")
                if col == 3 or col == 4: item.setText(f"{float(valor):.2f}")
                self.tabla_stock_insumos.setItem(fila, col, item)
        self.lista_alertas.addItems(insumos_en_alerta); self.combo_insumo_compra.clear(); self.combo_insumo_perdida.clear()
        insumo_lista_formato = [f"{id} - {nombre}" for id, nombre in insumo_nombres.items()]
        self.combo_insumo_compra.addItems(insumo_lista_formato); self.combo_insumo_perdida.addItems(insumo_lista_formato)
        QMessageBox.information(self, "Información", f"Se cargaron {len(resultados)} insumos y {len(insumos_en_alerta)} alertas activas.")

    def registrar_compra(self):
        insumo_seleccionado = self.combo_insumo_compra.currentText()
        if not insumo_seleccionado: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un insumo."); return
        try: insumo_id = int(insumo_seleccionado.split(' - ')[0]); cantidad = float(self.entrada_cantidad_compra.text()); costo_unitario = float(self.entrada_costo_unitario.text())
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "Cantidad y Costo deben ser números válidos."); return
        if cantidad <= 0 or costo_unitario <= 0: QMessageBox.warning(self, "Advertencia", "Cantidad y Costo Unitario deben ser mayores a cero."); return
        query_actual = "SELECT stock_actual, costo_promedio FROM insumos WHERE id_insumo = %s"
        ok, datos_actuales = ejecutar_consulta_db(self.conexion, query_actual, (insumo_id,), fetch=True)
        if not ok or not datos_actuales: return
        stock_actual, costo_promedio_actual = float(datos_actuales[0][0]), float(datos_actuales[0][1])
        costo_total_antiguo = stock_actual * costo_promedio_actual; costo_total_nuevo = cantidad * costo_unitario
        stock_total_nuevo = stock_actual + cantidad
        nuevo_costo_promedio = (costo_total_antiguo + costo_total_nuevo) / stock_total_nuevo if stock_total_nuevo > 0 else costo_unitario 
        try:
            cursor = self.conexion.cursor()
            query_movimiento = "INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, costo_unitario, motivo) VALUES (%s, 'entrada', %s, %s, 'Compra registrada')"
            cursor.execute(query_movimiento, (insumo_id, cantidad, costo_unitario))
            query_insumo_update = "UPDATE insumos SET stock_actual = %s, costo_promedio = %s WHERE id_insumo = %s"
            cursor.execute(query_insumo_update, (stock_total_nuevo, nuevo_costo_promedio, insumo_id))
            self.conexion.commit()
            QMessageBox.information(self, "Éxito", "Compra registrada y costo promedio actualizado.")
            self.cargar_datos_stock(); self.entrada_cantidad_compra.clear(); self.entrada_costo_unitario.clear()
        except pymysql.MySQLError as e: QMessageBox.critical(self, "Error de DB", f"Fallo al registrar la compra:\n{str(e)}"); self.conexion.rollback()

    def registrar_perdida(self):
        insumo_seleccionado = self.combo_insumo_perdida.currentText()
        if not insumo_seleccionado: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un insumo."); return
        try: insumo_id = int(insumo_seleccionado.split(' - ')[0]); cantidad_perdida = float(self.entrada_cantidad_perdida.text()); motivo = self.entrada_motivo_perdida.text()
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "La cantidad debe ser un número válido."); return
        if cantidad_perdida <= 0: QMessageBox.warning(self, "Advertencia", "La cantidad de pérdida debe ser mayor a cero."); return
        if not motivo: QMessageBox.warning(self, "Advertencia", "Debe especificar un motivo para la pérdida."); return
        query_actual = "SELECT stock_actual FROM insumos WHERE id_insumo = %s"
        ok, datos_actuales = ejecutar_consulta_db(self.conexion, query_actual, (insumo_id,), fetch=True)
        if not ok or not datos_actuales: return
        stock_actual = float(datos_actuales[0][0])
        if cantidad_perdida > stock_actual: QMessageBox.critical(self, "Error de Stock", f"La pérdida ({cantidad_perdida}) es mayor al stock actual ({stock_actual})."); return
        stock_final = stock_actual - cantidad_perdida
        try:
            cursor = self.conexion.cursor()
            query_movimiento = "INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo) VALUES (%s, 'perdida', %s, %s)"
            cursor.execute(query_movimiento, (insumo_id, cantidad_perdida, motivo))
            query_insumo_update = "UPDATE insumos SET stock_actual = %s WHERE id_insumo = %s"
            cursor.execute(query_insumo_update, (stock_final, insumo_id))
            self.conexion.commit()
            QMessageBox.information(self, "Éxito", f"Pérdida de {cantidad_perdida} registrada. Stock actualizado.")
            self.cargar_datos_stock(); self.entrada_cantidad_perdida.clear(); self.entrada_motivo_perdida.clear()
        except pymysql.MySQLError as e: QMessageBox.critical(self, "Error de DB", f"Fallo al registrar la pérdida:\n{str(e)}"); self.conexion.rollback()


class InventarioWindow(QMainWindow):
    """Módulo 1: Gestión de Inventario (Submenú)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Submenu_Inventario.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("Módulo 1: Gestión de Inventario")
        self.boton_control_stock.clicked.connect(self.ir_a_control_stock)
        self.boton_config_recetas.clicked.connect(self.ir_a_recetas)
        self.boton_gestion_proveedores.clicked.connect(self.ir_a_proveedores)
        self.boton_volver_menu.clicked.connect(self.volver_menu)
        self.show()
    def volver_menu(self): self.parent_window.show(); self.hide()
    def navegar_a_submodulo(self, SubmoduloClase): self.modulo_actual = SubmoduloClase(self, self.conexion); self.hide()
    def ir_a_control_stock(self): self.navegar_a_submodulo(ControlStockWindow)
    def ir_a_recetas(self): self.navegar_a_submodulo(RecetasWindow)
    def ir_a_proveedores(self): self.navegar_a_submodulo(ProveedoresWindow)


class RecetasWindow(QMainWindow):
    """Módulo 1.2: Definición de Recetas y Cálculo de CMV Base."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Recetas.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("1.2 Definición de Recetas y CMV")
        self.showMaximized()
        self.producto_seleccionado_id = None
        self.productos_map = {}; self.insumos_map = {}
        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.combo_productos.currentIndexChanged.connect(self.cargar_receta_y_cmv)
        self.boton_agregar_insumo.clicked.connect(self.agregar_o_modificar_insumo_receta)
        self.boton_eliminar_insumo.clicked.connect(self.eliminar_insumo_receta)
        self.cargar_comboboxes(); self.tabla_receta.setEditTriggers(self.tabla_receta.NoEditTriggers)

    def volver_menu(self): self.parent_window.show(); self.hide()

    def cargar_comboboxes(self):
        query_productos = "SELECT id_producto, nombre, precio_venta FROM productos WHERE activo = TRUE ORDER BY nombre"
        ok_p, productos = ejecutar_consulta_db(self.conexion, query_productos, fetch=True)
        if ok_p:
            self.combo_productos.clear(); self.productos_map = {}
            for id_p, nombre, precio in productos: self.productos_map[id_p] = {'nombre': nombre, 'precio': float(precio)}; self.combo_productos.addItem(f"{id_p} - {nombre}")
            if self.combo_productos.count() > 0: self.cargar_receta_y_cmv()
        query_insumos = "SELECT id_insumo, nombre, unidad_medida, costo_promedio FROM insumos WHERE activo = TRUE ORDER BY nombre"
        ok_i, insumos = ejecutar_consulta_db(self.conexion, query_insumos, fetch=True)
        if ok_i:
            self.combo_insumo_nuevo.clear(); self.insumos_map = {}
            for id_i, nombre, unidad, costo in insumos: self.insumos_map[id_i] = {'nombre': nombre, 'unidad': unidad, 'costo_promedio': float(costo)}; self.combo_insumo_nuevo.addItem(f"{id_i} - {nombre} ({unidad})")

    def calcular_cmv_y_margen(self, receta_actual):
        cmv_total = sum(float(insumo[4]) for insumo in receta_actual)
        if self.producto_seleccionado_id not in self.productos_map: return
        id_p = self.producto_seleccionado_id; precio_venta = self.productos_map[id_p]['precio']; margen = precio_venta - cmv_total
        self.label_precio_venta_valor.setText(f"Precio Venta: $ {precio_venta:,.0f}"); self.label_cmv_actual.setText(f"CMV Estimado: $ {cmv_total:,.2f}")
        self.label_margen_contribucion.setText(f"Margen Contribución: $ {margen:,.2f}")
        if margen < precio_venta * 0.40: self.label_margen_contribucion.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else: self.label_margen_contribucion.setStyleSheet("color: #2ecc71; font-weight: bold;")

    def cargar_receta_y_cmv(self):
        item_texto = self.combo_productos.currentText()
        if not item_texto: self.tabla_receta.setRowCount(0); return
        try: self.producto_seleccionado_id = int(item_texto.split(' - ')[0])
        except ValueError: self.tabla_receta.setRowCount(0); return
        query = "SELECT r.id_receta, r.id_insumo, i.nombre, r.cantidad_requerida, i.unidad_medida, i.costo_promedio FROM recetas r JOIN insumos i ON r.id_insumo = i.id_insumo WHERE r.id_producto = %s ORDER BY i.nombre"
        ok, resultados = ejecutar_consulta_db(self.conexion, query, (self.producto_seleccionado_id,), fetch=True)
        if not ok: self.tabla_receta.setRowCount(0); return
        self.tabla_receta.setRowCount(len(resultados)); receta_actual_data = [] 
        for fila, datos in enumerate(resultados):
            id_receta, id_insumo, nombre, cantidad, unidad, costo_promedio = datos
            costo_cmv = float(cantidad) * float(costo_promedio)
            self.tabla_receta.setItem(fila, 0, QTableWidgetItem(str(id_receta))); self.tabla_receta.setItem(fila, 1, QTableWidgetItem(str(id_insumo)))
            self.tabla_receta.setItem(fila, 2, QTableWidgetItem(nombre)); self.tabla_receta.setItem(fila, 3, QTableWidgetItem(f"{float(cantidad):.3f}"))
            self.tabla_receta.setItem(fila, 4, QTableWidgetItem(unidad)); self.tabla_receta.setItem(fila, 5, QTableWidgetItem(f"$ {costo_cmv:,.2f}"))
            receta_actual_data.append((id_insumo, nombre, cantidad, unidad, costo_cmv))
        self.calcular_cmv_y_margen(receta_actual_data)
    def agregar_o_modificar_insumo_receta(self):
        if self.producto_seleccionado_id is None: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un producto (Roll) primero."); return
        insumo_texto = self.combo_insumo_nuevo.currentText()
        if not insumo_texto: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un insumo."); return
        try: insumo_id = int(insumo_texto.split(' - ')[0]); cantidad_requerida = float(self.entrada_cantidad_requerida.text())
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "Cantidad debe ser un número decimal válido."); return
        if cantidad_requerida <= 0: QMessageBox.warning(self, "Advertencia", "La cantidad requerida debe ser mayor a cero."); return
        query_check = "SELECT id_receta FROM recetas WHERE id_producto = %s AND id_insumo = %s"
        ok, resultado_check = ejecutar_consulta_db(self.conexion, query_check, (self.producto_seleccionado_id, insumo_id), fetch=True)
        if not ok: return
        if resultado_check: query = "UPDATE recetas SET cantidad_requerida = %s WHERE id_receta = %s"; params = (cantidad_requerida, resultado_check[0][0]); mensaje = f"Receta actualizada: Cantidad de {self.insumos_map[insumo_id]['nombre']} modificada."
        else: query = "INSERT INTO recetas (id_producto, id_insumo, cantidad_requerida) VALUES (%s, %s, %s)"; params = (self.producto_seleccionado_id, insumo_id, cantidad_requerida); mensaje = f"Receta actualizada: {self.insumos_map[insumo_id]['nombre']} agregado."
        ok_op, _ = ejecutar_consulta_db(self.conexion, query, params)
        if ok_op: QMessageBox.information(self, "Éxito", mensaje); self.entrada_cantidad_requerida.clear(); self.cargar_receta_y_cmv()
        else: QMessageBox.critical(self, "Error de DB", "No se pudo actualizar la receta.")
    def eliminar_insumo_receta(self):
        selected_rows = self.tabla_receta.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Advertencia", "Seleccione un insumo de la receta para eliminar."); return
        fila_seleccionada = selected_rows[0].row(); id_receta = self.tabla_receta.item(fila_seleccionada, 0).text()
        nombre_insumo = self.tabla_receta.item(fila_seleccionada, 2).text()
        confirmacion = QMessageBox.question(self, "Confirmar Eliminación", f"¿Desea eliminar '{nombre_insumo}' de la receta actual?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes:
            query = "DELETE FROM recetas WHERE id_receta = %s"; ok, _ = ejecutar_consulta_db(self.conexion, query, (id_receta,))
            if ok: QMessageBox.information(self, "Éxito", f"'{nombre_insumo}' eliminado de la receta."); self.cargar_receta_y_cmv()


class ControlStockWindow(QMainWindow):
    """Módulo 1.1: Visualización y Gestión de Entradas/Salidas/Pérdidas de Stock."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Control_Stock.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("1.1 Control de Stock y Alertas")
        self.showMaximized()
        self.boton_volver_submenu.clicked.connect(self.volver_menu)
        self.boton_recargar_tabla.clicked.connect(self.cargar_datos_stock)
        self.boton_registrar_compra.clicked.connect(self.registrar_compra)
        self.boton_registrar_perdida.clicked.connect(self.registrar_perdida)
        self.combo_filtro_alertas.currentIndexChanged.connect(self.cargar_datos_stock)
        self.cargar_datos_stock()

    def volver_menu(self): self.parent_window.show(); self.hide()
    
    def cargar_datos_stock(self):
        query = """
        SELECT i.id_insumo, i.nombre, i.unidad_medida, i.stock_actual, i.stock_minimo, 
               i.costo_promedio, p.nombre AS proveedor_principal, i.stock_actual <= i.stock_minimo AS es_critico
        FROM insumos i LEFT JOIN proveedores p ON i.id_proveedor_principal = p.id_proveedor
        WHERE i.activo = TRUE
        """
        filtro = self.combo_filtro_alertas.currentText()
        if 'Críticos' in filtro or 'Bajo Stock' in filtro: query += " AND i.stock_actual <= i.stock_minimo"
        elif 'Suficiente' in filtro: query += " AND i.stock_actual > i.stock_minimo"
        ok, resultados = ejecutar_consulta_db(self.conexion, query, fetch=True)
        if not ok: self.tabla_stock_insumos.setRowCount(0); return
        columnas = ["ID", "Insumo", "Unidad", "Stock Actual", "Stock Mínimo", "Costo Promedio (CLP)", "Proveedor Principal", "Estado"]
        self.tabla_stock_insumos.setRowCount(len(resultados)); self.tabla_stock_insumos.setColumnCount(len(columnas)); self.tabla_stock_insumos.setHorizontalHeaderLabels(columnas)
        self.lista_alertas.clear(); insumos_en_alerta = []; insumo_nombres = {}
        for fila, datos in enumerate(resultados):
            insumo_id, insumo_nombre, unidad, stock_actual, stock_minimo, costo_promedio, proveedor, es_critico = datos
            stock_actual, stock_minimo = float(stock_actual), float(stock_minimo)
            insumo_nombres[insumo_id] = insumo_nombre
            for col, valor in enumerate(datos):
                item = QTableWidgetItem(str(valor)); item.setFlags(item.flags() & ~Qt.ItemIsEditable) 
                if es_critico:
                    item.setBackground(QColor(255, 230, 230))
                    if col == 7:
                        estado_texto = "🚨 SIN STOCK" if stock_actual <= 0 else "⚠️ CRÍTICO"; item.setText(estado_texto)
                        if stock_actual <= stock_minimo:
                            tipo = "SIN STOCK" if stock_actual <= 0 else "CRÍTICO"; alerta_msg = f"⚠️ {insumo_nombre} (ID {insumo_id}): {stock_actual:.2f} {unidad}. ¡{tipo}!"; insumos_en_alerta.append(alerta_msg)
                elif col == 7: item.setText("🟢 OK")
                if col == 5: item.setText(f"${float(valor):,.2f}")
                if col == 3 or col == 4: item.setText(f"{float(valor):.2f}")
                self.tabla_stock_insumos.setItem(fila, col, item)
        self.lista_alertas.addItems(insumos_en_alerta); self.combo_insumo_compra.clear(); self.combo_insumo_perdida.clear()
        insumo_lista_formato = [f"{id} - {nombre}" for id, nombre in insumo_nombres.items()]
        self.combo_insumo_compra.addItems(insumo_lista_formato); self.combo_insumo_perdida.addItems(insumo_lista_formato)
        QMessageBox.information(self, "Información", f"Se cargaron {len(resultados)} insumos y {len(insumos_en_alerta)} alertas activas.")

    def registrar_compra(self):
        insumo_seleccionado = self.combo_insumo_compra.currentText()
        if not insumo_seleccionado: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un insumo."); return
        try: insumo_id = int(insumo_seleccionado.split(' - ')[0]); cantidad = float(self.entrada_cantidad_compra.text()); costo_unitario = float(self.entrada_costo_unitario.text())
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "Cantidad y Costo deben ser números válidos."); return
        if cantidad <= 0 or costo_unitario <= 0: QMessageBox.warning(self, "Advertencia", "Cantidad y Costo Unitario deben ser mayores a cero."); return
        query_actual = "SELECT stock_actual, costo_promedio FROM insumos WHERE id_insumo = %s"
        ok, datos_actuales = ejecutar_consulta_db(self.conexion, query_actual, (insumo_id,), fetch=True)
        if not ok or not datos_actuales: return
        stock_actual, costo_promedio_actual = float(datos_actuales[0][0]), float(datos_actuales[0][1])
        costo_total_antiguo = stock_actual * costo_promedio_actual; costo_total_nuevo = cantidad * costo_unitario
        stock_total_nuevo = stock_actual + cantidad
        nuevo_costo_promedio = (costo_total_antiguo + costo_total_nuevo) / stock_total_nuevo if stock_total_nuevo > 0 else costo_unitario 
        try:
            cursor = self.conexion.cursor()
            query_movimiento = "INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, costo_unitario, motivo) VALUES (%s, 'entrada', %s, %s, 'Compra registrada')"
            cursor.execute(query_movimiento, (insumo_id, cantidad, costo_unitario))
            query_insumo_update = "UPDATE insumos SET stock_actual = %s, costo_promedio = %s WHERE id_insumo = %s"
            cursor.execute(query_insumo_update, (stock_total_nuevo, nuevo_costo_promedio, insumo_id))
            self.conexion.commit()
            QMessageBox.information(self, "Éxito", "Compra registrada y costo promedio actualizado.")
            self.cargar_datos_stock(); self.entrada_cantidad_compra.clear(); self.entrada_costo_unitario.clear()
        except pymysql.MySQLError as e: QMessageBox.critical(self, "Error de DB", f"Fallo al registrar la compra:\n{str(e)}"); self.conexion.rollback()

    def registrar_perdida(self):
        insumo_seleccionado = self.combo_insumo_perdida.currentText()
        if not insumo_seleccionado: QMessageBox.warning(self, "Advertencia", "Debe seleccionar un insumo."); return
        try: insumo_id = int(insumo_seleccionado.split(' - ')[0]); cantidad_perdida = float(self.entrada_cantidad_perdida.text()); motivo = self.entrada_motivo_perdida.text()
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "La cantidad debe ser un número válido."); return
        if cantidad_perdida <= 0: QMessageBox.warning(self, "Advertencia", "La cantidad de pérdida debe ser mayor a cero."); return
        if not motivo: QMessageBox.warning(self, "Advertencia", "Debe especificar un motivo para la pérdida."); return
        query_actual = "SELECT stock_actual FROM insumos WHERE id_insumo = %s"
        ok, datos_actuales = ejecutar_consulta_db(self.conexion, query_actual, (insumo_id,), fetch=True)
        if not ok or not datos_actuales: return
        stock_actual = float(datos_actuales[0][0])
        if cantidad_perdida > stock_actual: QMessageBox.critical(self, "Error de Stock", f"La pérdida ({cantidad_perdida}) es mayor al stock actual ({stock_actual})."); return
        stock_final = stock_actual - cantidad_perdida
        try:
            cursor = self.conexion.cursor()
            query_movimiento = "INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo) VALUES (%s, 'perdida', %s, %s)"
            cursor.execute(query_movimiento, (insumo_id, cantidad_perdida, motivo))
            query_insumo_update = "UPDATE insumos SET stock_actual = %s WHERE id_insumo = %s"
            cursor.execute(query_insumo_update, (stock_final, insumo_id))
            self.conexion.commit()
            QMessageBox.information(self, "Éxito", f"Pérdida de {cantidad_perdida} registrada. Stock actualizado.")
            self.cargar_datos_stock(); self.entrada_cantidad_perdida.clear(); self.entrada_motivo_perdida.clear()
        except pymysql.MySQLError as e: QMessageBox.critical(self, "Error de DB", f"Fallo al registrar la pérdida:\n{str(e)}"); self.conexion.rollback()


class InventarioWindow(QMainWindow):
    """Módulo 1: Gestión de Inventario (Submenú)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Submenu_Inventario.ui", self)
        self.conexion = conexion
        self.parent_window = parent_window
        self.setWindowTitle("Módulo 1: Gestión de Inventario")
        self.boton_control_stock.clicked.connect(self.ir_a_control_stock)
        self.boton_config_recetas.clicked.connect(self.ir_a_recetas)
        self.boton_gestion_proveedores.clicked.connect(self.ir_a_proveedores)
        self.boton_volver_menu.clicked.connect(self.volver_menu)
        self.show()
    def volver_menu(self): self.parent_window.show(); self.hide()
    def navegar_a_submodulo(self, SubmoduloClase): self.modulo_actual = SubmoduloClase(self, self.conexion); self.hide()
    def ir_a_control_stock(self): self.navegar_a_submodulo(ControlStockWindow)
    def ir_a_recetas(self): self.navegar_a_submodulo(RecetasWindow)
    def ir_a_proveedores(self): self.navegar_a_submodulo(ProveedoresWindow)


class PedidosWindow(QMainWindow):
    """Módulo 2: Registro de Pedidos (TPV) - Lógica de Venta y Consumo de Stock."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Pedidos.ui", self); self.conexion = conexion; self.parent_window = parent_window
        self.setWindowTitle("2. Registro de Pedidos (TPV)"); self.showMaximized()
        self.current_pedido = []; self.productos_data = {} 
        self.boton_volver_menu.clicked.connect(self.volver_menu)
        self.combo_categoria.currentIndexChanged.connect(self.cargar_productos_por_categoria)
        self.boton_agregar_a_pedido.clicked.connect(self.agregar_a_pedido)
        self.boton_eliminar_item.clicked.connect(self.eliminar_item); self.boton_cancelar_pedido.clicked.connect(self.cancelar_pedido)
        self.boton_finalizar_venta.clicked.connect(self.finalizar_venta)
        self.tabla_pedido_actual.setSelectionBehavior(self.tabla_pedido_actual.SelectRows); self.tabla_pedido_actual.setEditTriggers(self.tabla_pedido_actual.NoEditTriggers)
        self.cargar_inicial()
    def volver_menu(self): self.parent_window.show(); self.hide()
    def cargar_inicial(self):
        query_cat = "SELECT id_categoria, nombre FROM categorias_productos ORDER BY nombre"
        ok_c, categorias = ejecutar_consulta_db(self.conexion, query_cat, fetch=True)
        if ok_c:
            self.combo_categoria.clear(); self.combo_categoria.addItem("Todas las Categorías")
            for id_c, nombre in categorias: self.combo_categoria.addItem(f"{id_c} - {nombre}")
        query_prod = "SELECT id_producto, nombre, precio_venta, id_categoria FROM productos WHERE activo = TRUE"
        ok_p, productos = ejecutar_consulta_db(self.conexion, query_prod, fetch=True)
        if ok_p:
            self.productos_data = {}
            for id_p, nombre, precio, id_cat in productos: self.productos_data[id_p] = {'nombre': nombre, 'precio_venta': float(precio), 'id_categoria': id_cat}
        self.cargar_productos_por_categoria(); self.actualizar_resumen()
    def cargar_productos_por_categoria(self):
        self.lista_productos.clear(); filtro = self.combo_categoria.currentText(); selected_category_id = None
        if filtro != "Todas las Categorías" and filtro:
             try: selected_category_id = int(filtro.split(' - ')[0])
             except ValueError: pass
        for id_p, data in self.productos_data.items():
            if selected_category_id is None or data['id_categoria'] == selected_category_id:
                item_text = f"[{id_p}] {data['nombre']} - ${data['precio_venta']:,.0f}"; item = QListWidgetItem(item_text); item.setData(Qt.UserRole, id_p); self.lista_productos.addItem(item)
    def agregar_a_pedido(self):
        selected_item = self.lista_productos.currentItem()
        if not selected_item: QMessageBox.warning(self, "Advertencia", "Seleccione un producto de la lista."); return
        prod_id = selected_item.data(Qt.UserRole)
        try: cantidad = int(self.entrada_cantidad.text())
        except ValueError: QMessageBox.critical(self, "Error de Entrada", "Cantidad debe ser un número entero positivo."); return
        if cantidad <= 0: QMessageBox.critical(self, "Error de Entrada", "Cantidad debe ser un número entero positivo."); return
        data = self.productos_data.get(prod_id)
        precio_unitario = data['precio_venta']; total_item = cantidad * precio_unitario
        self.current_pedido.append({'id_producto': prod_id, 'nombre': data['nombre'], 'cantidad': cantidad, 'precio_unitario': precio_unitario, 'total_item': total_item})
        self.actualizar_resumen(); self.entrada_cantidad.setText("1")
    def eliminar_item(self):
        selected_rows = self.tabla_pedido_actual.selectionModel().selectedRows()
        if not selected_rows: QMessageBox.warning(self, "Advertencia", "Seleccione un ítem del pedido para eliminar."); return
        fila = selected_rows[0].row(); del self.current_pedido[fila]; self.tabla_pedido_actual.removeRow(fila)
        self.actualizar_resumen()
    def cancelar_pedido(self):
        confirmacion = QMessageBox.question(self, "Confirmar Cancelación", "¿Desea CANCELAR y limpiar el pedido actual?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion == QMessageBox.Yes: self.current_pedido = []; self.actualizar_resumen(); QMessageBox.information(self, "Cancelado", "Pedido cancelado. El carrito está vacío.")
    def actualizar_resumen(self):
        subtotal = sum(item['total_item'] for item in self.current_pedido); total_final = subtotal
        self.tabla_pedido_actual.setRowCount(len(self.current_pedido))
        for fila, item in enumerate(self.current_pedido):
            self.tabla_pedido_actual.setItem(fila, 0, QTableWidgetItem(str(item['id_producto']))); self.tabla_pedido_actual.setItem(fila, 1, QTableWidgetItem(item['nombre']))
            self.tabla_pedido_actual.setItem(fila, 2, QTableWidgetItem(str(item['cantidad']))); self.tabla_pedido_actual.setItem(fila, 3, QTableWidgetItem(f"${item['precio_unitario']:,.0f}"))
            self.tabla_pedido_actual.setItem(fila, 4, QTableWidgetItem(f"${item['total_item']:,.0f}"))
        self.label_subtotal.setText(f"SUBTOTAL: $ {subtotal:,.0f}"); self.label_total.setText(f"TOTAL FINAL: $ {total_final:,.0f}")
    def finalizar_venta(self):
        if not self.current_pedido: QMessageBox.warning(self, "Advertencia", "El pedido está vacío."); return
        canal_venta = self.combo_canal_venta.currentText(); total_pedido = sum(item['total_item'] for item in self.current_pedido)
        confirmacion = QMessageBox.question(self, "CONFIRMAR VENTA", f"Total a registrar: ${total_pedido:,.0f}\nCanal: {canal_venta}\n¿Desea confirmar y consumir stock?", QMessageBox.Yes | QMessageBox.No)
        if confirmacion != QMessageBox.Yes: return
        consumo_total_insumos = {}; venta_registros = []
        try:
            cursor = self.conexion.cursor()
            for item in self.current_pedido:
                prod_id = item['id_producto']; cantidad_vendida = item['cantidad']
                query_receta = "SELECT r.id_insumo, r.cantidad_requerida, i.costo_promedio, i.stock_actual FROM recetas r JOIN insumos i ON r.id_insumo = i.id_insumo WHERE r.id_producto = %s"
                cursor.execute(query_receta, (prod_id,)); receta = cursor.fetchall()
                item_cmv = 0.0
                for id_insumo, req_por_unidad, costo_unitario, stock_actual in receta:
                    req_total = float(req_por_unidad) * cantidad_vendida; item_cmv += float(req_por_unidad) * float(costo_unitario)
                    if float(stock_actual) < req_total:
                        QMessageBox.critical(self, "ERROR CRÍTICO", f"STOCK INSUFICIENTE para Insumo ID {id_insumo} ({float(stock_actual):.2f}). Venta abortada."); return 
                    consumo_total_insumos[id_insumo] = consumo_total_insumos.get(id_insumo, 0) + req_total
                venta_registros.append({
                    'fecha_venta': QDate.currentDate().toString("yyyy-MM-dd"), 'id_producto': prod_id, 'cantidad': cantidad_vendida,
                    'precio_unitario': item['precio_unitario'], 'costo_unitario_calculado': item_cmv,
                    'total_venta': item['total_item'], 'canal_venta': canal_venta
                })
            query_insert_venta = "INSERT INTO ventas (fecha_venta, id_producto, cantidad, precio_unitario, costo_unitario_calculado, total_venta, canal_venta) VALUES (%s, %s, %s, %s, %s, %s, %s)"
            for registro in venta_registros: cursor.execute(query_insert_venta, tuple(registro.values()))
            for id_insumo, consumo in consumo_total_insumos.items():
                query_stock_actual = "SELECT stock_actual FROM insumos WHERE id_insumo = %s"; cursor.execute(query_stock_actual, (id_insumo,))
                stock_actual = float(cursor.fetchone()[0]); nuevo_stock = stock_actual - consumo
                query_insert_mov = "INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, motivo) VALUES (%s, 'salida', %s, 'Consumo por Venta TPV')"
                cursor.execute(query_insert_mov, (id_insumo, consumo))
                query_update_stock = "UPDATE insumos SET stock_actual = %s WHERE id_insumo = %s"
                cursor.execute(query_update_stock, (nuevo_stock, id_insumo))
            self.conexion.commit()
            QMessageBox.information(self, "Éxito de Venta", f"Venta Total (${total_pedido:,.0f}) registrada y stock consumido.")
            self.cancelar_pedido()
        except pymysql.MySQLError as e: QMessageBox.critical(self, "ERROR DE TRANSACCIÓN", f"Fallo en MySQL. Transacción revertida. Error: {str(e)}"); self.conexion.rollback()
        except Exception as e: QMessageBox.critical(self, "ERROR GENERAL", f"Fallo inesperado al procesar la venta. Transacción revertida. Error: {str(e)}"); self.conexion.rollback()


class InsumosSecundariosWindow(QMainWindow): 
    """Módulo 3.1: CRUD de Insumos Secundarios (Placeholder)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        self.conexion = conexion; self.parent_window = parent_window
        self.setWindowTitle("3.1 Gestión de Insumos Secundarios"); self.showMaximized()
        QMessageBox.information(self, "Desarrollo", "Preparando Módulo de Insumos Secundarios..."); 
    def volver_menu(self): self.parent_window.show(); self.hide()


class GastosFijosWindow(QMainWindow): 
    """Módulo 3.2: Gestión CRUD de la tabla gastos_operativos (Placeholder)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        self.conexion = conexion; self.parent_window = parent_window
        self.setWindowTitle("3.2 Gestión de Gastos Fijos"); self.showMaximized()
        QMessageBox.information(self, "Desarrollo", "Preparando Módulo de Gastos Fijos...");
    def volver_menu(self): self.parent_window.show(); self.hide()


class ExportarDatosWindow(QMainWindow): 
    """Módulo 3.3: Exportación de datos a CSV/Excel (Implementación base)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        self.conexion = conexion; self.parent_window = parent_window
        self.setWindowTitle("3.3 Exportar Datos Históricos"); self.showMaximized()
        temp_widget = QWidget(); temp_layout = QVBoxLayout(temp_widget)
        self.export_button = QPushButton("EXPORTAR TODAS LAS TABLAS A CSV")
        self.export_button.setStyleSheet("background-color: #e67e22; color: white; min-height: 50px; border-radius: 8px; font-size: 14pt;")
        self.export_button.clicked.connect(self.exportar_tablas)
        self.volver_button = QPushButton("⬅️ Volver al Submenú")
        self.volver_button.setStyleSheet("background-color: #95a5a6; color: white; min-height: 40px; border-radius: 8px; font-size: 12pt;")
        self.volver_button.clicked.connect(self.volver_menu)
        temp_layout.addWidget(QLabel("Seleccione la opción para generar archivos de auditoría."))
        temp_layout.addWidget(self.export_button); temp_layout.addStretch(); temp_layout.addWidget(self.volver_button)
        self.setCentralWidget(temp_widget)

    def volver_menu(self): self.parent_window.show(); self.hide()

    def exportar_tablas(self):
        tablas_a_exportar = ["ventas", "movimientos_inventario", "gastos_operativos", "insumos", "productos", "proveedores"]
        directorio = QFileDialog.getExistingDirectory(self, "Seleccionar Carpeta para Exportar", os.getcwd())
        if not directorio: QMessageBox.warning(self, "Advertencia", "Exportación cancelada."); return
        for tabla in tablas_a_exportar:
            query = f"SELECT * FROM {tabla}"
            ok, resultados = ejecutar_consulta_db(self.conexion, query, fetch=True)
            if ok:
                try:
                    cursor = self.conexion.cursor(); cursor.execute(query)
                    columnas = [desc[0] for desc in cursor.description]
                    filepath = os.path.join(directorio, f"{tabla}_data.csv")
                    with open(filepath, 'w', newline='', encoding='utf-8') as f:
                        writer = csv.writer(f); writer.writerow(columnas)
                        writer.writerows([[str(col) for col in row] for row in resultados])
                    QMessageBox.information(self, "Éxito", f"Datos de la tabla '{tabla}' exportados correctamente a:\n{filepath}")
                except Exception as e: QMessageBox.critical(self, "Error de Exportación", f"Fallo al exportar la tabla {tabla}:\n{str(e)}")
            else: QMessageBox.critical(self, "Error de Consulta", f"No se pudo obtener datos para la tabla {tabla}.")


class VentasGastosWindow(QMainWindow):
    """Carga el Submenú de Carga de Ventas, Gastos y Exportación (Módulo 3)."""
    def __init__(self, parent_window, conexion):
        super().__init__()
        loadUi("Submenu_Ventas_Gastos.ui", self); self.conexion = conexion; self.parent_window = parent_window
        self.setWindowTitle("Módulo 3: Carga de Datos, Gastos y Exportación")
        self.boton_insumos_secundarios.clicked.connect(self.ir_a_insumos_secundarios)
        self.boton_gestion_gastos.clicked.connect(self.ir_a_gastos_fijos)
        self.boton_exportar_datos.clicked.connect(self.ir_a_exportar_datos)
        self.boton_volver_menu.clicked.connect(self.volver_menu); self.show()
    def volver_menu(self): self.parent_window.show(); self.hide()
    def navegar_a_submodulo(self, SubmoduloClase): self.modulo_actual = SubmoduloClase(self, self.conexion); self.hide()
    def ir_a_insumos_secundarios(self): self.navegar_a_submodulo(InsumosSecundariosWindow)
    def ir_a_gastos_fijos(self): self.navegar_a_submodulo(GastosFijosWindow)
    def ir_a_exportar_datos(self): self.navegar_a_submodulo(ExportarDatosWindow)




class MenuPrincipalWindow(QMainWindow):
    """Ventana principal de navegación."""
    def __init__(self, conexion):
        super().__init__()
        loadUi("Menu_Principal.ui", self)
        self.conexion = conexion
        self.setWindowTitle("Menú Principal - Atai Sushi SIG")
        self.boton_inventario.clicked.connect(self.ir_a_inventario); self.boton_pedidos.clicked.connect(self.ir_a_pedidos)
        self.boton_reportes.clicked.connect(self.ir_a_reportes)
    def navegar_a_modulo(self, ModuloClase): self.modulo_actual = ModuloClase(self, self.conexion); self.hide()
    def ir_a_inventario(self): self.navegar_a_modulo(InventarioWindow)
    def ir_a_pedidos(self): self.navegar_a_modulo(PedidosWindow)
    def ir_a_reportes(self): self.navegar_a_modulo(ReportesWindow)




class IngresoDBWindow(QMainWindow):
    """Ventana inicial de la aplicación (Login)."""
    def __init__(self):
        super().__init__(); loadUi("Ingreso_DB.ui", self); self.conexion = None
        self.boton_conectar.clicked.connect(self.connect_to_database); self.menu_window = None
    def connect_to_database(self):
        host = self.entrada_host.text(); user = self.entrada_usuario.text(); password = self.entrada_clave.text()
        database_name = "atai_sushi_sig"
        try:
            self.conexion = pymysql.connect(host=host, user=user, password=password, database=database_name)
            QMessageBox.information(self, "Éxito de Conexión", f"¡Conexión exitosa a la base de datos '{database_name}'!")
            self.menu_window = MenuPrincipalWindow(self.conexion); self.menu_window.show(); self.hide() 
        except pymysql.MySQLError as e: QMessageBox.critical(self, "Error de Conexión", f"Fallo al conectar. Verifique credenciales o el servidor. \nError: {str(e)}")
        except Exception as e: QMessageBox.critical(self, "Error General", f"Ocurrió un error inesperado. \nError: {str(e)}")


if __name__ == "__main__":
    app = QCoreApplication.instance(); 
    if app is None: app = QApplication(sys.argv)
    main_window = IngresoDBWindow(); main_window.show()
    sys.exit(app.exec_())