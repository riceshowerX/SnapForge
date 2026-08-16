// =============================================
// SnapForge 国际化配置
// =============================================
// F-03：全站文案统一收敛到词表，中文默认、英文完整。
// 词条按组件/区域组织，删除确认无引用的死词条。

export type Language = 'zh' | 'en';

export interface Translations {
  // ---------- 导航 / 头部 ----------
  upload: string;
  process: string;
  duplicateDetection: string;
  statistics: string;
  images: string; // {count} 张图片 / {count} images
  hidePanel: string;
  showPanel: string;
  showConfigPanel: string;
  uploaded: string; // 已上传 / Uploaded
  selected: string; // 已选择 / Selected
  config: string;
  preview: string;
  schemes: string;
  history: string;
  viewDocs: string;
  welcomeTitle: string;
  welcomeDesc: string;
  keyboardShortcuts: string;
  paste: string;
  selectAllKey: string;
  delete: string;
  processAction: string;
  close: string;

  // ---------- 上传区 ----------
  dragDropHint: string;
  orClickToUpload: string;
  supportedFormats: string;
  uploading: string;
  selectAll: string;
  deleteSelected: string;
  clearAll: string;
  deleteSingle: string;
  select: string;
  deselect: string;
  selectOnly: string;
  selectedCount: string; // 已选择 {selected} / {total} 张
  uploadFailed: string;
  invalidFileType: string;
  someUploadsFailed: string;

  // ---------- 处理面板 ----------
  enabledConfigs: string; // 已启用配置
  historyRecords: string; // 历史记录
  ready: string;
  readyHint: string;
  selectedAndConfig: string; // 已选择 {count} 张图片，{configs} 项配置已启用
  noImagesToProcess: string;
  processingSettings: string;
  concurrency: string;
  concurrencyHint: string;
  stopOnError: string;
  stopOnErrorHint: string;
  finish: string;
  startProcessing: string;
  startProcessingHint: string;
  processingInProgress: string;
  processingComplete: string;
  stop: string;
  downloadAll: string;
  download: string;
  reset: string;
  success: string;
  failed: string;
  waiting: string;
  processingProgress: string;
  processedFile: string;
  currentProcessing: string; // 正在处理第 {current} / {total} 张 (并发: {concurrency})
  successSummary: string; // 成功 {success} 张{failedText}，共 {total} 张
  failedSummary: string; // ，失败 {failed} 张
  processingInterrupted: string;
  processingError: string;

  // ---------- 配置面板 ----------
  formatConversion: string;
  resize: string;
  crop: string;
  rotateFlip: string;
  filters: string;
  colorAdjustment: string;
  watermark: string;
  border: string;
  rename: string;
  preserveMetadata: string;
  outputFormat: string;
  quality: string;
  progressiveLoading: string;
  optimizeCompression: string;
  fitMode: string;
  onlyShrink: string;
  cropX: string;
  cropY: string;
  cropWidth: string;
  cropHeight: string;
  rotationAngle: string;
  noRotation: string;
  rotate90: string;
  rotate180: string;
  rotate270: string;
  flipVertical: string;
  flipHorizontal: string;
  filterType: string;
  intensity: string;
  brightness: string;
  contrast: string;
  saturation: string;
  sharpness: string;
  watermarkType: string;
  textWatermark: string;
  imageWatermark: string;
  watermarkText: string;
  position: string;
  opacity: string;
  fontSize: string;
  borderWidth: string;
  borderColor: string;
  prefix: string;
  startNumber: string;
  quickWeb: string;
  quickThumbnail: string;
  resetConfig: string;
  optionContain: string;
  optionCover: string;
  optionStretch: string;
  optionFill: string;
  optionJpeg: string;
  optionPng: string;
  optionWebp: string;
  optionAvif: string;
  optionTiff: string;
  filterGrayscale: string;
  filterSepia: string;
  filterInvert: string;
  filterBlur: string;
  filterSharpen: string;
  filterEmboss: string;
  filterEdge: string;
  filterVintage: string;
  filterNoir: string;
  posTopLeft: string;
  posTopCenter: string;
  posTopRight: string;
  posCenterLeft: string;
  posCenter: string;
  posCenterRight: string;
  posBottomLeft: string;
  posBottomCenter: string;
  posBottomRight: string;
  posTile: string;
  watermarkTextPlaceholder: string;

