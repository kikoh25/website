from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import os

# ── CONFIG ──
SECRET_KEY = "nexusef@2026#supersecreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
DATABASE_URL = "postgresql://nexus:Ivete%402019%40%23@localhost/nexusadmin"

# ── DB ──
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ── MODELS ──
class Cliente(Base):
    __tablename__ = "clientes"
    id = Column(Integer, primary_key=True, index=True)
    empresa = Column(String(200), nullable=False)
    cnpj = Column(String(20))
    responsavel = Column(String(100), nullable=False)
    cargo = Column(String(100))
    email = Column(String(150), nullable=False)
    telefone = Column(String(20))
    plano = Column(String(50))
    status = Column(String(30), default="Ativo")
    obs = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Contrato(Base):
    __tablename__ = "contratos"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False)
    cliente_nome = Column(String(200))
    produto = Column(String(100))
    valor = Column(Float, default=0)
    tipo = Column(String(50))
    inicio = Column(String(20))
    fim = Column(String(20))
    status = Column(String(30), default="Ativo")
    obs = Column(Text)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Tenant(Base):
    __tablename__ = "tenants"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False)
    cliente_nome = Column(String(200))
    subdominio = Column(String(100))
    plano = Column(String(50))
    tickets_mes = Column(Integer, default=500)
    usuarios = Column(Integer, default=10)
    status = Column(String(30), default="Ativo")
    criado_em = Column(DateTime, default=datetime.utcnow)

class LeadNow(Base):
    __tablename__ = "leadnow"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False)
    cliente_nome = Column(String(200))
    evento = Column(String(200))
    base_conhecimento = Column(String(300))
    inicio = Column(String(20))
    fim = Column(String(20))
    status = Column(String(30), default="Ativo")
    leads = Column(Integer, default=0)
    criado_em = Column(DateTime, default=datetime.utcnow)

class Financeiro(Base):
    __tablename__ = "financeiro"
    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, nullable=False)
    cliente_nome = Column(String(200))
    descricao = Column(String(300))
    valor = Column(Float, default=0)
    data = Column(String(20))
    status = Column(String(30), default="Pago")
    criado_em = Column(DateTime, default=datetime.utcnow)

class Atividade(Base):
    __tablename__ = "atividades"
    id = Column(Integer, primary_key=True, index=True)
    texto = Column(Text)
    cor = Column(String(50))
    criado_em = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

# ── AUTH ──
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ADMIN_USER = "erick"
ADMIN_PASS = pwd_context.hash("Nexus@2026#")

