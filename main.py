from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from scanner_api import router as scanner_router
import importlib.util
import os
import sys
import traceback

app = FastAPI()

# Разрешаваме CORS за всички домейни
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://food-label-scanner.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/ping")
def ping():
    return {"status": "ok"}

@app.post("/run-script")
async def run_script(script_name: str = Form(...), function_name: str = Form(...), file: UploadFile = File(None)):
    try:
        script_path = os.path.join("scripts", script_name)
        if not os.path.exists(script_path):
            return {"error": f"Script '{script_name}' not found."}

        spec = importlib.util.spec_from_file_location("module.name", script_path)
        module = importlib.util.module_from_spec(spec)
        sys.modules["module.name"] = module
        spec.loader.exec_module(module)

        func = getattr(module, function_name, None)
        if not func:
            return {"error": f"Function '{function_name}' not found in '{script_name}'."}

        if file:
            result = func(file.file)
        else:
            result = func()

        return {"result": result}
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

app.include_router(scanner_router, prefix="/scanner", tags=["scanner"])
