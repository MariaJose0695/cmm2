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

        # Convertir lista a diccionario (agrupado por fila de JSN)
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

        # 🔴 FILTRAR SOLO LAS COLUMNAS DESEADAS
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
