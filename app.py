import sqlite3
from datetime import datetime
import pandas as pd
import streamlit as st
from google import genai

# Configuración de la página
st.set_page_config(
    page_title="Asistente 360° - Excelencia Personal",
    page_icon="⚡",
    layout="wide",
)

# --- CONFIGURACIÓN DE BASE DE DATOS SQLITE ---
conn = sqlite3.connect("asistente_360.db", check_same_thread=False)
cursor = conn.cursor()

# Crear tablas si no existen
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS finanzas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT, categoria TEXT, monto REAL, fecha TEXT, descripcion TEXT
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS agenda (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, hora TEXT, tarea TEXT, prioridad TEXT, estado TEXT
    )
"""
)
cursor.execute(
    """
    CREATE TABLE IF NOT EXISTS notas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fecha TEXT, categoria TEXT, contenido TEXT
    )
"""
)
conn.commit()

# --- BARRA LATERAL (CONFIGURACIÓN Y GEMINI) ---
st.sidebar.title("⚡ Control Central")
api_key = st.sidebar.text_input(
    "API Key de Gemini", type="password", help="Ingresa tu clave de la API de Gemini"
)

menu = st.sidebar.selectbox(
    "Navegación",
    [
        "🏠 Dashboard Ejecutivo",
        "💰 Finanzas & Pagos",
        "📅 Agenda & Tiempo",
        "🏋️ Nutrición & Bienestar",
        "🧠 Bitácora & IA",
    ],
)

# Inicializar cliente Gemini si hay API Key
client = None
if api_key:
  try:
    client = genai.Client(api_key=api_key)
  except Exception as e:
    st.sidebar.error(f"Error al conectar con Gemini: {e}")

# --- 1. DASHBOARD EJECUTIVO ---
if menu == "🏠 Dashboard Ejecutivo":
  st.title("🚀 Panel de Control - Hombre Ideal & Negocios")
  st.markdown(
      "Bienvenido a tu centro de comando operativo. Visualiza tu rendimiento y"
      " estado general de hoy."
  )

  col1, col2, col3 = st.columns(3)

  # Calcular totales financieros rápidos
  df_fin = pd.read_sql_query("SELECT * FROM finanzas", conn)
  total_ingresos = (
      df_fin[df_fin["tipo"] == "Ingreso"]["monto"].sum()
      if not df_fin.empty
      else 0
  )
  total_egresos = (
      df_fin[df_fin["tipo"] == "Egreso"]["monto"].sum()
      if not df_fin.empty
      else 0
  )
  balance = total_ingresos - total_egresos

  col1.metric("Balance Financiero", f"${balance:,.2f}")
  col2.metric("Ingresos Totales", f"${total_ingresos:,.2f}")
  col3.metric("Egresos Totales", f"${total_egresos:,.2f}")

  st.divider()

  # Resumen de IA del día
  st.subheader("🤖 Análisis Matutino del Asistente IA")
  if st.button("Generar Resumen de Enfoque Diario"):
    if client:
      with st.spinner("Analizando tus registros y preparando directrices..."):
        # Recopilar contexto de notas y finanzas
        notas_df = pd.read_sql_query("SELECT * FROM notas", conn)
        contexto_notas = (
            "\n".join(notas_df["contenido"].tail(5).tolist())
            if not notas_df.empty
            else "Sin notas recientes."
        )

        prompt = f"""
                Actúa como mi mentor de alto rendimiento, asesor financiero y coach de vida personal. 
                Basado en mis registros recientes y estas notas guardadas:
                {contexto_notas}
                
                Dame un reporte ejecutivo breve y contundente para hoy que incluya:
                1. 3 prioridades de alto valor para enfocar mi día como empresario.
                2. Un consejo rápido de optimización financiera.
                3. Una directriz de nutrición/disciplina física.
                Sé directo, motivador y sumamente exigente con la excelencia.
                """
        response = client.models.generate_content(
            model="gemini-2.5-flash", contents=prompt
        )
        st.success(response.text)
    else:
      st.warning(
          "Por favor, ingresa tu API Key de Gemini en la barra lateral para"
          " activar el coaching de IA."
      )

# --- 2. FINANZAS Y CONTABILIDAD BÁSICA ---
elif menu == "💰 Finanzas & Pagos":
  st.title("💰 Módulo Financiero y Contabilidad")

  tab1, tab2 = st.tabs(["📊 Registrar Movimiento", "📅 Ver Historial y Balances"])

  with tab1:
    with st.form("form_finanzas"):
      tipo = st.selectbox("Tipo de Movimiento", ["Ingreso", "Egreso"])
      categoria = st.selectbox(
          "Categoría",
          [
              "Ventas/Negocio",
              "Gastos Fijos (Servicios/Alquiler)",
              "Alimentación",
              "Inversión",
              "Lujos/Otros",
          ],
      )
      monto = st.number_input("Monto ($)", min_value=0.0, step=10.0)
      fecha = st.date_input("Fecha", datetime.today())
      descripcion = st.text_input("Descripción / Proveedor / Notas")

      submitted = st.form_submit_button("Guardar Movimiento")
      if submitted:
        cursor.execute(
            "INSERT INTO finanzas (tipo, categoria, monto, fecha, descripcion)"
            " VALUES (?, ?, ?, ?, ?)",
            (tipo, categoria, monto, str(fecha), descripcion),
        )
        conn.commit()
        st.success("¡Movimiento registrado con éxito!")

  with tab2:
    st.subheader("Historial de Transacciones")
    df_fin = pd.read_sql_query("SELECT * FROM finanzas", conn)
    st.dataframe(df_fin, use_container_width=True)

# --- 3. AGENDA Y TIEMPO ---
elif menu == "📅 Agenda & Tiempo":
  st.title("📅 Agenda, Time Blocking y Tareas")

  col1, col2 = st.columns([1, 2])

  with col1:
    st.subheader("Nueva Tarea / Evento")
    with st.form("form_agenda"):
      fecha_tarea = st.date_input("Fecha de Actividad", datetime.today())
      hora_tarea = st.time_input("Hora")
      tarea = st.text_input("Actividad (Ej: Bloque de Trabajo Profundo)")
      prioridad = st.selectbox("Prioridad", ["Alta (HVT)", "Media", "Baja"])
      submit_tarea = st.form_submit_button("Agendar")

      if submit_tarea:
        cursor.execute(
            "INSERT INTO agenda (fecha, hora, tarea, prioridad, estado)"
            " VALUES (?, ?, ?, ?, ?)",
            (
                str(fecha_tarea),
                str(hora_tarea),
                tarea,
                prioridad,
                "Pendiente",
            ),
        )
        conn.commit()
        st.success("Actividad agendada.")

  with col2:
    st.subheader("Tu Agenda Programada")
    df_agenda = pd.read_sql_query(
        "SELECT * FROM agenda ORDER BY fecha, hora", conn
    )
    st.dataframe(df_agenda, use_container_width=True)

# --- 4. NUTRICIÓN Y BIENESTAR ---
elif menu == "🏋️ Nutrición & Bienestar":
  st.title("🏋️ Optimización Física y Nutricional")
  st.markdown(
      "Controla tus pilares biológicos para sostener un rendimiento empresarial"
      " de alto nivel."
  )

  col1, col2 = st.columns(2)
  with col1:
    st.info(
        "**Rutina de Fuerza & Gimnasio:**\n- 5 días de hipertrofia.\n- Sesión"
        " de sauna post-entreno.\n- Suplementación: Creatina, Magnesio,"
        " Multivitamínico."
    )
  with col2:
    st.success(
        "**Enfoque Nutricional Diario:**\n- Alta ingesta proteica limpia.\n-"
        " Hidratación estricta (mínimo 3.5L).\n- Control de azúcares y grasas"
        " saturadas."
    )

  st.divider()
  st.subheader("Asesoría Nutricional con IA")
  meta_actual = st.text_input(
      "¿Cómo te sientes hoy o qué ajuste nutricional/energético necesitas?",
      placeholder=(
          "Ej: Tengo un día muy pesado de reuniones, ¿qué debería desayunar"
          " para mantener el foco?"
      ),
  )
  if st.button("Consultar con el Coach de Nutrición IA") and client:
    with st.spinner("Consultando recomendaciones..."):
      prompt_nutricion = f"""
            Actúa como mi especialista en nutrición deportiva y rendimiento cognitivo. 
            Mi situación/pregunta actual es: {meta_actual}
            Dame un consejo preciso, directo y enfocado en maximizar mi energía mental y rendimiento físico.
            """
      res = client.models.generate_content(
          model="gemini-2.5-flash", contents=prompt_nutricion
      )
      st.write(res.text)

# --- 5. BITÁCORA Y ALIMENTACIÓN DE IA ---
elif menu == "🧠 Bitácora & IA":
  st.title("🧠 Bitácora de Conocimiento (Alimenta tu IA)")
  st.markdown(
      "Escribe aquí tus ideas de negocio, pensamientos, aprendizajes o"
      " reflexiones. Esta base de datos interna le da contexto a tu asistente"
      " personal para conocerte mejor."
  )

  with st.form("form_bitacora"):
    categoria_nota = st.selectbox(
        "Categoría",
        [
            "Idea de Negocio",
            "Aprendizaje/Libro",
            "Reflexión Personal",
            "Estrategia",
        ],
    )
    contenido_nota = st.text_area(
        "Escribe tu nota o pensamiento aquí...", height=150
    )
    guardar_nota = st.form_submit_button("Guardar en la Memoria del Sistema")

    if guardar_nota and contenido_nota:
      cursor.execute(
          "INSERT INTO notas (fecha, categoria, contenido) VALUES (?, ?, ?)",
          (str(datetime.today()), categoria_nota, contenido_nota),
      )
      conn.commit()
      st.success("¡Nota guardada! Tu asistente IA la usará en futuros análisis.")

  st.divider()
  st.subheader("Notas Guardadas Recientemente")
  df_notas = pd.read_sql_query(
      "SELECT fecha, categoria, contenido FROM notas ORDER BY id DESC", conn
  )
  for index, row in df_notas.iterrows():
    with st.expander(f"[{row['categoria']}] - {row['fecha']}"):
      st.write(row["contenido"])

  st.divider()
  st.subheader("💬 Chat Libre con tu Asistente 360°")
  pregunta_libre = st.text_input(
      "Hazle una consulta general a tu asistente IA sobre negocios,"
      " organización o estrategia:"
  )
  if st.button("Enviar Pregunta") and client:
    with st.spinner("Pensando..."):
      # Extraer contexto de notas previas
      notas_df = pd.read_sql_query("SELECT contenido FROM notas", conn)
      contexto = (
          "\n".join(notas_df["contenido"].tolist()) if not notas_df.empty else ""
      )

      prompt_chat = f"""
            Eres mi asistente personal, contador analítico y mentor de alto rendimiento. Con base en mis notas y reflexiones previas:
            {contexto}
            
            Responde a la siguiente consulta del usuario con absoluta profesionalidad, franqueza y orientación a resultados:
            {pregunta_libre}
            """
      respuesta_chat = client.models.generate_content(
          model="gemini-2.5-flash", contents=prompt_chat
      )
      st.markdown("### Respuesta del Asistente:")
      st.write(respuesta_chat.text)
