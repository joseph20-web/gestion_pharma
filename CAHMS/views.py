from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Fournisseur, Produit, Perte, Approvisionnement, DemandeFond, Approvisionner, TypePerte, Agent, Encaisse, Designer, Paiement, Commande
from .forms import FournisseurForm, ProduitForm, PerteForm, ApprovisionnementForm, DemandeFondForm, DesignerForm, PaiementForm
from django.forms import inlineformset_factory
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import CommandeForm
from .models import Contenir
from .models import Client
from .forms import ClientPersonneForm
from django.contrib import messages
from .forms import SortieFondForm
from .models import SortieFond
from .forms import ApprovisionnerForm
from django.contrib.auth import authenticate, login as auth_login
from django.http import HttpResponse
from .forms import AgentForm, GestionnaireAgentFullForm



def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)
            agent = Agent.objects.filter(user=user).first()
            if agent and agent.fonction and agent.fonction.designation:
                designation = agent.fonction.designation.lower()
                if 'gestionnaire' in designation:
                    return redirect('dashboard')
                elif 'caisse' in designation or 'caissier' in designation:
                    return redirect('caisse_dashboard')
                elif 'facturation' in designation or 'facture' in designation:
                    return redirect('agent_facture_dashboard')
                elif 'livraison' in designation or 'livreur' in designation:
                    return redirect('agent_livraison_dashboard')
                else:
                    return redirect('login')
            else:
                return redirect('login')
        else:
            return render(request, 'login/login.html', {'error': "Nom d'utilisateur ou mot de passe incorrect."})
    return render(request, 'login/login.html')

# --- FOURNISSEUR ---
@login_required
def fournisseur_list(request):
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'gestionaire/fournisseur/list.html', {'fournisseurs': fournisseurs})

@login_required
def fournisseur_create(request):
    if request.method == 'POST':
        form = FournisseurForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm()
    return render(request, 'gestionaire/fournisseur/form.html', {'form': form, 'title': 'Nouveau Fournisseur'})

