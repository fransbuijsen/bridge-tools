"""Maak per speelschema een CSV met een loopbriefje voor iedere speler."""

import argparse
import csv
from pathlib import Path


def lees_schema(pad):
    """Lees N, Z, O, W en spelgroep per tafel, in rondevolgorde."""
    regels = [
        regel.split(";", 1)[0].split()
        for regel in pad.read_text(encoding="utf-8-sig").splitlines()
    ]
    regels = [regel for regel in regels if regel]
    if not regels:
        raise ValueError(f"{pad.name}: leeg schema")
    header = regels[0]
    if len(header) not in (5, 6) or (len(header) == 6 and header[5] != "g"):
        raise ValueError(f"{pad.name}: ongeldige header")
    spelers, tafels, ronden, groepen, versie = map(int, header[:5])
    if min(spelers, tafels, ronden, groepen) < 1 or versie != 1:
        raise ValueError(f"{pad.name}: ongeldige aantallen of formaatversie")
    if len(regels) - 1 != ronden:
        raise ValueError(f"{pad.name}: verwacht {ronden} ronden")
    schema = []
    for ronde, regel in enumerate(regels[1:], 1):
        if len(regel) != tafels * 5:
            raise ValueError(f"{pad.name}: ronde {ronde}: onjuist aantal tafels")
        gezien = set()
        indeling = []
        for offset in range(0, len(regel), 5):
            plaatsen = tuple(map(int, regel[offset:offset + 4]))
            groep = regel[offset + 4]
            groepnummer = (
                int(groep) if groep.isdecimal()
                else ord(groep) - ord("A") + 1
                if len(groep) == 1 and "A" <= groep <= "Z"
                else 0
            )
            if not 1 <= groepnummer <= groepen:
                raise ValueError(f"{pad.name}: ronde {ronde}: ongeldige spelgroep")
            for speler in plaatsen:
                if not 1 <= speler <= spelers or speler in gezien:
                    raise ValueError(
                        f"{pad.name}: ronde {ronde}: ongeldig of dubbel "
                        f"spelernummer {speler}"
                    )
                gezien.add(speler)
            indeling.append((plaatsen, groep))
        schema.append(indeling)
    return spelers, schema


def loopregels(speler, schema):
    """Kolommen: ronde, tafel, spelgroep, richting, partner, tegenstanders."""
    for ronde, indeling in enumerate(schema, 1):
        for tafel, (plaatsen, groep) in enumerate(indeling, 1):
            if speler not in plaatsen:
                continue
            positie = plaatsen.index(speler)
            partner = plaatsen[positie ^ 1]
            tegenstanders = plaatsen[2:4] if positie < 2 else plaatsen[:2]
            yield [
                ronde, tafel, groep, ("N", "Z", "O", "W")[positie],
                partner, " - ".join(map(str, tegenstanders)),
            ]
            break
        else:
            yield [ronde, "", "", "Rust", "", ""]


def schrijf_csv(pad, spelers, schema):
    # Puntkomma's en een UTF-8-BOM maken openen in Nederlandstalig Excel eenvoudig.
    with pad.open("w", encoding="utf-8-sig", newline="") as bestand:
        schrijver = csv.writer(bestand, delimiter=";")
        for speler in range(1, spelers + 1):
            if speler > 1:
                schrijver.writerow([])
            schrijver.writerow([f"Speler {speler} ({spelers} spelers)"])
            schrijver.writerow([])
            schrijver.writerows(loopregels(speler, schema))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "schema", nargs="*", type=Path,
        help="TXT-bestanden; standaard alle schema's naast dit script",
    )
    parser.add_argument(
        "--uitvoer", type=Path,
        default=Path(__file__).resolve().parent / "loopbriefjes",
        help="Uitvoermap (standaard: loopbriefjes naast dit script)",
    )
    args = parser.parse_args()
    bestanden = args.schema or sorted(
        pad for pad in Path(__file__).resolve().parent.iterdir()
        if pad.suffix.lower() == ".txt" and pad.stem[:1].isdigit()
    )
    if not bestanden:
        parser.error("geen speelschema's gevonden")
    # Valideer alle invoer voordat uitvoerbestanden worden geschreven.
    try:
        schemas = [(pad, *lees_schema(pad)) for pad in bestanden]
    except (OSError, ValueError) as fout:
        parser.error(str(fout))
    args.uitvoer.mkdir(parents=True, exist_ok=True)
    for pad, spelers, schema in schemas:
        uitvoer = args.uitvoer / f"{pad.stem}.csv"
        schrijf_csv(uitvoer, spelers, schema)
        print(f"{uitvoer.name}: {spelers} spelers, {len(schema)} ronden")
    print(f"{len(schemas)} CSV-bestanden geschreven in {args.uitvoer}")


if __name__ == "__main__":
    main()
