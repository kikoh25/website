from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel
import uuid

# ── CONFIG ──
SECRET_KEY = "nexusplatform@2026#supersecreto"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480
DATABASE_URL = "postgresql://nexus_user:Ivete%402019%40%23@localhost/nexusplatform"

# ── DB ──
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try: yield db
    finally: db.close()

# ── AUTH ──
pwd_context = CryptContext(schemes=["sha256_crypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

ADMIN_USER = "erick"
ADMIN_PASS = pwd_context.hash("Nexus@2026#")

def create_token(data: dict):
    d = data.copy()
    d.update({"exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)})
    return jwt.encode(d, SECRET_KEY, algorithm=ALGORITHM)

def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user = payload.get("sub")
        if not user: raise HTTPException(status_code=401, detail="Token inválido")
        return user
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

# ── APP ──
app = FastAPI(title="Nexus Platform API", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# ── SCHEMAS ──
class Token(BaseModel): access_token: str; token_type: str
class TenantStatusUpdate(BaseModel): ativo: bool; motivo_inativo: Optional[str] = None
class TenantPlanoUpdate(BaseModel): plano: str; max_tecnicos: Optional[int] = None; max_usuarios: Optional[int] = None; max_ativos: Optional[int] = None

# ── AUTH ROUTE ──
@app.post("/token", response_model=Token)
def login(form: OAuth2PasswordRequestForm = Depends()):
    if form.username != ADMIN_USER or not pwd_context.verify(form.password, ADMIN_PASS):
        raise HTTPException(status_code=400, detail="Credenciais inválidas")
    return {"access_token": create_token({"sub": form.username}), "token_type": "bearer"}

@app.get("/health")
def health(): return {"status": "ok", "api": "Nexus Platform API", "db": "nexusplatform"}

# ── TENANTS ──
@app.get("/tenants")
def list_tenants(db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.execute(text("""
        SELECT t.id, t.nome, t.slug, t.email_admin, t.telefone, t.cnpj,
               t.plano, t.plano_ativo, t.ativo, t.motivo_inativo,
               t.max_tecnicos, t.max_usuarios, t.max_ativos,
               t.trial_ate, t.assinatura_ate, t.criado_em,
               COUNT(DISTINCT u.id) as total_usuarios,
               COUNT(DISTINCT tk.id) as total_tickets,
               COUNT(DISTINCT a.id) as total_ativos
        FROM tenants t
        LEFT JOIN users u ON u.tenant_id = t.id AND u.ativo = true
        LEFT JOIN tickets tk ON tk.tenant_id = t.id
        LEFT JOIN assets a ON a.tenant_id = t.id
        GROUP BY t.id
        ORDER BY t.criado_em DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/tenants/{tenant_id}")
def get_tenant(tenant_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.execute(text("""
        SELECT t.*,
               COUNT(DISTINCT u.id) as total_usuarios,
               COUNT(DISTINCT tk.id) as total_tickets,
               COUNT(DISTINCT a.id) as total_ativos
        FROM tenants t
        LEFT JOIN users u ON u.tenant_id = t.id AND u.ativo = true
        LEFT JOIN tickets tk ON tk.tenant_id = t.id
        LEFT JOIN assets a ON a.tenant_id = t.id
        WHERE t.id = :id
        GROUP BY t.id
    """), {"id": tenant_id}).fetchone()
    if not row: raise HTTPException(404, "Tenant não encontrado")
    return dict(row._mapping)

@app.patch("/tenants/{tenant_id}/status")
def update_tenant_status(tenant_id: str, data: TenantStatusUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    db.execute(text("""
        UPDATE tenants SET ativo = :ativo, motivo_inativo = :motivo, atualizado_em = now()
        WHERE id = :id
    """), {"ativo": data.ativo, "motivo": data.motivo_inativo, "id": tenant_id})
    db.commit()
    return {"ok": True, "ativo": data.ativo}

@app.patch("/tenants/{tenant_id}/plano")
def update_tenant_plano(tenant_id: str, data: TenantPlanoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    campos = {"plano": data.plano, "id": tenant_id}
    extras = ""
    if data.max_tecnicos: campos["max_tecnicos"] = data.max_tecnicos; extras += ", max_tecnicos = :max_tecnicos"
    if data.max_usuarios: campos["max_usuarios"] = data.max_usuarios; extras += ", max_usuarios = :max_usuarios"
    if data.max_ativos:   campos["max_ativos"]   = data.max_ativos;   extras += ", max_ativos = :max_ativos"
    db.execute(text(f"UPDATE tenants SET plano = :plano{extras}, atualizado_em = now() WHERE id = :id"), campos)
    db.commit()
    return {"ok": True, "plano": data.plano}

# ── USUARIOS ──
@app.get("/tenants/{tenant_id}/usuarios")
def list_usuarios(tenant_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.execute(text("""
        SELECT id, nome, email, role, departamento, cargo, ativo,
               ultimo_login, criado_em, slack_user_id, teams_user_id
        FROM users WHERE tenant_id = :tid ORDER BY criado_em DESC
    """), {"tid": tenant_id}).fetchall()
    return [dict(r._mapping) for r in rows]

@app.patch("/tenants/{tenant_id}/usuarios/{user_id}/status")
def toggle_user(tenant_id: str, user_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    row = db.execute(text("SELECT ativo FROM users WHERE id = :id AND tenant_id = :tid"), {"id": user_id, "tid": tenant_id}).fetchone()
    if not row: raise HTTPException(404)
    novo = not row.ativo
    db.execute(text("UPDATE users SET ativo = :ativo, atualizado_em = now() WHERE id = :id"), {"ativo": novo, "id": user_id})
    db.commit()
    return {"ok": True, "ativo": novo}

# ── TICKETS ──
@app.get("/tenants/{tenant_id}/tickets")
def list_tickets(tenant_id: str, status: Optional[str] = None, limit: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    filtro = "AND tk.status = :status" if status else ""
    rows = db.execute(text(f"""
        SELECT tk.id, tk.numero, tk.titulo, tk.status, tk.prioridade,
               tk.criado_em, tk.fechado_em,
               tk.sla_resolucao_prazo, tk.sla_resolucao_ok,
               u.nome as solicitante, t.nome as tecnico
        FROM tickets tk
        LEFT JOIN users u ON u.id = tk.solicitante_id
        LEFT JOIN users t ON t.id = tk.tecnico_id
        WHERE tk.tenant_id = :tid {filtro}
        ORDER BY tk.criado_em DESC LIMIT :limit
    """), {"tid": tenant_id, "status": status, "limit": limit}).fetchall()
    return [dict(r._mapping) for r in rows]

# ── ATIVOS ──
@app.get("/tenants/{tenant_id}/ativos")
def list_ativos(tenant_id: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.execute(text("""
        SELECT a.id, a.nome, a.numero_serie, a.status, a.tipo,
               a.criado_em, u.nome as responsavel
        FROM assets a
        LEFT JOIN users u ON u.id = a.responsavel_id
        WHERE a.tenant_id = :tid
        ORDER BY a.criado_em DESC LIMIT 100
    """), {"tid": tenant_id}).fetchall()
    return [dict(r._mapping) for r in rows]

# ── STATS GERAIS ──
@app.get("/stats")
def get_stats(db: Session = Depends(get_db), user=Depends(get_current_user)):
    tenants_ativos = db.execute(text("SELECT COUNT(*) FROM tenants WHERE ativo = true")).scalar()
    tenants_total  = db.execute(text("SELECT COUNT(*) FROM tenants")).scalar()
    usuarios_total = db.execute(text("SELECT COUNT(*) FROM users WHERE ativo = true")).scalar()
    tickets_abertos = db.execute(text("SELECT COUNT(*) FROM tickets WHERE status IN ('aberto','em_andamento','pendente')")).scalar()
    tickets_total  = db.execute(text("SELECT COUNT(*) FROM tickets")).scalar()
    ativos_total   = db.execute(text("SELECT COUNT(*) FROM assets")).scalar()
    sla_violados   = db.execute(text("SELECT COUNT(*) FROM tickets WHERE sla_resolucao_ok = false AND fechado_em IS NOT NULL")).scalar()

    por_plano = db.execute(text("""
        SELECT plano, COUNT(*) as total FROM tenants WHERE ativo = true GROUP BY plano
    """)).fetchall()

    por_status = db.execute(text("""
        SELECT status, COUNT(*) as total FROM tickets GROUP BY status
    """)).fetchall()

    return {
        "tenants_ativos": tenants_ativos,
        "tenants_total": tenants_total,
        "usuarios_ativos": usuarios_total,
        "tickets_abertos": tickets_abertos,
        "tickets_total": tickets_total,
        "ativos_total": ativos_total,
        "sla_violados": sla_violados,
        "por_plano": [dict(r._mapping) for r in por_plano],
        "por_status": [dict(r._mapping) for r in por_status],
    }

# ── AUDIT LOG ──
@app.get("/tenants/{tenant_id}/audit")
def get_audit(tenant_id: str, limit: int = 50, db: Session = Depends(get_db), user=Depends(get_current_user)):
    rows = db.execute(text("""
        SELECT al.id, al.acao, al.tabela, al.criado_em,
               u.nome as usuario
        FROM audit_log al
        LEFT JOIN users u ON u.id = al.usuario_id
        WHERE al.tenant_id = :tid
        ORDER BY al.criado_em DESC LIMIT :limit
    """), {"tid": tenant_id, "limit": limit}).fetchall()
    return [dict(r._mapping) for r in rows]