@login_required
def fournisseur_update(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        form = FournisseurForm(request.POST, instance=fournisseur)
        if form.is_valid():
            form.save()
            return redirect('fournisseur_list')
    else:
        form = FournisseurForm(instance=fournisseur)
    return render(request, 'gestionaire/fournisseur/form.html', {'form': form, 'title': 'Modifier Fournisseur'})

@login_required
def fournisseur_delete(request, pk):
    fournisseur = get_object_or_404(Fournisseur, pk=pk)
    if request.method == 'POST':
        fournisseur.delete()
        return redirect('fournisseur_list')
    return render(request, 'gestionaire/fournisseur/delete.html', {'fournisseur': fournisseur})

# --- PRODUIT ---
@login_required
def produit_list(request):
    produits = Produit.objects.all()
    return render(request, 'gestionaire/produit/list.html', {'produits': produits})

@login_required
def produit_create(request):
    if request.method == 'POST':
        form = ProduitForm(request.POST)
        if form.is_valid():
            # Validation de la date d'expiration
            date_expiration = form.cleaned_data.get('date_expiration')
            if date_expiration and date_expiration <= timezone.now().date():
                form.add_error('date_expiration', 'La date d\'expiration doit être strictement supérieure à la date actuelle.')
            else:
                form.save()
                return redirect('produit_list')
    else:
        form = ProduitForm()
    return render(request, 'gestionaire/produit/form.html', {'form': form, 'title': 'Nouveau Produit'})

@login_required
def produit_update(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        form = ProduitForm(request.POST, instance=produit)
        if form.is_valid():
            # Validation de la date d'expiration
            date_expiration = form.cleaned_data.get('date_expiration')
            if date_expiration and date_expiration <= timezone.now().date():
                form.add_error('date_expiration', 'La date d\'expiration doit être strictement supérieure à la date actuelle.')
            else:
                form.save()
                return redirect('produit_list')
    else:
        form = ProduitForm(instance=produit)
    return render(request, 'gestionaire/produit/form.html', {'form': form, 'title': 'Modifier Produit'})

@login_required
def produit_delete(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    if request.method == 'POST':
        produit.delete()
        return redirect('produit_list')
    return render(request, 'gestionaire/produit/delete.html', {'produit': produit})

@login_required
def produit_print(request, pk):
    produit = get_object_or_404(Produit, pk=pk)
    return render(request, 'gestionaire/produit/print.html', {
        'produit': produit,
        'user': request.user
    })

# --- PERTE ---
@login_required
def perte_list(request):
    pertes = Perte.objects.select_related('agent__personne', 'type_perte').prefetch_related('encaisse_set__produit')
    return render(request, 'gestionaire/perte/list.html', {'pertes': pertes})

@login_required
def perte_create(request):
    if request.method == 'POST':
        form = PerteForm(request.POST)
        if form.is_valid():
            # Vérifier le stock avant de créer la perte
            produit = form.cleaned_data['produit']
            quantite_perte = form.cleaned_data['quantite_perdue']
            stock_disponible = produit.quantite_stock
            
            # Bloquer si la quantité de perte est strictement supérieure au stock
            if quantite_perte > stock_disponible:
                messages.error(request, f"❌ PERTE REFUSÉE - Quantité de perte ({quantite_perte}) supérieure au stock disponible ({stock_disponible}) pour le produit {produit.nom_produit}.")
                return render(request, 'gestionaire/perte/form.html', {'form': form, 'title': 'Nouvelle Perte'})
            
            perte = form.save(commit=False)
            # Remplir automatiquement l'agent connecté
            if hasattr(request.user, 'agent'):
                perte.agent = request.user.agent
            perte.save()
            
            # Créer la relation Encaisse pour lier la perte au produit
            Encaisse.objects.create(perte=perte, produit=produit, quantite=quantite_perte)
            
            # Diminuer le stock du produit
            produit.quantite_stock -= quantite_perte
            produit.save()
            
            # Vérifier si le stock est épuisé après la perte
            if produit.quantite_stock == 0:
                messages.warning(request, f"⚠️ ATTENTION - Stock épuisé pour le produit {produit.nom_produit} après cette perte.")
            
            messages.success(request, f"Perte créée avec succès. Stock du produit {produit.nom_produit} mis à jour ({stock_disponible} → {produit.quantite_stock}).")
            return redirect('perte_list')
    else:
        form = PerteForm()
    return render(request, 'gestionaire/perte/form.html', {'form': form, 'title': 'Nouvelle Perte'})

@login_required
def perte_update(request, pk):
    perte = get_object_or_404(Perte, pk=pk)
    if request.method == 'POST':
        form = PerteForm(request.POST, instance=perte)
        if form.is_valid():
            # Récupérer l'ancienne quantité de perte
            ancienne_quantite = perte.quantite_perdue
            nouveau_produit = form.cleaned_data['produit']
            nouvelle_quantite = form.cleaned_data['quantite_perdue']
            
            # Récupérer l'ancien produit via la relation Encaisse
            ancien_produit = perte.encaisse_set.first().produit if perte.encaisse_set.exists() else None
            
            # Vérifier si le produit a changé
            if ancien_produit != nouveau_produit:
                # Restaurer le stock de l'ancien produit
                if ancien_produit:
                    ancien_produit.quantite_stock += ancienne_quantite
                    ancien_produit.save()
                
                # Vérifier le stock du nouveau produit
                stock_disponible = nouveau_produit.quantite_stock
                if nouvelle_quantite > stock_disponible:
                    messages.error(request, f"❌ MODIFICATION REFUSÉE - Quantité de perte ({nouvelle_quantite}) supérieure au stock disponible ({stock_disponible}) pour le produit {nouveau_produit.nom_produit}.")
                    return render(request, 'gestionaire/perte/form.html', {'form': form, 'title': 'Modifier Perte'})
                
                # Diminuer le stock du nouveau produit
                nouveau_produit.quantite_stock -= nouvelle_quantite
                nouveau_produit.save()
                
                # Vérifier si le stock est épuisé
                if nouveau_produit.quantite_stock == 0:
                    messages.warning(request, f"⚠️ ATTENTION - Stock épuisé pour le produit {nouveau_produit.nom_produit} après cette modification.")
                
            else:
                # Même produit, ajuster selon la différence
                difference = nouvelle_quantite - ancienne_quantite
                
                if difference > 0:
                    # Augmentation de la perte
                    stock_disponible = nouveau_produit.quantite_stock
                    if difference > stock_disponible:
                        messages.error(request, f"❌ MODIFICATION REFUSÉE - Augmentation de perte ({difference}) supérieure au stock disponible ({stock_disponible}) pour le produit {nouveau_produit.nom_produit}.")
                        return render(request, 'gestionaire/perte/form.html', {'form': form, 'title': 'Modifier Perte'})
                    
                    nouveau_produit.quantite_stock -= difference
                    nouveau_produit.save()
                    
                    # Vérifier si le stock est épuisé
                    if nouveau_produit.quantite_stock == 0:
                        messages.warning(request, f"⚠️ ATTENTION - Stock épuisé pour le produit {nouveau_produit.nom_produit} après cette modification.")
                
                elif difference < 0:
                    # Diminution de la perte (restaurer du stock)
                    nouveau_produit.quantite_stock += abs(difference)
                    nouveau_produit.save()
            
            perte = form.save(commit=False)
            if hasattr(request.user, 'agent'):
                perte.agent = request.user.agent
            perte.save()
            
            # Mettre à jour ou créer la relation Encaisse
            encaisse, created = Encaisse.objects.get_or_create(perte=perte, defaults={'produit': nouveau_produit, 'quantite': nouvelle_quantite})
            if not created:
                encaisse.produit = nouveau_produit
                encaisse.quantite = nouvelle_quantite
                encaisse.save()
            
            messages.success(request, f"Perte modifiée avec succès. Stock du produit {nouveau_produit.nom_produit} ajusté.")
            return redirect('perte_list')
    else:
        form = PerteForm(instance=perte)
    return render(request, 'gestionaire/perte/form.html', {'form': form, 'title': 'Modifier Perte'})

@login_required
def perte_delete(request, pk):
    perte = get_object_or_404(Perte, pk=pk)
    if request.method == 'POST':
        # Restaurer le stock du produit avant de supprimer la perte
        encaisse = perte.encaisse_set.first()
        if encaisse:
            produit = encaisse.produit
            quantite_restauree = perte.quantite_perdue
            ancien_stock = produit.quantite_stock
        else:
            # Si pas de relation Encaisse, pas de stock à restaurer
            messages.warning(request, "Perte supprimée mais aucune relation produit trouvée.")
            perte.delete()
            return redirect('perte_list')
        
        produit.quantite_stock += quantite_restauree
        produit.save()
        
        # Supprimer la perte (cela supprimera aussi la relation Encaisse via CASCADE)
        perte.delete()
        
        messages.success(request, f"Perte supprimée avec succès. Stock du produit {produit.nom_produit} restauré ({ancien_stock} → {produit.quantite_stock}).")
        return redirect('perte_list')
    return render(request, 'gestionaire/perte/delete.html', {'perte': perte})

@login_required
def perte_print(request, pk):
    perte = get_object_or_404(Perte, pk=pk)
    return render(request, 'gestionaire/perte/print.html', {
        'perte': perte,
        'user': request.user
    })

# --- APPROVISIONNEMENT ---
@login_required
def approvisionnement_list(request):
    approvisionnements = Approvisionnement.objects.all()
    return render(request, 'gestionaire/approvisionnement/list.html', {'approvisionnements': approvisionnements})

@login_required
def approvisionnement_create(request):
    ApprovisionnerFormSet = inlineformset_factory(
        Approvisionnement, Approvisionner,
        form=ApprovisionnerForm, extra=1, can_delete=True
    )
    
    if request.method == 'POST':
        form = ApprovisionnementForm(request.POST)
        formset = ApprovisionnerFormSet(request.POST)
        
        if form.is_valid() and formset.is_valid():
            appro = form.save(commit=False)
            # Remplir automatiquement l'agent connecté
            if hasattr(request.user, 'agent'):
                appro.agent = request.user.agent
            appro.save()
            formset.instance = appro
            formset.save()
            
            # Mettre à jour le stock des produits approvisionnés
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    produit = form.cleaned_data['produit']
                    quantite = form.cleaned_data['quantite']
                    # Ajouter la quantité au stock existant
                    produit.quantite_stock += quantite
                    produit.save()
            
            messages.success(request, "Approvisionnement créé avec succès et stock mis à jour.")
            return redirect('approvisionnement_list')
    else:
        form = ApprovisionnementForm()
        formset = ApprovisionnerFormSet()

    return render(request, 'gestionaire/approvisionnement/form.html', {
        'form': form,
        'formset': formset,
        'title': 'Nouvel Approvisionnement'
    })

@login_required
def approvisionnement_update(request, pk):
    appro = get_object_or_404(Approvisionnement, pk=pk)
    ApprovisionnerFormSet = inlineformset_factory(
        Approvisionnement, Approvisionner, form=ApprovisionnerForm, extra=0, can_delete=True
    )
    
    if request.method == 'POST':
        form = ApprovisionnementForm(request.POST, instance=appro)
        formset = ApprovisionnerFormSet(request.POST, instance=appro)
        if form.is_valid() and formset.is_valid():
            # Sauvegarder les anciennes quantités pour les soustraire du stock
            anciennes_quantites = {}
            for approvisionner in appro.approvisionner_set.all():
                anciennes_quantites[approvisionner.produit.id] = approvisionner.quantite
                # Soustraire l'ancienne quantité du stock
                produit = approvisionner.produit
                produit.quantite_stock -= approvisionner.quantite
                produit.save()
            
            appro = form.save(commit=False)
            if hasattr(request.user, 'agent'):
                appro.agent = request.user.agent
            appro.save()
            formset.save()
            
            # Ajouter les nouvelles quantités au stock
            for form in formset:
                if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                    produit = form.cleaned_data['produit']
                    quantite = form.cleaned_data['quantite']
                    produit.quantite_stock += quantite
                    produit.save()
            
            messages.success(request, "Approvisionnement modifié avec succès et stock mis à jour.")
            return redirect('approvisionnement_list')
    else:
        form = ApprovisionnementForm(instance=appro)
        formset = ApprovisionnerFormSet(instance=appro)
    return render(request, 'gestionaire/approvisionnement/form.html', {'form': form, 'formset': formset, 'title': 'Modifier Approvisionnement'})

@login_required
def approvisionnement_delete(request, pk):
    appro = get_object_or_404(Approvisionnement, pk=pk)
    if request.method == 'POST':
        appro.delete()
        return redirect('approvisionnement_list')
    return render(request, 'gestionaire/approvisionnement/delete.html', {'approvisionnement': appro})

@login_required
def approvisionnement_print(request, pk):
    approvisionnement = get_object_or_404(Approvisionnement, pk=pk)
    approvisionnements = Approvisionner.objects.filter(approvisionnement=approvisionnement)
    return render(request, 'gestionaire/approvisionnement/print.html', {
        'approvisionnement': approvisionnement, 
        'approvisionnements': approvisionnements, 
        'date_du_jour': timezone.now(),
        'user': request.user
    })

# --- DEMANDE DE FONDS ---
@login_required
def demande_fond_list(request):
    demandes = DemandeFond.objects.all()
    return render(request, 'gestionaire/commande_fournisseur/list.html', {'demandes': demandes})



@login_required
def demande_fond_create(request):
    produits = Produit.objects.all()
    
    # Création du formset pour les produits
    ProduitFormSet = inlineformset_factory(
        DemandeFond,
        Designer,
        form=DesignerForm,
        extra=1,
        can_delete=True
    )

    if request.method == 'POST':
        form = DemandeFondForm(request.POST)
        formset = ProduitFormSet(request.POST, prefix='produits')
        
        if form.is_valid() and formset.is_valid():
            demande = form.save(commit=False)
            
            # Remplir automatiquement l'agent connecté
            if hasattr(request.user, 'agent'):
                demande.agent = request.user.agent
            else:
                # Si l'utilisateur n'a pas d'agent, afficher une erreur claire
                messages.error(request, "Votre utilisateur n'est pas lié à un agent. Veuillez contacter l'administrateur.")
                return render(request, 'gestionaire/commande_fournisseur/form.html', {
                    'form': form,
                    'formset': formset,
                    'produits': produits,
                    'title': 'Nouvelle Demande de Fonds'
                })
            
            # Calculer le montant total à partir des produits
            total = 0
            for prod_form in formset:
                if prod_form.cleaned_data and not prod_form.cleaned_data.get('DELETE', False):
                    produit_id = prod_form.cleaned_data['produit'].id
                    quantite = prod_form.cleaned_data['quantite']
                    produit = Produit.objects.get(id=produit_id)
                    total += produit.prix_unitaire * quantite
            
            demande.montant = total
            demande.save()
            formset.instance = demande
            formset.save()
            messages.success(request, "Demande de fonds créée avec succès.")
            return redirect('demande_fond_list')
        else:
            # Erreurs de validation gérées via le template/messages
            pass
    else:
        form = DemandeFondForm()
        formset = ProduitFormSet(prefix='produits')

    return render(request, 'gestionaire/commande_fournisseur/form.html', {
        'form': form,
        'formset': formset,
        'produits': produits,
        'title': 'Nouvelle Demande de Fonds'
    })

@login_required
def demande_fond_update(request, pk):
    demande = get_object_or_404(DemandeFond, pk=pk)
    produits = Produit.objects.all()
    
    ProduitFormSet = inlineformset_factory(
        DemandeFond,
        Designer,
        form=DesignerForm,
        extra=0,
        can_delete=True
    )

    if request.method == 'POST':
        form = DemandeFondForm(request.POST, instance=demande)
        formset = ProduitFormSet(request.POST, instance=demande, prefix='produits')
        
        if form.is_valid() and formset.is_valid():
            demande = form.save(commit=False)
            
            # Remplir automatiquement l'agent connecté
            if hasattr(request.user, 'agent'):
                demande.agent = request.user.agent
            
            # Recalculer le montant total
            total = 0
            for prod_form in formset:
                if prod_form.cleaned_data and not prod_form.cleaned_data.get('DELETE', False):
                    produit_id = prod_form.cleaned_data['produit'].id
                    quantite = prod_form.cleaned_data['quantite']
                    produit = Produit.objects.get(id=produit_id)
                    total += produit.prix_unitaire * quantite
            
            demande.montant = total
            demande.save()
            formset.save()
            messages.success(request, "Demande de fonds modifiée avec succès.")
            return redirect('demande_fond_list')
        else:
            # Erreurs de validation gérées via le template/messages
            pass
    else:
        form = DemandeFondForm(instance=demande)
        formset = ProduitFormSet(instance=demande, prefix='produits')

    return render(request, 'gestionaire/commande_fournisseur/form.html', {
        'form': form,
        'formset': formset,
        'produits': produits,
        'title': 'Modifier Demande de Fonds'
    })

@login_required
def demande_fond_delete(request, pk):
    demande = get_object_or_404(DemandeFond, pk=pk)
    if request.method == 'POST':
        demande.delete()
        return redirect('demande_fond_list')
    return render(request, 'gestionaire/commande_fournisseur/delete.html', {'demande': demande})

@login_required
def demande_fond_print(request, pk):
    demande = get_object_or_404(DemandeFond, pk=pk)
    designers = Designer.objects.filter(demande_fond=demande)
    return render(request, 'gestionaire/commande_fournisseur/print.html', {
        'demande': demande,
        'designers': designers,
        'date_du_jour': timezone.now(),
        'user': request.user
    })

# --- PROFIL UTILISATEUR ---
@login_required
def profile_utilisateur(request):
    user = request.user
    agent = getattr(user, 'agent', None)
    personne = agent.personne if agent else None
    return render(request, 'gestionaire/profile.html', {
        'user': user,
        'agent': agent,
        'personne': personne,
    })

# --- CAISSE : PAIEMENTS ---
@login_required
def caisse_paiement_list(request):
    paiements = Paiement.objects.all()
    return render(request, 'caisse/paiement/list.html', {'paiements': paiements})

# --- CAISSE : DASHBOARD ---
@login_required
def caisse_dashboard(request):
    """Dashboard du caissier avec statistiques réelles"""
    from datetime import date
    
    # Récupération des statistiques
    total_commandes = Commande.objects.count()
    total_paiements = Paiement.objects.count()
    total_clients = Client.objects.count()
    total_produits = Produit.objects.count()
    
    # Statistiques du jour
    commandes_aujourd_hui = Commande.objects.filter(date_commande=date.today()).count()
    paiements_aujourd_hui = Paiement.objects.filter(date_paiement=date.today()).count()
    
    # Produits en rupture de stock
    produits_rupture = Produit.objects.filter(quantite_stock=0).count()
    produits_faible_stock = Produit.objects.filter(quantite_stock__lte=10).count()
    
    context = {
        'total_commandes': total_commandes,
        'total_paiements': total_paiements,
        'total_clients': total_clients,
        'total_produits': total_produits,
        'commandes_aujourd_hui': commandes_aujourd_hui,
        'paiements_aujourd_hui': paiements_aujourd_hui,
        'produits_rupture': produits_rupture,
        'produits_faible_stock': produits_faible_stock,
    }
    
    return render(request, 'caisse/dashboard.html', context)

# --- CAISSE : COMMANDES ---
@login_required
def caisse_commande_list(request):
    commandes = Commande.objects.select_related('client__personne', 'agent__personne').all()
    return render(request, 'caisse/commande/list.html', {'commandes': commandes})

# --- CAISSE : AGENTS ---
@login_required
def caisse_agent_list(request):
    agents = Agent.objects.select_related('personne', 'fonction').all()
    return render(request, 'caisse/agent/list.html', {'agents': agents})

# --- CAISSE : PRODUITS ---
@login_required
def caisse_produit_list(request):
    produits = Produit.objects.all()
    return render(request, 'caisse/produit/list.html', {'produits': produits})

# --- CAISSE : CLIENTS ---
@login_required
def caisse_client_list(request):
    from .models import Client
    clients = Client.objects.select_related('personne').all()
    return render(request, 'caisse/client/list.html', {'clients': clients})

# --- CAISSE : FOURNISSEURS ---
@login_required
def caisse_fournisseur_list(request):
    from .models import Fournisseur
    fournisseurs = Fournisseur.objects.all()
    return render(request, 'caisse/fournisseur/list.html', {'fournisseurs': fournisseurs})

# --- CAISSE : CREATION PAIEMENT ---
@login_required
def caisse_paiement_create(request):
    if request.method == 'POST':
        form = PaiementForm(request.POST)
        if form.is_valid():
            paiement = form.save(commit=False)
            # Remplir automatiquement l'agent connecté
            if hasattr(request.user, 'agent'):
                paiement.agent = request.user.agent
            paiement.save()
            messages.success(request, "Paiement créé avec succès.")
            return redirect('caisse_paiement_detail', paiement.id)
    else:
        form = PaiementForm()
        
        # Optimiser le queryset des commandes pour inclure les relations nécessaires
        if hasattr(form.fields['commande'], 'queryset'):
            form.fields['commande'].queryset = form.fields['commande'].queryset.select_related(
                'client__personne'
            ).order_by('-date_commande')
    
    return render(request, 'caisse/paiement/form.html', {'form': form, 'title': 'Nouveau Paiement'})

# --- CAISSE : DETAIL PAIEMENT ---
@login_required
def caisse_paiement_detail(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    return render(request, 'caisse/paiement/detail.html', {'paiement': paiement})

# --- CAISSE : MODIFICATION PAIEMENT ---
@login_required
def caisse_paiement_update(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        form = PaiementForm(request.POST, instance=paiement)
        if form.is_valid():
            paiement = form.save(commit=False)
            if hasattr(request.user, 'agent'):
                paiement.agent = request.user.agent
            paiement.save()
            messages.success(request, "Paiement modifié avec succès.")
            return redirect('caisse_paiement_detail', paiement.id)
    else:
        form = PaiementForm(instance=paiement)
        
        # Optimiser le queryset des commandes pour inclure les relations nécessaires
        if hasattr(form.fields['commande'], 'queryset'):
            form.fields['commande'].queryset = form.fields['commande'].queryset.select_related(
                'client__personne'
            ).order_by('-date_commande')
    
    return render(request, 'caisse/paiement/form.html', {'form': form, 'title': 'Modifier Paiement'})

# --- CAISSE : SUPPRESSION PAIEMENT ---
@login_required
def caisse_paiement_delete(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    if request.method == 'POST':
        paiement.delete()
        return redirect('caisse_paiement_list')
    return render(request, 'caisse/paiement/delete.html', {'paiement': paiement})

# --- CAISSE : IMPRESSION/DETAIL PAIEMENT ---
@login_required
def caisse_paiement_print(request, pk):
    paiement = get_object_or_404(Paiement, pk=pk)
    commande = paiement.commande
    
    # Optimiser les requêtes avec select_related et prefetch_related
    from .models import Contenir
    lignes_qs = Contenir.objects.filter(commande=commande).select_related(
        'produit'
    ).order_by('produit__nom_produit')
    
    # Construire les lignes avec tous les détails nécessaires
    lignes = []
    total_calcule = 0
    
    for contenir in lignes_qs:
        produit = contenir.produit
        total_ligne = produit.prix_unitaire * contenir.quantite
        total_calcule += total_ligne
        
        lignes.append({
            'produit': produit,
            'quantite': contenir.quantite,
            'prix_unitaire': produit.prix_unitaire,
            'total_ligne': total_ligne,
            'dosage': produit.dosage,
            'forme': produit.get_forme_display(),
            'unite': produit.unite
        })
    
    # Vérifier que le total calculé correspond au prix total de la commande
    if total_calcule != commande.prix_total:
        print(f"Attention: Total calculé ({total_calcule}) ≠ Prix total commande ({commande.prix_total})")
    
    from django.utils import timezone
    date_du_jour = timezone.now()
    user = request.user
    
    context = {
        'paiement': paiement,
        'commande': commande,
        'lignes': lignes,
        'date_du_jour': date_du_jour,
        'user': user,
        'total_calcule': total_calcule,
        'nb_produits': len(lignes)
    }
    
    return render(request, 'caisse/paiement/print.html', context)

# --- CAISSE : VERIFICATION FACTURE ---
@login_required
def caisse_verification_facture(request):
    paiement = None
    not_found = False
    if request.method == 'POST':
        numero = request.POST.get('numero_paiement')
        try:
            paiement = Paiement.objects.get(pk=numero)
        except Paiement.DoesNotExist:
            not_found = True
    return render(request, 'caisse/paiement/verification.html', {'paiement': paiement, 'not_found': not_found})

# --- STOCK ---
@login_required
def stock_list(request):
    produits = Produit.objects.all()
    return render(request, 'gestionaire/stock/list.html', {'produits': produits})

# --- DASHBOARD (optionnel) ---
@login_required
def gestionnaire_dashboard(request):
    from django.utils import timezone
    from datetime import date
    
    # Calculer les vraies données
    nb_produits = Produit.objects.count()
    nb_produits_en_stock = Produit.objects.filter(quantite_stock__gt=0).count()
    
    # Alertes de stock faible (produits avec moins de 10 unités)
    alertes_stock_faible = Produit.objects.filter(quantite_stock__lt=10).count()
    
    # Réceptions aujourd'hui (approvisionnements d'aujourd'hui)
    aujourd_hui = date.today()
    receptions_aujourd_hui = Approvisionnement.objects.filter(date_approvisionnement=aujourd_hui).count()
    
    # Produits qui expirent dans 10 jours
    from datetime import timedelta
    date_limite = aujourd_hui + timedelta(days=10)
    produits_expiration_proche = Produit.objects.filter(
        date_expiration__lte=date_limite,
        date_expiration__gte=aujourd_hui,
        quantite_stock__gt=0
    ).count()
    
    context = {
        'nb_produits': nb_produits,
        'nb_produits_en_stock': nb_produits_en_stock,
        'alertes_stock_faible': alertes_stock_faible,
        'produits_expiration_proche': produits_expiration_proche,
        'receptions_aujourd_hui': receptions_aujourd_hui,
    }
    
    return render(request, 'gestionaire/dashboard.html', context)

@login_required
def caisse_client_detail(request, pk):
    from .models import Client
    client = Client.objects.select_related('personne').get(pk=pk)
    return render(request, 'caisse/client/detail.html', {'client': client})

@login_required
def caisse_produit_detail(request, pk):
    from .models import Produit
    produit = Produit.objects.get(pk=pk)
    return render(request, 'caisse/produit/detail.html', {'produit': produit})

@login_required
def caisse_agent_detail(request, pk):
    from .models import Agent
    agent = Agent.objects.select_related('personne', 'fonction').get(pk=pk)
    return render(request, 'caisse/agent/detail.html', {'agent': agent})

# --- AGENT FACTURE ---
from django.contrib.auth.decorators import login_required

@login_required
def agent_facture_profile(request):
    from .models import Agent, Commande, Client
    from django.shortcuts import get_object_or_404
    from django.db.models import Count, Sum
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Récupérer l'agent connecté
    agent = get_object_or_404(Agent, user=request.user)
    
    # Calculer les statistiques de l'agent
    commandes_count = Commande.objects.filter(agent=agent).count()
    clients_count = Client.objects.filter(commande__agent=agent).distinct().count()
    total_ventes = Commande.objects.filter(agent=agent).aggregate(total=Sum('prix_total'))['total'] or 0
    
    # Commandes du mois en cours
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    commandes_ce_mois = Commande.objects.filter(
        agent=agent,
        date_commande__gte=debut_mois
    ).count()
    
    context = {
        'agent': agent,
        'personne': agent.personne,
        'profile_mode': True,
        'commandes_count': commandes_count,
        'clients_count': clients_count,
        'total_ventes': total_ventes,
        'commandes_ce_mois': commandes_ce_mois
    }
    
    return render(request, 'agent_facture/profile.html', context)

@login_required
def agent_facture_dashboard(request):
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Statistiques des commandes
    total_commandes = Commande.objects.count()
    commandes_aujourd_hui = Commande.objects.filter(
        date_commande__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0),
        date_commande__lt=timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    ).count()
    
    # Statistiques des clients
    total_clients = Client.objects.count()
    
    # Produits en stock faible
    produits_stock_faible = Produit.objects.filter(quantite_stock__lt=10).count()
    produits_stock_faible_list = Produit.objects.filter(quantite_stock__lt=10)[:5]
    
    # Dernières commandes
    dernieres_commandes = Commande.objects.select_related(
        'client__personne', 'agent__personne'
    ).order_by('-date_commande')[:5]
    
    context = {
        'total_commandes': total_commandes,
        'commandes_aujourd_hui': commandes_aujourd_hui,
        'total_clients': total_clients,
        'produits_stock_faible': produits_stock_faible,
        'produits_stock_faible_list': produits_stock_faible_list,
        'dernieres_commandes': dernieres_commandes,
    }
    
    return render(request, 'agent_facture/dashboard.html', context)

@login_required
def agent_facture_list(request):
    return render(request, 'agent_facture/list.html')

@login_required
def agent_facture_form(request):
    return render(request, 'agent_facture/form.html')

@login_required
def agent_facture_detail(request, pk):
    # Rediriger vers la vue d'impression complète de la commande
    return redirect('agent_facture_commande_print', pk=pk)

@login_required
def agent_facture_commande_list(request):
    from django.core.paginator import Paginator
    from django.db.models import Q, Sum
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Récupérer les paramètres de filtrage
    search = request.GET.get('search', '')
    date_debut = request.GET.get('date_debut', '')
    date_fin = request.GET.get('date_fin', '')
    statut = request.GET.get('statut', '')
    
    # Filtrer les commandes
    commandes = Commande.objects.select_related('client__personne', 'agent__personne')
    
    if search:
        commandes = commandes.filter(
            Q(client__personne__nom__icontains=search) |
            Q(client__personne__prenom__icontains=search) |
            Q(contenir__produit__nom_produit__icontains=search)
        ).distinct()
    
    if date_debut:
        commandes = commandes.filter(date_commande__gte=date_debut)
    
    if date_fin:
        commandes = commandes.filter(date_commande__lte=date_fin)
    
    if statut == 'recente':
        commandes = commandes.filter(date_commande__gte=timezone.now().date() - timedelta(days=7))
    elif statut == 'ancienne':
        commandes = commandes.filter(date_commande__lt=timezone.now().date() - timedelta(days=30))
    
    # Trier par ordre d'enregistrement (plus récentes en premier)
    commandes = commandes.order_by('-id')
    
    # Pagination
    paginator = Paginator(commandes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Statistiques
    total_commandes = commandes.count()
    commandes_aujourd_hui = commandes.filter(
        date_commande__gte=timezone.now().replace(hour=0, minute=0, second=0, microsecond=0),
        date_commande__lt=timezone.now().replace(hour=23, minute=59, second=59, microsecond=999999)
    ).count()
    total_montant = commandes.aggregate(total=Sum('prix_total'))['total'] or 0
    commandes_ce_mois = commandes.filter(
        date_commande__month=timezone.now().month,
        date_commande__year=timezone.now().year
    ).count()
    
    context = {
        'commandes': page_obj,
        'total_commandes': total_commandes,
        'commandes_aujourd_hui': commandes_aujourd_hui,
        'total_montant': total_montant,
        'commandes_ce_mois': commandes_ce_mois,
    }
    
    return render(request, 'agent_facture/commande_list.html', context)

@login_required
def agent_facture_stock(request):
    produits = Produit.objects.all()
    
    # Calculer les statistiques
    total_produits = produits.count()
    stock_faible = produits.filter(quantite_stock__lt=10).count()
    stock_ok = produits.filter(quantite_stock__gte=50).count()
    
    # Calculer la valeur totale du stock
    valeur_stock = sum(produit.prix_unitaire * produit.quantite_stock for produit in produits)
    
    context = {
        'produits': produits,
        'total_produits': total_produits,
        'stock_faible': stock_faible,
        'stock_ok': stock_ok,
        'valeur_stock': valeur_stock,
    }
    
    return render(request, 'agent_facture/stock.html', context)
@login_required
def agent_facture_commande_create(request):
    ProduitFormSet = inlineformset_factory(
        Commande,
        Contenir,
        fields=('produit', 'quantite'),
        extra=0,
        can_delete=True,
        min_num=1,
        validate_min=True
    )

    if request.method == 'POST':
        form = CommandeForm(request.POST)
        formset = ProduitFormSet(request.POST, prefix='produits')
        
        # Debug logs removed in production
        
        if form.is_valid() and formset.is_valid():
            # Créer la commande
            commande = form.save(commit=False)
            
            # Assigner l'agent connecté
            if hasattr(request.user, 'agent'):
                commande.agent = request.user.agent
            else:
                messages.error(request, "Votre utilisateur n'est pas lié à un agent. Veuillez contacter l'administrateur.")
                produits = Produit.objects.all()
                produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}
                return render(request, 'agent_facture/form.html', {
                    'form': form,
                    'formset': formset,
                    'produits_data': produits_data,
                })
            
            # Vérifier le stock et calculer le total
            total = 0
            stock_insuffisant = []
            produits_commandes = []
            
            for produit_form in formset:
                if produit_form.cleaned_data and not produit_form.cleaned_data.get('DELETE', False):
                    produit = produit_form.cleaned_data['produit']
                    quantite = produit_form.cleaned_data['quantite']
                    
                    # Vérifier le stock
                    if produit.quantite_stock < quantite:
                        stock_insuffisant.append({
                            'produit': produit.nom_produit,
                            'stock_disponible': produit.quantite_stock,
                            'quantite_demandee': quantite
                        })
                    else:
                        # Ajouter à la liste des produits commandés
                        produits_commandes.append({
                            'produit': produit,
                            'quantite': quantite
                        })
                        # Calculer le total
                        total += quantite * produit.prix_unitaire
            
            # Si stock insuffisant, refuser l'enregistrement
            if stock_insuffisant:
                messages.error(request, "❌ ENREGISTREMENT REFUSÉ - Stock insuffisant pour certains produits :")
                for item in stock_insuffisant:
                    messages.error(request, f"• {item['produit']}: Stock disponible {item['stock_disponible']}, Quantité demandée {item['quantite_demandee']}")
                messages.error(request, "Veuillez ajuster les quantités ou contacter le gestionnaire pour un approvisionnement.")
                
                # Préparer les données pour réafficher le formulaire
                produits = Produit.objects.all()
                produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}
                
                return render(request, 'agent_facture/form.html', {
                    'form': form,
                    'formset': formset,
                    'produits_data': produits_data,
                })
            
            # Sauvegarder la commande
            commande.prix_total = total
            commande.save()
            
            # Sauvegarder les produits et diminuer le stock
            formset.instance = commande
            formset.save()
            
            # Diminuer le stock des produits commandés
            for item in produits_commandes:
                produit = item['produit']
                quantite = item['quantite']
                produit.quantite_stock -= quantite
                produit.save()
            
            messages.success(request, f"Commande créée avec succès. Total: {total:.2f} FC")
            return redirect('agent_facture_commande_list')
        else:
            # Erreurs de validation gérées via messages ou affichage template
            
            # Préparer les données pour réafficher le formulaire
            produits = Produit.objects.all()
            produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}
            
            return render(request, 'agent_facture/form.html', {
                'form': form,
                'formset': formset,
                'produits_data': produits_data,
            })
    else:
        form = CommandeForm()
        formset = ProduitFormSet(prefix='produits', queryset=Contenir.objects.none())

    # Préparer les données des produits pour le JavaScript
    produits = Produit.objects.all()
    produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}

    return render(request, 'agent_facture/form.html', {
        'form': form,
        'formset': formset,
        'produits_data': produits_data,
    })
@login_required
def agent_facture_commande_detail(request, pk):
    from .models import Commande
    from django.shortcuts import get_object_or_404
    
    commande = get_object_or_404(Commande, pk=pk)
    
    # Récupérer les lignes de la commande avec calcul du total par ligne
    lignes = []
    for contenir in commande.contenir_set.all():
        ligne = {
            'produit': contenir.produit,
            'quantite': contenir.quantite,
            'prix_unitaire': contenir.produit.prix_unitaire,
            'total_ligne': contenir.produit.prix_unitaire * contenir.quantite
        }
        lignes.append(ligne)
    
    context = {
        'commande': commande,
        'lignes': lignes,
        'detail_mode': True
    }
    
    return render(request, 'agent_facture/detail.html', context)

@login_required
def agent_facture_commande_delete(request, pk):
    from .models import Commande
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    
    commande = get_object_or_404(Commande, pk=pk)
    
    if request.method == 'POST':
        # Restaurer le stock des produits commandés
        for contenir in commande.contenir_set.all():
            produit = contenir.produit
            produit.quantite_stock += contenir.quantite
            produit.save()
        
        # Supprimer la commande
        commande.delete()
        messages.success(request, f"Commande #{pk} supprimée avec succès.")
        return redirect('agent_facture_commande_list')
    
    # Afficher la page de confirmation de suppression
    context = {
        'commande': commande,
        'lignes': commande.contenir_set.all()
    }
    return render(request, 'agent_facture/delete_confirm.html', context)

@login_required
def agent_facture_commande_edit(request, pk):
    from .models import Commande, Produit
    from django.shortcuts import get_object_or_404, redirect
    from django.contrib import messages
    from django.forms import inlineformset_factory
    
    # Récupérer la commande existante
    commande = get_object_or_404(Commande, pk=pk)
    
    # Créer le formset pour les produits
    ProduitFormSet = inlineformset_factory(
        Commande,
        Contenir,
        fields=('produit', 'quantite'),
        extra=1,
        can_delete=True,
        min_num=1,
        validate_min=True
    )
    
    if request.method == 'POST':
        form = CommandeForm(request.POST, instance=commande)
        formset = ProduitFormSet(request.POST, instance=commande, prefix='produits')
        
        # Debug logs removed in production
        
        if form.is_valid() and formset.is_valid():
            # Sauvegarder la commande
            commande = form.save(commit=False)
            
            # Assigner l'agent connecté si pas déjà assigné
            if hasattr(request.user, 'agent') and not commande.agent:
                commande.agent = request.user.agent
            
            # Calculer le nouveau total
            total = 0
            stock_insuffisant = []
            produits_commandes = []
            
            for produit_form in formset:
                if produit_form.cleaned_data and not produit_form.cleaned_data.get('DELETE', False):
                    produit = produit_form.cleaned_data['produit']
                    quantite = produit_form.cleaned_data['quantite']
                    
                    # Vérifier le stock (en tenant compte des quantités déjà commandées)
                    quantite_actuelle = 0
                    if produit_form.instance.pk:
                        # Si c'est une modification, récupérer l'ancienne quantité
                        ancien_contenir = Contenir.objects.get(id=produit_form.instance.pk)
                        quantite_actuelle = ancien_contenir.quantite
                    
                    stock_disponible = produit.quantite_stock + quantite_actuelle
                    
                    if stock_disponible < quantite:
                        stock_insuffisant.append({
                            'produit': produit.nom_produit,
                            'stock_disponible': stock_disponible,
                            'quantite_demandee': quantite
                        })
                    else:
                        # Ajouter à la liste des produits commandés
                        produits_commandes.append({
                            'produit': produit,
                            'quantite': quantite,
                            'ancienne_quantite': quantite_actuelle
                        })
                        # Calculer le total
                        total += quantite * produit.prix_unitaire
            
            # Si stock insuffisant, refuser l'enregistrement
            if stock_insuffisant:
                messages.error(request, "❌ MODIFICATION REFUSÉE - Stock insuffisant pour certains produits :")
                for item in stock_insuffisant:
                    messages.error(request, f"• {item['produit']}: Stock disponible {item['stock_disponible']}, Quantité demandée {item['quantite_demandee']}")
                messages.error(request, "Veuillez ajuster les quantités ou contacter le gestionnaire pour un approvisionnement.")
                
                # Préparer les données pour réafficher le formulaire
                produits = Produit.objects.all()
                produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}
                
                return render(request, 'agent_facture/form.html', {
                    'form': form,
                    'formset': formset,
                    'produits_data': produits_data,
                    'edit_mode': True,
                    'commande': commande
                })
            
            # Sauvegarder la commande
            commande.prix_total = total
            commande.save()
            
            # Sauvegarder les produits et ajuster le stock
            formset.save()
            
            # Ajuster le stock des produits commandés
            for item in produits_commandes:
                produit = item['produit']
                nouvelle_quantite = item['quantite']
                ancienne_quantite = item['ancienne_quantite']
                
                # Restaurer l'ancienne quantité et soustraire la nouvelle
                produit.quantite_stock += ancienne_quantite - nouvelle_quantite
                produit.save()
            
            messages.success(request, f"Commande #{pk} modifiée avec succès. Nouveau total: {total:.2f} FC")
            return redirect('agent_facture_commande_list')
        else:
            # Erreurs de validation gérées via messages ou affichage template
            
            # Préparer les données pour réafficher le formulaire
            produits = Produit.objects.all()
            produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}
            
            return render(request, 'agent_facture/form.html', {
                'form': form,
                'formset': formset,
                'produits_data': produits_data,
                'edit_mode': True,
                'commande': commande
            })
    else:
        # Afficher le formulaire de modification
        form = CommandeForm(instance=commande)
        formset = ProduitFormSet(instance=commande, prefix='produits')
        
        # Préparer les données des produits pour le JavaScript
        produits = Produit.objects.all()
        produits_data = {str(p.id): {'nom': p.nom_produit, 'prix': float(p.prix_unitaire), 'stock': p.quantite_stock} for p in produits}
        
        return render(request, 'agent_facture/form.html', {
            'form': form,
            'formset': formset,
            'produits_data': produits_data,
            'edit_mode': True,
            'commande': commande
        })

