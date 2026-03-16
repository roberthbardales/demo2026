"""
Script de datos de prueba completo
Ejecutar con: python manage.py shell -c "exec(open('seed_data.py', encoding='utf-8-sig').read())"
"""
import random
from datetime import date, timedelta
from decimal import Decimal
from django.utils import timezone

print("Iniciando carga de datos...")

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
    return '9' + str(random.randint(10000000, 99999999))

distritos = [
    'Miraflores', 'San Isidro', 'Surco', 'La Molina', 'San Borja',
    'Los Olivos', 'San Martin de Porres', 'Independencia', 'Comas',
    'Villa El Salvador', 'Brena', 'Rimac', 'Jesus Maria', 'Lince',
]

calles = [
    'Av. Javier Prado', 'Av. La Marina', 'Av. Arequipa', 'Calle Los Pinos',
    'Jr. Huallaga', 'Av. Brasil', 'Av. Benavides', 'Jr. de la Union',
    'Av. Universitaria', 'Av. Colonial', 'Calle Las Flores', 'Av. Argentina',
]

def direccion():
    return f"{random.choice(calles)} {random.randint(100,999)}, {random.choice(distritos)}, Lima"

nombres_m = [
    'Carlos', 'Juan', 'Pedro', 'Luis', 'Miguel', 'Jorge', 'Roberto', 'Fernando',
    'Ricardo', 'Alejandro', 'Daniel', 'David', 'Sergio', 'Eduardo', 'Manuel',
    'Antonio', 'Francisco', 'Raul', 'Cesar', 'Victor', 'Oscar', 'Rodrigo',
    'Diego', 'Andres', 'Gustavo', 'Javier', 'Pablo', 'Hector', 'Enrique', 'Marco',
]

nombres_f = [
    'Maria', 'Ana', 'Rosa', 'Carmen', 'Patricia', 'Sandra', 'Lucia', 'Claudia',
    'Veronica', 'Gabriela', 'Valeria', 'Sofia', 'Andrea', 'Paola', 'Monica',
    'Jessica', 'Karina', 'Milagros', 'Vanessa', 'Natalia', 'Adriana', 'Diana',
    'Silvia', 'Elena', 'Isabel', 'Roxana', 'Cynthia', 'Gisela', 'Fiorella', 'Melissa',
]

apellidos = [
    'Garcia', 'Rodriguez', 'Lopez', 'Martinez', 'Gonzalez', 'Perez', 'Sanchez',
    'Ramirez', 'Torres', 'Flores', 'Rivera', 'Gomez', 'Diaz', 'Reyes', 'Cruz',
    'Morales', 'Ortiz', 'Gutierrez', 'Chavez', 'Quispe', 'Mamani', 'Huanca',
    'Vargas', 'Rojas', 'Herrera', 'Mendoza', 'Castillo', 'Ramos', 'Paredes',
    'Villanueva', 'Espinoza', 'Vega', 'Castro', 'Alvarado', 'Cisneros',
    'Condori', 'Huaman', 'Cardenas', 'Pacheco', 'Salazar', 'Aguilar', 'Nunez',
]

# ─────────────────────────────────────────────────────────────
# 1. USUARIOS
# ─────────────────────────────────────────────────────────────
print("Creando usuarios...")

from applications.users.models import User

roles_dist = (
    [User.ADMIN] * 3 +
    [User.RRHH] * 7 +
    [User.INVENTARIO] * 10 +
    ['4'] * 8 +
    [User.EMPLEADO] * 22
)
random.shuffle(roles_dist)

usuarios_creados = []
used_emails = set()

