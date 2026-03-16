"""
Script de datos de prueba — Empresa Comercial Peruana
Ejecutar con: python manage.py shell < seed_data.py
"""
import random
from datetime import date, timedelta, datetime
from decimal import Decimal
from django.utils import timezone

print("🚀 Iniciando carga de datos...")

# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def fecha_aleatoria(inicio, fin):
    delta = fin - inicio
    return inicio + timedelta(days=random.randint(0, delta.days))

def dni_aleatorio():
    return str(random.randint(10000000, 99999999))

def ruc_aleatorio():
    return '20' + str(random.randint(100000000, 999999999))

def telefono_aleatorio():
    prefijos = ['9', '99', '98', '97', '96', '95']
    return random.choice(prefijos) + str(random.randint(10000000, 99999999))

# ─────────────────────────────────────────────────────────────
# DATOS BASE
# ─────────────────────────────────────────────────────────────

nombres_masculinos = [
    'Carlos', 'Juan', 'Pedro', 'Luis', 'Miguel', 'Jorge', 'Roberto', 'Fernando',
    'Ricardo', 'Alejandro', 'Daniel', 'David', 'Sergio', 'Eduardo', 'Manuel',
    'Antonio', 'Francisco', 'Raúl', 'César', 'Víctor', 'Óscar', 'Rodrigo',
    'Diego', 'Andrés', 'Gustavo', 'Javier', 'Pablo', 'Héctor', 'Enrique', 'Marco'
]

nombres_femeninos = [
    'María', 'Ana', 'Rosa', 'Carmen', 'Patricia', 'Sandra', 'Lucía', 'Claudia',
    'Verónica', 'Gabriela', 'Valeria', 'Sofía', 'Andrea', 'Paola', 'Mónica',
    'Jessica', 'Karina', 'Milagros', 'Vanessa', 'Natalia', 'Adriana', 'Diana',
    'Silvia', 'Elena', 'Isabel', 'Roxana', 'Cynthia', 'Gisela', 'Fiorella', 'Melissa'
]

apellidos = [
    'García', 'Rodríguez', 'López', 'Martínez', 'González', 'Pérez', 'Sánchez',
    'Ramírez', 'Torres', 'Flores', 'Rivera', 'Gómez', 'Díaz', 'Reyes', 'Cruz',
    'Morales', 'Ortiz', 'Gutiérrez', 'Chávez', 'Quispe', 'Mamani', 'Huanca',
    'Vargas', 'Rojas', 'Herrera', 'Mendoza', 'Castillo', 'Ramos', 'Paredes',
    'Villanueva', 'Espinoza', 'Vega', 'Castro', 'Alvarado', 'Cisneros', 'Ccopa',
    'Condori', 'Huamán', 'Cárdenas', 'Pacheco', 'Salazar', 'Aguilar', 'Núñez'
]

distritos_lima = [
    'Miraflores', 'San Isidro', 'Surco', 'La Molina', 'San Borja',
    'Pueblo Libre', 'Jesús María', 'Lince', 'Breña', 'Rímac',
    'Los Olivos', 'San Martín de Porres', 'Independencia', 'Comas',
    'Villa El Salvador', 'Villa María del Triunfo', 'San Juan de Lurigancho'
]

calles = [
    'Av. Javier Prado', 'Av. La Marina', 'Av. Arequipa', 'Calle Los Pinos',
    'Jr. Huallaga', 'Av. Brasil', 'Calle Las Flores', 'Av. Benavides',
    'Jr. de la Unión', 'Av. Universitaria', 'Calle Los Álamos', 'Av. Colonial'
]

def direccion_aleatoria():
    return f"{random.choice(calles)} {random.randint(100, 999)}, {random.choice(distritos_lima)}, Lima"

def email_corporativo(nombre, apellido):
    n = nombre.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u').replace(' ','')
    a = apellido.lower().replace('á','a').replace('é','e').replace('í','i').replace('ó','o').replace('ú','u')
    return f"{n}.{a}@empresa.com.pe"

# ─────────────────────────────────────────────────────────────
# 1. USUARIOS DEL SISTEMA
# ─────────────────────────────────────────────────────────────
print("👤 Creando usuarios...")

from applications.users.models import User

roles = [User.ADMIN, User.RRHH, User.INVENTARIO, User.EMPLEADO]
roles_dist = [User.ADMIN]*3 + [User.RRHH]*7 + [User.INVENTARIO]*10 + [User.EMPLEADO]*30

generos_opciones = [User.VARON, User.MUJER]

usuarios_creados = []
used_emails = set()
used_dnis_user = set()

