import streamlit as st
import pandas as pd
import numpy as np
import io
import xml.etree.ElementTree as ET

st.set_page_config(page_title="Comparación Perceptron Frontal vs Final", layout="wide")
st.title("📈 Comparación Perceptron Frontal vs Final")

# ------------------------- SECCIÓN 1: TXT a formato original vertical -------------------------
st.subheader("📄 Convertir archivo TXT de CMM a Excel (formato original vertical)")

archivo_txt = st.file_uploader("📤 Carga un archivo TXT de mediciones", type=["txt"], key="txt_vertical")

if archivo_txt:
    try:
        contenido = archivo_txt.read().decode("latin-1").splitlines()
        datos = []
        dim_actual = ""

        for linea in contenido:
            linea = linea.strip()

            if linea.startswith("DIM ") and "UNIDADES=MM" in linea:
                dim_actual = linea.split("=")[0].replace("DIM", "").strip()
                continue

            partes = linea.split()
            if len(partes) >= 7 and partes[0] in ['X', 'Y', 'Z', 'M', 'D', 'E']:
                try:
                    eje = partes[0]
                    med = float(partes[1])
                    nom = float(partes[2])
                    tol_plus = float(partes[3])
                    tol_minus = float(partes[4])
                    desv = float(partes[5])
                    fueratol = float(partes[6])

                    datos.append({
                        "Punto": dim_actual,
                        "Eje": eje,
                        "Nominal": nom,
                        "Tolerancia +": tol_plus,
                        "Tolerancia -": tol_minus,
                        "Medición": med,
                        "Desviación": desv,
                        "Fuera de Tolerancia": fueratol
                    })
                except ValueError:
                    continue

        df_txt = pd.DataFrame(datos)

        if df_txt.empty:
            st.warning("⚠️ No se detectaron datos. Revisa el formato del archivo.")
        else:
            st.success(f"✅ Archivo TXT procesado correctamente. {len(df_txt)} registros detectados.")
            st.dataframe(df_txt)

            buffer_txt = io.BytesIO()
            with pd.ExcelWriter(buffer_txt, engine="openpyxl") as writer:
                df_txt.to_excel(writer, index=False, sheet_name="CMM TXT")

            st.download_button(
                label="📥 Descargar Excel vertical",
                data=buffer_txt.getvalue(),
                file_name="Mediciones_vertical.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo TXT: {e}")

# ------------------------- SECCIÓN 2: TXT a formato horizontal actualizado -------------------------
st.subheader("📄 Convertir archivo TXT a formato horizontal (solo desviaciones)")

archivo_txt_hor = st.file_uploader("📤 Carga otro archivo TXT (para tabla horizontal)", type=["txt"], key="txt_horizontal")

if archivo_txt_hor:
    try:
        contenido = archivo_txt_hor.read().decode("latin-1").splitlines()
        datos = []
        registros = []

        dim_actual = ""
        jsn = psn = date = time = cycle_mode = ""
        station = model = ""

        for linea in contenido:
            linea = linea.strip()

            if "STATION=" in linea:
                station = linea.split("STATION=")[1].strip()
            if "MODEL=" in linea:
                model = linea.split("MODEL=")[1].strip()
            if "JSN=" in linea:
                jsn = linea.split("JSN=")[1].strip()
            if "PSN=" in linea:
                psn = linea.split("PSN=")[1].strip()
            if "FECHA=" in linea or "DATE=" in linea:
                date = linea.split("=")[1].strip()
            if "TIME=" in linea:
                time = linea.split("TIME=")[1].strip()
            if "CYCLE MODE=" in linea:
                cycle_mode = linea.split("CYCLE MODE=")[1].strip()

            if linea.startswith("DIM ") and "UNIDADES=MM" in linea:
                dim_actual = linea.split("=")[0].replace("DIM", "").strip()
                continue

            partes = linea.split()
            if len(partes) >= 7 and partes[0] in ['X', 'Y', 'Z']:
                try:
                    eje = partes[0]
                    desv = float(partes[5])
                    nombre_columna = f"{dim_actual}_{eje}"
                    datos.append((nombre_columna, desv))
                except ValueError:
                    continue

        fila = {
            "JSN": jsn,
            "PSN": psn,
            "Fecha": date,
            "Hora": time,
            "Estación": station,
            "Modelo": model
        }

        for nombre_col, valor in datos:
            fila[nombre_col] = valor

        df_horizontal = pd.DataFrame([fila])

        # ✅ FILTRAR SOLO LAS COLUMNAS DESEADAS
        columnas_deseadas = ['JSN', 'PSN', 'Fecha', 'Hora', 'Estación', 'Modelo',
                             '1000R_X', '1000R_Y', '1000R_Z']
        df_horizontal = df_horizontal[[col for col in columnas_deseadas if col in df_horizontal.columns]]

        if df_horizontal.empty:
            st.warning("⚠️ No se detectaron desviaciones para los puntos seleccionados.")
        else:
            st.success("✅ Archivo procesado correctamente con las desviaciones de 1000R.")
            st.dataframe(df_horizontal)

            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
                df_horizontal.to_excel(writer, index=False, sheet_name="Desviaciones_H")

            st.download_button(
                label="📥 Descargar Excel horizontal (1000R)",
                data=buffer.getvalue(),
                file_name="Desviaciones_1000R.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

    except Exception as e:
        st.error(f"❌ Error al procesar el archivo TXT: {e}")