@login_required
def agent_facture_commande_print(request, pk):
    from .models import Commande
    from django.utils import timezone
    
    try:
        commande = Commande.objects.select_related(
            'client__personne', 
            'agent__personne'
        ).prefetch_related(
            'contenir_set__produit'
        ).get(id=pk)
        
        # Récupérer les lignes de la commande avec calcul du total par ligne
        lignes = []
        for contenir in commande.contenir_set.all():
            ligne = {
                'produit': contenir.produit,
                'quantite': contenir.quantite,
                'prix_unitaire': contenir.produit.prix_unitaire,
                'total_ligne': contenir.produit.prix_unitaire * contenir.quantite
            }
            lignes.append(ligne)
        
        context = {
            'commande': commande,
            'lignes': lignes,
            'date_du_jour': timezone.now(),
            'print_mode': True,
            'user': request.user
        }
        
        return render(request, 'agent_facture/print.html', context)
    except Commande.DoesNotExist:
        from django.shortcuts import get_object_or_404
        return get_object_or_404(Commande, id=pk)

@login_required
def agent_facture_client_create(request):
    # Utilise le formulaire standardisé ClientPersonneForm (évite duplications)
    if request.method == 'POST':
        form = ClientPersonneForm(request.POST)
        if form.is_valid():
            client = form.save()
            messages.success(request, f'Client {client.personne.prenom} {client.personne.nom} créé avec succès.')
            return redirect('agent_facture_client_list')
    else:
        form = ClientPersonneForm()
    return render(request, 'agent_facture/client_form.html', {'form': form, 'title': 'Créer un client'})

