-- 1. Clientes con su persona (si es persona natural)
select *
from [Sales].[Customer] c
inner join Person.Person p on c.PersonID = p.BusinessEntityID;


-- 2. Clientes con su persona y su tienda (si es cuenta de tienda)
--    Nota: se referencia la tienda por c.StoreID
select *
from Sales.Customer c
inner join Person.Person p on c.PersonID = p.BusinessEntityID
inner join Sales.Store s on c.StoreID = s.BusinessEntityID;


-- 3. Selección de columnas clave de cliente + nombre completo persona + nombre de tienda
--    Sugerencia: agrega un espacio entre nombres
select
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    c.TerritoryID,
    c.AccountNumber,
    p.PersonType,
    p.FirstName + ' ' + p.LastName as NombrePersona,
    s.Name as Tienda
from Sales.Customer c
inner join Person.Person p on c.PersonID = p.BusinessEntityID
inner join Sales.Store s on c.StoreID = s.BusinessEntityID;


-- 4. Igual que la anterior pero mostrando el nombre del territorio con subconsulta escalar
--    (Se puede reemplazar por JOIN a Sales.SalesTerritory para mejor rendimiento)
select
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    (select t.Name from Sales.SalesTerritory t where t.TerritoryID = c.TerritoryID) as TerritoryName,
    c.AccountNumber,
    p.PersonType,
    p.FirstName + ' ' + p.LastName as NombrePersona,
    s.Name as Tienda
from Sales.Customer c
inner join Person.Person p on c.PersonID = p.BusinessEntityID
inner join Sales.Store s on c.StoreID = s.BusinessEntityID;


-- 5. Explorar todas las personas
select * from Person.Person;


-- 6. Glosario manual de PersonType (referencial)
-- EM EMPLEADO | SC TIENDA | SP VENDEDOR | VC PROVEEDOR | DC CONTACTO GENERAL | IN INDIVIDUAL


-- 7. Tipos de contacto disponibles
select * from Person.ContactType;


-- 8. Clientes + territorio por nombre + tipificación legible de PersonType
--    Nota: 'EN' parecía un typo; en AdventureWorks es 'EM' (Empleado).
select
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    (select t.Name from Sales.SalesTerritory t where t.TerritoryID = c.TerritoryID) as TerritoryName,
    c.AccountNumber,
    (case p.PersonType
        when 'EM' then 'EMPLEADO'
        when 'SC' then 'TIENDA'
        when 'SP' then 'VENDEDOR'
        when 'VC' then 'PROVEEDOR'
        when 'DC' then 'CONTACTO GENERAL'
        when 'IN' then 'INDIVIDUAL'
     end) as TipoPersona,
    p.PersonType,
    p.FirstName + ' ' + p.LastName as NombrePersona,
    s.Name as Tienda
from Sales.Customer c
inner join Person.Person p on c.PersonID = p.BusinessEntityID
inner join Sales.Store s on c.StoreID = s.BusinessEntityID;


-- 9. Igual que 8) pero filtrando por tipos de persona (EMPLEADO o PROVEEDOR)
select
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    (select t.Name from Sales.SalesTerritory t where t.TerritoryID = c.TerritoryID) as TerritoryName,
    c.AccountNumber,
    (case p.PersonType
        when 'EM' then 'EMPLEADO'
        when 'SC' then 'TIENDA'
        when 'SP' then 'VENDEDOR'
        when 'VC' then 'PROVEEDOR'
        when 'DC' then 'CONTACTO GENERAL'
        when 'IN' then 'INDIVIDUAL'
     end) as TipoPersona,
    p.PersonType,
    p.FirstName + ' ' + p.LastName as NombrePersona,
    s.Name as Tienda
from Sales.Customer c
inner join Person.Person p on c.PersonID = p.BusinessEntityID
inner join Sales.Store s on c.StoreID = s.BusinessEntityID
where p.PersonType in ('EM', 'VC');


-- 10. Igual que 9) pero con LEFT JOIN (mantiene clientes aunque falte persona/tienda)
--     OJO: el WHERE sobre p.PersonType vuelve el LEFT en INNER para esas filas.
select
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    (select t.Name from Sales.SalesTerritory t where t.TerritoryID = c.TerritoryID) as TerritoryName,
    c.AccountNumber,
    (case p.PersonType
        when 'EM' then 'EMPLEADO'
        when 'SC' then 'TIENDA'
        when 'SP' then 'VENDEDOR'
        when 'VC' then 'PROVEEDOR'
        when 'DC' then 'CONTACTO GENERAL'
        when 'IN' then 'INDIVIDUAL'
     end) as TipoPersona,
    p.PersonType,
    p.FirstName + ' ' + p.LastName as NombrePersona,
    s.Name as Tienda