for i in range(50):
    genero = random.choice(generos_opciones)
    if genero == User.VARON:
        nombre = random.choice(nombres_masculinos)
    else:
        nombre = random.choice(nombres_femeninos)
    apellido1 = random.choice(apellidos)
    apellido2 = random.choice(apellidos)
    full_name = f"{nombre} {apellido1} {apellido2}"

    email = email_corporativo(nombre, apellido1)
    counter = 1
    base_email = email
    while email in used_emails:
        email = base_email.replace('@', f'{counter}@')
        counter += 1
    used_emails.add(email)

    occupation = roles_dist[i] if i < len(roles_dist) else User.EMPLEADO
    fecha_nac = fecha_aleatoria(date(1975, 1, 1), date(2000, 12, 31))

    user = User.objects.create_user(
        email=email,
        password='admin',
        full_name=full_name,
        occupation=occupation,
        genero=genero,
        date_birth=fecha_nac,
    )
    usuarios_creados.append(user)

print(f"   ✅ {len(usuarios_creados)} usuarios creados")

# ─────────────────────────────────────────────────────────────
# 2. RRHH
# ─────────────────────────────────────────────────────────────
print("👥 Creando datos de RRHH...")

from applications.rrhh.models import (
    Departamento, Cargo, Empleado, Contrato,
    Asistencia, Ausencia, Vacaciones, Documento
)

# Departamentos
departamentos_data = [
    ('Ventas', 'Gestión de ventas y atención al cliente'),
    ('Logística', 'Control de almacén, despacho y distribución'),
    ('Administración', 'Gestión administrativa y contabilidad'),
    ('Recursos Humanos', 'Gestión del personal y bienestar laboral'),
    ('Tecnología', 'Sistemas de información y soporte técnico'),
    ('Marketing', 'Publicidad, promociones y redes sociales'),
    ('Finanzas', 'Tesorería, presupuestos y control financiero'),
]

departamentos_objs = []
for nombre, desc in departamentos_data:
    d, _ = Departamento.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
    departamentos_objs.append(d)

# Cargos
cargos_data = {
    'Ventas': ['Gerente de Ventas', 'Supervisor de Ventas', 'Ejecutivo de Ventas', 'Promotor Comercial', 'Cajero'],
    'Logística': ['Jefe de Almacén', 'Almacenero', 'Operario de Despacho', 'Conductor', 'Auxiliar de Almacén'],
    'Administración': ['Gerente General', 'Asistente Administrativo', 'Recepcionista', 'Secretaria', 'Archivista'],
    'Recursos Humanos': ['Jefe de RRHH', 'Analista de RRHH', 'Asistente de RRHH', 'Psicólogo Organizacional'],
    'Tecnología': ['Jefe de TI', 'Desarrollador de Software', 'Soporte Técnico', 'Analista de Sistemas'],
    'Marketing': ['Jefe de Marketing', 'Diseñador Gráfico', 'Community Manager', 'Analista de Marketing'],
    'Finanzas': ['Contador General', 'Tesorero', 'Analista Financiero', 'Asistente Contable'],
}

cargos_objs = []
for dep_obj in departamentos_objs:
    nombres_cargos = cargos_data.get(dep_obj.nombre, [])
    for nombre_cargo in nombres_cargos:
        c, _ = Cargo.objects.get_or_create(
            nombre=nombre_cargo,
            departamento=dep_obj,
            defaults={'descripcion': f'Responsabilidades del cargo {nombre_cargo}'}
        )
        cargos_objs.append(c)

# Empleados
print("   Creando empleados...")
empleados_creados = []
used_dnis = set()
used_codigos = set()

estados_emp = [Empleado.ACTIVO]*80 + [Empleado.VACACIONES]*10 + [Empleado.LICENCIA]*5 + [Empleado.INACTIVO]*5
random.shuffle(estados_emp)

for i in range(100):
    genero = random.choice([Empleado.VARON, Empleado.MUJER])
    if genero == Empleado.VARON:
        nombre = random.choice(nombres_masculinos)
    else:
        nombre = random.choice(nombres_femeninos)
    apellido1 = random.choice(apellidos)
    apellido2 = random.choice(apellidos)

    dni = dni_aleatorio()
    while dni in used_dnis:
        dni = dni_aleatorio()
    used_dnis.add(dni)

    codigo = f'EMP{str(i+1).zfill(4)}'
    fecha_ingreso = fecha_aleatoria(date(2015, 1, 1), date(2024, 12, 31))
    fecha_nac = fecha_aleatoria(date(1975, 1, 1), date(2000, 12, 31))
    sueldo = Decimal(str(random.choice([1025, 1200, 1500, 1800, 2000, 2500, 3000, 3500, 4000, 5000])))
    cargo = random.choice(cargos_objs)
    estado = estados_emp[i]

    # vincular algunos empleados a usuarios del sistema
    usuario_vinculado = None
    if i < len(usuarios_creados) and random.random() > 0.6:
        usuario_vinculado = usuarios_creados[i]

    emp = Empleado.objects.create(
        codigo=codigo,
        nombres=nombre,
        apellidos=f"{apellido1} {apellido2}",
        dni=dni,
        genero=genero,
        fecha_nacimiento=fecha_nac,
        email=email_corporativo(nombre, apellido1),
        telefono=telefono_aleatorio(),
        direccion=direccion_aleatoria(),
        cargo=cargo,
        fecha_ingreso=fecha_ingreso,
        sueldo_base=sueldo,
        estado=estado,
        usuario=usuario_vinculado,
    )
    empleados_creados.append(emp)

