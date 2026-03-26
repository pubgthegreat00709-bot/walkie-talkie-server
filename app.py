import socketio
from aiohttp import web
import os

# 1. Setup the Server
# We allow all origins (*) so your PC can connect from home
sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# 2. When a user chooses a frequency
@sio.on('join_frequency')
async def handle_join(sid, frequency):
    # Leave old frequencies first
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:
            sio.leave_room(sid, room)
    
    sio.enter_room(sid, str(frequency))
    print(f"User {sid} joined frequency: {frequency}")

# 3. When voice data arrives, send it ONLY to people on the same frequency
@sio.on('voice_data')
async def handle_voice(sid, data):
    # Get the user's current frequency (room)
    rooms = sio.rooms(sid)
    for frequency in rooms:
        if frequency != sid:
            # Broadcast to everyone in this room except the speaker
            await sio.emit('voice_receive', data, room=frequency, skip_sid=sid)

if __name__ == '__main__':
    # Render provides a 'PORT' environment variable we must use
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, port=port)
