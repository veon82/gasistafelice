"""These models include everything necessary to manage GAS activity.

They rely on base models and Supplier-related ones to get Product and Stock infos.

Definition: `Vocabolario - GAS <http://www.jagom.org/trac/REESGas/wiki/BozzaVocabolario#GAS>`__ (ita only)
"""

from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from gasistafelice.base.models import Person, Role, DefaultWorkflow
from gasistafelice.supplier.models import Supplier, SupplierStock

from gasistafelice.gas.const import STATES_LIST
from gasistafelice.gas import managers

from workflows.models import Workflow, Transition

class GAS(models.Model):
    """A group of people which make some purchases together.
    Every GAS member has a Role where the basic Role is just to be a member of the GAS.

    """
    #TODO: Prevedere qui tutta la parte di configurazione del GAS

    name = models.CharField(max_length=128)
    logo = models.ImageField(upload_to="/images/")
    description = models.TextField(help_text=_("Who are you? What are yours specialties?"))

    workflow_default_gasmember_order = models.ForeignKey(DefaultWorkflow)
    workflow_default_gassupplier_order = models.ForeignKey(DefaultWorkflow)

    supplier_set = models.ManyToManyField(Supplier, through='GASSupplierSolidalPact')

    objects = managers.GASRolesManager()

    class Meta:
        verbose_name_plural = _('GAS')

    def __unicode__(self):
        return self.name
    

class GASMember(models.Model):
    """A bind of a Person into a GAS.
    Each GAS member specifies which Roles he is available for.
    This way, every time there is a need to assign one or more GAS Members to a given Role,
    there is already a group of people to choose from. 
    
    """

    person = models.ForeignKey(Person)
    gas = models.ForeignKey(GAS)
    available_for_role_set = models.ManyToManyField(Role, null=True, blank=True, related_name="gasmember_available_for_roles_set")
    role_set = models.ManyToManyField(Role, null=True, blank=True, related_name="gasmember_set")

    def __unicode__(self):
        return _("%(person)s of %(gas)s GAS") % {'person' : self.person, 'gas': self.gas}

#    def save(self):
#        self.first_name = self.name
#        self.last_name = self.last_name
#        super(GASUser, self).save()
    
class GASSupplierSolidalPact(models.Model):
    """Define a GAS <-> Supplier relationship agreement.
    Each Supplier comes into relathionship with a GAS by signing this pact.
    In this pact we factorize behaviour agreements 
    between these two entities.
    It acts as configuration for order and delivery management 
    to the specific supplier.
    """

    gas = models.ForeignKey(GAS)
    supplier = models.ForeignKey(Supplier)
    date_signed = models.DateField()
    order_minimum_amount = models.PositiveIntegerField(null=True, blank=True)
    order_delivery_cost = models.PositiveIntegerField(null=True, blank=True)
    order_deliver_interval = models.TimeField()
    order_price_percent_update = models.FloatField()
    
