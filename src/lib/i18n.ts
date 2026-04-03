// =============================================
// SnapForge 国际化配置
// =============================================

export type Language = 'zh' | 'en';

export interface Translations {
  // 导航
  appName: string;
  upload: string;
  process: string;
  history: string;
  settings: string;
  
  // 上传区域
  dragDropHint: string;
  orClickToUpload: string;
  supportedFormats: string;
  pasteHint: string;
  
  // 图片操作
  selected: string;
  processing: string;
  completed: string;
  failed: string;
  pending: string;
  selectAll: string;
  deselectAll: string;
  deleteSelected: string;
  clearAll: string;
  
  // 处理配置
  formatConversion: string;
  resize: string;
  crop: string;
  rotateFlip: string;
  filters: string;
  colorAdjustment: string;
  watermark: string;
  border: string;
  
  // 格式选项
  format: string;
  quality: string;
  maintainRatio: string;
  
  // 尺寸调整
  width: string;
  height: string;
  fitMode: string;
  fit: string;
  fill: string;
  stretch: string;
  scale: string;
  
  // 裁剪
  cropArea: string;
  aspectRatio: string;
  custom: string;
  
  // 旋转翻转
  rotation: string;
  flipHorizontal: string;
  flipVertical: string;
  
  // 滤镜
  applyFilter: string;
  grayscale: string;
  sepia: string;
  vintage: string;
  fade: string;
  brighten: string;
  darken: string;
  sharpen: string;
  blur: string;
  emboss: string;
  invert: string;
  
  // 色彩调整
  brightness: string;
  contrast: string;
  saturation: string;
  
  // 水印
  watermarkSettings: string;
  watermarkType: string;
  textWatermark: string;
  imageWatermark: string;
  watermarkText: string;
  fontSize: string;
  opacity: string;
  position: string;
  tile: string;
  selectWatermarkImage: string;
  
  // 边框
  borderSettings: string;
  borderWidth: string;
  borderColor: string;
  borderRadius: string;
  
  // 操作按钮
  resetConfig: string;
  applyPreset: string;
  startProcessing: string;
  downloadAll: string;
  downloadSelected: string;
  
  // 状态消息
  noImagesSelected: string;
  processingInProgress: string;
  processingComplete: string;
  processingFailed: string;
  noImagesToProcess: string;
  selectImagesFirst: string;
  
  // 高级功能
  advancedFeatures: string;
  duplicateDetection: string;
  statistics: string;
  schemeManagement: string;
  
  // 重复检测
  findDuplicates: string;
  similarityThreshold: string;
  noDuplicatesFound: string;
  duplicatesFound: string;
  
  // 统计
  processingTrend: string;
  efficiencyTrend: string;
  successRate: string;
  featureUsage: string;
  totalProcessed: string;
  totalSuccess: string;
  totalFailed: string;
  
  // 方案管理
  savedSchemes: string;
  saveCurrentScheme: string;
  schemeName: string;
  importScheme: string;
  exportScheme: string;
  deleteScheme: string;
  noSavedSchemes: string;
  
  // 历史记录
  processingHistory: string;
  clearHistory: string;
  noHistory: string;
  taskDetails: string;
  
  // 图片对比
  imageComparison: string;
  slider: string;
  overlay: string;
  sideBySide: string;
  zoom: string;
  fullscreen: string;
  
  // EXIF 信息
  exifInfo: string;
  camera: string;
  lens: string;
  focalLength: string;
  aperture: string;
  iso: string;
  shutterSpeed: string;
  dateTaken: string;
  gps: string;
  
  // 快捷键
  keyboardShortcuts: string;
  paste: string;
  selectAllKey: string;
  delete: string;
  processAction: string;
  copyConfig: string;
  
  // 错误消息
  fileTooLarge: string;
  invalidFileType: string;
  uploadFailed: string;
  processingError: string;
  
