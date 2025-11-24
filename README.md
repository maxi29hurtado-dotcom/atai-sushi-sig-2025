# SIG Atai Sushi - Sistema de Información para la Gestión

**Curso:** ICN292 - Sistemas de Información para la Gestión  
**Semestre:** 2025/02  
**Universidad Técnica Federico Santa María** **Profesor:** Eloy Alvarado Narváez

## 1. Descripción del Proyecto

Este proyecto consiste en el desarrollo e implementación de un Sistema de Información para la Gestión (SIG) diseñado a medida para la PyME Atai Sushi. La solución es una plataforma de gestión que centraliza las operaciones críticas del negocio, permitiendo el control integral de inventarios, el costeo dinámico de recetas y el registro de ventas en un entorno unificado.

El sistema aborda y soluciona la problemática de la gestión manual y fragmentada, reemplazando el uso de planillas de cálculo y registros en papel por una base de datos relacional robusta.

Sus principales capacidades son:

Automatización Financiera: Cálculo automático del Costo de Mercadería Vendida (CMV) y generación de Estado de Resultados (P&L) en tiempo real.

Control de Stock: Descuento automático de ingredientes basado en recetas estándar al momento de la venta.

Gestión de Mermas: Registro y valorización de pérdidas para control de costos.

Interfaz Unificada: Panel de control para perfiles de Administrador, Caja y Cocina.

## 2. Tecnologías Utilizadas

* **Lenguaje de Programación:** Python 3.x
* **Interfaz Gráfica (GUI):** PyQt5 (Qt Designer)
* **Base de Datos:** MySQL
* **Conector de Base de Datos:** PyMySQL
* **Modelado de Procesos:** Bizagi Modeler (.bpm)

## 3. Estructura del Repositorio

El código fuente entregado está organizado de la siguiente manera:

* **`main.py`**: Archivo principal de ejecución. Contiene la lógica del negocio, conexión a la base de datos y orquestación de la interfaz gráfica.
* **`BDD_AtaiSushi.sql`**: Script SQL completo. Incluye la creación de la base de datos (`atai_sushi_sig`), tablas, inserción de datos iniciales (semilla), triggers de automatización y vistas.
* **`Proceso_Venta_Atai.bpm`**: Archivo fuente del diagrama de procesos de negocio (Bizagi).
* **Archivos de Interfaz (.ui)**:
  * `Ingreso_DB.ui`: Pantalla de inicio de sesión y conexión.
  * `Menu_Principal.ui`: Dashboard principal de navegación.
  * `Control_Stock.ui`: Módulo 1.1 para gestión de stock y alertas.
  * `Recetas.ui`: Módulo 1.2 para definición de recetas y costos.
  * `Proveedores.ui`: Módulo 1.3 para gestión de proveedores.
  * `Pedidos.ui`: Módulo 2 (Punto de Venta).
  * `Reporte_EERR.ui`: Visualización del Estado de Resultados.
  * `Submenu_Inventario.ui`, `Submenu_Reportes.ui`, `Submenu_Ventas_Gastos.ui`: Menús intermedios.

## 4. Guía de Instalación y Configuración

Siga estrictamente estos pasos para desplegar el sistema en un entorno local de desarrollo.

Requisitos Previos del Sistema:
- Sistema Operativo: Windows 10/11, macOS o Linux.
- Python: Versión 3.8 o superior.
- MySQL Server: Versión 5.7 o 8.0 (XAMPP recomendado para facilidad de uso).
- 
### Paso 1: Configuración del Motor de Base de Datos (MySQL)

1. Iniciar el Servidor: Asegúrese de que el servicio MySQL esté ejecutándose (ej. Panel de control de XAMPP -> MySQL -> Start).
2. Importar el Script SQL:
   - Abra su herramienta de administración SQL (phpMyAdmin, MySQL Workbench, DBeaver).
   - Abra el archivo BDD_AtaiSushi.sql incluido en este repositorio.
   - Ejecute el script completo.
   - Verificación: Confirme que se haya creado la base de datos llamada atai_sushi_sig y que contenga las tablas pobladas (ej. tabla productos con datos).

### Paso 2: Configuración del Entorno Python
1. Verificar Python: Abra una terminal (CMD o PowerShell) y ejecute python --version. Si no está instalado, descárguelo desde python.org.
2. Instalar Dependencias: Ejecute el siguiente comando para instalar las librerías gráficas y de conexión:
   
```bash
pip install PyQt5 pymysql
```

### Paso 3: Ejecución de la Aplicación

1. Manteniendo la terminal abierta en la carpeta del proyecto, ejecute el archivo principal:
```bash
python main.py
```

2. Pantalla de Conexión: Se abrirá la ventana de "Ingreso DB".
3. Credenciales: Ingrese los datos de su servidor local.
   - Host: localhost
   - Usuario: root (Estándar en XAMPP)
   - Clave: (Ingrese su clave personal de MySQL).
     
4. Presione "CONECTAR". Si la configuración es correcta, accederá al Menú Principal.
   
## 5. Manual de Uso Básico

### A. Inicio de Sesión y Conexión

Al iniciar la aplicación, el sistema solicitará las credenciales del servidor de base de datos. Una vez conectado, verá el panel principal de navegación.
Nota sobre Roles: El sistema está diseñado para diferentes perfiles. Algunas funciones (como el Estado de Resultados) pueden requerir permisos de "Administrador".

### B. Funcionalidades Principales por Módulo

1. Módulo de Inventario:
   - Monitor de Stock: Visualice el listado completo de insumos. El sistema utiliza un código de colores:
     🔴 Rojo: Stock crítico o bajo el mínimo (requiere reposición).
     ⚪ Blanco: Stock normal.
   - Registrar Compra: Use esta opción para ingresar facturas de proveedores. El sistema aumentará el stock y recalculará el Precio Promedio Ponderado (PPP) automáticamente.
   - Registrar Pérdida: Permite dar de baja insumos por merma (vencimiento, daño), manteniendo la trazabilidad del motivo.

 2. Módulo de Pedidos (Punto de Venta - TPV)
Diseñado para el uso diario de la cajera:

a) Seleccione la Categoría y el Producto del menú desplegable.

b) Ingrese la cantidad y presione "Agregar al Pedido".

c) Al finalizar, presione "Confirmar Venta".
   - Acción del Sistema: Descuenta automáticamente los ingredientes del inventario basándose en la Receta Estándar y registra el costo histórico de la transacción.


3. Reportes y Finanzas
Estado de Resultados (P&L): Seleccione un rango de fechas para generar el reporte financiero. El sistema calcula automáticamente:
- (+) Ingresos por Ventas.
- (-) Costo de Mercadería Vendida (CMV Real).
- (-) Gastos Operativos y Mermas.
- (=) Utilidad Neta Real.

KPIs Operacionales: Visualización gráfica de métricas clave como la Tasa de Quiebre de Stock y el Porcentaje de Mermas sobre compras.

## 6. Autores (Equipo de Trabajo)
Este proyecto fue desarrollado por el Grupo 6 para la asignatura de Sistemas de Información para la Gestión:
- Cristian Álvarez Miranda
- Maximiliano Hurtado Cerda
- Joaquín López Lock
- Ignacio Mera Solís
