"""Gemeinsames Datenmodell und Validierung für beide Eingabewege."""
from dataclasses import dataclass, fields
from datetime import date
from decimal import Decimal, InvalidOperation
import re


COMPANIES = {
    "Nordwerk GmbH": False,
    "Nordwerk Services GmbH": True,
    "Nordwerk Digital GmbH": False,
}
TEXT_FIELDS = ("first_name", "last_name", "street", "postal_code", "city", "position", "company")
OPTIONS = ("commission", "bonus", "mobile_work", "company_car", "blue_card")
MONEY_FIELDS = ("salary", "commission_amount", "bonus_amount")
LABELS = {
    "first_name": "Vorname", "last_name": "Nachname", "street": "Straße und Hausnummer",
    "postal_code": "Postleitzahl", "city": "Ort", "position": "Position",
    "company": "Gesellschaft", "start_date": "Eintrittsdatum", "salary": "Jahresbruttogehalt",
    "commission": "Provision", "commission_amount": "Provisionshöhe",
    "bonus": "Bonus", "bonus_amount": "Bonushöhe", "mobile_work": "Mobiles Arbeiten",
    "company_car": "Dienstwagen", "blue_card": "Blue Card",
}


class ValidationError(ValueError):
    pass


def money(value):
    """EUR: Dezimalpunkt oder eindeutig gruppiertes deutsches Betragsformat."""
    if value is None or isinstance(value, bool):
        raise ValidationError("Betrag fehlt oder ist ungültig.")
    if isinstance(value, (int, float, Decimal)):
        result = Decimal(str(value))
        if not result.is_finite() or not 0 < result <= Decimal("999999999.99") or result.as_tuple().exponent < -2:
            raise ValidationError("Betrag muss positiv sein und höchstens zwei Nachkommastellen haben.")
        return result.quantize(Decimal("0.01"))
    text = str(value).strip().replace("€", "").strip()
    if re.fullmatch(r"\d{1,3}(?:\.\d{3})+(?:,\d{1,2})?", text):
        text = text.replace(".", "").replace(",", ".")
    elif re.fullmatch(r"\d+(?:[.,]\d{1,2})?", text):
        text = text.replace(",", ".")
    else:
        raise ValidationError("Betrag ungültig; zum Beispiel 55000 oder 55.000,00 eingeben.")
    try:
        result = Decimal(text)
    except InvalidOperation as exc:
        raise ValidationError("Betrag ungültig.") from exc
    if not result.is_finite() or not 0 < result <= Decimal("999999999.99"):
        raise ValidationError("Betrag muss positiv sein und darf 999.999.999,99 € nicht überschreiten.")
    return result.quantize(Decimal("0.01"))


def parse_date(value):
    if type(value) is date:
        result = value
    else:
        if not isinstance(value, str) or not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValidationError("Eintrittsdatum muss ein gültiges Datum im Format JJJJ-MM-TT sein.")
        try:
            result = date.fromisoformat(value)
        except ValueError as exc:
            raise ValidationError("Eintrittsdatum muss ein gültiges Datum im Format JJJJ-MM-TT sein.") from exc
    if not date(1900, 1, 1) <= result <= date(2200, 12, 31):
        raise ValidationError("Eintrittsdatum muss zwischen 1900 und 2200 liegen.")
    return result


@dataclass(frozen=True)
class Contract:
    first_name: str
    last_name: str
    street: str
    postal_code: str
    city: str
    start_date: date
    position: str
    company: str
    salary: Decimal
    commission: bool
    bonus: bool
    mobile_work: bool
    company_car: bool
    blue_card: bool
    commission_amount: Decimal | None = None
    bonus_amount: Decimal | None = None

    def __post_init__(self):
        errors = []
        for key in TEXT_FIELDS:
            value = getattr(self, key)
            if not isinstance(value, str) or not value.strip() or len(value) > 200 or any(ord(c) < 32 for c in value):
                errors.append(f"{LABELS[key]} fehlt oder ist ungültig (maximal 200 Zeichen).")
        if self.company not in COMPANIES:
            errors.append("Bitte eine der drei Demo-Gesellschaften auswählen.")
        if not isinstance(self.postal_code, str) or not re.fullmatch(r"\d{5}", self.postal_code):
            errors.append("Postleitzahl muss aus fünf Ziffern bestehen.")
        if isinstance(self.street, str) and not re.search(r"\d", self.street):
            errors.append("Straße einschließlich Hausnummer angeben.")
        try:
            if type(self.start_date) is not date:
                raise ValidationError("Eintrittsdatum fehlt oder ist ungültig.")
            parse_date(self.start_date)
        except ValidationError as exc:
            errors.append(str(exc))
        for key in OPTIONS:
            if type(getattr(self, key)) is not bool:
                errors.append(f"{LABELS[key]}: Bitte ausdrücklich Ja oder Nein auswählen.")
        for key in MONEY_FIELDS:
            value = getattr(self, key)
            needed = key == "salary" or getattr(self, key.removesuffix("_amount")) is True
            if needed:
                if not isinstance(value, Decimal) or not value.is_finite() or value <= 0 or value > Decimal("999999999.99") or value.as_tuple().exponent < -2:
                    errors.append(f"{LABELS[key]}: gültigen positiven Betrag mit maximal zwei Nachkommastellen angeben.")
            elif value is not None:
                errors.append(f"{LABELS[key]} darf nur bei ausgewähltem Baustein angegeben werden.")
        if errors:
            raise ValidationError("\n".join(errors))


def build_contract(raw):
    values = {}
    errors = []
    for key in TEXT_FIELDS:
        value = raw.get(key)
        values[key] = value.strip() if isinstance(value, str) else value
    for key in OPTIONS:
        values[key] = raw.get(key)
    try:
        values["start_date"] = parse_date(raw.get("start_date"))
    except ValidationError as exc:
        errors.append(str(exc))
    for key in MONEY_FIELDS:
        needed = key == "salary" or raw.get(key.removesuffix("_amount")) is True
        try:
            values[key] = money(raw.get(key)) if needed else None
        except ValidationError as exc:
            errors.append(f"{LABELS[key]}: {exc}")
    if errors:
        raise ValidationError("\n".join(errors))
    return Contract(**values)


ALL_FIELDS = tuple(field.name for field in fields(Contract))
