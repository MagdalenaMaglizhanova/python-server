from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
import importlib.util
import os
import sys
import traceback

app = FastAPI()

# Разрешаваме CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # можеш да ограничиш към фронтенд домейна
    allow_methods=["*"],
    allow_headers=["*"]
)

# Тест ендпойнт
@app.get("/ping")
def ping():
    return {"status": "ok"}

# Универсален ендпойнт за изпълнение на Python скрипт от папка scripts
@app.post("/run-script")
async def run_script(script_name: str = Form(...), function_name: str = Form(...), file: UploadFile = File(None)):
    try:
        script_path = os.path.join("scripts", script_name)
        if not os.path.exists(script_path):
            return {"error": f"Script '{script_name}' not found."}

        # Зареждаме скрипта динамично
        spec = importlib.util.spec_from_file_location("module.name", script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["module.name"] = module
        spec.loader.exec_module(module)

        # Взимаме функцията
        func = getattr(module, function_name, None)
        if not func:
            return {"error": f"Function '{function_name}' not found in '{script_name}'."}

        # Ако има файл, подаден като аргумент
        if file:
            result = func(file.file)
        else:
            result = func()

        return {"result": result}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}