print(f"   ✅ {len(empleados_creados)} empleados creados")

# Contratos
print("   Creando contratos...")
tipos_contrato = [Contrato.INDEFINIDO, Contrato.PLAZO_FIJO, Contrato.PRACTICAS, Contrato.LOCACION]
for emp in empleados_creados:
    num_contratos = random.randint(1, 3)
    fecha_ini = emp.fecha_ingreso
    for j in range(num_contratos):
        tipo = random.choice(tipos_contrato)
        if tipo == Contrato.INDEFINIDO:
            fecha_fin = None
            estado = Contrato.VIGENTE
        else:
            duracion = random.randint(90, 365)
            fecha_fin = fecha_ini + timedelta(days=duracion)
            estado = Contrato.VIGENTE if fecha_fin > date.today() else Contrato.VENCIDO

        Contrato.objects.create(
            empleado=emp,
            tipo=tipo,
            fecha_inicio=fecha_ini,
            fecha_fin=fecha_fin,
            sueldo=emp.sueldo_base + Decimal(str(random.randint(0, 500))),
            estado=estado,
            observaciones=f'Contrato #{j+1} del empleado {emp.nombre_completo}',
        )
        if fecha_fin:
            fecha_ini = fecha_fin + timedelta(days=1)

print("   ✅ Contratos creados")

# Asistencias — último mes
print("   Creando asistencias...")
hoy = date.today()
hace_30 = hoy - timedelta(days=30)
estados_asist = [Asistencia.PRESENTE]*20 + [Asistencia.TARDANZA]*3 + [Asistencia.FALTA]*1 + [Asistencia.JUSTIFICADO]*1

admin_user = User.objects.filter(is_superuser=True).first()

for emp in random.sample(empleados_creados, min(60, len(empleados_creados))):
    fecha_iter = hace_30
    while fecha_iter <= hoy:
        if fecha_iter.weekday() < 5:  # lunes a viernes
            estado = random.choice(estados_asist)
            hora_entrada = None
            hora_salida = None
            if estado in [Asistencia.PRESENTE, Asistencia.TARDANZA]:
                h_entrada = 8 if estado == Asistencia.PRESENTE else random.randint(9, 10)
                hora_entrada = f"{h_entrada:02d}:{random.randint(0,59):02d}:00"
                hora_salida = f"{random.randint(17,18):02d}:{random.randint(0,59):02d}:00"
            Asistencia.objects.get_or_create(
                empleado=emp,
                fecha=fecha_iter,
                defaults={
                    'hora_entrada': hora_entrada,
                    'hora_salida': hora_salida,
                    'estado': estado,
                    'registrado_por': admin_user,
                }
            )
        fecha_iter += timedelta(days=1)

print("   ✅ Asistencias creadas")

# Ausencias
print("   Creando ausencias...")
tipos_ausencia = [Ausencia.ENFERMEDAD, Ausencia.PERSONAL, Ausencia.FAMILIAR, Ausencia.CAPACITACION, Ausencia.OTRO]
estados_ausencia = [Ausencia.APROBADO, Ausencia.APROBADO, Ausencia.APROBADO, Ausencia.PENDIENTE, Ausencia.RECHAZADO]

for emp in random.sample(empleados_creados, min(40, len(empleados_creados))):
    num = random.randint(1, 3)
    for _ in range(num):
        inicio = fecha_aleatoria(date(2024, 1, 1), date(2025, 6, 30))
        fin = inicio + timedelta(days=random.randint(1, 5))
        estado = random.choice(estados_ausencia)
        Ausencia.objects.create(
            empleado=emp,
            tipo=random.choice(tipos_ausencia),
            fecha_inicio=inicio,
            fecha_fin=fin,
            motivo=random.choice([
                'Enfermedad con certificado médico',
                'Trámites personales urgentes',
                'Emergencia familiar',
                'Capacitación externa',
                'Cita médica programada',
                'Fallecimiento de familiar',
            ]),
            estado=estado,
            aprobado_por=admin_user if estado != Ausencia.PENDIENTE else None,
        )

