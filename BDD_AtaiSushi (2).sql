DROP DATABASE IF EXISTS atai_sushi_sig;
CREATE DATABASE IF NOT EXISTS atai_sushi_sig;
USE atai_sushi_sig;

-- 1. TABLAS
CREATE TABLE proveedores (
    id_proveedor INT PRIMARY KEY AUTO_INCREMENT,
    nombre varchar(100) NOT NULL,
    contacto varchar(100),
    telefono varchar(20),
    activo BOOLEAN DEFAULT TRUE
);

CREATE TABLE insumos (
    id_insumo INT PRIMARY KEY AUTO_INCREMENT,
    nombre varchar(100) NOT NULL,
    unidad_medida varchar(20) NOT NULL,
    stock_minimo DECIMAL(10,2) NOT NULL,
    stock_actual DECIMAL(10,2) DEFAULT 0,
    costo_promedio DECIMAL(10,2) DEFAULT 0,
    id_proveedor_principal INT,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_proveedor_principal) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE categorias_productos (
    id_categoria INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT
);

CREATE TABLE productos (
    id_producto INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    id_categoria INT,
    precio_venta DECIMAL(10,2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE,
    FOREIGN KEY (id_categoria) REFERENCES categorias_productos(id_categoria)
);

CREATE TABLE recetas (
    id_receta INT AUTO_INCREMENT PRIMARY KEY,
    id_producto INT NOT NULL,
    id_insumo INT NOT NULL,
    cantidad_requerida DECIMAL(8,3) NOT NULL,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto),
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo)
);
CREATE INDEX idx_receta_producto ON recetas(id_producto);
CREATE INDEX idx_receta_insumo ON recetas(id_insumo);

CREATE TABLE movimientos_inventario (
    id_movimiento INT AUTO_INCREMENT PRIMARY KEY,
    id_insumo INT NOT NULL,
    tipo_movimiento ENUM('entrada', 'salida', 'ajuste', 'perdida') NOT NULL,
    cantidad DECIMAL(10,2) NOT NULL,
    costo_unitario DECIMAL(10,2),
    fecha_movimiento DATETIME DEFAULT CURRENT_TIMESTAMP,
    motivo VARCHAR(200),
    id_proveedor INT,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo),
    FOREIGN KEY (id_proveedor) REFERENCES proveedores(id_proveedor)
);

CREATE TABLE ventas (
    id_venta INT AUTO_INCREMENT PRIMARY KEY,
    fecha_venta DATE NOT NULL,
    id_producto INT NOT NULL,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    costo_unitario_calculado DECIMAL(10,2) NOT NULL,
    total_venta DECIMAL(10,2) NOT NULL,
    canal_venta ENUM('whatsapp', 'delivery_app', 'telefono', 'local') NOT NULL,
    fecha_importacion DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_producto) REFERENCES productos(id_producto)
);

CREATE TABLE alertas_stock (
    id_alerta INT AUTO_INCREMENT PRIMARY KEY,
    id_insumo INT NOT NULL,
    tipo_alerta ENUM('stock_minimo', 'stock_critico', 'sin_stock') NOT NULL,
    nivel_actual DECIMAL(10,2) NOT NULL,
    nivel_minimo DECIMAL(10,2) NOT NULL,
    fecha_alerta DATETIME DEFAULT CURRENT_TIMESTAMP,
    leida BOOLEAN DEFAULT FALSE,
    FOREIGN KEY (id_insumo) REFERENCES insumos(id_insumo)
);

CREATE TABLE gastos_operativos (
    id_gasto INT AUTO_INCREMENT PRIMARY KEY,
    fecha_gasto DATE NOT NULL,
    categoria ENUM('arriendo', 'sueldos', 'servicios_basicos', 'marketing', 'otros') NOT NULL,
    descripcion VARCHAR(200),
    monto DECIMAL(10,2) NOT NULL,
    usuario_registro VARCHAR(50)
);

CREATE TABLE usuarios (
    id_usuario INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL, 
    -- AQUÍ ESTABA EL ERROR: Agregamos 'cajero' y 'barra' a la lista permitida
    rol ENUM('administrador', 'cajera', 'cajero', 'cocina', 'barra') NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);

-- 2. INSERCIONES (CORREGIDAS)

INSERT INTO proveedores (nombre, contacto, telefono) VALUES
('Roll Stock S.A.', 'Lucas Poblete', '+56930035579'),
('Prodimarket S.A', 'María González', '+56947807862');

-- AQUÍ ESTÁ LA CORRECCIÓN PRINCIPAL: IDs explícitos para coincidir con recetas
INSERT INTO insumos (id_insumo, nombre, unidad_medida, stock_minimo, costo_promedio, id_proveedor_principal) VALUES
-- Pescados y Mariscos (IDs 1-6)
(1, 'Camarón', 'kg', 1.0, 7000, 1),
(2, 'Salmón', 'kg', 2.0, 13600, 1),
(3, 'Atún', 'kg', 1.0, 10000, 1),
(4, 'Camarón Tempura', 'kg', 1.0, 7000, 1),
(5, 'Pulpo', 'kg', 1.0, 10000, 1),
(6, 'Kanikama', 'kg', 1.0, 3200, 1),

