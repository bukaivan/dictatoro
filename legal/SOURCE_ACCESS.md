# Исходники и замена библиотек

## Что включено

Папка `sources` содержит официальные исходники Qt Base 6.11.2, PySide6/Shiboken6 6.11.2, pywin32 b310, certifi 2026.7.22 и tqdm 4.70.0. Все архивы устанавливаются вместе с основными файлами, независимо от выбора дополнительной инструкции. Оригинальные адреса и SHA-256 указаны в файлах provenance рядом с этим документом.

Qt, PySide6 и Shiboken6 не изменены нами; упаковка сокращена до используемых модулей. В faster-whisper изменён только путь импорта необязательного декодера, плюс метаданные зависимости; исходный текст установлен как Python-код, разница приведена в `faster-whisper-pcm.patch`. Преобразование частоты микрофона выполняется кодом Dictatoro `audio_processing.py`.

## Замена LGPL-библиотек

1. Полностью завершите Dictatoro через значок в трее.
2. Сохраните копию папок `runtime/Lib/site-packages/PySide6` и `runtime/Lib/site-packages/shiboken6`.
3. Распакуйте исходники из `legal/sources` и следуйте их инструкциям сборки для Windows x64. Используйте ABI-совместимые настройки с Python 3.11 и Qt/PySide6 6.11.2; Qt DLL, файлы привязок `.pyd`, плагины и Shiboken должны быть совместимы между собой. Для справки о настройках штатной сборки можно использовать `QtCore.QLibraryInfo.build()`.
4. Замените соответствующие файлы в указанных папках своей совместимой сборкой. Qt Core/Gui/Widgets и используемые плагины находятся в папке PySide6.
5. Запустите Dictatoro обычным способом. Программа не требует нашей подписи или ключа для запуска заменённых LGPL-библиотек. Манифест служит для проверки заводской упаковки и не блокирует запуск пользовательской сборки.

Исследование приложения для отладки изменений LGPL-библиотек допускается в объёме, предусмотренном LGPL. Если несовместимая сборка не запускается, можно восстановить сохранённые файлы. Автоматическое обновление или повторная установка может восстановить штатные библиотеки — сохраните свои изменения отдельно.

## English

The `sources` directory contains the source archives of the listed components, with their build instructions and licenses. Qt/PySide6/Shiboken have not been modified by Dictatoro; only the deployed file set is reduced. To replace LGPL libraries, quit the app, back up the PySide6 and shiboken6 directories, build compatible Windows x64/Python 3.11 bindings and Qt 6.11.2 libraries, replace the DLL/PYD/plugin files, and restart. No Dictatoro signing key is required. The packaging manifest is not enforced as a runtime restriction. Reverse engineering for debugging modifications to LGPL libraries is permitted to the extent granted by that license.
