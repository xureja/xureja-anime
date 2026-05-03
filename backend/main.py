from fastapi import FastAPI, HTTPException, Depends, Form
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional
from sqlalchemy.orm import Session
from passlib.context import CryptContext # <-- ¡Nueva herramienta de seguridad!
from database import SessionLocal, Anime, Episodio, Enlace, Usuario, Favorito, PerfilUsuario, crear_base_de_datos

# Aseguramos que las tablas existan
crear_base_de_datos()

app = FastAPI(title="API Xureja Anime")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuración para encriptar contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# RUTA 1: Inicio
@app.get("/api/inicio/animes")
def get_animes(db: Session = Depends(get_db)):
    return db.query(Anime).all()

# RUTA 2: Reproductor
@app.get("/api/reproductor/{titulo}/{num_ep}")
def get_video(titulo: str, num_ep: int, db: Session = Depends(get_db)):
    anime = db.query(Anime).filter(Anime.titulo.ilike(titulo)).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime no encontrado")
    
    episodio = db.query(Episodio).filter(Episodio.anime_id == anime.id, Episodio.numero == num_ep).first()
    if not episodio:
        raise HTTPException(status_code=404, detail="Episodio no encontrado")

    return {
        "anime": anime.titulo,
        "episodio": episodio.numero,
        "servidores": [{"nombre": e.servidor, "url": e.url} for e in episodio.enlaces]
    }

# RUTA 3: Panel Admin
@app.post("/api/admin/agregar_anime")
def agregar_anime_desde_web(
    titulo: str = Form(...), genero: str = Form(...), sinopsis: str = Form(...),
    portada: str = Form(...), numero_ep: int = Form(...), enlace_video: str = Form(...),
    servidor: str = Form("Principal"), db: Session = Depends(get_db)
):
    anime_existente = db.query(Anime).filter(Anime.titulo == titulo).first()
    if not anime_existente:
        anime_existente = Anime(titulo=titulo, genero=genero, sinopsis=sinopsis, portada=portada)
        db.add(anime_existente)
        db.commit()
        db.refresh(anime_existente)
    
    episodio_existente = db.query(Episodio).filter(Episodio.anime_id == anime_existente.id, Episodio.numero == numero_ep).first()
    if not episodio_existente:
        episodio_existente = Episodio(numero=numero_ep, anime_id=anime_existente.id)
        db.add(episodio_existente)
        db.commit()
        db.refresh(episodio_existente)

    nuevo_enlace = Enlace(servidor=servidor, url=enlace_video, episodio_id=episodio_existente.id)
    db.add(nuevo_enlace)
    db.commit()
    return {"mensaje": f"¡Contenido guardado con éxito! {titulo} - Episodio {numero_ep}"}

# RUTA 4: Detalles del Anime
@app.get("/api/anime/{titulo}")
def obtener_detalles_anime(titulo: str, db: Session = Depends(get_db)):
    anime = db.query(Anime).filter(Anime.titulo.ilike(titulo)).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime no encontrado")
    lista_episodios = sorted([ep.numero for ep in anime.episodios])
    return {
        "id": anime.id, # <-- ¡Añadimos el ID!
        "titulo": anime.titulo, 
        "genero": anime.genero, 
        "sinopsis": anime.sinopsis, 
        "portada": anime.portada, 
        "episodios": lista_episodios
    }

# RUTA 5: Buscador
@app.get("/api/buscar/{query}")
def buscar_anime(query: str, db: Session = Depends(get_db)):
    return db.query(Anime).filter(Anime.titulo.ilike(f"%{query}%")).all()

""""
# ==========================================
# RUTA 6: REGISTRO DE USUARIOS (¡NUEVA!)
# ==========================================
@app.post("/api/auth/registro")
def registrar_usuario(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Verificamos si el correo ya existe
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")
    
    # 2. Verificamos si el nombre de usuario ya existe
    if db.query(Usuario).filter(Usuario.username == username).first():
        raise HTTPException(status_code=400, detail="Este nombre de usuario ya está en uso.")

    """"""
    # 3. Encriptamos la contraseña y guardamos
    hashed_password = get_password_hash(password)
    nuevo_usuario = Usuario(username=username, email=email, password=hashed_password)
    

    db.add(nuevo_usuario)
    db.commit()
    
    return {"mensaje": "¡Registro exitoso! Redirigiendo..."}
"""