-- Vegetales (IDs 7-14)
(7, 'Palta', 'kg', 3.0, 3300, 2),
(8, 'Pepino', 'kg', 1.0, 1000, 2),
(9, 'Cebollín', 'kg', 1.0, 8000, 2),
(10, 'Ciboulette', 'kg', 0.5, 4000, 2),
(11, 'Palmito', 'tarro', 1.0, 2500, 2),
(12, 'Pimentón Rojo', 'kg', 1.0, 2500, 2),
(13, 'Champiñón', 'kg', 0.5, 3000, 2),
(14, 'Pimentón Verde', 'kg', 1.0, 2500, 2), -- Usado en recetas veggies

-- Carnes (ID 15)
(15, 'Pollo', 'kg', 4.0, 6747, 1),

-- Lácteos (IDs 19-20)
(19, 'Queso Crema', 'kg', 3.0, 9100, 2),
(20, 'Queso Mantecoso', 'kg', 2.0, 8500, 2), -- AGREGADO (Faltaba y causaba error)

-- Base y Algas (IDs 22-23)
(22, 'Arroz Sushi', 'kg', 8.0, 1600, 2),
(23, 'Alga Nori', 'paquete', 1, 10000, 2),

-- Acompañamientos (IDs 24-25 y 33)
(24, 'Almendras', 'kg', 1.0, 6000, 2),
(25, 'Sésamo', 'kg', 1.0, 3500, 2),
(33, 'Papas Hilo', 'kg', 1.0, 2500, 2),

-- Salsas (IDs 26-27 y 30-32)
(26, 'Salsa Teriyaki', 'lt', 3.0, 3000, 2),
(27, 'Salsa Acevichada', 'lt', 2.0, 4000, 2),
(30, 'Salsa de Soja', 'lt', 5.0, 2000, 2), -- ASIGNADO ID 30 PARA NO CHOCAR CON HARINA
(31, 'Salsa Huancaina', 'lt', 2.0, 3500, 2),
(32, 'Salsa de Cilantro', 'lt', 1.0, 4500, 2),

-- Apanado (IDs 28-29)
(28, 'Pan Panko', 'kg', 2.0, 2200, 2),
(29, 'Harina Tempura', 'kg', 2.0, 2800, 2); 


INSERT INTO categorias_productos (nombre, descripcion) VALUES
('Special Rolls', 'Rolls premium con ingredientes especiales y únicos'),
('California Rolls', 'Rolls clásicos estilo California con variaciones'),
('Rolls Calientes', 'Rolls apanados, fritos o tempura'),
('Rolls Nikkey Especial', 'Rolls con influencia peruana y salsas especiales'),
('Nikkey Sin Arroz', 'Rolls envueltos en palta u otros ingredientes sin arroz'),
('Rolls Veggies', 'Rolls sin productos animales'),
('Envuelto Queso Crema', 'Rolls envueltos o cubiertos con queso crema'),
('Promociones', 'Combos y promociones especiales');