for i in range(50):
    genero = random.choice([User.VARON, User.MUJER])
    nombre = random.choice(nombres_m if genero == User.VARON else nombres_f)
    ap1 = random.choice(apellidos)
    ap2 = random.choice(apellidos)

    base = f"{nombre.lower()}.{ap1.lower()}@empresa.com.pe"
    email = base
    c = 1
    while email in used_emails:
        email = base.replace('@', f'{c}@')
        c += 1
    used_emails.add(email)

    u = User.objects.create_user(
        email=email,
        password='admin',
        full_name=f"{nombre} {ap1} {ap2}",
        occupation=roles_dist[i],
        genero=genero,
        date_birth=fecha_aleatoria(date(1975,1,1), date(2000,12,31)),
    )
    usuarios_creados.append(u)

print(f"   {len(usuarios_creados)} usuarios creados")

# ─────────────────────────────────────────────────────────────
# 2. RRHH
# ─────────────────────────────────────────────────────────────
print("Creando RRHH...")

from applications.rrhh.models import (
    Departamento, Cargo, Empleado, Contrato,
    Asistencia, Ausencia, Vacaciones, Documento
)

deps_data = [
    ('Ventas', 'Gestion de ventas'),
    ('Logistica', 'Control de almacen'),
    ('Administracion', 'Gestion administrativa'),
    ('Recursos Humanos', 'Gestion del personal'),
    ('Tecnologia', 'Sistemas de informacion'),
    ('Marketing', 'Publicidad y promociones'),
    ('Finanzas', 'Tesoreria y presupuestos'),
]
deps = []
for n, d in deps_data:
    obj, _ = Departamento.objects.get_or_create(nombre=n, defaults={'descripcion': d})
    deps.append(obj)

cargos_por_dep = {
    'Ventas': ['Gerente de Ventas', 'Supervisor de Ventas', 'Ejecutivo de Ventas', 'Promotor Comercial', 'Cajero'],
    'Logistica': ['Jefe de Almacen', 'Almacenero', 'Operario de Despacho', 'Conductor', 'Auxiliar de Almacen'],
    'Administracion': ['Gerente General', 'Asistente Administrativo', 'Recepcionista', 'Secretaria'],
    'Recursos Humanos': ['Jefe de RRHH', 'Analista de RRHH', 'Asistente de RRHH'],
    'Tecnologia': ['Jefe de TI', 'Desarrollador de Software', 'Soporte Tecnico'],
    'Marketing': ['Jefe de Marketing', 'Disenador Grafico', 'Community Manager'],
    'Finanzas': ['Contador General', 'Tesorero', 'Analista Financiero', 'Asistente Contable'],
}
cargos = []
for dep in deps:
    for nc in cargos_por_dep.get(dep.nombre, []):
        obj, _ = Cargo.objects.get_or_create(nombre=nc, departamento=dep, defaults={'descripcion': nc})
        cargos.append(obj)

empleados = []
used_dnis = set()
estados_e = [Empleado.ACTIVO]*80 + [Empleado.VACACIONES]*10 + [Empleado.LICENCIA]*5 + [Empleado.INACTIVO]*5
random.shuffle(estados_e)

for i in range(100):
    g = random.choice([Empleado.VARON, Empleado.MUJER])
    n = random.choice(nombres_m if g == Empleado.VARON else nombres_f)
    a1 = random.choice(apellidos)
    a2 = random.choice(apellidos)
    dni = dni_aleatorio()
    while dni in used_dnis:
        dni = dni_aleatorio()
    used_dnis.add(dni)

    u_vinc = None
    if i < len(usuarios_creados) and random.random() > 0.6:
        try:
            _ = usuarios_creados[i].empleado
        except Exception:
            u_vinc = usuarios_creados[i]

    emp = Empleado.objects.create(
        codigo=f'EMP{str(i+1).zfill(4)}',
        nombres=n,
        apellidos=f"{a1} {a2}",
        dni=dni,
        genero=g,
        fecha_nacimiento=fecha_aleatoria(date(1975,1,1), date(2000,12,31)),
        email=f"{n.lower()}.{a1.lower()}@empresa.com.pe",
        telefono=telefono_aleatorio(),
        direccion=direccion(),
        cargo=random.choice(cargos),
        fecha_ingreso=fecha_aleatoria(date(2015,1,1), date(2024,12,31)),
        sueldo_base=Decimal(str(random.choice([1025,1200,1500,1800,2000,2500,3000,3500,4000,5000]))),
        estado=estados_e[i],
        usuario=u_vinc,
    )
    empleados.append(emp)

