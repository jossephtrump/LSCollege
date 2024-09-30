-- phpMyAdmin SQL Dump
-- version 5.2.1
-- https://www.phpmyadmin.net/
--
-- Servidor: 127.0.0.1
-- Tiempo de generación: 23-09-2024 a las 05:56:21
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
(191, 19836275, 'Peter Parker', '2010-09-22', '5to año', 'los mangos', '0414', 'Masculino', 'gmail', 0.00, 0),
(192, 19836275, 'Rosa Meltrozo', '2011-09-22', '4to año', 'los mangos', '0412', 'Femenino', 'gmail', 0.00, 0);

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
-- Restricciones para tablas volcadas
--

--
-- Filtros para la tabla `alumno`
--
ALTER TABLE `alumno`
  ADD CONSTRAINT `alumno_ibfk_1` FOREIGN KEY (`cedula_representante`) REFERENCES `representante` (`cedula`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
