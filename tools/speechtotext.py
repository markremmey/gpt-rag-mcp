import os
import logging
import requests
import json
import io

from typing import Annotated, Any, Dict
from semantic_kernel.functions import kernel_function
from configuration import Configuration
from .base_plugin import BasePlugin

import azure.cognitiveservices.speech as speechsdk

class SpeechToTextPlugin(BasePlugin):
    """
    Speech To Text Plugin
    """

    def __init__(self, settings : Dict= {}):
        super().__init__(settings)

        config : Configuration = settings.get("config", {})

        self.name = "Speech To Text"
        self.description = "A plugin to process documents using Speech To Text API."
        self.speech_key = config.get_value("SPEECH_KEY", "YourSpeechKey")
        self.speech_region = config.get_value("SPEECH_REGION", "YourSpeechRegion")
        self.lang_id = settings.get("lang_id", "en-US")
    
    @kernel_function(
        name="process_sound_file",
        description="Will process a sound file and return the transcription.",
    )
    async def process_sound_file(self,
        documentUrl: Annotated[str, "The URL of the document."]
        ) -> Any:
        """
        Process a document using the Speech To Text API.
        """

        logging.info(f"[speech_process_document_url] Processing document: {documentUrl}")

        try:

            speech_config = speechsdk.SpeechConfig(subscription=self.speech_key, region=self.speech_region)

            #get the file name from the URL
            filename = documentUrl.split("/")[-1]
            
            #remove any query parameters from the filename
            if "?" in filename:
                filename = filename.split("?")[0]
            
            result = None

            try:
                with open(filename, "wb") as audio_file:
                    # Download the audio file from the URL using requests
                    audio_data = requests.get(documentUrl).content
                    audio_file.write(audio_data)

                    audio_config = speechsdk.AudioConfig(filename=filename)

                    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)
                    speech_recognition_result = speech_recognizer.recognize_once()
                    result = speech_recognition_result.text

            finally:
                try:
                    os.remove(filename)
                except Exception as e:
                    logging.error(f"Error removing file {filename}: {str(e)}")

            return result
            
        except Exception as e:
            return f"Error: {str(e)}"