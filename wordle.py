import re
from collections import Counter
import random
import math
import time

c = math.sqrt(2)
startwoorden = ["schot", "samen", "brits"]
pad = "pad_naar_woordenlijst.txt"

def laad_woordenlijst(pad):
    with open(pad, "r", encoding="utf-8") as bestand:
        alle_woorden = bestand.readlines()
   
    for i in range(len(alle_woorden)):
        alle_woorden[i] = alle_woorden[i].strip()
   
    return alle_woorden


def naief(woordenlijst, max_pogingen=6, eerste_gok=None, geheim=None):  
    if eerste_gok is None:
        gok = random.choice(woordenlijst)
    else:
        gok = eerste_gok.strip()
       
    if geheim is None:
        geheim = random.choice(woordenlijst)
    else:
        geheim = geheim.strip()
   
    mogelijke_geheimen = woordenlijst.copy()
    pogingen = []

    for poging in range(max_pogingen):
        pogingen.append(gok)
        fb = feedback(geheim, gok)
       
        if fb == "GGGGG":
            return {"succes": True, "pogingen": pogingen}
       
        # Filter de woordenlijst
        mogelijke_geheimen_nieuw = []
        for woord in mogelijke_geheimen:
            if woord != gok and woord_mogelijk(woord, gok, fb):
                mogelijke_geheimen_nieuw.append(woord)
       
        mogelijke_geheimen = mogelijke_geheimen_nieuw
       
        if not mogelijke_geheimen:
            return {"succes": False, "pogingen": pogingen}
       
        gok = random.choice(mogelijke_geheimen)
   
    # Maximum aantal pogingen bereikt
    return {"succes": False, "pogingen": pogingen}


class Node:
    def __init__(self, mogelijke_geheimen, gok_geschiedenis=None, ouder=None, laatste_gok=None):
        self.mogelijke_geheimen = mogelijke_geheimen.copy()
        self.gok_geschiedenis = gok_geschiedenis or []
        self.ouder = ouder
        self.laatste_gok = laatste_gok
       
        self.score = 0
        self.kinderen = {}
        self.bezoeken = 0
        self.mogelijke_gokken = None
   

    def get_mogelijke_gokken(self):
        """Krijg alle nog niet uitgeprobeerde gokken"""
        if self.mogelijke_gokken is None:
            gokken = []
       
            for woord in self.mogelijke_geheimen:
                if woord not in self.gok_geschiedenis:
                    gokken.append(woord)
       
            self.mogelijke_gokken = gokken
   
        return self.mogelijke_gokken
       

    def volledig_verkend(self):
        """Checkt of de node volledig verkend is (alle mogelijke gokken zijn geprobeerd)"""
        if len(self.get_mogelijke_gokken()) == 0:
            return True
        return False
   

    def eindnode(self):
        """Checkt of dit een terminal node is (het spel is afgelopen)"""
        if len(self.mogelijke_geheimen) <= 1 or len(self.gok_geschiedenis) >= 6:
            return True
        return False
       

    def selecteer_beste_kind(self, c=c):
        """Selecteer kind met hoogste UCB1 waarde"""
        if not self.kinderen:
             return None
   
        beste_kind = None
        hoogste_waarde = -math.inf
   
        for kind in self.kinderen.values():
            if kind.bezoeken == 0:
                beste_kind = kind
                return beste_kind  # Kies onverkende kinderen eerst
       
            gemiddelde_score = kind.score / kind.bezoeken
            verkenning_bonus = c * math.sqrt(math.log(self.bezoeken) / kind.bezoeken)
            ucb1 = gemiddelde_score + verkenning_bonus
       
            if ucb1 > hoogste_waarde:
                hoogste_waarde = ucb1
                beste_kind = kind
   
        return beste_kind
   
    
    def expand(self, gok):
        """Voegt een nieuwe child node toe voor gegeven gok"""
        if gok in self.kinderen:
            return self.kinderen[gok]
       
        nieuwe_poging = self.gok_geschiedenis + [gok]
       
        kind = Node(
            mogelijke_geheimen=self.mogelijke_geheimen,
            gok_geschiedenis=nieuwe_poging,
            ouder=self,
            laatste_gok=gok
        )
       
        self.kinderen[gok] = kind
        self.mogelijke_gokken.remove(gok)
        return kind
   
    
    def backpropagate(self, score):
        """Propageer score terug naar root"""
        self.bezoeken += 1
        self.score += score
        if self.ouder:
            self.ouder.backpropagate(score)