@login_required
def agent_facture_client_list(request):
    from .models import Client
    from django.db.models import Count, Q
    from django.core.paginator import Paginator
    from django.utils import timezone
    from datetime import timedelta
    
    # Récupérer tous les clients avec leurs données liées
    clients = Client.objects.select_related('personne').prefetch_related('commande_set')
    
    # Filtres
    search = request.GET.get('search', '')
    tri = request.GET.get('tri', 'nom')
    statut = request.GET.get('statut', '')
    
    # Appliquer les filtres
    if search:
        clients = clients.filter(
            Q(personne__nom__icontains=search) |
            Q(personne__prenom__icontains=search) |
            Q(personne__postnom__icontains=search)
        )
    
    # Tri
    if tri == 'nom':
        clients = clients.order_by('personne__nom', 'personne__prenom')
    elif tri == 'recent':
        clients = clients.order_by('-id')
    elif tri == 'ancien':
        clients = clients.order_by('id')
    
    # Statut (actif/inactif basé sur les commandes récentes)
    if statut == 'actif':
        date_limite = timezone.now().date() - timedelta(days=30)
        clients = clients.filter(commande__date_commande__gte=date_limite).distinct()
    elif statut == 'inactif':
        date_limite = timezone.now().date() - timedelta(days=30)
        clients = clients.exclude(commande__date_commande__gte=date_limite).distinct()
    
    # Pagination
    paginator = Paginator(clients, 10)
    page_number = request.GET.get('page')
    clients_page = paginator.get_page(page_number)
    
    # Statistiques
    total_clients = Client.objects.count()
    clients_actifs = Client.objects.filter(
        commande__date_commande__gte=timezone.now().date() - timedelta(days=30)
    ).distinct().count()
    nouveaux_clients = Client.objects.filter(
        id__gte=Client.objects.count() - 10  # Approximatif pour les nouveaux
    ).count()
    
    # Calculer la moyenne des commandes par client
    total_commandes = sum(client.commande_set.count() for client in Client.objects.all())
    commandes_moyenne = total_commandes / total_clients if total_clients > 0 else 0
    
    context = {
        'clients': clients_page,
        'total_clients': total_clients,
        'clients_actifs': clients_actifs,
        'nouveaux_clients': nouveaux_clients,
        'commandes_moyenne': round(commandes_moyenne, 1),
    }
    
    return render(request, 'agent_facture/client_list.html', context)

