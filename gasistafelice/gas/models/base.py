from django.db import models
from django.utils.translation import ugettext, ugettext_lazy as _

from permissions.models import Role
from workflows.models import Workflow
from history.models import HistoricalRecords

from gasistafelice.base.models import PermissionResource, Person, Place
from gasistafelice.base.const import DAY_CHOICES

from gasistafelice.auth import GAS_REFERRER_SUPPLIER, GAS_REFERRER_TECH, GAS_REFERRER_CASH, GAS_MEMBER
from gasistafelice.auth.utils import register_parametric_role 
from gasistafelice.auth.models import ParamRole, PrincipalParamRoleRelation

from gasistafelice.supplier.models import Supplier, Product, SupplierStock

from gasistafelice.gas import managers

from gasistafelice.bank.models import Account

from gasistafelice.base.fields import CurrencyField
from decimal import Decimal
import datetime

class GAS(models.Model, PermissionResource):

    """A group of people which make some purchases together.

    Every GAS member has a Role where the basic Role is just to be a member of the GAS.
    """

    name = models.CharField(max_length=128)
    id_in_des = models.CharField(_("GAS code"), max_length=8, null=False, blank=False, unique=True, help_text=_("GAS unique identifier in the DES. Example: CAMERINO--> CAM"))	
    logo = models.ImageField(upload_to="/images/", null=True, blank=True)
    headquarter = models.ForeignKey(Place, related_name="gas_headquarter_set", help_text=_("main address"))
    description = models.TextField(blank=True, help_text=_("Who are you? What are yours specialties?"))
    membership_fee = CurrencyField(default=Decimal("0"), help_text=_("Membership fee for partecipating in this GAS"), blank=True)

    suppliers = models.ManyToManyField(Supplier, through='GASSupplierSolidalPact', null=True, blank=True, help_text=_("Suppliers bound to the GAS through a solidal pact"))

    #, editable=False: admin validation refers to field 'account_state' that is missing from the form
    account = models.ForeignKey(Account, null=True, blank=True, related_name="gas_set", help_text=_("GAS manage all bank account for GASMember and PDS."))
    #TODO: change name
    liquidity = models.ForeignKey(Account, null=True, blank=True, related_name="gas_set2", help_text=_("GAS have is own bank account. "))

    #active = models.BooleanField()
    birthday = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text=_("Born"))
    vat = models.CharField(max_length=11, blank=True, help_text=_("VAT number"))	
    fcc = models.CharField(max_length=16, blank=True, help_text=_("Fiscal code card"))	

    email_gas = models.EmailField(null=True, blank=True)

    #COMMENT fero: imho email_referrer should be a property
    #that retrieve email contact from GAS_REFERRER (role just added). GAS REFERRER usually is GAS President
    #COMMENT domthu: The president 
    email_referrer = models.EmailField(null=True, blank=True, help_text=_("Email president"))
    phone = models.CharField(max_length=50, blank=True)	
    website = models.URLField(verify_exists=True, null=True, blank=True) 

    association_act = models.FileField(upload_to='gas/docs', null=True, blank=True)
    intent_act = models.FileField(upload_to='gas/docs', null=True, blank=True)

    note = models.TextField(blank=True)

    #COMMENT fero: photogallery and attachments does not go here
    #they should be managed elsewhere in Wordpress (now, at least)

#    #-- Config --#
#    #config = models.OneToOneField(GASConfig, null=True)

    #-- Managers --#

    objects = managers.GASRolesManager()
#    history = HistoricalRecords()

    #-- Meta --#
    class Meta:
        verbose_name_plural = _('GAS')
        app_label = 'gas'

    #-- Overriding built-in methods --#
    def __unicode__(self):
        return self.name

    #-- Properties --#
    @property        
    def local_grants(self):
        rv = (
              # permission specs go here
              )     
        return rv  

    @property
    def city(self):
        return self.headquarter.city 

    @property
    def economic_state(self):
        return u"%s - %s" % (self.account, self.liquidity)
    
    #-- Methods --#

    def setup_roles(self):
        # register a new `GAS_MEMBER` Role for this GAS
        register_parametric_role(name=GAS_MEMBER, gas=self)
        # register a new `GAS_REFERRER_TECH` Role for this GAS
        register_parametric_role(name=GAS_REFERRER_TECH, gas=self)
        # register a new `GAS_REFERRER_CASH` Role for this GAS
        register_parametric_role(name=GAS_REFERRER_CASH, gas=self)
        rv = (
              # initial roles setup goes here
              )     
        return rv  

    def save(self, *args, **kw):
        self.id_in_des = self.id_in_des.upper()
        if self.pk == None:
            self.account = Account.objects.create(balance=0)
            self.liquidity = Account.objects.create(balance=0)
        super(GAS, self).save(*args, **kw)

