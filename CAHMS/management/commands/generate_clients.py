from django.core.management.base import BaseCommand
import random
from datetime import date, timedelta
from CAHMS.models import Personne, Client

class Command(BaseCommand):
    help = 'Générer 10 clients avec des données réalistes'

    def add_arguments(self, parser):
        parser.add_argument(
            '--count',
            type=int,
            default=10,
            help='Nombre de clients à générer (défaut: 10)',
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forcer la génération sans demander confirmation',
        )

    def handle(self, *args, **options):
        count = options['count']
        force = options['force']
        
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
        
        if not force:
            # Vérifier s'il y a déjà des clients
            clients_existants = Client.objects.count()
            if clients_existants > 0:
                self.stdout.write(
                    self.style.WARNING(f'⚠️  Attention: {clients_existants} client(s) existent déjà')
                )
                reponse = input("Voulez-vous continuer et ajouter de nouveaux clients? (oui/non): ").lower().strip()
                
                if reponse not in ['oui', 'o', 'yes', 'y']:
                    self.stdout.write(
                        self.style.ERROR('❌ Opération annulée')
                    )
                    return
            
            # Demander confirmation
            reponse = input(f"Voulez-vous générer {count} nouveaux clients? (oui/non): ").lower().strip()
            
            if reponse not in ['oui', 'o', 'yes', 'y']:
                self.stdout.write(
                    self.style.ERROR('❌ Opération annulée')
                )
                return
        
        self.stdout.write(
            self.style.SUCCESS(f'👥 Génération de {count} clients')
        )
        self.stdout.write('=' * 50)
        
        clients_crees = 0
        
        for i in range(count):
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
            self.stdout.write(
                self.style.SUCCESS(f'✅ Client {clients_crees}: {prenom} {nom} {postnom}')
            )
            self.stdout.write(f'   Sexe: {sexe_text}')
            self.stdout.write(f'   Date de naissance: {date_naissance.strftime("%d/%m/%Y")}')
            self.stdout.write(f'   Âge: {age} ans')
            self.stdout.write('')
        
        self.stdout.write('=' * 50)
        self.stdout.write(
            self.style.SUCCESS(f'🎉 Génération terminée!')
        )
        self.stdout.write(f'📊 {clients_crees} clients créés avec succès')
        self.stdout.write('=' * 50)
        
        # Afficher la liste complète
        self.stdout.write('\n📋 Liste complète des clients:')
        self.stdout.write('-' * 50)
        clients = Client.objects.all().order_by('personne__nom', 'personne__prenom')
        
        for i, client in enumerate(clients, 1):
            personne = client.personne
            sexe_text = "M" if personne.sexe == 'M' else "F"
            self.stdout.write(f'{i:2d}. {personne.prenom} {personne.nom} {personne.postnom} ({sexe_text})')
        
        self.stdout.write('-' * 50)
        self.stdout.write(f'Total: {clients.count()} clients') 