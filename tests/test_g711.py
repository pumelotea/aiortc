import sys

from aiortc.codecs import PCMA_CODEC, PCMU_CODEC, get_decoder, get_encoder
from aiortc.codecs.g711 import PcmaDecoder, PcmaEncoder, PcmuDecoder, PcmuEncoder
from aiortc.jitterbuffer import JitterFrame

from .codecs import CodecTestCase

# silence
PCMA_PAYLOAD = b"\xd5" * 160
PCMU_PAYLOAD = b"\xff" * 160


class PcmaTest(CodecTestCase):
    def test_decoder(self) -> None:
        decoder = get_decoder(PCMA_CODEC)
        self.assertIsInstance(decoder, PcmaDecoder)

        frames = decoder.decode(JitterFrame(data=PCMA_PAYLOAD, timestamp=0))
        self.assertEqual(len(frames), 1)
        frame = frames[0]
        self.assertAudioFrame(
            frame,
            data=(b"\x08\x00" if sys.byteorder == "little" else b"\x00\x08") * 160,
            layout="mono",
            pts=0,
            samples=160,
            sample_rate=8000,
        )

    def test_encoder_mono_8khz(self) -> None:
        encoder = get_encoder(PCMA_CODEC)
        self.assertIsInstance(encoder, PcmaEncoder)

        for frame in self.create_audio_frames(
            layout="mono", sample_rate=8000, count=10
        ):
            payloads, timestamp = encoder.encode(frame)
            self.assertEqual(payloads, [PCMA_PAYLOAD])
            self.assertEqual(timestamp, frame.pts)

    def test_encoder_stereo_8khz(self) -> None:
        encoder = get_encoder(PCMA_CODEC)
        self.assertIsInstance(encoder, PcmaEncoder)

        for frame in self.create_audio_frames(
            layout="stereo", sample_rate=8000, count=10
        ):
            payloads, timestamp = encoder.encode(frame)
            self.assertEqual(payloads, [PCMA_PAYLOAD])
            self.assertEqual(timestamp, frame.pts)

    def test_encoder_stereo_48khz(self) -> None:
        encoder = get_encoder(PCMA_CODEC)
        self.assertIsInstance(encoder, PcmaEncoder)

        output = [
            encoder.encode(frame)
            for frame in self.create_audio_frames(
                layout="stereo", sample_rate=48000, count=10
            )
        ]
        self.assertEqual(
            output,
            [
                ([], None),  # No output due to buffering.
                ([PCMA_PAYLOAD], 0),
                ([PCMA_PAYLOAD], 160),
                ([PCMA_PAYLOAD], 320),
                ([PCMA_PAYLOAD], 480),
                ([PCMA_PAYLOAD], 640),
                ([PCMA_PAYLOAD], 800),
                ([PCMA_PAYLOAD], 960),
                ([PCMA_PAYLOAD], 1120),
                ([PCMA_PAYLOAD], 1280),
            ],
        )

    def test_encoder_pack(self) -> None:
        encoder = get_encoder(PCMA_CODEC)
        self.assertTrue(isinstance(encoder, PcmaEncoder))

        packet = self.create_packet(payload=PCMA_PAYLOAD, pts=1)
        payloads, timestamp = encoder.pack(packet)
        self.assertEqual(payloads, [PCMA_PAYLOAD])
        self.assertEqual(timestamp, 8)

    def test_roundtrip(self) -> None:
        self.roundtrip_audio(PCMA_CODEC, layout="mono", sample_rate=8000)

    def test_roundtrip_with_loss(self) -> None:
        self.roundtrip_audio(PCMA_CODEC, layout="mono", sample_rate=8000, drop=[1])


class PcmuTest(CodecTestCase):
    def test_decoder(self) -> None:
        decoder = get_decoder(PCMU_CODEC)
        self.assertIsInstance(decoder, PcmuDecoder)

        frames = decoder.decode(JitterFrame(data=PCMU_PAYLOAD, timestamp=0))
        self.assertEqual(len(frames), 1)
        frame = frames[0]
        self.assertAudioFrame(
            frame,
            data=b"\x00\x00" * 160,
            layout="mono",
            pts=0,
            samples=160,
            sample_rate=8000,
        )

    def test_encoder_mono_8khz(self) -> None:
        encoder = get_encoder(PCMU_CODEC)
        self.assertIsInstance(encoder, PcmuEncoder)

        for frame in self.create_audio_frames(
            layout="mono", sample_rate=8000, count=10
        ):
            payloads, timestamp = encoder.encode(frame)
            self.assertEqual(payloads, [PCMU_PAYLOAD])
            self.assertEqual(timestamp, frame.pts)

    def test_encoder_stereo_8khz(self) -> None:
        encoder = get_encoder(PCMU_CODEC)
        self.assertIsInstance(encoder, PcmuEncoder)

        for frame in self.create_audio_frames(
            layout="stereo", sample_rate=8000, count=10
        ):
            payloads, timestamp = encoder.encode(frame)
            self.assertEqual(payloads, [PCMU_PAYLOAD])
            self.assertEqual(timestamp, frame.pts)

    def test_encoder_stereo_48khz(self) -> None:
        encoder = get_encoder(PCMU_CODEC)
        self.assertIsInstance(encoder, PcmuEncoder)

        output = [
            encoder.encode(frame)
            for frame in self.create_audio_frames(
                layout="stereo", sample_rate=48000, count=10
            )
        ]
        self.assertEqual(
            output,
            [
                ([], None),  # No output due to buffering
                ([PCMU_PAYLOAD], 0),
                ([PCMU_PAYLOAD], 160),
                ([PCMU_PAYLOAD], 320),
                ([PCMU_PAYLOAD], 480),
                ([PCMU_PAYLOAD], 640),
                ([PCMU_PAYLOAD], 800),
                ([PCMU_PAYLOAD], 960),
                ([PCMU_PAYLOAD], 1120),
                ([PCMU_PAYLOAD], 1280),
            ],
        )

    def test_roundtrip(self) -> None:
        self.roundtrip_audio(PCMU_CODEC, layout="mono", sample_rate=8000)

    def test_roundtrip_with_loss(self) -> None:
        self.roundtrip_audio(PCMU_CODEC, layout="mono", sample_rate=8000, drop=[1])
