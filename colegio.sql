-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 09-10-2024 a las 03:36:03
-- Versión del servidor: 10.4.32-MariaDB
-- Versión de PHP: 8.2.12

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";


/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Base de datos: `colegio`
--

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `alumno`
--

CREATE TABLE `alumno` (
  `cedula` bigint(20) NOT NULL,
  `cedula_representante` bigint(20) DEFAULT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `fecha_nacimiento` date NOT NULL DEFAULT current_timestamp(),
  `curso` varchar(20) NOT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `genero` text NOT NULL,
  `email` varchar(255) NOT NULL DEFAULT 'example@example.com',
  `pago` float(10,2) NOT NULL,
  `matricula` int(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `alumno`
--

INSERT INTO `alumno` (`cedula`, `cedula_representante`, `nombre`, `fecha_nacimiento`, `curso`, `direccion`, `telefono`, `genero`, `email`, `pago`, `matricula`) VALUES
(18, 18662865, 'arthur trump', '2020-09-20', 'Segundo', 'Viento Norte', '0412', 'Masculino', 'gmail', 0.00, 0),
(182, 18662865, 'Ilon Motts', '2016-09-22', 'Sexto', 'viento norte', '0412', 'Masculino', 'gmail', 0.00, 0),
(191, 19214453, 'Maria Corina', '2013-09-29', '5to año', 'las mercedes', NULL, 'Femenino', '', 0.00, 0),
(192, 19836275, 'Rosa Meltrozo', '2011-09-22', '4to año', 'los mangos, sector 1', '0412', 'Femenino', 'gmail', 0.00, 0),
(1234, 123, 'Anlo fonseca', '2018-09-29', 'Octavo', 'españa', NULL, 'Masculino', 'gmail', 0.00, 0),
(7771, 777, 'rafa leao', '2019-09-29', 'Primero', NULL, NULL, 'Masculino', 'hotmail', 0.00, 0),
(12345, 123, 'Tomath Tuyukota', '2014-09-30', 'Noveno', 'nigeria', NULL, 'Masculino', 'gmail.com', 0.00, 0),
(237687122, 23768712, 'DANIELA ISABEL ZAMBRANO REYES', '2018-03-27', 'Primero', 'LA CURVA QLQ', '04146707509', 'Femenino', 'JEZV18@GMAIL.COM', 0.00, 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `registro_pagos`
--

CREATE TABLE `registro_pagos` (
  `id_factura` int(20) NOT NULL,
  `fecha_pago` date DEFAULT current_timestamp(),
  `hora` time DEFAULT current_timestamp(),
  `cedula_estudiante` bigint(20) DEFAULT NULL,
  `nombre_alumno` varchar(20) NOT NULL,
  `cedula_representante` bigint(20) DEFAULT NULL,
  `monto` double DEFAULT NULL,
  `tipo_pago` varchar(25) NOT NULL,
  `mes` varchar(20) NOT NULL,
  `curso` varchar(255) NOT NULL,
  `anulado` tinyint(1) DEFAULT 0
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `registro_pagos`
--

INSERT INTO `registro_pagos` (`id_factura`, `fecha_pago`, `hora`, `cedula_estudiante`, `nombre_alumno`, `cedula_representante`, `monto`, `tipo_pago`, `mes`, `curso`, `anulado`) VALUES
(23, '2024-09-20', '00:28:00', NULL, 'arthur trump', 18662865, 2000, 'Mensualidad', 'Septiembre', 'Primero', 0),
(24, '2024-09-20', '00:28:00', NULL, 'arthur trump', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Primero', 0),
(25, '2024-09-22', '23:45:48', NULL, 'arthur trump', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Segundo', 0),
(26, '2024-09-22', '23:45:48', NULL, 'arthur trump', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Segundo', 0),
(27, '2024-09-22', '23:50:04', NULL, 'Peter Parker', 19836275, 2000, 'Mensualidad', 'Octubre', '5to año', 0),
(28, '2024-09-22', '23:50:04', NULL, 'Rosa Meltrozo', 19836275, 2000, 'Mensualidad', 'Enero', '4to año', 0),
(29, '2024-09-23', '00:36:08', 191, 'Peter Parker', 19836275, 1500, 'Mensualidad', 'Agosto', '5to año', 0),
(30, '2024-09-23', '00:36:08', 192, 'Rosa Meltrozo', 19836275, 1500, 'Mensualidad', 'Agosto', '4to año', 0),
(31, '2024-09-23', '00:40:43', 18, 'arthur trump', 18662865, 1000, 'Mensualidad', 'Julio', 'Segundo', 0),
(32, '2024-09-23', '00:40:43', 182, 'Ilon Motts', 18662865, 1000, 'Mensualidad', 'Julio', 'Sexto', 0),
(33, '2024-09-23', '00:47:07', 191, 'Peter Parker', 19836275, 1000, 'Mensualidad', 'Julio', '5to año', 0),
(34, '2024-09-23', '00:47:07', 192, 'Rosa Meltrozo', 19836275, 1000, 'Mensualidad', 'Julio', '4to año', 0),
(35, '2024-09-23', '00:48:39', 18, 'arthur trump', 18662865, 1000, 'Mensualidad', 'Junio', 'Segundo', 0),
(36, '2024-09-23', '00:48:39', 182, 'Ilon Motts', 18662865, 1000, 'Mensualidad', 'Junio', 'Sexto', 0),
(37, '2024-09-23', '00:49:34', 191, 'Peter Parker', 19836275, 1000, 'Mensualidad', 'Junio', '5to año', 0),
(38, '2024-09-23', '00:49:34', 192, 'Rosa Meltrozo', 19836275, 1000, 'Mensualidad', 'Junio', '4to año', 0),
(39, '2024-09-24', '12:15:42', 237687122, 'DANIELA ISABEL ZAMBR', 23768712, 1500, 'Inscripción', 'Septiembre', 'Primero', 0),
(40, '2024-09-24', '12:15:42', 237687122, 'DANIELA ISABEL ZAMBR', 23768712, 1200, 'Mensualidad', 'Septiembre', 'Primero', 0),
(41, '2024-09-29', '01:24:42', 191, 'Maria Corina', 19214453, 1000, 'Inscripción', 'Septiembre', '5to año', 0),
(42, '2024-09-29', '01:24:42', 191, 'Maria Corina', 19214453, 1000, 'Mensualidad', 'Septiembre', '5to año', 0),
(43, '2024-09-29', '01:50:41', 192, 'Rosa Meltrozo', 19836275, 1000, 'Inscripción', 'Julio', '4to año', 0),
(44, '2024-09-29', '15:23:08', 1234, 'fonseca', 123, 1234, 'Mensualidad', 'Septiembre', 'Octavo', 0),
(45, '2024-09-29', '15:23:08', 1234, 'fonseca', 123, 1111, 'Mensualidad', 'Octubre', 'Octavo', 0),
(46, '2024-09-29', '15:23:08', 1234, 'fonseca', 123, 2222, 'Mensualidad', 'Noviembre', 'Octavo', 0),
(47, '2024-09-29', '15:23:08', 1234, 'fonseca', 123, 3333, 'Mensualidad', 'Diciembre', 'Octavo', 0),
(48, '2024-09-29', '15:37:22', 182, 'Ilon Motts', 18662865, 1254, 'Mensualidad', 'Octubre', 'Sexto', 0),
(49, '2024-09-29', '15:37:22', 182, 'Ilon Motts', 18662865, 1000, 'Inscripción', 'Septiembre', 'Sexto', 0),
(50, '2024-09-29', '20:42:59', 7771, 'rafa leao', 777, 1000, 'Inscripción', 'Octubre', 'Primero', 0),
(51, '2024-09-29', '20:42:59', 7771, 'rafa leao', 777, 1000, 'Mensualidad', 'Septiembre', 'Primero', 1),
(52, '2024-10-01', '22:13:44', 18, 'arthur trump', 18662865, 1000, 'Inscripción', 'Septiembre', 'Segundo', 0),
(53, '2024-10-01', '23:32:19', 18, 'arthur trump', 18662865, 2000, 'Mensualidad', 'Octubre', 'Segundo', 0),
(54, '2024-10-01', '23:32:19', 182, 'Ilon Motts', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Sexto', 0);

-- --------------------------------------------------------

--
-- Estructura de tabla para la tabla `representante`
--

CREATE TABLE `representante` (
  `cedula` bigint(20) NOT NULL,
  `nombre` varchar(255) DEFAULT NULL,
  `direccion` varchar(255) DEFAULT NULL,
  `telefono` varchar(15) DEFAULT NULL,
  `birth` date DEFAULT current_timestamp(),
  `correo` varchar(60) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `representante`
--

INSERT INTO `representante` (`cedula`, `nombre`, `direccion`, `telefono`, `birth`, `correo`) VALUES
(123, 'netanyahu', 'isareal', '041200000', '1989-09-29', 'mossad'),
(666, 'MOISES ', 'israel', '0426', '2000-09-29', 'gmaIL'),
(777, 'Leao', 'portugal', '0412', '2000-09-29', 'msn'),
(18662865, 'josseph trump', 'viento norte', '0414', '1989-09-20', 'gmail'),
(19214453, 'kareem Cordero', 'santiago', '0412', '1990-09-29', 'hotmail.com'),
(19836275, 'Freed Harrys', 'los mangos', '0414', '1992-09-22', 'gmail'),
(23768712, 'JESUS EDUARDO ZAMBRANO', 'LA CURVA QLQ', '04146707509', '1994-12-04', 'JEZV18@GMAIL.COM');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `alumno`
--
ALTER TABLE `alumno`
  ADD PRIMARY KEY (`cedula`),
  ADD KEY `cedula_representante` (`cedula_representante`);

--
-- Indices de la tabla `registro_pagos`
--
ALTER TABLE `registro_pagos`
  ADD PRIMARY KEY (`id_factura`),
  ADD KEY `cedula_estudiante` (`cedula_estudiante`),
  ADD KEY `cedula_representante` (`cedula_representante`);

--
-- Indices de la tabla `representante`
--
ALTER TABLE `representante`
  ADD PRIMARY KEY (`cedula`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `registro_pagos`
--
ALTER TABLE `registro_pagos`
  MODIFY `id_factura` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=55;

--
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alumno`
--
ALTER TABLE `alumno`
  ADD CONSTRAINT `alumno_ibfk_1` FOREIGN KEY (`cedula_representante`) REFERENCES `representante` (`cedula`);

--
-- Filtros para la tabla `registro_pagos`
--
ALTER TABLE `registro_pagos`
  ADD CONSTRAINT `registro_pagos_ibfk_1` FOREIGN KEY (`cedula_estudiante`) REFERENCES `alumno` (`cedula`),
  ADD CONSTRAINT `registro_pagos_ibfk_2` FOREIGN KEY (`cedula_representante`) REFERENCES `representante` (`cedula`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
