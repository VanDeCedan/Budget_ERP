import reflex as rx
from ...state.request_state import RequestState

def new_request_form_content() -> rx.Component:
    return rx.vstack(
        rx.text("Informations Générales", font_size="0.8em", font_weight="bold", color="gray"),
        rx.hstack(
            rx.select(
                RequestState.issuer_options,
                placeholder="Demandeur",
                value=RequestState.issuer_id,
                on_change=RequestState.set_issuer_id,
                width="50%",
                size="1"
            ),
            rx.select(
                ["Voyage", "Achat"],
                placeholder="Type de requête",
                value=RequestState.request_type,
                on_change=RequestState.set_request_type,
                width="50%",
                size="1"
            ),
            width="100%",
        ),
        rx.text_area(
            placeholder="Objet", 
            value=RequestState.object, 
            on_change=RequestState.set_object,
            width="100%",
            size="1"
        ),
        spacing="2",
        width="100%",
    )