print("   ✅ Ausencias creadas")

# Vacaciones
print("   Creando vacaciones...")
estados_vac = [Vacaciones.APROBADO, Vacaciones.APROBADO, Vacaciones.GOZADO, Vacaciones.PENDIENTE]

for emp in random.sample(empleados_creados, min(50, len(empleados_creados))):
    num = random.randint(1, 2)
    for _ in range(num):
        inicio = fecha_aleatoria(date(2023, 1, 1), date(2025, 3, 31))
        dias = random.choice([7, 14, 15, 21, 30])
        fin = inicio + timedelta(days=dias)
        estado = random.choice(estados_vac)
        Vacaciones.objects.create(
            empleado=emp,
            fecha_inicio=inicio,
            fecha_fin=fin,
            dias_solicitados=dias,
            estado=estado,
            aprobado_por=admin_user if estado != Vacaciones.PENDIENTE else None,
            observaciones='Vacaciones anuales' if dias >= 15 else 'Vacaciones parciales',
        )

print("   ✅ Vacaciones creadas")

# Documentos
print("   Creando documentos...")
tipos_doc = [Documento.DNI, Documento.CV, Documento.CONTRATO, Documento.CERTIFICADO, Documento.TITULO]

for emp in random.sample(empleados_creados, min(70, len(empleados_creados))):
    for tipo in random.sample(tipos_doc, random.randint(2, 4)):
        nombres_doc = {
            Documento.DNI: 'DNI escaneado',
            Documento.CV: 'Currículum Vitae actualizado',
            Documento.CONTRATO: 'Contrato de trabajo firmado',
            Documento.CERTIFICADO: 'Certificado de estudios',
            Documento.TITULO: 'Título profesional',
        }
        fecha_em = fecha_aleatoria(date(2010, 1, 1), date(2023, 12, 31))
        Documento.objects.create(
            empleado=emp,
            tipo=tipo,
            nombre=nombres_doc[tipo],
            archivo='documentos/placeholder.pdf',
            fecha_emision=fecha_em,
            fecha_vencimiento=fecha_em + timedelta(days=365*5) if tipo == Documento.DNI else None,
            observaciones='Documento verificado',
        )

print("   ✅ Documentos creados")
print("✅ RRHH completo")

# ─────────────────────────────────────────────────────────────
# 3. INVENTARIO
# ─────────────────────────────────────────────────────────────
print("📦 Creando datos de Inventario...")

from applications.inventario.models import (
    UnidadMedida, Categoria, Almacen, Proveedor,
    Producto, Movimiento, AjusteInventario, Alerta
)

# Unidades de medida
unidades_data = [
    ('Unidad', 'UND'), ('Kilogramo', 'KG'), ('Gramo', 'GR'),
    ('Litro', 'LT'), ('Mililitro', 'ML'), ('Metro', 'MT'),
    ('Centímetro', 'CM'), ('Caja', 'CJA'), ('Bolsa', 'BLS'),
    ('Docena', 'DOC'), ('Par', 'PAR'), ('Paquete', 'PKT'),
]
unidades_objs = []
for nombre, abrev in unidades_data:
    u, _ = UnidadMedida.objects.get_or_create(nombre=nombre, defaults={'abreviatura': abrev})
    unidades_objs.append(u)

# Categorías
categorias_data = [
    ('Abarrotes', 'Productos de primera necesidad y consumo masivo'),
    ('Bebidas', 'Bebidas gaseosas, jugos, aguas y lácteos'),
    ('Limpieza', 'Productos de limpieza del hogar e higiene'),
    ('Cuidado Personal', 'Cosméticos, higiene personal y cuidado corporal'),
    ('Electrónica', 'Artefactos eléctricos, tecnología y accesorios'),
    ('Ropa y Calzado', 'Prendas de vestir y calzado para toda la familia'),
    ('Ferretería', 'Herramientas, materiales de construcción y ferretería'),
    ('Juguetería', 'Juguetes, juegos y artículos infantiles'),
    ('Papelería', 'Útiles escolares, oficina y papelería en general'),
    ('Farmacia', 'Medicamentos OTC, vitaminas y productos de salud'),
]
categorias_objs = []
for nombre, desc in categorias_data:
    c, _ = Categoria.objects.get_or_create(nombre=nombre, defaults={'descripcion': desc})
    categorias_objs.append(c)