from Sales.Customer c
left join Person.Person p on c.PersonID = p.BusinessEntityID
left join Sales.Store s on c.StoreID = s.BusinessEntityID
where p.PersonType in ('EM', 'VC'); -- si quieres mantener NULL, mueve este filtro al JOIN


-- 11. Clientes en territorios 7 u 8 + etiqueta tienda/persona
select
    c.CustomerID,
    c.PersonID,
    c.StoreID,
    s.Name as Tienda,
    (select t.Name from Sales.SalesTerritory t where t.TerritoryID = c.TerritoryID) as TerritoryName,
    c.AccountNumber,
    (case p.PersonType
        when 'EM' then 'EMPLEADO'
        when 'SC' then 'TIENDA'
        when 'SP' then 'VENDEDOR'
        when 'VC' then 'PROVEEDOR'
        when 'DC' then 'CONTACTO GENERAL'
        when 'IN' then 'INDIVIDUAL'
     end) as TipoPersona,
    p.PersonType,
    p.FirstName + ' ' + p.LastName as NombrePersona
from Sales.Customer c
inner join Person.Person p on c.PersonID = p.BusinessEntityID
inner join Sales.Store s on c.StoreID = s.BusinessEntityID
where c.TerritoryID in (7, 8);


-- 12. Conteo de emails por persona (solo las que tienen más de un email)
select p.BusinessEntityID, count(*) as CantEmails
from Person.Person p
inner join Person.EmailAddress e on p.BusinessEntityID = e.BusinessEntityID
group by p.BusinessEntityID
having count(*) > 1;


-- 13. Ver detalle de emails para una persona específica (ej: 14)
select *
from Person.Person p
inner join Person.EmailAddress e on p.BusinessEntityID = e.BusinessEntityID
where p.BusinessEntityID = 14;


-- 14. (Demostrativo) Personas con duplicados por BusinessEntityID (no habrá >1 en Person.Person)
--     En AdventureWorks normalmente esto devolverá 0 filas.
select p.BusinessEntityID, count(*) as Repeticiones
from Person.Person p
group by p.BusinessEntityID
having count(*) > 1;


-- 15. Tablas de RR.HH. para armar relaciones Empleado-Departamento-Historial
select * from HumanResources.Department;
select * from HumanResources.EmployeeDepartmentHistory;
select * from HumanResources.Employee;


-- 16. Empleados con su historial y departamento (nombres de grupo/depto)
--     BirthDate formateado (dd/mm/aaaa con estilo 103)
select
    e.BusinessEntityID,
    e.NationalIDNumber,
    e.JobTitle,
    convert(varchar(10), e.BirthDate, 103) as FechaNacimiento,
    d.GroupName,
    d.Name as DepartmentName
from HumanResources.Employee e
inner join HumanResources.EmployeeDepartmentHistory eh on e.BusinessEntityID = eh.BusinessEntityID
inner join HumanResources.Department d on eh.DepartmentID = d.DepartmentID;


-- 17. Igual que 16) pero agregando el nombre completo desde Person.Person
select
    e.BusinessEntityID,
    e.NationalIDNumber,
    e.JobTitle,
    concat(p.FirstName, ' ', p.LastName) as NombreEmpleado,
    convert(varchar(10), e.BirthDate, 103) as FechaNacimiento,
    d.GroupName,
    d.Name as DepartmentName
from HumanResources.Employee e
inner join HumanResources.EmployeeDepartmentHistory eh on e.BusinessEntityID = eh.BusinessEntityID
inner join HumanResources.Department d on eh.DepartmentID = d.DepartmentID
inner join Person.Person p on e.BusinessEntityID = p.BusinessEntityID;


-- 18. Provincias/estados (de Person.StateProvince) y empleados (exploración)
select * from Person.StateProvince;
select * from HumanResources.Employee;


-- 19. Territorios de venta con sus estados/provincias relacionados (incluye país, flags)
select
    t.TerritoryID,
    t.Name as TerritoryName,
    t.CountryRegionCode,
    p.StateProvinceCode,
    p.IsOnlyStateProvinceFlag,
    p.Name as Estado
from Sales.SalesTerritory t
inner join Person.StateProvince p on t.TerritoryID = p.TerritoryID;


-- 20. Variante reducida de 19) con menos columnas
select
    t.TerritoryID,
    t.Name as TerritoryName,
    p.StateProvinceCode,
    p.Name as Estado
from Sales.SalesTerritory t
inner join Person.StateProvince p on t.TerritoryID = p.TerritoryID;
