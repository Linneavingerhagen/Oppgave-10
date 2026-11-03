import csv
from datetime import datetime
from collections import defaultdict
from statistics import median
import matplotlib.pyplot as plt


# --------------------------------------------------
# LES DATA FRA CSV
# --------------------------------------------------

def les_tall(verdi):
    if verdi is None or verdi == "-" or verdi == "":
        return None
    return float(verdi.replace(",", "."))


def les_data(filnavn):
    data = []

    with open(filnavn, "r", encoding="utf-8-sig") as fil:
        leser = csv.DictReader(fil, delimiter=";")

        for rad in leser:
            if rad.get("Stasjon", "") == "":
                continue

            data.append({
                "dato": datetime.strptime(
                    rad["Tid(norsk normaltid)"],
                    "%d.%m.%Y"
                ),
                "maks_temp": les_tall(
                    rad["Maksimumstemperatur (døgn)"]
                ),
                "middeltemp": les_tall(
                    rad["Middeltemperatur (døgn)"]
                ),
                "nedbor": les_tall(
                    rad["Nedbør (døgn)"]
                ),
                "vind": les_tall(
                    rad["Høyeste middelvind (døgn)"]
                ),
                "snodybde": les_tall(
                    rad["Snødybde"]
                )
            })

    data.sort(key=lambda r: r["dato"])
    return data




# --------------------------------------------------
# HOVEDPROGRAM
# --------------------------------------------------

filer = {
    "Sinnes": "/Users/linneavingerhagen/Downloads/sinnes_2014_2025_med_makstemperatur.csv",
    "Oslo Blindern": "/Users/linneavingerhagen/Downloads/flere_vaerstasjoner_med_makstemperatur/oslo_blindern_1954_2025_med_makstemperatur.csv",
    "Røros": "/Users/linneavingerhagen/Downloads/flere_vaerstasjoner_med_makstemperatur/roeros_1954_2025_med_makstemperatur.csv",
    "Tromsø": "/Users/linneavingerhagen/Downloads/flere_vaerstasjoner_med_makstemperatur/tromsoe_1954_2025_med_makstemperatur.csv",
    "Værnes": "/Users/linneavingerhagen/Downloads/flere_vaerstasjoner_med_makstemperatur/vaernes_1954_2025_med_makstemperatur.csv",
    "Venabu": "/Users/linneavingerhagen/Downloads/flere_vaerstasjoner_med_makstemperatur/venabu_1954_2025_med_makstemperatur.csv"
}

datasett = {}

# Les inn data for alle filer som finnes
for navn, filnavn in filer.items():
    try:
        datasett[navn] = les_data(filnavn)
    except FileNotFoundError:
        pass

# Kjøring av enkeltoppgaver
if "Sinnes" in datasett:
    oppgave_a(datasett["Sinnes"])
    oppgave_d(datasett["Sinnes"])

if "Oslo Blindern" in datasett:
    oppgave_b(datasett["Oslo Blindern"])

# Kjøring av sammmenlikningsoppgaver for alle stasjoner
if datasett:
    oppgave_c(datasett)
    oppgave_e(datasett)
