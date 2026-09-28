"""Pure helpers shared by the UI and tests."""
DEFAULTS = {"key": "f8", "model": "base", "language": "ru", "device": None, "ui_language": "ru", "translate_to_english": False, "vocabulary": ""}
UI_LANGUAGES = {"ru": "Русский", "en": "English", "pl": "Polski", "es": "Español", "de": "Deutsch", "fr": "Français", "ar": "العربية", "zh": "简体中文"}
MOUSE_BUTTONS = ("middle", "x1", "x2")
KEYS = ["f" + str(i) for i in range(1, 13)] + ["right ctrl", "right alt", "pause", "scroll lock"]
MODELS = ["tiny", "base", "small", "medium"]
LANGUAGES = ["ru", "auto", "en", "uk", "pl", "de", "fr", "es", "ar", "zh"]

POPULAR_ENGLISH_TERMS = ('AI', 'ChatGPT', 'OpenAI', 'Claude', 'Gemini', 'DeepSeek',
    'YouTube', 'Google', 'Chrome', 'Telegram', 'WhatsApp', 'Discord', 'Zoom',
    'Notion', 'Figma', 'Canva', 'GitHub', 'Windows', 'iPhone', 'Android',
    'Wi-Fi', 'Bluetooth', 'API', 'GPT', 'Smile',
    'Gmail', 'Google Meet', 'Google Drive', 'Google Maps', 'Google Docs',
    'Google Sheets', 'Google Play', 'Microsoft', 'Microsoft Teams', 'Outlook',
    'Word', 'Excel', 'PowerPoint', 'OneDrive', 'OneNote', 'Edge', 'Bing',
    'Copilot', 'Apple', 'MacBook', 'macOS', 'iPad', 'AirPods', 'Safari',
    'iCloud', 'App Store', 'Instagram', 'Facebook', 'TikTok', 'LinkedIn',
    'Reddit', 'Twitch', 'Spotify', 'Netflix', 'Slack', 'Skype', 'Viber',
    'Signal', 'Pinterest', 'Snapchat', 'Steam', 'PlayStation', 'Xbox',
    'Dropbox', 'Trello', 'Asana', 'Jira', 'Miro', 'Obsidian', 'Todoist',
    'Adobe', 'Photoshop', 'Illustrator', 'Premiere Pro', 'After Effects',
    'Lightroom', 'CapCut', 'DaVinci Resolve', 'Blender', 'Midjourney',
    'Stable Diffusion', 'Perplexity', 'Cursor', 'Visual Studio Code',
    'GitLab', 'Docker', 'Python', 'JavaScript', 'TypeScript', 'React',
    'HTML', 'CSS', 'SQL', 'JSON', 'USB', 'HDMI', 'VPN', 'PDF', 'SSD',
    'CPU', 'GPU', 'RAM', 'NVIDIA', 'Intel', 'AMD', 'Samsung', 'Xiaomi',
    'Huawei', 'PayPal', 'Revolut', 'Amazon', 'Booking', 'Airbnb',
    'Uber', 'Bolt', 'Wireshark', 'WordPress', 'Shopify', 'Zoom', 'Dictatoro')


def add_english_terms(text):
    """Merge an opt-in preset without replacing the user's vocabulary."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    seen = {line.casefold() for line in lines}
    for term in POPULAR_ENGLISH_TERMS:
        if term.casefold() not in seen:
            lines.append(term)
            seen.add(term.casefold())
    result = '\n'.join(lines)
    if len(result) > 1000:
        raise ValueError('Vocabulary too long')
    return result


def validate_config(raw):
    result = dict(DEFAULTS)
    if not isinstance(raw, dict):
        return result
    for name, choices in (("key", KEYS), ("model", MODELS), ("language", LANGUAGES)):
        if raw.get(name) in choices:
            result[name] = raw[name]
    key = raw.get("key")
    if isinstance(key, dict) and key.get("mouse") in MOUSE_BUTTONS:
        result["key"] = {"mouse": key["mouse"]}
    if isinstance(key, dict) and type(key.get("scan_code")) is int and -255 <= key["scan_code"] <= 767 and key["scan_code"] != 0:
        if isinstance(key.get("name"), str) and 0 < len(key["name"]) <= 80 and type(key.get("is_keypad")) is bool:
            result["key"] = {"scan_code": key["scan_code"], "name": key["name"], "is_keypad": key["is_keypad"]}
    if isinstance(raw.get("device"), str):
        result["device"] = raw["device"]
    if isinstance(raw.get("ui_language"), str) and raw['ui_language'] in UI_LANGUAGES:
        result["ui_language"] = raw["ui_language"]
    if type(raw.get("translate_to_english")) is bool:
        result["translate_to_english"] = raw["translate_to_english"]
    if isinstance(raw.get('vocabulary'), str):
        result['vocabulary'] = '\n'.join(dict.fromkeys(
            line.strip()[:60] for line in raw['vocabulary'][:2000].splitlines() if line.strip()))[:1000]
    return result


def key_label(key):
    if isinstance(key, dict):
        if "mouse" in key:
            return key["mouse"]
        return key["name"].upper() + (" (NumPad)" if key["is_keypad"] else "")
    return key.upper()


def matches_custom(key, event):
    # Letters follow the physical key across keyboard-layout changes.
    if event.scan_code != key["scan_code"] or bool(event.is_keypad) != key["is_keypad"]:
        return False
    if key["name"].startswith(("right ", "left ")):
        return event.name == key["name"]
    return True


def can_insert(target, current, own_process, target_process, original_process):
    return bool(target and original_process > 0 and target_process > 0
                and target == current and target_process != own_process
                and target_process == original_process)
