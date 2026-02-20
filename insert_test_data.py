#!/usr/bin/env python
"""
Script pour insérer des données de test dans la base de données CAHMS
- 10 fournisseurs
- 100 produits avec dosages, formes et prix unitaires
"""

import os
import sys
import django
from datetime import date, timedelta
import random
from decimal import Decimal

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APPRO.settings')
django.setup()

from CAHMS.models import Fournisseur, Produit

def create_fournisseurs():
    """Créer 10 fournisseurs"""
    fournisseurs_data = [
        "Pharmacie Centrale de Kinshasa",
        "Laboratoires Pharmakina",
        "Société Pharmaceutique du Congo",
        "Medicaments Express",
        "Pharmacie Universelle",
        "Laboratoires Biocongo",
        "Pharmacie Moderne",
        "Société de Distribution Pharmaceutique",
        "Pharmacie de Référence",
        "Laboratoires Congopharma"
    ]
    
    fournisseurs = []
    for designation in fournisseurs_data:
        fournisseur, created = Fournisseur.objects.get_or_create(
            designation=designation
        )
        fournisseurs.append(fournisseur)
        if created:
            print(f"✅ Fournisseur créé: {designation}")
        else:
            print(f"⚠️ Fournisseur existant: {designation}")
    
    return fournisseurs

def create_products():
    """Créer 100 produits avec dosages, formes et prix unitaires"""
    
    # Données pour les produits
    noms_produits = [
        "Paracétamol", "Ibuprofène", "Amoxicilline", "Oméprazole", "Métronidazole",
        "Ciprofloxacine", "Doxycycline", "Azithromycine", "Clarithromycine", "Céphalexine",
        "Ampicilline", "Pénicilline", "Érythromycine", "Tétracycline", "Chloramphénicol",
        "Gentamicine", "Kanamycine", "Streptomycine", "Néomycine", "Polymyxine",
        "Colistine", "Bacitracine", "Vancomycine", "Rifampicine", "Isoniazide",
        "Pyrazinamide", "Éthambutol", "Streptomycine", "Capréomycine", "Amikacine",
        "Tobramycine", "Netilmicine", "Sisomicine", "Dibékacine", "Arbékacine",
        "Aspirine", "Diclofénac", "Kétoprofène", "Naproxène", "Indométacine",
        "Piroxicam", "Méloxicam", "Célécoxib", "Rofécoxib", "Valdécoxib",
        "Étorécoxib", "Lumiracoxib", "Parecoxib", "Ténoxicam", "Lornoxicam",
        "Métamizole", "Phénazone", "Propiphénazone", "Isopropylantipyrine", "Aminophénazone",
        "Déxaméthasone", "Prednisolone", "Méthylprednisolone", "Triamcinolone", "Bétaméthasone",
        "Budesonide", "Fluticasone", "Mometasone", "Ciclesonide", "Beclomethasone",
        "Salbutamol", "Terbutaline", "Formotérol", "Salmétérol", "Indacatérol",
        "Vilanterol", "Olodaterol", "Abediterol", "Carmoterol", "Bitolterol",
        "Montelukast", "Zafirlukast", "Pranlukast", "Ibudilast", "Cilomilast",
        "Roflumilast", "Apremilast", "Crisaborole", "Tofacitinib", "Baricitinib",
        "Upadacitinib", "Filgotinib", "Peficitinib", "Delgocitinib", "Ruxolitinib",
        "Loratadine", "Cétirizine", "Fexofénadine", "Desloratadine", "Levocétirizine",
        "Bilastine", "Rupatadine", "Ebastine", "Azelastine", "Olopatadine",
        "Ranitidine", "Famotidine", "Cimétidine", "Nizatidine", "Roxatidine",
        "Lafutidine", "Lafutidine", "Lafutidine", "Lafutidine", "Lafutidine",
        "Lansoprazole", "Pantoprazole", "Rabéprazole", "Ésoméprazole", "Dexlansoprazole",
        "Ilaprazole", "Tenatoprazole", "Pumaprazole", "S-pantoprazole", "R-lansoprazole"
    ]
    
    formes = [
        ('comprime', 'Comprimé'),
        ('gelule', 'Gélule'),
        ('sirop', 'Sirop'),
        ('injectable', 'Injectable'),
        ('pommade', 'Pommade'),
        ('creme', 'Crème'),
        ('suppositoire', 'Suppositoire'),
        ('collyre', 'Collyre'),
        ('suspension', 'Suspension'),
        ('poudre', 'Poudre')
    ]
    
    unites = [
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
        ('UI', 'UI (unités internationales)')
    ]
    
    dosages = [
        "500mg", "1000mg", "250mg", "125mg", "750mg", "400mg", "200mg", "100mg", "50mg", "25mg",
        "10mg", "5mg", "2.5mg", "1mg", "0.5mg", "0.25mg", "0.1mg", "0.05mg", "0.025mg", "0.01mg",
        "20mg", "40mg", "80mg", "160mg", "320mg", "640mg", "1280mg", "2560mg", "5120mg", "10240mg",
        "15mg", "30mg", "60mg", "120mg", "240mg", "480mg", "960mg", "1920mg", "3840mg", "7680mg",
        "7.5mg", "15mg", "30mg", "60mg", "120mg", "240mg", "480mg", "960mg", "1920mg", "3840mg"
    ]
    
    produits_crees = []
    
    for i in range(100):
        # Sélectionner des données aléatoires
        nom = noms_produits[i % len(noms_produits)]
        forme = formes[i % len(formes)][0]
        unite = unites[i % len(unites)][0]
        dosage = dosages[i % len(dosages)]
        
        # Générer un prix unitaire en entier (entre 100 et 5000 FC)
        prix = Decimal(str(random.randint(100, 5000)))
        
        # Générer une date d'expiration (entre 1 an et 5 ans)
        date_exp = date.today() + timedelta(days=random.randint(365, 1825))
        
        # Générer un code produit unique
        code_produit = f"PROD{(i+1):03d}"
        
        # Créer le produit
        produit, created = Produit.objects.get_or_create(
            code_produit=code_produit,
            defaults={
                'nom_produit': f"{nom} {dosage}",
                'prix_unitaire': prix,
                'dosage': dosage,
                'forme': forme,
                'unite': unite,
                'date_expiration': date_exp,
                'quantite_stock': random.randint(0, 1000)
            }
        )
        
        if created:
            produits_crees.append(produit)
            print(f"✅ Produit créé: {produit.nom_produit} - {prix} FC - Stock: {produit.quantite_stock}")
        else:
            print(f"⚠️ Produit existant: {produit.nom_produit}")
    
    return produits_crees

def main():
    """Fonction principale"""
    print("🚀 Début de l'insertion des données de test...")
    print("=" * 50)
    
    # Créer les fournisseurs
    print("\n📦 Création des fournisseurs...")
    fournisseurs = create_fournisseurs()
    print(f"✅ {len(fournisseurs)} fournisseurs traités")
    
    # Créer les produits
    print("\n💊 Création des produits...")
    produits = create_products()
    print(f"✅ {len(produits)} produits traités")
    
    print("\n" + "=" * 50)
    print("🎉 Insertion des données terminée avec succès!")
    print(f"📊 Résumé:")
    print(f"   - Fournisseurs: {Fournisseur.objects.count()}")
    print(f"   - Produits: {Produit.objects.count()}")
    print("=" * 50)

if __name__ == "__main__":
    main() 