# Almacenes
almacenes_data = [
    ('Almacén Central', 'Av. Argentina 1250, Cercado de Lima'),
    ('Almacén Norte', 'Av. Túpac Amaru 3400, Comas'),
    ('Almacén Sur', 'Av. Pachacútec 1800, Villa El Salvador'),
    ('Almacén Este', 'Av. Gran Chimú 500, San Juan de Lurigancho'),
]
almacenes_objs = []
for nombre, ubicacion in almacenes_data:
    a, _ = Almacen.objects.get_or_create(nombre=nombre, defaults={
        'ubicacion': ubicacion,
        'responsable': random.choice(usuarios_creados),
    })
    almacenes_objs.append(a)

# Proveedores
proveedores_data = [
    ('Alicorp S.A.A.', ruc_aleatorio(), 'Luis Torres', 'Av. Argentina 4793, Callao'),
    ('Gloria S.A.', ruc_aleatorio(), 'María Quispe', 'Av. República de Argentina 4791, Lima'),
    ('Backus & Johnston', ruc_aleatorio(), 'Carlos Mendoza', 'Av. Nicolás Ayllón 3986, Lima'),
    ('Procter & Gamble Perú', ruc_aleatorio(), 'Ana Flores', 'Calle Amador Merino Reyna 267, San Isidro'),
    ('Unilever Andina Perú', ruc_aleatorio(), 'Pedro Rojas', 'Av. Los Frutales 220, Ate'),
    ('Nestlé Perú S.A.', ruc_aleatorio(), 'Sandra García', 'Av. República de Panamá 3074, San Isidro'),
    ('Kimberly-Clark Perú', ruc_aleatorio(), 'Roberto Díaz', 'Av. Los Laureles 365, San Isidro'),
    ('Bimbo Perú S.A.', ruc_aleatorio(), 'Claudia Vargas', 'Av. Materiales 2400, San Martín de Porres'),
    ('Ajinomoto del Perú', ruc_aleatorio(), 'Diego Castillo', 'Av. Nicolás Arriola 740, Santa Catalina'),
    ('Aje Group', ruc_aleatorio(), 'Valeria Huanca', 'Av. Naciones Unidas 1084, Ate'),
    ('Distribuidora Norte SAC', ruc_aleatorio(), 'Marco López', 'Jr. Cusco 450, Breña'),
    ('Importaciones Sur EIRL', ruc_aleatorio(), 'Fiorella Ccopa', 'Av. Grau 890, Barranco'),
]
proveedores_objs = []
for nombre, ruc, contacto, direccion in proveedores_data:
    p, _ = Proveedor.objects.get_or_create(nombre=nombre, defaults={
        'ruc': ruc,
        'contacto': contacto,
        'telefono': telefono_aleatorio(),
        'email': f"ventas@{nombre.lower().replace(' ','').replace('.','').replace(',','')[:15]}.com.pe",
        'direccion': direccion,
    })
    proveedores_objs.append(p)

# Productos — 500 productos realistas para empresa comercial
print("   Creando 500 productos...")