# Duplicate removed: agent_facture_client_create is defined earlier

@login_required
def agent_facture_client_detail(request, pk):
    from .models import Client
    client = Client.objects.select_related('personne').get(pk=pk)
    return render(request, 'agent_facture/client_detail.html', {'client': client})

@login_required
def agent_facture_client_edit(request, pk):
    from .models import Client, Personne
    client = get_object_or_404(Client, pk=pk)
    personne = client.personne
    if request.method == 'POST':
        form = ClientPersonneForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            personne.nom = data['nom']
            personne.postnom = data['postnom']
            personne.prenom = data['prenom']
            personne.sexe = data['sexe']
            personne.date_naissance = data['date_naissance']
            personne.save()
            messages.success(request, 'Client modifié avec succès.')
            return redirect('agent_facture_client_detail', pk=client.pk)
    else:
        form = ClientPersonneForm(initial={
            'nom': personne.nom,
            'postnom': personne.postnom,
            'prenom': personne.prenom,
            'sexe': personne.sexe,
            'date_naissance': personne.date_naissance
        })
    return render(request, 'agent_facture/client_form.html', {'form': form, 'title': 'Modifier le client'})

@login_required
def agent_facture_client_delete(request, pk):
    from .models import Client
    client = get_object_or_404(Client, pk=pk)
    if request.method == 'POST':
        client.personne.delete()
        client.delete()
        messages.success(request, 'Client supprimé avec succès.')
        return redirect('agent_facture_client_list')
    return render(request, 'agent_facture/client_confirm_delete.html', {'client': client})

