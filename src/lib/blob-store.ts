// =============================================
// SnapForge IndexedDB Blob 存储
// =============================================
// 用于把 >2MB 大图的原始 Blob 落到 IndexedDB，store 中只保留小缩略图 + blobKey，
// 从根本上解决 base64 全量驻留内存问题（P-02）与大图原始数据丢失问题（F-01）。
//
// 降级策略：任何 IndexedDB 不可用 / 写入失败（如 QuotaExceededError）时返回 false，
// 调用方应保留 originalDataUrl 于内存中，保证功能正确优先。

const DB_NAME = 'snapforge-blobs';
const STORE_NAME = 'images';
const DB_VERSION = 1;

let dbPromise: Promise<IDBDatabase | null> | null = null;

function isIndexedDBAvailable(): boolean {
  return typeof window !== 'undefined' && 'indexedDB' in window;
}

function openDb(): Promise<IDBDatabase | null> {
  if (!isIndexedDBAvailable()) return Promise.resolve(null);
  if (dbPromise) return dbPromise;

  dbPromise = new Promise((resolve) => {
    try {
      const request = indexedDB.open(DB_NAME, DB_VERSION);

      request.onupgradeneeded = () => {
        const db = request.result;
        if (!db.objectStoreNames.contains(STORE_NAME)) {
          db.createObjectStore(STORE_NAME);
        }
      };

      request.onsuccess = () => {
        resolve(request.result);
      };

      request.onerror = () => {
        console.warn('[blob-store] IndexedDB open failed:', request.error);
        resolve(null);
      };

      request.onblocked = () => {
        console.warn('[blob-store] IndexedDB open blocked');
        resolve(null);
      };
    } catch (error) {
      console.warn('[blob-store] IndexedDB unavailable:', error);
      resolve(null);
    }
  });

  return dbPromise;
}

/**
 * 存储 Blob。成功返回 true；失败（含 QuotaExceededError）返回 false，
 * 调用方据此回退到内存 base64。
 */
export async function putBlob(key: string, blob: Blob): Promise<boolean> {
  const db = await openDb();
  if (!db) return false;

  return new Promise((resolve) => {
    try {
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.put(blob, key);

      transaction.oncomplete = () => resolve(true);
      transaction.onerror = () => {
        if (transaction.error?.name === 'QuotaExceededError') {
          console.warn('[blob-store] Quota exceeded, falling back to memory');
        } else {
          console.warn('[blob-store] put failed:', transaction.error);
        }
        resolve(false);
      };
      transaction.onabort = () => {
        console.warn('[blob-store] transaction aborted');
        resolve(false);
      };
    } catch (error) {
      console.warn('[blob-store] put threw:', error);
      resolve(false);
    }
  });
}

/** 读取 Blob。不存在或失败时返回 null。 */
export async function getBlob(key: string): Promise<Blob | null> {
  const db = await openDb();
  if (!db) return null;

  return new Promise((resolve) => {
    try {
      const transaction = db.transaction(STORE_NAME, 'readonly');
      const store = transaction.objectStore(STORE_NAME);
      const request = store.get(key);

      request.onsuccess = () => {
        const result = request.result;
        resolve(result instanceof Blob ? result : null);
      };
      request.onerror = () => {
        console.warn('[blob-store] get failed:', request.error);
        resolve(null);
      };
    } catch (error) {
      console.warn('[blob-store] get threw:', error);
      resolve(null);
    }
  });
}

/** 删除 Blob。不存在视为成功。 */
export async function deleteBlob(key: string): Promise<boolean> {
  const db = await openDb();
  if (!db) return false;

  return new Promise((resolve) => {
    try {
      const transaction = db.transaction(STORE_NAME, 'readwrite');
      const store = transaction.objectStore(STORE_NAME);
      store.delete(key);

      transaction.oncomplete = () => resolve(true);
      transaction.onerror = () => {
        console.warn('[blob-store] delete failed:', transaction.error);
        resolve(false);
      };
    } catch (error) {
      console.warn('[blob-store] delete threw:', error);
      resolve(false);
    }
  });
}

/**
 * 从 ImageFile 获取可用于处理/解析的原始 Blob。
 * 优先级：blobKey（IndexedDB）→ originalDataUrl（内存 base64）→ preview。
 * 全部不可用时返回 null。
 */
export async function getImageBlob(image: {
  blobKey?: string;
  originalDataUrl?: string;
  preview?: string;
  type?: string;
}): Promise<Blob | null> {
  if (image.blobKey) {
    const blob = await getBlob(image.blobKey);
    if (blob) return blob;
  }

  const dataUrl = image.originalDataUrl || image.preview;
  if (dataUrl && dataUrl.startsWith('data:')) {
    try {
      // 用 fetch 解码 data URL，避免 atob 大循环阻塞主线程
      const response = await fetch(dataUrl);
      if (response.ok) {
        return await response.blob();
      }
    } catch (error) {
      console.warn('[blob-store] failed to decode data URL:', error);
    }
  }

  return null;
}