  // ---------- EXIF / 预览 ----------
  imageInfo: string;
  fileName: string;
  fileSize: string;
  dimensions: string;
  type: string;
  manufacturer: string;
  model: string;
  aperture: string;
  shutter: string;
  iso: string;
  focalLength: string;
  dateTaken: string;
  gps: string;
  software: string;
  xResolution: string;
  colorSpace: string;
  basicInfo: string;
  cameraInfo: string;
  advancedInfo: string;
  noExif: string;
  selectImageHint: string;
  selectPreviewHint: string;
  selectPreviewHint2: string;
  fileInfo: string;
  unknown: string;

  // ---------- 重复检测 ----------
  findDuplicates: string;
  scanning: string;
  startDetection: string;
  noDuplicatesFound: string;
  scannedCount: string; // 已扫描 {count} 张图片
  duplicateGroups: string; // 共 {groups} 组，{count} 张重复图片
  selectedDuplicates: string; // 已选择 {count} 张重复图片
  deselectAll: string;
  selectAllDuplicates: string;
  keep: string;
  groupLabel: string; // 组 {index}
  similarity: string;
  imagesSimilar: string; // {count} 张相似
  duplicatesBadge: string; // 发现 {count} 组重复
  uploadAtLeast2: string;
  clickToSelect: string;
  clickToDeselect: string;
  clickToDelete: string;

  // ---------- 统计 ----------
  totalProcessed: string;
  sizeSaved: string;
  avgProcessingTime: string;
  successRate: string;
  processingTrend: string;
  featureUsage: string;
  recentTasks: string;
  clearHistory: string;
  noData: string;
  optimized: string;
  quick: string;
  normal: string;
  excellent: string;
  good: string;
  attention: string;
  imagesCount: string; // {count} 张图片
  successRatio: string; // {success}/{total} 成功
  completed: string;
  partialSuccess: string;
  sizeSavedSubtitle: string;
  avgTimeSubtitle: string;
  successRateSubtitle: string;
  trend7d: string;
  featureUsageSubtitle: string;
  noFeatureData: string;
  noHistoryData: string;
  noTrendData: string;

  // ---------- 历史 ----------
  processingHistory: string;
  noHistory: string;
  historyHint: string;
  recordsCount: string; // {count} 条记录
  duration: string; // 耗时 {duration}

  // ---------- 主题 ----------
  light: string;
  dark: string;
  system: string;

  // ---------- 方案管理 ----------
  schemeManagement: string;
  schemeHint: string;
  recommended: string;
  mySchemes: string;
  saveCurrentScheme: string;
  createSchemeTitle: string;
  createSchemeDesc: string;
  schemeName: string;
  description: string;
  cancel: string;
  save: string;
  importScheme: string;
  exportScheme: string;
  deleteScheme: string;
  apply: string;
  applied: string;
  importFailed: string;
  featureConvert: string;
  featureResize: string;
  featureCrop: string;
  featureRotate: string;
  featureFilter: string;
  featureWatermark: string;
  featureEffects: string;
  featureBorder: string;
  featureCompression: string;
  customSchemeDesc: string;
  schemeNamePlaceholder: string;
  schemeDescPlaceholder: string;

  // ---------- 错误页 ----------
  errorTitle: string;
  errorGeneric: string;
  errorHome: string;
  errorRetry: string;
  errorDigest: string;

  // ---------- 使用技巧 ----------
  tips: string;
  tipDragDrop: string;
  tipSchemes: string;
  tipAutoSave: string;
  tipZip: string;
  haveIssues: string;
  submitFeedback: string;
}

