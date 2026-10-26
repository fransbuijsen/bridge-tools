import csv
from pathlib import Path
import tempfile
import unittest

from maak_loopbriefjes import lees_schema, loopregels, schrijf_csv


ROOT = Path(__file__).resolve().parent


class LoopbriefjesTests(unittest.TestCase):
    def test_alle_windrichtingen(self):
        schema = [[((7, 3, 9, 5), "A")]]
        verwacht = {
            7: ("N", 3, "9 - 5"),
            3: ("Z", 7, "9 - 5"),
            9: ("O", 5, "7 - 3"),
            5: ("W", 9, "7 - 3"),
        }
        for speler, gegevens in verwacht.items():
            self.assertEqual(
                list(loopregels(speler, schema)),
                [[1, 1, "A", *gegevens]],
            )

    def test_rustbeurt(self):
        _, schema = lees_schema(ROOT / "05i05rInd++.txt")
        self.assertEqual(list(loopregels(3, schema))[0], [1, "", "", "Rust", "", ""])

    def test_numerieke_spelgroepen(self):
        for naam in ("16i15rPavlicek.opt.txt", "32i07rNBBopt.txt"):
            with self.subTest(naam=naam):
                _, schema = lees_schema(ROOT / naam)
                self.assertEqual(schema[0][0][1], "1")

    def test_csv_formaat(self):
        with tempfile.TemporaryDirectory() as mapnaam:
            pad = Path(mapnaam) / "voorbeeld.csv"
            schrijf_csv(pad, 5, [[((1, 2, 3, 4), "A")]])
            with pad.open(encoding="utf-8-sig", newline="") as bestand:
                regels = list(csv.reader(bestand, delimiter=";"))
            self.assertEqual(regels[:3], [
                ["Speler 1 (5 spelers)"], [],
                ["1", "1", "A", "N", "2", "3 - 4"],
            ])
            self.assertEqual(regels[-1], ["1", "", "", "Rust", "", ""])

    def test_ongeldige_invoer(self):
        for tekst in (
            "4 1 2 1 1\n1 2 3 4 A\n",
            "4 1 1 1 1\n1 2 3 A\n",
            "4 1 1 1 1\n1 1 3 4 A\n",
            "4 1 1 1 1\n1 2 3 5 A\n",
            "4 1 1 1 1\n1 2 3 4 B\n",
        ):
            with self.subTest(tekst=tekst), tempfile.TemporaryDirectory() as mapnaam:
                pad = Path(mapnaam) / "ongeldig.txt"
                pad.write_text(tekst, encoding="utf-8")
                with self.assertRaises(ValueError):
                    lees_schema(pad)

    def test_alle_schemas(self):
        bestanden = sorted(ROOT.glob("[0-9]*.txt"))
        self.assertTrue(bestanden)
        for pad in bestanden:
            with self.subTest(schema=pad.name):
                spelers, schema = lees_schema(pad)
                for speler in range(1, spelers + 1):
                    regels = list(loopregels(speler, schema))
                    self.assertEqual(len(regels), len(schema))
                    for ronde, tafel, groep, richting, partner, tegen in regels:
                        if richting == "Rust":
                            self.assertFalse(any(
                                speler in plaatsen for plaatsen, _ in schema[ronde - 1]
                            ))
                            continue
                        plaatsen, bron_groep = schema[ronde - 1][tafel - 1]
                        self.assertEqual(groep, bron_groep)
                        self.assertEqual(plaatsen[("N", "Z", "O", "W").index(richting)], speler)
                        self.assertEqual(
                            {speler, partner, *map(int, tegen.split(" - "))},
                            set(plaatsen),
                        )
                        partnerregel = list(loopregels(partner, schema))[ronde - 1]
                        self.assertEqual(partnerregel[4], speler)
                        self.assertEqual(partnerregel[5], tegen)


if __name__ == "__main__":
    unittest.main()
