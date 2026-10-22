-- Inicializacion de la base de datos de Healenium.
-- El backend crea sus tablas al arrancar (Flyway), pero necesita el schema.
CREATE SCHEMA IF NOT EXISTS healenium;
GRANT ALL ON SCHEMA healenium TO healenium_user;
