from src.Area import AreaSelector
from PIL import Image, ImageDraw, ImageFont
import easyocr
from googletrans import Translator
import numpy as np
import os
import cv2
import matplotlib.pyplot as plt

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

def restore_background(image, bbox):
    """
    使用图像修复技术还原背景
    """
    # 创建掩码
    mask = np.zeros(image.shape[:2], dtype=np.uint8)
    (top_left, top_right, bottom_right, bottom_left) = bbox
    
    # 将文字区域转换为多边形点集
    pts = np.array([top_left, top_right, bottom_right, bottom_left], np.int32)
    pts = pts.reshape((-1, 1, 2))
    
    # 在掩码上绘制多边形
    cv2.fillPoly(mask, [pts], 255)
    
    # 使用图像修复算法还原背景
    return cv2.inpaint(image, mask, inpaintRadius=3, flags=cv2.INPAINT_TELEA)

def ocr_translate_selected(image_path, source_langs=['ch_sim', 'en'], target_lang='en', output_path='output.jpg'):
    """
    仅翻译用户框选的区域内的文字
    
    参数:
        image_path: 输入图片路径
        source_langs: 要识别的语言列表(默认中英文)
        target_lang: 目标翻译语言代码(默认英文)
        output_path: 输出图片路径
    """
    # 让用户选择要翻译的区域和颜色
    print("请在弹出的窗口中：")
    print("1. 左键拖动选择要翻译的区域")
    print("2. 在选中的区域内右键点击选择文字颜色")
    print("3. 按回车键完成选择")
    
    selector = AreaSelector(image_path)
    selections = selector.get_selections()  # 获取(rect, color)元组列表
    
    if not selections:
        print("未选择任何区域，程序退出")
        return
    
    # 加载图像
    image_pil = Image.open(image_path)
    if image_pil.mode == 'RGBA':
        image_pil = image_pil.convert('RGB')
    image_cv2 = np.array(image_pil)
    
    print("正在处理选中的区域...")
    translator = Translator()
    draw = ImageDraw.Draw(image_pil)
    
    font_path = None
    if target_lang == 'zh':
        font_path = "simhei.ttf"
    elif target_lang in ['ja', 'ko']:
        font_path = "arialuni.ttf"
    else:
        font_path = "arial.ttf"

    for rect, text_color in selections:
        # 提取选中区域
        x1, y1, x2, y2 = rect
        region = image_cv2[y1:y2, x1:x2]
        
        # 仅对选中区域进行OCR识别
        reader = easyocr.Reader([EASYOCR_LANG_MAP.get(source_langs[0], 'en')])  # 使用第一种源语言
        results = reader.readtext(region)
        
        if not results:
            print(f"在区域 {rect} 中未识别到文字")
            continue
            
        # 还原背景
        for (bbox, _, _) in results:
            # 调整bbox坐标到原图
            adjusted_bbox = [
                [bbox[0][0] + x1, bbox[0][1] + y1],
                [bbox[1][0] + x1, bbox[1][1] + y1],
                [bbox[2][0] + x1, bbox[2][1] + y1],
                [bbox[3][0] + x1, bbox[3][1] + y1]
            ]
            image_cv2 = restore_background(image_cv2, adjusted_bbox)
        
        # 更新PIL图像
        image_pil = Image.fromarray(image_cv2)
        draw = ImageDraw.Draw(image_pil)
                            # 把图片plot出来
        # plt.imshow(image_pil)
        # plt.show(block=True)
        # 翻译并绘制文字
        for (bbox, text, _) in results:
            print(bbox, text)

            try:
                translated = translator.translate(text, dest=target_lang).text
                print(f"区域 {rect} 原文: {text} → 翻译: {translated} | 使用颜色: {text_color}")
                
                # 调整bbox坐标到原图
                adjusted_bbox = [
                    [bbox[0][0] + x1, bbox[0][1] + y1],
                    [bbox[1][0] + x1, bbox[1][1] + y1],
                    [bbox[2][0] + x1, bbox[2][1] + y1],
                    [bbox[3][0] + x1, bbox[3][1] + y1]
                ]
                
                # 计算文字大小和位置
                top_left = adjusted_bbox[0]
                bottom_right = adjusted_bbox[2]
                width = bottom_right[0] - top_left[0]
                height = bottom_right[1] - top_left[1]
                
                # 自动调整字体大小
                font_size = 1
                while True:
                    try:
                        font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
                    except:
                        font = ImageFont.load_default()
                    
                    bbox_text = font.getbbox(translated)
                    text_width = bbox_text[2] - bbox_text[0]
                    text_height = bbox_text[3] - bbox_text[1]
                    
                    if text_width > width * 0.95 or text_height > height * 0.95:
                        font_size -= 1
                        break
                    font_size += 1
                    
                    # if font_size > 100:
                    #     break

                font_size = max(font_size, 1)
                
                try:
                    font = ImageFont.truetype(font_path, font_size) if font_path else ImageFont.load_default()
                except:
                    font = ImageFont.load_default()

                text_x = top_left[0]
                text_y = top_left[1] + (height - text_height) // 2
                # 纯白颜色
                default_color = (255, 255, 255)
                # 使用选择的颜色绘制翻译后的文本
                draw.text((text_x, text_y), translated, font=font, fill=text_color if text_color else default_color)

                
                
            except Exception as e:
                print(f"翻译失败: {text}, 错误: {e}")
                continue
        image_cv2 = np.array(image_pil)
    # 保存结果
    if image_pil.mode != 'RGB':
        image_pil = image_pil.convert('RGB')
    image_pil.save(output_path, quality=100)
    print(f"处理完成！结果已保存至: {os.path.abspath(output_path)}")
