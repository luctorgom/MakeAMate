from django.db import models

class Suscripcion(models.Model):
    name = models.CharField(max_length=191)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name


