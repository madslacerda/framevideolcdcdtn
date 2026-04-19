import streamlit as st
import cv2
import os
import tempfile
import zipfile
import numpy as np

st.title("Video Frame Extraction")

st.write("Upload a video and extract frames at user-defined time intervals.")

video_file = st.file_uploader(
    "Select a video file",
    type=["mp4", "avi", "mov", "mkv"]
)

start_time = st.number_input(
    "Initial time (s)",
    min_value=0.0,
    value=0.0
)

interval = st.number_input(
    "Frame interval (s)",
    min_value=0.1,
    value=1.0
)

num_frames = st.number_input(
    "Number of frames",
    min_value=1,
    value=10
)

if video_file is not None:

    # Save uploaded video temporarily
    tfile = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
    tfile.write(video_file.read())
    tfile.close()

    video = cv2.VideoCapture(tfile.name)

    if not video.isOpened():
        st.error("Error opening video file.")
    else:

        fps = video.get(cv2.CAP_PROP_FPS)

        if fps == 0:
            st.error("Unable to detect video FPS.")
        else:

            output_folder = tempfile.mkdtemp()

            saved_frames = []

            if st.button("Extract Frames"):

                progress = st.progress(0)

                for i in range(int(num_frames)):

                    current_time = start_time + i * interval
                    frame_number = int(current_time * fps)

                    video.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

                    success, frame = video.read()

                    if not success:
                        st.warning(f"Frame not found at {current_time:.2f} s")
                        continue

                    filename = os.path.join(
                        output_folder,
                        f"frame_{i+1}.jpg"
                    )

                    cv2.imwrite(filename, frame)

                    saved_frames.append(filename)

                    st.image(
                        frame,
                        caption=f"Frame {i+1} ({current_time:.2f} s)",
                        channels="BGR"
                    )

                    progress.progress((i + 1) / num_frames)

                video.release()

                # Create ZIP file
                zip_path = os.path.join(output_folder, "frames.zip")

                with zipfile.ZipFile(zip_path, "w") as zipf:
                    for f in saved_frames:
                        zipf.write(f, os.path.basename(f))

                with open(zip_path, "rb") as f:

                    st.download_button(
                        label="Download frames (ZIP)",
                        data=f,
                        file_name="frames.zip",
                        mime="application/zip"
                    )

                st.success("Extraction completed successfully.")
