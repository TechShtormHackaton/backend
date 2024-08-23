from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.staticfiles import StaticFiles
from controllers.load_file_controllers import router as LoadFileController


app = FastAPI()

app.include_router(LoadFileController)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.mount('/static', StaticFiles(directory='static'), name='static')