def verify_password(plain, hashed): return pwd_context.verify(plain, hashed)
def create_token(data: dict):
    d = data.copy()
    d.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(d, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if user is None: raise HTTPException(status_code=401, detail="Token inválido")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ── APP ──
app = FastAPI(title="Nexus EF Admin API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ── SCHEMAS ──
class Token(BaseModel): access_token: str; token_type: str
class ClienteIn(BaseModel):
    empresa: str; cnpj: Optional[str]=""; responsavel: str; cargo: Optional[str]=""
    email: str; telefone: Optional[str]=""; plano: Optional[str]="Starter"
    status: Optional[str]="Ativo"; obs: Optional[str]=""
class ContratoIn(BaseModel):
    cliente_id: int; cliente_nome: Optional[str]=""; produto: str; valor: Optional[float]=0
    tipo: Optional[str]="Recorrente mensal"; inicio: Optional[str]=""; fim: Optional[str]=""
    status: Optional[str]="Ativo"; obs: Optional[str]=""
class TenantIn(BaseModel):
    cliente_id: int; cliente_nome: Optional[str]=""; subdominio: Optional[str]=""
    plano: Optional[str]="Starter"; tickets_mes: Optional[int]=500
    usuarios: Optional[int]=10; status: Optional[str]="Ativo"
class LeadNowIn(BaseModel):
    cliente_id: int; cliente_nome: Optional[str]=""; evento: Optional[str]=""
    base_conhecimento: Optional[str]=""; inicio: Optional[str]=""; fim: Optional[str]=""
    status: Optional[str]="Ativo"
class FinanceiroIn(BaseModel):
    cliente_id: int; cliente_nome: Optional[str]=""; descricao: Optional[str]=""
    valor: Optional[float]=0; data: Optional[str]=""; status: Optional[str]="Pago"
class StatusUpdate(BaseModel): status: str

# ── ROUTES ──
@app.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != ADMIN_USER or not verify_password(form.password, ADMIN_PASS):
        raise HTTPException(status_code=400, detail="Usuário ou senha incorretos")
    return {"access_token": create_token({"sub": form.username}), "token_type": "bearer"}

@app.get("/health")
def health(): return {"status": "ok", "api": "Nexus EF Admin"}

# Clientes
@app.get("/clientes")
def list_clientes(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Cliente).order_by(Cliente.criado_em.desc()).all()

@app.post("/clientes", status_code=201)
def create_cliente(data: ClienteIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = Cliente(**data.dict())
    db.add(c); db.commit(); db.refresh(c)
    log(db, f"Novo cliente: {c.empresa}", "var(--green)")
    return c

@app.patch("/clientes/{id}/status")
def update_cliente_status(id: int, data: StatusUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.query(Cliente).filter(Cliente.id==id).first()
    if not c: raise HTTPException(404)
    c.status = data.status; db.commit()
    log(db, f"Cliente {c.empresa} → {data.status}", "var(--yellow)")
    return c

@app.delete("/clientes/{id}")
def delete_cliente(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.query(Cliente).filter(Cliente.id==id).first()
    if not c: raise HTTPException(404)
    log(db, f"Cliente removido: {c.empresa}", "var(--red)")
    db.delete(c); db.commit()
    return {"ok": True}

# Contratos
@app.get("/contratos")
def list_contratos(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Contrato).order_by(Contrato.criado_em.desc()).all()

@app.post("/contratos", status_code=201)
def create_contrato(data: ContratoIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = Contrato(**data.dict()); db.add(c); db.commit(); db.refresh(c)
    log(db, f"Contrato criado: {c.cliente_nome} — {c.produto}", "var(--blue)")
    return c

@app.delete("/contratos/{id}")
def delete_contrato(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.query(Contrato).filter(Contrato.id==id).first()
    if not c: raise HTTPException(404)
    db.delete(c); db.commit()
    log(db, f"Contrato removido: {c.cliente_nome}", "var(--red)")
    return {"ok": True}

# Tenants
@app.get("/tenants")
def list_tenants(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Tenant).order_by(Tenant.criado_em.desc()).all()

@app.post("/tenants", status_code=201)
def create_tenant(data: TenantIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = Tenant(**data.dict()); db.add(t); db.commit(); db.refresh(t)
    log(db, f"Tenant criado: {t.cliente_nome}", "var(--purple)")
    return t

@app.patch("/tenants/{id}/status")
def update_tenant_status(id: int, data: StatusUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(Tenant).filter(Tenant.id==id).first()
    if not t: raise HTTPException(404)
    t.status = data.status; db.commit()
    log(db, f"Tenant {t.cliente_nome} → {data.status}", "var(--yellow)")
    return t

@app.delete("/tenants/{id}")
def delete_tenant(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    t = db.query(Tenant).filter(Tenant.id==id).first()
    if not t: raise HTTPException(404)
    db.delete(t); db.commit()
    return {"ok": True}

# LeadNow
@app.get("/leadnow")
def list_leadnow(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(LeadNow).order_by(LeadNow.criado_em.desc()).all()

@app.post("/leadnow", status_code=201)
def create_leadnow(data: LeadNowIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    l = LeadNow(**data.dict()); db.add(l); db.commit(); db.refresh(l)
    log(db, f"LeadNow: {l.evento}", "var(--purple)")
    return l

@app.delete("/leadnow/{id}")
def delete_leadnow(id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    l = db.query(LeadNow).filter(LeadNow.id==id).first()
    if not l: raise HTTPException(404)
    db.delete(l); db.commit()
    return {"ok": True}

# Financeiro
@app.get("/financeiro")
def list_financeiro(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Financeiro).order_by(Financeiro.criado_em.desc()).all()

@app.post("/financeiro", status_code=201)
def create_financeiro(data: FinanceiroIn, db: Session = Depends(get_db), user=Depends(get_current_user)):
    f = Financeiro(**data.dict()); db.add(f); db.commit(); db.refresh(f)
    log(db, f"Receita: {f.cliente_nome} R${f.valor}", "var(--green)")
    return f

# Atividades
@app.get("/atividades")
def list_atividades(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Atividade).order_by(Atividade.criado_em.desc()).limit(50).all()

@app.delete("/atividades")
def clear_atividades(db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.query(Atividade).delete(); db.commit()
    return {"ok": True}

# Stats
@app.get("/stats")
def get_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    from sqlalchemy import func
    clientes_ativos = db.query(Cliente).filter(Cliente.status=="Ativo").count()
    contratos_ativos = db.query(Contrato).filter(Contrato.status=="Ativo").count()
    tenants_ativos = db.query(Tenant).filter(Tenant.status=="Ativo").count()
    mrr = db.query(func.sum(Contrato.valor)).filter(Contrato.status=="Ativo").scalar() or 0
    total_clientes = db.query(Cliente).count()
    return {"clientes_ativos": clientes_ativos, "total_clientes": total_clientes,
            "contratos_ativos": contratos_ativos, "tenants_ativos": tenants_ativos, "mrr": mrr}

def log(db, texto, cor="var(--purple)"):
    db.add(Atividade(texto=texto, cor=cor)); db.commit()
