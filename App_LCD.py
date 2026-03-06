import streamlit as st
import os
import opencv_python
import tempfile
import zipfile

st.title("Extração de Frames de Vídeo")

st.write("Faça upload de um vídeo e extraia frames em intervalos definidos.")

# Upload do vídeo
video_file = st.file_uploader("Selecione o vídeo", type=["mp4","avi","mov","mkv"])

tempo_inicial = st.number_input("Tempo inicial (s)", min_value=0.0, value=0.0)
intervalo = st.number_input("Intervalo entre frames (s)", min_value=0.1, value=1.0)
num_frames = st.number_input("Número de frames", min_value=1, value=10)

if video_file is not None:

    # Salva vídeo temporariamente
    tfile = tempfile.NamedTemporaryFile(delete=False)
    tfile.write(video_file.read())

    video = cv2.VideoCapture(tfile.name)

    if not video.isOpened():
        st.error("Erro ao abrir o vídeo.")

    else:

        fps = video.get(cv2.CAP_PROP_FPS)

        pasta_saida = tempfile.mkdtemp()

        frames_salvos = []

        if st.button("Extrair Frames"):

            for i in range(num_frames):

                tempo_atual = tempo_inicial + i * intervalo
                numero_frame = int(tempo_atual * fps)

                video.set(cv2.CAP_PROP_POS_FRAMES, numero_frame)

                sucesso, frame = video.read()

                if not sucesso:
                    st.warning(f"Não foi possível extrair o frame no tempo {tempo_atual}s")
                    continue

                nome_arquivo = os.path.join(pasta_saida, f"frame_{i+1}.jpg")
                cv2.imwrite(nome_arquivo, frame)

                frames_salvos.append(nome_arquivo)

                st.image(frame, caption=f"Frame {i+1} ({tempo_atual:.2f}s)", channels="BGR")

            video.release()

            # Criar ZIP para download
            zip_path = os.path.join(pasta_saida, "frames.zip")

            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for f in frames_salvos:
                    zipf.write(f, os.path.basename(f))

            with open(zip_path, "rb") as f:
                st.download_button(
                    label="Baixar frames (ZIP)",
                    data=f,
                    file_name="frames.zip",
                    mime="application/zip"
                )


            st.success("Extração concluída.")


