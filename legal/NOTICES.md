# Сторонние компоненты Dictatoro

Dictatoro использует библиотеки и модели сторонних авторов. Их авторские права и условия сохраняются; название Dictatoro не означает, что эти библиотеки разработаны нами. По вопросам комплекта: dictatoro.app@gmail.com.

## Распознавание и обработка звука

- Whisper и faster-whisper: MIT. Текст лицензии модели находится в `upstream/Whisper-MIT.txt`, лицензия faster-whisper — в `components/runtime/Lib/site-packages/faster_whisper-1.2.1.dist-info/LICENSE`.
- faster-whisper 1.2.1 изменён для Dictatoro: загрузка PyAV стала необязательной при передаче PCM-массива. Изменение датировано 12 сентября 2026 года и приведено в `faster-whisper-pcm.patch`. PyAV и FFmpeg не включены; декодирование аудиофайлов в этой поставке не поддерживается. Обычная диктовка из микрофона поддерживается.
- CTranslate2: MIT, с отдельными условиями встроенных зависимостей. Intel OpenMP и Intel MKL не следует считать компонентами под MIT: их собственные тексты находятся в соответствующих папках `components/Intel-*`.
- ONNX Runtime: MIT и уведомления о встроенных компонентах из его `ThirdPartyNotices.txt`.
- Silero VAD: MIT, `upstream/Silero-VAD-MIT.txt`.
- sounddevice, PortAudio и keyboard: MIT. Необязательные ASIO и NVIDIA cuDNN не включены.

## Интерфейс Qt и права пользователя

В программе используются Qt Core, Qt GUI, Qt Widgets, PySide6 и Shiboken6 версии 6.11.2 по LGPLv3. Сопутствующие части Qt имеют собственные лицензии; оригинальные тексты находятся в папках `components/qtbase` и `components/pyside-setup`. Qt Charts, Qt Graphs, Qt DataVisualization, Qt VirtualKeyboard, QML и WebEngine не поставляются.

Пользователь вправе пользоваться правами, предоставленными LGPL, включая изменение и замену LGPL-библиотек и исследование приложения для отладки таких изменений. Уведомления Dictatoro не ограничивают эти права. Отдельные условия других компонентов не распространяются автоматически на LGPL-библиотеки.

Соответствующие исходники Qt Base и PySide6/Shiboken6 версии 6.11.2 включены в папку `sources`; в них находятся тексты лицензий и инструкции сборки. Порядок замены библиотек описан в [SOURCE_ACCESS.md](SOURCE_ACCESS.md). Доступ к этим материалам не требует оплаты или подключения к интернету после установки.

## Python и другие библиотеки

Python и pywin32 распространяются со своими лицензиями PSF и уведомлениями дополнительных компонентов. В исходниках pywin32 также сохранены материалы adodbapi. NumPy содержит отдельные уведомления OpenBLAS, LAPACK и GCC Runtime Exception: см. полный `LICENSE.txt` NumPy.

Для certifi и tqdm сохранены MPL-уведомления и включены исходники соответствующих версий. MPL применяется к покрываемым ею файлам, а не автоматически ко всем независимым файлам Dictatoro.

Перечень пакетов и версий находится в `package-inventory.json`, оригинальные уведомления — в `components/runtime`, дополнительные тексты — в `upstream`. Условия оригинальных лицензий имеют приоритет над этим кратким описанием.

## Windows и установка

Microsoft Visual C++ Runtime не включён ни отдельным установщиком, ни его библиотеками в папке приложения. При необходимости установщик получает проверенную версию непосредственно с сайта Microsoft; Microsoft показывает свои условия отдельно. Эти компоненты устанавливаются в систему и не удаляются деинсталлятором Dictatoro.

Файлы шрифтов Windows не поставляются: интерфейс использует шрифты, уже доступные в системе. Inno Setup используется с сохранением его уведомлений. Материалы Lucide относятся к макету; лицензия сохранена для последующего переноса иконок.

## English summary

Dictatoro uses third-party software under its respective licenses. Qt Base, PySide6 and Shiboken6 6.11.2 are used under LGPLv3. Corresponding source archives are included in `sources`. Users may replace these libraries and reverse-engineer the application for debugging such modifications as permitted by the LGPL. Other component terms do not limit those LGPL rights. See SOURCE_ACCESS.md for replacement instructions and the original license files for authoritative terms.

