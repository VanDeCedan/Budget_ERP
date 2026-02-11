import reflex as rx
from ...state.request_state import RequestState

def complementary_request_form_content() -> rx.Component:
    return rx.vstack(
        rx.text("Informations Générales", font_size="0.8em", font_weight="bold", color="gray"),
        rx.select(
            RequestState.issuer_options,
            placeholder="Demandeur",
            value=RequestState.comp_filter_issuer,
            on_change=RequestState.set_comp_filter_issuer,
            width="100%",
            size="1"
        ),
        rx.select(
            RequestState.initial_sub_request_options,
            placeholder="Requête initiale",
            value=RequestState.selected_initial_id,
            on_change=RequestState.set_selected_initial_id,
            width="100%",
            size="1"
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
