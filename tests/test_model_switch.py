import os,sys
from pathlib import Path
from unittest.mock import patch,Mock
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root))
os.environ['DICTATOR_DATA_DIR']=str(root/'.test-data/model-switch-test-data')
import app
from PySide6 import QtWidgets
qt=QtWidgets.QApplication([])
real_load=app.Window.load_model
with patch.object(app.Window,'load_model'),patch.object(app.Window,'bind'),patch.object(app.Window,'unhook'),patch.object(app,'autostart_enabled',return_value=False):
 w=app.Window();w.timer.stop();qt.processEvents()
 w.config['model']='tiny';w.model_box.select('tiny');w.model=object()
 with patch.object(w,'load_model') as load:
  w.model_box.select('small');load.assert_called_once_with(True)
 w.pool.shutdown(wait=False)
 w.pool=Mock();w.pool.submit.side_effect=lambda fn:fn()
 with patch.object(app,'WhisperModel',return_value=object()) as engine:
  real_load(w,True);qt.processEvents();w.tick()
  assert engine.call_args.kwargs['local_files_only'] is True
  assert w.model is not None and not w.apply_button.isEnabled()
  assert w.apply_button.text()==app.tr('Модель готова')
 with patch.object(app,'WhisperModel',side_effect=FileNotFoundError('not cached')):
  real_load(w,True);qt.processEvents();w.tick()
  assert w.model is None and w.apply_button.isEnabled()
  assert w.apply_button.text()==app.tr('Загрузить модель')
 w.tray.hide();w.hide()
print('PASS: switching checks disk offline, cached model ready, missing model offers download')