@login_required
def agent_livraison_dashboard(request):
    return render(request, 'agent_livraison/dashboard.html')

@login_required
def agent_livraison_stock(request):
    produits = Produit.objects.all()
    return render(request, 'agent_livraison/stock.html', {'produits': produits})

@login_required
def agent_livraison_facture_verification(request):
    facture = None
    numero = request.GET.get('numero_facture')
    if numero:
        try:
            commande = Commande.objects.get(id=numero)
            client = commande.client
            personne = client.personne
            nom_complet = f"{personne.nom} {personne.postnom} {personne.prenom}"
            facture = {
                'numero': commande.id,
                'client': nom_complet,
                'date': commande.date_commande,
                'montant_total': commande.prix_total,
                'lignes': Contenir.objects.filter(commande=commande)
            }
        except Commande.DoesNotExist:
            facture = None
    return render(request, 'agent_livraison/facture_verification.html', {'facture': facture})

@login_required
def caisse_sortie_fond_list(request):
    sorties = SortieFond.objects.select_related('agent', 'demande').all()
    return render(request, 'caisse/sortie_fond/list.html', {'sorties': sorties})

@login_required
def caisse_sortie_fond_create(request):
    if request.method == 'POST':
        form = SortieFondForm(request.POST)
        if form.is_valid():
            sortie = form.save(commit=False)
            # Remplir automatiquement l'agent connecté
            if hasattr(request.user, 'agent'):
                sortie.agent = request.user.agent
            sortie.save()
            messages.success(request, "Sortie de fonds créée avec succès.")
            return redirect('caisse_sortie_fond_detail', sortie.id)
    else:
        form = SortieFondForm()
    return render(request, 'caisse/sortie_fond/form.html', {'form': form, 'title': 'Nouvelle Sortie de Fonds'})

