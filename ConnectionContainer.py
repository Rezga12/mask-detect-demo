from aiortc import MediaStreamTrack, RTCPeerConnection, RTCSessionDescription
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from OpenCVStreamTrack import OpenCVStreamTrack


def register_handlers(connection, mode):
    @connection.on('track')
    def on_track(track):
        print('track received')
        print(type(track))
        transformed_track = OpenCVStreamTrack(track, mode)
        connection.addTrack(transformed_track)
        pass


class ConnectionContainer:
    def __init__(self):
        self.connections = []

    async def handle_offer(self, sdp, mode):

        connection = RTCPeerConnection()
        self.connections.append(connection)
        register_handlers(connection, mode)

        offer = RTCSessionDescription(sdp, type='offer')
        await connection.setRemoteDescription(offer)

        answer = await connection.createAnswer()
        await connection.setLocalDescription(answer)

        return answer