class GASConfig(GAS):
#class GASConfig(models.Model):
    """
    Encapsulate here gas settings and configuration facilities
    """

    # Link to parent class 
    #COMMENT: multi-table inheritance models does not required attribute with OneToOneField. It will be created automaticaly
    gas = models.OneToOneField(GAS, parent_link=True, primary_key=True, related_name="config")
    #gas = models.OneToOneField(GAS, parent_link=True, related_name="config")

    default_workflow_gasmember_order = models.ForeignKey(Workflow, editable=False, 
        related_name="gasmember_order_set", null=True, blank=True
    )
    default_workflow_gassupplier_order = models.ForeignKey(Workflow, editable=False, 
        related_name="gassupplier_order_set", null=True, blank=True
    )

    can_change_price = models.BooleanField(default=False,
        help_text=_("GAS can change supplier products price (i.e. to hold some funds for the GAS itself)")
    )

    show_order_by_supplier = models.BooleanField(default=True, 
        help_text=_("GAS views open orders by supplier. If disabled, views open order by delivery appointment")
    )  

    #TODO: see ticket #65
    default_close_day = models.CharField(max_length=16, blank=True, choices=DAY_CHOICES, 
        help_text=_("default closing order day of the week")
    )  
    #COMMENT 'default_close_time'  auto_now=True is specified for this field. That makes it a non-editable field
    default_close_time = models.TimeField(blank=True, null=True,
        help_text=_("default order closing hour and minutes")
    )
  
    #TODO: see ticket #65
    default_delivery_day = models.CharField(max_length=16, blank=True, choices=DAY_CHOICES, 
        help_text=_("default delivery day of the week")
    )  

    #auto_now=True: admin validation refers to field 'account_state' that is missing from the form
    default_delivery_time = models.TimeField(blank=True, null=True,
        help_text=_("default delivery closing hour and minutes")
    )  

    use_single_delivery = models.BooleanField(default=True, 
        help_text=_("GAS uses only one delivery place")
    )

    use_headquarter_as_withdrawal = models.BooleanField(default=True)
    default_delivery_place = models.ForeignKey(Place, blank=True, related_name='gas_default_delivery_set')
    default_withdrawal_place = models.ForeignKey(Place, blank=True, related_name='gas_default_withdrawal_set')
    is_active = models.BooleanField(default=True)
    use_scheduler = models.BooleanField(default=False)  

    #history = HistoricalRecords()

    #-- Meta --#
    class Meta:
        verbose_name = _('GAS with configuration')
        verbose_name_plural = _('GAS with configuration')
        app_label = 'gas'

    def __unicode__(self):
        return _('Configuration for GAS "%s"') % self.gas 

    def save(self, *args, **kw):
        if self.default_close_time is None:
            self.default_close_time = datetime.datetime.now()
        if self.default_delivery_time is None:
            self.default_delivery_time = datetime.datetime.now()
        #if self.default_delivery_place is None:
        #    self.default_delivery_place =  '' #self.gas.headquarter;
        #if self.default_withdrawal_place is None:
        #    self.default_withdrawal_place = '' #self.gas.headquarter;
        return super(GASConfig, self).save(*args, **kw)

