import socketio
from aiohttp import web
import os
import logging
import sys

# --- FORCE SYSTEM LOGGING ---
logging.basicConfig(level=logging.INFO, stream=sys.stdout,
                    format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

async def index(request):
    return web.Response(text="<h1>Walkie-Talkie Server is LIVE!</h1>", content_type='text/html')
app.router.add_get('/', index)

@sio.event
async def connect(sid, environ):
    logger.info(f"[+] NEW CONNECTION: {sid}")

@sio.event
async def disconnect(sid):
    logger.info(f"[-] DISCONNECTED: {sid}")

@sio.on('join_frequency')
async def handle_join(sid, frequency):
    freq_str = str(frequency)
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:
            # THE BUG WAS HERE: We must AWAIT the room leaving/entering!
            await sio.leave_room(sid, room)
            
    await sio.enter_room(sid, freq_str)
    logger.info(f"[ROOM] User {sid} securely locked into Frequency: {freq_str}")

@sio.on('voice_data')
async def handle_voice(sid, data):
    logger.info(f"[AUDIO] Server received data from {sid}, routing to others...")
    rooms = sio.rooms(sid)
    for freq in rooms:
        if freq != sid:
            await sio.emit('voice_receive', data, room=freq, skip_sid=sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    logger.info(f"🚀 SERVER AWAKE ON PORT {port} 🚀")
    web.run_app(app, port=port)