// 中文翻译
const zh: Translations = {
  // 导航 / 头部
  upload: '上传',
  process: '处理',
  duplicateDetection: '重复检测',
  statistics: '统计',
  images: '{count} 张图片',
  hidePanel: '隐藏面板',
  showPanel: '显示面板',
  showConfigPanel: '显示配置面板',
  uploaded: '已上传',
  selected: '已选择',
  config: '配置',
  preview: '预览',
  schemes: '方案',
  history: '历史',
  viewDocs: '查看文档',
  welcomeTitle: '欢迎使用 SnapForge',
  welcomeDesc: '专业图像处理平台，支持批量处理、格式转换、滤镜特效等',
  keyboardShortcuts: '快捷键',
  paste: '粘贴',
  selectAllKey: '全选',
  delete: '删除',
  processAction: '处理',
  close: '关闭',

  // 上传区
  dragDropHint: '拖拽图片到此处',
  orClickToUpload: '或点击选择文件',
  supportedFormats: '支持 JPEG, PNG, WebP, GIF · 最大 50MB · Ctrl+V 粘贴',
  uploading: '上传中...',
  selectAll: '全选',
  deleteSelected: '删除选中',
  clearAll: '清空',
  deleteSingle: '删除',
  select: '选择',
  deselect: '取消选择',
  selectOnly: '仅选择此图片',
  selectedCount: '已选择 {selected} / {total} 张',
  uploadFailed: '上传失败',
  invalidFileType: '不支持的文件格式，仅支持 JPEG/PNG/WebP/GIF',
  someUploadsFailed: '部分图片上传失败，请检查文件格式与大小',

  // 处理面板
  enabledConfigs: '已启用配置',
  historyRecords: '历史记录',
  ready: '准备就绪',
  readyHint: '配置完成后即可开始批量处理',
  selectedAndConfig: '已选择 {count} 张图片，{configs} 项配置已启用',
  noImagesToProcess: '请先上传并选择要处理的图片',
  processingSettings: '处理设置',
  concurrency: '并发数量',
  concurrencyHint: '同时处理的图片数量，数值越高速度越快（1-10）',
  stopOnError: '遇到错误停止',
  stopOnErrorHint: '第一张图片处理失败时停止处理',
  finish: '完成',
  startProcessing: '开始处理',
  startProcessingHint: '点击开始处理选中图片 (Ctrl+Enter)',
  processingInProgress: '处理中...',
  processingComplete: '处理完成',
  stop: '停止',
  downloadAll: '下载全部',
  download: '下载',
  reset: '重置',
  success: '成功',
  failed: '失败',
  waiting: '等待处理',
  processingProgress: '处理进度',
  processedFile: '处理失败',
  currentProcessing: '正在处理第 {current} / {total} 张 (并发: {concurrency})',
  successSummary: '成功 {success} 张{failedText}，共 {total} 张',
  failedSummary: '，失败 {failed} 张',
  processingInterrupted: '处理已中断',
  processingError: '处理错误',

  // 配置面板
  formatConversion: '格式转换',
  resize: '尺寸调整',
  crop: '裁剪',
  rotateFlip: '旋转与翻转',
  filters: '滤镜效果',
  colorAdjustment: '色彩调整',
  watermark: '水印',
  border: '边框',
  rename: '智能重命名',
  preserveMetadata: '保留元数据',
  outputFormat: '输出格式',
  quality: '质量',
  progressiveLoading: '渐进式加载',
  optimizeCompression: '优化压缩',
  fitMode: '缩放模式',
  onlyShrink: '仅缩小不放大',
  cropX: 'X 起点',
  cropY: 'Y 起点',
  cropWidth: '宽度',
  cropHeight: '高度',
  rotationAngle: '旋转角度',
  noRotation: '不旋转',
  rotate90: '顺时针 90°',
  rotate180: '180°',
  rotate270: '顺时针 270°',
  flipVertical: '垂直翻转',
  flipHorizontal: '水平翻转',
  filterType: '滤镜类型',
  intensity: '强度',
  brightness: '亮度',
  contrast: '对比度',
  saturation: '饱和度',
  sharpness: '锐度',
  watermarkType: '水印类型',
  textWatermark: '文本水印',
  imageWatermark: '图片水印',
  watermarkText: '水印文字',
  position: '位置',
  opacity: '透明度',
  fontSize: '字体大小',
  borderWidth: '边框宽度',
  borderColor: '边框颜色',
  prefix: '文件名前缀',
  startNumber: '起始编号',
  quickWeb: 'Web优化',
  quickThumbnail: '缩略图',
  resetConfig: '重置配置',
  optionContain: '适应 - 保持比例',
  optionCover: '填充 - 裁剪适应',
  optionStretch: '拉伸 - 忽略比例',
  optionFill: '内部 - 完全包含',
  optionJpeg: 'JPEG - 通用格式',
  optionPng: 'PNG - 无损压缩',
  optionWebp: 'WebP - 现代格式',
  optionAvif: 'AVIF - 高压缩比',
  optionTiff: 'TIFF - 印刷质量',
  filterGrayscale: '灰度',
  filterSepia: '复古棕褐',
  filterInvert: '反色',
  filterBlur: '模糊',
  filterSharpen: '锐化',
  filterEmboss: '浮雕',
  filterEdge: '边缘检测',
  filterVintage: '复古',
  filterNoir: '黑白电影',
  posTopLeft: '左上角',
  posTopCenter: '顶部居中',
  posTopRight: '右上角',
  posCenterLeft: '左侧居中',
  posCenter: '正中心',
  posCenterRight: '右侧居中',
  posBottomLeft: '左下角',
  posBottomCenter: '底部居中',
  posBottomRight: '右下角',
  posTile: '平铺',
  watermarkTextPlaceholder: '输入水印文字',

  // EXIF / 预览
  imageInfo: '图片信息',
  fileName: '文件名',
  fileSize: '文件大小',
  dimensions: '尺寸',
  type: '类型',
  manufacturer: '制造商',
  model: '型号',
  aperture: '光圈',
  shutter: '快门',
  iso: 'ISO',
  focalLength: '焦距',
  dateTaken: '拍摄时间',
  gps: 'GPS',
  software: '软件',
  xResolution: '分辨率',
  colorSpace: '色彩空间',
  basicInfo: '基本信息',
  cameraInfo: '拍摄信息',
  advancedInfo: '高级信息',
  noExif: '此图片无 EXIF 元数据',
  selectImageHint: '选择图片查看详细信息',
  selectPreviewHint: '选择图片查看预览',
  selectPreviewHint2: '点击图片或使用 Ctrl+A 全选',
  fileInfo: '文件信息',
  unknown: '未知',

  // 重复检测
  findDuplicates: '查找重复',
  scanning: '正在扫描图片...',
  startDetection: '开始检测',
  noDuplicatesFound: '未发现重复图片',
  scannedCount: '已扫描 {count} 张图片',
  duplicateGroups: '共 {groups} 组，{count} 张重复图片',
  selectedDuplicates: '已选择 {count} 张重复图片',
  deselectAll: '取消选择',
  selectAllDuplicates: '全选重复项',
  keep: '保留',
  groupLabel: '组 {index}',
  similarity: '相似度',
  imagesSimilar: '{count} 张相似',
  duplicatesBadge: '发现 {count} 组重复',
  uploadAtLeast2: '上传至少 2 张图片后可进行重复检测',
  clickToSelect: '点击选择删除',
  clickToDeselect: '点击取消选择',
  clickToDelete: '点击其他图片选择删除',

  // 统计
  totalProcessed: '已处理图片',
  sizeSaved: '节省空间',
  avgProcessingTime: '平均处理时间',
  successRate: '成功率',
  processingTrend: '处理趋势',
  featureUsage: '功能使用分布',
  recentTasks: '最近任务',
  clearHistory: '清空历史',
  noData: '暂无数据',
  optimized: '优化有效',
  quick: '快速',
  normal: '正常',
  excellent: '优秀',
  good: '良好',
  attention: '需关注',
  imagesCount: '{count} 张图片',
  successRatio: '{success}/{total} 成功',
  completed: '完成',
  partialSuccess: '部分成功',
  sizeSavedSubtitle: '通过压缩优化',
  avgTimeSubtitle: '单张图片',
  successRateSubtitle: '处理成功比例',
  trend7d: '最近7天处理量',
  featureUsageSubtitle: '各功能使用次数统计',
  noFeatureData: '暂无功能使用数据',
  noHistoryData: '暂无处理历史',
  noTrendData: '暂无处理数据',

  // 历史
  processingHistory: '处理历史',
  noHistory: '暂无处理历史',
  historyHint: '处理图片后显示记录',
  recordsCount: '{count} 条记录',
  duration: '耗时 {duration}',

  // 主题
  light: '浅色',
  dark: '深色',
  system: '跟随系统',

  // 方案管理
  schemeManagement: '处理方案',
  schemeHint: '快速应用预设或自定义配置',
  recommended: '推荐方案',
  mySchemes: '我的方案',
  saveCurrentScheme: '保存当前配置',
  createSchemeTitle: '保存当前配置',
  createSchemeDesc: '将当前的处理配置保存为方案，方便下次使用',
  schemeName: '方案名称',
  description: '描述（可选）',
  cancel: '取消',
  save: '保存',
  importScheme: '导入方案',
  exportScheme: '导出方案',
  deleteScheme: '删除方案',
  apply: '应用',
  applied: '已应用',
  importFailed: '方案导入失败：文件格式无效',
  featureConvert: '格式转换',
  featureResize: '尺寸调整',
  featureCrop: '裁剪',
  featureRotate: '旋转',
  featureFilter: '滤镜',
  featureWatermark: '水印',
  featureEffects: '特效',
  featureBorder: '边框',
  featureCompression: '压缩',
  customSchemeDesc: '自定义处理方案',
  schemeNamePlaceholder: '例如：电商产品图',
  schemeDescPlaceholder: '描述此方案的用途...',

  // 错误页
  errorTitle: '出错了',
  errorGeneric: '应用程序遇到了一个错误。请刷新页面重试。',
  errorHome: '返回首页',
  errorRetry: '重试',
  errorDigest: '错误标识',

  // 使用技巧
  tips: '使用技巧',
  tipDragDrop: '拖拽或粘贴图片快速上传',
  tipSchemes: '使用方案快速应用预设配置',
  tipAutoSave: '批量处理时自动保存历史',
  tipZip: '支持导出为 ZIP 批量下载',
  haveIssues: '遇到问题？',
  submitFeedback: '提交反馈 →',
};

