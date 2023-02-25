import ffmpeg_streaming
from ffmpeg_streaming import Formats, Bitrate, Representation, Size

video = ffmpeg_streaming.input('./deployment.mp4')
dash = video.dash(Formats.h264(video))

_240p = Representation(Size(426, 240), Bitrate(150 * 1024, 94 * 1024))
_360p = Representation(Size(640, 360), Bitrate(276 * 1024, 128 * 1024))
_720p = Representation(Size(1280, 720), Bitrate(2048 * 1024, 320 * 1024))

dash.representations(_240p, _360p, _720p)
dash.output('./dash.mpd')
