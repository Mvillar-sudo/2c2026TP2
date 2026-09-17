DROP DATABASE IF EXISTS club_deportivo;

CREATE DATABASE IF NOT EXISTS club_deportivo;
USE club_deportivo;

CREATE TABLE IF NOT EXISTS deportes(
    id_deporte INT AUTO_INCREMENT PRIMARY KEY,
    nombre_deporte VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS canchas(
    id_cancha INT AUTO_INCREMENT PRIMARY KEY,
    nombre_cancha VARCHAR(50) NOT NULL,
    id_deporte INT NOT NULL,
    precio_hora INT NOT NULL,
    techada BOOLEAN default false,
    cancha_activa BOOLEAN default true,
    FOREIGN KEY (id_deporte) references deportes(id_deporte)
);

CREATE TABLE IF NOT EXISTS socios(
  id_socio INT AUTO_INCREMENT PRIMARY KEY,
  nombre_socio VARCHAR(50) NOT NULL,
  email VARCHAR(30) NOT NULL UNIQUE,
  socio_activo BOOLEAN default true
);

CREATE TABLE IF NOT EXISTS reservas(
  id_reserva INT AUTO_INCREMENT PRIMARY KEY,
  id_socio INT NOT NULL,
  id_cancha INT NOT NULL,
  fecha_hora_inicio DATETIME NOT NULL,
  fecha_hora_fin DATETIME NOT NULL,
  estado VARCHAR(20) NOT NULL default 'confirmada',
  CONSTRAINT chk_estado CHECK (estado IN ('confirmada', 'cancelada', 'finalizada')),
  precio_hora_historico INT NOT NULL,
  total INT NOT NULL,
  FOREIGN KEY (id_socio) references socios(id_socio),
  FOREIGN KEY (id_cancha) references canchas(id_cancha)
);