print(f"   {len(empleados)} empleados")

for emp in empleados:
    fi = emp.fecha_ingreso
    for j in range(random.randint(1,3)):
        tipo = random.choice([Contrato.INDEFINIDO, Contrato.PLAZO_FIJO, Contrato.PRACTICAS, Contrato.LOCACION])
        if tipo == Contrato.INDEFINIDO:
            ff, est = None, Contrato.VIGENTE
        else:
            ff = fi + timedelta(days=random.randint(90,365))
            est = Contrato.VIGENTE if ff > date.today() else Contrato.VENCIDO
        Contrato.objects.create(
            empleado=emp, tipo=tipo, fecha_inicio=fi, fecha_fin=ff,
            sueldo=emp.sueldo_base + Decimal(str(random.randint(0,500))),
            estado=est, observaciones=f'Contrato #{j+1}',
        )
        if ff:
            fi = ff + timedelta(days=1)

admin_user = User.objects.filter(is_superuser=True).first()
hoy = date.today()
estados_a = [Asistencia.PRESENTE]*20 + [Asistencia.TARDANZA]*3 + [Asistencia.FALTA]*1 + [Asistencia.JUSTIFICADO]*1

for emp in random.sample(empleados, min(60, len(empleados))):
    d = hoy - timedelta(days=30)
    while d <= hoy:
        if d.weekday() < 5:
            est = random.choice(estados_a)
            he = hs = None
            if est in [Asistencia.PRESENTE, Asistencia.TARDANZA]:
                h = 8 if est == Asistencia.PRESENTE else random.randint(9,10)
                he = f"{h:02d}:{random.randint(0,59):02d}:00"
                hs = f"{random.randint(17,18):02d}:{random.randint(0,59):02d}:00"
            Asistencia.objects.get_or_create(
                empleado=emp, fecha=d,
                defaults={'hora_entrada':he,'hora_salida':hs,'estado':est,'registrado_por':admin_user}
            )
        d += timedelta(days=1)

tipos_aus = [Ausencia.ENFERMEDAD, Ausencia.PERSONAL, Ausencia.FAMILIAR, Ausencia.CAPACITACION, Ausencia.OTRO]
estados_aus = [Ausencia.APROBADO]*3 + [Ausencia.PENDIENTE, Ausencia.RECHAZADO]
motivos_aus = ['Enfermedad con certificado', 'Tramites personales', 'Emergencia familiar', 'Capacitacion externa', 'Cita medica']

for emp in random.sample(empleados, min(40, len(empleados))):
    for _ in range(random.randint(1,3)):
        ini = fecha_aleatoria(date(2024,1,1), date(2025,6,30))
        fin = ini + timedelta(days=random.randint(1,5))
        est = random.choice(estados_aus)
        Ausencia.objects.create(
            empleado=emp, tipo=random.choice(tipos_aus),
            fecha_inicio=ini, fecha_fin=fin,
            motivo=random.choice(motivos_aus), estado=est,
            aprobado_por=admin_user if est != Ausencia.PENDIENTE else None,
        )

estados_vac = [Vacaciones.APROBADO]*2 + [Vacaciones.GOZADO, Vacaciones.PENDIENTE]
for emp in random.sample(empleados, min(50, len(empleados))):
    for _ in range(random.randint(1,2)):
        ini = fecha_aleatoria(date(2023,1,1), date(2025,3,31))
        dias = random.choice([7,14,15,21,30])
        est = random.choice(estados_vac)
        Vacaciones.objects.create(
            empleado=emp, fecha_inicio=ini, fecha_fin=ini+timedelta(days=dias),
            dias_solicitados=dias, estado=est,
            aprobado_por=admin_user if est != Vacaciones.PENDIENTE else None,
            observaciones='Vacaciones anuales' if dias >= 15 else 'Vacaciones parciales',
        )