INSERT INTO productos (nombre, id_categoria, precio_venta) VALUES
-- SPECIAL ROLLS
('Avocado Rolls', 1, 4900),
('Bagel rolls', 1, 4900),
('Ebi Cheese Rolls', 1, 4900),
('Ebi Sake', 1, 4900),
('Rainbow Rolls', 1, 4900),
('Spyci Rolls', 1, 4900),
('Tako Fish', 1, 4900),
('Tako Rolls', 1, 4900),
('Teriyaki Rolls', 1, 4900),
('Tery Rolls', 1, 4900),
('Tori Crocante', 1, 4900),
-- California Rolls
('California Almond', 2, 3900),
('California Ebi', 2, 3900),
('California Maki', 2, 3900),
('California Sake', 2, 3900),
('California Smoked', 2, 3900),
('California Tako', 2, 3900),
('California Tempura', 2, 3900),
('California Tery', 2, 3900),
-- ROLLS CALIENTES 
('Almond Furay', 3, 4900),
('Bife Rolls', 3, 4900),
('Cheese Furay', 3, 4900),
('Ebi Cheese Furay', 3, 4900),
('Ebi Katzu', 3, 4900),
('Kani Hot', 3, 4900),
('Mantecooso Biffe', 3, 4800),
('Sake Cheese Tempura', 3, 4800),
('Smoked Hot', 3, 4800),
('Tery Furay', 3, 4600),
('Tonkatsu', 3, 4900),
-- ROLLS NIKKEY ESPECIAL
('Acevichado Rolls', 4, 6500),
('Acevichado Sake Tuna', 4, 6500),
('Acevichado Tuna', 4, 6500),
('Atai Premium', 4, 7990),
('Ceviche Rolls', 4, 8990),
('Crish Rolls', 4, 6500),
('Ebi Fresh Nikkiey', 4, 6500),
('Ebi Tory Furay', 4, 6500),
('Ebi Tori Rolls', 4, 6500),
('Edu Furay', 4, 6500),
('Fish Fresh', 4, 6500),
('Huancaina Chicken', 4, 6500),
('Huancaina Furay', 4, 6500),
('Iberico Rolls', 4, 6500),
('Sake Fresh Nikkiey', 4, 6500),
('Tako Spicy Acevichado', 4, 6500),
-- ROLLS NIKKEY SIN ARROZ 
('Almond Chicken', 5, 6900),
('Atai Fish', 5, 6900),
('Atai Oriental', 5, 6900),
('Atai Sake', 5, 6900),
('Fresh Oriental', 5, 6900),
('Futomaki Tempura', 5 ,6900),
('Tempura Maki Rolls', 5, 6900),
-- ROLLS VEGGIES
('California Veggie', 6, 4500),
('Pimento Tempura', 6, 4500),
('Veggie Cheese', 6, 4500),
('Veggie Fresh', 6, 4500),
('Veggie Furay', 6, 4500),
('Veggie Sin Arroz', 6, 4500),
('Veggie Tempura', 6, 4500),
-- ENVUELTO EN QUESO CREMA 
('Ebi Cheese', 7, 4900),
('Ebi Tempura Cheese', 7 , 4900),
('Kani Cheese', 7, 4900),
('Sake Cheese', 7 , 4500),
('Tako Cheese', 7 , 4500),
('Tori Cheese', 7 , 4500),
-- PROMOCIONES 
('Promo 20', 8 , 7900),
('Promo 20 sin arroz', 8 , 8990),
('Promo 40 Tempura', 8 , 12990),
('Promo 30 Mixta', 8 , 11490),
('Promo 30 Veggie', 8 , 11490),
('Promo 40 Mixta', 8 , 14990),
('Promo 60 Familiar', 8 , 17990),
('Promo 50 Mixta', 8 , 18990),
('Promo 60 Mixta', 8 , 21990),
('Promo 70 Mixta', 8 , 25990),
('Promo 80 Mixta', 8 , 29990),
('Promo HandRolls', 8, 6000);

INSERT INTO recetas (id_producto, id_insumo, cantidad_requerida) VALUES
-- Avocado Rolls (id_producto: 1)
(1, 22, 0.180), 
(1, 23, 1.000), 
(1, 7, 0.080), 
(1, 25, 0.015), 
(1, 30, 0.010), -- CORREGIDO: ID 30 para Salsa de Soja

-- Bagel Rolls (id_producto: 2)
(2, 22, 0.190), 
(2, 23, 1.000), 
(2, 15, 0.090), 
(2, 19, 0.040), 
(2, 8, 0.030), 

-- Ebi Cheese Rolls (id_producto: 3)
(3, 22, 0.200), 
(3, 23, 1.000), 
(3, 1, 0.070), 
(3, 19, 0.050), 
(3, 25, 0.010), 

-- Ebi Sake (id_producto: 4)
(4, 22, 0.185), 
(4, 23, 1.000), 
(4, 1, 0.060), 
(4, 2, 0.050), 
(4, 7, 0.040), 

-- Rainbow Rolls (id_producto: 5)
(5, 22, 0.195), 
(5, 23, 1.000), 
(5, 2, 0.040), 
(5, 3, 0.035), 
(5, 1, 0.030), 
(5, 7, 0.025), 

-- Spyci Rolls (id_producto: 6)
(6, 22, 0.190), 
(6, 23, 1.000), 
(6, 2, 0.080), 
(6, 27, 0.025), 
(6, 25, 0.008), 

-- Tako Fish (id_producto: 7)
(7, 22, 0.180), 
(7, 23, 1.000), 
(7, 5, 0.075), 
(7, 3, 0.045), 
(7, 8, 0.035), 

-- Tako Rolls (id_producto: 8)
(8, 22, 0.200), 
(8, 23, 1.000), 
(8, 5, 0.085), 
(8, 7, 0.045), 
(8, 25, 0.012), 

-- Teriyaki Rolls (id_producto: 9)
(9, 22, 0.185), 
(9, 23, 1.000), 
(9, 15, 0.095), 
(9, 26, 0.035), 
(9, 25, 0.010), 

-- Tery Rolls (id_producto: 10)
(10, 22, 0.190), 
(10, 23, 1.000), 
(10, 15, 0.088), 
(10, 7, 0.042), 
(10, 26, 0.028), 

-- Tori Crocante (id_producto: 11)
(11, 22, 0.195), 
(11, 23, 1.000), 
(11, 15, 0.092), 
(11, 28, 0.020), 
(11, 25, 0.015), 

-- California Almond (id_producto: 12)
(12, 22, 0.175), 
(12, 23, 1.000), 
(12, 6, 0.065), 
(12, 24, 0.025), 
(12, 7, 0.038), 

