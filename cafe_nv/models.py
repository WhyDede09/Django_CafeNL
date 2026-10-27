from decimal import Decimal

from django.db import models


class Cliente(models.Model):
    first_name = models.CharField(verbose_name="Nome", max_length=30)
    last_name = models.CharField(verbose_name="Sobrenome", max_length=30)
    email = models.EmailField(verbose_name="E-mail", unique=True)
    phone = models.CharField(verbose_name="Telefone", max_length=20, blank=True)

    class Meta:
        verbose_name = "Cliente"
        verbose_name_plural = "Clientes"
        ordering = ["first_name"]

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


class Categoria(models.Model):
    name = models.CharField(verbose_name="Nome da categoria", max_length=50, unique=True)

    class Meta:
        verbose_name = "Categoria"
        verbose_name_plural = "Categorias"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Produto(models.Model):
    name = models.CharField(verbose_name="Nome do produto", max_length=100)
    description = models.TextField(verbose_name="Descrição", blank=True)
    price = models.DecimalField(
        verbose_name="Preço (R$)",
        max_digits=7,
        decimal_places=2,
        default=Decimal("0.00"),
    )
    image = models.ImageField(
        verbose_name="Imagem",
        upload_to="produtos/",
        blank=True,
        null=True,
    )
    available = models.BooleanField(verbose_name="Disponível", default=True)
    category = models.ForeignKey(
        Categoria,
        on_delete=models.PROTECT,
        verbose_name="Categoria",
        related_name="produtos",
    )

    class Meta:
        verbose_name = "Produto"
        verbose_name_plural = "Produtos"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Pedido(models.Model):
    STATUS_CHOICES = [
        ("P", "Pendente"),
        ("A", "Em preparo"),
        ("R", "Pronto para retirada"),
        ("E", "Entregue"),
        ("C", "Cancelado"),
    ]

    PAYMENT_CHOICES = [
        ("PIX", "Pix"),
        ("CC", "Cartão de crédito"),
        ("CD", "Cartão de débito"),
        ("DN", "Dinheiro"),
    ]

    customer = models.ForeignKey(
        Cliente,
        on_delete=models.CASCADE,
        verbose_name="Cliente",
        related_name="pedidos",
    )
    status = models.CharField(
        verbose_name="Status",
        max_length=1,
        choices=STATUS_CHOICES,
        default="P",
    )
    payment_method = models.CharField(
        verbose_name="Forma de pagamento",
        max_length=3,
        choices=PAYMENT_CHOICES,
        default="PIX",
    )
    notes = models.TextField(verbose_name="Observações", blank=True)
    created_at = models.DateTimeField(verbose_name="Data do pedido", auto_now_add=True)

    class Meta:
        verbose_name = "Pedido"
        verbose_name_plural = "Pedidos"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Pedido #{self.pk} - {self.customer}"

    @property
    def total(self):
        return sum((item.subtotal for item in self.itens.all()), Decimal("0.00"))


class ItemPedido(models.Model):
    order = models.ForeignKey(
        Pedido,
        on_delete=models.CASCADE,
        verbose_name="Pedido",
        related_name="itens",
    )
    product = models.ForeignKey(
        Produto,
        on_delete=models.PROTECT,
        verbose_name="Produto",
    )
    quantity = models.PositiveIntegerField(verbose_name="Quantidade", default=1)
    unit_price = models.DecimalField(
        verbose_name="Preço unitário (R$)",
        max_digits=7,
        decimal_places=2,
    )

    class Meta:
        verbose_name = "Item do pedido"
        verbose_name_plural = "Itens do pedido"

    def __str__(self):
        return f"{self.quantity}x {self.product}"

    @property
    def subtotal(self):
        return self.quantity * self.unit_price

    def save(self, *args, **kwargs):
        # Guarda o preço do produto no momento da compra,
        # para que alterações futuras no cardápio não afetem pedidos antigos.
        if self.unit_price is None:
            self.unit_price = self.product.price
        super().save(*args, **kwargs)