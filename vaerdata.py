"""DAT120 øving 10, del 2: sammenlikning av flere værstasjoner (oppgave a-e).

Kjør:  python vaerdata.py
Legg csv-filene (semikolon-separert, desimalkomma) i samme mappe som dette
programmet, eller endre STASJONSFILER under. Figurene vises og lagres som png.
"""

import csv
import math
from datetime import date, datetime

import matplotlib.pyplot as plt

# ----------------------------------------------------------------------------
# Innstillinger
# ----------------------------------------------------------------------------
# Navn som vises i plottene -> filnavn. Legg gjerne til Sinnes fra øving 7 her
# (så lenge filen har samme kolonner).
STASJONSFILER = {
    "Oslo Blindern": "oslo_blindern_1954_2025_med_makstemperatur.csv",
    "Røros": "roeros_1954_2025_med_makstemperatur.csv",
    "Tromsø": "tromsoe_1954_2025_med_makstemperatur.csv",
    "Værnes": "vaernes_1954_2025_med_makstemperatur.csv",
    "Venabu": "venabu_1954_2025_med_makstemperatur.csv",
    "Sinnes": "sinnes_2014_2025 2.csv",   # fra øving 7 (ingen maks-temperatur)
}

MIN_DAGER_NEDBOR = 20      # a) minst så mange gyldige nedbørsmålinger i måneden
MIN_DAGER_AAR = 300        # b), c) minst så mange dager med data i året
STASJON_VIND = "Oslo Blindern"   # d) stasjon for min/median/maks vind
SKIFORE_GRENSE_CM = 20     # e) antatt: skiføre = snødybde på minst 20 cm
SESONG_START = (11, 1)     # e) skisesong: 1. november ...
SESONG_SLUTT = (5, 31)     # ... til 31. mai året etter (som i øving 7)


# ----------------------------------------------------------------------------
# Innlesing
# ----------------------------------------------------------------------------
def til_tall(tekst):
    """Gjør '12,3' om til 12.3. Manglende verdi ('-' eller tom) blir None."""
    tekst = tekst.strip()
    if tekst in ("", "-"):
        return None
    return float(tekst.replace(",", "."))


def les_stasjon(filnavn):
    """Leser en stasjonsfil og returnerer en liste med én ordbok per dag.

    Kolonnene hentes på navn, så filer uten maksimumstemperatur (som Sinnes)
    fungerer også: da blir 'tmax' None for alle dager."""
    dager = []
    with open(filnavn, encoding="utf-8-sig", newline="") as f:
        for rad in csv.DictReader(f, delimiter=";"):
            # Hopp over infolinjer og tomme linjer (tom 'Stasjon' eller ugyldig dato)
            if not rad.get("Stasjon"):
                continue
            try:
                dato = datetime.strptime(rad["Tid(norsk normaltid)"], "%d.%m.%Y").date()
            except (ValueError, KeyError, TypeError):
                continue
            dager.append({
                "dato": dato,
                "tmax": til_tall(rad.get("Maksimumstemperatur (døgn)") or "-"),
                "tmean": til_tall(rad.get("Middeltemperatur (døgn)") or "-"),
                "nedbor": til_tall(rad.get("Nedbør (døgn)") or "-"),
                "vind": til_tall(rad.get("Høyeste middelvind (døgn)") or "-"),
                "snø": til_tall(rad.get("Snødybde") or "-"),
            })
    # Noen filer har datoene i feil rekkefølge, så vi sorterer etter dato
    dager.sort(key=lambda d: d["dato"])
    return dager


def gyldige(verdier):
    """Fjerner None fra en liste."""
    return [v for v in verdier if v is not None]