tipos_doc = [Documento.DNI, Documento.CV, Documento.CONTRATO, Documento.CERTIFICADO, Documento.TITULO]
ndoc = {Documento.DNI:'DNI escaneado', Documento.CV:'Curriculum Vitae', Documento.CONTRATO:'Contrato firmado', Documento.CERTIFICADO:'Certificado', Documento.TITULO:'Titulo profesional'}

for emp in random.sample(empleados, min(70, len(empleados))):
    for tipo in random.sample(tipos_doc, random.randint(2,4)):
        fe = fecha_aleatoria(date(2010,1,1), date(2023,12,31))
        Documento.objects.create(
            empleado=emp, tipo=tipo, nombre=ndoc[tipo],
            archivo='documentos/placeholder.pdf', fecha_emision=fe,
            fecha_vencimiento=fe+timedelta(days=365*5) if tipo==Documento.DNI else None,
            observaciones='Documento verificado',
        )

print("RRHH completo")

# ─────────────────────────────────────────────────────────────
# 3. INVENTARIO
# ─────────────────────────────────────────────────────────────
print("Creando Inventario...")

from applications.inventario.models import (
    UnidadMedida, Categoria, Almacen, Proveedor,
    Producto, Movimiento, AjusteInventario, Alerta
)

for n, a in [('Unidad','UND'),('Kilogramo','KG'),('Gramo','GR'),('Litro','LT'),('Mililitro','ML'),('Metro','MT'),('Caja','CJA'),('Bolsa','BLS'),('Docena','DOC'),('Par','PAR'),('Paquete','PKT')]:
    UnidadMedida.objects.get_or_create(nombre=n, defaults={'abreviatura':a})

unidades = list(UnidadMedida.objects.all())

for n, d in [('Abarrotes','Productos de primera necesidad'),('Bebidas','Bebidas y liquidos'),('Limpieza','Productos de limpieza'),('Cuidado Personal','Higiene personal'),('Electronica','Tecnologia'),('Ropa y Calzado','Vestimenta'),('Ferreteria','Herramientas'),('Jugueteria','Juguetes'),('Papeleria','Utiles de oficina'),('Farmacia','Medicamentos OTC')]:
    Categoria.objects.get_or_create(nombre=n, defaults={'descripcion':d})

categorias = list(Categoria.objects.all())
cat_map = {c.nombre: c for c in categorias}

for n, ub in [('Almacen Central','Av. Argentina 1250, Lima'),('Almacen Norte','Av. Tupac Amaru 3400, Comas'),('Almacen Sur','Av. Pachacutec 1800, VES'),('Almacen Este','Av. Gran Chimu 500, SJL')]:
    Almacen.objects.get_or_create(nombre=n, defaults={'ubicacion':ub,'responsable':random.choice(usuarios_creados)})

almacenes = list(Almacen.objects.all())

for n, ruc, ct in [('Alicorp S.A.A.',ruc_aleatorio(),'Luis Torres'),('Gloria S.A.',ruc_aleatorio(),'Maria Quispe'),('Backus Johnston',ruc_aleatorio(),'Carlos Mendoza'),('Procter Gamble Peru',ruc_aleatorio(),'Ana Flores'),('Unilever Andina Peru',ruc_aleatorio(),'Pedro Rojas'),('Nestle Peru S.A.',ruc_aleatorio(),'Sandra Garcia'),('Kimberly Clark Peru',ruc_aleatorio(),'Roberto Diaz'),('Bimbo Peru S.A.',ruc_aleatorio(),'Claudia Vargas'),('Ajinomoto del Peru',ruc_aleatorio(),'Diego Castillo'),('Aje Group',ruc_aleatorio(),'Valeria Huanca'),('Distribuidora Norte SAC',ruc_aleatorio(),'Marco Lopez'),('Importaciones Sur EIRL',ruc_aleatorio(),'Fiorella Ccopa')]:
    Proveedor.objects.get_or_create(nombre=n, defaults={'ruc':ruc,'contacto':ct,'telefono':telefono_aleatorio(),'email':f"ventas@{n.lower().replace(' ','')[:15]}.com.pe",'direccion':direccion()})

