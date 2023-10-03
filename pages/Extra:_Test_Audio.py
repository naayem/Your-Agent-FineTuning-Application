import streamlit as st
import openai
from audiorecorder import audiorecorder
from st_audiorec import st_audiorec
import os

########################################################################################################################
# TEST AUDIO
########################################################################################################################

audio_file_path = "audio.mp3"
transcript = None


def transcribe(audio_path):
    audio_path = open(audio_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_path)
    return transcript


with st.form("audio_recorder"):
    audio = audiorecorder("Click to record", "Click to stop recording")
    submitted = st.form_submit_button("Submit")
    if submitted:
        if not audio.empty():
            # To play audio in frontend:
            st.audio(audio.export(format='mp3').read())

            # Check if the file exists before deleting it
            if os.path.exists(audio_file_path):
                os.remove(audio_file_path)
                st.write(f"'{audio_file_path}' deleted successfully.")
            else:
                st.write(f"'{audio_file_path}' does not exist.")

            # To save audio to a file, use pydub export method:
            audio.export("audio.mp3", format="mp3")
            st.write("Transcription: ", transcribe("audio.mp3"))
            # To get audio properties, use pydub AudioSegment properties:
            st.write(
                f"Frame rate: {audio.frame_rate},"
                f"Frame width: {audio.frame_width}, Duration: {audio.duration_seconds} seconds"
                )

wav_audio_data = st_audiorec()

if wav_audio_data is not None:
    st.audio(wav_audio_data, format='audio/wav')
