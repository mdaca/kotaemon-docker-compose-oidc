import os
import subprocess
import sys

from theflow.settings import settings as flowsettings

KH_APP_DATA_DIR = getattr(flowsettings, "KH_APP_DATA_DIR", ".")
GRADIO_TEMP_DIR = os.getenv("GRADIO_TEMP_DIR", None)
# override GRADIO_TEMP_DIR if it's not set
if GRADIO_TEMP_DIR is None:
    GRADIO_TEMP_DIR = os.path.join(KH_APP_DATA_DIR, "gradio_tmp")
    os.environ["GRADIO_TEMP_DIR"] = GRADIO_TEMP_DIR


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])
install('Authlib')
install('itsdangerous')


from ktem.main import App  # noqa
from authlib.integrations.starlette_client import OAuth, OAuthError
from fastapi import FastAPI, Depends, Request
from starlette.config import Config
from starlette.responses import RedirectResponse
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import gradio as gr

app = FastAPI()

# Replace these with your own OAuth settings
GOOGLE_CLIENT_ID = os.getenv("OPENID_CLIENT_ID", None)
GOOGLE_CLIENT_SECRET = os.getenv("OPENID_CLIENT_SECRET", None)
SECRET_KEY = os.getenv("SECRET_KEY", None)
CONFIG_URL = os.getenv("OPENID_CONFIG_URL", None)

config_data = {'GOOGLE_CLIENT_ID': GOOGLE_CLIENT_ID, 'GOOGLE_CLIENT_SECRET': GOOGLE_CLIENT_SECRET}
starlette_config = Config(environ=config_data)
oauth = OAuth(starlette_config)
oauth.register(
    name='google',
    server_metadata_url=CONFIG_URL,
    client_kwargs={'scope': 'openid email profile'},
)

SECRET_KEY = os.environ.get('SECRET_KEY') or "(SF88bvs8bs9b797hgest325/23%R@%V*#@*%VJ@#5rv325)"
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Dependency to get the current user
def get_user(request: Request):
    user = request.session.get('user')
    if user:
        return user['email']
    return None

@app.get('/favicon.ico', include_in_schema=False)
async def favicon():
    return FileResponse(ktemApp._favicon)

@app.get('/')
def public(user: dict = Depends(get_user)):
    if user:
        return RedirectResponse(url='/mdaca-privategpt')
    else:
        return RedirectResponse(url='/login-landing')

@app.route('/logout')
async def logout(request: Request):
    request.session.pop('user', None)
    return RedirectResponse(url='/')

@app.route('/login')
async def login(request: Request):
    redirect_uri = request.url_for('auth')
    # If your app is running on https, you should ensure that the
    # `redirect_uri` is https, e.g. uncomment the following lines:
    # 
    # from urllib.parse import urlparse, urlunparse
    # redirect_uri = urlunparse(urlparse(str(redirect_uri))._replace(scheme='https'))
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.route('/auth')
async def auth(request: Request):
    try:
        access_token = await oauth.google.authorize_access_token(request)
    except OAuthError:
        return RedirectResponse(url='/')
    request.session['user'] = dict(access_token)["userinfo"]
    return RedirectResponse(url='/')

with gr.Blocks() as login_demo:
    gr.Markdown(f"# Welcome to MDACA PrivateGPT!")
    gr.Button("Login", link="/login")

app = gr.mount_gradio_app(app, login_demo, path="/login-landing")

ktemApp = App()
main_demo = ktemApp.make()

app = gr.mount_gradio_app(app, main_demo, path="/mdaca-privategpt", auth_dependency=get_user, allowed_paths=["libs/ktem/ktem/assets",
    GRADIO_TEMP_DIR
    ])

uvicorn.run(app, host='0.0.0.0', port=8000)