# Python packages
import os
import sys
projectRoot = os.path.abspath(os.path.join(os.path.dirname(__file__), '..')) 
sys.path.insert(0, projectRoot) # Set projectRoot as the working directory
import click
from fastapi import FastAPI
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel
import uvicorn
import pyttsx3 as tts

# Custom packages
from Common.CommonFunctions import ParseConfiguration
   
def InitializeTts(config):
    ttsEngine = tts.init()
    ttsEngine.setProperty('rate', config['ttsSettings']['speedOfSpeech']) # speed of speech
    ttsEngine.setProperty('volume', config['ttsSettings']['volume'])  # volume level (0.0 to 1.0)
    voices = ttsEngine.getProperty('voices') # get available voices
    voiceIndex = config['ttsSettings']['speaker'] # select speaker
    try:
        ttsEngine.setProperty('voice', voices[voiceIndex].id)  # change index to select different voice  
    except Exception:
        ttsEngine.setProperty('voice', voices[0].id)
        print(f"Warning: Invalid voice index. Default voice selected.")
    return ttsEngine

def TtsServer(config):
    
    # Initialize fast api server.
    serverApp = FastAPI()
    
    class TextRequest(BaseModel):
        transcription: str

    # handle requests
    @serverApp.post("/tts")
    def TtsGenerateAudio(request: TextRequest):
              
        try:
            # Initialize text to speech engine.
            ttsEngine = InitializeTts(config)
            
            filePath = 'ttsSample.wav'          
            ttsEngine.save_to_file(request.transcription, filePath)
            ttsEngine.runAndWait()        

            return FileResponse(filePath, media_type='application/wav', filename=filePath)
 
        except Exception as e:
            return JSONResponse(content={"error": str(e)}, status_code=500)    
        
    uvicorn.run(serverApp, host=config["server"]["host"], port=config["server"]["port"])
    
@click.command()
@click.option('--c', help="YAML configuration file")
def main(c):
    config = ParseConfiguration(c)
    TtsServer(config)
    
# main
if __name__ == "__main__":
    main()