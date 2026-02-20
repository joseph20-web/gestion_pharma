#!/usr/bin/env python
"""
Script pour générer 10 clients avec des données réalistes
"""

import os
import sys
import django
import random
from datetime import date, timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'APPRO.settings')
django.setup()

from CAHMS.models import Personne, Client

def generate_clients():
    """Générer 10 clients avec des données réalistes"""
    
    # Noms et prénoms congolais réalistes
    noms = [
        "Mukendi", "Lubaki", "Tshibanda", "Kazadi", "Mpunga",
        "Banza", "Kabasele", "Mukeba", "Tshilombo", "Kambala",
        "Luboya", "Mukenge", "Tshibangu", "Kazumba", "Mpata",
        "Banza", "Kabasele", "Mukeba", "Tshilombo", "Kambala"
    ]
    
    prenoms_masculins = [
        "Jean", "Pierre", "Paul", "André", "Michel",
        "Joseph", "François", "Charles", "David", "Patrick",
        "Emmanuel", "Christian", "Roger", "Albert", "Marcel",
        "Théophile", "Gustave", "Léon", "Victor", "Henri"
    ]
    
    prenoms_feminins = [
        "Marie", "Jeanne", "Louise", "Sophie", "Anne",
        "Catherine", "Françoise", "Madeleine", "Thérèse", "Claire",
        "Monique", "Brigitte", "Christine", "Isabelle", "Martine",
        "Suzanne", "Colette", "Nicole", "Danielle", "Hélène"
    ]
    
    postnoms = [
        "Mukendi", "Lubaki", "Tshibanda", "Kazadi", "Mpunga",
        "Banza", "Kabasele", "Mukeba", "Tshilombo", "Kambala",
        "Luboya", "Mukenge", "Tshibangu", "Kazumba", "Mpata",
        "Banza", "Kabasele", "Mukeba", "Tshilombo", "Kambala"
    ]
    
    print("👥 Génération de 10 clients")
    print("=" * 50)
    
    clients_crees = 0
    
    for i in range(10):
        # Choisir aléatoirement le sexe
        sexe = random.choice(['M', 'F'])
        
        # Choisir prénom selon le sexe
        if sexe == 'M':
            prenom = random.choice(prenoms_masculins)
        else:
            prenom = random.choice(prenoms_feminins)
        
        # Choisir nom et postnom
        nom = random.choice(noms)
        postnom = random.choice(postnoms)
        
        # Générer date de naissance (entre 18 et 80 ans)
        age = random.randint(18, 80)
        date_naissance = date.today() - timedelta(days=age*365 + random.randint(0, 365))
        
        # Créer la personne
        personne = Personne.objects.create(
            nom=nom,
            postnom=postnom,
            prenom=prenom,
            sexe=sexe,
            date_naissance=date_naissance,
            est_actif=True
        )
        
        # Créer le client
        client = Client.objects.create(
            personne=personne
        )
        
        clients_crees += 1
        
        # Afficher les informations
        sexe_text = "Masculin" if sexe == 'M' else "Féminin"
        print(f"✅ Client {clients_crees}: {prenom} {nom} {postnom}")
        print(f"   Sexe: {sexe_text}")
        print(f"   Date de naissance: {date_naissance.strftime('%d/%m/%Y')}")
        print(f"   Âge: {age} ans")
        print()
    
    print("=" * 50)
    print(f"🎉 Génération terminée!")
    print(f"📊 {clients_crees} clients créés avec succès")
    print("=" * 50)
    
    # Afficher la liste complète
    print("\n📋 Liste complète des clients:")
    print("-" * 50)
    clients = Client.objects.all().order_by('personne__nom', 'personne__prenom')
    
    for i, client in enumerate(clients, 1):
        personne = client.personne
        sexe_text = "M" if personne.sexe == 'M' else "F"
        print(f"{i:2d}. {personne.prenom} {personne.nom} {personne.postnom} ({sexe_text})")
    
    print("-" * 50)
    print(f"Total: {clients.count()} clients")

def main():
    """Fonction principale"""
    print("👥 Générateur de Clients")
    print("Création de 10 clients avec des données réalistes")
    print()
    
    # Vérifier s'il y a déjà des clients
    clients_existants = Client.objects.count()
    if clients_existants > 0:
        print(f"⚠️  Attention: {clients_existants} client(s) existent déjà")
        reponse = input("Voulez-vous continuer et ajouter 10 nouveaux clients? (oui/non): ").lower().strip()
        
        if reponse not in ['oui', 'o', 'yes', 'y']:
            print("❌ Opération annulée")
            return
    
    # Demander confirmation
    reponse = input("Voulez-vous générer 10 nouveaux clients? (oui/non): ").lower().strip()
    
    if reponse in ['oui', 'o', 'yes', 'y']:
        generate_clients()
    else:
        print("❌ Opération annulée")

if __name__ == "__main__":
    main() 