class GASMember(models.Model, PermissionResource):
    """A bind of a Person into a GAS.
    Each GAS member specifies which Roles he is available for.
    This way, every time there is a need to assign one or more GAS Members to a given Role,
    there is already a group of people to choose from. 
    
    """

    person = models.ForeignKey(Person)
    gas = models.ForeignKey(GAS)
    id_in_gas = models.CharField(_("Card number"), max_length=10, blank=True, help_text=_("GAS card number"))	
    available_for_roles = models.ManyToManyField(Role, null=True, blank=True, related_name="gas_member_available_set")
    roles = models.ManyToManyField(ParamRole, null=True, blank=True, related_name="gas_member_set")
    account = models.ForeignKey(Account, null=True, blank=True)
    membership_fee_payed = models.DateField(auto_now=False, auto_now_add=False, null=True, blank=True, help_text=_("When was the last the annual quote payment"))

    history = HistoricalRecords()

    class Meta:
        app_label = 'gas'
        unique_together = (('gas', 'id_in_gas'), )

    def __unicode__(self):
        return _('%(person)s in GAS "%(gas)s"') % {'person' : self.person, 'gas': self.gas}
    
    @property
    def verbose_name(self):
        """Return GASMember representation along with his own card number in GAS"""
        #See ticket #54
        return _("%(id_in_gas)s - %(gas_member)s") % {'gas_member' : self, 'id_in_gas': self.id_in_gas}

    #COMMENT domthu: fero added id_in_des (or id_in_gas ) for GASMember. That it not required: ask to community if necesary.
    @property
    def id_in_des(self):
        """TODO: Return unique GAS member "card number" in the DES.
        This must be referred to a Person, not to a GAS membership.
        Think about its use cases.."""
        # TODO:
        # return self.person.id_in_des
        # or
        # return something
        raise NotImplementedError

    #COMMENT domthu: fero added id_in_retina for GASMember. That it not required: ask to community if necesary.
    @property
    def id_in_retina(self):
        #TODO: Should we provide also and id for retina?
        #TODO: is it dependent by person or by membership?
        #TODO: should we provide a "retina" parameter and make this a function
        """Some algorhythm to return unique GAS member "card number" in Retina"""
        raise NotImplementedError

    def setup_roles(self):
        # automatically add a new GASMember to the `GAS_MEMBER` Role
        user = self.person.user
        if user is None:
            return ""
        role = register_parametric_role(name=GAS_MEMBER, gas=self.gas)
        #COMMENT: issue #3 TypeError: The principal must be either a User instance or a Group instance.
        #TODO: fixtures create user foreach person
        role.add_principal(user)
    
    @property        
    def local_grants(self):
        rv = (
            # GAS tech referrers have full access to members of their own GAS 
            ('ALL', ParamRole.objects.filter(role=GAS_REFERRER_TECH, param1=self.gas)),
            # GAS members can see list and details of their fellow members
            ('LIST', ParamRole.objects.filter(role=GAS_MEMBER, param1=self.gas)),
            ('VIEW', ParamRole.objects.filter(role=GAS_MEMBER, param1=self.gas)),
              )     
        return rv  
    
    def save(self, *args, **kwargs):
        # TODO: refactor as a validator (?)
        if not self.person.user: # GAS members must have an account on the system
            raise AttributeError('GAS Members must be registered users')     
        super(GASMember, self).save(*args, **kwargs)
       
    def save(self, *args, **kw):
        if self.membership_fee_payed is None:
            self.membership_fee_payed = datetime.date.today()
        super(GASMember, self).save(*args, **kw)

class GASSupplierStock(models.Model, PermissionResource):
    """A Product as available to a given GAS (including price, order constraints and availability information)."""

    pact = models.ForeignKey("GASSupplierSolidalPact")
    supplier_stock = models.ForeignKey(SupplierStock)
    # if a Product is available to GAS Members; policy is GAS-specific
    enabled = models.BooleanField()    
    ## constraints on what a single GAS Member is able to order
    # minimun amount of Product units a GAS Member is able to order 
    order_minimum_amount = models.PositiveIntegerField(null=True, blank=True)
    # increment step (in Product units) for amounts exceeding minimum; 
    # useful when a Product ships in packages containing multiple units. 
    order_step = models.PositiveSmallIntegerField(null=True, blank=True)
    
    history = HistoricalRecords()

    def __unicode__(self):
        return unicode(self.supplier_stock)
        
    @property
    def supplier(self):
        return self.supplier_stock.supplier

    @property
    def price(self):
        # Product base price as updated by agreements contained in GASSupplierSolidalPact
        price_percent_update = GASSupplierSolidalPact.objects.get(gas=self.gas, supplier=self.supplier).order_price_percent_update
        return self.supplier_stock.price*(1 + price_percent_update)
    
    @property        
    def local_grants(self):
        rv = (
              # permission specs go here
              )     
        return rv
    
    class Meta:
        app_label = 'gas'
        verbose_name = _("GAS supplier stock")
        verbose_name_plural = _("GAS supplier stocks")


