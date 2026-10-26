# Vertragsbaukasten – öffentliche Demo

Manueller HR-Prototyp mit ausschließlich fiktiven Musterunternehmen und Vertragsbausteinen. Keine Rechtsberatung, keine produktive Vertragsvorlage.

## Streamlit Community Cloud

- Einstieg: `demo.py` im Repository-Hauptverzeichnis.
- Python: 3.13 (lokal geprüfte Version).
- Abhängigkeiten: `requirements.txt` (Streamlit 1.66.0, python-docx 1.2.0).
- Keine Secrets, Umgebungsvariablen, Postfach-Zugangsdaten oder Ollama-Installation erforderlich.
- Die App muss öffentlich zugänglich sein, damit die Portfolio-Einbettung funktioniert.

## Lokal starten

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m streamlit run demo.py --server.address 127.0.0.1
```

Nur fiktive Angaben erfassen, alle Optionen ausdrücklich auswählen, Zusammenfassung prüfen und bestätigen, DOCX herunterladen. Änderungen an Angaben verwerfen die vorherige Freigabe und den Download.

## Sicherheitsgrenze

Dieses Repository enthält nur die manuelle Oberfläche, Validierung, fiktive Klauseln, den Word-Generator und die erforderlichen Laufzeitdateien. KI-Extraktion, Mail-Listener, Mail-Transport, private Konfiguration, Zugangsdaten und Original-Projektverlauf sind nicht enthalten. Die öffentliche Distribution erzwingt den Demo-Modus auch in der gemeinsamen UI. Der KI-Button bleibt sichtbar deaktiviert.

Die Anwendung hält Eingaben und Dokumente im Sitzungsspeicher und schreibt keine Vertragsdaten dauerhaft auf den Server. Heruntergeladene Dateien liegen auf dem Gerät des Nutzers. Keine echten personenbezogenen Daten verwenden.
