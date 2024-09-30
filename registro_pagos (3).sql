-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 23-09-2024 a las 05:56:32
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
-- Estructura de tabla para la tabla `registro_pagos`
--

CREATE TABLE `registro_pagos` (
  `id` int(20) NOT NULL,
  `fecha` date DEFAULT current_timestamp(),
  `hora` time DEFAULT current_timestamp(),
  `cedula_estudiante` bigint(20) DEFAULT NULL,
  `nombre_alumno` varchar(20) NOT NULL,
  `cedula_representante` bigint(20) DEFAULT NULL,
  `monto` double DEFAULT NULL,
  `tipo_pago` varchar(25) NOT NULL,
  `mes` varchar(20) NOT NULL,
  `curso` varchar(255) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_general_ci;

--
-- Volcado de datos para la tabla `registro_pagos`
--

INSERT INTO `registro_pagos` (`id`, `fecha`, `hora`, `cedula_estudiante`, `nombre_alumno`, `cedula_representante`, `monto`, `tipo_pago`, `mes`, `curso`) VALUES
(23, '2024-09-20', '00:28:00', NULL, 'arthur trump', 18662865, 2000, 'Mensualidad', 'Septiembre', 'Primero'),
(24, '2024-09-20', '00:28:00', NULL, 'arthur trump', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Primero'),
(25, '2024-09-22', '23:45:48', NULL, 'arthur trump', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Segundo'),
(26, '2024-09-22', '23:45:48', NULL, 'arthur trump', 18662865, 1500, 'Mensualidad', 'Septiembre', 'Segundo'),
(27, '2024-09-22', '23:50:04', NULL, 'Peter Parker', 19836275, 2000, 'Mensualidad', 'Octubre', '5to año'),
(28, '2024-09-22', '23:50:04', NULL, 'Rosa Meltrozo', 19836275, 2000, 'Mensualidad', 'Enero', '4to año');

--
-- Índices para tablas volcadas
--

--
-- Indices de la tabla `registro_pagos`
--
ALTER TABLE `registro_pagos`
  ADD PRIMARY KEY (`id`),
  ADD KEY `cedula_estudiante` (`cedula_estudiante`),
  ADD KEY `cedula_representante` (`cedula_representante`);

--
-- AUTO_INCREMENT de las tablas volcadas
--

--
-- AUTO_INCREMENT de la tabla `registro_pagos`
--
ALTER TABLE `registro_pagos`
  MODIFY `id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=29;

--
-- Restricciones para tablas volcadas
--

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