class GASSupplierSolidalPact(models.Model, PermissionResource):
    """Define a GAS <-> Supplier relationship agreement.

    Each Supplier comes into relationship with a GAS by signing this pact,
    where are factorized behaviour agreements between these two entities.
    This pact acts as a configurator for order and delivery management with respect to the given Supplier.

    >>> from gasistafelice.gas.models.base import *
    >>> from gasistafelice.supplier.models import *
    >>> g1 = GAS.objects.all()[0]
    >>> gname = g1.name
    >>> s1 = Supplier.objects.all()[0]
    >>> sname = s1.name

    #If running fixtures we can do
    >>> gname
    u'Gas1'
    >>> gname
    u'Gas1sdfasgasga'
    >>> sname
    u'NameSupplier1'

    >>> pds = GASSupplierSolidalPact()
    >>> pds.save()
    Traceback (most recent call last):
        ...
        if not isinstance(self.gas, GAS):
        ...
        raise self.field.rel.to.DoesNotExist
    DoesNotExist
    >>> pds = GASSupplierSolidalPact(gas=g1)
    >>> pds.save()
    Traceback (most recent call last):
        ...
        if not isinstance(self.supplier, Supplier):
        ...
        raise self.field.rel.to.DoesNotExist
    DoesNotExist
    >>> pds.supplier
    Traceback (most recent call last):
    ...
        raise self.field.rel.to.DoesNotExist
    DoesNotExist
    >>> pds.supplier = s1
    >>> pds.save()
    Traceback (most recent call last):
      File "<console>", line 1, in <module>
        ...
        super(GASMember, self).save(*args, **kw)
    TypeError: super(type, obj): obj must be an instance or subtype of type
    #TODO: resolve GASMember

    #TODO: import GASSupplierStock in the GAS models see ticket#79

    """

    gas = models.ForeignKey(GAS)
    supplier = models.ForeignKey(Supplier)
    date_signed = models.DateField(blank=True, null=True, default=None)

    # which Products GAS members can order from Supplier
    # COMMENT fero: I think the solution proposed by domthu in ticket #80 respect
    # the semantic of the through parameter for a ManyToManyField relation:
    # GASSupplierStock is just a way to augment relation between a pact and a supplier stock
    supplier_stock = models.ManyToManyField(SupplierStock, through=GASSupplierStock, null=True, blank=True)
    order_minimum_amount = CurrencyField(null=True, blank=True)
    order_delivery_cost = CurrencyField(null=True, blank=True)
    #time needed for the delivery since the GAS issued the order disposition
    order_deliver_interval = models.TimeField(null=True, blank=True)  
    # how much (in percentage) base prices from the Supplier are modified for the GAS  
    order_price_percent_update = models.FloatField(null=True, blank=True)
    
    #domthu: if GAS's configuration use only one 
    #TODO: see ticket #65
    default_withdrawal_day = models.CharField(max_length=16, choices=DAY_CHOICES, blank=True,
        help_text=_("Withdrawal week day agreement")
    )
    default_withdrawal_time = models.TimeField(null= True, blank=True, \
        help_text=_("withdrawal time agreement")
    )    

    default_withdrawal_place = models.ForeignKey(Place, related_name="pact_default_withdrawal_place_set", null=True, blank=True)

    account = models.ForeignKey(Account, null=True, blank=True)

    history = HistoricalRecords()
    
    @property
    def supplier_referrers(self):
        '''Retrieve all the GAS supplier referrers associated with this solidal pact'''
        # TODO: write unit tests for this method
        # retrieve the right parametric role
        # TODO: REFACTORING NEEDED
        # NOTE: parametric_role = ParamRole.objects.get(role__name=GAS_REFERRER_SUPPLIER, gas=self.gas, supplier=self.supplier)
        prs = ParamRole.objects.filter(role__name=GAS_REFERRER_SUPPLIER)
        for pr in prs:
            if pr.gas == self.gas and pr.supplier == self.supplier:
                parametric_role = pr
                break

        referrer_as_users = User.objects.filter(principal_param_role_relation=parametric_role)
        referrers_as_members = self.gas.gas_member_set.filter(person__user_in=referrer_as_users)
        
        return referrers_as_members 

    def setup_roles(self):
        # register a new `GAS_REFERRER_SUPPLIER` Role for this GAS/Supplier pair
        register_parametric_role(name=GAS_REFERRER_SUPPLIER, gas=self.gas, supplier=self.supplier)     
    
    @property        
    def local_grants(self):
        rv = (
              # permission specs go here
              )     
        return rv

    class Meta:
        app_label = 'gas'
     
    def elabore_report(self):
        #TODO return report like pdf format. Report has to be signed-firmed by partners
        return "" 

    history = HistoricalRecords()

    #def set_default_product_set(self):
    def save(self, *args, **kw):
        if not isinstance(self.gas, GAS):
            raise AttributeError("PDS gas cannot be null")
        if not isinstance(self.supplier, Supplier):
            raise AttributeError("PDS supplier cannot be null")
        #TODO 
        #if self.pk == None:
        #    products = SupplierStock.objects.filter(supplier=self.supplier)
        #    for p in products:
        #        GASSupplierStock.objects.create(gas=self.gas, supplier_stock=p)
        super(GASMember, self).save(*args, **kw)
