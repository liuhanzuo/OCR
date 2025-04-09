from PIL import Image, ImageDraw, ImageFont, ImageTk
import tkinter as tk
from tkinter import messagebox

class AreaSelector:
    def __init__(self, image_path):
        self.root = tk.Tk()
        self.root.title("选择区域和颜色 (按回车键结束)")
        
        self.image = Image.open(image_path)
        if self.image.mode == 'RGBA':
            self.image = self.image.convert('RGB')
        
        self.tk_image = ImageTk.PhotoImage(self.image)
        
        self.canvas = tk.Canvas(self.root, 
                               width=self.tk_image.width(), 
                               height=self.tk_image.height())
        self.canvas.pack()
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.tk_image)
        
        self.selections = []  # 存储(rectangle, color)二元组
        self.current_rect = None
        self.current_color = None
        self.color_marker = None
        
        # 状态跟踪
        self.rect_start = None
        self.color_sample_pos = None
        
        # 绑定事件
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Button-3>", self.on_right_click)
        self.root.bind("<Return>", self.on_confirm)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
    
    def on_press(self, event):
        """左键按下开始绘制矩形"""
        if self.color_sample_pos is not None:
            messagebox.showwarning("警告", "请先完成当前选择！")
            return
            
        self.rect_start = (event.x, event.y)
        self.current_rect = self.canvas.create_rectangle(
            event.x, event.y, event.x, event.y, 
            outline='green', width=2
        )
    
    def on_drag(self, event):
        """拖动鼠标调整矩形大小"""
        if self.current_rect:
            self.canvas.coords(
                self.current_rect, 
                self.rect_start[0], self.rect_start[1], 
                event.x, event.y
            )
    
    def on_release(self, event):
        """左键释放完成矩形绘制"""
        if not self.current_rect:
            return
            
        x1, y1 = self.rect_start
        x2, y2 = event.x, event.y
        rect = (
            min(x1, x2), min(y1, y2), 
            max(x1, x2), max(y1, y2)
        )
        
        # 等待颜色采样
        self.color_sample_pos = rect
        print(f"已选择区域: {rect}, 请在区域内右键点击选择文字颜色")
    
    def on_right_click(self, event):
        """右键点击采样颜色"""
        if not self.color_sample_pos:
            messagebox.showwarning("警告", "请先选择一个区域！")
            return
            
        # 检查点击位置是否在选定区域内
        x, y = event.x, event.y
        x1, y1, x2, y2 = self.color_sample_pos
        if not (x1 <= x <= x2 and y1 <= y <= y2):
            messagebox.showwarning("警告", "请在选定的区域内选择颜色！")
            return
            
        # 获取颜色并存储选择
        color = self.image.getpixel((x, y))
        self.current_color = color
        
        # 清除之前的颜色标记
        if self.color_marker:
            self.canvas.delete(self.color_marker)
        
        # 在点击处画标记
        self.color_marker = self.canvas.create_oval(
            x-3, y-3, x+3, y+3,
            outline='red', width=2
        )
        
        # 存储完整选择
        self.selections.append((self.color_sample_pos, color))
        print(f"已记录选择: 区域 {self.color_sample_pos}, 颜色 {color}")
        
        # 重置当前选择状态
        self.color_sample_pos = None
        self.current_rect = None
        if self.color_marker:
            self.canvas.delete(self.color_marker)
            self.color_marker = None
    
    def on_confirm(self, event=None):
        """按回车键确认完成"""
        if self.color_sample_pos is not None:
            messagebox.showwarning("警告", "请先完成当前颜色选择！")
            return
        self.root.quit()
    
    def on_close(self):
        """窗口关闭时确认"""
        if messagebox.askokcancel("退出", "确定要退出吗？未完成的选择将丢失"):
            self.root.quit()
    
    def get_selections(self):
        """返回(rectangle, color)二元组列表"""
        self.root.mainloop()
        return self.selections
