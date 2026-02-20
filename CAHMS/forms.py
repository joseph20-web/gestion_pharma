from django import forms
from .models import (
    User, Personne, Fonction, Agent, Client, Produit, Fournisseur,
    Commande, TypePerte, Perte, Paiement, SortieFond,
    Approvisionnement, Approvisionner, Designer, DemandeFond
)
from django.contrib.auth.forms import UserCreationForm

class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'role', 'first_name', 'last_name', 'password']

    def save(self, commit=True):
        user: User = super().save(commit=False)
        raw_password = self.cleaned_data.get('password')
        if raw_password:
            user.set_password(raw_password)
        if commit:
            user.save()
        return user

class PersonneForm(forms.ModelForm):
    class Meta:
        model = Personne
        fields = ['nom', 'postnom', 'prenom', 'sexe', 'date_naissance']

class FonctionForm(forms.ModelForm):
    class Meta:
        model = Fonction
        fields = ['designation']

class AgentForm(forms.ModelForm):
    class Meta:
        model = Agent
        fields = ['user', 'matricule', 'personne', 'fonction']

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['personne']

class ProduitForm(forms.ModelForm):
    class Meta:
        model = Produit
        fields = ['nom_produit', 'prix_unitaire', 'dosage', 'forme', 'unite', 'date_expiration']

class FournisseurForm(forms.ModelForm):
    class Meta:
        model = Fournisseur
        fields = ['designation']

class CommandeForm(forms.ModelForm):
    prix_total = forms.DecimalField(
        widget=forms.HiddenInput(),
        required=False,
        initial=0
    )
    
    class Meta:
        model = Commande
        fields = ['client', 'date_commande', 'prix_total']
        widgets = {
            'date_commande': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class TypePerteForm(forms.ModelForm):
    class Meta:
        model = TypePerte
        fields = ['designation']

class PerteForm(forms.ModelForm):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        label='Produit',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = Perte
        fields = ['quantite_perdue', 'date_perte', 'type_perte']

class PaiementForm(forms.ModelForm):
    class Meta:
        model = Paiement
        fields = ['montant', 'commande', 'date_paiement']
        widgets = {
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': 'readonly',
                'placeholder': 'Montant automatique'
            }),
            'commande': forms.Select(attrs={
                'class': 'form-select',
                'required': True
            }),
            'date_paiement': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'required': True
            })
        }
        labels = {
            'montant': 'Montant Total',
            'commande': 'Commande',
            'date_paiement': 'Date de Paiement'
        }

class DemandeFondForm(forms.ModelForm):
    # Ajouter des labels personnalisés
    date_demande = forms.DateField(
        label="Date de demande",
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    class Meta:
        model = DemandeFond
        fields = ['montant', 'motif', 'date_demande', 'fournisseur']
        widgets = {
            'montant': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'readonly': 'readonly',
                'placeholder': 'Calculé automatiquement'
            }),
            'motif': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Détails de la demande...'
            }),
            'fournisseur': forms.Select(attrs={'class': 'form-select'}),
        }
    
    # Validation supplémentaire
    def clean_montant(self):
        montant = self.cleaned_data.get('montant')
        if montant and montant <= 0:
            raise forms.ValidationError("Le montant doit être positif")
        return montant

class DesignerForm(forms.ModelForm):
    # Rendre le champ produit obligatoire avec affichage personnalisé
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select select-produit'}),
        required=True,
        empty_label="Sélectionnez un produit"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser l'affichage des produits
        self.fields['produit'].label_from_instance = self._produit_label
    
    def _produit_label(self, obj):
        """Affiche le nom, dosage et forme du produit"""
        return f"{obj.nom_produit} - {obj.dosage} {obj.unite} ({obj.get_forme_display()})"
    
    class Meta:
        model = Designer
        fields = ['produit', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={
                'class': 'form-control quantite-input',
                'min': 1,
                'value': 1  # Valeur par défaut
            }),
        }
        labels = {
            'produit': "Produit",
            'quantite': "Quantité"
        }

class SortieFondForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['demande'].label_from_instance = lambda obj: f"DF{obj.id:03d} - {obj.fournisseur.designation} - {obj.montant} FC - {obj.date_demande.strftime('%d/%m/%Y')}"
    class Meta:
        model = SortieFond
        fields = ['montant', 'motif', 'demande', 'date_sortie']

class ApprovisionnementForm(forms.ModelForm):
    sortie_fond = forms.ModelChoiceField(
        queryset=SortieFond.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Sortie de fonds',
        empty_label="Sélectionnez une sortie de fonds"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser l'affichage des sorties de fonds
        self.fields['sortie_fond'].label_from_instance = lambda obj: f"SF{obj.id:03d} - {obj.montant} FC - {obj.demande.fournisseur.designation} - {obj.date_sortie.strftime('%d/%m/%Y')}"
    
    class Meta:
        model = Approvisionnement
        fields = ['observation', 'sortie_fond', 'date_approvisionnement']
        widgets = {
            'observation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Notes sur l\'approvisionnement...'}),
            'date_approvisionnement': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class ClientPersonneForm(forms.ModelForm):
    nom = forms.CharField(label='Nom', max_length=50)
    postnom = forms.CharField(label='Post-nom', max_length=50)
    prenom = forms.CharField(label='Prénom', max_length=50)
    sexe = forms.ChoiceField(label='Sexe', choices=Personne.SEXE_CHOICES)
    date_naissance = forms.DateField(label='Date de naissance', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Client
        fields = []  # On ne gère pas le champ personne directement ici

    def save(self, commit=True):
        data = self.cleaned_data
        personne = Personne.objects.create(
            nom=data['nom'],
            postnom=data['postnom'],
            prenom=data['prenom'],
            sexe=data['sexe'],
            date_naissance=data['date_naissance']
        )
        client = Client(personne=personne)
        if commit:
            personne.save()
            client.save()
        return client

class ApprovisionnerForm(forms.ModelForm):
    produit = forms.ModelChoiceField(
        queryset=Produit.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True,
        empty_label="Sélectionnez un produit"
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['produit'].label_from_instance = lambda obj: f"{obj.nom_produit} - {obj.dosage} {obj.unite} ({obj.get_forme_display()})"

    class Meta:
        model = Approvisionner
        fields = ['produit', 'quantite']
        widgets = {
            'quantite': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'value': 1}),
        }
        labels = {
            'produit': 'Produit',
            'quantite': 'Quantité',
        }

class GestionnaireAgentFullForm(forms.Form):
    username = forms.CharField(label='Nom utilisateur', max_length=150)
    email = forms.EmailField(label='Email', required=False)
    password = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    role = forms.ChoiceField(label='Rôle', choices=User.ROLE_CHOICES)
    first_name = forms.CharField(label='Prénom', max_length=150)
    last_name = forms.CharField(label='Nom', max_length=150)

    matricule = forms.CharField(label='Matricule', max_length=10)
    fonction = forms.ModelChoiceField(label='Fonction', queryset=Fonction.objects.all())

    nom = forms.CharField(label='Nom', max_length=50)
    postnom = forms.CharField(label='Post-nom', max_length=50)
    prenom = forms.CharField(label='Prénom', max_length=50)
    sexe = forms.ChoiceField(label='Sexe', choices=[('M', 'Masculin'), ('F', 'Féminin')])
    date_naissance = forms.DateField(label='Date de naissance', widget=forms.DateInput(attrs={'type': 'date'}))

    def save(self):
        # Création de la personne
        personne = Personne.objects.create(
            nom=self.cleaned_data['nom'],
            postnom=self.cleaned_data['postnom'],
            prenom=self.cleaned_data['prenom'],
            sexe=self.cleaned_data['sexe'],
            date_naissance=self.cleaned_data['date_naissance']
        )
        # Création de l'utilisateur
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password'],
            role=self.cleaned_data['role'],
            first_name=self.cleaned_data['first_name'],
            last_name=self.cleaned_data['last_name']
        )
        # Création de l'agent
        agent = Agent.objects.create(
            user=user,
            matricule=self.cleaned_data['matricule'],
            personne=personne,
            fonction=self.cleaned_data['fonction']
        )
        return agent


