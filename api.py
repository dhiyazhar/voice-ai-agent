from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
import wave
import ffmpeg
import os

SAMPLING_RATE = 16000

output_dir = 'audio_buffers'
os.makedirs(output_dir, exist_ok=True)

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI(title="FastAPI RealTime Whisper Transcriber")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

def decode_webm_to_pcm(webm_data):
    try:
        process = (
            ffmpeg
            .input('pipe:0', format='webm')
            .output('pipe:1', format='wav', acodec='pcm_s16le', ar='16000', ac=1)
            .run_async(pipe_stdin=True, pipe_stdout=True, pipe_stderr=True)
        )
        pcm_data, _ = process.communicate(input=webm_data)
        logger.debug(f'convert PCM success.')
        return pcm_data
    except Exception as e:
        logger.error(f"Error decoding WebM: {e}")
        return None

@app.websocket('/ws')
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    client_id = str(id(websocket))[:8]
    logger.info(f"Client {client_id} terkoneksi via WebSocket.")

    buffer = b""
    accumulate = b""
    buffer_counter = 1

    while True:
        raw_bytes = await websocket.receive_bytes()
        logger.info(f"WebSocket -> Receiving data stream from client...")

        if not raw_bytes:
            print("Data not received.")
            break

        buffer += raw_bytes
        accumulate += buffer
        print(f"Len accumulate: {len(accumulate)}")

        # raw_path = os.path.join(output_dir, f'buffer_raw_{buffer_counter}.webm')
        # with open(raw_path, 'wb') as f:
        #     f.write(raw_bytes)  
        # logger.debug(f'Raw chunk written to {raw_path}')

        # buffer_test = decode_webm_to_pcm(buffer)
        # if buffer_test:
        #     filename = os.path.join(output_dir, f'buffer_test_{buffer_counter}.wav')
        #     with wave.open(filename, 'wb') as bufferfile:
        #         bufferfile.setsampwidth(2)
        #         bufferfile.setnchannels(1)
        #         bufferfile.setframerate(16000)
        #         bufferfile.writeframes(buffer_test[44:])
        #     logger.info(f'succesfully written to {filename}')
        #     buffer_counter += 1
        
        # print(buffer_counter)
        # buffer = b""  

        if len(accumulate) >= 200000:
            pcm_data = decode_webm_to_pcm(accumulate)
            if pcm_data:
                with wave.open('test.wav', 'wb') as audiofile:
                    audiofile.setsampwidth(2)  
                    audiofile.setnchannels(1)  
                    audiofile.setframerate(16000)  
                    audiofile.writeframes(pcm_data[44:])  
            accumulate = b"" 

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5000)