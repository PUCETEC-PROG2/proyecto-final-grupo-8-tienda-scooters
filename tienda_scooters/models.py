from django.db import models
from django.core.validators import MinLengthValidator, RegexValidator
from datetime import date
from django.core.exceptions import ValidationError

# Modelo Cliente
class Cliente(models.Model):
    id_cliente = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, null=False, verbose_name="Nombre")
    apellido = models.CharField(max_length=50, null=False, verbose_name="Apellido")
    direccion = models.CharField(max_length=100, null=False, verbose_name="Dirección")
    correo = models.EmailField(max_length=100, null=False, unique=True, verbose_name="Correo Electrónico")
    cedula = models.CharField(
        max_length=20,
        validators=[
            MinLengthValidator(10, message="La cédula debe tener al menos 10 dígitos."),
            RegexValidator(r'^\d+$', message="La cédula debe contener solo números.")
        ],
        unique=True,
        verbose_name="Cédula"
    )
    telefono = models.CharField(
        max_length=15,
        validators=[
            MinLengthValidator(10, message="El número de teléfono debe tener al menos 10 dígitos."),
            RegexValidator(r'^\d+$', message="El número de teléfono debe contener solo números.")
        ],
        verbose_name="Teléfono"
    )

    def __str__(self):
        return f"{self.nombre} {self.apellido} - {self.correo}"

    class Meta:
        indexes = [
            models.Index(fields=['cedula']),
            models.Index(fields=['correo']),
        ]

# Modelo Producto
class Producto(models.Model):
    id_producto = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, null=False, verbose_name="Nombre del Producto")
    descripcion = models.TextField(null=True, blank=True, verbose_name="Descripción")
    precio = models.DecimalField(max_digits=10, decimal_places=2, null=False, verbose_name="Precio")

    def __str__(self):
        return f"{self.nombre} - ${self.precio}"

    class Meta:
        indexes = [
            models.Index(fields=['nombre']),
            models.Index(fields=['precio']),
        ]

# Modelo Inventario
class Inventario(models.Model):
    id_inventario = models.AutoField(primary_key=True)
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(null=False, verbose_name="Cantidad en Inventario")

    def __str__(self):
        return f"{self.producto.nombre} - Cantidad: {self.cantidad}"

    class Meta:
        indexes = [
            models.Index(fields=['producto']),
        ]

# Modelo Compras
class Compra(models.Model):
    id_compra = models.AutoField(primary_key=True)
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, verbose_name="Cliente")
    productos = models.ManyToManyField(Producto, through='DetalleCompra', verbose_name="Productos")
    fecha_compra = models.DateField(default=date.today, verbose_name="Fecha de Compra")

    def calcular_precio_total(self):
        total = sum(detalle.subtotal for detalle in self.detallecompra_set.all())
        return total

    def __str__(self):
        return f"Compra {self.id_compra} - Cliente: {self.cliente.nombre} {self.cliente.apellido}"

    class Meta:
        indexes = [
            models.Index(fields=['cliente']),
            models.Index(fields=['fecha_compra']),
        ]

# Modelo DetalleCompra (relación intermedia entre Compra y Producto)
class DetalleCompra(models.Model):
    compra = models.ForeignKey(Compra, on_delete=models.CASCADE, verbose_name="Compra")
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, verbose_name="Producto")
    cantidad = models.PositiveIntegerField(null=False, verbose_name="Cantidad")

    @property
    def subtotal(self):
        return self.cantidad * self.producto.precio

    def __str__(self):
        return f"Compra: {self.compra.id_compra}, Producto: {self.producto.nombre}, Cantidad: {self.cantidad}, Subtotal: ${self.subtotal}"

    class Meta:
        unique_together = ('compra', 'producto')
        indexes = [
            models.Index(fields=['compra']),
            models.Index(fields=['producto']),
        ]
