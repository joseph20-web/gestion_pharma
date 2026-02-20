from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('gestionnaire_stock', 'Gestionnaire de stock'),
        ('caissier', 'Caissier'),
        ('agent_facturation', 'Agent de facturation'),
        ('agent_livraison', 'Agent de livraison'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

# Create your models here

# ---------------------------------------------------------------------
# PERSONNE, FONCTION, AGENT, CLIENT
# ---------------------------------------------------------------------

class Fonction(models.Model):
    designation = models.CharField(max_length=100)
    
    def __str__(self):
        return self.designation

class Personne(models.Model):
    SEXE_CHOICES = [
        ('M', 'Masculin'),
        ('F', 'Féminin'),
    ]
    nom = models.CharField(max_length=50)
    postnom = models.CharField(max_length=50)
    prenom = models.CharField(max_length=50)
    sexe = models.CharField(max_length=1, choices=SEXE_CHOICES)
    date_naissance = models.DateField(default='2000-01-01')
    est_actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.prenom} {self.nom}"

class Agent(models.Model):
    user = models.OneToOneField('CAHMS.User', on_delete=models.CASCADE, null=True, blank=True)
    matricule = models.CharField(max_length=10, unique=True)
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    fonction = models.ForeignKey(Fonction, on_delete=models.CASCADE)
    
    def __str__(self):
        return f"{self.personne} - {self.fonction} ({self.matricule})"

class Client(models.Model):
    personne = models.ForeignKey(Personne, on_delete=models.CASCADE)
    
    def __str__(self):
        if self.personne:
            return f"{self.personne.prenom} {self.personne.nom} {self.personne.postnom}"
        return f"Client #{self.id}"

# ---------------------------------------------------------------------
# PRODUIT, FOURNISSEUR
# ---------------------------------------------------------------------

class Produit(models.Model):
    FORME_CHOICES = [
        ('comprime', 'Comprimé'),
        ('gelule', 'Gélule'),
        ('sirop', 'Sirop'),
        ('injectable', 'Injectable'),
        ('pommade', 'Pommade'),
        ('creme', 'Crème'),
        ('suppositoire', 'Suppositoire'),
        ('collyre', 'Collyre'),
        ('suspension', 'Suspension'),
        ('poudre', 'Poudre'),
        ('autre', 'Autre'),
    ]
    
    UNITE_CHOICES = [
        ('mg', 'mg'),
        ('g', 'g'),
        ('mcg', 'mcg'),
        ('mg/ml', 'mg/ml'),
        ('g/ml', 'g/ml'),
        ('mg/5ml', 'mg/5ml'),
        ('g/100ml', 'g/100ml'),
        ('%', '%'),
        ('UI/ml', 'UI/ml'),
        ('µg/ml', 'µg/ml'),
        ('mg/g', 'mg/g'),
        ('g_tube', 'g (tube)'),
        ('UI', 'UI (unités internationales)'),
    ]
    
    code_produit = models.CharField(max_length=10, unique=True, blank=True)
    nom_produit = models.CharField(max_length=100)
    prix_unitaire = models.DecimalField(max_digits=10, decimal_places=2)
    dosage = models.CharField(max_length=50)
    forme = models.CharField(max_length=50, choices=FORME_CHOICES)
    unite = models.CharField(max_length=20, choices=UNITE_CHOICES)
    date_expiration = models.DateField()
    quantite_stock = models.PositiveIntegerField(default=0, verbose_name="Quantité en stock")
    
    def __str__(self):
        return f"{self.nom_produit} ({self.code_produit})"

    def save(self, *args, **kwargs):
        is_creating = self.pk is None
        # First save to get an ID
        super().save(*args, **kwargs)
        # Then generate a stable code based on the ID if missing
        if is_creating and not self.code_produit:
            self.code_produit = f"PROD{self.id:03d}"
            super().save(update_fields=['code_produit'])



class Commande(models.Model):
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    date_commande = models.DateField()

    def __str__(self):
        personne = self.client.personne
        nom_client = f"{personne.nom} {personne.postnom} {personne.prenom}" if personne else "Client inconnu"
        return f"Commande #{self.id} - {nom_client} - {self.date_commande.strftime('%d/%m/%Y')}"

class Contenir(models.Model):
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('commande', 'produit')


class Fournisseur(models.Model):
    designation = models.CharField(max_length=100)
    
    def __str__(self):
        return self.designation
# ---------------------------------------------------------------------
# AUTRES MODELES (Perte, Approvisionnement, etc.)
# ---------------------------------------------------------------------

class TypePerte(models.Model):
    designation = models.CharField(max_length=100)
    
    def __str__(self):
        return self.designation

class Perte(models.Model):
    quantite_perdue = models.IntegerField()
    date_perte = models.DateField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    type_perte = models.ForeignKey(TypePerte, on_delete=models.CASCADE)

class Encaisse(models.Model):
    perte = models.ForeignKey(Perte, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

class Paiement(models.Model):
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    commande = models.ForeignKey(Commande, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    date_paiement = models.DateField()

class DemandeFond(models.Model):
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    motif = models.TextField()
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    date_demande = models.DateField()
    fournisseur = models.ForeignKey(Fournisseur, on_delete=models.CASCADE)
    numero_demande = models.CharField(max_length=10, unique=True, blank=True)

    def save(self, *args, **kwargs):
        is_creating = self.pk is None
        # First save to obtain ID
        super().save(*args, **kwargs)
        if is_creating and not self.numero_demande:
            self.numero_demande = f"DF{self.id:03d}"
            super().save(update_fields=['numero_demande'])

    @property
    def montant_total(self):
        return self.montant

class Designer(models.Model):
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    demande_fond = models.ForeignKey(DemandeFond, on_delete=models.CASCADE)
    quantite = models.IntegerField(default=1)

    @property
    def get_total(self):
        return self.produit.prix_unitaire * self.quantite

    class Meta:
        unique_together = ('produit', 'demande_fond')

class SortieFond(models.Model):
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    motif = models.TextField()
    demande = models.ForeignKey(DemandeFond, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    date_sortie = models.DateField()
    
    def __str__(self):
        return f"SF{self.id:03d} - {self.montant} FC - {self.demande.fournisseur.designation} - {self.date_sortie.strftime('%d/%m/%Y')}"

class Approvisionnement(models.Model):
    observation = models.TextField()
    sortie_fond = models.ForeignKey(SortieFond, on_delete=models.CASCADE)
    agent = models.ForeignKey(Agent, on_delete=models.CASCADE)
    date_approvisionnement = models.DateField()

class Approvisionner(models.Model):
    approvisionnement = models.ForeignKey(Approvisionnement, on_delete=models.CASCADE)
    produit = models.ForeignKey(Produit, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('approvisionnement', 'produit') 