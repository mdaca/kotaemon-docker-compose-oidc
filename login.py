import hashlib

import gradio as gr
from ktem.app import BasePage
from ktem.db.models import User, engine
from sqlmodel import Session, select
from starlette.responses import RedirectResponse

fetch_creds = """
function() {
    const username = getStorage('username', '')
    const password = getStorage('password', '')
    return [username, password, null];
}
"""

signin_js = """
function(usn, pwd) {
    setStorage('username', usn);
    setStorage('password', pwd);
    return [usn, pwd];
}
"""


class LoginPage(BasePage):

    public_events = ["onSignIn"]

    def __init__(self, app):
        self._app = app
        self.on_building_ui()

    def on_building_ui(self):
        gr.Markdown(f"# Welcome to MDACA PrivateGPT!")
        self.usn = gr.Textbox(label="Username", visible=False)
        self.pwd = gr.Textbox(label="Password", type="password", visible=False)
        self.btn_login = gr.Button("Login", visible=False, elem_id="button")
        def greet(request: gr.Request):
            self.username = request.username
            return None
        with gr.Blocks() as main_demo:
            gr.Button("Logout", link="/logout")
            # Adding custom JavaScript to modify the page
            gr.HTML("""
            <script>
                function loginbuttonclick() {
                    document.getElementById("button").click();
                }
                window.onload = loginbuttonclick;
            </script>
            """)
            main_demo.load(greet, None, self.usn)


    def on_register_events(self):
        onSignIn = gr.on(
            triggers=[self.btn_login.click, self.pwd.submit],
            fn=self.login,
            inputs=[self.usn, self.pwd],
            outputs=[self._app.user_id, self.usn, self.pwd],
            show_progress="hidden",
            js=signin_js,
        ).then(
            self.toggle_login_visibility,
            inputs=[self._app.user_id],
            outputs=[self.usn, self.pwd, self.btn_login],
        )
        for event in self._app.get_event("onSignIn"):
            onSignIn = onSignIn.success(**event)

    def toggle_login_visibility(self, user_id):
        return (
            gr.update(visible=user_id is None),
            gr.update(visible=user_id is None),
            gr.update(visible=user_id is None),
        )

    def _on_app_created(self):
        onSignIn = self._app.app.load(
            self.login,
            inputs=[self.usn, self.pwd],
            outputs=[self._app.user_id, self.usn, self.pwd],
            show_progress="hidden",
            js=fetch_creds,
        ).then(
            self.toggle_login_visibility,
            inputs=[self._app.user_id],
            outputs=[self.usn, self.pwd, self.btn_login],
        )
        for event in self._app.get_event("onSignIn"):
            onSignIn = onSignIn.success(**event)

    def on_subscribe_public_events(self):
        self._app.subscribe_event(
            name="onSignOut",
            definition={
                "fn": self.toggle_login_visibility,
                "inputs": [self._app.user_id],
                "outputs": [self.usn, self.pwd, self.btn_login],
                "show_progress": "hidden",
            },
        )

    def login(self, usn, pwd):
        if not usn or not pwd:
            with Session(engine) as session:
                stmt = select(User).where(
                    User.username_lower == self.username.lower().strip()
                )
                result = session.exec(stmt).all()
                if result:
                    return result[0].id, "", ""

                gr.Warning("Invalid email address, please ask an admin to add you")
                return None, usn, pwd
        else:
            hashed_password = hashlib.sha256(pwd.encode()).hexdigest()
            with Session(engine) as session:
                stmt = select(User).where(
                    User.username_lower == usn.lower().strip(),
                    User.password == hashed_password,
                )
                result = session.exec(stmt).all()
                if result:
                    return result[0].id, "", ""

                gr.Warning("Invalid username or password")
