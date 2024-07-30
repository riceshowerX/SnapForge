# SnapForge/gui/main_window.py
< MainWindow >:
BoxLayout:
orientation: 'vertical'
spacing: 10
padding: 10

# 文件选择区域
BoxLayout:
orientation: 'horizontal'
spacing: 10
size_hint_y: None
height: 40

Label:
text: '选择图片文件夹/文件:'
Button:
id: source_button
text: '选择'
on_press: root.select_source()

# 保存文件夹选择区域
BoxLayout:
orientation: 'horizontal'
spacing: 10
size_hint_y: None
height: 40

Label:
text: '选择保存图片文件夹:'
Button:
id: target_button
text: '选择文件夹'
on_press: root.select_target_directory()

# 重命名区域
BoxLayout:
orientation: 'horizontal'
spacing: 10

Label:
text: '前缀:'
TextInput:
id: prefix_input
size_hint_x: None
width: 200

Label:
text: '起始编号:'
TextInput:
id: start_number_input
size_hint_x: None
width: 100

Button:
id: rename_button
text: '执行重命名'
on_press: root.rename_files()

# 转换区域
BoxLayout:
orientation: 'horizontal'
spacing: 10

Label:
text: '目标格式:'
TextInput:
id: format_input
size_hint_x: None
width: 100

Button:
id: convert_button
text: '执行转换'
on_press: root.convert_files()

# 压缩区域
BoxLayout:
orientation: 'horizontal'
spacing: 10

Label:
text: '压缩质量 (1-100):'
TextInput:
id: quality_input
size_hint_x: None
width: 100

Button:
id: compress_button
text: '执行压缩'
on_press: root.compress_files()

# 进度条
ProgressBar:
id: progress_bar