  // 其他
  language: string;
  theme: string;
  dark: string;
  light: string;
  system: string;
  close: string;
  cancel: string;
  confirm: string;
  save: string;
  help: string;
  about: string;
  version: string;
}

// 中文翻译
const zh: Translations = {
  // 导航
  appName: 'SnapForge',
  upload: '上传',
  process: '处理',
  history: '历史',
  settings: '设置',
  
  // 上传区域
  dragDropHint: '拖拽图片到此处',
  orClickToUpload: '或点击上传',
  supportedFormats: '支持 JPEG, PNG, WebP 等格式',
  pasteHint: 'Ctrl+V 粘贴图片',
  
  // 图片操作
  selected: '已选择',
  processing: '处理中',
  completed: '已完成',
  failed: '失败',
  pending: '等待中',
  selectAll: '全选',
  deselectAll: '取消全选',
  deleteSelected: '删除所选',
  clearAll: '清空全部',
  
  // 处理配置
  formatConversion: '格式转换',
  resize: '调整尺寸',
  crop: '裁剪',
  rotateFlip: '旋转翻转',
  filters: '滤镜效果',
  colorAdjustment: '色彩调整',
  watermark: '水印',
  border: '边框',
  
  // 格式选项
  format: '格式',
  quality: '质量',
  maintainRatio: '保持比例',
  
  // 尺寸调整
  width: '宽度',
  height: '高度',
  fitMode: '适应模式',
  fit: '适应',
  fill: '填充',
  stretch: '拉伸',
  scale: '缩放',
  
  // 裁剪
  cropArea: '裁剪区域',
  aspectRatio: '比例',
  custom: '自定义',
  
  // 旋转翻转
  rotation: '旋转',
  flipHorizontal: '水平翻转',
  flipVertical: '垂直翻转',
  
  // 滤镜
  applyFilter: '应用滤镜',
  grayscale: '灰度',
  sepia: '复古',
  vintage: '怀旧',
  fade: '褪色',
  brighten: '提亮',
  darken: '变暗',
  sharpen: '锐化',
  blur: '模糊',
  emboss: '浮雕',
  invert: '反色',
  
  // 色彩调整
  brightness: '亮度',
  contrast: '对比度',
  saturation: '饱和度',
  
  // 水印
  watermarkSettings: '水印设置',
  watermarkType: '水印类型',
  textWatermark: '文字水印',
  imageWatermark: '图片水印',
  watermarkText: '水印文字',
  fontSize: '字体大小',
  opacity: '透明度',
  position: '位置',
  tile: '平铺',
  selectWatermarkImage: '选择水印图片',
  
  // 边框
  borderSettings: '边框设置',
  borderWidth: '边框宽度',
  borderColor: '边框颜色',
  borderRadius: '圆角',
  
  // 操作按钮
  resetConfig: '重置配置',
  applyPreset: '应用预设',
  startProcessing: '开始处理',
  downloadAll: '下载全部',
  downloadSelected: '下载所选',
  
  // 状态消息
  noImagesSelected: '未选择图片',
  processingInProgress: '处理中...',
  processingComplete: '处理完成',
  processingFailed: '处理失败',
  noImagesToProcess: '没有可处理的图片',
  selectImagesFirst: '请先选择图片',
  
  // 高级功能
  advancedFeatures: '高级功能',
  duplicateDetection: '重复检测',
  statistics: '统计分析',
  schemeManagement: '方案管理',
  
  // 重复检测
  findDuplicates: '查找重复',
  similarityThreshold: '相似度阈值',
  noDuplicatesFound: '未发现重复图片',
  duplicatesFound: '发现 {count} 组重复图片',
  
  // 统计
  processingTrend: '处理趋势',
  efficiencyTrend: '效率趋势',
  successRate: '成功率',
  featureUsage: '功能使用排行',
  totalProcessed: '总处理数',
  totalSuccess: '成功数',
  totalFailed: '失败数',
  
  // 方案管理
  savedSchemes: '已保存方案',
  saveCurrentScheme: '保存当前方案',
  schemeName: '方案名称',
  importScheme: '导入方案',
  exportScheme: '导出方案',
  deleteScheme: '删除方案',
  noSavedSchemes: '暂无保存的方案',
  
  // 历史记录
  processingHistory: '处理历史',
  clearHistory: '清空历史',
  noHistory: '暂无历史记录',
  taskDetails: '任务详情',
  
  // 图片对比
  imageComparison: '图片对比',
  slider: '滑块',
  overlay: '叠加',
  sideBySide: '并排',
  zoom: '缩放',
  fullscreen: '全屏',
  
  // EXIF 信息
  exifInfo: 'EXIF 信息',
  camera: '相机',
  lens: '镜头',
  focalLength: '焦距',
  aperture: '光圈',
  iso: 'ISO',
  shutterSpeed: '快门',
  dateTaken: '拍摄时间',
  gps: 'GPS 位置',
  
  // 快捷键
  keyboardShortcuts: '快捷键',
  paste: '粘贴',
  selectAllKey: '全选',
  delete: '删除',
  processAction: '处理',
  copyConfig: '复制配置',
  
  // 错误消息
  fileTooLarge: '文件过大',
  invalidFileType: '不支持的文件格式',
  uploadFailed: '上传失败',
  processingError: '处理错误',
  
  // 其他
  language: '语言',
  theme: '主题',
  dark: '深色',
  light: '浅色',
  system: '跟随系统',
  close: '关闭',
  cancel: '取消',
  confirm: '确认',
  save: '保存',
  help: '帮助',
  about: '关于',
  version: '版本',
};

