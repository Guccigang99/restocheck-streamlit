# RestoCheck Streamlit App

Multi-restaurant wettelijke roostercontrole.

## Start lokaal

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Fase 1 bevat

- Taalkeuze NL / FR / EN
- Restaurant toevoegen, bewerken en verwijderen
- Restaurant selecteren voor je verder kan
- Crew toevoegen via formulier
- Geboortedatum opgeslagen, leeftijd dagelijks automatisch berekend
- Statuut: student / vast / flexi / interim
- Contracturen verplicht bij statuut vast
- SQLite database in `data/restocheck.db`

## Volgende fase

- Bestaande wettelijke controlelogica toevoegen
- Bestaande gemarkeerde Excel-export behouden