-- California Ebi (id_producto: 13)
(13, 22, 0.180), 
(13, 23, 1.000), 
(13, 1, 0.072), 
(13, 7, 0.044), 
(13, 8, 0.032), 

-- California Maki (id_producto: 14)
(14, 22, 0.170), 
(14, 23, 1.000), 
(14, 6, 0.068), 
(14, 7, 0.046), 
(14, 8, 0.036), 

-- California Sake (id_producto: 15)
(15, 22, 0.185), 
(15, 23, 1.000), 
(15, 2, 0.078), 
(15, 7, 0.041), 
(15, 8, 0.029), 

-- California Smoked (id_producto: 16)
(16, 22, 0.182), 
(16, 23, 1.000), 
(16, 2, 0.074), 
(16, 19, 0.036), 
(16, 7, 0.039), 

-- California Tako (id_producto: 17)
(17, 22, 0.178), 
(17, 23, 1.000), 
(17, 5, 0.082), 
(17, 7, 0.043), 
(17, 8, 0.031), 

-- California Tempura (id_producto: 18)
(18, 22, 0.192), 
(18, 23, 1.000), 
(18, 4, 0.088), 
(18, 7, 0.037), 
(18, 29, 0.018), 

-- California Tery (id_producto: 19)
(19, 22, 0.187), 
(19, 23, 1.000), 
(19, 15, 0.091), 
(19, 7, 0.040), 
(19, 26, 0.032), 

-- Almond Furay (id_producto: 20)
(20, 22, 0.195), 
(20, 23, 1.000), 
(20, 15, 0.085), 
(20, 24, 0.030), 
(20, 28, 0.025), 

-- Bife Rolls (id_producto: 21)
(21, 22, 0.190), 
(21, 23, 1.000), 
(21, 15, 0.095), 
(21, 7, 0.045), 
(21, 26, 0.028), 

-- Cheese Furay (id_producto: 22)
(22, 22, 0.185), 
(22, 23, 1.000), 
(22, 19, 0.055), 
(22, 20, 0.035), -- ID 20 Ahora existe (Queso Mantecoso)
(22, 28, 0.022), 

-- Ebi Cheese Furay (id_producto: 23)
(23, 22, 0.192), 
(23, 23, 1.000), 
(23, 1, 0.075), 
(23, 19, 0.048), 
(23, 28, 0.020), 

-- Ebi Katzu (id_producto: 24)
(24, 22, 0.188), 
(24, 23, 1.000), 
(24, 1, 0.080), 
(24, 28, 0.035), 
(24, 25, 0.012), 

-- Kani Hot (id_producto: 25)
(25, 22, 0.195), 
(25, 23, 1.000), 
(25, 6, 0.090), 
(25, 27, 0.030), 
(25, 25, 0.015), 

-- Mantecooso Biffe (id_producto: 26)
(26, 22, 0.190), 
(26, 23, 1.000), 
(26, 15, 0.092), 
(26, 20, 0.042), -- ID 20 Ahora existe
(26, 7, 0.038), 

-- Sake Cheese Tempura (id_producto: 27)
(27, 22, 0.185), 
(27, 23, 1.000), 
(27, 2, 0.082), 
(27, 19, 0.044), 
(27, 29, 0.025), 

-- Smoked Hot (id_producto: 28)
(28, 22, 0.192), 
(28, 23, 1.000), 
(28, 2, 0.078), 
(28, 27, 0.032), 
(28, 25, 0.014), 

-- Tery Furay (id_producto: 29)
(29, 22, 0.187), 
(29, 23, 1.000), 
(29, 15, 0.088), 
(29, 26, 0.035), 
(29, 28, 0.028), 

-- Tonkatsu (id_producto: 30)
(30, 22, 0.195), 
(30, 23, 1.000), 
(30, 15, 0.098), 
(30, 28, 0.040), 
(30, 26, 0.030), 

-- Acevichado Rolls (id_producto: 31)
(31, 22, 0.200), 
(31, 23, 1.000), 
(31, 2, 0.085), 
(31, 27, 0.038), 
(31, 25, 0.016), 

-- Acevichado Sake Tuna (id_producto: 32)
(32, 22, 0.205), 
(32, 23, 1.000), 
(32, 2, 0.065), 
(32, 3, 0.055), 
(32, 27, 0.040), 

-- Acevichado Tuna (id_producto: 33)
(33, 22, 0.198), 
(33, 23, 1.000), 
(33, 3, 0.095), 
(33, 27, 0.036), 
(33, 25, 0.018), 

-- Atai Premium (id_producto: 34)
(34, 22, 0.210), 
(34, 23, 1.000), 
(34, 2, 0.070), 
(34, 3, 0.060), 
(34, 1, 0.050), 
(34, 27, 0.045), 

-- Ceviche Rolls (id_producto: 35)
(35, 22, 0.195), 
(35, 23, 1.000), 
(35, 3, 0.088), 
(35, 8, 0.042), 
(35, 27, 0.050), 

