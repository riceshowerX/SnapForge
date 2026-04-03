// =============================================
// SnapForge Zustand Store
// =============================================

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import {
  ImageFile,
  ProcessConfig,
  BatchTask,
  ProcessResult,
  defaultProcessConfig,
} from '@/types';
import { v4 as uuidv4 } from 'uuid';

// =============================================
// Store 状态接口
// =============================================

interface AppState {
  // 图像文件列表（不持久化）
  images: ImageFile[];
  
  // 处理配置
  config: ProcessConfig;
  
  // 批量任务（不持久化）
  currentTask: BatchTask | null;
  
  // 任务历史（持久化，但精简数据）
  taskHistory: BatchTask[];
  
  // UI 状态
  selectedImageIds: string[];
  isProcessing: boolean;
  activeTab: string;
  
  // 操作方法
  addImages: (files: ImageFile[]) => void;
  removeImages: (ids: string[]) => void;
  clearImages: () => void;
  toggleImageSelection: (id: string) => void;
  selectAllImages: () => void;
  deselectAllImages: () => void;
  
  // 配置方法
  updateConfig: <K extends keyof ProcessConfig>(
    key: K,
    value: ProcessConfig[K]
  ) => void;
  resetConfig: () => void;
  
  // 处理方法
  startProcessing: () => void;
  updateProcessResult: (result: ProcessResult) => void;
  completeProcessing: () => void;
  
  // UI 方法
  setActiveTab: (tab: string) => void;
  
  // 清理方法
  clearTaskHistory: () => void;
}

// =============================================
// 辅助函数：精简任务数据用于存储
// =============================================

function stripLargeData(task: BatchTask): BatchTask {
  return {
    ...task,
    // 移除文件的 base64 数据，只保留元数据
    files: task.files.map((f) => ({
      ...f,
      url: '', // 清空 base64 URL
      preview: '', // 清空预览数据
    })),
    // 移除结果中的 URL 数据
    results: task.results.map((r) => ({
      ...r,
      processedUrl: undefined,
    })),
  };
}

// =============================================
// 自定义存储：带错误处理和容量管理
// =============================================

const createCustomStorage = (): Storage => {
  const storage = typeof window !== 'undefined' ? window.localStorage : null;
  
  return {
    getItem: (name: string) => {
      try {
        return storage?.getItem(name) || null;
      } catch (error) {
        console.warn('Failed to read from localStorage:', error);
        return null;
      }
    },
    setItem: (name: string, value: string) => {
      try {
        storage?.setItem(name, value);
      } catch (error) {
        // QuotaExceededError - 存储空间已满
        if (error instanceof DOMException && error.name === 'QuotaExceededError') {
          console.warn('localStorage quota exceeded, clearing old data...');
          
          try {
            // 尝试清理旧的历史记录
            const existingData = storage?.getItem(name);
            if (existingData) {
              const parsed = JSON.parse(existingData);
              if (parsed?.state?.taskHistory) {
                // 只保留最近 3 条记录
                parsed.state.taskHistory = parsed.state.taskHistory.slice(0, 3);
                storage?.setItem(name, JSON.stringify(parsed));
                console.log('Cleaned up task history to free space');
              }
            }
          } catch (cleanupError) {
            // 如果清理失败，清空整个存储
            console.warn('Failed to clean up, clearing storage:', cleanupError);
            storage?.removeItem(name);
          }
        } else {
          console.warn('Failed to write to localStorage:', error);
        }
      }
    },
    removeItem: (name: string) => {
      try {
        storage?.removeItem(name);
      } catch (error) {
        console.warn('Failed to remove from localStorage:', error);
      }
    },
    get length() {
      return storage?.length || 0;
    },
    key: (index: number) => storage?.key(index) || null,
    clear: () => storage?.clear(),
  };
};

// =============================================
// Store 实现
// =============================================

