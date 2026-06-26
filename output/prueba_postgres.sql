-- SQL Export generado por MigradorBD
-- Fecha: 2026-06-25 14:26:33.148206
-- Motor destino: postgres

CREATE TABLE IF NOT EXISTS "public"."usuarios" ("id" INTEGER, "nombre" TEXT NOT NULL, "email" TEXT NOT NULL, PRIMARY KEY ("id"));
INSERT INTO "public"."usuarios" ("id", "nombre", "email") VALUES (1, 'Juan Perez', 'juan@ejemplo.com');
INSERT INTO "public"."usuarios" ("id", "nombre", "email") VALUES (2, 'Maria Lopez', 'maria@ejemplo.com');
