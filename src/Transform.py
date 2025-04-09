import os
from PIL import Image

def convert_to_bmp(input_path, output_folder=None):
    """
    将图像文件转换为BMP格式
    
    参数:
        input_path: 输入文件路径
        output_folder: 输出文件夹(可选)
    
    返回:
        转换后的BMP文件路径
    """
    supported_formats = ('.icns', '.jpg', '.jpeg', '.png', '.webp', '.tiff', '.bmp')
    file_ext = os.path.splitext(input_path)[1].lower()
    if file_ext not in supported_formats:
        raise ValueError(f"不支持的文件格式: {file_ext}")
    
    try:
        img = Image.open(input_path)
    except Exception as e:
        raise ValueError(f"无法打开图像文件: {e}")
    
    if output_folder:
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.splitext(os.path.basename(input_path))[0] + '.bmp'
        output_path = os.path.join(output_folder, filename)
    else:
        output_path = os.path.splitext(input_path)[0] + '.bmp'
    
    try:
        img.save(output_path, 'BMP')
        print(f"成功转换: {input_path} -> {output_path}")
        return output_path
    except Exception as e:
        raise ValueError(f"转换失败: {e}")

def batch_convert_to_bmp(input_folder, output_folder=None):
    """
    批量转换文件夹中的图像为BMP格式
    
    参数:
        input_folder: 输入文件夹路径
        output_folder: 输出文件夹(可选)
    """
    if not output_folder:
        output_folder = os.path.join(input_folder, 'BMP_Output')
    
    os.makedirs(output_folder, exist_ok=True)
    
    converted_files = []
    for filename in os.listdir(input_folder):
        try:
            input_path = os.path.join(input_folder, filename)
            if os.path.isfile(input_path):
                output_path = convert_to_bmp(input_path, output_folder)
                converted_files.append(output_path)
        except Exception as e:
            print(f"处理文件 {filename} 时出错: {e}")
    
    print(f"\n转换完成! 共转换了 {len(converted_files)} 个文件")
    return converted_files