# ==========================================
# RUTA 6: REGISTRO DE USUARIOS (SIN ENCRIPTAR - SOLO PRUEBAS)
# ==========================================
@app.post("/api/auth/registro")
def registrar_usuario(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Verificamos si el correo ya existe
    if db.query(Usuario).filter(Usuario.email == email).first():
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")
    
    # 2. Verificamos si el nombre de usuario ya existe
    if db.query(Usuario).filter(Usuario.username == username).first():
        raise HTTPException(status_code=400, detail="Este nombre de usuario ya está en uso.")

    # 3. Guardamos al usuario con la contraseña en texto plano (sin encriptar)
    nuevo_usuario = Usuario(username=username, email=email, password=password)
    
    db.add(nuevo_usuario)
    db.commit()
    
    return {"mensaje": "¡Registro exitoso! Redirigiendo..."}

# ==========================================
# RUTA 7: INICIAR SESIÓN (LOGIN)
# ==========================================
@app.post("/api/auth/login")
def iniciar_sesion(
    username: str = Form(...), # <-- Cambiamos email por username
    password: str = Form(...),
    db: Session = Depends(get_db)
):
    # 1. Buscamos al usuario por su NOMBRE DE USUARIO en la base de datos
    usuario = db.query(Usuario).filter(Usuario.username == username).first()
    
    # 2. Si no existe, lanzamos error
    if not usuario:
        raise HTTPException(status_code=404, detail="El usuario no existe.")
    
    # 3. Comparamos la contraseña
    if usuario.password != password:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta.")
    
    # 4. Si todo está bien, le damos la bienvenida
    return {
        "mensaje": f"¡Bienvenido de vuelta, {usuario.username}!", 
        "username": usuario.username
    }

# ==========================================
# RUTA 8: EDITAR ANIME Y/O EPISODIO
# ==========================================
@app.put("/api/admin/editar_anime/{anime_id}")
def editar_anime(
    anime_id: int,
    titulo: str = Form(...),
    genero: str = Form(...),
    sinopsis: str = Form(...),
    portada: str = Form(...),
    numero_ep: Optional[int] = Form(None), 
    servidor: Optional[str] = Form(None),
    enlace_video: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    # 1. Actualizamos los datos generales del Anime
    anime = db.query(Anime).filter(Anime.id == anime_id).first()
    if not anime:
        raise HTTPException(status_code=404, detail="Anime no encontrado")
    
    anime.titulo = titulo
    anime.genero = genero
    anime.sinopsis = sinopsis
    anime.portada = portada
    
    # 2. Lógica inteligente para tu tabla separada de "Enlaces"
    if numero_ep is not None and enlace_video:
        nombre_servidor = servidor or "Principal"
        
        # A. Buscamos si el episodio ya existe, si no, lo creamos
        episodio = db.query(Episodio).filter(Episodio.anime_id == anime_id, Episodio.numero == numero_ep).first()
        if not episodio:
            episodio = Episodio(numero=numero_ep, anime_id=anime_id)
            db.add(episodio)
            db.flush() # Simula guardar para obtener el ID, pero sin bloquear el archivo

        # B. Ahora que tenemos el Episodio, buscamos o creamos su Enlace (video)
        enlace = db.query(Enlace).filter(Enlace.episodio_id == episodio.id, Enlace.servidor == nombre_servidor).first()
        
        if enlace:
            # Si ya existía este servidor para este episodio, solo actualizamos la URL
            enlace.url = enlace_video
        else:
            # Si no existía, creamos un nuevo enlace
            nuevo_enlace = Enlace(servidor=nombre_servidor, url=enlace_video, episodio_id=episodio.id)
            db.add(nuevo_enlace)

    # 3. Guardamos todos los cambios finales
    db.commit()
    
    return {"mensaje": f"¡'{titulo}' actualizado con éxito!"}

# ==========================================
# RUTA 9: SISTEMA DE FAVORITOS (MI LISTA)
# ==========================================
@app.post("/api/favoritos/toggle")
def toggle_favorito(
    username: str = Form(...),
    anime_id: int = Form(...),
    db: Session = Depends(get_db)
):
    # Buscamos si ya le dio corazón antes
    fav_existente = db.query(Favorito).filter(Favorito.usuario == username, Favorito.anime_id == anime_id).first()

    if fav_existente:
        # Si ya lo tiene, lo quitamos (Dislike)
        db.delete(fav_existente)
        db.commit()
        return {"mensaje": "Eliminado de tu lista", "estado": False}
    else:
        # Si no lo tiene, lo agregamos (Like)
        nuevo_fav = Favorito(usuario=username, anime_id=anime_id)
        db.add(nuevo_fav)
        db.commit()
        return {"mensaje": "Añadido a tu lista", "estado": True}

@app.get("/api/favoritos/check/{username}/{anime_id}")
def check_favorito(username: str, anime_id: int, db: Session = Depends(get_db)):
    # Revisa si el corazón debe ir rojo o gris al cargar la página
    fav = db.query(Favorito).filter(Favorito.usuario == username, Favorito.anime_id == anime_id).first()
    return {"es_favorito": fav is not None}

@app.get("/api/favoritos/lista/{username}")
def obtener_mi_lista(username: str, db: Session = Depends(get_db)):
    # Buscamos todos los favoritos de este usuario
    mis_favoritos = db.query(Favorito).filter(Favorito.usuario == username).all()
    
    lista_animes = []
    for fav in mis_favoritos:
        # Como relacionamos la tabla, podemos acceder a los datos del anime directamente
        anime = fav.anime
        if anime:
            lista_animes.append({
                "id": anime.id,
                "titulo": anime.titulo,
                "portada": anime.portada
            })
            
    return lista_animes

# ==========================================
# RUTA 10: ELIMINAR ANIME (PANEL ADMIN)
# ==========================================
@app.delete("/api/admin/anime/{anime_id}")
def eliminar_anime(anime_id: int, db: Session = Depends(get_db)):
    # 1. Buscamos el anime
    anime = db.query(Anime).filter(Anime.id == anime_id).first()
    
    if not anime:
        return {"error": "Anime no encontrado"}
    
    # 2. Limpieza de tablas relacionadas (Evita errores en la base de datos)
    db.query(Favorito).filter(Favorito.anime_id == anime_id).delete()
    db.query(Episodio).filter(Episodio.anime_id == anime_id).delete()
    
    # 3. Golpe final: Eliminamos el anime
    db.delete(anime)
    db.commit()
    
    return {"mensaje": "Anime eliminado con éxito"}

# ==========================================
# RUTA 11: OBTENER Y ACTUALIZAR PERFIL
# ==========================================
@app.get("/api/perfil/{username}")
def obtener_perfil(username: str, db: Session = Depends(get_db)):
    perfil = db.query(PerfilUsuario).filter(PerfilUsuario.usuario == username).first()
    
    # Si el usuario es nuevo y no tiene perfil creado en la tabla, se lo creamos invisiblemente
    if not perfil:
        perfil = PerfilUsuario(usuario=username)
        db.add(perfil)
        db.commit()
        db.refresh(perfil)
        
    return {"biografia": perfil.biografia, "avatar_url": perfil.avatar_url}

@app.post("/api/perfil/actualizar")
def actualizar_perfil(
    username: str = Form(...),
    biografia: str = Form(...),
    avatar_url: str = Form(""),
    db: Session = Depends(get_db)
):
    perfil = db.query(PerfilUsuario).filter(PerfilUsuario.usuario == username).first()
    if not perfil:
        perfil = PerfilUsuario(usuario=username)
        db.add(perfil)
        
    perfil.biografia = biografia
    perfil.avatar_url = avatar_url
    db.commit()
    
    return {"mensaje": "¡Perfil actualizado con éxito!"}

# ==========================================
# RUTA 12: REGISTRAR VISTA DE UN ANIME
# ==========================================
@app.post("/api/vistas/registrar/{anime_id}")
def registrar_vista(anime_id: int, db: Session = Depends(get_db)):
    anime = db.query(Anime).filter(Anime.id == anime_id).first()
    if anime:
        # Si el anime no tenía vistas registradas (por ser viejo), lo iniciamos en 0
        if anime.vistas is None:
            anime.vistas = 0
            
        anime.vistas += 1
        db.commit()
        return {"mensaje": "Vista registrada", "vistas_actuales": anime.vistas}
    return {"error": "Anime no encontrado"}

# ==========================================
# RUTA 13: OBTENER TOP TENDENCIAS (MÁS VISTOS)
# ==========================================
@app.get("/api/inicio/top-tendencias")
def obtener_top_tendencias(db: Session = Depends(get_db)):
    # Traemos los 5 animes con más vistas, de mayor a menor
    # .desc() significa "descendente" (el más grande primero)
    return db.query(Anime).order_by(Anime.vistas.desc()).limit(5).all()