"""Zentrale, deterministische Auswahl fiktiver Demo-Bausteine."""
from .model import COMPANIES, Contract

DISCLAIMER = "Frei formulierter Demo-Text mit erfundenen Vertragsangaben. Dieses Dokument dient nur zur Vorführung der Software, ist keine Rechtsberatung und darf nicht als Arbeitsvertrag verwendet oder unterzeichnet werden."
REMUNERATION = {
    (False, False): "Fixgehalt",
    (True, False): "Fixgehalt + Provision",
    (False, True): "Fixgehalt + Bonus",
    (True, True): "Fixgehalt + Provision + Bonus",
}
OPTIONAL = {
    "mobile_work": ("Mobiles Arbeiten", "Erfundener Beispielsfall: Die ausgewählte Person arbeitet gelegentlich von einem anderen Ort. Dieser Demo-Baustein legt weder einen Anspruch noch konkrete Bedingungen fest."),
    "company_car": ("Dienstwagen", "Erfundener Beispielsfall: Für die ausgewählte Person wird ein Musterfahrzeug eingeplant. Die Vorführung enthält keine Regelung zur Fahrzeugüberlassung oder privaten Nutzung."),
    "blue_card": ("Blue-Card-Prüfhinweis", "Erfundener Beispielsfall: In der Eingabemaske wurde eine zusätzliche Prüfung zur Blue Card ausgewählt. Die Software prüft keine aufenthaltsrechtlichen Voraussetzungen und erteilt keine Beschäftigungsfreigabe."),
}


def eur(amount):
    return f"{amount:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".") + " €"


def sections(contract: Contract):
    if not isinstance(contract, Contract):
        raise TypeError("Ein validierter Vertrag ist erforderlich.")
    c = contract
    pay = f"Für die technische Vorführung wurde ein Jahresbruttogehalt von {eur(c.salary)} eingetragen. Der Betrag ist ein fiktiver Eingabewert und begründet keine Zahlungsverpflichtung."
    if c.commission:
        pay += f" Die ausgewählte Muster-Provision beträgt jährlich {eur(c.commission_amount)}. Berechnungs- oder Anspruchsregeln sind nicht Bestandteil dieser Demo."
    if c.bonus:
        pay += f" Der ausgewählte Muster-Bonus beträgt jährlich {eur(c.bonus_amount)}. Die Auswahl veranschaulicht lediglich einen zusätzlichen Textbaustein."
    result = [
        ("Vertragsparteien", f"Dieser Softwaretest verwendet {c.company} als erfundenes Unternehmen und {c.first_name} {c.last_name}, {c.street}, {c.postal_code} {c.city}, als erfundene Person. Die Angaben werden ausschließlich für diesen Musterentwurf zusammengestellt."),
        ("Eintritt und Tätigkeit", f"Die Demo zeigt den eingegebenen Musterbeginn {c.start_date:%d.%m.%Y} und die Musterposition {c.position}. Daraus entsteht kein Beschäftigungsverhältnis."),
        ("Vergütung – " + REMUNERATION[c.commission, c.bonus], pay),
    ]
    result.extend(clause for key, clause in OPTIONAL.items() if getattr(c, key))
    if COMPANIES[c.company]:
        result.append(("Betriebsvereinbarung", "Nur im erfundenen Beispielsfall Nordwerk Services GmbH erscheint dieser Zusatz. Er demonstriert eine bedingte Textauswahl; eine echte Betriebsvereinbarung wird weder wiedergegeben noch vorausgesetzt."))
    result.append(("Allgemeine Demo-Bestimmungen", "Alle Absätze dieses Musterentwurfs wurden für die Softwarevorführung frei formuliert. Sie bilden keinen vollständigen Vertrag und regeln keine arbeitsrechtlichen Ansprüche. Verwenden Sie ausschließlich erfundene Namen, Adressen und Beträge."))
    return result