proveedores = list(Proveedor.objects.all())

prods_lista = [
    ('Arroz Extra Superior','Abarrotes'),('Azucar Rubia 1kg','Abarrotes'),('Aceite Vegetal 1L','Abarrotes'),
    ('Fideos Tallarin 500g','Abarrotes'),('Avena Quaker 400g','Abarrotes'),('Leche Gloria Evaporada','Abarrotes'),
    ('Mayonesa Alacena 500g','Abarrotes'),('Atun Florida 170g','Abarrotes'),('Mantequilla Gloria 90g','Abarrotes'),
    ('Mermelada Fanny Fresa','Abarrotes'),('Cafe Nescafe Classic 200g','Abarrotes'),('Sal de Mesa 1kg','Abarrotes'),
    ('Harina Sin Preparar 1kg','Abarrotes'),('Chocolate Sublime 32g','Abarrotes'),('Galleta Oreo 137g','Abarrotes'),
    ('Cereal Angel 500g','Abarrotes'),('Quinua 500g','Abarrotes'),('Ketchup Alacena 400g','Abarrotes'),
    ('Sardina en Salsa 170g','Abarrotes'),('Miel de Abeja 250g','Abarrotes'),
    ('Gaseosa Inca Kola 1.5L','Bebidas'),('Gaseosa Coca Cola 1.5L','Bebidas'),('Agua San Luis 625ml','Bebidas'),
    ('Jugo Frugos Durazno 1L','Bebidas'),('Leche Gloria UHT 1L','Bebidas'),('Yogurt Gloria Fresa 1kg','Bebidas'),
    ('Bebida Powerade 500ml','Bebidas'),('Cerveza Cristal 650ml','Bebidas'),('Cerveza Pilsen 650ml','Bebidas'),
    ('Agua Cielo 625ml','Bebidas'),('Jugo Pulp Naranja 500ml','Bebidas'),('Gaseosa Pepsi 1.5L','Bebidas'),
    ('Detergente Ariel 360g','Limpieza'),('Lejia Clorox 680ml','Limpieza'),('Jabon Marsella 230g','Limpieza'),
    ('Limpiatodo Sapolio 500ml','Limpieza'),('Papel Higienico Elite 4 rollos','Limpieza'),('Suavitel 850ml','Limpieza'),
    ('Esponja de Cocina 2u','Limpieza'),('Bolsa de Basura 10u','Limpieza'),('Papel Toalla Scott 3 rollos','Limpieza'),
    ('Lavavajilla Ayudin 360g','Limpieza'),
    ('Shampoo Pantene 400ml','Cuidado Personal'),('Jabon Dove 90g','Cuidado Personal'),
    ('Desodorante Rexona 150ml','Cuidado Personal'),('Crema Nivea 400ml','Cuidado Personal'),
    ('Pasta Dental Colgate 90g','Cuidado Personal'),('Cepillo Dental Colgate','Cuidado Personal'),
    ('Toalla Femenina Always 8u','Cuidado Personal'),('Pañal Huggies Talla M 30u','Cuidado Personal'),
    ('Shampoo Head Shoulders 400ml','Cuidado Personal'),('Bloqueador Solar FPS50 120ml','Cuidado Personal'),
    ('Foco LED 9W','Electronica'),('Cable HDMI 1.8m','Electronica'),('Cargador USB Universal','Electronica'),
    ('Memoria USB 32GB','Electronica'),('Mouse Inalambrico','Electronica'),('Auriculares Bluetooth','Electronica'),
    ('Bateria Portatil 10000mAh','Electronica'),('Extension Electrica 3m','Electronica'),
    ('Pila Alcalina AA x2','Electronica'),('Calculadora Casio FX','Electronica'),
    ('Polo Basico Talla M','Ropa y Calzado'),('Jean Clasico Talla 32','Ropa y Calzado'),
    ('Zapatilla Deportiva Talla 40','Ropa y Calzado'),('Calcetines x3 pares','Ropa y Calzado'),
    ('Chompa de Lana M','Ropa y Calzado'),('Casaca Impermeable M','Ropa y Calzado'),
    ('Polo Manga Larga M','Ropa y Calzado'),('Jean Clasico Talla 30','Ropa y Calzado'),
    ('Pintura Latex Blanco 1 galon','Ferreteria'),('Martillo 500g','Ferreteria'),
    ('Destornillador Estrella','Ferreteria'),('Cinta Metrica 5m','Ferreteria'),
    ('Clavo 2 pulgadas 1kg','Ferreteria'),('Llave Inglesa 10 pulgadas','Ferreteria'),
    ('Serrucho 20 pulgadas','Ferreteria'),('Taladro Electrico 500W','Ferreteria'),
    ('Pelota de Futbol N5','Jugueteria'),('Rompecabezas 500 piezas','Jugueteria'),
    ('Muneca Bebe 30cm','Jugueteria'),('Auto de Control Remoto','Jugueteria'),
    ('Crayolas 24 colores','Jugueteria'),('Lego Basico 200 piezas','Jugueteria'),
    ('Cuaderno A4 100 hojas','Papeleria'),('Lapicero Bic Azul x12','Papeleria'),
    ('Papel Bond A4 500 hojas','Papeleria'),('Folder Manila A4 x50','Papeleria'),
    ('Archivador Oficio Lomo 8','Papeleria'),('Resaltador Amarillo','Papeleria'),
    ('Tijera Escolar 7 pulgadas','Papeleria'),('Engrapador Estandar','Papeleria'),
    ('Paracetamol 500mg x100','Farmacia'),('Vitamina C 500mg x60','Farmacia'),
    ('Alcohol 70 grados 1 litro','Farmacia'),('Agua Oxigenada 120ml','Farmacia'),
    ('Mascarilla KN95 x10','Farmacia'),('Gel Antibacterial 500ml','Farmacia'),
    ('Termometro Digital','Farmacia'),('Ibuprofeno 400mg x100','Farmacia'),
]

