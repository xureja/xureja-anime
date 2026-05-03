document.addEventListener('DOMContentLoaded', () => {
    
    // ==========================================
    // 1. DIRECTORIO Y BUSCADOR (Páginas que NO son el inicio)
    // ==========================================
    // Evitamos que esto se ejecute en la página principal para que no haya conflictos
    const gridAnimes = document.querySelector('.grid-animes:not(#recomendaciones-inicio):not(#contenedor-mi-lista)');
    
    if (gridAnimes) {
        const params = new URLSearchParams(window.location.search);
        const searchQuery = params.get('search');
        let urlFetch = 'http://127.0.0.1:8000/api/inicio/animes'; 
        
        if (searchQuery) {
            urlFetch = `http://127.0.0.1:8000/api/buscar/${encodeURIComponent(searchQuery)}`;
        }

        fetch(urlFetch)
            .then(res => res.json())
            .then(animes => {
                gridAnimes.innerHTML = ''; 

                if (searchQuery && animes.length === 0) {
                    gridAnimes.innerHTML = `
                    <div style="grid-column: 1 / -1; text-align: center; color: #aaa; padding: 50px;">
                        <p style="font-size: 1.2rem; margin-bottom: 10px;">😕 No se encontraron resultados para "${searchQuery}".</p>
                        <p>Intenta con otra palabra clave o haz clic en "Inicio" para ver todo el catálogo.</p>
                    </div>`;
                    return;
                }
                
                animes.forEach(anime => {
                    gridAnimes.innerHTML += `
                    <article class="anime-card" onclick="window.location.href='anime.html?name=${encodeURIComponent(anime.titulo)}'">
                        <div class="img-container">
                            <img src="${anime.portada}" alt="${anime.titulo}">
                            <div class="anime-overlay"><span>Ver Detalles</span></div>
                        </div>
                        <h3>${anime.titulo}</h3>
                    </article>`;
                });
            })
            .catch(err => {
                console.error("Error cargando la cartelera:", err);
                gridAnimes.innerHTML = '<p style="color:red; text-align:center; width:100%;">Error al conectar con el servidor.</p>';
            });
    }

    // ==========================================
    // 2. HERO DINÁMICO, RECOMENDACIONES Y ÚLTIMOS CAPÍTULOS
    // ==========================================
    const recomendacionesInicio = document.getElementById('recomendaciones-inicio');
    const episodiosInicio = document.getElementById('episodios-inicio');
    
    // Variables para el Hero Banner
    const heroBanner = document.getElementById('hero-banner');
    const heroTitle = document.getElementById('hero-title');
    const heroSynopsis = document.getElementById('hero-synopsis');
    const heroLink = document.getElementById('hero-link');
    
    if (recomendacionesInicio && episodiosInicio) {
        fetch('http://127.0.0.1:8000/api/inicio/animes')
            .then(res => res.json())
            .then(animes => {
                recomendacionesInicio.innerHTML = ''; 
                episodiosInicio.innerHTML = '';
                
                if (animes.length === 0) {
                    recomendacionesInicio.innerHTML = '<p style="color: #aaa;">No hay animes publicados aún.</p>';
                    episodiosInicio.innerHTML = '<p style="color: #aaa;">No hay episodios publicados aún.</p>';
                    if(heroTitle) heroTitle.textContent = "Bienvenido a Xureja Anime";
                    return;
                }

                // Invertimos la lista para tener los más nuevos al principio
                const animesNuevos = animes.reverse();

                // ----------------------------------------------------
                // A) LÓGICA DEL BANNER DINÁMICO (CARRUSEL)
                // ----------------------------------------------------
                if (heroBanner) {
                    // Tomamos los 3 más recientes para el carrusel
                    const animesCarrusel = animesNuevos.slice(0, 3);
                    let indiceActual = 0;

                    function actualizarBanner() {
                        const animeActual = animesCarrusel[indiceActual];
                        
                        heroTitle.textContent = animeActual.titulo;
                        
                        // Si la sinopsis es muy larga, la cortamos para que no rompa el diseño
                        let sinopsisCorta = animeActual.sinopsis;
                        if (sinopsisCorta.length > 180) {
                            sinopsisCorta = sinopsisCorta.substring(0, 180) + '...';
                        }
                        heroSynopsis.textContent = sinopsisCorta;
                        
                        heroLink.href = `reproductor.html?anime=${encodeURIComponent(animeActual.titulo)}&ep=1`;
                        
                        // Le pasamos la URL de la foto a la variable de CSS
                        heroBanner.style.setProperty('--bg-image', `url('${animeActual.portada}')`);

                        // Avanzamos al siguiente anime (y si llegamos al final, volvemos al 0)
                        indiceActual = (indiceActual + 1) % animesCarrusel.length;
                    }

                    // Ejecutamos la primera vez y luego cada 5 segundos (5000 ms)
                    actualizarBanner();
                    setInterval(actualizarBanner, 5000);
                }

                // ----------------------------------------------------
                // B) LÓGICA DE TARJETAS (ARRIBA Y ABAJO)
                // ----------------------------------------------------
                animesNuevos.forEach(anime => {
                    // Recomendaciones (Arriba)
                    const urlDetalles = `anime.html?name=${encodeURIComponent(anime.titulo)}`;
                    recomendacionesInicio.innerHTML += `
                        <a href="${urlDetalles}" style="text-decoration: none; color: inherit;">
                            <article class="anime-card">
                                <div class="img-container">
                                    <img src="${anime.portada}" alt="${anime.titulo}">
                                    <div class="anime-overlay"><span>Ver Detalles</span></div>
                                </div>
                                <h3 style="margin-top: 10px; color: white;">${anime.titulo}</h3>
                            </article>
                        </a>
                    `;

                    // Últimos Capítulos (Abajo)
                    const urlReproductor = `reproductor.html?anime=${encodeURIComponent(anime.titulo)}&ep=1`;
                    episodiosInicio.innerHTML += `
                        <a href="${urlReproductor}" style="text-decoration: none; color: inherit;">
                            <article class="episode-card">
                                <div class="episode-img-wrapper">
                                    <img src="${anime.portada}" alt="${anime.titulo}">
                                    <div class="play-icon">▶</div>
                                </div>
                                <div class="episode-info">
                                    <h3>${anime.titulo}</h3>
                                    <p>Episodio 1</p>
                                </div>
                            </article>
                        </a>
                    `;
                });
            })
            .catch(error => console.error("Error cargando el inicio:", error));
    }

    // ==========================================
    // 3. CARGA DINÁMICA: PÁGINA DE DETALLES (anime.html)
    // ==========================================
    const animeContent = document.getElementById('anime-content');
    const loadingMessage = document.getElementById('loading-message');
    
    if (animeContent && loadingMessage) {
        const params = new URLSearchParams(window.location.search);
        const animeName = params.get('name');

        if (!animeName) {
            loadingMessage.textContent = "Error: No se especificó el anime en la URL.";
            loadingMessage.style.color = "red";
        } else {
            fetch(`http://127.0.0.1:8000/api/anime/${encodeURIComponent(animeName)}`)
            .then(res => {
                if (!res.ok) throw new Error("Anime no encontrado en la base de datos");
                return res.json();
            })
            .then(data => {
                loadingMessage.style.display = 'none';
                animeContent.style.display = 'block';

                document.getElementById('anime-title').textContent = data.titulo;
                document.getElementById('anime-genre').textContent = data.genero;
                document.getElementById('anime-synopsis').textContent = data.sinopsis;
                document.getElementById('anime-cover').src = data.portada;

                // --- LÓGICA DEL BOTÓN DE FAVORITOS ---
                const btnFav = document.getElementById('btn-fav');
                const usuarioActual = localStorage.getItem('usuarioXureja');

                if (btnFav && usuarioActual) {
                    btnFav.style.display = 'inline-block'; // Mostramos el botón
                    
                    // 1. Al cargar, preguntamos a Python si ya es favorito
                    fetch(`http://127.0.0.1:8000/api/favoritos/check/${usuarioActual}/${data.id}`)
                        .then(r => r.json())
                        .then(favData => {
                            if (favData.es_favorito) {
                                btnFav.innerHTML = '❤️ Quitar de Mi Lista';
                                btnFav.classList.add('active'); // CSS lo vuelve naranja
                            }
                        });

                    // 2. ¿Qué pasa cuando hacemos clic en el botón?
                    btnFav.onclick = () => {
                        const formData = new FormData();
                        formData.append('username', usuarioActual);
                        formData.append('anime_id', data.id);

                        btnFav.innerHTML = '⏳ Cargando...';

                        fetch('http://127.0.0.1:8000/api/favoritos/toggle', {
                            method: 'POST',
                            body: formData
                        })
                        .then(r => r.json())
                        .then(res => {
                            if (res.estado) {
                                // Se añadió a favoritos
                                btnFav.innerHTML = '❤️ Quitar de Mi Lista';
                                btnFav.classList.add('active');
                            } else {
                                // Se quitó de favoritos
                                btnFav.innerHTML = '🤍 Añadir a Mi Lista';
                                btnFav.classList.remove('active');
                            }
                        });
                    };
                }
                // -------------------------------------

                const episodesGrid = document.getElementById('episodes-grid');
                if (data.episodios.length === 0) {
                    episodesGrid.innerHTML = '<p style="color:#aaa; grid-column: 1/-1;">Aún no hay episodios subidos para este anime.</p>';
                } else {
                    data.episodios.forEach(numEp => {
                        const btn = document.createElement('a');
                        btn.className = 'btn-episode';
                        btn.textContent = `Episodio ${numEp}`;
                        
                        // Enlaza correctamente al reproductor
                        btn.href = `reproductor.html?anime=${encodeURIComponent(data.titulo)}&ep=${numEp}`;
                        
                        episodesGrid.appendChild(btn);
                    });
                }
            })
            .catch(err => {
                console.error(err);
                loadingMessage.textContent = "Error: No se pudo cargar la información de la base de datos.";
                loadingMessage.style.color = "red";
            });
        }
    }

    // ==========================================
    // 4. BUSCADOR GLOBAL (Input en la NavBar)
    // ==========================================
    const searchInput = document.querySelector('input[placeholder="Buscar anime..."]');
    
    if (searchInput) {
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault(); 
                const query = this.value.trim();
                
                if (query.length > 0) {
                    window.location.href = `index.html?search=${encodeURIComponent(query)}`;
                } else {
                    window.location.href = 'index.html';
                }
            }
        });
    }

    // ==========================================
    // 5. MANEJO DE SESIÓN EN LA INTERFAZ (PERFIL MEJORADO)
    // ==========================================
    const btnLoginNormal = document.getElementById('btn-login-header');
    const userProfileMenu = document.getElementById('user-profile-menu');
    const navUsername = document.getElementById('nav-username');
    const userAvatarImg = document.getElementById('user-avatar-img');
    const btnLogout = document.getElementById('btn-logout-dropdown');
    const navAdmin = document.getElementById('nav-admin'); 
    
    const usuarioActual = localStorage.getItem('usuarioXureja');

    if (usuarioActual) {
        // 1. Si hay sesión, ocultamos el botón viejo de login
        if (btnLoginNormal) btnLoginNormal.style.display = 'none';
        
        // 2. Mostramos el nuevo menú de perfil
        if (userProfileMenu) {
            userProfileMenu.style.display = 'flex';
            navUsername.textContent = usuarioActual;
            
            // MAGIA: Generamos un avatar dinámico basado en su nombre
            // Si el usuario es "gonzalez", le dará un personaje de anime; si es "xureja", le dará otro distinto.
            userAvatarImg.src = `https://api.dicebear.com/7.x/adventurer/svg?seed=${usuarioActual}&backgroundColor=ff6b00`;
        }

        // 3. Lógica para el botón rojo de cerrar sesión del desplegable
        if (btnLogout) {
            btnLogout.addEventListener('click', function(e) {
                e.preventDefault(); 
                localStorage.removeItem('usuarioXureja');
                window.location.href = 'index.html'; 
            });
        }
    } else {
        // Si NO hay sesión, nos aseguramos de que el perfil esté oculto
        if (btnLoginNormal) btnLoginNormal.style.display = 'inline-block';
        if (userProfileMenu) userProfileMenu.style.display = 'none';
    }

    // Lógica para mostrar el panel Admin solo al jefe
    if (navAdmin) {
        const nombreDelJefe = 'gonzalez'; 
        if (usuarioActual === nombreDelJefe) {
            navAdmin.style.display = 'inline-block';
        } else {
            navAdmin.style.display = 'none';
        }
    }

    // ==========================================
    // 6. CARGAR TOP TENDENCIAS
    // ==========================================
    const contenedorTop = document.getElementById('top-tendencias');
    
    if (contenedorTop) {
        fetch('http://127.0.0.1:8000/api/inicio/top-tendencias')
            .then(res => res.json())
            .then(animes => {
                contenedorTop.innerHTML = '';
                
                if (animes.length === 0) {
                    contenedorTop.innerHTML = '<p class="loading-text">Aún no hay datos de tendencias.</p>';
                    return;
                }

                animes.forEach(anime => {
                    const urlDetalles = `anime.html?name=${encodeURIComponent(anime.titulo)}`;
                    contenedorTop.innerHTML += `
                        <a href="${urlDetalles}" class="anime-card-link">
                            <article class="anime-card">
                                <div class="img-container">
                                    <div class="vistas-badge">👁️ ${anime.vistas || 0}</div>
                                    <img src="${anime.portada}" alt="${anime.titulo}">
                                    <div class="anime-overlay"><span>Ver Detalles</span></div>
                                </div>
                                <h3>${anime.titulo}</h3>
                            </article>
                        </a>
                    `;
                });
            })
            .catch(err => console.error("Error cargando tendencias:", err));
    }
});