productos_por_categoria = {
    'Abarrotes': [
        'Arroz Extra Superior', 'Arroz Paisano', 'Azúcar Rubia', 'Azúcar Blanca',
        'Aceite Vegetal 1L', 'Aceite de Oliva 500ml', 'Sal de Mesa 1kg', 'Fideos Tallarin',
        'Fideos Espagueti', 'Fideos Cabello Angel', 'Harina Sin Preparar 1kg',
        'Avena 3 Ositos 200g', 'Avena Quaker 400g', 'Leche Gloria Evaporada',
        'Leche Condensada', 'Mayonesa Alacena 500g', 'Kétchup Alacena 400g',
        'Mostaza Alacena 400g', 'Salsa de Tomate Heinz', 'Atún Florida 170g',
        'Atún Van Camps', 'Sardina en Salsa', 'Mantequilla Gloria 90g',
        'Margarina Dorina 100g', 'Mermelada Fanny Fresa', 'Mermelada Fanny Piña',
        'Miel de Abeja 250g', 'Chocolate Sublime 32g', 'Galleta Oreo', 'Galleta Soda',
        'Galleta Vainilla', 'Cereal Ángel 500g', 'Maíz Morado 100g', 'Quinua 500g',
        'Kiwicha 500g', 'Café Nescafé Classic 200g', 'Café Altomayo 200g',
        'Té Lipton 25 sobres', 'Manzanilla 25 sobres', 'Canela Molida 50g',
    ],
    'Bebidas': [
        'Gaseosa Inca Kola 1.5L', 'Gaseosa Coca Cola 1.5L', 'Gaseosa Pepsi 1.5L',
        'Gaseosa Sprite 1.5L', 'Agua San Luis 625ml', 'Agua Cielo 625ml',
        'Agua San Mateo 500ml', 'Jugo Frugos Durazno 1L', 'Jugo Frugos Naranja 1L',
        'Jugo Pulp Naranja 500ml', 'Jugo Watts Piña 1L', 'Leche Gloria UHT 1L',
        'Leche Laive Entera 1L', 'Leche Ideal 946ml', 'Yogurt Gloria Fresa 1kg',
        'Yogurt Yomost Vainilla 150g', 'Bebida Powerade 500ml', 'Bebida Gatorade 500ml',
        'Cerveza Cristal 650ml', 'Cerveza Pilsen 650ml', 'Cerveza Cusqueña 650ml',
        'Vino Tabernero Borgoña 750ml', 'Chicha Morada 500ml', 'Maracuyá Concentrado 500ml',
    ],
    'Limpieza': [
        'Detergente Ariel 360g', 'Detergente Ace 360g', 'Detergente Bolivar 360g',
        'Jabón Marsella 230g', 'Jabón Bolivar 230g', 'Lejía Clorox 680ml',
        'Lejía Sapolio 680ml', 'Limpiatodo Sapolio 500ml', 'Pinesol 500ml',
        'Desinfectante Lysol 500ml', 'Suavitel 850ml', 'Downy 850ml',
        'Esponja de Cocina 2 unidades', 'Guantes de Limpieza Talla M',
        'Escoba Plástica', 'Trapeador Algodón', 'Balde Plástico 10L',
        'Papel Higiénico Elite 4 rollos', 'Papel Higiénico Suave 4 rollos',
        'Servilletas Elite 100 unidades', 'Papel Toalla Scott 3 rollos',
        'Bolsa de Basura 10 unidades', 'Ambientador Glade 400ml',
        'Pastilla WC Pato 50g', 'Lavavajilla Ayudín Limón 360g',
    ],
    'Cuidado Personal': [
        'Shampoo Head & Shoulders 400ml', 'Shampoo Pantene 400ml', 'Shampoo Sedal 400ml',
        'Acondicionador Pantene 400ml', 'Jabón Dove 90g', 'Jabón Lux 90g',
        'Jabón Palmolive 90g', 'Desodorante Rexona 150ml', 'Desodorante Axe 150ml',
        'Desodorante Nivea 150ml', 'Crema Nivea 400ml', 'Crema Pond\'s 200g',
        'Crema Jergens 200ml', 'Bloqueador Solar Sundown FPS50 120ml',
        'Pasta Dental Colgate 90g', 'Pasta Dental Oral-B 90g', 'Cepillo Dental Colgate',
        'Hilo Dental Oral-B 50m', 'Enjuague Bucal Listerine 500ml',
        'Toalla Femenina Always 8 unidades', 'Protector Diario Stayfree 30 unidades',
        'Pañal Huggies Talla M 30 unidades', 'Pañal Pampers Talla M 30 unidades',
        'Perfume Genève 50ml', 'Maquinilla de Afeitar Gillette 2 unidades',
    ],
    'Electrónica': [
        'Foco LED 9W', 'Foco LED 15W', 'Foco Espiral 20W', 'Extensión Eléctrica 3m',
        'Cargador USB Universal', 'Cable HDMI 1.8m', 'Cable USB-C 1m',
        'Auriculares Bluetooth', 'Audífono In-ear', 'Parlante Portátil Bluetooth',
        'Batería Portátil 10000mAh', 'Mouse Inalámbrico', 'Teclado USB',
        'Webcam HD 720p', 'Memoria USB 32GB', 'Memoria USB 64GB',
        'Tarjeta Micro SD 32GB', 'Adaptador WiFi USB', 'Regleta 5 tomas',
        'Pila Alcalina AA x2', 'Pila Alcalina AAA x2', 'Calculadora Casio FX',
        'Radio AM/FM Portátil', 'Plancha de Cabello', 'Secadora de Cabello 1200W',
    ],
    'Ferretería': [
        'Pintura Látex Blanco 1 galón', 'Pintura Látex Amarillo 1 galón',
        'Pintura Esmalte Negro 1/4 galón', 'Thinner 1 litro', 'Brocha 3 pulgadas',
        'Rodillo de Pintar', 'Cinta Masking 2 pulgadas', 'Cinta Aislante Negra',
        'Alambre N°16 1kg', 'Clavo 2 pulgadas 1kg', 'Tornillo Autorroscante x100',
        'Tarugo Plástico x50', 'Llave Inglesa 10 pulgadas', 'Destornillador Estrella',
        'Destornillador Plano', 'Martillo 500g', 'Serrucho 20 pulgadas',
        'Cinta Métrica 5m', 'Nivel Burbuja 30cm', 'Lija Grano 80',
        'Silicona Transparente 280ml', 'Pegamento Epóxico', 'Candado 40mm',
        'Bisagra 3 pulgadas x2', 'Interruptor Simple',
    ],
    'Papelería': [
        'Cuaderno A4 100 hojas', 'Cuaderno A5 80 hojas', 'Libreta Espiral A5',
        'Papel Bond A4 500 hojas', 'Papel Craft 50 hojas', 'Cartulina Blanca A3',
        'Lapicero Bic Azul x12', 'Lapicero Pilot Negro x12', 'Lápiz 2B x12',
        'Borrador Pelikan', 'Tajador Metálico', 'Regla 30cm Transparente',
        'Tijera Escolar 7 pulgadas', 'Engrapador Estándar', 'Grapas 26/6 x1000',
        'Perforador 2 agujeros', 'Folder Manila A4 x50', 'Archivador Oficio Lomo 8',
        'Post-it 3x3 100 hojas', 'Resaltador Amarillo', 'Marcador Permanente Negro',
        'Plumón de Pizarra Azul', 'Corrector Líquido Faber', 'Sobre Manila A4 x50',
        'Cinta Scotch 18mm x50m',
    ],
    'Farmacia': [
        'Paracetamol 500mg x100', 'Ibuprofeno 400mg x100', 'Aspirina 100mg x100',
        'Vitamina C 500mg x60', 'Vitamina D3 1000UI x60', 'Complejo B x60',
        'Calcio + D3 x60', 'Omega 3 x60', 'Zinc 10mg x60', 'Multivitamínico x60',
        'Alcohol 70° 1 litro', 'Agua Oxigenada 120ml', 'Algodón 100g',
        'Gasa Estéril 10x10 x10', 'Esparadrapo 2.5cm x5m', 'Vendaje Elástico 5cm',
        'Termómetro Digital', 'Tensiómetro Digital Brazo', 'Glucómetro Kit',
        'Mascarilla KN95 x10', 'Guantes Nitrilo Talla M x100',
        'Gel Antibacterial 500ml', 'Jabón Antibacterial 250ml',
        'Repelente de Insectos 100ml', 'Pomada Bepanthen 30g',
    ],
}