productos = []
for i, (np, cat_n) in enumerate(prods_lista):
    cat = cat_map.get(cat_n, random.choice(categorias))
    pc = Decimal(str(round(random.uniform(1.5, 150.0), 2)))
    pv = round(pc * Decimal(str(round(random.uniform(1.15, 1.60), 2))), 2)
    smin = random.randint(5, 20)
    smax = random.randint(100, 500)
    sa = random.randint(smin, smax)
    p = Producto.objects.create(
        codigo=f'PROD{str(i+1).zfill(5)}',
        nombre=np,
        descripcion=f'{np} - producto de calidad.',
        categoria=cat,
        unidad_medida=random.choice(unidades),
        proveedor=random.choice(proveedores),
        precio_compra=pc,
        precio_venta=pv,
        stock_actual=Decimal(str(sa)),
        stock_minimo=Decimal(str(smin)),
        stock_maximo=Decimal(str(smax)),
        activo=True,
    )
    productos.append(p)

print(f"   {len(productos)} productos")

mot_e = ['Compra a proveedor', 'Devolucion de cliente', 'Reposicion de stock']
mot_s = ['Venta al cliente', 'Muestra de producto', 'Venta mayorista']

for _ in range(500):
    prod = random.choice(productos)
    alm = random.choice(almacenes)
    tipo = random.choice([Movimiento.ENTRADA, Movimiento.SALIDA])
    cant = Decimal(str(random.randint(1, 50)))
    if tipo == Movimiento.SALIDA and prod.stock_actual < cant:
        tipo = Movimiento.ENTRADA
    Movimiento.objects.create(
        tipo=tipo, producto=prod, almacen=alm, cantidad=cant,
        precio_unitario=prod.precio_compra if tipo == Movimiento.ENTRADA else prod.precio_venta,
        motivo=random.choice(mot_e if tipo == Movimiento.ENTRADA else mot_s),
        documento_referencia=f'DOC-{random.randint(10000,99999)}',
        usuario=admin_user or random.choice(usuarios_creados),
    )

