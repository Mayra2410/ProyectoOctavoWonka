-- MySQL dump 10.13  Distrib 8.0.28, for Win64 (x86_64)
--
-- Host: localhost    Database: wonka
-- ------------------------------------------------------
-- Server version	8.0.28

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cierres_diarios`
--

DROP TABLE IF EXISTS `cierres_diarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cierres_diarios` (
  `id_cierre` int NOT NULL AUTO_INCREMENT,
  `fecha` date NOT NULL,
  `ingresos_totales` decimal(12,2) DEFAULT NULL,
  `egresos_totales` decimal(12,2) DEFAULT NULL,
  `reserva_proveedores` decimal(12,2) DEFAULT NULL,
  `utilidad_neta` decimal(12,2) DEFAULT NULL,
  `ventas_count` int DEFAULT NULL,
  `generado_en` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_cierre`),
  UNIQUE KEY `fecha` (`fecha`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cierres_diarios`
--

LOCK TABLES `cierres_diarios` WRITE;
/*!40000 ALTER TABLE `cierres_diarios` DISABLE KEYS */;
/*!40000 ALTER TABLE `cierres_diarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clientes`
--

DROP TABLE IF EXISTS `clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `clientes` (
  `id_cliente` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `email` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `tipo` enum('MINORISTA','MAYORISTA') DEFAULT 'MINORISTA',
  `fecha_registro` date DEFAULT (curdate()),
  `categoria_comprador` enum('OCASIONAL','FRECUENTE') DEFAULT 'OCASIONAL',
  `imagen_cliente` longtext,
  `estatus` varchar(10) DEFAULT 'ACTIVO',
  `notas` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_cliente`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `clientes_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clientes`
--

LOCK TABLES `clientes` WRITE;
/*!40000 ALTER TABLE `clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `compras_materia_prima`
--

DROP TABLE IF EXISTS `compras_materia_prima`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `compras_materia_prima` (
  `id_compra` int NOT NULL AUTO_INCREMENT,
  `materia_prima_id` int NOT NULL,
  `cantidad` decimal(10,2) NOT NULL,
  `costo_unitario` decimal(10,2) NOT NULL,
  `fecha_compra` datetime DEFAULT CURRENT_TIMESTAMP,
  `proveedor_id` int DEFAULT NULL,
  `observaciones` varchar(200) DEFAULT NULL,
  `estatus_compra` enum('PENDIENTE','PAGADO','RECIBIDO','CANCELADO') NOT NULL DEFAULT 'PENDIENTE',
  PRIMARY KEY (`id_compra`),
  KEY `materia_prima_id` (`materia_prima_id`),
  KEY `proveedor_id` (`proveedor_id`),
  CONSTRAINT `compras_materia_prima_ibfk_1` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`),
  CONSTRAINT `compras_materia_prima_ibfk_2` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `compras_materia_prima`
--

LOCK TABLES `compras_materia_prima` WRITE;
/*!40000 ALTER TABLE `compras_materia_prima` DISABLE KEYS */;
/*!40000 ALTER TABLE `compras_materia_prima` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cortes_caja`
--

DROP TABLE IF EXISTS `cortes_caja`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `cortes_caja` (
  `id_corte` int NOT NULL AUTO_INCREMENT,
  `fecha_inicio` date NOT NULL,
  `fecha_fin` date NOT NULL,
  `total_ingresos` decimal(12,2) NOT NULL,
  `total_egresos` decimal(12,2) NOT NULL,
  `monto_reserva` decimal(12,2) NOT NULL,
  `utilidad_neta` decimal(12,2) NOT NULL,
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_corte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cortes_caja`
--

LOCK TABLES `cortes_caja` WRITE;
/*!40000 ALTER TABLE `cortes_caja` DISABLE KEYS */;
/*!40000 ALTER TABLE `cortes_caja` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalles_produccion`
--

DROP TABLE IF EXISTS `detalles_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_produccion` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `orden_produccion_id` int NOT NULL,
  `materia_prima_id` int NOT NULL,
  `cantidad_requerida` decimal(10,2) NOT NULL,
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  `subtotal` decimal(12,2) GENERATED ALWAYS AS ((`cantidad_requerida` * `costo_unitario`)) STORED,
  `observaciones` varchar(200) DEFAULT NULL,
  PRIMARY KEY (`id_detalle`),
  KEY `orden_produccion_id` (`orden_produccion_id`),
  KEY `materia_prima_id` (`materia_prima_id`),
  CONSTRAINT `detalles_produccion_ibfk_1` FOREIGN KEY (`orden_produccion_id`) REFERENCES `ordenes_produccion` (`id_orden_produccion`),
  CONSTRAINT `detalles_produccion_ibfk_2` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_produccion`
--

LOCK TABLES `detalles_produccion` WRITE;
/*!40000 ALTER TABLE `detalles_produccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalles_produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `detalles_ventas`
--

DROP TABLE IF EXISTS `detalles_ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `detalles_ventas` (
  `id_detalle` int NOT NULL AUTO_INCREMENT,
  `venta_id` int NOT NULL,
  `producto_id` int NOT NULL,
  `cantidad` int NOT NULL,
  `precio_unitario` decimal(10,2) NOT NULL,
  `subtotal` decimal(10,2) GENERATED ALWAYS AS ((`cantidad` * `precio_unitario`)) STORED,
  PRIMARY KEY (`id_detalle`),
  KEY `venta_id` (`venta_id`),
  KEY `producto_id` (`producto_id`),
  CONSTRAINT `detalles_ventas_ibfk_1` FOREIGN KEY (`venta_id`) REFERENCES `ventas` (`id_venta`),
  CONSTRAINT `detalles_ventas_ibfk_2` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `detalles_ventas`
--

LOCK TABLES `detalles_ventas` WRITE;
/*!40000 ALTER TABLE `detalles_ventas` DISABLE KEYS */;
/*!40000 ALTER TABLE `detalles_ventas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `empleados`
--

DROP TABLE IF EXISTS `empleados`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `empleados` (
  `id_empleado` int NOT NULL AUTO_INCREMENT,
  `usuario_id` int DEFAULT NULL,
  `nombre` varchar(100) NOT NULL,
  `apellido` varchar(100) NOT NULL,
  `dni_cedula` varchar(20) NOT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `puesto` enum('GERENTE','CHOCOLATERO','CONTROL_CALIDAD','VENTAS','LOGISTICA','MANTENIMIENTO') NOT NULL,
  `fecha_contratacion` date DEFAULT (curdate()),
  `salario_mensual` decimal(10,2) DEFAULT NULL,
  `imagen_empleado` longtext,
  `estatus` varchar(10) DEFAULT 'ACTIVO',
  PRIMARY KEY (`id_empleado`),
  UNIQUE KEY `dni_cedula` (`dni_cedula`),
  UNIQUE KEY `usuario_id` (`usuario_id`),
  UNIQUE KEY `email` (`email`),
  CONSTRAINT `empleados_ibfk_1` FOREIGN KEY (`usuario_id`) REFERENCES `usuarios` (`id_usuario`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `empleados`
--

LOCK TABLES `empleados` WRITE;
/*!40000 ALTER TABLE `empleados` DISABLE KEYS */;
INSERT INTO `empleados` VALUES (1,1,'Mayra','Hernández','12345678-A','555-9000','mayrahdezao@gmail.com',NULL,'GERENTE','2026-04-18',2500.00,NULL,'ACTIVO');
/*!40000 ALTER TABLE `empleados` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `inventario_movimientos`
--

DROP TABLE IF EXISTS `inventario_movimientos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `inventario_movimientos` (
  `id_movimiento` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `tipo_movimiento` enum('ENTRADA','SALIDA','AJUSTE') NOT NULL,
  `cantidad` int NOT NULL,
  `motivo` varchar(255) NOT NULL,
  `usuario_id` varchar(50) DEFAULT NULL,
  `fecha_movimiento` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_movimiento`),
  KEY `fk_movimiento_producto` (`producto_id`),
  CONSTRAINT `fk_movimiento_producto` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `inventario_movimientos`
--

LOCK TABLES `inventario_movimientos` WRITE;
/*!40000 ALTER TABLE `inventario_movimientos` DISABLE KEYS */;
/*!40000 ALTER TABLE `inventario_movimientos` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_validar_inventario_activo` BEFORE INSERT ON `inventario_movimientos` FOR EACH ROW BEGIN
    DECLARE v_activo BOOLEAN;

    -- Verificar si el producto del movimiento está activo
    SELECT activo INTO v_activo 
    FROM productos 
    WHERE id_producto = NEW.producto_id;

    IF v_activo = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Error: No se permiten movimientos de inventario para productos INACTIVOS.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `materias_primas`
--

DROP TABLE IF EXISTS `materias_primas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `materias_primas` (
  `id_materia_prima` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `unidad_medida` varchar(20) NOT NULL,
  `stock_actual` decimal(10,2) DEFAULT '0.00',
  `stock_minimo` decimal(10,2) DEFAULT '10.00',
  `costo_unitario` decimal(10,2) DEFAULT NULL,
  `proveedor_id` int DEFAULT NULL,
  `fecha_ultima_compra` date DEFAULT NULL,
  `porcentaje_merma` decimal(5,2) DEFAULT '0.00',
  `imagen_materia` text,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_materia_prima`),
  KEY `proveedor_id` (`proveedor_id`),
  CONSTRAINT `materias_primas_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id_proveedor`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `materias_primas`
--

LOCK TABLES `materias_primas` WRITE;
/*!40000 ALTER TABLE `materias_primas` DISABLE KEYS */;
/*!40000 ALTER TABLE `materias_primas` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ordenes_produccion`
--

DROP TABLE IF EXISTS `ordenes_produccion`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ordenes_produccion` (
  `id_orden_produccion` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `cantidad_requerida` int NOT NULL,
  `fecha_inicio` datetime DEFAULT NULL,
  `fecha_fin` datetime DEFAULT NULL,
  `estado` enum('PENDIENTE','EN_PROCESO','COMPLETADA','CANCELADA') DEFAULT 'PENDIENTE',
  `lote` varchar(50) DEFAULT NULL,
  `prioridad` enum('BAJA','MEDIA','ALTA','URGENTE') DEFAULT 'MEDIA',
  `observaciones` varchar(200) DEFAULT NULL,
  `costo_total_real` decimal(12,2) DEFAULT NULL,
  `receta_id` int DEFAULT NULL,
  PRIMARY KEY (`id_orden_produccion`),
  UNIQUE KEY `lote` (`lote`),
  KEY `producto_id` (`producto_id`),
  KEY `receta_id` (`receta_id`),
  CONSTRAINT `ordenes_produccion_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`),
  CONSTRAINT `ordenes_produccion_ibfk_2` FOREIGN KEY (`receta_id`) REFERENCES `recetas` (`id_receta`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ordenes_produccion`
--

LOCK TABLES `ordenes_produccion` WRITE;
/*!40000 ALTER TABLE `ordenes_produccion` DISABLE KEYS */;
/*!40000 ALTER TABLE `ordenes_produccion` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `pagos_proveedores`
--

DROP TABLE IF EXISTS `pagos_proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `pagos_proveedores` (
  `id_pago` int NOT NULL AUTO_INCREMENT,
  `proveedor_id` int NOT NULL,
  `fecha_pago` datetime DEFAULT CURRENT_TIMESTAMP,
  `monto` decimal(12,2) NOT NULL,
  `metodo_pago` enum('EFECTIVO','TRANSFERENCIA') DEFAULT 'EFECTIVO',
  `compra_id` int DEFAULT NULL,
  `observaciones` varchar(200) DEFAULT NULL,
  `usuario_registro` varchar(50) DEFAULT NULL,
  `estatus_compra` enum('PENDIENTE','PAGADO','CANCELADO') DEFAULT NULL,
  `numero_comprobante` varchar(75) DEFAULT NULL,
  PRIMARY KEY (`id_pago`),
  KEY `proveedor_id` (`proveedor_id`),
  KEY `compra_id` (`compra_id`),
  CONSTRAINT `pagos_proveedores_ibfk_1` FOREIGN KEY (`proveedor_id`) REFERENCES `proveedores` (`id_proveedor`),
  CONSTRAINT `pagos_proveedores_ibfk_2` FOREIGN KEY (`compra_id`) REFERENCES `compras_materia_prima` (`id_compra`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `pagos_proveedores`
--

LOCK TABLES `pagos_proveedores` WRITE;
/*!40000 ALTER TABLE `pagos_proveedores` DISABLE KEYS */;
/*!40000 ALTER TABLE `pagos_proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `productos`
--

DROP TABLE IF EXISTS `productos`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `productos` (
  `id_producto` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `descripcion` varchar(200) DEFAULT NULL,
  `categoria` varchar(50) DEFAULT NULL,
  `precio_venta` decimal(10,2) NOT NULL,
  `costo_produccion_estimado` decimal(10,2) DEFAULT NULL,
  `stock_actual` int DEFAULT '0',
  `stock_minimo` int DEFAULT '10',
  `unidad_medida` varchar(20) DEFAULT 'unidad',
  `tiempo_produccion_minutos` int DEFAULT NULL,
  `imagen_producto` longtext,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `productos`
--

LOCK TABLES `productos` WRITE;
/*!40000 ALTER TABLE `productos` DISABLE KEYS */;
/*!40000 ALTER TABLE `productos` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `proveedores`
--

DROP TABLE IF EXISTS `proveedores`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `proveedores` (
  `id_proveedor` int NOT NULL AUTO_INCREMENT,
  `nombre` varchar(100) NOT NULL,
  `contacto` varchar(100) DEFAULT NULL,
  `telefono` varchar(20) DEFAULT NULL,
  `email` varchar(100) DEFAULT NULL,
  `direccion` varchar(200) DEFAULT NULL,
  `ruc` varchar(20) DEFAULT NULL,
  `notas` varchar(200) DEFAULT NULL,
  `activo` tinyint(1) DEFAULT '1',
  `fecha_registro` date DEFAULT (curdate()),
  PRIMARY KEY (`id_proveedor`),
  UNIQUE KEY `uc_nombre` (`nombre`),
  UNIQUE KEY `uc_ruc` (`ruc`),
  UNIQUE KEY `uc_telefono` (`telefono`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `proveedores`
--

LOCK TABLES `proveedores` WRITE;
/*!40000 ALTER TABLE `proveedores` DISABLE KEYS */;
/*!40000 ALTER TABLE `proveedores` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `recetas`
--

DROP TABLE IF EXISTS `recetas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas` (
  `id_receta` int NOT NULL AUTO_INCREMENT,
  `producto_id` int NOT NULL,
  `nombre_receta` varchar(100) DEFAULT NULL,
  `cantidad_lote` int DEFAULT '1',
  `instrucciones` text,
  `activo` tinyint(1) DEFAULT '1',
  PRIMARY KEY (`id_receta`),
  UNIQUE KEY `uc_producto_receta` (`producto_id`),
  CONSTRAINT `recetas_ibfk_1` FOREIGN KEY (`producto_id`) REFERENCES `productos` (`id_producto`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas`
--

LOCK TABLES `recetas` WRITE;
/*!40000 ALTER TABLE `recetas` DISABLE KEYS */;
/*!40000 ALTER TABLE `recetas` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_validar_producto_activo` BEFORE INSERT ON `recetas` FOR EACH ROW BEGIN
    DECLARE v_activo BOOLEAN;

    -- Buscamos el estado del producto
    SELECT activo INTO v_activo 
    FROM productos 
    WHERE id_producto = NEW.producto_id;

    -- Si el producto está inactivo (0), lanzamos un error
    IF v_activo = 0 THEN
        SIGNAL SQLSTATE '45000'
        SET MESSAGE_TEXT = 'Operación cancelada: No se puede crear una receta para un producto INACTIVO.';
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Table structure for table `recetas_detalle`
--

DROP TABLE IF EXISTS `recetas_detalle`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `recetas_detalle` (
  `id_receta_detalle` int NOT NULL AUTO_INCREMENT,
  `receta_id` int NOT NULL,
  `materia_prima_id` int NOT NULL,
  `cantidad_necesaria` decimal(10,4) NOT NULL,
  `cantidad_capturada` decimal(10,4) DEFAULT NULL,
  `unidad_capturada` varchar(20) DEFAULT NULL,
  `unidad_medida` varchar(20) DEFAULT NULL,
  PRIMARY KEY (`id_receta_detalle`),
  KEY `receta_id` (`receta_id`),
  KEY `materia_prima_id` (`materia_prima_id`),
  CONSTRAINT `recetas_detalle_ibfk_1` FOREIGN KEY (`receta_id`) REFERENCES `recetas` (`id_receta`),
  CONSTRAINT `recetas_detalle_ibfk_2` FOREIGN KEY (`materia_prima_id`) REFERENCES `materias_primas` (`id_materia_prima`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `recetas_detalle`
--

LOCK TABLES `recetas_detalle` WRITE;
/*!40000 ALTER TABLE `recetas_detalle` DISABLE KEYS */;
/*!40000 ALTER TABLE `recetas_detalle` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `reporte_diario_wonka`
--

DROP TABLE IF EXISTS `reporte_diario_wonka`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `reporte_diario_wonka` (
  `id_reporte` int NOT NULL AUTO_INCREMENT,
  `fecha` date DEFAULT NULL,
  `total_ganado` decimal(10,2) DEFAULT NULL,
  `total_gastado` decimal(10,2) DEFAULT NULL,
  `utilidad_neta` decimal(10,2) DEFAULT NULL,
  `total_ventas_realizadas` int DEFAULT NULL,
  `creado_el` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_reporte`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `reporte_diario_wonka`
--

LOCK TABLES `reporte_diario_wonka` WRITE;
/*!40000 ALTER TABLE `reporte_diario_wonka` DISABLE KEYS */;
/*!40000 ALTER TABLE `reporte_diario_wonka` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tarjetas_clientes`
--

DROP TABLE IF EXISTS `tarjetas_clientes`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `tarjetas_clientes` (
  `id_tarjeta` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int NOT NULL,
  `numero_encriptado` varchar(100) NOT NULL,
  `terminacion` varchar(4) NOT NULL,
  `banco` varchar(50) DEFAULT NULL,
  `activa` tinyint(1) DEFAULT '1',
  `fecha_registro` datetime DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_tarjeta`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `tarjetas_clientes_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id_cliente`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tarjetas_clientes`
--

LOCK TABLES `tarjetas_clientes` WRITE;
/*!40000 ALTER TABLE `tarjetas_clientes` DISABLE KEYS */;
/*!40000 ALTER TABLE `tarjetas_clientes` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `usuarios`
--

DROP TABLE IF EXISTS `usuarios`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `usuarios` (
  `id_usuario` int NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password_hash` varchar(255) NOT NULL,
  `email` varchar(100) NOT NULL,
  `rol` enum('GERENTE','CHOCOLATERO','CONTROL_CALIDAD','VENTAS','LOGISTICA','MANTENIMIENTO','CLIENTE') NOT NULL DEFAULT 'CLIENTE',
  `activo` tinyint(1) DEFAULT '1',
  `verificado` tinyint(1) DEFAULT '0',
  `codigo_verificacion` varchar(6) DEFAULT NULL,
  `intentos_fallidos` int DEFAULT '0',
  `bloqueado_hasta` datetime DEFAULT NULL,
  PRIMARY KEY (`id_usuario`),
  UNIQUE KEY `username` (`username`),
  UNIQUE KEY `email` (`email`)
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `usuarios`
--

LOCK TABLES `usuarios` WRITE;
/*!40000 ALTER TABLE `usuarios` DISABLE KEYS */;
INSERT INTO `usuarios` VALUES (1,'admin_mayra','pbkdf2:sha256:600000$mydI4uWl3X1q82s5$4c825c79b40a1915c640cb4466e7f40911460afb62d0f022607b903793f86488','mayrahdezao@gmail.com','GERENTE',1,1,NULL,0,NULL);
/*!40000 ALTER TABLE `usuarios` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `ventas`
--

DROP TABLE IF EXISTS `ventas`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `ventas` (
  `id_venta` int NOT NULL AUTO_INCREMENT,
  `cliente_id` int DEFAULT NULL,
  `fecha_venta` datetime DEFAULT CURRENT_TIMESTAMP,
  `total` decimal(12,2) NOT NULL,
  `metodo_pago` enum('EFECTIVO','TARJETA') DEFAULT NULL,
  `estado` enum('PENDIENTE','COMPLETADA','CANCELADA','ENTREGADA') DEFAULT 'PENDIENTE',
  PRIMARY KEY (`id_venta`),
  KEY `cliente_id` (`cliente_id`),
  CONSTRAINT `ventas_ibfk_1` FOREIGN KEY (`cliente_id`) REFERENCES `clientes` (`id_cliente`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `ventas`
--

LOCK TABLES `ventas` WRITE;
/*!40000 ALTER TABLE `ventas` DISABLE KEYS */;
/*!40000 ALTER TABLE `ventas` ENABLE KEYS */;
UNLOCK TABLES;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
/*!50003 CREATE*/ /*!50017 DEFINER=`root`@`localhost`*/ /*!50003 TRIGGER `tg_actualizar_cliente_frecuente` AFTER INSERT ON `ventas` FOR EACH ROW BEGIN
    DECLARE total_compras_mes INT;

    -- Contamos cuántas ventas ha hecho el cliente en el mes y año actual
    SELECT COUNT(*) INTO total_compras_mes
    FROM ventas
    WHERE cliente_id = NEW.cliente_id 
      AND MONTH(fecha_venta) = MONTH(NOW())
      AND YEAR(fecha_venta) = YEAR(NOW()); -- Precisión total

    -- Si tiene 5 o más compras en el mes, lo subimos a FRECUENTE
    IF total_compras_mes >= 5 THEN 
        UPDATE clientes 
        SET categoria_comprador = 'FRECUENTE' 
        WHERE id_cliente = NEW.cliente_id;
    END IF;
END */;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;

--
-- Dumping events for database 'wonka'
--
/*!50106 SET @save_time_zone= @@TIME_ZONE */ ;
/*!50106 DROP EVENT IF EXISTS `cierre_automatico_wonka` */;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `cierre_automatico_wonka` ON SCHEDULE EVERY 1 DAY STARTS '2026-04-18 22:59:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    INSERT INTO cierres_diarios (fecha, ingresos_totales, egresos_totales, reserva_proveedores, utilidad_neta, ventas_count)
    SELECT 
        CURDATE(),
        IFNULL(SUM(total), 0),
        (SELECT IFNULL(SUM(monto), 0) FROM pagos_proveedores WHERE DATE(fecha_pago) = CURDATE()),
        IFNULL(SUM(total), 0) * 0.20,
        (IFNULL(SUM(total), 0) - (SELECT IFNULL(SUM(monto), 0) FROM pagos_proveedores WHERE DATE(fecha_pago) = CURDATE()) - (IFNULL(SUM(total), 0) * 0.20)),
        COUNT(id_venta)
    FROM ventas
    WHERE DATE(fecha_venta) = CURDATE() AND estado = 'COMPLETADA';
END */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
/*!50106 DROP EVENT IF EXISTS `evt_limpieza_reportes_antiguos` */;;
DELIMITER ;;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;;
/*!50003 SET character_set_client  = utf8mb4 */ ;;
/*!50003 SET character_set_results = utf8mb4 */ ;;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;;
/*!50003 SET @saved_time_zone      = @@time_zone */ ;;
/*!50003 SET time_zone             = 'SYSTEM' */ ;;
/*!50106 CREATE*/ /*!50117 DEFINER=`root`@`localhost`*/ /*!50106 EVENT `evt_limpieza_reportes_antiguos` ON SCHEDULE EVERY 1 MONTH STARTS '2026-05-18 00:00:00' ON COMPLETION NOT PRESERVE ENABLE DO BEGIN
    -- Eliminamos registros de reportes diarios con más de 2 años de antigüedad
    DELETE FROM reporte_diario_wonka 
    WHERE fecha < DATE_SUB(CURRENT_DATE, INTERVAL 2 YEAR);
END */ ;;
/*!50003 SET time_zone             = @saved_time_zone */ ;;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;;
/*!50003 SET character_set_client  = @saved_cs_client */ ;;
/*!50003 SET character_set_results = @saved_cs_results */ ;;
/*!50003 SET collation_connection  = @saved_col_connection */ ;;
DELIMITER ;
/*!50106 SET TIME_ZONE= @save_time_zone */ ;

--
-- Dumping routines for database 'wonka'
--
/*!50003 DROP PROCEDURE IF EXISTS `sp_finalizar_venta_wonka` */;
/*!50003 SET @saved_cs_client      = @@character_set_client */ ;
/*!50003 SET @saved_cs_results     = @@character_set_results */ ;
/*!50003 SET @saved_col_connection = @@collation_connection */ ;
/*!50003 SET character_set_client  = utf8mb4 */ ;
/*!50003 SET character_set_results = utf8mb4 */ ;
/*!50003 SET collation_connection  = utf8mb4_0900_ai_ci */ ;
/*!50003 SET @saved_sql_mode       = @@sql_mode */ ;
/*!50003 SET sql_mode              = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION' */ ;
DELIMITER ;;
CREATE DEFINER=`root`@`localhost` PROCEDURE `sp_finalizar_venta_wonka`(
    IN p_cliente_id INT,
    IN p_total_final DECIMAL(10,2),
    IN p_metodo_pago VARCHAR(50),
    IN p_producto_id INT,
    IN p_cantidad_cajas INT,
    IN p_piezas_totales INT,
    IN p_precio_unitario DECIMAL(10,2)
)
BEGIN
    DECLARE v_venta_id INT;
    DECLARE v_stock_actual INT;
    
    -- Manejador de errores 
    DECLARE EXIT HANDLER FOR SQLEXCEPTION 
    BEGIN
        GET DIAGNOSTICS CONDITION 1 @p1 = RETURNED_SQLSTATE, @p2 = MESSAGE_TEXT;
        ROLLBACK;
        RESIGNAL SET MESSAGE_TEXT = @p2; 
    END;

    START TRANSACTION;

    INSERT INTO ventas (cliente_id, total, metodo_pago, fecha_venta, estado)
    VALUES (p_cliente_id, p_total_final, p_metodo_pago, NOW(), 'COMPLETADA');
    
    SET v_venta_id = LAST_INSERT_ID();

    INSERT INTO detalle_ventas (venta_id, producto_id, cantidad, precio_unitario)
    VALUES (v_venta_id, p_producto_id, p_cantidad_cajas, p_precio_unitario);

    SELECT stock_actual INTO v_stock_actual FROM productos WHERE id_producto = p_producto_id FOR UPDATE;

    IF v_stock_actual >= p_piezas_totales THEN
        UPDATE productos SET stock_actual = stock_actual - p_piezas_totales WHERE id_producto = p_producto_id;
    ELSE
        UPDATE ventas SET estado = 'PENDIENTE' WHERE id_venta = v_venta_id;

        INSERT INTO ordenes_produccion (producto_id, cantidad_requerida, lote, prioridad, estado, fecha_inicio, observaciones)
        VALUES (p_producto_id, p_piezas_totales, CONCAT('AUTO-', v_venta_id), 'URGENTE', 'PENDIENTE', NOW(), 
                CONCAT('Falta stock: Tenías ', v_stock_actual, ' y pidieron ', p_piezas_totales));
    END IF;

    COMMIT;
END ;;
DELIMITER ;
/*!50003 SET sql_mode              = @saved_sql_mode */ ;
/*!50003 SET character_set_client  = @saved_cs_client */ ;
/*!50003 SET character_set_results = @saved_cs_results */ ;
/*!50003 SET collation_connection  = @saved_col_connection */ ;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2026-04-18 10:03:16
