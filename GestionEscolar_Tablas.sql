-- Crear la base de datos
CREATE DATABASE GestionEscolar;
GO

USE GestionEscolar;
GO

-- Tabla Estudiantes
CREATE TABLE Estudiantes (
    IdEstudiante INT IDENTITY(1,1) PRIMARY KEY,
    DNI CHAR(8) NOT NULL UNIQUE,
    Nombres NVARCHAR(50) NOT NULL,
    Apellidos NVARCHAR(50) NOT NULL,
    FechaNacimiento DATE NOT NULL,
    Genero CHAR(1) CHECK (Genero IN ('M','F')),
    Direccion NVARCHAR(100),
    Telefono CHAR(9),
    Email NVARCHAR(100) UNIQUE
);

-- Tabla Profesores
CREATE TABLE Profesores (
    IdProfesor INT IDENTITY(1,1) PRIMARY KEY,
    DNI CHAR(8) NOT NULL UNIQUE,
    Nombres NVARCHAR(50) NOT NULL,
    Apellidos NVARCHAR(50) NOT NULL,
    Especialidad NVARCHAR(50),
    Telefono CHAR(9),
    Email NVARCHAR(100) UNIQUE
);

-- Tabla Materias
CREATE TABLE Materias (
    IdMateria INT IDENTITY(1,1) PRIMARY KEY,
    Nombre NVARCHAR(100) NOT NULL UNIQUE,
    Creditos INT NOT NULL CHECK (Creditos BETWEEN 1 AND 10),
    IdProfesor INT NOT NULL,
    CONSTRAINT FK_Materia_Profesor FOREIGN KEY (IdProfesor)
        REFERENCES Profesores(IdProfesor)
);

-- Tabla Grupos
CREATE TABLE Grupos (
    IdGrupo INT IDENTITY(1,1) PRIMARY KEY,
    IdMateria INT NOT NULL,
    NombreGrupo NVARCHAR(50) NOT NULL,
    Semestre CHAR(6) NOT NULL, -- Ejemplo: 2025-1
    Aula NVARCHAR(20),
    CONSTRAINT FK_Grupo_Materia FOREIGN KEY (IdMateria)
        REFERENCES Materias(IdMateria),
    CONSTRAINT UQ_Grupo UNIQUE (IdMateria, NombreGrupo, Semestre)
);

-- Tabla Matriculas
CREATE TABLE Matriculas (
    IdMatricula INT IDENTITY(1,1) PRIMARY KEY,
    IdEstudiante INT NOT NULL,
    IdGrupo INT NOT NULL,
    FechaMatricula DATE NOT NULL DEFAULT GETDATE(),
    Estado NVARCHAR(20) NOT NULL DEFAULT 'Activo',
    CONSTRAINT FK_Matricula_Estudiante FOREIGN KEY (IdEstudiante)
        REFERENCES Estudiantes(IdEstudiante),
    CONSTRAINT FK_Matricula_Grupo FOREIGN KEY (IdGrupo)
        REFERENCES Grupos(IdGrupo),
    CONSTRAINT UQ_Matricula UNIQUE (IdEstudiante, IdGrupo)
);

-- Tabla Calificaciones
CREATE TABLE Calificaciones (
    IdCalificacion INT IDENTITY(1,1) PRIMARY KEY,
    IdMatricula INT NOT NULL,
    Nota DECIMAL(5,2) CHECK (Nota BETWEEN 0 AND 20),
    FechaRegistro DATE NOT NULL DEFAULT GETDATE(),
    CONSTRAINT FK_Calificacion_Matricula FOREIGN KEY (IdMatricula)
        REFERENCES Matriculas(IdMatricula)
);