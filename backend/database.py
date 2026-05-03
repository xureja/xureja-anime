from sqlalchemy import create_engine, Column, Integer, String, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship

# Configuración de la base de datos (Usaremos SQLite para que sea fácil)
SQLALCHEMY_DATABASE_URL = "sqlite:///./anime_xureja.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# ==========================================
# TABLA 1: ANIMES
# ==========================================
class Anime(Base):
    __tablename__ = "animes"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String, unique=True, index=True)
    genero = Column(String)
    sinopsis = Column(String)
    portada = Column(String)
    vistas = Column(Integer, default=0)

    # Relación: Un anime tiene muchos episodios
    episodios = relationship("Episodio", back_populates="anime")

# ==========================================
# TABLA 2: EPISODIOS
# ==========================================
class Episodio(Base):
    __tablename__ = "episodios"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(Integer)
    anime_id = Column(Integer, ForeignKey("animes.id"))

    anime = relationship("Anime", back_populates="episodios")
    # Relación: Un episodio puede tener enlaces en varios servidores
    enlaces = relationship("Enlace", back_populates="episodio")

# ==========================================
# TABLA 3: ENLACES (SERVIDORES)
# ==========================================
class Enlace(Base):
    __tablename__ = "enlaces"

    id = Column(Integer, primary_key=True, index=True)
    servidor = Column(String)
    url = Column(String)
    episodio_id = Column(Integer, ForeignKey("episodios.id"))

    episodio = relationship("Episodio", back_populates="enlaces")

# ==========================================
# TABLA 4: USUARIOS (¡NUEVA!)
# ==========================================
class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    password = Column(String) # Aquí guardaremos la contraseña encriptada

# ==========================================
# TABLA 5: FAVORITOS (MI LISTA)
# ==========================================
class Favorito(Base):
    __tablename__ = "favoritos"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, index=True) # Guardaremos el username del usuario
    anime_id = Column(Integer, ForeignKey("animes.id"))

    # Relación para traer los datos del anime si los necesitamos luego
    anime = relationship("Anime")

# ==========================================
# FUNCIÓN PARA CREAR LAS TABLAS
# ==========================================

# ==========================================
# TABLA 6: PERFIL DE USUARIO
# ==========================================
class PerfilUsuario(Base):
    __tablename__ = "perfiles"

    id = Column(Integer, primary_key=True, index=True)
    usuario = Column(String, unique=True, index=True) # Lo enlazamos con el username
    biografia = Column(String, default="¡Hola! Soy un amante del anime. Aún no he escrito mi biografía.")
    avatar_url = Column(String, default="") # Si está vacío, usaremos el generador automático

def crear_base_de_datos():
    Base.metadata.create_all(bind=engine)