faster-whisper 1.2.1 contains a documented PCM-only distribution patch. PyAV, FFmpeg, ASIO and cuDNN are not bundled. Intel components carry separate licenses, not MIT. Microsoft runtime components are obtained directly from Microsoft when needed.

## Отдельная установка Intel OpenMP

Сборка IntelOnline не включает libiomp5md.dll. При отсутствии зарегистрированного Intel Runtime 2025.2.1 установщик скачивает подписанный пакет непосредственно с сервера Intel, проверяет SHA256 и открывает обычный интерфейс Intel. Условия принимает пользователь в установщике Intel. Общий компонент Intel не удаляется при удалении Dictatoro. Сведения и исходные уведомления этого пакета сохранены в components/Intel-runtime-2025.2.1.

Встроенный MKL сохраняет собственную Intel Simplified Software License. Дополнительные условия Intel не ограничивают права на Qt, PySide6 и другие компоненты LGPL. Материалы OpenMP 2025.3 относятся к прежней тестовой сборке, а не к DLL, поставляемой сборкой IntelOnline.

Полный каталог лицензий MKL 2025.3.0 из официального oneAPI Base Toolkit 2025.3.0.372 включён в `components/Intel-MKL-2025.3.0/toolkit-notices`, включая вложенные сторонние уведомления. Происхождение и контрольные суммы записаны в `provenance.json`. Наличие уведомления для необязательного компонента полного комплекта не означает, что этот компонент используется Dictatoro. Лицензия и сторонние уведомления oneDNN 3.1.1 находятся в `upstream/oneDNN-3.1.1-*`.


## Включённая модель Base / Included Base model

Установщик включает многоязычную Systran/faster-whisper-base — преобразование
OpenAI Whisper Base для CTranslate2, распространяемое под MIT. Исходная модель:
https://huggingface.co/openai/whisper-base ; преобразованная модель:
https://huggingface.co/Systran/faster-whisper-base . Версия и SHA-256 каждого файла
зафиксированы в bundled-base-provenance.json. Карточка модели сохранена в
upstream/faster-whisper-base-model-card.md; лицензия Whisper — upstream/Whisper-MIT.txt.
Dictatoro не является автором исходных весов модели.

## Дополнительные уведомления вложенных библиотек (проверка 25 сентября 2026)

В `components/CTranslate2-4.8.2-dependencies` сохранены исходные уведомления
подмодулей CTranslate2 из зафиксированных upstream-коммитов: cpu_features,
spdlog (включая уведомление fmt), Thrust, CUTLASS и вспомогательные библиотеки.
Каталог содержит также необязательные и тестовые компоненты; это не утверждение,
что каждый из них используется при диктовке. Происхождение файлов указано в provenance.json.

В `components/Rust-dependency-notices` сохранены уведомления зависимостей из
Cargo.lock официальных исходных пакетов tokenizers 0.23.2 и hf-xet 1.6.0.
Список заведомо шире рабочей сборки: содержит зависимости разработки, других
платформ и необязательных функций. Хеши архивов проверены по Cargo.lock;
недостающие в пакетах общие уведомления дополнены из соответствующих коммитов
upstream там, где происхождение удалось подтвердить. Оставшиеся вопросы отмечены
в provenance.json. Исходники tokenizers/hf-xet и покрываемых MPL/CDDL пакетов из
этого списка сохранены в `sources`. Наличие этих материалов не заменяет проверку
точного состава нативной сборки издателя.

Dictatoro выполняет распознавание на CPU, но поставляемый upstream-бинарник
CTranslate2 собран с GPU-поддержкой. Удаление отдельной cuDNN DLL не доказывает
отсутствие встроенного кода CUDA. До стабильного выпуска требуется завершить
проверку условий встроенных компонентов CUDA или заменить бинарник проверенной
CPU-сборкой. MIT нашего кода не распространяется на проприетарные части Intel/NVIDIA.

Additional upstream submodule and Rust dependency notices are preserved in the
directories above, with provenance and source archives. This is a conservative
superset, not proof of the exact publisher link inputs. The app uses CPU inference;
the upstream CTranslate2 binary was built with CUDA support. Its embedded CUDA
licensing review remains open. No proprietary Intel/NVIDIA code is relicensed as MIT.

The installer includes the multilingual Systran/faster-whisper-base conversion of
OpenAI Whisper Base under MIT. See the pinned revision and file hashes in
bundled-base-provenance.json, the included upstream model card and Whisper MIT license.