for _ in range(30):
    prod = random.choice(productos)
    AjusteInventario.objects.create(
        producto=prod, almacen=random.choice(almacenes),
        cantidad_anterior=prod.stock_actual,
        cantidad_nueva=Decimal(str(random.randint(0, int(prod.stock_maximo)))),
        motivo=random.choice(['CONTEO','DANO','VENCIMIENTO','ROBO','OTRO']),
        observacion='Ajuste periodico',
        usuario=admin_user or random.choice(usuarios_creados),
    )

for prod in productos:
    if prod.stock_actual == 0:
        Alerta.objects.get_or_create(producto=prod, tipo=Alerta.SIN_STOCK, resuelta=False, defaults={'mensaje': f"'{prod.nombre}' sin stock."})
    elif prod.stock_actual <= prod.stock_minimo:
        Alerta.objects.get_or_create(producto=prod, tipo=Alerta.STOCK_BAJO, resuelta=False, defaults={'mensaje': f"'{prod.nombre}' stock bajo."})

print("Inventario completo")

# ─────────────────────────────────────────────────────────────
# 4. VENTAS
# ─────────────────────────────────────────────────────────────
print("Creando Ventas...")

from applications.ventas.models import (
    Cliente, Pedido, DetallePedido, Comprobante, DetalleComprobante
)

empresas = [
    'Supermercados Metro SAC','Distribuidora Lima Norte EIRL','Minimarket El Sol SAC',
    'Bodega Central SRL','Inversiones Andinas SAC','Comercial Pacifico EIRL',
    'Hipermercado Plaza SAC','Distribuciones Sur Peru SRL','Mayorista Central SAC',
    'Tiendas El Campo EIRL','Supermercado La Canasta SAC','Distribuciones Oriente SRL',
    'Comercio Unidos Peru SAC','Megacentro Comercial SRL','Importaciones Lima SAC',
    'Bodega Los Alamos EIRL','Distribuciones Rapidas SAC','Comercial San Martin SRL',
    'Tiendas Populares SAC','Mayoreo Andino EIRL','Inversiones del Norte SAC',
    'Bodega La Estrella EIRL','Comercializadora Lima SRL','Distribuciones Peruanas SAC',
    'Almacenes del Sur EIRL','Comercial Los Andes SAC','Megatiendas Peru SRL',
    'Distribuidora Central SAC','Supermercado Popular EIRL','Tiendas Express SAC',
]

clientes = []
used_docs = set()

for i in range(50):
    n = random.choice(nombres_m + nombres_f)
    a = random.choice(apellidos)
    dni = dni_aleatorio()
    while dni in used_docs:
        dni = dni_aleatorio()
    used_docs.add(dni)
    clientes.append(Cliente.objects.create(
        tipo=Cliente.NATURAL,
        nombre=f"{n} {a} {random.choice(apellidos)}",
        documento=dni,
        email=f"{n.lower()}.{a.lower()}@gmail.com",
        telefono=telefono_aleatorio(),
        direccion=direccion(),
    ))