// 英文翻译
const en: Translations = {
  // 导航
  appName: 'SnapForge',
  upload: 'Upload',
  process: 'Process',
  history: 'History',
  settings: 'Settings',
  
  // 上传区域
  dragDropHint: 'Drag & drop images here',
  orClickToUpload: 'or click to upload',
  supportedFormats: 'Supports JPEG, PNG, WebP and more',
  pasteHint: 'Ctrl+V to paste images',
  
  // 图片操作
  selected: 'selected',
  processing: 'Processing',
  completed: 'Completed',
  failed: 'Failed',
  pending: 'Pending',
  selectAll: 'Select All',
  deselectAll: 'Deselect All',
  deleteSelected: 'Delete Selected',
  clearAll: 'Clear All',
  
  // 处理配置
  formatConversion: 'Format Conversion',
  resize: 'Resize',
  crop: 'Crop',
  rotateFlip: 'Rotate & Flip',
  filters: 'Filters',
  colorAdjustment: 'Color Adjustment',
  watermark: 'Watermark',
  border: 'Border',
  
  // 格式选项
  format: 'Format',
  quality: 'Quality',
  maintainRatio: 'Maintain Ratio',
  
  // 尺寸调整
  width: 'Width',
  height: 'Height',
  fitMode: 'Fit Mode',
  fit: 'Fit',
  fill: 'Fill',
  stretch: 'Stretch',
  scale: 'Scale',
  
  // 裁剪
  cropArea: 'Crop Area',
  aspectRatio: 'Aspect Ratio',
  custom: 'Custom',
  
  // 旋转翻转
  rotation: 'Rotation',
  flipHorizontal: 'Flip Horizontal',
  flipVertical: 'Flip Vertical',
  
  // 滤镜
  applyFilter: 'Apply Filter',
  grayscale: 'Grayscale',
  sepia: 'Sepia',
  vintage: 'Vintage',
  fade: 'Fade',
  brighten: 'Brighten',
  darken: 'Darken',
  sharpen: 'Sharpen',
  blur: 'Blur',
  emboss: 'Emboss',
  invert: 'Invert',
  
  // 色彩调整
  brightness: 'Brightness',
  contrast: 'Contrast',
  saturation: 'Saturation',
  
  // 水印
  watermarkSettings: 'Watermark Settings',
  watermarkType: 'Watermark Type',
  textWatermark: 'Text Watermark',
  imageWatermark: 'Image Watermark',
  watermarkText: 'Watermark Text',
  fontSize: 'Font Size',
  opacity: 'Opacity',
  position: 'Position',
  tile: 'Tile',
  selectWatermarkImage: 'Select Watermark Image',
  
  // 边框
  borderSettings: 'Border Settings',
  borderWidth: 'Border Width',
  borderColor: 'Border Color',
  borderRadius: 'Border Radius',
  
  // 操作按钮
  resetConfig: 'Reset Config',
  applyPreset: 'Apply Preset',
  startProcessing: 'Start Processing',
  downloadAll: 'Download All',
  downloadSelected: 'Download Selected',
  
  // 状态消息
  noImagesSelected: 'No images selected',
  processingInProgress: 'Processing...',
  processingComplete: 'Processing complete',
  processingFailed: 'Processing failed',
  noImagesToProcess: 'No images to process',
  selectImagesFirst: 'Please select images first',
  
  // 高级功能
  advancedFeatures: 'Advanced Features',
  duplicateDetection: 'Duplicates',
  statistics: 'Statistics',
  schemeManagement: 'Schemes',
  
  // 重复检测
  findDuplicates: 'Find Duplicates',
  similarityThreshold: 'Similarity Threshold',
  noDuplicatesFound: 'No duplicates found',
  duplicatesFound: 'Found {count} duplicate groups',
  
  // 统计
  processingTrend: 'Processing Trend',
  efficiencyTrend: 'Efficiency Trend',
  successRate: 'Success Rate',
  featureUsage: 'Feature Usage',
  totalProcessed: 'Total Processed',
  totalSuccess: 'Total Success',
  totalFailed: 'Total Failed',
  
  // 方案管理
  savedSchemes: 'Saved Schemes',
  saveCurrentScheme: 'Save Current Scheme',
  schemeName: 'Scheme Name',
  importScheme: 'Import Scheme',
  exportScheme: 'Export Scheme',
  deleteScheme: 'Delete Scheme',
  noSavedSchemes: 'No saved schemes',
  
  // 历史记录
  processingHistory: 'Processing History',
  clearHistory: 'Clear History',
  noHistory: 'No history yet',
  taskDetails: 'Task Details',
  
  // 图片对比
  imageComparison: 'Image Comparison',
  slider: 'Slider',
  overlay: 'Overlay',
  sideBySide: 'Side by Side',
  zoom: 'Zoom',
  fullscreen: 'Fullscreen',
  
  // EXIF 信息
  exifInfo: 'EXIF Info',
  camera: 'Camera',
  lens: 'Lens',
  focalLength: 'Focal Length',
  aperture: 'Aperture',
  iso: 'ISO',
  shutterSpeed: 'Shutter Speed',
  dateTaken: 'Date Taken',
  gps: 'GPS Location',
  
  // 快捷键
  keyboardShortcuts: 'Keyboard Shortcuts',
  paste: 'Paste',
  selectAllKey: 'Select All',
  delete: 'Delete',
  processAction: 'Process',
  copyConfig: 'Copy Config',
  
  // 错误消息
  fileTooLarge: 'File too large',
  invalidFileType: 'Unsupported file type',
  uploadFailed: 'Upload failed',
  processingError: 'Processing error',
  
  // 其他
  language: 'Language',
  theme: 'Theme',
  dark: 'Dark',
  light: 'Light',
  system: 'System',
  close: 'Close',
  cancel: 'Cancel',
  confirm: 'Confirm',
  save: 'Save',
  help: 'Help',
  about: 'About',
  version: 'Version',
};

export const translations: Record<Language, Translations> = { zh, en };

export function t(lang: Language, key: keyof Translations, params?: Record<string, string | number>): string {
  let text = translations[lang][key];
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      text = text.replace(`{${k}}`, String(v));
    });
  }
  return text;
}