// 英文翻译
const en: Translations = {
  // Navigation / Header
  upload: 'Upload',
  process: 'Process',
  duplicateDetection: 'Duplicates',
  statistics: 'Stats',
  images: '{count} images',
  hidePanel: 'Hide Panel',
  showPanel: 'Show Panel',
  showConfigPanel: 'Show Config Panel',
  uploaded: 'Uploaded',
  selected: 'Selected',
  config: 'Config',
  preview: 'Preview',
  schemes: 'Schemes',
  history: 'History',
  viewDocs: 'View Docs',
  welcomeTitle: 'Welcome to SnapForge',
  welcomeDesc:
    'Professional image processing platform with batch processing, format conversion, filters and more',
  keyboardShortcuts: 'Keyboard Shortcuts',
  paste: 'Paste',
  selectAllKey: 'Select All',
  delete: 'Delete',
  processAction: 'Process',
  close: 'Close',

  // Upload area
  dragDropHint: 'Drag & drop images here',
  orClickToUpload: 'or click to select files',
  supportedFormats: 'Supports JPEG, PNG, WebP, GIF · Max 50MB · Ctrl+V to paste',
  uploading: 'Uploading...',
  selectAll: 'Select All',
  deleteSelected: 'Delete Selected',
  clearAll: 'Clear All',
  deleteSingle: 'Delete',
  select: 'Select',
  deselect: 'Deselect',
  selectOnly: 'Select Only This',
  selectedCount: '{selected} / {total} selected',
  uploadFailed: 'Upload failed',
  invalidFileType: 'Unsupported file type. Only JPEG/PNG/WebP/GIF are supported.',
  someUploadsFailed: 'Some images failed to upload. Check file format and size.',

  // Processing panel
  enabledConfigs: 'Active Configs',
  historyRecords: 'History',
  ready: 'Ready',
  readyHint: 'Configure options then start batch processing',
  selectedAndConfig: '{count} images selected, {configs} configs enabled',
  noImagesToProcess: 'Upload and select images to process first',
  processingSettings: 'Processing Settings',
  concurrency: 'Concurrency',
  concurrencyHint: 'Number of images processed at once (1-10)',
  stopOnError: 'Stop on Error',
  stopOnErrorHint: 'Stop processing when the first image fails',
  finish: 'Done',
  startProcessing: 'Start Processing',
  startProcessingHint: 'Start processing selected images (Ctrl+Enter)',
  processingInProgress: 'Processing...',
  processingComplete: 'Processing Complete',
  stop: 'Stop',
  downloadAll: 'Download All',
  download: 'Download',
  reset: 'Reset',
  success: 'Success',
  failed: 'Failed',
  waiting: 'Waiting',
  processingProgress: 'Progress',
  processedFile: 'Processing failed',
  currentProcessing:
    'Processing {current} / {total} (concurrency: {concurrency})',
  successSummary: '{success} succeeded{failedText}, {total} total',
  failedSummary: ', {failed} failed',
  processingInterrupted: 'Processing interrupted',
  processingError: 'Processing error',

  // Config panel
  formatConversion: 'Format Conversion',
  resize: 'Resize',
  crop: 'Crop',
  rotateFlip: 'Rotate & Flip',
  filters: 'Filters',
  colorAdjustment: 'Color Adjustment',
  watermark: 'Watermark',
  border: 'Border',
  rename: 'Smart Rename',
  preserveMetadata: 'Preserve Metadata',
  outputFormat: 'Output Format',
  quality: 'Quality',
  progressiveLoading: 'Progressive',
  optimizeCompression: 'Optimize Compression',
  fitMode: 'Fit Mode',
  onlyShrink: 'Shrink Only',
  cropX: 'X Start',
  cropY: 'Y Start',
  cropWidth: 'Width',
  cropHeight: 'Height',
  rotationAngle: 'Rotation Angle',
  noRotation: 'No Rotation',
  rotate90: '90° Clockwise',
  rotate180: '180°',
  rotate270: '270° Clockwise',
  flipVertical: 'Flip Vertical',
  flipHorizontal: 'Flip Horizontal',
  filterType: 'Filter Type',
  intensity: 'Intensity',
  brightness: 'Brightness',
  contrast: 'Contrast',
  saturation: 'Saturation',
  sharpness: 'Sharpness',
  watermarkType: 'Watermark Type',
  textWatermark: 'Text Watermark',
  imageWatermark: 'Image Watermark',
  watermarkText: 'Watermark Text',
  position: 'Position',
  opacity: 'Opacity',
  fontSize: 'Font Size',
  borderWidth: 'Border Width',
  borderColor: 'Border Color',
  prefix: 'Filename Prefix',
  startNumber: 'Start Number',
  quickWeb: 'Web',
  quickThumbnail: 'Thumbnail',
  resetConfig: 'Reset Config',
  optionContain: 'Contain - Keep Ratio',
  optionCover: 'Cover - Crop to Fit',
  optionStretch: 'Stretch - Ignore Ratio',
  optionFill: 'Fill - Fully Inside',
  optionJpeg: 'JPEG - Universal',
  optionPng: 'PNG - Lossless',
  optionWebp: 'WebP - Modern',
  optionAvif: 'AVIF - High Compression',
  optionTiff: 'TIFF - Print Quality',
  filterGrayscale: 'Grayscale',
  filterSepia: 'Sepia',
  filterInvert: 'Invert',
  filterBlur: 'Blur',
  filterSharpen: 'Sharpen',
  filterEmboss: 'Emboss',
  filterEdge: 'Edge Detect',
  filterVintage: 'Vintage',
  filterNoir: 'Noir',
  posTopLeft: 'Top Left',
  posTopCenter: 'Top Center',
  posTopRight: 'Top Right',
  posCenterLeft: 'Center Left',
  posCenter: 'Center',
  posCenterRight: 'Center Right',
  posBottomLeft: 'Bottom Left',
  posBottomCenter: 'Bottom Center',
  posBottomRight: 'Bottom Right',
  posTile: 'Tile',
  watermarkTextPlaceholder: 'Enter watermark text',

  // EXIF / Preview
  imageInfo: 'Image Info',
  fileName: 'File Name',
  fileSize: 'File Size',
  dimensions: 'Dimensions',
  type: 'Type',
  manufacturer: 'Manufacturer',
  model: 'Model',
  aperture: 'Aperture',
  shutter: 'Shutter Speed',
  iso: 'ISO',
  focalLength: 'Focal Length',
  dateTaken: 'Date Taken',
  gps: 'GPS',
  software: 'Software',
  xResolution: 'Resolution',
  colorSpace: 'Color Space',
  basicInfo: 'Basic Info',
  cameraInfo: 'Camera Info',
  advancedInfo: 'Advanced Info',
  noExif: 'No EXIF metadata for this image',
  selectImageHint: 'Select an image to view details',
  selectPreviewHint: 'Select an image to preview',
  selectPreviewHint2: 'Click images or press Ctrl+A to select all',
  fileInfo: 'File Info',
  unknown: 'Unknown',

  // Duplicate detection
  findDuplicates: 'Find Duplicates',
  scanning: 'Scanning images...',
  startDetection: 'Start Detection',
  noDuplicatesFound: 'No duplicates found',
  scannedCount: '{count} images scanned',
  duplicateGroups: '{groups} groups, {count} duplicate images',
  selectedDuplicates: '{count} duplicate images selected',
  deselectAll: 'Deselect',
  selectAllDuplicates: 'Select All Duplicates',
  keep: 'Keep',
  groupLabel: 'Group {index}',
  similarity: 'Similarity',
  imagesSimilar: '{count} similar',
  duplicatesBadge: '{count} duplicate groups found',
  uploadAtLeast2: 'Upload at least 2 images to run duplicate detection',
  clickToSelect: 'Click to select for deletion',
  clickToDeselect: 'Click to deselect',
  clickToDelete: 'Click other images to select for deletion',

  // Stats
  totalProcessed: 'Images Processed',
  sizeSaved: 'Space Saved',
  avgProcessingTime: 'Avg. Time',
  successRate: 'Success Rate',
  processingTrend: 'Processing Trend',
  featureUsage: 'Feature Usage',
  recentTasks: 'Recent Tasks',
  clearHistory: 'Clear History',
  noData: 'No data',
  optimized: 'Optimized',
  quick: 'Fast',
  normal: 'Normal',
  excellent: 'Excellent',
  good: 'Good',
  attention: 'Attention',
  imagesCount: '{count} images',
  successRatio: '{success}/{total} succeeded',
  completed: 'Completed',
  partialSuccess: 'Partial',
  sizeSavedSubtitle: 'via compression',
  avgTimeSubtitle: 'per image',
  successRateSubtitle: 'success ratio',
  trend7d: 'Last 7 days',
  featureUsageSubtitle: 'Usage count per feature',
  noFeatureData: 'No feature usage data',
  noHistoryData: 'No processing history',
  noTrendData: 'No processing data',

  // History
  processingHistory: 'Processing History',
  noHistory: 'No history yet',
  historyHint: 'Records appear after processing',
  recordsCount: '{count} records',
  duration: '{duration}',

  // Theme
  light: 'Light',
  dark: 'Dark',
  system: 'System',

  // Scheme management
  schemeManagement: 'Schemes',
  schemeHint: 'Apply presets or custom configs quickly',
  recommended: 'Recommended',
  mySchemes: 'My Schemes',
  saveCurrentScheme: 'Save Current Config',
  createSchemeTitle: 'Save Current Config',
  createSchemeDesc: 'Save current processing config as a scheme for later use',
  schemeName: 'Scheme Name',
  description: 'Description (optional)',
  cancel: 'Cancel',
  save: 'Save',
  importScheme: 'Import Scheme',
  exportScheme: 'Export Scheme',
  deleteScheme: 'Delete Scheme',
  apply: 'Apply',
  applied: 'Applied',
  importFailed: 'Scheme import failed: invalid file format',
  featureConvert: 'Convert',
  featureResize: 'Resize',
  featureCrop: 'Crop',
  featureRotate: 'Rotate',
  featureFilter: 'Filter',
  featureWatermark: 'Watermark',
  featureEffects: 'Effects',
  featureBorder: 'Border',
  featureCompression: 'Compress',
  customSchemeDesc: 'Custom processing scheme',
  schemeNamePlaceholder: 'e.g. E-commerce product photo',
  schemeDescPlaceholder: 'Describe the purpose of this scheme...',

  // Error page
  errorTitle: 'Something went wrong',
  errorGeneric:
    'The application encountered an error. Please refresh the page and try again.',
  errorHome: 'Back to Home',
  errorRetry: 'Retry',
  errorDigest: 'Error ID',

  // Tips
  tips: 'Tips',
  tipDragDrop: 'Drag & drop or paste images to upload',
  tipSchemes: 'Use schemes to apply presets quickly',
  tipAutoSave: 'Batch processing auto-saves history',
  tipZip: 'Export results as ZIP for batch download',
  haveIssues: 'Have issues?',
  submitFeedback: 'Submit Feedback →',
};

export const translations: Record<Language, Translations> = { zh, en };

export function t(
  lang: Language,
  key: keyof Translations,
  params?: Record<string, string | number>
): string {
  let text = translations[lang][key];
  if (params) {
    Object.entries(params).forEach(([k, v]) => {
      text = text.replace(`{${k}}`, String(v));
    });
  }
  return text;
}