-- Crish Rolls (id_producto: 36)
(36, 22, 0.190), 
(36, 23, 1.000), 
(36, 15, 0.090), 
(36, 24, 0.028), 
(36, 25, 0.020), 

-- Ebi Fresh Nikkiey (id_producto: 37)
(37, 22, 0.185), 
(37, 23, 1.000), 
(37, 1, 0.082), 
(37, 8, 0.044), 
(37, 27, 0.032), 

-- Ebi Tory Furay (id_producto: 38)
(38, 22, 0.192), 
(38, 23, 1.000), 
(38, 1, 0.078), 
(38, 15, 0.045), 
(38, 28, 0.030), 

-- Ebi Tori Rolls (id_producto: 39)
(39, 22, 0.188), 
(39, 23, 1.000), 
(39, 1, 0.075), 
(39, 15, 0.050), 
(39, 7, 0.040), 

-- Edu Furay (id_producto: 40)
(40, 22, 0.195), 
(40, 23, 1.000), 
(40, 15, 0.092), 
(40, 19, 0.048), 
(40, 28, 0.035), 

-- Fish Fresh (id_producto: 41)
(41, 22, 0.180), 
(41, 23, 1.000), 
(41, 3, 0.085), 
(41, 8, 0.035),

-- Huancaina Chicken (id_producto: 42)
(42, 22, 0.185), 
(42, 23, 1.000), 
(42, 15, 0.090), 
(42, 28, 0.030),

-- Huancaina Furay (id_producto: 43)
(43, 22, 0.190), 
(43, 23, 1.000), 
(43, 15, 0.088), 
(43, 28, 0.032),

-- Iberico Rolls (id_producto: 44)
(44, 22, 0.195), 
(44, 23, 1.000), 
(44, 2, 0.080), 
(44, 19, 0.040),

-- Sake Fresh Nikkiey (id_producto: 45)
(45, 22, 0.188), 
(45, 23, 1.000), 
(45, 2, 0.082), 
(45, 8, 0.038),

-- Tako Spicy Acevichado (id_producto: 46)
(46, 22, 0.192), 
(46, 23, 1.000), 
(46, 5, 0.085), 
(46, 27, 0.035),

-- Almond Chicken (id_producto: 47)
(47, 22, 0.185), 
(47, 23, 1.000), 
(47, 15, 0.092), 
(47, 24, 0.025),

-- Atai Fish (id_producto: 48)
(48, 22, 0.190),
(48, 23, 1.000),
(48, 3, 0.078), 
(48, 1, 0.045),

-- Atai Oriental (id_producto: 49)
(49, 22, 0.195), 
(49, 23, 1.000), 
(49, 2, 0.075), 
(49, 15, 0.055),

-- Atai Sake (id_producto: 50)
(50, 22, 0.188), 
(50, 23, 1.000), 
(50, 2, 0.085), 
(50, 7, 0.042),

-- Fresh Oriental (id_producto: 51)
(51, 22, 0.185),
(51, 23, 1.000), 
(51, 3, 0.080), 
(51, 8, 0.040),

-- Futomaki Tempura (id_producto: 52)
(52, 22, 0.200), 
(52, 23, 1.000), 
(52, 4, 0.090), 
(52, 29, 0.028),

-- Tempura Maki Rolls (id_producto: 53)
(53, 22, 0.195), 
(53, 23, 1.000), 
(53, 4, 0.085), 
(53, 7, 0.038),

-- California Veggie (id_producto: 54)
(54, 22, 0.175), 
(54, 23, 1.000),
(54, 7, 0.060), 
(54, 8, 0.045),

-- Pimento Tempura (id_producto: 55)
(55, 22, 0.180), 
(55, 23, 1.000), 
(55, 14, 0.055), 
(55, 29, 0.022),

-- Veggie Cheese (id_producto: 56)
(56, 22, 0.185), 
(56, 23, 1.000), 
(56, 19, 0.050), 
(56, 7, 0.048),

-- Veggie Fresh (id_producto: 57)
(57, 22, 0.178), 
(57, 23, 1.000), 
(57, 8, 0.052), 
(57, 11, 0.040),

-- Veggie Furay (id_producto: 58)
(58, 22, 0.190), 
(58, 23, 1.000), 
(58, 7, 0.058), 
(58, 28, 0.030),

-- Veggie Sin Arroz (id_producto: 59)
(59, 7, 0.120), 
(59, 8, 0.080), 
(59, 14, 0.060), 
(59, 11, 0.050),

-- Veggie Tempura (id_producto: 60)
(60, 22, 0.185), 
(60, 23, 1.000), 
(60, 7, 0.055), 
(60, 29, 0.025),

-- Ebi Cheese (id_producto: 61)
(61, 22, 0.188), 
(61, 23, 1.000), 
(61, 1, 0.075), 
(61, 19, 0.045),

-- Ebi Tempura Cheese (id_producto: 62)
(62, 22, 0.192), 
(62, 23, 1.000), 
(62, 4, 0.080), 
(62, 19, 0.042),

