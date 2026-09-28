"""Exercise settings persistence and actual recording-completion dispatch without a microphone."""
import os
import sys
import json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch, Mock
root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
os.environ['DICTATOR_DATA_DIR'] = str(root / '.test-data/translation-test-data')
import app
from core import validate_config
from PySide6 import QtWidgets
import numpy as np
assert validate_config({})['translate_to_english'] is False
assert validate_config({'translate_to_english': 'false'})['translate_to_english'] is False
assert validate_config({'translate_to_english': True})['translate_to_english'] is True
qt = QtWidgets.QApplication([])
with patch.object(app.Window, 'bind'), patch.object(app.Window, 'unhook'), patch.object(app, 'set_ui_language'), patch.object(app.Window, 'load_model'), patch.object(app, 'get_ui_language', return_value='ru'), patch.object(app, 'autostart_enabled', return_value=False):
    w = app.Window()
    w.timer.stop()
    w.events.result.disconnect(w.on_result)
    results = []
    w.events.result.connect(lambda *args: results.append(args))
    with patch.object(w, 'bind'), patch.object(w, 'unhook'):
        w.translation_box.setChecked(True)
        assert json.loads((app.DATA / 'settings.json').read_text('utf-8'))['translate_to_english'] is True
        w.build_ui() if hasattr(w, 'build_ui') else None
        assert w.translation_box.isChecked()
        with patch.object(w, 'persist', side_effect=OSError('test')):
            w.translation_box.setChecked(False)
            assert w.translation_box.isChecked() and w.config['translate_to_english']
        for enabled, language in ((True, 'ru'), (True, 'auto'), (False, 'ru')):
            w.config.update(translate_to_english=enabled, language=language, vocabulary='Dictatoro')
            w.model = Mock()
            w.model.transcribe.return_value = ([SimpleNamespace(text=' Hello world ')], None)
            w.stream = Mock()
            w.chunks = [np.ones(16000, dtype=np.float32)]
            w.rate = 16000
            w.audio_error = False
            w.target = 0
            w.target_pid = 0
            with patch.object(w.pool, 'submit', side_effect=lambda fn: fn()):
                w.stop_recording()
                kwargs = w.model.transcribe.call_args.kwargs
                assert kwargs['hotwords'] == (None if enabled else 'Dictatoro')
                assert kwargs['task'] == ('translate' if enabled else 'transcribe')
                assert kwargs['language'] == (None if language == 'auto' else language)
                assert results[-1][0] == 'Hello world'
            w.busy = False
    w.quit_app()
print('PASS: defaults, validation, persistence, save failure rollback, translate/transcribe dispatch, automatic source language, output')
