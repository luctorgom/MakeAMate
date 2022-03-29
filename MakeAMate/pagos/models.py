from django.db import models

class Suscripcion(models.Model):
    name = models.CharField(max_length=191)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField()

    def __str__(self):
        return self.name
        
class Order(models.Model):
	suscripcion = models.ForeignKey(Suscripcion, max_length=200, null=True, blank=True, on_delete = models.SET_NULL)
	created =  models.DateTimeField(auto_now_add=True) 

	def __str__(self):
		return self.product.name

