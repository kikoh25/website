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


# ── NEXUS CONTÁBIL — ADMIN ENDPOINTS ──
from sqlalchemy import create_engine as _ce2, text as _text2
from sqlalchemy.orm import sessionmaker as _sm2

_CONTABIL_URL = "postgresql+psycopg2://nexuscontabil:NexusContabil2026@localhost/nexuscontabil"
_engine2 = _ce2(_CONTABIL_URL)
_ContabilSession = _sm2(autocommit=False, autoflush=False, bind=_engine2)

def get_contabil_db():
    db = _ContabilSession()
    try:
        yield db
    finally:
        db.close()

@app.get("/contabil/tenants")
def contabil_tenants(db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT t.id, t.nome, t.cnpj, t.email, t.telefone,
               t.plano, t.status, t."trialEndsAt", t."xmlsUsadosMes",
               t."createdAt",
               COUNT(DISTINCT e.id) as total_empresas,
               COUNT(DISTINCT u.id) as total_usuarios,
               COUNT(DISTINCT d.id) as total_documentos
        FROM tenants t
        LEFT JOIN empresas e ON e."tenantId" = t.id
        LEFT JOIN usuarios u ON u."tenantId" = t.id
        LEFT JOIN documentos d ON d."tenantId" = t.id
        GROUP BY t.id
        ORDER BY t."createdAt" DESC
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/contabil/stats")
def contabil_stats(db=Depends(get_contabil_db), user=Depends(get_current_user)):
    stats = db.execute(_text2("""
        SELECT
            COUNT(*) as total_tenants,
            COUNT(*) FILTER (WHERE status = 'ACTIVE') as tenants_ativos,
            COUNT(*) FILTER (WHERE status = 'TRIAL') as tenants_trial,
            COUNT(*) FILTER (WHERE status = 'CANCELLED') as tenants_cancelados,
            COUNT(*) FILTER (WHERE plano = 'STARTER') as plano_starter,
            COUNT(*) FILTER (WHERE plano = 'PROFISSIONAL') as plano_profissional,
            COUNT(*) FILTER (WHERE plano = 'ENTERPRISE') as plano_enterprise
        FROM tenants
    """)).fetchone()
    empresas = db.execute(_text2("SELECT COUNT(*) as total FROM empresas")).fetchone()
    documentos = db.execute(_text2("SELECT COUNT(*) as total FROM documentos")).fetchone()
    return {
        **dict(stats._mapping),
        "total_empresas": empresas.total,
        "total_documentos": documentos.total
    }

@app.get("/contabil/tenants/{tenant_id}")
def contabil_tenant_detail(tenant_id: str, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    tenant = db.execute(_text2("""
        SELECT * FROM tenants WHERE id = :id
    """), {"id": tenant_id}).fetchone()
    if not tenant:
        raise HTTPException(404, "Tenant não encontrado")
    empresas = db.execute(_text2("""
        SELECT id, nome, cnpj, regime, "createdAt" FROM empresas WHERE "tenantId" = :id ORDER BY nome
    """), {"id": tenant_id}).fetchall()
    usuarios = db.execute(_text2("""
        SELECT id, nome, email, perfil, ativo, "createdAt" FROM usuarios WHERE "tenantId" = :id ORDER BY nome
    """), {"id": tenant_id}).fetchall()
    docs = db.execute(_text2("""
        SELECT COUNT(*) as total FROM documentos WHERE "tenantId" = :id
    """), {"id": tenant_id}).fetchone()
    return {
        "tenant": dict(tenant._mapping),
        "empresas": [dict(r._mapping) for r in empresas],
        "usuarios": [dict(r._mapping) for r in usuarios],
        "total_documentos": docs.total
    }

class ContabilPlanoUpdate(BaseModel):
    plano: str
    status: Optional[str] = None

@app.patch("/contabil/tenants/{tenant_id}/plano")
def contabil_update_plano(tenant_id: str, data: ContabilPlanoUpdate, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    campos = {"plano": data.plano, "id": tenant_id}
    sql = 'UPDATE tenants SET plano = :plano, "updatedAt" = now()'
    if data.status:
        sql += ', status = :status'
        campos["status"] = data.status
    sql += " WHERE id = :id"
    db.execute(_text2(sql), campos)
    db.commit()
    return {"ok": True}

@app.patch("/contabil/tenants/{tenant_id}/status")
def contabil_update_status(tenant_id: str, data: dict, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    db.execute(_text2('UPDATE tenants SET status = :status, "updatedAt" = now() WHERE id = :id'),
               {"status": data.get("status"), "id": tenant_id})
    db.commit()
    return {"ok": True}

# ── CONTÁBIL — ENDPOINTS AVANÇADOS ──

@app.get("/contabil/tenants/{tenant_id}/tickets")
def contabil_tenant_tickets(tenant_id: str, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT id, tipo, titulo, descricao, status, "createdAt", "updatedAt"
        FROM tickets WHERE "tenantId" = :id ORDER BY "createdAt" DESC LIMIT 20
    """), {"id": tenant_id}).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/contabil/tenants/{tenant_id}/documentos-mes")
def contabil_docs_mes(tenant_id: str, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT DATE_TRUNC('month', d."dataImportacao") as mes,
               COUNT(*) as total,
               SUM(d.valor) as valor_total
        FROM documentos d
        JOIN empresas e ON e.id = d."empresaId"
        WHERE e."tenantId" = :id
          AND d."dataImportacao" >= NOW() - INTERVAL '12 months'
        GROUP BY 1 ORDER BY 1
    """), {"id": tenant_id}).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/contabil/tenants/{tenant_id}/auditoria")
def contabil_tenant_auditoria(tenant_id: str, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT a.id, a.acao, a.entidade, a.descricao, a."usuarioId",
               u.nome as usuario_nome, a."createdAt"
        FROM audit_logs a
        LEFT JOIN usuarios u ON u.id = a."usuarioId"
        WHERE a."tenantId" = :id
        ORDER BY a."createdAt" DESC LIMIT 20
    """), {"id": tenant_id}).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/contabil/crescimento")
def contabil_crescimento(db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT DATE_TRUNC('month', "createdAt") as mes,
               COUNT(*) as novos,
               COUNT(*) FILTER (WHERE status = 'ACTIVE') as ativos
        FROM tenants
        WHERE "createdAt" >= NOW() - INTERVAL '12 months'
        GROUP BY 1 ORDER BY 1
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/contabil/trial-expirando")
def contabil_trial_expirando(db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT id, nome, email, plano, status, "trialEndsAt",
               EXTRACT(DAY FROM "trialEndsAt" - NOW()) as dias_restantes
        FROM tenants
        WHERE status = 'TRIAL'
          AND "trialEndsAt" IS NOT NULL
          AND "trialEndsAt" > NOW()
          AND "trialEndsAt" <= NOW() + INTERVAL '7 days'
        ORDER BY "trialEndsAt"
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@app.get("/contabil/inativos")
def contabil_inativos(db=Depends(get_contabil_db), user=Depends(get_current_user)):
    rows = db.execute(_text2("""
        SELECT t.id, t.nome, t.email, t.plano, t.status,
               MAX(u."lastLoginAt") as ultimo_login,
               EXTRACT(DAY FROM NOW() - MAX(u."lastLoginAt")) as dias_sem_acesso
        FROM tenants t
        LEFT JOIN usuarios u ON u."tenantId" = t.id
        WHERE t.status = 'ACTIVE'
        GROUP BY t.id
        HAVING MAX(u."lastLoginAt") < NOW() - INTERVAL '30 days'
            OR MAX(u."lastLoginAt") IS NULL
        ORDER BY ultimo_login ASC NULLS FIRST
    """)).fetchall()
    return [dict(r._mapping) for r in rows]

@app.patch("/contabil/tenants/{tenant_id}/trial")
def contabil_extend_trial(tenant_id: str, data: dict, db=Depends(get_contabil_db), user=Depends(get_current_user)):
    dias = data.get("dias", 7)
    db.execute(_text2("""
        UPDATE tenants
        SET "trialEndsAt" = COALESCE("trialEndsAt", NOW()) + (:dias || ' days')::INTERVAL,
            "updatedAt" = NOW()
        WHERE id = :id
    """), {"dias": dias, "id": tenant_id})
    db.commit()
    return {"ok": True, "dias_adicionados": dias}

@app.get("/contabil/mrr")
def contabil_mrr(db=Depends(get_contabil_db), user=Depends(get_current_user)):
    precos = {"STARTER": 297, "PROFISSIONAL": 497, "ENTERPRISE": 697}
    rows = db.execute(_text2("""
        SELECT plano, COUNT(*) as quantidade
        FROM tenants WHERE status = 'ACTIVE'
        GROUP BY plano
    """)).fetchall()
    mrr = 0
    detalhes = []
    for r in rows:
        preco = precos.get(r.plano, 0)
        subtotal = preco * r.quantidade
        mrr += subtotal
        detalhes.append({"plano": r.plano, "quantidade": r.quantidade, "preco": preco, "subtotal": subtotal})
    return {"mrr_total": mrr, "detalhes": detalhes}


# ── ADMIN DASHBOARD COMBINADO ──

@app.get("/admin/dashboard")
def admin_dashboard(
    db=Depends(get_db),
    dbc=Depends(get_contabil_db),
    user=Depends(get_current_user)
):
    # Platform stats
    p = db.execute(text("""
        SELECT
            COUNT(*) as total_tenants,
            COUNT(*) FILTER (WHERE plano != 'trial' AND ativo = true) as tenants_pagos,
            COUNT(*) FILTER (WHERE plano = 'trial') as tenants_trial,
            COUNT(*) FILTER (WHERE ativo = false) as tenants_suspensos,
            COUNT(*) FILTER (WHERE plano = 'chamados') as plano_starter,
            COUNT(*) FILTER (WHERE plano = 'completo') as plano_pro,
            COUNT(*) FILTER (WHERE criado_em >= NOW() - INTERVAL '30 days') as novos_30d,
            COUNT(*) FILTER (WHERE criado_em >= NOW() - INTERVAL '7 days') as novos_7d
        FROM tenants
    """)).fetchone()

    # Platform MRR
    p_mrr_map = {"chamados": 149, "completo": 349}
    p_mrr_rows = db.execute(text("""
        SELECT plano, COUNT(*) as qtd FROM tenants
        WHERE ativo = true AND plano != 'trial' GROUP BY plano
    """)).fetchall()
    p_mrr = sum(p_mrr_map.get(r.plano, 0) * r.qtd for r in p_mrr_rows)

    # Contábil stats
    c = dbc.execute(_text2("""
        SELECT
            COUNT(*) as total_tenants,
            COUNT(*) FILTER (WHERE status = 'ACTIVE') as tenants_ativos,
            COUNT(*) FILTER (WHERE status = 'TRIAL') as tenants_trial,
            COUNT(*) FILTER (WHERE "createdAt" >= NOW() - INTERVAL '30 days') as novos_30d,
            COUNT(*) FILTER (WHERE "createdAt" >= NOW() - INTERVAL '7 days') as novos_7d
        FROM tenants
    """)).fetchone()

    # Contábil MRR
    c_mrr_map = {"STARTER": 297, "PROFISSIONAL": 497, "ENTERPRISE": 697}
    c_mrr_rows = dbc.execute(_text2("""
        SELECT plano, COUNT(*) as qtd FROM tenants
        WHERE status = 'ACTIVE' GROUP BY plano
    """)).fetchall()
    c_mrr = sum(c_mrr_map.get(r.plano, 0) * r.qtd for r in c_mrr_rows)

    # Tickets suporte contábil hoje
    tickets_hoje = dbc.execute(_text2("""
        SELECT COUNT(*) as total FROM tickets
        WHERE "createdAt" >= NOW() - INTERVAL '24 hours'
    """)).fetchone()

    # Crescimento combinado 6 meses
    p_crescimento = db.execute(text("""
        SELECT DATE_TRUNC('month', criado_em) as mes, COUNT(*) as novos
        FROM tenants WHERE criado_em >= NOW() - INTERVAL '6 months'
        GROUP BY 1 ORDER BY 1
    """)).fetchall()
    c_crescimento = dbc.execute(_text2("""
        SELECT DATE_TRUNC('month', "createdAt") as mes, COUNT(*) as novos
        FROM tenants WHERE "createdAt" >= NOW() - INTERVAL '6 months'
        GROUP BY 1 ORDER BY 1
    """)).fetchall()

    return {
        "mrr_total": p_mrr + c_mrr,
        "mrr_platform": p_mrr,
        "mrr_contabil": c_mrr,
        "platform": dict(p._mapping),
        "contabil": dict(c._mapping),
        "novos_hoje_platform": dict(p._mapping).get("novos_7d", 0),
        "novos_hoje_contabil": dict(c._mapping).get("novos_7d", 0),
        "tickets_suporte_hoje": tickets_hoje.total,
        "crescimento_platform": [{"mes": str(r.mes)[:7], "novos": r.novos} for r in p_crescimento],
        "crescimento_contabil": [{"mes": str(r.mes)[:7], "novos": r.novos} for r in c_crescimento],
    }

# ── SUPORTE UNIFICADO ──

@app.get("/suporte/tickets")
def suporte_tickets(
    status: Optional[str] = None,
    produto: Optional[str] = None,
    db=Depends(get_db),
    dbc=Depends(get_contabil_db),
    user=Depends(get_current_user)
):
    tickets = []

    # Tickets do Contábil
    if produto in (None, "contabil"):
        sql = """
            SELECT t.id, t."tenantId", t.tipo, t.titulo, t.descricao,
                   t.status, t."createdAt", t."updatedAt",
                   tn.nome as tenant_nome, tn.email as tenant_email
            FROM tickets t
            LEFT JOIN tenants tn ON tn.id = t."tenantId"
            WHERE 1=1
        """
        if status:
            sql += f" AND t.status = '{status}'"
        sql += ' ORDER BY t."createdAt" DESC LIMIT 100'
        rows = dbc.execute(_text2(sql)).fetchall()
        for r in rows:
            d = dict(r._mapping)
            d["produto"] = "contabil"
            d["createdAt"] = str(d.get("createdAt",""))
            d["updatedAt"] = str(d.get("updatedAt",""))
            tickets.append(d)

    tickets.sort(key=lambda x: x.get("createdAt",""), reverse=True)
    return tickets

@app.patch("/suporte/tickets/{ticket_id}/status")
def suporte_ticket_status(
    ticket_id: str,
    data: dict,
    dbc=Depends(get_contabil_db),
    user=Depends(get_current_user)
):
    dbc.execute(_text2("""
        UPDATE tickets SET status = :status, "updatedAt" = NOW() WHERE id = :id
    """), {"status": data.get("status"), "id": ticket_id})
    dbc.commit()
    return {"ok": True}

# ── CONFIGURAÇÕES DE PLANOS ──

from pydantic import BaseModel as _BM

class PlanoConfig(_BM):
    produto: str
    plano: str
    max_tecnicos: Optional[int] = None
    max_usuarios: Optional[int] = None
    max_ativos: Optional[int] = None
    preco: Optional[float] = None

_PLANOS_CONFIG = {
    "platform": {
        "trial":    {"nome":"Free","preco":0,"max_tecnicos":1,"max_usuarios":5,"max_ativos":15},
        "chamados": {"nome":"Starter","preco":149,"max_tecnicos":2,"max_usuarios":20,"max_ativos":50},
        "completo": {"nome":"Pro","preco":349,"max_tecnicos":5,"max_usuarios":100,"max_ativos":300},
    },
    "contabil": {
        "STARTER":     {"nome":"Starter","preco":297,"max_empresas":5,"max_xmls":2000,"max_usuarios":2},
        "PROFISSIONAL":{"nome":"Profissional","preco":497,"max_empresas":25,"max_xmls":15000,"max_usuarios":5},
        "ENTERPRISE":  {"nome":"Enterprise","preco":697,"max_empresas":-1,"max_xmls":-1,"max_usuarios":-1},
    }
}

@app.get("/config/planos")
def get_planos_config(user=Depends(get_current_user)):
    return _PLANOS_CONFIG

@app.patch("/config/planos")
def update_planos_config(data: dict, user=Depends(get_current_user)):
    produto = data.get("produto")
    plano = data.get("plano")
    if produto not in _PLANOS_CONFIG or plano not in _PLANOS_CONFIG[produto]:
        raise HTTPException(400, "Produto ou plano inválido")
    _PLANOS_CONFIG[produto][plano].update({k:v for k,v in data.items() if k not in ("produto","plano")})
    return {"ok": True, "config": _PLANOS_CONFIG[produto][plano]}

# ── ANALYTICS COMBINADO ──

@app.get("/admin/conversao")
def admin_conversao(
    db=Depends(get_db),
    dbc=Depends(get_contabil_db),
    user=Depends(get_current_user)
):
    # Platform: trial -> pago
    p_total_trial = db.execute(text("SELECT COUNT(*) as n FROM tenants WHERE plano = 'trial'")).fetchone().n
    p_total_pago = db.execute(text("SELECT COUNT(*) as n FROM tenants WHERE plano != 'trial' AND status = 'ativo'")).fetchone().n

    # Contábil: trial -> ativo
    c_total_trial = dbc.execute(_text2("SELECT COUNT(*) as n FROM tenants WHERE status = 'TRIAL'")).fetchone().n
    c_total_ativo = dbc.execute(_text2("SELECT COUNT(*) as n FROM tenants WHERE status = 'ACTIVE'")).fetchone().n

    total_clientes = p_total_pago + c_total_ativo
    total_trial = p_total_trial + c_total_trial

    return {
        "platform": {"trial": p_total_trial, "pago": p_total_pago,
                     "taxa_conversao": round(p_total_pago/(p_total_pago+p_total_trial)*100,1) if (p_total_pago+p_total_trial) > 0 else 0},
        "contabil": {"trial": c_total_trial, "ativo": c_total_ativo,
                     "taxa_conversao": round(c_total_ativo/(c_total_ativo+c_total_trial)*100,1) if (c_total_ativo+c_total_trial) > 0 else 0},
        "total_clientes_pagos": total_clientes,
        "total_trial": total_trial,
    }


# ── ASAAS INTEGRATION ──
import urllib.request as _ur
import json as _json

ASAAS_KEY = "$aact_prod_000MzkwODA2MWY2OGM3MWRlMDU2NWM3MzJlNzZmNGZhZGY6OmY3MTRjMjVmLTAwZjgtNDRkZS1hNjlhLTA2MmM2MjM0MDhiMTo6JGFhY2hfMzliMWViYTctMmQyYy00NTZiLTkzOTQtNGM5ZjY5YTdmODgz"
ASAAS_BASE = "https://api.asaas.com/v3"

def asaas_get(path: str, params: dict = {}):
    qs = "&".join(f"{k}={v}" for k,v in params.items())
    url = f"{ASAAS_BASE}{path}{'?'+qs if qs else ''}"
    req = _ur.Request(url, headers={"access_token": ASAAS_KEY, "Content-Type": "application/json"})
    with _ur.urlopen(req, timeout=10) as r:
        return _json.loads(r.read())

def asaas_post(path: str, payload: dict):
    url = f"{ASAAS_BASE}{path}"
    data = _json.dumps(payload).encode()
    req = _ur.Request(url, data=data, method="POST",
        headers={"access_token": ASAAS_KEY, "Content-Type": "application/json"})
    with _ur.urlopen(req, timeout=10) as r:
        return _json.loads(r.read())

@app.get("/asaas/subscriptions")
def asaas_subscriptions(user=Depends(get_current_user)):
    try:
        data = asaas_get("/subscriptions", {"limit": "100"})
        return data.get("data", [])
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/asaas/payments")
def asaas_payments(user=Depends(get_current_user)):
    try:
        data = asaas_get("/payments", {"limit": "100", "order": "desc"})
        return {"data": data.get("data", []), "total": data.get("totalCount", 0)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/asaas/payments/overdue")
def asaas_overdue(user=Depends(get_current_user)):
    try:
        data = asaas_get("/payments", {"status": "OVERDUE", "limit": "50"})
        return {"data": data.get("data", []), "total": data.get("totalCount", 0)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/asaas/mrr")
def asaas_mrr(user=Depends(get_current_user)):
    try:
        subs = asaas_get("/subscriptions", {"status": "ACTIVE", "limit": "100"})
        total_mrr = sum(s.get("value", 0) for s in subs.get("data", []))
        por_plano = {}
        for s in subs.get("data", []):
            desc = s.get("description", "")
            plano = "Outro"
            for p in ["STARTER", "PROFISSIONAL", "ENTERPRISE", "Starter", "Pro", "chamados", "completo"]:
                if p.upper() in desc.upper():
                    plano = p.upper()
                    break
            por_plano[plano] = por_plano.get(plano, 0) + s.get("value", 0)
        return {"mrr_total": total_mrr, "por_plano": por_plano,
                "total_assinaturas": subs.get("totalCount", 0)}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/asaas/churn")
def asaas_churn(user=Depends(get_current_user)):
    try:
        canceladas = asaas_get("/subscriptions", {"status": "CANCELLED", "limit": "100"})
        ativas = asaas_get("/subscriptions", {"status": "ACTIVE", "limit": "100"})
        total_cancel = canceladas.get("totalCount", 0)
        total_ativas = ativas.get("totalCount", 0)
        total = total_cancel + total_ativas
        churn_rate = round(total_cancel / total * 100, 1) if total > 0 else 0
        return {"canceladas": total_cancel, "ativas": total_ativas,
                "churn_rate": churn_rate, "detalhes": canceladas.get("data", [])[:10]}
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/asaas/projecao")
def asaas_projecao(user=Depends(get_current_user)):
    try:
        subs = asaas_get("/subscriptions", {"status": "ACTIVE", "limit": "100"})
        mrr = sum(s.get("value", 0) for s in subs.get("data", []))
        return {
            "mrr": mrr,
            "mes_1": mrr,
            "mes_2": round(mrr * 1.05, 2),
            "mes_3": round(mrr * 1.10, 2),
            "arr": round(mrr * 12, 2)
        }
    except Exception as e:
        raise HTTPException(500, str(e))

@app.get("/asaas/customers/{customer_id}/payments")
def asaas_customer_payments(customer_id: str, user=Depends(get_current_user)):
    try:
        data = asaas_get("/payments", {"customer": customer_id, "limit": "20", "order": "desc"})
        return data.get("data", [])
    except Exception as e:
        raise HTTPException(500, str(e))

# ── PLATFORM — MELHORIAS ──

@app.get("/tenants/{tenant_id}/stats")
def tenant_stats(tenant_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    """Stats detalhados de um tenant: limites, uso, último login"""
    tenant = db.execute(text("SELECT * FROM tenants WHERE id = :id"), {"id": tenant_id}).fetchone()
    if not tenant:
        raise HTTPException(404, "Tenant não encontrado")
    
    tickets_total = db.execute(text("SELECT COUNT(*) as n FROM tickets WHERE tenant_id = :id"), {"id": tenant_id}).fetchone().n
    tickets_abertos = db.execute(text("SELECT COUNT(*) as n FROM tickets WHERE tenant_id = :id AND status = 'aberto'"), {"id": tenant_id}).fetchone().n
    try:
        tickets_sla_vencido = db.execute(text("""
            SELECT COUNT(*) as n FROM tickets 
            WHERE tenant_id = :id AND status NOT IN ('resolvido','fechado')
            AND prazo_sla IS NOT NULL AND prazo_sla < NOW()
        """), {"id": tenant_id}).fetchone().n
    except:
        tickets_sla_vencido = 0
    
    usuarios_total = db.execute(text("SELECT COUNT(*) as n FROM users WHERE tenant_id = :id"), {"id": tenant_id}).fetchone().n
    ativos_total = db.execute(text("SELECT COUNT(*) as n FROM assets WHERE tenant_id = :id"), {"id": tenant_id}).fetchone().n
    try:
        ultimo_login = db.execute(text("""
            SELECT MAX(created_at) as ultimo FROM user_sessions WHERE tenant_id = :id
        """), {"id": tenant_id}).fetchone().ultimo
    except:
        ultimo_login = None
    ultimo_ticket = db.execute(text("""
        SELECT MAX(criado_em) as ultimo FROM tickets WHERE tenant_id = :id
    """), {"id": tenant_id}).fetchone().ultimo

    t = dict(tenant._mapping)
    limites = LIMITES_PLANO.get(t.get("plano","trial"), {})
    
    return {
        "tenant": t,
        "uso": {
            "tickets_total": tickets_total,
            "tickets_abertos": tickets_abertos,
            "tickets_sla_vencido": tickets_sla_vencido,
            "usuarios_total": usuarios_total,
            "ativos_total": ativos_total,
        },
        "limites": limites,
        "ultimo_login": str(ultimo_login) if ultimo_login else None,
        "ultimo_ticket": str(ultimo_ticket) if ultimo_ticket else None,
    }

@app.post("/tenants/{tenant_id}/reset-senha")
def tenant_reset_senha(tenant_id: str, db=Depends(get_db), user=Depends(get_current_user)):
    """Gera nova senha temporária para o admin do tenant"""
    import secrets, string
    nova_senha = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    hashed = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    
    admin = db.execute(text("""
        SELECT id, email FROM users WHERE tenant_id = :id AND role = 'admin' LIMIT 1
    """), {"id": tenant_id}).fetchone()
    
    if not admin:
        raise HTTPException(404, "Admin do tenant não encontrado")
    
    db.execute(text("UPDATE users SET password_hash = :h WHERE id = :id"),
               {"h": hashed, "id": admin.id})
    db.commit()
    return {"ok": True, "email": admin.email, "nova_senha": nova_senha}

@app.post("/tenants/{tenant_id}/email")
async def enviar_email_tenant(tenant_id: str, data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    """Envia e-mail direto para o admin do tenant"""
    tenant = db.execute(text("SELECT * FROM tenants WHERE id = :id"), {"id": tenant_id}).fetchone()
    if not tenant:
        raise HTTPException(404, "Tenant não encontrado")
    t = dict(tenant._mapping)
    
    admin = db.execute(text("SELECT email, nome FROM users WHERE tenant_id = :id AND role = 'admin' LIMIT 1"),
                       {"id": tenant_id}).fetchone()
    dest_email = admin.email if admin else t.get("email")
    
    import urllib.request as ur2, json as j2
    payload = j2.dumps({
        "from": "contato@nexusefbusiness.com.br",
        "to": [dest_email],
        "subject": data.get("assunto", "Mensagem da Nexus EF Business"),
        "html": f"<p>{data.get('mensagem','')}</p><br><small>Nexus EF Business — nexusefbusiness.com.br</small>"
    }).encode()
    req = ur2.Request("https://api.resend.com/emails", data=payload, method="POST",
        headers={"Authorization": "Bearer re_4FHQ6SYU_5WBE2MfqARXSBmuNQ7gPBqEh", "Content-Type": "application/json"})
    with ur2.urlopen(req, timeout=10) as r:
        result = j2.loads(r.read())
    return {"ok": True, "email_enviado_para": dest_email, "resend_id": result.get("id")}

# Contábil reset senha
@app.post("/contabil/tenants/{tenant_id}/reset-senha")
def contabil_reset_senha(tenant_id: str, dbc=Depends(get_contabil_db), user=Depends(get_current_user)):
    import secrets, string, hashlib
    nova_senha = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    hashed = bcrypt.hashpw(nova_senha.encode(), bcrypt.gensalt()).decode()
    
    admin = dbc.execute(_text2("""
        SELECT id, email FROM usuarios WHERE "tenantId" = :id AND role = 'ADMIN' LIMIT 1
    """), {"id": tenant_id}).fetchone()
    
    if not admin:
        raise HTTPException(404, "Admin não encontrado")
    
    dbc.execute(_text2('UPDATE usuarios SET senha = :h WHERE id = :id'),
                {"h": hashed, "id": admin.id})
    dbc.commit()
    return {"ok": True, "email": admin.email, "nova_senha": nova_senha}

@app.post("/contabil/tenants/{tenant_id}/email")
async def enviar_email_contabil(tenant_id: str, data: dict, dbc=Depends(get_contabil_db), user=Depends(get_current_user)):
    tenant = dbc.execute(_text2("SELECT * FROM tenants WHERE id = :id"), {"id": tenant_id}).fetchone()
    if not tenant:
        raise HTTPException(404, "Tenant não encontrado")
    t = dict(tenant._mapping)
    
    import urllib.request as ur2, json as j2
    payload = j2.dumps({
        "from": "contato@nexusefbusiness.com.br",
        "to": [t.get("email")],
        "subject": data.get("assunto", "Mensagem da Nexus EF Business"),
        "html": f"<p>Olá, <strong>{t.get('nome')}</strong>!</p><p>{data.get('mensagem','')}</p><br><small>Nexus EF Business — nexusefbusiness.com.br</small>"
    }).encode()
    req = ur2.Request("https://api.resend.com/emails", data=payload, method="POST",
        headers={"Authorization": "Bearer re_4FHQ6SYU_5WBE2MfqARXSBmuNQ7gPBqEh", "Content-Type": "application/json"})
    with ur2.urlopen(req, timeout=10) as r:
        result = j2.loads(r.read())
    return {"ok": True, "email_enviado_para": t.get("email"), "resend_id": result.get("id")}

# Observações e tags por cliente (Platform)
@app.patch("/tenants/{tenant_id}/observacoes")
def tenant_observacoes(tenant_id: str, data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    obs = data.get("observacoes","")
    tags = data.get("tags","")
    db.execute(text("""
        UPDATE tenants SET 
            observacoes = :obs,
            tags = :tags
        WHERE id = :id
    """), {"obs": obs, "tags": tags, "id": tenant_id})
    db.commit()
    return {"ok": True}

# Contábil — converter trial para pago
@app.post("/contabil/tenants/{tenant_id}/converter-trial")
def contabil_converter_trial(tenant_id: str, data: dict, dbc=Depends(get_contabil_db), user=Depends(get_current_user)):
    plano = data.get("plano", "STARTER")
    dbc.execute(_text2("""
        UPDATE tenants SET status = 'ACTIVE', plano = :plano, "updatedAt" = NOW()
        WHERE id = :id
    """), {"plano": plano, "id": tenant_id})
    dbc.commit()
    return {"ok": True, "plano_ativado": plano}

# Admin churn combinado
@app.get("/admin/churn")
def admin_churn(db=Depends(get_db), dbc=Depends(get_contabil_db), user=Depends(get_current_user)):
    # Platform cancelados no mês
    p_churn = db.execute(text("""
        SELECT COUNT(*) as n FROM tenants 
        WHERE ativo = false
        AND criado_em >= DATE_TRUNC('month', NOW())
    """)).fetchone().n
    # Contábil cancelados no mês  
    c_churn = dbc.execute(_text2("""
        SELECT COUNT(*) as n FROM tenants 
        WHERE status = 'CANCELLED'
        AND "updatedAt" >= DATE_TRUNC('month', NOW())
    """)).fetchone().n
    
    p_total = db.execute(text("SELECT COUNT(*) as n FROM tenants")).fetchone().n
    c_total = dbc.execute(_text2("SELECT COUNT(*) as n FROM tenants")).fetchone().n
    
    return {
        "platform": {"churn_mes": p_churn, "total": p_total, "rate": round(p_churn/p_total*100,1) if p_total>0 else 0},
        "contabil": {"churn_mes": c_churn, "total": c_total, "rate": round(c_churn/c_total*100,1) if c_total>0 else 0},
        "total_churn": p_churn + c_churn
    }


# ── CONTATOS E OBSERVAÇÕES POR CLIENTE ──
from sqlalchemy import Column, Integer, String, Text, DateTime

@app.get("/clientes/{cliente_id}/contatos")
def get_contatos(cliente_id: int, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        rows = db.execute(text("""
            SELECT id, tipo, nota, data, criado_em FROM contatos_cliente
            WHERE cliente_id = :id ORDER BY data DESC LIMIT 50
        """), {"id": cliente_id}).fetchall()
        return [dict(r._mapping) for r in rows]
    except:
        return []

@app.post("/clientes/{cliente_id}/contatos")
def add_contato(cliente_id: int, data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        db.execute(text("""
            INSERT INTO contatos_cliente (cliente_id, tipo, nota, data, criado_em)
            VALUES (:cid, :tipo, :nota, :data, NOW())
        """), {"cid": cliente_id, "tipo": data.get("tipo"), "nota": data.get("nota"), "data": data.get("data")})
        db.commit()
        return {"ok": True}
    except Exception as e:
        # Criar tabela se não existir
        db.execute(text("""
            CREATE TABLE IF NOT EXISTS contatos_cliente (
                id SERIAL PRIMARY KEY,
                cliente_id INTEGER,
                tipo TEXT,
                nota TEXT,
                data TIMESTAMP,
                criado_em TIMESTAMP DEFAULT NOW()
            )
        """))
        db.commit()
        db.execute(text("""
            INSERT INTO contatos_cliente (cliente_id, tipo, nota, data, criado_em)
            VALUES (:cid, :tipo, :nota, :data, NOW())
        """), {"cid": cliente_id, "tipo": data.get("tipo"), "nota": data.get("nota"), "data": data.get("data")})
        db.commit()
        return {"ok": True}

@app.patch("/clientes/{cliente_id}/observacoes")
def update_observacoes(cliente_id: int, data: dict, db=Depends(get_db), user=Depends(get_current_user)):
    try:
        db.execute(text("""
            UPDATE clientes SET observacoes = :obs, tags = :tags WHERE id = :id
        """), {"obs": data.get("observacoes",""), "tags": data.get("tags",""), "id": cliente_id})
        db.commit()
        return {"ok": True}
    except Exception as e:
        # Adicionar colunas se não existirem
        try:
            db.execute(text("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS observacoes TEXT"))
            db.execute(text("ALTER TABLE clientes ADD COLUMN IF NOT EXISTS tags TEXT"))
            db.commit()
            db.execute(text("UPDATE clientes SET observacoes=:obs, tags=:tags WHERE id=:id"),
                {"obs": data.get("observacoes",""), "tags": data.get("tags",""), "id": cliente_id})
            db.commit()
        except: pass
        return {"ok": True}

# ── CONFIG TRIAL ──
@app.patch("/config/trial")
def config_trial(data: dict, user=Depends(get_current_user)):
    dias = data.get("dias", 7)
    return {"ok": True, "trial_dias": dias, "mensagem": f"Trial configurado para {dias} dias (aplique no código para persistir)"}
