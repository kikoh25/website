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

# ── DB ──
DATABASE_URL = "postgresql+psycopg2://nexus_user:NexusDB2026@localhost/nexusplatform"
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

    # Se suspendendo, invalida todas as sessões dos usuários do tenant imediatamente
    if not data.ativo:
        usuarios = db.execute(text("SELECT id FROM users WHERE tenant_id = :tid"), {"tid": tenant_id}).fetchall()
        for u in usuarios:
            uid = str(u.id)
            db.execute(text("""
                DELETE FROM user_sessions
                WHERE sess->'user'->>'id' = :uid
            """), {"uid": uid})
        # Também invalida por tenant_id direto
        db.execute(text("""
            DELETE FROM user_sessions
            WHERE sess->'user'->>'tenant_id' = :tid
        """), {"tid": tenant_id})

    db.commit()
    return {"ok": True, "ativo": data.ativo}

LIMITES_PLANO = {
    "trial":     {"max_tecnicos": 1,  "max_usuarios": 5,   "max_ativos": 15},
    "chamados":  {"max_tecnicos": 2,  "max_usuarios": 20,  "max_ativos": 50},
    "completo":  {"max_tecnicos": 5,  "max_usuarios": 100, "max_ativos": 300},
    "inventario":{"max_tecnicos": 2,  "max_usuarios": 20,  "max_ativos": 200},
}