-- Kani Cheese (id_producto: 63)
(63, 22, 0.185), 
(63, 23, 1.000), 
(63, 6, 0.085), 
(63, 19, 0.048),

-- Sake Cheese (id_producto: 64)
(64, 22, 0.190), 
(64, 23, 1.000), 
(64, 2, 0.078), 
(64, 19, 0.044),

-- Tako Cheese (id_producto: 65)
(65, 22, 0.187), 
(65, 23, 1.000), 
(65, 5, 0.082), 
(65, 19, 0.040),

-- Tori Cheese (id_producto: 66)
(66, 22, 0.185), 
(66, 23, 1.000), 
(66, 15, 0.090), 
(66, 19, 0.046),

-- Promo 20 (id_producto: 67)
(67, 22, 0.400),
(67, 23, 2.000),
(67, 2, 0.160),
(67, 1, 0.120),

-- Promo 20 sin arroz (id_producto: 68)
(68, 7, 0.200),
(68, 2, 0.180),
(68, 1, 0.150),
(68, 8, 0.100),

-- Promo 40 Tempura (id_producto: 69)
(69, 22, 0.800),
(69, 23, 4.000),
(69, 4, 0.350),
(69, 29, 0.100),

-- Promo 30 Mixta (id_producto: 70)
(70, 22, 0.600),
(70, 23, 3.000),
(70, 2, 0.240),
(70, 15, 0.180),

-- Promo 30 Veggie (id_producto: 71)
(71, 22, 0.550),
(71, 23, 3.000),
(71, 7, 0.300),
(71, 8, 0.250),

-- Promo 40 Mixta (id_producto: 72)
(72, 22, 0.800),
(72, 23, 4.000),
(72, 2, 0.320),
(72, 1, 0.240),

-- Promo 60 Familiar (id_producto: 73)
(73, 22, 1.200),
(73, 23, 6.000),
(73, 2, 0.480),
(73, 15, 0.360),

-- Promo 50 Mixta (id_producto: 74)
(74, 22, 1.000),
(74, 23, 5.000),
(74, 2, 0.400),
(74, 1, 0.300),

-- Promo 60 Mixta (id_producto: 75)
(75, 22, 1.200),
(75, 23, 6.000),
(75, 2, 0.480),
(75, 3, 0.360),

-- Promo 70 Mixta (id_producto: 76)
(76, 22, 1.400),
(76, 23, 7.000),
(76, 2, 0.560),
(76, 1, 0.420),

-- Promo 80 Mixta (id_producto: 77)
(77, 22, 1.600),
(77, 23, 8.000),
(77, 2, 0.640),
(77, 15, 0.480),

-- Promo HandRolls (id_producto: 78)
(78, 22, 0.500),
(78, 23, 4.000),
(78, 2, 0.200),
(78, 7, 0.150);

INSERT INTO movimientos_inventario (id_insumo, tipo_movimiento, cantidad, costo_unitario, motivo, id_proveedor) VALUES
-- ENTRADAS (compras recientes)
(2, 'entrada', 5.00, 13500, 'Compra semanal salmón', 1),
(7, 'entrada', 10.00, 4400, 'Compra paltas', 2),
(22, 'entrada', 25.00, 2700, 'Compra arroz sushi', 2),
(1, 'entrada', 4.00, 6800, 'Compra camarón', 1),
(15, 'entrada', 8.00, 3700, 'Compra pollo', 1),
(19, 'entrada', 5.00, 6500, 'Compra queso crema', 2),
(23, 'entrada', 100.00, 180, 'Compra alga nori', 2),
(25, 'entrada', 2.00, 3500, 'Compra sésamo', 2),

-- SALIDAS (consumo producción)
(2, 'salida', 2.50, NULL, 'Consumo rolls salmón', NULL),
(7, 'salida', 3.20, NULL, 'Consumo rolls palta', NULL),
(22, 'salida', 8.50, NULL, 'Consumo arroz', NULL),
(1, 'salida', 1.80, NULL, 'Consumo camarón', NULL),
(15, 'salida', 4.20, NULL, 'Consumo pollo', NULL),
(19, 'salida', 2.10, NULL, 'Consumo queso crema', NULL),
(23, 'salida', 45.00, NULL, 'Consumo alga nori', NULL),
(25, 'salida', 0.80, NULL, 'Consumo sésamo', NULL),

-- AJUSTES (conteo físico)
(2, 'ajuste', -0.30, NULL, 'Ajuste por merma salmón', NULL),
(7, 'ajuste', -0.50, NULL, 'Ajuste paltas maduras', NULL),
(25, 'ajuste', 0.20, NULL, 'Ajuste positivo sésamo', NULL),
(23, 'ajuste', -5.00, NULL, 'Ajuste por rotura algas', NULL),

-- PÉRDIDAS
(7, 'perdida', 0.80, NULL, 'Pérdida paltas en mal estado', NULL),
(8, 'perdida', 0.30, NULL, 'Pérdida pepinos', NULL),
(22, 'perdida', 1.20, NULL, 'Arroz derramado', NULL),
(19, 'perdida', 0.25, NULL, 'Queso crema vencido', NULL),

