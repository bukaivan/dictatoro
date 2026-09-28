"""Base defaults, offline dispatch, fallback, missing assets and optional real inference."""
import os
from pathlib import Path
import sys
import tempfile
from unittest.mock import Mock,patch

root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['DICTATOR_DATA_DIR']=str(root/'.test-data/bundled-base')
os.environ['HF_HUB_OFFLINE']='1'
import app
import model_assets
from core import DEFAULTS
from PySide6 import QtWidgets
assert DEFAULTS['model']=='base'
with tempfile.TemporaryDirectory() as td:
    fake=Path(td)/'model_assets.py';folder=Path(td)/'models/base';folder.mkdir(parents=True)
    with patch.object(model_assets,'__file__',str(fake)):
        for name in model_assets.BASE_FILES[:-1]:(folder/name).write_bytes(b'dummy')
        assert model_assets.bundled_base_path() is None
        (folder/model_assets.BASE_FILES[-1]).write_bytes(b'dummy')
        assert model_assets.bundled_base_path()==folder
qt=QtWidgets.QApplication([])
real_load=app.Window.load_model
with patch.object(app.Window,'load_model'),patch.object(app.Window,'bind'),patch.object(app.Window,'unhook'),patch.object(app,'autostart_enabled',return_value=False),patch.object(app,'get_ui_language',return_value='ru'):
    w=app.Window();w.timer.stop();w.pool.shutdown(wait=False)
    w.pool=Mock();w.pool.submit.side_effect=lambda fn:fn()
    w.config['model']='base'
    with patch.object(app,'bundled_base_path',return_value=Path('fixture/base')),patch.object(app,'WhisperModel',return_value=object()) as engine:
        real_load(w,False);w.tick()
        assert engine.call_args.args[0]==str(Path('fixture/base'))
        assert engine.call_args.kwargs['local_files_only'] is True
        assert w.ready_model_name=='base' and not w.apply_button.isEnabled()
    w.config['model']='small'
    with patch.object(app,'WhisperModel',side_effect=FileNotFoundError('missing')) as engine:
        real_load(w,True);w.tick()
        assert engine.call_args.args[0]=='small' and engine.call_args.kwargs['local_files_only'] is True
        assert w.model is None and w.apply_button.isEnabled()
    w.config['model']='base'
    with patch.object(app,'bundled_base_path',return_value=None),patch.object(app,'WhisperModel',return_value=object()) as engine:
        real_load(w,True)
        assert engine.call_args.args[0]=='base'  # source mode / existing user cache still works
    bundled=model_assets.bundled_base_path()
    if '--require-bundled' in sys.argv:assert bundled is not None
    if bundled:
        # No download function or socket connection may be used to open the packaged model.
        with patch('socket.socket.connect',side_effect=AssertionError('Network forbidden')):
            real_load(w,True);w.tick()
            assert w.model is not None and w.ready_model_name=='base'
            import numpy as np
            segments,_=w.model.transcribe(np.zeros(8000,dtype=np.float32),language='en',vad_filter=False,beam_size=1)
            list(segments)
        print('PASS: bundled Base opens and executes inference with network forbidden')
    w.quit_app()
print('PASS: default Base, forced offline bundle, other-model download state, cache fallback, asset validation')
