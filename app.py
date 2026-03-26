import socketio
from aiohttp import web
import os

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

# Track how many people are talking on each frequency
# Format: { "100.5": 2 }
active_talkers = {}

@sio.on('join_frequency')
async def handle_join(sid, frequency):
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:
            sio.leave_room(sid, room)
    sio.enter_room(sid, str(frequency))

@sio.on('start_talking')
async def start_talking(sid, frequency):
    freq = str(frequency)
    active_talkers[freq] = active_talkers.get(freq, 0) + 1
    # If more than 1 person is talking, tell everyone on that frequency to BEEP
    if active_talkers[freq] > 1:
        await sio.emit('collision', True, room=freq)

@sio.on('stop_talking')
async def stop_talking(sid, frequency):
    freq = str(frequency)
    active_talkers[freq] = max(0, active_talkers.get(freq, 1) - 1)
    if active_talkers[freq] <= 1:
        await sio.emit('collision', False, room=freq)

@sio.on('voice_data')
async def handle_voice(sid, data):
    rooms = sio.rooms(sid)
    for freq in rooms:
        if freq != sid:
            await sio.emit('voice_receive', data, room=freq, skip_sid=sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    web.run_app(app, port=port)