def median(verdier):
    """Midterste verdi av sortert liste; snitt av de to midterste ved partall."""
    s = sorted(verdier)
    n = len(s)
    if n == 0:
        return None
    if n % 2 == 1:
        return s[n // 2]
    return (s[n // 2 - 1] + s[n // 2]) / 2


def gruppe_etter(dager, nokkelfunksjon):
    """Grupperer dagene i en ordbok: nøkkel -> liste av dager."""
    grupper = {}
    for dag in dager:
        grupper.setdefault(nokkelfunksjon(dag), []).append(dag)
    return grupper


def maks_eller_nan(verdier):
    v = gyldige(verdier)
    return max(v) if v else math.nan


def min_eller_nan(verdier):
    v = gyldige(verdier)
    return min(v) if v else math.nan


# ----------------------------------------------------------------------------
# a) Månedlige aggregater
# ----------------------------------------------------------------------------
def manedlige_verdier(dager):
    """Returnerer lister (måneder, maks snø, total nedbør, maks/min middeltemp,
    maks vind). NaN betyr ingen verdi, slik at plottet får et hull."""
    per_maned = gruppe_etter(dager, lambda d: (d["dato"].year, d["dato"].month))
    res = {"maned": [], "snø": [], "nedbor": [], "tmax": [], "tmin": [], "vind": []}
    for (aar, mnd) in sorted(per_maned):
        dgr = per_maned[(aar, mnd)]
        nedbor = gyldige([d["nedbor"] for d in dgr])
        res["maned"].append(date(aar, mnd, 1))
        res["snø"].append(maks_eller_nan([d["snø"] for d in dgr]))
        # Total nedbør bare om det er nok gyldige målinger
        res["nedbor"].append(sum(nedbor) if len(nedbor) > MIN_DAGER_NEDBOR else math.nan)
        res["tmax"].append(maks_eller_nan([d["tmean"] for d in dgr]))
        res["tmin"].append(min_eller_nan([d["tmean"] for d in dgr]))
        res["vind"].append(maks_eller_nan([d["vind"] for d in dgr]))
    return res


def plott_a(stasjoner):
    for navn, dager in stasjoner.items():
        r = manedlige_verdier(dager)
        fig, akser = plt.subplots(4, 1, figsize=(12, 10), sharex=True)
        akser[0].plot(r["maned"], r["snø"], color="tab:blue")
        akser[0].set_ylabel("Maks snødybde (cm)")
        akser[1].plot(r["maned"], r["nedbor"], color="tab:green")
        akser[1].set_ylabel("Total nedbør (mm)")
        akser[2].plot(r["maned"], r["tmax"], color="tab:red", label="Maks middeltemp.")
        akser[2].plot(r["maned"], r["tmin"], color="tab:purple", label="Min middeltemp.")
        akser[2].set_ylabel("Temperatur (°C)")
        akser[2].legend(loc="upper left")
        akser[3].plot(r["maned"], r["vind"], color="tab:orange")
        akser[3].set_ylabel("Maks middelvind (m/s)")
        akser[3].set_xlabel("År")
        for ax in akser:
            ax.grid(alpha=0.3)
        fig.suptitle(f"{navn}: månedlige verdier")
        fig.tight_layout()
        fig.savefig(f"a_maned_{navn.replace(' ', '_')}.png", dpi=120)


# ----------------------------------------------------------------------------
# b) Sommerdager, høysommerdager og tropedager pr. år
# ----------------------------------------------------------------------------
def antall_pr_aar(dager):
    """Teller dager med tmax over 20, 25 og 30 grader for hvert år med nok data."""
    per_aar = gruppe_etter(dager, lambda d: d["dato"].year)
    aar_liste, sommer, hoysommer, trope = [], [], [], []
    for aar in sorted(per_aar):
        tmax = gyldige([d["tmax"] for d in per_aar[aar]])
        if len(tmax) < MIN_DAGER_AAR:   # ufullstendig år gir misvisende tall
            continue
        aar_liste.append(aar)
        sommer.append(sum(1 for t in tmax if t > 20))
        hoysommer.append(sum(1 for t in tmax if t > 25))
        trope.append(sum(1 for t in tmax if t > 30))
    return aar_liste, sommer, hoysommer, trope


def plott_b(stasjoner):
    # Stasjoner uten maksimumstemperatur (Sinnes) kan ikke brukes her
    navn_liste = [n for n, d in stasjoner.items()
                  if any(x["tmax"] is not None for x in d)]
    fig, akser = plt.subplots(len(navn_liste), 1, figsize=(12, 3.2 * len(navn_liste)),
                              sharex=True)
    for ax, navn in zip(akser, navn_liste):
        aar, s, h, t = antall_pr_aar(stasjoner[navn])
        ax.plot(aar, s, label="Sommerdager (>20 °C)", color="gold")
        ax.plot(aar, h, label="Høysommerdager (>25 °C)", color="tab:orange")
        ax.plot(aar, t, label="Tropedager (>30 °C)", color="tab:red")
        ax.set_title(navn)
        ax.set_ylabel("Antall dager")
        ax.grid(alpha=0.3)
        ax.legend(loc="upper left", fontsize=8)
    akser[-1].set_xlabel("År")
    fig.tight_layout()
    fig.savefig("b_sommerdager.png", dpi=120)


# ----------------------------------------------------------------------------
# c) Årlig gjennomsnittstemperatur
# ----------------------------------------------------------------------------
def aarsmiddel(dager):
    per_aar = gruppe_etter(dager, lambda d: d["dato"].year)
    aar_liste, snitt = [], []
    for aar in sorted(per_aar):
        temp = gyldige([d["tmean"] for d in per_aar[aar]])
        if len(temp) >= MIN_DAGER_AAR:
            aar_liste.append(aar)
            snitt.append(sum(temp) / len(temp))
    return aar_liste, snitt


def plott_c(stasjoner):
    plt.figure(figsize=(12, 6))
    for navn, dager in stasjoner.items():
        aar, snitt = aarsmiddel(dager)
        plt.plot(aar, snitt, label=navn)
    plt.xlabel("År")
    plt.ylabel("Gjennomsnittstemperatur (°C)")
    plt.title("Årlig gjennomsnittstemperatur")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("c_aarsmiddel.png", dpi=120)


# ----------------------------------------------------------------------------
# d) Min, median og maks vind pr. kalendermåned (alle år samlet)
# ----------------------------------------------------------------------------
def vindstatistikk(dager):
    per_maned = gruppe_etter(dager, lambda d: d["dato"].month)
    mnd, lav, med, hoy = [], [], [], []
    for m in range(1, 13):
        vind = gyldige([d["vind"] for d in per_maned.get(m, [])])
        if vind:
            mnd.append(m)
            lav.append(min(vind))
            med.append(median(vind))
            hoy.append(max(vind))
    return mnd, lav, med, hoy


def plott_d(stasjoner, navn):
    mnd, lav, med, hoy = vindstatistikk(stasjoner[navn])
    plt.figure(figsize=(9, 5))
    plt.plot(mnd, lav, marker="o", label="Minimum")
    plt.plot(mnd, med, marker="o", label="Median")
    plt.plot(mnd, hoy, marker="o", label="Maksimum")
    plt.xticks(range(1, 13), ["jan", "feb", "mar", "apr", "mai", "jun",
                              "jul", "aug", "sep", "okt", "nov", "des"])
    plt.ylabel("Høyeste middelvind (m/s)")
    plt.title(f"{navn}: vindstyrke pr. måned (alle år)")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("d_vind.png", dpi=120)


# ----------------------------------------------------------------------------
# e) Skisesonger
# ----------------------------------------------------------------------------
def skidager_pr_sesong(dager):
    """Sesongen 'år' går fra 1. nov år til 31. mai år+1.
    Returnerer sesongstart-år og antall dager med snødybde >= grensen."""
    def sesong(d):
        dt = d["dato"]
        start = date(dt.year, *SESONG_START)
        if dt >= start:
            return dt.year
        if dt <= date(dt.year, *SESONG_SLUTT):
            return dt.year - 1
        return None  # utenfor sesong

    per_sesong = gruppe_etter([d for d in dager if sesong(d) is not None], sesong)
    forste_dato = dager[0]["dato"]
    sesonger, antall = [], []
    for aar in sorted(per_sesong):
        if date(aar, *SESONG_START) < forste_dato:
            continue  # sesongen startet før dataene begynner (delvis sesong)
        lengde = (date(aar + 1, *SESONG_SLUTT) - date(aar, *SESONG_START)).days + 1
        snø = gyldige([d["snø"] for d in per_sesong[aar]])
        if len(snø) >= lengde / 2:   # data for minst halvparten av dagene
            sesonger.append(aar)
            antall.append(sum(1 for s in snø if s >= SKIFORE_GRENSE_CM))
    return sesonger, antall


def plott_e(stasjoner):
    plt.figure(figsize=(12, 6))
    for navn, dager in stasjoner.items():
        sesonger, antall = skidager_pr_sesong(dager)
        plt.plot(sesonger, antall, label=navn)
    plt.xlabel("Sesongstart (1. november dette året til 31. mai neste år)")
    plt.ylabel(f"Dager med snødybde ≥ {SKIFORE_GRENSE_CM} cm")
    plt.title("Antall dager med skiføre pr. sesong")
    plt.grid(alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig("e_skisesonger.png", dpi=120)


# ----------------------------------------------------------------------------
def main():
    stasjoner = {navn: les_stasjon(fil) for navn, fil in STASJONSFILER.items()}
    for navn, dager in stasjoner.items():
        print(f"{navn}: {len(dager)} dager, {dager[0]['dato']} – {dager[-1]['dato']}")

    plott_a(stasjoner)
    plott_b(stasjoner)
    plott_c(stasjoner)
    plott_d(stasjoner, STASJON_VIND)
    plott_e(stasjoner)
    plt.show()


if __name__ == "__main__":
    main()
