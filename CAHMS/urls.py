from django.urls import path
from django.shortcuts import redirect
from . import views

def redirect_to_dashboard(request):
    return redirect('dashboard')

def redirect_to_login(request):
    return redirect('login')

urlpatterns = [
    # Page d'accueil - redirection vers dashboard
    path('', redirect_to_login, name='home'),
    
    # Dashboard
    path('dashboard/', views.gestionnaire_dashboard, name='dashboard'),

    # Fournisseur
    path('fournisseurs/', views.fournisseur_list, name='fournisseur_list'),
    path('fournisseurs/creer/', views.fournisseur_create, name='fournisseur_create'),
    path('fournisseurs/<int:pk>/modifier/', views.fournisseur_update, name='fournisseur_update'),
    path('fournisseurs/<int:pk>/supprimer/', views.fournisseur_delete, name='fournisseur_delete'),

    # Produit
    path('produits/', views.produit_list, name='produit_list'),
    path('produits/creer/', views.produit_create, name='produit_create'),
    path('produits/<int:pk>/modifier/', views.produit_update, name='produit_update'),
    path('produits/<int:pk>/supprimer/', views.produit_delete, name='produit_delete'),
    path('produits/<int:pk>/imprimer/', views.produit_print, name='produit_print'),

    # Perte
    path('pertes/', views.perte_list, name='perte_list'),
    path('pertes/creer/', views.perte_create, name='perte_create'),
    path('pertes/<int:pk>/modifier/', views.perte_update, name='perte_update'),
    path('pertes/<int:pk>/supprimer/', views.perte_delete, name='perte_delete'),
    path('pertes/<int:pk>/imprimer/', views.perte_print, name='perte_print'),

    # Approvisionnement
    path('approvisionnements/', views.approvisionnement_list, name='approvisionnement_list'),
    path('approvisionnements/creer/', views.approvisionnement_create, name='approvisionnement_create'),
    path('approvisionnements/<int:pk>/modifier/', views.approvisionnement_update, name='approvisionnement_update'),
    path('approvisionnements/<int:pk>/supprimer/', views.approvisionnement_delete, name='approvisionnement_delete'),
    path('approvisionnements/<int:pk>/imprimer/', views.approvisionnement_print, name='approvisionnement_print'),

    # Demande de fonds
    path('demandes-fonds/', views.demande_fond_list, name='demande_fond_list'),
    path('demandes-fonds/creer/', views.demande_fond_create, name='demande_fond_create'),
    path('demandes-fonds/<int:pk>/modifier/', views.demande_fond_update, name='demande_fond_update'),
    path('demandes-fonds/<int:pk>/supprimer/', views.demande_fond_delete, name='demande_fond_delete'),
    path('demandes-fonds/<int:pk>/imprimer/', views.demande_fond_print, name='demande_fond_print'),

    # Stock
    path('stock/', views.stock_list, name='stock_list'),

    # Profil utilisateur
    path('profil/', views.profile_utilisateur, name='profile_utilisateur'),

    # Caisse - Paiements
    path('caisse/paiements/', views.caisse_paiement_list, name='caisse_paiement_list'),
    # Caisse - Paiement détail
    path('caisse/paiements/<int:pk>/', views.caisse_paiement_detail, name='caisse_paiement_detail'),
    # Caisse - Paiement modification
    path('caisse/paiements/<int:pk>/modifier/', views.caisse_paiement_update, name='caisse_paiement_update'),
    # Caisse - Paiement suppression
    path('caisse/paiements/<int:pk>/supprimer/', views.caisse_paiement_delete, name='caisse_paiement_delete'),
    # Caisse - Paiement impression
    path('caisse/paiements/<int:pk>/imprimer/', views.caisse_paiement_print, name='caisse_paiement_print'),
    # Caisse - Commandes
    path('caisse/commandes/', views.caisse_commande_list, name='caisse_commande_list'),
    # Caisse - Agents
    path('caisse/agents/', views.caisse_agent_list, name='caisse_agent_list'),
    # Caisse - Agent détail
    path('caisse/agents/<int:pk>/', views.caisse_agent_detail, name='caisse_agent_detail'),
    # Caisse - Produits
    path('caisse/produits/', views.caisse_produit_list, name='caisse_produit_list'),
    # Caisse - Produit détail
    path('caisse/produits/<int:pk>/', views.caisse_produit_detail, name='caisse_produit_detail'),
    # Caisse - Clients
    path('caisse/clients/', views.caisse_client_list, name='caisse_client_list'),
    # Caisse - Client détail
    path('caisse/clients/<int:pk>/', views.caisse_client_detail, name='caisse_client_detail'),
    # Caisse - Paiement création
    path('caisse/paiements/creer/', views.caisse_paiement_create, name='caisse_paiement_create'),
    # Caisse - Fournisseurs
    path('caisse/fournisseurs/', views.caisse_fournisseur_list, name='caisse_fournisseur_list'),
    # Caisse - Vérification facture
    path('caisse/paiements/verification/', views.caisse_verification_facture, name='caisse_verification_facture'),
    # Caisse - Dashboard
    path('caisse/', views.caisse_dashboard, name='caisse_dashboard'),
    # Agent Facture - Dashboard
    path('agent-facture/', views.agent_facture_dashboard, name='agent_facture_dashboard'),
    # Agent Facture - Profile
    path('agent-facture/profile/', views.agent_facture_profile, name='agent_facture_profile'),
    # Agent Facture - Liste des factures
    path('agent-facture/factures/', views.agent_facture_list, name='agent_facture_list'),
    # Agent Facture - Création
    path('agent-facture/factures/creer/', views.agent_facture_form, name='agent_facture_create'),
    # Agent Facture - Détail/Impression
    path('agent-facture/factures/<int:pk>/', views.agent_facture_detail, name='agent_facture_detail'),
    # Agent Facture - Commande création
    path('agent-facture/commandes/creer/', views.agent_facture_commande_create, name='agent_facture_commande_create'),
    # Agent Facture - Commande détail
    path('agent-facture/commandes/<int:pk>/', views.agent_facture_commande_detail, name='agent_facture_commande_detail'),
    # Agent Facture - Commande édition
    path('agent-facture/commandes/<int:pk>/modifier/', views.agent_facture_commande_edit, name='agent_facture_commande_edit'),
    # Agent Facture - Commande impression
    path('agent-facture/commandes/<int:pk>/imprimer/', views.agent_facture_commande_print, name='agent_facture_commande_print'),
    # Agent Facture - Commande suppression
    path('agent-facture/commandes/<int:pk>/supprimer/', views.agent_facture_commande_delete, name='agent_facture_commande_delete'),
    # Agent Facture - Clients CRUD
    path('agent-facture/clients/', views.agent_facture_client_list, name='agent_facture_client_list'),
    path('agent-facture/clients/creer/', views.agent_facture_client_create, name='agent_facture_client_create'),
    path('agent-facture/clients/<int:pk>/', views.agent_facture_client_detail, name='agent_facture_client_detail'),
    path('agent-facture/clients/<int:pk>/modifier/', views.agent_facture_client_edit, name='agent_facture_client_edit'),
    path('agent-facture/clients/<int:pk>/supprimer/', views.agent_facture_client_delete, name='agent_facture_client_delete'),
    path('agent-facture/stock/', views.agent_facture_stock, name='agent_facture_stock'),
    path('agent-facture/commandes/', views.agent_facture_commande_list, name='agent_facture_commande_list'),
    # Agent Livraison - Dashboard
    path('agent-livraison/', views.agent_livraison_dashboard, name='agent_livraison_dashboard'),
    # Agent Livraison - Stock
    path('agent-livraison/stock/', views.agent_livraison_stock, name='agent_livraison_stock'),
    # Agent Livraison - Vérification Facture
    path('agent-livraison/facture-verification/', views.agent_livraison_facture_verification, name='agent_livraison_facture_verification'),
    # Caisse - Sortie de fond
    path('caisse/sorties-fond/', views.caisse_sortie_fond_list, name='caisse_sortie_fond_list'),
    path('caisse/sorties-fond/creer/', views.caisse_sortie_fond_create, name='caisse_sortie_fond_create'),
    path('caisse/sorties-fond/<int:pk>/', views.caisse_sortie_fond_detail, name='caisse_sortie_fond_detail'),
    path('caisse/sorties-fond/<int:pk>/supprimer/', views.caisse_sortie_fond_delete, name='caisse_sortie_fond_delete'),
    path('caisse/sorties-fond/<int:pk>/modifier/', views.caisse_sortie_fond_update, name='caisse_sortie_fond_update'),
    path('caisse/sorties-fond/<int:pk>/imprimer/', views.caisse_sortie_fond_print, name='caisse_sortie_fond_print'),
]

urlpatterns += [
    path('login/', views.login_view, name='login'),
    path('gestionnaire/agents/', views.gestionnaire_agent_list, name='gestionnaire_agent_list'),
    path('gestionnaire/agents/<int:pk>/modifier/', views.gestionnaire_agent_update, name='gestionnaire_agent_update'),
]

# =============================================================================
# URLs POUR LES RAPPORTS
# =============================================================================

urlpatterns += [
    # Rapports
    path('rapports/', views.rapport_index, name='rapport_index'),
    path('rapports/approvisionnement/', views.rapport_approvisionnement, name='rapport_approvisionnement'),
    path('rapports/etat-stock/', views.rapport_etat_stock, name='rapport_etat_stock'),
    path('rapports/activite-globale/', views.rapport_activite_globale, name='rapport_activite_globale'),
    path('rapports/pertes/', views.rapport_pertes, name='rapport_pertes'),
]
