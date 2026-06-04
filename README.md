
# 🤖 Agente de Ventas IA — GO4MORE

Sistema de inteligencia artificial diseñado para asistir a ejecutivos 
de ventas en la prospección de cursos de inglés, generando mensajes 
personalizados basados en la metodología comercial de GO4MORE.

---

## 📋 Descripción

Agente RAG (Retrieval-Augmented Generation) entrenado con el material 
de capacitación interno de GO4MORE: talleres de ventas, plantillas de 
prospección y grabaciones de cierres reales. Permite a los ejecutivos 
generar mensajes efectivos para cada situación de prospección en segundos.

---

## ✨ Características

- 🧠 Base de conocimiento vectorial con ChromaDB
- 💬 Generación de mensajes personalizados por contexto
- 📊 Dashboard con métricas de uso en tiempo real
- 📋 Historial completo de consultas por ejecutivo
- 📈 Gráficas de rendimiento con Chart.js
- 🔐 Sistema de autenticación con usuarios y contraseñas
- 📱 Interfaz responsive para móvil y escritorio
- 🌐 Deploy en la nube con Railway

---

## 🛠️ Tecnologías utilizadas

| Tecnología | Uso |
|------------|-----|
| Python | Lenguaje principal |
| Flask | Framework web |
| LangChain | Framework de IA |
| ChromaDB | Base de datos vectorial |
| HuggingFace | Modelo de embeddings |
| Groq (Llama 3.1) | Modelo de lenguaje |
| SQLite + SQLAlchemy | Base de datos de usuarios |
| Flask-Login | Autenticación |
| Chart.js | Visualización de métricas |
| Faster-Whisper | Transcripción de audio/video |
| Railway | Deploy en producción |

---

## 🏗️ Arquitectura del proyecto
AGENTE_VENTAS_IA/
├── app.py                  # Aplicación principal Flask
├── agente.py               # Configuración del agente RAG
├── auth.py                 # Autenticación y login
├── database.py             # Modelos de base de datos
├── transcribir.py          # Script de transcripción con Whisper
├── requirements.txt        # Dependencias del proyecto
├── Procfile               # Configuración para Railway
├── .env                   # Variables de entorno (no subir a Git)
├── Transcripciones/       # Material de entrenamiento del agente
│   ├── PLANTILLAS GO4MORE.txt
│   ├── PROSPECCION GO4MORE.txt
│   └── [talleres y grabaciones transcritas]
└── templates/             # Interfaces web
├── login.html
├── dashboard.html
├── index.html
├── historial.html
└── metricas.html

---

## 🚀 Instalación local

### Requisitos previos
- Python 3.10+
- Anaconda o Miniconda
- GPU NVIDIA (recomendado para transcripción)

### Pasos

**1. Clonar el repositorio:**
```bash
git clone https://github.com/Nihilus-tech/agente-ventas-ia.git
cd agente-ventas-ia
```

**2. Crear entorno virtual:**
```bash
conda create -n ventas_ia_pro python=3.10
conda activate ventas_ia_pro
```

**3. Instalar dependencias:**
```bash
pip install -r requirements.txt
```

**4. Configurar variables de entorno:**
Crea un archivo `.env` en la raíz del proyecto:
GROQ_API_KEY=tu_clave_de_groq

**5. Ejecutar la aplicación:**
```bash
python app.py
```

**6. Abrir en el navegador:**
http://127.0.0.1:5000/
---

## 🔄 Flujo de trabajo
Videos/Audios de capacitación
↓
transcribir.py (Faster-Whisper + GPU)
↓
Archivos .txt en carpeta Transcripciones
↓
ChromaDB (base vectorial)
↓
Agente RAG (LangChain + Groq)
↓
Interfaz web Flask
↓
Ejecutivo de ventas genera mensaje

---

## 📱 Capturas de pantalla

## ageregar imagenes capturas del sistema

---

## 🗺️ Roadmap

- [x] Transcripción automática de videos con GPU
- [x] Base de conocimiento vectorial
- [x] Agente RAG funcional
- [x] Interfaz web con autenticación
- [x] Dashboard de métricas
- [x] Historial de consultas
- [x] Deploy en producción
- [ ] Integración con WhatsApp Business API
- [ ] Análisis de sentimiento en conversaciones
- [ ] Panel de administración de usuarios
- [ ] Soporte multiempresa

---

## 👨‍💻 Desarrollado por

**Ilúvatar** — Desarrollador autodidacta  
GitHub: [@Nihilus-tech](https://github.com/Nihilus-tech)

---

## 📄 Licencia

MIT License — Ver archivo LICENSE para más detalles.