def mcts_wordle(woordenlijst, max_pogingen=6, eerste_gok=None, geheim=None, iteraties=10000, gamma=0.6):
    pogingen = []
   
    if geheim is None:
        geheim = random.choice(woordenlijst)
    else:
        geheim = geheim.strip()

    mogelijke_woorden = woordenlijst.copy()
   
    for poging_nummer in range(max_pogingen):
        # Als er een eerste gok wordt meegegeven als argument, gebruik dit als eerste gok
        if poging_nummer == 0 and eerste_gok is not None:
            huidige_gok = eerste_gok.strip()
        else:
            root = Node(mogelijke_woorden, gok_geschiedenis=pogingen.copy())
           
            for i in range(iteraties):
                # 1. SELECTIE: Navigeer naar beste leaf node
                node = root
                while not node.eindnode() and node.volledig_verkend():
                    beste_kind = node.selecteer_beste_kind()
                    if beste_kind is None:
                        break
                    node = beste_kind
               
                # 2. EXPANSIE: Als node niet terminaal is en niet volledig verkend: voeg nieuw kind toe
                if node is not None and not node.eindnode() and not node.volledig_verkend():
                    gokken_mogelijk = node.get_mogelijke_gokken()
                    if gokken_mogelijk:
                        gok = random.choice(gokken_mogelijk)
                        node = node.expand(gok)
               
                # 3. SIMULATIE (rollout): Speel random spel uit vanaf deze node
                if node is not None:
                    score = simulatie(node, max_pogingen - poging_nummer, woordenlijst, gamma)

                    # 4. BACKPROPAGATION: Update alle nodes in het pad
                    node.backpropagate(score)
           
            # Kies beste actie op basis van meeste bezoeken
            if root.kinderen:
                beste_gok = None
                meest_bezocht = 0

                for gok, kind in root.kinderen.items():
                    if kind.bezoeken > meest_bezocht:
                        meest_bezocht = kind.bezoeken
                        beste_gok = gok

                huidige_gok = beste_gok
            else:
                huidige_gok = random.choice(mogelijke_woorden)
       
        pogingen.append(huidige_gok)
        fb = feedback(geheim, huidige_gok)
       
        if fb == "GGGGG":
            return {"succes": True, "pogingen": pogingen}
       
        # Filter mogelijke woorden op basis van feedback
        nieuwe_mogelijke_woorden = []
        for woord in mogelijke_woorden:
            if woord != huidige_gok and woord_mogelijk(woord, huidige_gok, fb):
                nieuwe_mogelijke_woorden.append(woord)
       
        mogelijke_woorden = nieuwe_mogelijke_woorden
       
        if not mogelijke_woorden:
            return {"succes": False, "pogingen": pogingen}
   
    return {"succes": False, "pogingen": pogingen}


def simulatie(node, max_resterende_pogingen, woordenlijst, gamma=0.6):
    mogelijke_geheimen = node.mogelijke_geheimen.copy()
    pogingen_simulatie = node.gok_geschiedenis.copy()
    geheim_simulatie = random.choice(mogelijke_geheimen)
   
    for simulatie_poging in range(max_resterende_pogingen):
        beschikbare_gokken = []
        for woord in mogelijke_geheimen:
            if woord not in pogingen_simulatie:
                beschikbare_gokken.append(woord)
       
        if not beschikbare_gokken:
            return 0
           
        gok = random.choice(beschikbare_gokken)
        pogingen_simulatie.append(gok)
        fb = feedback(geheim_simulatie, gok)
        if fb == "GGGGG":
            return gamma ** simulatie_poging
    
        mogelijke_geheimen_nieuw = []
        for woord in mogelijke_geheimen:
            if woord != gok and woord_mogelijk(woord, gok, fb):
                mogelijke_geheimen_nieuw.append(woord)
               
        mogelijke_geheimen = mogelijke_geheimen_nieuw
   
    # Niet gevonden binnen max pogingen
    return -1


def feedback(geheim, gok):
    fb = ['B'] * 5
    geheim_letters = list(geheim)
    gok_letters = list(gok)
   
    # Groene letters (exacte matches)
    for i in range(5):
        if gok_letters[i] == geheim_letters[i]:
            fb[i] = 'G'
            geheim_letters[i] = None
            gok_letters[i] = None
   
    # Gele letters (verkeerde positie)
    for i in range(5):
        if gok_letters[i] is not None and gok_letters[i] in geheim_letters:
            fb[i] = 'Y'
            # Verwijder eerste voorkomen van letter uit geheim_letters
            geheim_letters[geheim_letters.index(gok_letters[i])] = None
   
    return ''.join(fb)


