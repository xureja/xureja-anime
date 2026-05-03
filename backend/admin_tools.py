from database import SessionLocal, Anime, Episodio, Enlace, crear_base_de_datos

def agregar_contenido():
    db = SessionLocal()
    titulo_nuevo = "One Piece" 
    
    # Comprueba si el anime ya existe
    existe = db.query(Anime).filter(Anime.titulo == titulo_nuevo).first()
    
    if not existe:
        nuevo = Anime(
            titulo=titulo_nuevo, 
            genero="Shonen", 
            sinopsis="Aventura pirata", 
            portada="assets/img/hero-bg.jpg" # Asegúrate de que esta imagen exista en tu frontend
        )
        db.add(nuevo)
        db.commit()
        db.refresh(nuevo)

        ep = Episodio(numero=1100, anime_id=nuevo.id)
        db.add(ep)
        db.commit()
        db.refresh(ep)

        db.add(Enlace(servidor="Mega", url="https://www.youtube.com/embed/dQw4w9WgXcQ", episodio_id=ep.id))
        db.commit()
        print(f"✅ '{titulo_nuevo}' añadido correctamente a la base de datos.")
    else:
        print(f"ℹ️ '{titulo_nuevo}' ya existe en la base de datos.")
    
    db.close()

if __name__ == "__main__":
    crear_base_de_datos()
    agregar_contenido()