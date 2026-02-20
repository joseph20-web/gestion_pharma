from django.core.management.base import BaseCommand
import random
from decimal import Decimal
from CAHMS.models import Produit

class Command(BaseCommand):
    help = 'Mettre à jour les prix des produits existants en nombres entiers'

    def add_arguments(self, parser):
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la mise à jour sans demander confirmation',
        )

    def handle(self, *args, **options):
        # Récupérer tous les produits
        produits = Produit.objects.all()
        
        if not options['force']:
            self.stdout.write(
                self.style.WARNING(f'⚠️  Vous êtes sur le point de modifier {produits.count()} produits')
            )
            reponse = input("Voulez-vous continuer? (oui/non): ").lower().strip()
            
            if reponse not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(
                    self.style.ERROR('❌ Opération annulée')
                )
                return

        self.stdout.write(
            self.style.SUCCESS(f'🚀 Début de la mise à jour des prix pour {produits.count()} produits...')
        )
        self.stdout.write('=' * 60)

        produits_modifies = 0

        for produit in produits:
            # Générer un nouveau prix en entier (entre 100 et 5000 FC)
            nouveau_prix = Decimal(str(random.randint(100, 5000)))
            
            # Sauvegarder l'ancien prix pour l'affichage
            ancien_prix = produit.prix_unitaire
            
            # Mettre à jour le prix
            produit.prix_unitaire = nouveau_prix
            produit.save()
            
            produits_modifies += 1
            
            self.stdout.write(
                self.style.SUCCESS(f'✅ {produit.nom_produit}')
            )
            self.stdout.write(
                f'   Ancien prix: {ancien_prix} FC → Nouveau prix: {nouveau_prix} FC'
            )
            self.stdout.write('')

        self.stdout.write('=' * 60)
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Mise à jour terminée!')
        )
        self.stdout.write(f'📊 {produits_modifies} produits mis à jour')
        self.stdout.write('=' * 60) 