@login_required
def caisse_sortie_fond_detail(request, pk):
    sortie = get_object_or_404(SortieFond, pk=pk)
    return render(request, 'caisse/sortie_fond/detail.html', {'sortie': sortie})

@login_required
def caisse_sortie_fond_delete(request, pk):
    sortie = get_object_or_404(SortieFond, pk=pk)
    if request.method == 'POST':
        sortie.delete()
        return redirect('caisse_sortie_fond_list')
    return render(request, 'caisse/sortie_fond/delete.html', {'sortie': sortie})

@login_required
def caisse_sortie_fond_update(request, pk):
    sortie = get_object_or_404(SortieFond, pk=pk)
    if request.method == 'POST':
        form = SortieFondForm(request.POST, instance=sortie)
        if form.is_valid():
            sortie = form.save(commit=False)
            if hasattr(request.user, 'agent'):
                sortie.agent = request.user.agent
            sortie.save()
            messages.success(request, "Sortie de fonds modifiée avec succès.")
            return redirect('caisse_sortie_fond_detail', sortie.id)
    else:
        form = SortieFondForm(instance=sortie)
    return render(request, 'caisse/sortie_fond/form.html', {'form': form, 'title': 'Modifier Sortie de Fonds'})

@login_required
def caisse_sortie_fond_print(request, pk):
    sortie = get_object_or_404(SortieFond, pk=pk)
    from django.utils import timezone
    date_du_jour = timezone.now()
    user = request.user
    return render(request, 'caisse/sortie_fond/print.html', {
        'sortie': sortie,
        'date_du_jour': date_du_jour,
        'user': user,
    })

@login_required
def gestionnaire_agent_list(request):
    from .models import Agent
    agents = Agent.objects.select_related('user', 'personne', 'fonction').all()
    return render(request, 'gestionaire/agent/list.html', {'agents': agents})

@login_required
def gestionnaire_agent_update(request, pk):
    from .models import Agent
    agent = Agent.objects.get(pk=pk)
    if request.method == 'POST':
        form = AgentForm(request.POST, instance=agent)
        if form.is_valid():
            form.save()
            return redirect('gestionnaire_agent_list')
    else:
        form = AgentForm(instance=agent)
    return render(request, 'gestionaire/agent/form.html', {'form': form, 'title': 'Modifier un agent'})

# =============================================================================
# VUES POUR LES RAPPORTS
# =============================================================================