# Agregar categoría Ropa (simplificada)
productos_por_categoria['Ropa y Calzado'] = [
    f'Polo Básico Talla {t}' for t in ['S', 'M', 'L', 'XL', 'XXL']
] + [
    f'Jean Clásico Talla {t}' for t in ['28', '30', '32', '34', '36']
] + [
    f'Zapatilla Deportiva Talla {t}' for t in ['38', '39', '40', '41', '42', '43']
] + [
    'Calcetines x3 pares', 'Ropa Interior Algodón', 'Polo Manga Larga M',
    'Chompa de Lana M', 'Casaca Impermeable M',
]
# Agregar Juguetería
productos_por_categoria['Juguetería'] = [
    'Pelota de Fútbol N°5', 'Pelota de Básquet N°7', 'Raqueta de Tenis',
    'Muñeca Bebé 30cm', 'Auto de Control Remoto', 'Rompecabezas 500 piezas',
    'Juego de Mesa Monopoly', 'Lego Básico 200 piezas', 'Peluche Oso 40cm',
    'Pistola de Agua', 'Yoyo Profesional', 'Trompo Clásico',
    'Crayolas 24 colores', 'Plastilina 6 colores', 'Kit de Pintura Infantil',
    'Triciclo Infantil', 'Patines 4 ruedas Talla 34', 'Cometa Plástica',
    'Disfraz Superhéroe', 'Globos x50 unidades',
]

productos_creados = []
codigo_counter = 1

for cat_obj in categorias_objs:
    nombres_productos = productos_por_categoria.get(cat_obj.nombre, [])
    for nombre_prod in nombres_productos:
        if len(productos_creados) >= 500:
            break
        codigo = f'PROD{str(codigo_counter).zfill(5)}'
        codigo_counter += 1

        precio_compra = Decimal(str(round(random.uniform(1.5, 150.0), 2)))
        margen = Decimal(str(round(random.uniform(1.15, 1.60), 2)))
        precio_venta = round(precio_compra * margen, 2)
        stock_min = random.randint(5, 20)
        stock_max = random.randint(100, 500)
        stock_actual = random.randint(0, stock_max)
        unidad = random.choice(unidades_objs)
        proveedor = random.choice(proveedores_objs)

        p = Producto.objects.create(
            codigo=codigo,
            nombre=nombre_prod,
            descripcion=f'{nombre_prod} — producto de calidad para distribución comercial.',
            categoria=cat_obj,
            unidad_medida=unidad,
            proveedor=proveedor,
            precio_compra=precio_compra,
            precio_venta=precio_venta,
            stock_actual=Decimal(str(stock_actual)),
            stock_minimo=Decimal(str(stock_min)),
            stock_maximo=Decimal(str(stock_max)),
            activo=True,
        )
        productos_creados.append(p)
    if len(productos_creados) >= 500:
        break

