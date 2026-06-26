-- SQL Export generado por MigradorBD
-- Origen: SQL Server  -->  Destino: POSTGRESQL
-- Conversion automatica de dialectos

-- Crear la base de datos
CREATE DATABASE GestionEscolar;
-- Tabla Estudiantes
CREATE TABLE Estudiantes (
    IdEstudiante SERIAL PRIMARY KEY,
    DNI CHAR(8) NOT NULL UNIQUE,
    Nombres VARCHAR(50) NOT NULL,
    Apellidos VARCHAR(50) NOT NULL,
    FechaNacimiento DATE NOT NULL,
    Genero CHAR(1) CHECK (Genero IN ('M','F')),
    Direccion VARCHAR(100),
    Telefono CHAR(9),
    Email VARCHAR(100) UNIQUE
);

-- Tabla Profesores
CREATE TABLE Profesores (
    IdProfesor SERIAL PRIMARY KEY,
    DNI CHAR(8) NOT NULL UNIQUE,
    Nombres VARCHAR(50) NOT NULL,
    Apellidos VARCHAR(50) NOT NULL,
    Especialidad VARCHAR(50),
    Telefono CHAR(9),
    Email VARCHAR(100) UNIQUE
);

-- Tabla Materias
CREATE TABLE Materias (
    IdMateria SERIAL PRIMARY KEY,
    Nombre VARCHAR(100) NOT NULL UNIQUE,
    Creditos INT NOT NULL CHECK (Creditos BETWEEN 1 AND 10),
    IdProfesor INT NOT NULL,
    CONSTRAINT FK_Materia_Profesor FOREIGN KEY (IdProfesor)
        REFERENCES Profesores(IdProfesor)
);

-- Tabla Grupos
CREATE TABLE Grupos (
    IdGrupo SERIAL PRIMARY KEY,
    IdMateria INT NOT NULL,
    NombreGrupo VARCHAR(50) NOT NULL,
    Semestre CHAR(6) NOT NULL, -- Ejemplo: 2025-1
    Aula VARCHAR(20),
    CONSTRAINT FK_Grupo_Materia FOREIGN KEY (IdMateria)
        REFERENCES Materias(IdMateria),
    CONSTRAINT UQ_Grupo UNIQUE (IdMateria, NombreGrupo, Semestre)
);

-- Tabla Matriculas
CREATE TABLE Matriculas (
    IdMatricula SERIAL PRIMARY KEY,
    IdEstudiante INT NOT NULL,
    IdGrupo INT NOT NULL,
    FechaMatricula DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    Estado VARCHAR(20) NOT NULL DEFAULT 'Activo',
    CONSTRAINT FK_Matricula_Estudiante FOREIGN KEY (IdEstudiante)
        REFERENCES Estudiantes(IdEstudiante),
    CONSTRAINT FK_Matricula_Grupo FOREIGN KEY (IdGrupo)
        REFERENCES Grupos(IdGrupo),
    CONSTRAINT UQ_Matricula UNIQUE (IdEstudiante, IdGrupo)
);

-- Tabla Calificaciones
CREATE TABLE Calificaciones (
    IdCalificacion SERIAL PRIMARY KEY,
    IdMatricula INT NOT NULL,
    Nota DECIMAL(5,2) CHECK (Nota BETWEEN 0 AND 20),
    FechaRegistro DATE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT FK_Calificacion_Matricula FOREIGN KEY (IdMatricula)
        REFERENCES Matriculas(IdMatricula)
);