@login_required
def rapport_approvisionnement(request):
    """Rapport d'approvisionnement de médicaments filtrable par plage de dates"""
    from django.db.models import Sum
    from datetime import datetime
    
    # Récupération des paramètres de filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    # Requête de base
    approvisionnements = Approvisionnement.objects.select_related(
        'agent', 'sortie_fond', 'sortie_fond__demande', 'sortie_fond__demande__fournisseur'
    ).prefetch_related('approvisionner_set__produit')
    
    # Application des filtres
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            approvisionnements = approvisionnements.filter(date_approvisionnement__gte=date_debut)
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            approvisionnements = approvisionnements.filter(date_approvisionnement__lte=date_fin)
        except ValueError:
            pass
    
    # Calcul des statistiques
    total_approvisionnements = approvisionnements.count()
    total_produits = 0
    for appro in approvisionnements:
        total_produits += appro.approvisionner_set.count()
    
    context = {
        'approvisionnements': approvisionnements,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'total_approvisionnements': total_approvisionnements,
        'total_produits': total_produits,
    }
    
    return render(request, 'gestionaire/rapport/approvisionnement.html', context)

@login_required
def rapport_etat_stock(request):
    """État de stock actuel avec filtrage possible"""
    from django.db.models import Q
    
    # Récupération des paramètres de filtrage
    categorie = request.GET.get('categorie')
    produit_recherche = request.GET.get('produit')
    seuil_critique = request.GET.get('seuil_critique')
    
    # Requête de base
    produits = Produit.objects.all()
    
    # Application des filtres
    if categorie:
        produits = produits.filter(forme=categorie)
    
    if produit_recherche:
        produits = produits.filter(
            Q(nom_produit__icontains=produit_recherche) | 
            Q(code_produit__icontains=produit_recherche)
        )
    
    if seuil_critique:
        try:
            seuil = int(seuil_critique)
            produits = produits.filter(quantite_stock__lte=seuil)
        except ValueError:
            pass
    
    # Calcul des statistiques
    total_produits = produits.count()
    produits_en_rupture = produits.filter(quantite_stock=0).count()
    produits_faible_stock = produits.filter(quantite_stock__lte=10).count()
    produits_stock_ok = total_produits - produits_en_rupture - produits_faible_stock
    
    # Calcul des produits qui expirent dans 10 jours
    from datetime import date, timedelta
    aujourd_hui = date.today()
    date_limite = aujourd_hui + timedelta(days=10)
    
    produits_expiration_proche = produits.filter(
        date_expiration__lte=date_limite,
        date_expiration__gte=aujourd_hui,
        quantite_stock__gt=0
    ).count()
    
    context = {
        'produits': produits,
        'categorie': categorie,
        'produit_recherche': produit_recherche,
        'seuil_critique': seuil_critique,
        'total_produits': total_produits,
        'produits_en_rupture': produits_en_rupture,
        'produits_faible_stock': produits_faible_stock,
        'produits_stock_ok': produits_stock_ok,
        'produits_expiration_proche': produits_expiration_proche,
        'aujourd_hui': aujourd_hui,
        'date_limite': date_limite,
    }
    
    return render(request, 'gestionaire/rapport/etat_stock.html', context)

@login_required
def rapport_activite_globale(request):
    """Rapport global d'activité (Entrées/Sorties)"""
    from django.db.models import Sum, Q
    from datetime import datetime, timedelta
    
    # Récupération des paramètres de filtrage
    periode = request.GET.get('periode', '30')  # Par défaut 30 jours
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    
    try:
        periode = int(periode)
    except ValueError:
        periode = 30
    
    # Calcul des dates si non fournies
    if not date_debut:
        date_debut = datetime.now().date() - timedelta(days=periode)
    else:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
        except ValueError:
            date_debut = datetime.now().date() - timedelta(days=periode)
    
    if not date_fin:
        date_fin = datetime.now().date()
    else:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
        except ValueError:
            date_fin = datetime.now().date()
    
    # Récupération des données
    # Approvisionnements (Entrées)
    approvisionnements = Approvisionnement.objects.filter(
        date_approvisionnement__range=[date_debut, date_fin]
    ).select_related('agent', 'sortie_fond__demande__fournisseur')
    
    # Ventes (Sorties via Commandes)
    commandes = Commande.objects.filter(
        date_commande__range=[date_debut, date_fin]
    ).select_related('client__personne', 'agent')
    
    # Pertes (Sorties)
    pertes = Perte.objects.filter(
        date_perte__range=[date_debut, date_fin]
    ).select_related('agent', 'type_perte')
    
    # Calcul des statistiques
    total_approvisionnements = approvisionnements.count()
    total_commandes = commandes.count()
    total_pertes = pertes.count()
    
    # Calcul des montants
    montant_approvisionnements = sum(
        appro.sortie_fond.montant for appro in approvisionnements
    )
    montant_ventes = sum(commande.prix_total for commande in commandes)
    
    # Calcul de la balance (Ventes - Achats)
    balance = montant_ventes - montant_approvisionnements
    
    context = {
        'approvisionnements': approvisionnements,
        'commandes': commandes,
        'pertes': pertes,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'periode': periode,
        'total_approvisionnements': total_approvisionnements,
        'total_commandes': total_commandes,
        'total_pertes': total_pertes,
        'montant_approvisionnements': montant_approvisionnements,
        'montant_ventes': montant_ventes,
        'balance': balance,
    }
    
    return render(request, 'gestionaire/rapport/activite_globale.html', context)

@login_required
def rapport_pertes(request):
    """Rapport des pertes de médicaments"""
    from datetime import datetime
    
    # Récupération des paramètres de filtrage
    date_debut = request.GET.get('date_debut')
    date_fin = request.GET.get('date_fin')
    produit_id = request.GET.get('produit')
    type_perte_id = request.GET.get('type_perte')
    
    # Requête de base
    pertes = Perte.objects.select_related('agent', 'type_perte').prefetch_related('encaisse_set__produit')
    
    # Application des filtres
    if date_debut:
        try:
            date_debut = datetime.strptime(date_debut, '%Y-%m-%d').date()
            pertes = pertes.filter(date_perte__gte=date_debut)
        except ValueError:
            pass
    
    if date_fin:
        try:
            date_fin = datetime.strptime(date_fin, '%Y-%m-%d').date()
            pertes = pertes.filter(date_perte__lte=date_fin)
        except ValueError:
            pass
    
    if produit_id:
        pertes = pertes.filter(encaisse__produit_id=produit_id)
    
    if type_perte_id:
        pertes = pertes.filter(type_perte_id=type_perte_id)
    
    # Calcul des statistiques
    total_pertes = pertes.count()
    total_quantite_perdue = sum(perte.quantite_perdue for perte in pertes)
    
    # Récupération des listes pour les filtres
    produits = Produit.objects.all()
    types_perte = TypePerte.objects.all()
    
    context = {
        'pertes': pertes,
        'produits': produits,
        'types_perte': types_perte,
        'date_debut': date_debut,
        'date_fin': date_fin,
        'produit_id': produit_id,
        'type_perte_id': type_perte_id,
        'total_pertes': total_pertes,
        'total_quantite_perdue': total_quantite_perdue,
    }
    
    return render(request, 'gestionaire/rapport/pertes.html', context)

@login_required
def rapport_index(request):
    """Page d'accueil des rapports"""
    from datetime import date, timedelta
    
    # Calcul des statistiques rapides
    nb_produits_en_stock = Produit.objects.count()
    commandes_en_attente = Commande.objects.count()  # Simplifié pour l'exemple
    alertes_stock_faible = Produit.objects.filter(quantite_stock__lte=10).count()
    receptions_aujourd_hui = Approvisionnement.objects.filter(
        date_approvisionnement=date.today()
    ).count()
    
    context = {
        'nb_produits_en_stock': nb_produits_en_stock,
        'commandes_en_attente': commandes_en_attente,
        'alertes_stock_faible': alertes_stock_faible,
        'receptions_aujourd_hui': receptions_aujourd_hui,
    }
    
    return render(request, 'gestionaire/rapport/index.html', context)