export const useAppStore = create<AppState>()(
  persist(
    (set, get) => ({
      // 初始状态
      images: [],
      config: defaultProcessConfig,
      currentTask: null,
      taskHistory: [],
      selectedImageIds: [],
      isProcessing: false,
      activeTab: 'upload',
      
      // 添加图像
      addImages: (files) => {
        set((state) => ({
          images: [...state.images, ...files],
        }));
      },
      
      // 移除图像
      removeImages: (ids) => {
        set((state) => ({
          images: state.images.filter((img) => !ids.includes(img.id)),
          selectedImageIds: state.selectedImageIds.filter((id) => !ids.includes(id)),
        }));
      },
      
      // 清空所有图像
      clearImages: () => {
        set({
          images: [],
          selectedImageIds: [],
        });
      },
      
      // 切换图像选中状态
      toggleImageSelection: (id) => {
        set((state) => ({
          selectedImageIds: state.selectedImageIds.includes(id)
            ? state.selectedImageIds.filter((i) => i !== id)
            : [...state.selectedImageIds, id],
        }));
      },
      
      // 全选
      selectAllImages: () => {
        set((state) => ({
          selectedImageIds: state.images.map((img) => img.id),
        }));
      },
      
      // 取消全选
      deselectAllImages: () => {
        set({ selectedImageIds: [] });
      },
      
      // 更新配置
      updateConfig: (key, value) => {
        set((state) => ({
          config: {
            ...state.config,
            [key]: value,
          },
        }));
      },
      
      // 重置配置
      resetConfig: () => {
        set({ config: defaultProcessConfig });
      },
      
      // 开始处理
      startProcessing: () => {
        const { images, config, selectedImageIds } = get();
        const selectedImages = images.filter((img) =>
          selectedImageIds.includes(img.id)
        );
        
        if (selectedImages.length === 0) return;
        
        const task: BatchTask = {
          id: uuidv4(),
          files: selectedImages,
          config,
          results: selectedImages.map((img) => ({
            id: img.id,
            originalName: img.name,
            status: 'pending',
          })),
          status: 'processing',
          progress: 0,
          startTime: Date.now(),
        };
        
        set({
          currentTask: task,
          isProcessing: true,
        });
      },
      
      // 更新处理结果
      updateProcessResult: (result) => {
        set((state) => {
          if (!state.currentTask) return state;
          
          const results = state.currentTask.results.map((r) =>
            r.id === result.id ? result : r
          );
          
          const completedCount = results.filter(
            (r) => r.status === 'success' || r.status === 'error'
          ).length;
          const progress = (completedCount / results.length) * 100;
          
          return {
            currentTask: {
              ...state.currentTask,
              results,
              progress,
            },
          };
        });
      },
      
      // 完成处理
      completeProcessing: () => {
        set((state) => {
          if (!state.currentTask) return state;
          
          // 精简任务数据，移除大型二进制数据
          const completedTask = stripLargeData({
            ...state.currentTask,
            status: 'completed',
            progress: 100,
            endTime: Date.now(),
          });
          
          // 只保留最近 5 条历史记录
          const newHistory = [completedTask, ...state.taskHistory].slice(0, 5);
          
          return {
            currentTask: null,
            taskHistory: newHistory,
            isProcessing: false,
            activeTab: 'results',
          };
        });
      },
      
      // 设置活动标签页
      setActiveTab: (tab) => {
        set({ activeTab: tab });
      },
      
      // 清理任务历史
      clearTaskHistory: () => {
        set({ taskHistory: [] });
      },
    }),
    {
      name: 'snapforge-storage',
      storage: createJSONStorage(() => createCustomStorage()),
      // 只持久化必要的配置和精简后的历史
      partialize: (state) => ({
        config: state.config,
        // 历史记录已经通过 stripLargeData 精简
        taskHistory: state.taskHistory,
      }),
    }
  )
);

// =============================================
// 选择器 Hooks
// =============================================

export const useImages = () => useAppStore((state) => state.images);
export const useConfig = () => useAppStore((state) => state.config);
export const useIsProcessing = () => useAppStore((state) => state.isProcessing);
export const useSelectedImages = () =>
  useAppStore((state) =>
    state.images.filter((img) => state.selectedImageIds.includes(img.id))
  );
export const useCurrentTask = () => useAppStore((state) => state.currentTask);
