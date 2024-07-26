import tkinter as tk
from tkinter import filedialog, messagebox
from batch_rename import batch_rename_files
from batch_convert import batch_convert_images
from batch_compress import batch_compress_images

class ImageProcessingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("图片处理工具")
        
        # 原始图片路径和保存路径
        self.source_directory = None
        self.target_directory = None

        self.create_widgets()

    def create_widgets(self):
        # 选择文件夹
        tk.Label(self.root, text="选择原始图片文件夹:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Button(self.root, text="选择文件夹", command=self.select_source_directory).grid(row=0, column=1, padx=10, pady=5)

        tk.Label(self.root, text="选择保存图片文件夹:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        tk.Button(self.root, text="选择文件夹", command=self.select_target_directory).grid(row=1, column=1, padx=10, pady=5)

        # 批量重命名
        tk.Label(self.root, text="批量重命名图片").grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        tk.Label(self.root, text="前缀:").grid(row=3, column=0, padx=10, pady=5, sticky=tk.W)
        self.prefix_entry = tk.Entry(self.root)
        self.prefix_entry.grid(row=3, column=1, padx=10, pady=5)
        tk.Label(self.root, text="起始编号:").grid(row=4, column=0, padx=10, pady=5, sticky=tk.W)
        self.start_number_entry = tk.Entry(self.root)
        self.start_number_entry.grid(row=4, column=1, padx=10, pady=5)
        tk.Button(self.root, text="执行重命名", command=self.rename_files).grid(row=5, column=0, columnspan=2, padx=10, pady=5)

        # 批量格式转换
        tk.Label(self.root, text="批量转换图片格式").grid(row=6, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        tk.Label(self.root, text="目标格式 (如 jpeg, png):").grid(row=7, column=0, padx=10, pady=5, sticky=tk.W)
        self.format_entry = tk.Entry(self.root)
        self.format_entry.grid(row=7, column=1, padx=10, pady=5)
        tk.Button(self.root, text="执行转换", command=self.convert_files).grid(row=8, column=0, columnspan=2, padx=10, pady=5)

        # 批量压缩
        tk.Label(self.root, text="批量压缩图片").grid(row=9, column=0, columnspan=2, padx=10, pady=5, sticky=tk.W)
        tk.Label(self.root, text="压缩质量 (1-100):").grid(row=10, column=0, padx=10, pady=5, sticky=tk.W)
        self.quality_entry = tk.Entry(self.root)
        self.quality_entry.grid(row=10, column=1, padx=10, pady=5)
        tk.Button(self.root, text="执行压缩", command=self.compress_files).grid(row=11, column=0, columnspan=2, padx=10, pady=5)

    def select_source_directory(self):
        self.source_directory = filedialog.askdirectory(title="选择原始图片文件夹")
        if not self.source_directory:
            messagebox.showwarning("警告", "未选择原始图片文件夹！")

    def select_target_directory(self):
        self.target_directory = filedialog.askdirectory(title="选择保存图片文件夹")
        if not self.target_directory:
            messagebox.showwarning("警告", "未选择保存图片文件夹！")

    def rename_files(self):
        if not self.source_directory:
            messagebox.showwarning("警告", "请先选择原始图片文件夹！")
            return
        prefix = self.prefix_entry.get()
        try:
            start_number = int(self.start_number_entry.get())
        except ValueError:
            messagebox.showwarning("警告", "起始编号必须是一个整数！")
            return
        result = batch_rename_files(self.source_directory, prefix, start_number)
        messagebox.showinfo("结果", result)

    def convert_files(self):
        if not self.source_directory or not self.target_directory:
            messagebox.showwarning("警告", "请先选择原始和保存图片文件夹！")
            return
        target_format = self.format_entry.get()
        if not target_format:
            messagebox.showwarning("警告", "目标格式不能为空！")
            return
        result = batch_convert_images(self.source_directory, self.target_directory, target_format)
        messagebox.showinfo("结果", result)

    def compress_files(self):
        if not self.source_directory or not self.target_directory:
            messagebox.showwarning("警告", "请先选择原始和保存图片文件夹！")
            return
        try:
            quality = int(self.quality_entry.get())
            if quality < 1 or quality > 100:
                raise ValueError
        except ValueError:
            messagebox.showwarning("警告", "压缩质量必须是1到100之间的整数！")
            return
        result = batch_compress_images(self.source_directory, self.target_directory, quality)
        messagebox.showinfo("结果", result)

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessingApp(root)
    root.mainloop()