for i in range(50):
    emp = empresas[i % len(empresas)]
    if i >= len(empresas):
        emp = f"{emp} {i}"
    ruc = ruc_aleatorio()
    while ruc in used_docs:
        ruc = ruc_aleatorio()
    used_docs.add(ruc)
    clientes.append(Cliente.objects.create(
        tipo=Cliente.JURIDICA,
        nombre=emp,
        documento=ruc,
        email=f"ventas@{emp.lower().replace(' ','')[:15]}.com.pe",
        telefono=telefono_aleatorio(),
        direccion=direccion(),
    ))

print(f"   {len(clientes)} clientes")

vendedores = list(User.objects.filter(occupation__in=['4','0']))
if not vendedores:
    vendedores = usuarios_creados[:5]

estados_p = [Pedido.ENTREGADO]*50 + [Pedido.CONFIRMADO]*25 + [Pedido.PENDIENTE]*20 + [Pedido.ANULADO]*5
random.shuffle(estados_p)

cf = cb = 1
for i in range(100):
    cli = random.choice(clientes)
    vend = random.choice(vendedores)
    fp = fecha_aleatoria(date(2024,1,1), date.today())
    est = estados_p[i]
    prods_sel = random.sample(productos, random.randint(1,5))

    pedido = Pedido.objects.create(
        numero=f"PED-{str(i+1).zfill(6)}",
        cliente=cli, vendedor=vend, fecha=fp, estado=est,
        observaciones=f'Pedido #{i+1}',
        subtotal=Decimal('0'), igv=Decimal('0'), total=Decimal('0'),
    )

    subtotal = Decimal('0')
    for prod in prods_sel:
        cant = Decimal(str(random.randint(1,20)))
        desc = Decimal(str(random.choice([0,0,0,5,10])))
        det_sub = round(cant * prod.precio_venta * (1 - desc / Decimal('100')), 2)
        subtotal += det_sub
        DetallePedido.objects.create(
            pedido=pedido, producto=prod, cantidad=cant,
            precio_unitario=prod.precio_venta, descuento=desc,
        )

    igv = round(subtotal * Decimal('0.18'), 2)
    pedido.subtotal = subtotal
    pedido.igv = igv
    pedido.total = subtotal + igv
    pedido.save(update_fields=['subtotal','igv','total'])

    if est in [Pedido.ENTREGADO, Pedido.CONFIRMADO]:
        tipo_c = Comprobante.FACTURA if cli.tipo == Cliente.JURIDICA else Comprobante.BOLETA
        if tipo_c == Comprobante.FACTURA:
            serie, num_c = 'F001', str(cf).zfill(8)
            cf += 1
        else:
            serie, num_c = 'B001', str(cb).zfill(8)
            cb += 1

        comp = Comprobante.objects.create(
            tipo=tipo_c, serie=serie, numero=num_c,
            pedido=pedido, cliente=cli, vendedor=vend,
            fecha_emision=fp,
            subtotal=pedido.subtotal, igv=pedido.igv, total=pedido.total,
            estado=Comprobante.EMITIDO,
            observaciones='Comprobante emitido',
        )
        for det in pedido.detalles.select_related('producto'):
            DetalleComprobante.objects.create(
                comprobante=comp, producto=det.producto,
                descripcion=det.producto.nombre,
                cantidad=det.cantidad, precio_unitario=det.precio_unitario,
                descuento=det.descuento, subtotal=det.subtotal,
            )

print("Ventas completo")

# ─────────────────────────────────────────────────────────────
# RESUMEN
# ─────────────────────────────────────────────────────────────
print("\n" + "="*50)
print("CARGA COMPLETADA")
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
print(f"  Alertas:       {Alerta.objects.count()}")
print(f"  Clientes:      {Cliente.objects.count()}")
print(f"  Pedidos:       {Pedido.objects.count()}")
print(f"  Comprobantes:  {Comprobante.objects.count()}")
print("="*50)
print("  Contrasena: admin")
print("="*50)
