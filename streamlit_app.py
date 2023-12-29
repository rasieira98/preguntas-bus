import streamlit as st
import pandas as pd
from sklearn.metrics import accuracy_score

def asignar_valor_fila(row):
    valores = {
        'A': row['respuesta_A'],
        'B': row['respuesta_B'],
        'C': row['respuesta_C'],
        'D': row['respuesta_D']
    }
    return valores.get(row['respuesta_correcta'], None)

def load_data(file):
    df = pd.read_csv(file, header=None,
                     names=['pregunta', 'respuesta_A', 'respuesta_B', 'respuesta_C', 'respuesta_D',
                            'respuesta_correcta'])

    df['respuesta_correcta_valor'] = df.apply(asignar_valor_fila, axis=1)
    return df

def main():
    st.title("Aplicación de Examen")

    uploaded_file = st.file_uploader("Cargar archivo CSV", type=["csv"])

    if uploaded_file is not None:
        st.sidebar.info("CSV cargado correctamente.")

        df = load_data(uploaded_file)

        if 'exam_questions' not in st.session_state:
            st.session_state.exam_questions = None
            st.session_state.user_responses = None
            st.session_state.correct_answers = None
            st.session_state.accuracy = None

        num_preguntas = st.sidebar.slider("Selecciona el número de preguntas", 1, len(df), len(df))

        # Always generate a new set of random questions when "Iniciar Examen" button is clicked
        if st.sidebar.button("Iniciar Examen"):
            st.session_state.exam_questions = df.sample(n=num_preguntas)  # Remove random_state for true randomness
            st.session_state.user_responses = {}
            st.session_state.correct_answers = st.session_state.exam_questions['respuesta_correcta_valor'].tolist()

        if st.session_state.exam_questions is not None:
            st.write(f"Comienza el examen con {num_preguntas} preguntas:")

            # Mostrar preguntas y recoger respuestas del usuario
            for index, row in st.session_state.exam_questions.iterrows():
                if len(row['pregunta'].split('#'))==2:
                    st.write(f"**Pregunta:** {row['pregunta'].split('#')[0]}")
                    st.image(f"{row['pregunta'].split('#')[1]}")
                else:
                    st.write(f"**Pregunta:** {row['pregunta']}")
                options = [row['respuesta_A'], row['respuesta_B'], row['respuesta_C'], row['respuesta_D']]
                selected_option = st.radio("Selecciona tu respuesta:", options, key=index)
                st.session_state.user_responses[index] = selected_option

            if st.button("Submit"):
                st.write("¡Examen completado!")

                # Calcular resultados
                user_answers = [st.session_state.user_responses[index] for index in st.session_state.exam_questions.index]
                st.session_state.accuracy = accuracy_score(st.session_state.correct_answers, user_answers)

                # Change the color of accuracy based on the threshold
                accuracy_color = "red" if st.session_state.accuracy < 0.5 else "green"

                st.write(f"Porcentaje de aciertos: <span style='color:{accuracy_color}'>{st.session_state.accuracy * 100:.2f}%</span>", unsafe_allow_html=True)

                # Mostrar resultados de cada pregunta
                results_df = pd.DataFrame({
                    'Pregunta': st.session_state.exam_questions['pregunta'],
                    'Respuesta Correcta': st.session_state.correct_answers,
                    'Tu Respuesta': user_answers,
                    'Correcto': [1 if c == u else 0 for c, u in zip(st.session_state.correct_answers, user_answers)]
                })

                # Set the width of the DataFrame
                st.dataframe(results_df, width=800)

                # Limpiar el estado para permitir un nuevo examen
                st.session_state.exam_questions = None
                st.session_state.user_responses = None
                st.session_state.correct_answers = None
                st.session_state.accuracy = None

if __name__ == "__main__":
    main()