-- MÁS ENTRADAS
(3, 'entrada', 6.00, 9800, 'Compra atún', 1),
(4, 'entrada', 3.00, 11000, 'Compra camarón tempura', 1),
(5, 'entrada', 2.00, 13000, 'Compra pulpo', 1),
(6, 'entrada', 5.00, 6000, 'Compra kanikama', 1),
(8, 'entrada', 4.00, 2000, 'Compra pepino', 2),
(26, 'entrada', 3.00, 3000, 'Compra salsa teriyaki', 2),
(27, 'entrada', 2.00, 4000, 'Compra salsa acevichada', 2),

-- MÁS SALIDAS
(3, 'salida', 2.80, NULL, 'Consumo atún', NULL),
(4, 'salida', 1.50, NULL, 'Consumo camarón tempura', NULL),
(5, 'salida', 0.90, NULL, 'Consumo pulpo', NULL),
(6, 'salida', 3.20, NULL, 'Consumo kanikama', NULL),
(8, 'salida', 2.10, NULL, 'Consumo pepino', NULL),
(26, 'salida', 1.30, NULL, 'Consumo salsa teriyaki', NULL),
(27, 'salida', 0.95, NULL, 'Consumo salsa acevichada', NULL);

INSERT INTO ventas (fecha_venta, id_producto, cantidad, precio_unitario, costo_unitario_calculado, total_venta, canal_venta) VALUES
-- Ventas de julio 2024
('2024-07-01', 1, 2, 8990, 3200, 17980, 'whatsapp'),
('2024-07-01', 5, 1, 5990, 1800, 5990, 'local'),
('2024-07-01', 12, 1, 6990, 2500, 6990, 'delivery_app'),

('2024-07-02', 2, 1, 8590, 2800, 8590, 'whatsapp'),
('2024-07-02', 9, 2, 7290, 2500, 14580, 'delivery_app'),
('2024-07-02', 16, 1, 5490, 1500, 5490, 'local'),

('2024-07-03', 12, 1, 9190, 3500, 9190, 'telefono'),
('2024-07-03', 18, 1, 7690, 2700, 7690, 'delivery_app'),
('2024-07-03', 25, 3, 4900, 1600, 14700, 'whatsapp'),

('2024-07-04', 20, 1, 24990, 8500, 24990, 'whatsapp'),
('2024-07-04', 5, 3, 5990, 1800, 17970, 'local'),
('2024-07-04', 31, 2, 6500, 2200, 13000, 'delivery_app'),

('2024-07-05', 1, 1, 8990, 3200, 8990, 'delivery_app'),
('2024-07-05', 8, 2, 6790, 2300, 13580, 'whatsapp'),
('2024-07-05', 22, 1, 4900, 1700, 4900, 'local'),

('2024-07-06', 35, 1, 8990, 3800, 8990, 'telefono'),
('2024-07-06', 42, 2, 6500, 2100, 13000, 'whatsapp'),
('2024-07-06', 54, 1, 4500, 1200, 4500, 'local'),

('2024-07-07', 67, 1, 7900, 2800, 7900, 'delivery_app'),
('2024-07-07', 15, 2, 6490, 2000, 12980, 'whatsapp'),
('2024-07-07', 29, 1, 4600, 1500, 4600, 'local'),

('2024-07-08', 3, 1, 7990, 2900, 7990, 'telefono'),
('2024-07-08', 11, 2, 6990, 2400, 13980, 'whatsapp'),
('2024-07-08', 47, 1, 6900, 2300, 6900, 'delivery_app'),

('2024-07-09', 72, 1, 14990, 5200, 14990, 'whatsapp'),
('2024-07-09', 6, 3, 7590, 2600, 22770, 'local'),
('2024-07-09', 38, 1, 6500, 2100, 6500, 'delivery_app'),

('2024-07-10', 1, 2, 8990, 3200, 17980, 'whatsapp'),
('2024-07-10', 19, 1, 5990, 1900, 5990, 'local'),
('2024-07-10', 61, 2, 4900, 1600, 9800, 'delivery_app'),

-- Ventas promocionales grandes
('2024-07-11', 73, 1, 17990, 6500, 17990, 'whatsapp'),
('2024-07-11', 75, 1, 21990, 7800, 21990, 'telefono'),
('2024-07-11', 77, 1, 29990, 10500, 29990, 'whatsapp'),

('2024-07-12', 4, 2, 8290, 3000, 16580, 'delivery_app'),
('2024-07-12', 27, 1, 4800, 1600, 4800, 'local'),
('2024-07-12', 56, 3, 4500, 1300, 13500, 'whatsapp'),

('2024-07-13', 13, 1, 6490, 2100, 6490, 'delivery_app'),
('2024-07-13', 33, 2, 6500, 2200, 13000, 'whatsapp'),
('2024-07-13', 66, 1, 4500, 1500, 4500, 'local'),

