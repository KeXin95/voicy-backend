
---
title: Audiogen
emoji: 🏢
colorFrom: gray
colorTo: purple
sdk: docker
pinned: false
---

Check out the configuration reference at https://huggingface.co/docs/hub/spaces-config-reference


### Run the Docker Container

```bash
docker run -e FISH_AUDIO_API_KEY=your_api_key_here -p 7860:7860 weihong869/audiogen
```

Service will be available at:
👉 http://localhost:7860

If running the backend directly (e.g., Flask/FastAPI), it may be at:
👉 http://127.0.0.1:5001

### 🧪 Example Request
```curl -X POST -F "cid=bafkreicyxa77q63asy4j7p6wxoth5bn3e7kblhskyk7g67txcb7xwuqdfa" \
  -F "text=Hello, this is the text to synthesize" http://127.0.0.1:5001/api/voice-transfer --output cloned_voice.mp3
```

This will save the generated voice file as `cloned_voice.mp3`.