def woord_mogelijk(geheim, gok, fb):
    verwachte_feedback = feedback(geheim, gok)
    return verwachte_feedback == fb


def convert_tijd(seconden):
    if seconden < 60:
        return f"{seconden:.2f} seconden"
    elif seconden < 3600:
        minuten = seconden // 60
        seconden = seconden % 60
        return f"{int(minuten)} minuten en {round(seconden)} seconden"
    else:
        uren = seconden // 3600
        minuten = (seconden % 3600) // 60
        return f"{int(uren)} uur en {round(minuten)} minuten"
    

def evalueer(alg, woordenlijst, n=100, max_pogingen=6, eerste_gok=None, geheim=None, iteraties=10000, gamma=0.6):
    totaal_pogingen = 0
    succesvolle_spellen = 0
    mislukte_spellen = 0
    alg = alg.lower()

    if alg == "mcts":
        print(f"Iteraties: {iteraties}")
        print(f"C-waarde: {c}")
        print(f"Discount_factor: {gamma}")
    
    if eerste_gok != None:
        print(f"Eerste gok: {eerste_gok}")
    
    if geheim != None:
        print(f"Geheim woord: {geheim}")

    if n > 1:
        print(f"Evalueer {alg} algoritme voor {n} spellen...")
    else:
        print(f"Evalueer {alg} algoritme voor 1 spel...")

    start_alg = time.time()
   
    for i in range(n):
        start = time.time()
        if geheim is None:
            geheim_woord = random.choice(woordenlijst)
        else:
            geheim_woord = geheim
       
        if alg == "naief":
            resultaat = naief(woordenlijst, max_pogingen=max_pogingen, eerste_gok=eerste_gok, geheim=geheim_woord)
        elif alg == "mcts":
            if isinstance(eerste_gok, list):
                resultaat = mcts_wordle(woordenlijst, max_pogingen=max_pogingen, eerste_gok=random.choice(eerste_gok), geheim=geheim, iteraties=iteraties, gamma=gamma)
            else:
                resultaat = mcts_wordle(woordenlijst, max_pogingen=max_pogingen, eerste_gok=eerste_gok, geheim=geheim_woord, iteraties=iteraties, gamma=gamma)

        eind = time.time()
       
        succes = resultaat["succes"]
        pogingen = resultaat["pogingen"]
       
        if succes:
            aantal_pogingen = len(pogingen)
            totaal_pogingen += aantal_pogingen
            succesvolle_spellen += 1
            print(f"Spel {i+1}/{n}: '{geheim_woord}' geraden in {aantal_pogingen} pogingen ({eind - start:.2f} sec)")
        else:
            totaal_pogingen += 7
            mislukte_spellen += 1
            print(f"Spel {i+1}/{n}: '{geheim_woord}' NIET geraden ({eind - start:.2f} sec)")
    
    eind_alg = time.time()
    looptijd = eind_alg - start_alg
    ljust_afstand = 32
    gemiddelde_pogingen = totaal_pogingen / n

    print(f"\n{'='*100}")
    print(f"RESULTATEN {alg.upper()}")
    print(f"{'='*100}")
    print(f"{'Aantal woorden woordenlijst:'.ljust(ljust_afstand)} {len(woordenlijst)}")
    print(f"{'Totale looptijd:'.ljust(ljust_afstand)} {convert_tijd(looptijd)}")
    if eerste_gok != None:
        print(f"{'Eerste gok:'.ljust(ljust_afstand)} {eerste_gok}")
    print(f"{'Succespercentage:'.ljust(ljust_afstand)} {succesvolle_spellen}/{n} ({(succesvolle_spellen/n)*100:.1f}%)")
    print(f"{'Mislukte spellen:'.ljust(ljust_afstand)} {mislukte_spellen}")
    print(f"{'Gemiddelde aantal pogingen:'.ljust(ljust_afstand)} {gemiddelde_pogingen:.2f}")
    if alg == "mcts":
        print(f"{'Iteraties:'.ljust(ljust_afstand)} {iteraties}")
        print(f"{'c-waarde:'.ljust(ljust_afstand)} {c}")
        print(f"{'Discount_factor:'.ljust(ljust_afstand)}{gamma}")
    print(f"{'*'*100}")
    print(f"{'*'*100}")
   
    return {
        "succesvolle_spellen": succesvolle_spellen,
        "mislukte_spellen": mislukte_spellen,
        "gemiddelde_pogingen": gemiddelde_pogingen
    }
