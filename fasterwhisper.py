from faster_whisper import WhisperModel

model_size = 'large-v3'

model = WhisperModel(model_size, device='cuda')

segments, info = model.transcribe('test.wav')

print("Detected language '%s' with probability %f" % (info.language, info.language_probability))
for segment in segments:
    print("[%.2fs -> %.2fs] %s" % (segment.start, segment.end, segment.text))