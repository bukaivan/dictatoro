"""Regression cases found during publication review; no real recording or registry writes."""
import os
from pathlib import Path
import sys
from unittest.mock import Mock, patch

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['DICTATOR_DATA_DIR']=str(root/'.test-data/release-failures')
import app
from core import validate_config, can_insert, add_english_terms
from mouse_hook import MouseHook
from PySide6 import QtCore, QtWidgets

assert validate_config({'ui_language':{}})['ui_language']=='ru'
assert not can_insert(1,1,7,0,0), 'Unknown process identity must not permit insertion'
assert not can_insert(1,1,7,8,9)
assert can_insert(1,1,7,8,8)
assert len(add_english_terms(''))<=1000
assert add_english_terms('Google').splitlines().count('Google')==1
for button,down,up,data in [('middle',0x207,0x208,0),('x1',0x20B,0x20C,1<<16),('x2',0x20B,0x20C,2<<16)]:
    callback=Mock();hook=MouseHook(button,callback)
    assert hook.dispatch(down,data) and hook.dispatch(up,data)
    assert [c.args[0] for c in callback.call_args_list]==[True,False]
    assert not hook.dispatch(down,data,flags=1)
    assert not hook.dispatch(0x201)  # left mouse button remains available

qt=QtWidgets.QApplication([])
with patch.object(app.Window,'load_model'),patch.object(app.Window,'bind'),patch.object(app.Window,'unhook'),patch.object(app,'autostart_enabled',return_value=False),patch.object(app,'get_ui_language',return_value='ru'),patch.object(app,'set_ui_language') as registry:
    w=app.Window();w.timer.stop()
    def select_english():
        blocker=QtCore.QSignalBlocker(w.ui_language_box)
        w.ui_language_box.setCurrentIndex(w.ui_language_box.findData('en'))
        del blocker
    select_english()
    with patch.object(w,'persist',side_effect=OSError('disk unavailable')):
        w.change_language()
    assert not registry.called
    assert w.config['ui_language']=='ru' and w.ui_language_box.currentData()=='ru'
    select_english()
    with patch.object(app,'set_ui_language',side_effect=PermissionError('registry denied')),patch.object(w,'persist') as save:
        w.change_language()
    assert save.call_count==2 and w.config['ui_language']=='ru'
    assert w.ui_language_box.currentData()=='ru'
    stream=Mock();stream.start.side_effect=RuntimeError('start failed');stream.close.side_effect=RuntimeError('close failed')
    w.model=Mock()
    with patch.object(app.sd,'query_devices',return_value={'default_samplerate':16000}),patch.object(app.sd,'InputStream',return_value=stream):
        w.start_recording(manual=True)
    assert w.stream is None and 'start failed' in w.status.text()
    stream.stop.side_effect=RuntimeError('disconnected')
    w.stream=stream;w.quit_app()
    assert w.stream is None and w.closing
print('PASS: unknown PID guard, invalid config, mouse dispatch, vocabulary, language rollback, microphone failure cleanup')
