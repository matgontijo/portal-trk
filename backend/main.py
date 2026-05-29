from fastapi import FastAPI, Depends, HTTPException, Body
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
import requests
import json
import os

from database import engine, get_db, Base
import models

# Criar tabelas no banco de dados SQLite local
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="Portal TRK Backend")

# ── ROTAS DA API ──

@app.get("/api/empresas/omie-keys/{empresa_id}")
def get_omie_keys(empresa_id: str, db: Session = Depends(get_db)):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if empresa and empresa.omie_app_key:
        return {"has_keys": True, "app_key": empresa.omie_app_key, "app_secret": "********"}
    return {"has_keys": False}

@app.post("/api/empresas/omie-keys")
def save_omie_keys(empresa_id: str = Body(...), app_key: str = Body(...), app_secret: str = Body(...), db: Session = Depends(get_db)):
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    if not empresa:
        # Se a empresa não existe ainda no SQLite, vamos criá-la
        empresa = models.Empresa(id=empresa_id)
        db.add(empresa)
    
    empresa.omie_app_key = app_key
    empresa.omie_app_secret = app_secret
    db.commit()
    return {"message": "Chaves salvas com sucesso!"}

@app.post("/api/omie/conciliar")
def auto_conciliar_omie(empresa_id: str = Body(...), db: Session = Depends(get_db)):
    """
    Simula uma requisição real para o Omie para obter contas a pagar.
    """
    empresa = db.query(models.Empresa).filter(models.Empresa.id == empresa_id).first()
    
    if not empresa or not empresa.omie_app_key or not empresa.omie_app_secret:
        # Erro customizado nosso se a chave não estiver no BD
        return {"status": "erro", "detalhe": "Chaves do Omie não cadastradas para esta empresa no banco de dados local."}

    # Endpoint real do Omie para testarmos se a chave bate
    url = "https://app.omie.com.br/api/v1/financas/contapagar/"
    
    payload = {
        "call": "ListarContasPagar",
        "app_key": empresa.omie_app_key,
        "app_secret": empresa.omie_app_secret,
        "param": [
            {
                "pagina": 1,
                "registros_por_pagina": 10,
                "apenas_importado_api": "N"
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        # O Omie retorna 'faultstring' se a chave estiver errada
        if "faultstring" in data:
            return {"status": "erro", "detalhe": f"Resposta do Omie: {data['faultstring']}"}
        
        return {"status": "ok", "detalhe": "Conciliação efetuada!", "dados": data}

    except Exception as e:
        return {"status": "erro", "detalhe": f"Erro de comunicação: {str(e)}"}


# ── SERVIR FRONTEND ESTATICO ──
# O FastAPI vai servir tudo que está na pasta `frontend`
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")

@app.get("/")
def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

app.mount("/", StaticFiles(directory=FRONTEND_DIR), name="frontend")

