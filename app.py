from fastapi import FastAPI
from controllers.load_file_controllers import router as LoadFileController


app = FastAPI()

app.include_router(LoadFileController)
