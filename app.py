import socketio
from aiohttp import web
import os

sio = socketio.AsyncServer(async_mode='aiohttp', cors_allowed_origins='*')
app = web.Application()
sio.attach(app)

active_talkers = {}
packet_counters = {}

# --- STARTUP CHECK ---
print("=============================================", flush=True)
print("🚀 DIY WALKIE-TALKIE SERVER IS AWAKE 🚀", flush=True)
print("=============================================", flush=True)

@sio.event
async def connect(sid, environ):
    print(f">>> [NETWORK] User connected: {sid}", flush=True)

@sio.event
async def disconnect(sid):
    print(f"<<< [NETWORK] User disconnected: {sid}", flush=True)

@sio.on('join_frequency')
async def handle_join(sid, frequency):
    freq_str = str(frequency)
    rooms = sio.rooms(sid)
    for room in rooms:
        if room != sid:
            sio.leave_room(sid, room)
    sio.enter_room(sid, freq_str)
    print(f"[ROOM] User {sid} locked into Frequency: {freq_str}", flush=True)

@sio.on('start_talking')
async def start_talking(sid, frequency):
    freq = str(frequency)
    active_talkers[freq] = active_talkers.get(freq, 0) + 1
    print(f"[MIC OPEN] {sid} talking on {freq}. Total talkers: {active_talkers[freq]}", flush=True)
    if active_talkers[freq] > 1:
        await sio.emit('collision', True, room=freq)

@sio.on('stop_talking')
async def stop_talking(sid, frequency):
    freq = str(frequency)
    active_talkers[freq] = max(0, active_talkers.get(freq, 1) - 1)
    print(f"[MIC CLOSED] {sid} stopped. Total talkers: {active_talkers[freq]}", flush=True)
    if active_talkers[freq] <= 1:
        await sio.emit('collision', False, room=freq)

@sio.on('voice_data')
async def handle_voice(sid, data):
    packet_counters[sid] = packet_counters.get(sid, 0) + 1
    if packet_counters[sid] % 10 == 0:
        print(f"[AUDIO TRACE] Server received 10 packets from {sid}...", flush=True)

    rooms = sio.rooms(sid)
    for freq in rooms:
        if freq != sid:
            await sio.emit('voice_receive', data, room=freq, skip_sid=sid)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting web server on port {port}...", flush=True)
    web.run_app(app, port=port)
