import io
import streamlit as st
import openai
from audiorecorder import audiorecorder
from st_audiorec import st_audiorec
import os

# Initialize your OpenAI client with your API key
client = openai.OpenAI(api_key=st.secrets["OPENAI_TOKEN"])
models_list = client.models.list().data

# Filter models owned by 'epfl-42' and get their ids
ft_openai_models = [model.id for model in models_list if model.owned_by == "epfl-42"]

st.write(ft_openai_models)

voices = ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']

sel_voice = st.radio("Select a voice", voices)
# Streamlit app layout
st.title("Text-to-Speech App")

# Text input for text-to-speech
input_text = st.text_area("Enter text for speech synthesis:")

if st.button("Convert to Speech"):
    if input_text:
        # Convert text to speech
        response = client.audio.speech.create(
            model="tts-1",
            voice=sel_voice,
            input=input_text,
        )

        # Convert the binary response content to a byte stream
        byte_stream = io.BytesIO(response.content)
        response.stream_to_file("stream_to_file.mp3")
        st.audio("stream_to_file.mp3", format='audio/mp3')

        # Display the audio file in the Streamlit app
        st.audio(byte_stream, format='audio/mp3')
    else:
        st.error("Please enter some text to convert.")


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
