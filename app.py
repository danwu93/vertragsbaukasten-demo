from datetime import date
from pathlib import Path
from html import escape
import streamlit as st

if globals().get("PUBLIC_DEMO_ENTRY") is not True:
    st.error("Diese Demo ausschließlich über demo.py starten.")
    st.stop()

from contract_builder.model import (
    ALL_FIELDS, TEXT_FIELDS, OPTIONS, LABELS, COMPANIES, ValidationError, build_contract,
)
from contract_builder.clauses import DISCLAIMER, eur
from contract_builder.document import generate_docx, filename

# Server configuration only: never take this decision from widget/query state.
PUBLIC_DEMO = True  # Public distribution: development mode cannot be enabled.

st.set_page_config(page_title="Vertragsbaukasten", page_icon="📄", layout="centered")
st.html("<style>" + Path(__file__).with_name("styles.css").read_text(encoding="utf-8") + "</style>")

def invalidate():
    st.session_state.pop("checked", None)
    st.session_state.pop("document", None)
    st.session_state["approved"] = False


def reset():
    for key in list(st.session_state):
        del st.session_state[key]


def hint(message):
    st.markdown('<small class="contract-hint">' + escape(message) + '</small>', unsafe_allow_html=True)


with st.container(key="contract_app", gap="xsmall"):
    st.title("Vertragsbaukasten")
    st.markdown("### Vom Auftrag zum Vertragsentwurf.")
    if not PUBLIC_DEMO:
        st.info(DISCLAIMER)
    if PUBLIC_DEMO:
        st.info("Demonstrationsanwendung mit fiktiven Vertragsbausteinen. Keine Rechtsberatung und keine produktive Vertragsvorlage.")
        st.button("Mit KI erstellen", disabled=True, key="ai_unavailable")
        hint("KI-Modus in der öffentlichen Demo nicht verfügbar")
        st.radio("Wie möchtest du beginnen?", ["Manuell erstellen"], horizontal=True, key="demo_mode")
        mode = "Manuell erstellen"
    st.subheader("2 · Angaben prüfen und ergänzen")
    hint("Alle Personen und Angaben müssen fiktiv sein. Beträge beziehen sich auf ein Jahr und sind in EUR.")
    for key in ALL_FIELDS:
        default = None if key in OPTIONS or key in ("company", "start_date") else ""
        st.session_state.setdefault("input_" + key, default)


    def text(key):
        return st.text_input(LABELS[key], key="input_" + key, on_change=invalidate)


    with st.container(border=True, key="person_details", gap="xsmall"):
        st.markdown("#### Personendaten")
        left, right = st.columns(2, gap="xsmall")
        with left:
            text("first_name")
        with right:
            text("last_name")
        text("street")
        left, right = st.columns([1, 2], gap="xsmall")
        with left:
            text("postal_code")
        with right:
            text("city")

    with st.container(border=True, key="contract_details", gap="xsmall"):
        st.markdown("#### Vertragsdaten")
        left, right = st.columns(2, gap="xsmall")
        with left:
            st.date_input("Eintrittsdatum", min_value=date(1900, 1, 1), max_value=date(2200, 12, 31), key="input_start_date", on_change=invalidate)
        with right:
            text("position")
        left, right = st.columns(2, gap="xsmall")
        with left:
            st.selectbox("Gesellschaft", list(COMPANIES), placeholder="Gesellschaft auswählen", key="input_company", on_change=invalidate)
        with right:
            text("salary")
        company = st.session_state.input_company
        if company:
            st.caption("Betriebsvereinbarungs-Baustein: " + ("enthalten" if COMPANIES[company] else "nicht enthalten"))

    with st.container(border=True, key="optional_details", gap="xsmall"):
        st.markdown("#### Optionale Vertragsbestandteile")
        for index in range(0, len(OPTIONS), 2):
            columns = st.columns(2, gap="xsmall")
            for column, option in zip(columns, OPTIONS[index:index + 2]):
                with column:
                    st.selectbox(LABELS[option], [None, True, False], format_func=lambda value: "Unbekannt / bitte auswählen" if value is None else "Ja" if value else "Nein", key="input_" + option, on_change=invalidate)
                    if option in ("commission", "bonus") and st.session_state["input_" + option] is True:
                        text(option + "_amount")

    raw = {key: st.session_state["input_" + key] for key in ALL_FIELDS}
    missing = [LABELS[key] for key in (*TEXT_FIELDS, "start_date", "salary", *OPTIONS) if raw[key] is None or raw[key] == ""]
    if missing:
        st.warning("Noch unbekannt oder unvollständig: " + ", ".join(missing))

    with st.container(key="review_actions"):
        review_column, reset_column = st.columns([1.2, 1])
        with review_column:
            review_clicked = st.button("Angaben prüfen und Zusammenfassung anzeigen", type="primary", use_container_width=True, key="review_contract")
        with reset_column:
            st.button("Eingaben und Entwurf verwerfen", on_click=reset, type="secondary", use_container_width=True)

    if review_clicked:
        invalidate()
        try:
            st.session_state.checked = build_contract(raw)
        except ValidationError as exc:
            for line in str(exc).splitlines():
                st.error(line)

    contract = st.session_state.get("checked")
    if contract:
        st.subheader("3 · Zusammenfassung und Export")
        summary = []
        for key in ALL_FIELDS:
            value = getattr(contract, key)
            if key in OPTIONS:
                value = "Ja" if value else "Nein"
            elif key.endswith("_amount") or key == "salary":
                value = eur(value) if value is not None else "Nicht ausgewählt"
            elif key == "start_date":
                value = value.strftime("%d.%m.%Y")
            summary.append({"Angabe": LABELS[key], "Wert": str(value)})
        st.table(summary)
        st.checkbox("Ich habe alle Angaben und Bausteine geprüft. Es sind ausschließlich fiktive Daten; ich bestätige die Erstellung des Demo-Dokuments.", key="approved")
        if st.session_state.get("approved"):
            if "document" not in st.session_state:
                st.session_state.document = generate_docx(contract)
            st.download_button(
                "Vertrag erstellen & herunterladen",
                data=st.session_state.document,
                file_name=filename(contract),
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                key="contract_download", type="primary", on_click="ignore",
                use_container_width=True,
            )

    hint("Keine Speicherung von Eingaben oder Dokumenten durch die Anwendung. Daten bleiben während der Sitzung im Speicher. Mit ‚Eingaben und Entwurf verwerfen‘ zurücksetzen; Downloads liegen anschließend lokal bei dir.")
