-- SQL Export generado por MigradorBD
-- Fecha: 2026-06-25 14:26:31.985689
-- Motor destino: mysql

CREATE TABLE IF NOT EXISTS `public`.`usuarios` (`id` INTEGER, `nombre` VARCHAR(4000) NOT NULL, `email` VARCHAR(4000) NOT NULL, PRIMARY KEY (`id`));
INSERT INTO `public`.`usuarios` (`id`, `nombre`, `email`) VALUES (1, 'Juan Perez', 'juan@ejemplo.com');
INSERT INTO `public`.`usuarios` (`id`, `nombre`, `email`) VALUES (2, 'Maria Lopez', 'maria@ejemplo.com');
