
def Check(src):
  lang = None
  if src == "auto":
    lang = "Auto detect language"
  if src == "en":
    lang = "English - English"
  if src == "de":
    lang = "German - Deutsch"
  if src == "ar":
    lang = "Arabic - عربي"
  if src == "es":
    lang = "Spanish - español, castellano"
  if src == "ru":
    lang = "Russian - русский"
  if src == "pl":
    lang = "Polish - Polski"
  if src == "it":
    lang = "Italian - Italiano"
  if src == "ja":
    lang = "Japanese - 日本語"
  if src == "ga":
    lang = "Irish - Gaeilge"
  if src == "hi":
    lang = "Hindi - हिन्दी, हिंदी"
  if src == "he":
    lang = "Hebrew - עברית"
  if src == "fr":
    lang = "French - Français"
  if src == "nl":
    lang = "Dutch - Nederlands"
  if src == "cs":
    lang = "Czech - česky, čeština"
  if src == "da":
    lang = "Danish - Dansk"
  if src == "zh":
    lang = "Chinese - 中文, Zhōngwén"
  if src == "fa":
    lang = "Persian - فارسی"
  return lang

"""
  if src == "auto":
    src = "Auto detect language"
  if src == "en":
    src = "English - English"
  if src == "de":
    src = "German - Deutsch"
  if src == "ar":
    src = "Arabic - عربي"
  if src == "es":
    src = "Spanish - español, castellano"
  if src == "ru":
    src = "Russian - русский"
  if src == "pl":
    src = "Polish - Polski"
  if src == "it":
    src = "Italian - Italiano"
  if src == "ja":
    src = "Japanese - 日本語"
  if src == "ga":
    src = "Irish - Gaeilge"
  if src == "hi":
    src = "Hindi - हिन्दी, हिंदी"
  if src == "he":
    src = "Hebrew - עברית"
  if src == "fr":
    src = "French - Français"
  if src == "nl":
    src = "Dutch - Nederlands"
  if src == "cs":
    src = "Czech - česky, čeština"
  if src == "da":
    src = "Danish - Dansk"
  if src == "zh":
    src = "Chinese - 中文, Zhōngwén"
  if src == "fa":
    src = "Persian - فارسی"
  if dst == "en":
    dst = "English - English"
  if dst == "de":
    dst = "German - Deutsch"
  if dst == "ar":
    dst = "Arabic - عربي"
  if dst == "es":
    dst = "Spanish - español, castellano"
  if dst == "ru":
    dst = "Russian - русский"
  if dst == "pl":
    dst = "Polish - Polski"
  if dst == "it":
    dst = "Italian - Italiano"
  if dst == "ja":
    dst = "Japanese - 日本語"
  if dst == "ga":
    dst = "Irish - Gaeilge"
  if dst == "hi":
    dst = "Hindi - हिन्दी, हिंदी"
  if dst == "he":
    dst = "Hebrew - עברית"
  if dst == "fr":
    dst = "French - Français"
  if dst == "nl":
    dst = "Dutch - Nederlands"
  if dst == "cs":
    dst = "Czech - česky, čeština"
  if dst == "da":
    dst = "Danish - Dansk"
  if dst == "zh":
    dst = "Chinese - 中文, Zhōngwén"
  if dst == "fa":
    dst = "Persian - فارسی"
"""