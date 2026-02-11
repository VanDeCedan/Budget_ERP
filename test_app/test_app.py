import reflex as rx

def index() -> rx.Component:
    return rx.text("Test")

app = rx.App()
app.add_page(index)
