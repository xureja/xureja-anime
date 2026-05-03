// ==========================================
// LÓGICA DEL REPRODUCTOR DE VIDEO
// ==========================================
const apiBaseUrl = 'https://xureja-backend.onrender.com/api';

// 1. Inicialización al cargar la página
document.addEventListener('DOMContentLoaded', () => {
    const urlParams = new URLSearchParams(window.location.search);
    const animeName = urlParams.get('anime');
    const currentEp = parseInt(urlParams.get('ep'));

    if (!animeName || isNaN(currentEp)) {
        const titleEl = document.getElementById('video-title');
        titleEl.textContent = "Error: No se especificó el anime o el episodio en la URL.";
        titleEl.style.color = "red";
    } else {
        cargarReproductor(animeName, currentEp);
        cargarListaEpisodios(animeName, currentEp);
    }
});

// 2. Función para cargar el video y los servidores
function cargarReproductor(anime, ep) {
    fetch(`${apiBaseUrl}/reproductor/${anime}/${ep}`)
        .then(res => {
            if (!res.ok) throw new Error("Episodio no encontrado");
            return res.json();
        })
        .then(data => {
            document.getElementById('video-title').textContent = `${data.anime} - Episodio ${data.episodio}`;
            
            const serverList = document.getElementById('server-list');
            serverList.innerHTML = '<span>Servidores:</span>'; 
            
            if (data.servidores && data.servidores.length > 0) {
                // Seleccionar el primer servidor por defecto
                document.getElementById('video-iframe').src = data.servidores[0].url;

                data.servidores.forEach((srv, index) => {
                    const btn = document.createElement('button');
                    btn.className = `btn-server ${index === 0 ? 'active' : ''}`;
                    btn.textContent = srv.nombre;
                    
                    btn.onclick = (e) => {
                        document.getElementById('video-iframe').src = srv.url;
                        document.querySelectorAll('.btn-server').forEach(b => b.classList.remove('active'));
                        e.target.classList.add('active');
                    };
                    serverList.appendChild(btn);
                });
            } else {
                serverList.innerHTML += "<span style='color:red;'>No hay enlaces de video</span>";
            }
        })
        .catch(err => {
            document.getElementById('video-title').textContent = err.message;
        });
}

// 3. Función para cargar la lista lateral de episodios y REGISTRAR VISTAS
function cargarListaEpisodios(anime, currentEp) {
    fetch(`${apiBaseUrl}/anime/${anime}`)
        .then(res => res.json())
        .then(data => {
            // --- ¡NUEVO! REGISTRO INVISIBLE DE VISTAS ---
            // Revisamos si en esta sesión ya se le sumó una vista a este anime
            const vistaRegistrada = sessionStorage.getItem(`vista_${data.id}`);
            
            if (!vistaRegistrada && data.id) {
                fetch(`${apiBaseUrl}/vistas/registrar/${data.id}`, { method: 'POST' })
                    .then(r => r.json())
                    .then(resData => {
                        console.log(`¡Vista registrada! Total de vistas: ${resData.vistas_actuales}`);
                        // Lo marcamos en el navegador para no sumar vistas dobles si el usuario recarga la página
                        sessionStorage.setItem(`vista_${data.id}`, 'true');
                    })
                    .catch(err => console.error("Error al registrar vista:", err));
            }
            // ---------------------------------------------

            const listContainer = document.getElementById('episodes-list');
            listContainer.innerHTML = ''; 
            
            const episodios = data.episodios || [];
            
            episodios.forEach(epNum => {
                const isActive = epNum === currentEp ? 'active' : '';
                const itemHTML = `
                    <a href="reproductor.html?anime=${anime}&ep=${epNum}" class="ep-item ${isActive}">
                        <img src="${data.portada}" alt="Episodio ${epNum}">
                        <div class="ep-info">
                            <h4>Episodio ${epNum}</h4>
                        </div>
                    </a>
                `;
                listContainer.innerHTML += itemHTML;
            });

            // Lógica de navegación (Botones Anterior / Siguiente)
            const btnPrev = document.getElementById('btn-prev');
            const btnNext = document.getElementById('btn-next');
            const currentIndex = episodios.indexOf(currentEp);

            if (currentIndex > 0) {
                btnPrev.style.visibility = 'visible';
                btnPrev.href = `reproductor.html?anime=${anime}&ep=${episodios[currentIndex - 1]}`;
            } else {
                btnPrev.style.visibility = 'hidden';
            }

            if (currentIndex < episodios.length - 1) {
                btnNext.style.visibility = 'visible';
                btnNext.href = `reproductor.html?anime=${anime}&ep=${episodios[currentIndex + 1]}`;
            } else {
                btnNext.style.visibility = 'hidden';
            }
        })
        .catch(err => console.error("Error al cargar la lista de episodios:", err));
}