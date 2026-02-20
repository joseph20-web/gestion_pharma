from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, Personne, Fonction, Agent, Client, Produit, Fournisseur,
    Commande, Contenir, TypePerte, Perte, Encaisse, Paiement,
    DemandeFond, SortieFond, Designer, Approvisionnement, Approvisionner
)

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('id', 'personne', 'get_nom', 'get_postnom', 'get_prenom', 'get_sexe', 'get_date_naissance')
    search_fields = ('personne__nom', 'personne__postnom', 'personne__prenom')
    def get_nom(self, obj):
        return obj.personne.nom
    get_nom.short_description = 'Nom'
    def get_postnom(self, obj):
        return obj.personne.postnom
    get_postnom.short_description = 'Post-nom'
    def get_prenom(self, obj):
        return obj.personne.prenom
    get_prenom.short_description = 'Prénom'
    def get_sexe(self, obj):
        return obj.personne.sexe
    get_sexe.short_description = 'Sexe'
    def get_date_naissance(self, obj):
        return obj.personne.date_naissance
    get_date_naissance.short_description = 'Date de naissance'

@admin.register(Personne)
class PersonneAdmin(admin.ModelAdmin):
    list_display = ('nom', 'postnom', 'prenom', 'sexe', 'date_naissance', 'est_actif')
    search_fields = ('nom', 'postnom', 'prenom')

admin.site.register(User, UserAdmin)
admin.site.register(Fonction)
admin.site.register(Agent)
admin.site.register(Produit)
admin.site.register(Fournisseur)
admin.site.register(Commande)
admin.site.register(Contenir)
admin.site.register(TypePerte)
admin.site.register(Perte)
admin.site.register(Encaisse)
admin.site.register(Paiement)
admin.site.register(DemandeFond)
admin.site.register(SortieFond)
admin.site.register(Designer)
admin.site.register(Approvisionnement)
admin.site.register(Approvisionner)