('2024-07-14', 7, 1, 6990, 2400, 6990, 'telefono'),
('2024-07-14', 41, 2, 6500, 2100, 13000, 'whatsapp'),
('2024-07-14', 78, 1, 6000, 2000, 6000, 'delivery_app'),

('2024-07-15', 2, 3, 8590, 2800, 25770, 'whatsapp'),
('2024-07-15', 23, 1, 4900, 1700, 4900, 'local'),
('2024-07-15', 58, 2, 4500, 1400, 9000, 'delivery_app');


INSERT INTO alertas_stock (id_insumo, tipo_alerta, nivel_actual, nivel_minimo, leida) VALUES
(1, 'sin_stock', 0.00, 5.00, FALSE),           -- Salmón AGOTADO
(2, 'stock_critico', 0.80, 4.00, FALSE),       -- Palta CRÍTICO (0.8kg vs 4kg mínimo)
(8, 'stock_critico', 1.20, 3.00, FALSE),       -- Pollo CRÍTICO
-- Alertas de stock mínimo (próximo a agotarse)
(3, 'stock_minimo', 4.50, 5.00, TRUE),         -- Atún en mínimo (leída)
(5, 'stock_minimo', 2.80, 3.00, FALSE),        -- Queso Crema en mínimo
(10, 'stock_minimo', 0.40, 0.50, FALSE),       -- Ciboulette en mínimo
-- Alertas resueltas (ya fueron leídas y atendidas)
(4, 'stock_minimo', 8.00, 2.00, TRUE),         -- Camarón - ya se repuso
(6, 'stock_critico', 12.00, 15.00, TRUE);      -- Arroz - ya se repuso


INSERT INTO gastos_operativos (fecha_gasto, categoria, descripcion, monto, usuario_registro) VALUES
('2024-06-01', 'arriendo', 'Arriendo local Walker Martinez 3356', 450000, 'Fernando Angulo'),
('2024-07-01', 'arriendo', 'Arriendo local mes de Julio', 450000, 'Fernando Angulo'),
('2024-06-05', 'sueldos', 'Pago sueldos quincena 1 - Junio', 320000, 'Fernando Angulo'),
('2024-06-20', 'sueldos', 'Pago sueldos quincena 2 - Junio', 320000, 'Fernando Angulo'),
('2024-07-05', 'sueldos', 'Pago sueldos quincena 1 - Julio', 330000, 'Fernando Angulo'),
('2024-06-08', 'servicios_basicos', 'Cuenta de luz - Mayo', 65000, 'Pedro Martínez'),
('2024-06-10', 'servicios_basicos', 'Cuenta de agua - Mayo', 35000, 'Pedro Martínez'),
('2024-06-12', 'servicios_basicos', 'Internet y teléfono', 45000, 'Pedro Martínez'),
('2024-07-09', 'servicios_basicos', 'Cuenta de luz - Junio', 68000, 'Pedro Martínez'),
('2024-06-03', 'marketing', 'Publicidad Instagram y Facebook', 25000, 'Fernando Angulo'),
('2024-06-15', 'marketing', 'Flyers promocionales', 15000, 'Fernando Angulo'),
('2024-07-02', 'marketing', 'Promoción en Google Maps', 20000, 'Fernando Angulo'),
('2024-06-06', 'otros', 'Compra material de oficina', 25000, 'Pedro Martínez'),
('2024-06-14', 'otros', 'Mantenimiento equipos cocina', 40000, 'Ana Silva'),
('2024-06-18', 'otros', 'Limpieza profunda local', 30000, 'Carlos Rodríguez'),
('2024-06-25', 'otros', 'Reparación vitrina refrigerada', 75000, 'Fernando Angulo'),
('2024-07-07', 'otros', 'Compra uniformes personal', 60000, 'Fernando Angulo');


INSERT INTO usuarios (nombre, email, password_hash, rol, activo) VALUES
('Fernando Angulo', 'fernandoangulo14@ataisushi.cl', '$2y$10$rQdS5PkM8qW9tYzVlLx8OuJZQ7nBvC2wE3fH6jK8mN9pL1rT4sD0y', 'administrador', TRUE),
('Pedro Martínez', 'pedromart@ataisushi.cl', '$2y$10$tQ8wE5rT2yU4iP6oK9mN1pL3rT5uY7iO0qW2eR4tY6uI8oP1aS3dF5', 'cajero', TRUE),
('Ana Silva', 'anita.silva@ataisushi.cl', '$2y$10$uR9tY2wE4iP6oK8mN1pL3rT5uY7iO0qW2eR4tY6uI8oP1aS3dF5gH7', 'cocina', TRUE),
('Carlos Rodríguez', 'carlitos.rodr@ataisushi.cl', '$2y$10$vS0wE2rT4yU6iP8oK9mN1pL3rT5uY7iO0qW2eR4tY6uI8oP1aS3dF5gH7', 'barra', TRUE);