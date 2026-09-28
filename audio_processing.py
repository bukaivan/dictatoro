"""Convert microphone PCM to Whisper's 16 kHz without multimedia codecs."""
import numpy as np


def prepare_speech(samples):
    """Raise quiet mono PCM before VAD; preserve silence, peaks and duration.

    A single bounded gain avoids pumping between words. This is level
    adjustment, not noise removal. Never attenuate already loud recordings.
    """
    audio = np.asarray(samples, dtype=np.float32)
    if audio.ndim != 1 or not np.all(np.isfinite(audio)):
        raise ValueError('Expected finite mono PCM')
    if not audio.size:
        return np.ascontiguousarray(audio)
    rms = float(np.sqrt(np.mean(audio.astype(np.float64) ** 2)))
    if not 1e-6 < rms < 0.001:
        return np.ascontiguousarray(audio)
    peak = float(np.max(np.abs(audio)))
    gain = min(100.0, 0.02 / rms, 0.95 / peak)
    if gain <= 1.0:
        return np.ascontiguousarray(audio)
    return np.ascontiguousarray(audio * np.float32(gain))


def resample_microphone(samples, source_rate, target_rate=16000):
    """Windowed-sinc antialias filter followed by interpolation of mono PCM.

    Input and output are normalized float32 samples. Work is done after release,
    not in the realtime microphone callback. No files or codecs are involved.
    """
    source_rate, target_rate = int(source_rate), int(target_rate)
    if not 8000 <= source_rate <= 384000 or not 8000 <= target_rate <= 384000:
        raise ValueError('Unsupported audio sample rate')
    audio = np.asarray(samples, dtype=np.float32)
    if audio.ndim != 1:
        raise ValueError('Expected mono PCM')
    if not np.all(np.isfinite(audio)):
        raise ValueError('Audio contains non-finite samples')
    if not len(audio) or source_rate == target_rate:
        return np.ascontiguousarray(audio)
    if source_rate > target_rate:
        ratio = target_rate / source_rate
        radius = int(np.ceil(32 / ratio))
        taps = np.arange(-radius, radius + 1, dtype=np.float64)
        cutoff = 0.94 * ratio
        kernel = cutoff * np.sinc(cutoff * taps) * np.kaiser(len(taps), 8.6)
        kernel /= kernel.sum()
        padded = np.pad(audio, radius, mode='reflect' if len(audio) > 1 else 'edge')
        audio = np.convolve(padded, kernel.astype(np.float32), mode='valid')
    count = max(1, int(round(len(audio) * target_rate / source_rate)))
    positions = np.arange(count, dtype=np.float64) * source_rate / target_rate
    return np.interp(positions, np.arange(len(audio)), audio).astype(np.float32)
