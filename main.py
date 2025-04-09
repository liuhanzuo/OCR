
import os
from src.Translate import ocr_translate_selected
from src.Transform import convert_to_bmp, batch_convert_to_bmp
# 支持的语言列表
SUPPORTED_LANGUAGES = {
    'en': 'English',
    'zh': 'Chinese',
    'ja': 'Japanese',
    'ko': 'Korean',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'ru': 'Russian',
    'ar': 'Arabic',
    'pt': 'Portuguese',
    'it': 'Italian',
    'hi': 'Hindi'
}

# EasyOCR支持的语言代码映射
EASYOCR_LANG_MAP = {
    'en': 'en',
    'zh': 'ch_sim',
    'ja': 'ja',
    'ko': 'ko',
    'fr': 'fr',
    'de': 'de',
    'es': 'es',
    'ru': 'ru',
    'ar': 'ar',
    'pt': 'pt',
    'it': 'it',
    'hi': 'hi'
}


if __name__ == "__main__":
    input_image = "input.bmp"
    # input_image = "input.jpg"
    output_image = "output.bmp"
    
    bmp_image = convert_to_bmp(input_image, output_folder="./")
    print(f"转换后的BMP文件: {bmp_image}")
    print("支持的语言:")
    for code, name in SUPPORTED_LANGUAGES.items():
        print(f"{code}: {name}")
    
    source_langs = input("请输入要识别的语言代码(多个用逗号分隔,如zh,en): ").strip().split(',')
    target_lang = input("请输入目标翻译语言代码(如en): ").strip()
    
    if not os.path.exists(input_image):
        print(f"错误：输入图片 {input_image} 不存在！")
    else:
        ocr_translate_selected(
            bmp_image, 
            source_langs=source_langs,
            target_lang=target_lang,
            output_path=output_image
        )
