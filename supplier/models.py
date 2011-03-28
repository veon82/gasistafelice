"""These models include information about Products, Suppliers, Producers.

These are fundamental DES data to rely on. They represent market offering.

Models here rely on base model classes.

Definition: `Vocabolario - Fornitori <http://www.jagom.org/trac/REESGas/wiki/BozzaVocabolario#Fornitori>`__ (ITA only)
"""

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from gasistafelice.base import const
from gasistafelice.base.models import Person, Place

class Supplier(models.Model):
    """An actor having a stock of Products for sale to the DES."""

    name = models.CharField(max_length=128) 
    seat =  models.ForeignKey(Place)
    vat_number =  models.CharField(max_length=128, unique=True) #TODO: perhaps a custom field needed here ? (for validation purposes)
    website =  models.URLField(verify_exists=True, blank=True)
    referrers = models.ManyToManyField(Person, through="SupplierReferrer") 
    flavour = models.CharField(max_length=128, choices=const.SUPPLIER_FLAVOUR_LIST, default=const.SUPPLIER_FLAVOUR_LIST[0][0])
    certifications = models.ManyToManyField('Certification')

    # the set of products provided by this Supplier to every GAS
    @property
    def product_catalog(self):
        return [s.product for s in SupplierStock.objects.filter(supplier=self)]

    def __unicode__(self):
        return self.name

class SupplierReferrer(models.Model):
    supplier = models.ForeignKey(Supplier)
    person = models.ForeignKey(Person)
    job_title = models.CharField(max_length=256, blank=True)
    job_description = models.TextField(blank=True)

    
class Certification(models.Model):
    name = models.CharField(max_length=128, unique=True) 
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class ProductCategory(models.Model):
    # Proposal: the name is in the form MAINCATEGORY::SUBCATEGORY
    # like sourceforge categories
    name = models.CharField(max_length=128, unique=True, blank=False)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class ProductMU(models.Model):
    """Measurement unit for a Product.
         
    """
    # Implemented as a separated entity like GasDotto software.
    # Each SupplierReferrer has to be able to create its own measurement units.
    
    name = models.CharField(max_length=32, unique=True, blank=False)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.name

class Product(models.Model):

    uuid = models.CharField(max_length=128, unique=True, blank=True, null=True) # if empty, should be programmatically set at DB save time
    producer = models.ForeignKey(Supplier)
    category = models.ForeignKey(ProductCategory)
    mu = models.ForeignKey(ProductMU)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    
    @property
    def referrers(self):
        return self.producer.referrers.all()

class SupplierStock(models.Model):
    """A Product that a Supplier offers in the DES marketplace.
        
       Includes price, order constraints and availability information.          
    """

    supplier = models.ForeignKey(Supplier)
    product = models.ForeignKey(Product)
    price = models.FloatField() # FIXME: should be a `CurrencyField` ?
    amount_available = models.PositiveIntegerField(default=const.ALWAYS_AVAILABLE)
    ## constraints posed by the Supplier on orders issued by *every* GAS
    # minimum amount of Product units a GAS is able to order 
    order_minimum_amount = models.PositiveIntegerField(null=True, blank=True)
    # increment step (in Product units) for amounts exceeding minimum; 
    # useful when a Product ships in packages containing multiple units.
    order_step = models.PositiveSmallIntegerField(null=True, blank=True)
    # how the Product will be delivered
    delivery_terms = models.TextField(null=True, blank=True) #FIXME: find a better name for this attribute 
    @property
    def producer(self):
        return self.product.producer