@app.patch("/tenants/{tenant_id}/plano")
def update_tenant_plano(tenant_id: str, data: TenantPlanoUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    limites = LIMITES_PLANO.get(data.plano, {})
    campos = {
        "plano":        data.plano,
        "max_tecnicos": data.max_tecnicos or limites.get("max_tecnicos", 1),
        "max_usuarios": data.max_usuarios or limites.get("max_usuarios", 3),
        "max_ativos":   data.max_ativos   or limites.get("max_ativos", 5),
        "id": tenant_id
    }
    db.execute(text("""
        UPDATE tenants SET
            plano = :plano,
            max_tecnicos = :max_tecnicos,
            max_usuarios = :max_usuarios,
            max_ativos = :max_ativos,
            atualizado_em = now()
        WHERE id = :id
    """), campos)
    db.commit()
    return {"ok": True, "plano": data.plano, "limites": limites}

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

    # Se suspendendo, invalida sessão do usuário imediatamente
    if not novo:
        db.execute(text("""
            DELETE FROM user_sessions
            WHERE sess->'user'->>'id' = :uid
        """), {"uid": user_id})

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

# ── CADASTRO SELF-SERVICE ──
class CadastroIn(BaseModel):
    empresa: str
    cnpj: Optional[str] = ""
    nome: str
    email: str
    senha: str
    slug: str
    cargo: Optional[str] = ""
    telefone: Optional[str] = ""
    plano: str = "free"

PLANOS = {
    "free":    {"plano_db": "trial",    "max_tecnicos": 1,  "max_usuarios": 5,   "max_ativos": 15,  "plano_ativo": True},
    "starter": {"plano_db": "chamados", "max_tecnicos": 2,  "max_usuarios": 20,  "max_ativos": 50,  "plano_ativo": True},
    "pro":     {"plano_db": "completo", "max_tecnicos": 5,  "max_usuarios": 100, "max_ativos": 300, "plano_ativo": True},
}

@app.post("/cadastro", status_code=201)
def cadastro(data: CadastroIn, db: Session = Depends(get_db)):
    import re, bcrypt as _bcrypt

    # Validações
    if not data.empresa or not data.email or not data.senha or not data.slug:
        raise HTTPException(400, "Campos obrigatórios não preenchidos")
    if len(data.senha) < 8:
        raise HTTPException(400, "Senha mínima de 8 caracteres")
    if not re.match(r'^[a-z0-9][a-z0-9-]{1,28}[a-z0-9]$', data.slug):
        raise HTTPException(400, "Slug inválido")
    if data.plano not in PLANOS:
        raise HTTPException(400, "Plano inválido")

    # Verificar slug único
    existing = db.execute(text("SELECT id FROM tenants WHERE slug = :slug"), {"slug": data.slug}).fetchone()
    if existing:
        raise HTTPException(400, "Este identificador já está em uso. Escolha outro.")

    # Verificar email único
    existing_email = db.execute(text("SELECT id FROM users WHERE email = :email"), {"email": data.email}).fetchone()
    if existing_email:
        raise HTTPException(400, "Este e-mail já está cadastrado.")

    config = PLANOS[data.plano]

    # Criar tenant
    tenant_id = str(__import__('uuid').uuid4())
    db.execute(text("""
        INSERT INTO tenants (id, nome, slug, razao_social, cnpj, email_admin, telefone,
                             plano, plano_ativo, max_tecnicos, max_usuarios, max_ativos,
                             ativo, criado_em, atualizado_em)
        VALUES (:id, :nome, :slug, :nome, :cnpj, :email, :tel,
                :plano, :plano_ativo, :max_tec, :max_usr, :max_atv,
                true, now(), now())
    """), {
        "id": tenant_id, "nome": data.empresa, "slug": data.slug,
        "cnpj": data.cnpj, "email": data.email, "tel": data.telefone,
        "plano": config["plano_db"], "plano_ativo": config["plano_ativo"],
        "max_tec": config["max_tecnicos"], "max_usr": config["max_usuarios"],
        "max_atv": config["max_ativos"]
    })

    # Criar usuário admin
    senha_hash = _bcrypt.hashpw(data.senha.encode(), _bcrypt.gensalt(12)).decode()
    user_id = str(__import__('uuid').uuid4())
    db.execute(text("""
        INSERT INTO users (id, tenant_id, nome, email, senha_hash, role,
                           cargo, telefone, ativo, email_verificado, criado_em, atualizado_em)
        VALUES (:id, :tid, :nome, :email, :hash, 'admin',
                :cargo, :tel, true, false, now(), now())
    """), {
        "id": user_id, "tid": tenant_id, "nome": data.nome,
        "email": data.email, "hash": senha_hash,
        "cargo": data.cargo, "tel": data.telefone
    })

    db.commit()

    return {
        "ok": True,
        "tenant_id": tenant_id,
        "slug": data.slug,
        "plano": data.plano,
        "email": data.email,
        "message": "Conta criada com sucesso!"
    }

# ── VERIFICAR EMAIL (para login unificado) ──
class EmailCheck(BaseModel):
    email: str

@app.post("/verificar-email")
def verificar_email(data: EmailCheck, db: Session = Depends(get_db)):
    row = db.execute(text("SELECT id, nome FROM users WHERE email = :email AND ativo = true"), {"email": data.email}).fetchone()
    if row:
        return {"exists": True, "nome": row.nome}
    return {"exists": False}

@app.get("/me")
def get_me(user=Depends(get_current_user), db: Session = Depends(get_db)):
    row = db.execute(text("SELECT id, nome, email, role FROM users WHERE email = :email AND ativo = true"), {"email": user}).fetchone()
    if not row: raise HTTPException(404)
    return dict(row._mapping)

# ── RECUPERAÇÃO DE SENHA ──
import secrets, resend
from datetime import datetime, timedelta

resend.api_key = "re_4FHQ6SYU_5WBE2MfqARXSBmuNQ7gPBqEh"

# Armazena tokens em memória (simples, sem banco adicional)
reset_tokens = {}

class ForgotIn(BaseModel):
    email: str

class ResetIn(BaseModel):
    token: str
    nova_senha: str

@app.post("/esqueci-senha")
def esqueci_senha(data: ForgotIn, db: Session = Depends(get_db)):
    # Verificar se email existe
    row = db.execute(text("""
        SELECT u.id, u.nome, u.email, t.nome as tenant_nome
        FROM users u
        JOIN tenants t ON t.id = u.tenant_id
        WHERE u.email = :email AND u.ativo = true
    """), {"email": data.email}).fetchone()

    # Sempre retorna sucesso (segurança)
    if not row:
        return {"ok": True, "message": "Se o e-mail existir, você receberá as instruções."}

    # Gerar token seguro
    token = secrets.token_urlsafe(32)
    reset_tokens[token] = {
        "user_id": str(row.id),
        "email": row.email,
        "expires": datetime.utcnow() + timedelta(hours=2)
    }

    # Enviar e-mail via Resend
    reset_url = f"https://nexusefbusiness.com.br/redefinir-senha.html?token={token}"
    try:
        resend.Emails.send({
            "from": "Nexus Platform <contato@nexusefbusiness.com.br>",
            "to": [row.email],
            "subject": "Redefinição de senha — Nexus Platform",
            "html": f"""
            <div style="font-family:Inter,sans-serif;max-width:520px;margin:0 auto;padding:2rem">
              <div style="text-align:center;margin-bottom:2rem">
                <img src="https://nexusefbusiness.com.br/favicon.ico" width="40" style="margin-bottom:1rem"/>
                <h1 style="font-family:Georgia,serif;color:#1E1B4B;font-size:1.5rem;margin:0">Nexus<span style="color:#7C3AED">EF</span> Platform</h1>
              </div>
              <h2 style="color:#1E1B4B;font-size:1.2rem;margin-bottom:.75rem">Olá, {row.nome}!</h2>
              <p style="color:#52557A;line-height:1.7;margin-bottom:1.5rem">
                Recebemos uma solicitação para redefinir a senha da sua conta na Nexus Platform.
                Clique no botão abaixo para criar uma nova senha:
              </p>
              <div style="text-align:center;margin:2rem 0">
                <a href="{reset_url}" style="background:#7C3AED;color:#fff;padding:.9rem 2rem;border-radius:8px;text-decoration:none;font-weight:700;font-size:.95rem">
                  Redefinir minha senha
                </a>
              </div>
              <p style="color:#9096B8;font-size:.8rem;line-height:1.6">
                Este link expira em <strong>2 horas</strong>. Se você não solicitou a redefinição, ignore este e-mail.
              </p>
              <hr style="border:none;border-top:1px solid #ECEAF8;margin:1.5rem 0"/>
              <p style="color:#9096B8;font-size:.75rem;text-align:center">
                Nexus EF Business · nexusefbusiness.com.br
              </p>
            </div>
            """
        })
    except Exception as e:
        print(f"Erro ao enviar email: {e}")

    return {"ok": True, "message": "Se o e-mail existir, você receberá as instruções."}

@app.post("/redefinir-senha")
def redefinir_senha(data: ResetIn, db: Session = Depends(get_db)):
    # Verificar token
    token_data = reset_tokens.get(data.token)
    if not token_data:
        raise HTTPException(400, "Link inválido ou expirado.")
    if datetime.utcnow() > token_data["expires"]:
        del reset_tokens[data.token]
        raise HTTPException(400, "Link expirado. Solicite um novo.")
    if len(data.nova_senha) < 8:
        raise HTTPException(400, "Senha mínima de 8 caracteres.")

    # Atualizar senha
    import bcrypt as _bcrypt
    hash = _bcrypt.hashpw(data.nova_senha.encode(), _bcrypt.gensalt(12)).decode()
    db.execute(text("""
        UPDATE users SET senha_hash = :hash, atualizado_em = now()
        WHERE id = :id
    """), {"hash": hash, "id": token_data["user_id"]})

    # Invalidar sessões antigas
    db.execute(text("""
        DELETE FROM user_sessions WHERE sess->'user'->>'id' = :uid
    """), {"uid": token_data["user_id"]})

    db.commit()
    del reset_tokens[data.token]

    return {"ok": True, "message": "Senha redefinida com sucesso!"}

@app.get("/verificar-token")
def verificar_token(token: str):
    token_data = reset_tokens.get(token)
    if not token_data or datetime.utcnow() > token_data["expires"]:
        raise HTTPException(400, "Link inválido ou expirado.")
    return {"ok": True, "email": token_data["email"]}

# ── LOGIN DE USUÁRIO DA PLATAFORMA ──
class UserLoginIn(BaseModel):
    email: str
    password: str

@app.post("/login-usuario")
def login_usuario(data: UserLoginIn, db: Session = Depends(get_db)):
    import bcrypt as _bcrypt
    row = db.execute(text("""
        SELECT u.id, u.nome, u.email, u.senha_hash, u.role, u.ativo,
               t.id as tenant_id, t.nome as tenant_nome, t.plano, t.ativo as tenant_ativo
        FROM users u
        JOIN tenants t ON t.id = u.tenant_id
        WHERE u.email = :email
    """), {"email": data.email}).fetchone()

    if not row:
        raise HTTPException(401, "E-mail ou senha incorretos.")
    if not row.ativo:
        raise HTTPException(401, "Usuário suspenso. Entre em contato com o suporte.")
    if not row.tenant_ativo:
        raise HTTPException(401, "Conta suspensa. Entre em contato com o suporte.")

    # Verificar senha (bcrypt compatível com $2a$ e $2b$)
    try:
        senha_ok = _bcrypt.checkpw(data.password.encode(), row.senha_hash.encode())
    except Exception:
        raise HTTPException(401, "E-mail ou senha incorretos.")

    if not senha_ok:
        raise HTTPException(401, "E-mail ou senha incorretos.")

    return {
        "ok": True,
        "nome": row.nome,
        "email": row.email,
        "role": row.role,
        "tenant_id": str(row.tenant_id),
        "tenant_nome": row.tenant_nome,
        "plano": row.plano,
        "redirect": "https://ti.nexusefbusiness.com.br"
    }
