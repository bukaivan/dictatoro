"""Controller failure tests; no microphone, clipboard or actual key injection."""
import os,sys
from pathlib import Path
from unittest.mock import Mock,patch
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['DICTATOR_DATA_DIR']=str(root/'.test-data/recording-failure-data')
import app
import numpy as np
from PySide6 import QtWidgets
qt=QtWidgets.QApplication([])
with patch.object(app.Window,'load_model'),patch.object(app,'get_ui_language',return_value='ru'),patch.object(app,'autostart_enabled',return_value=False),patch.object(app.Window,'bind'),patch.object(app.Window,'unhook'):
    w=app.Window();w.timer.stop();w.model=Mock()
    with patch.object(w,'start_recording') as start:
        w.handle_key(True);w.handle_key(True);assert start.call_count==1
    w.pressed=False;w.busy=True
    with patch.object(w,'start_recording') as start:
        w.handle_key(True);assert not start.called
    w.busy=False;w.pressed=False
    with patch.object(app.sd,'query_devices',side_effect=RuntimeError('device disconnected')):
        w.start_recording(manual=True);assert w.stream is None;assert 'device disconnected' in w.status.text()
    with patch.object(app.win32gui,'GetForegroundWindow',return_value=222),patch.object(app,'process_of',return_value=44),patch.object(app.keyboard,'send') as send,patch.object(app.win32clipboard,'OpenClipboard') as clipboard:
        w.on_result('saved words','',(111,33));assert w.text.toPlainText()=='saved words';assert not send.called and not clipboard.called
    w.stream=Mock();w.stream.stop.side_effect=RuntimeError('device unplugged')
    stream=w.stream;w.chunks=[np.zeros(16000,dtype=np.float32)];w.rate=16000;w.target=0;w.target_pid=0;w.audio_error=False
    with patch.object(w.pool,'submit') as submit:
        w.stop_recording();assert stream.close.called;assert submit.called;assert w.audio_error
    w.busy=False;w.quit_app()
print('PASS: key repeat, busy guard, missing microphone, focus change, disconnected-stream recovery')