print(f"   ✅ {len(productos_creados)} productos creados")

# Movimientos — entradas y salidas
print("   Creando movimientos...")
admin_user = User.objects.filter(is_superuser=True).first()
motivos_entrada = ['Compra a proveedor', 'Devolución de cliente', 'Transferencia entre almacenes', 'Reposición de stock']
motivos_salida = ['Venta al cliente', 'Transferencia entre almacenes', 'Muestra de producto', 'Venta mayorista']

for _ in range(800):
    producto = random.choice(productos_creados)
    almacen = random.choice(almacenes_objs)
    tipo = random.choice([Movimiento.ENTRADA, Movimiento.SALIDA])
    cantidad = Decimal(str(random.randint(1, 50)))

    if tipo == Movimiento.ENTRADA:
        motivo = random.choice(motivos_entrada)
        precio_u = producto.precio_compra
    else:
        if producto.stock_actual < cantidad:
            continue
        motivo = random.choice(motivos_salida)
        precio_u = producto.precio_venta

    fecha_mov = timezone.make_aware(datetime.combine(
        fecha_aleatoria(date(2024, 1, 1), date.today()),
        datetime.min.time()
    ))

    Movimiento.objects.create(
        tipo=tipo,
        producto=producto,
        almacen=almacen,
        cantidad=cantidad,
        precio_unitario=precio_u,
        motivo=motivo,
        documento_referencia=f'DOC-{random.randint(10000, 99999)}',
        usuario=admin_user,
    )

print("   ✅ Movimientos creados")

# Ajustes de inventario
print("   Creando ajustes...")
motivos_ajuste = ['CONTEO', 'DANO', 'VENCIMIENTO', 'ROBO', 'OTRO']

for _ in range(50):
    producto = random.choice(productos_creados)
    almacen = random.choice(almacenes_objs)
    cantidad_nueva = Decimal(str(random.randint(0, int(producto.stock_maximo))))
    AjusteInventario.objects.create(
        producto=producto,
        almacen=almacen,
        cantidad_anterior=producto.stock_actual,
        cantidad_nueva=cantidad_nueva,
        motivo=random.choice(motivos_ajuste),
        observacion=random.choice([
            'Conteo físico mensual',
            'Producto dañado por humedad',
            'Pérdida detectada en auditoría',
            'Corrección de diferencia de inventario',
            'Producto vencido retirado',
        ]),
        usuario=admin_user,
    )

print("   ✅ Ajustes creados")

# Alertas
print("   Creando alertas...")
for producto in productos_creados:
    if producto.stock_actual == 0:
        Alerta.objects.get_or_create(
            producto=producto,
            tipo=Alerta.SIN_STOCK,
            resuelta=False,
            defaults={'mensaje': f"'{producto.nombre}' no tiene stock disponible."}
        )
    elif producto.stock_actual <= producto.stock_minimo:
        Alerta.objects.get_or_create(
            producto=producto,
            tipo=Alerta.STOCK_BAJO,
            resuelta=False,
            defaults={'mensaje': f"'{producto.nombre}' tiene stock bajo ({producto.stock_actual} {producto.unidad_medida.abreviatura})."}
        )

print("   ✅ Alertas creadas")
print("✅ Inventario completo")

# ─────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("🎉 CARGA DE DATOS COMPLETADA")
print("="*50)
print(f"  Usuarios:      {User.objects.count()}")
print(f"  Departamentos: {Departamento.objects.count()}")
print(f"  Cargos:        {Cargo.objects.count()}")
print(f"  Empleados:     {Empleado.objects.count()}")
print(f"  Contratos:     {Contrato.objects.count()}")
print(f"  Asistencias:   {Asistencia.objects.count()}")
print(f"  Ausencias:     {Ausencia.objects.count()}")
print(f"  Vacaciones:    {Vacaciones.objects.count()}")
print(f"  Documentos:    {Documento.objects.count()}")
print(f"  Productos:     {Producto.objects.count()}")
print(f"  Proveedores:   {Proveedor.objects.count()}")
print(f"  Movimientos:   {Movimiento.objects.count()}")
print(f"  Ajustes:       {AjusteInventario.objects.count()}")
print(f"  Alertas:       {Alerta.objects.count()}")
print("="*50)
print("  Contraseña de todos los usuarios: admin")
print("="*50)
