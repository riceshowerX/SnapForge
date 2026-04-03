import { NextRequest, NextResponse } from 'next/server';
import { calculateImageHash, calculateHashSimilarity } from '@/lib/image-processor';
import { v4 as uuidv4 } from 'uuid';
import { 
  successResponse, 
  errorResponse, 
  ErrorCodes 
} from '@/lib/api-response';
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit';

// =============================================
// POST /api/duplicates - 检测重复图片
// =============================================

const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB per file
const MAX_TOTAL_SIZE = 200 * 1024 * 1024; // 200MB total
const MAX_FILES = 100;
const MIN_THRESHOLD = 0.5;
const MAX_THRESHOLD = 1.0;

const ALLOWED_TYPES = [
  'image/jpeg',
  'image/png', 
  'image/webp',
  'image/gif',
  'image/bmp',
  'image/tiff'
];

// 扩展的重复图片信息，支持 imageId
interface DuplicateImage {
  id: string;
  name: string; // 原始文件名（可能是 imageId）
  size: number;
  type: string;
  imageId?: string; // 原始图片 ID
}

interface DuplicateGroup {
  id: string;
  images: DuplicateImage[];
  similarity: number;
  hash?: string;
}

export async function POST(request: NextRequest) {
  try {
    // 检查速率限制
    const rateLimit = checkRateLimit(request, 'duplicates');
    if (!rateLimit.allowed && rateLimit.response) {
      return rateLimit.response;
    }

    // 检查 Content-Type
    const contentType = request.headers.get('content-type') || '';
    if (!contentType.includes('multipart/form-data')) {
      return NextResponse.json(
        errorResponse(ErrorCodes.INVALID_REQUEST, 'Invalid content type. Expected multipart/form-data'),
        { status: 400 }
      );
    }

    const formData = await request.formData();
    const files = formData.getAll('files') as File[];
    const thresholdStr = formData.get('threshold') as string | null;
    
    if (!files || files.length === 0) {
      return NextResponse.json(
        errorResponse(ErrorCodes.NO_FILE_PROVIDED, 'No files provided'),
        { status: 400 }
      );
    }

    // 限制文件数量
    if (files.length > MAX_FILES) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.TOO_MANY_FILES, 
          `Too many files. Maximum: ${MAX_FILES}`,
          { maxFiles: MAX_FILES, actualFiles: files.length }
        ),
        { status: 400 }
      );
    }

    // 验证阈值参数
    const threshold = thresholdStr ? parseFloat(thresholdStr) : 0.9;
    if (isNaN(threshold) || threshold < MIN_THRESHOLD || threshold > MAX_THRESHOLD) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.INVALID_THRESHOLD, 
          `Invalid threshold. Must be between ${MIN_THRESHOLD} and ${MAX_THRESHOLD}`,
          { min: MIN_THRESHOLD, max: MAX_THRESHOLD, actual: threshold }
        ),
        { status: 400 }
      );
    }

    // 验证文件
    let totalSize = 0;
    for (const file of files) {
      // 检查文件大小
      if (file.size > MAX_FILE_SIZE) {
        return NextResponse.json(
          errorResponse(
            ErrorCodes.FILE_TOO_LARGE, 
            `File ${file.name} exceeds maximum size of ${MAX_FILE_SIZE / 1024 / 1024}MB`,
            { filename: file.name, maxSize: MAX_FILE_SIZE, actualSize: file.size }
          ),
          { status: 400 }
        );
      }
      
      // 检查文件类型
      if (!ALLOWED_TYPES.includes(file.type)) {
        return NextResponse.json(
          errorResponse(
            ErrorCodes.INVALID_FILE_TYPE, 
            `File ${file.name} has unsupported type: ${file.type}`,
            { filename: file.name, allowedTypes: ALLOWED_TYPES, actualType: file.type }
          ),
          { status: 400 }
        );
      }
      
      totalSize += file.size;
    }

    // 检查总大小
    if (totalSize > MAX_TOTAL_SIZE) {
      return NextResponse.json(
        errorResponse(
          ErrorCodes.TOTAL_SIZE_EXCEEDED, 
          `Total file size exceeds maximum of ${MAX_TOTAL_SIZE / 1024 / 1024}MB`,
          { maxSize: MAX_TOTAL_SIZE, actualSize: totalSize }
        ),
        { status: 400 }
      );
    }
    
    // 计算所有图片的哈希
    // 文件名现在可能是 imageId，用于精确匹配
    const hashMap = new Map<string, { file: File; hash: string; index: number }>();
    
    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      try {
        const buffer = Buffer.from(await file.arrayBuffer());
        const hash = await calculateImageHash(buffer);
        // 使用文件名（可能是 imageId）作为键
        hashMap.set(file.name, { file, hash, index: i });
      } catch (error) {
        console.warn(`Failed to hash file ${file.name}:`, error);
        // 跳过无法处理的文件
      }
    }
    
    // 找出相似的图片组
    const groups: DuplicateGroup[] = [];
    const processed = new Set<string>();
    
    for (const [name1, data1] of hashMap) {
      if (processed.has(name1)) continue;
      
      const similar: DuplicateImage[] = [{
        id: uuidv4(),
        name: name1, // 这可能是 imageId
        size: data1.file.size,
        type: data1.file.type,
        imageId: name1, // 假设文件名就是 imageId
      }];
      
      for (const [name2, data2] of hashMap) {
        if (name1 === name2 || processed.has(name2)) continue;
        
        const similarity = calculateHashSimilarity(data1.hash, data2.hash);
        
        if (similarity >= threshold) {
          similar.push({
            id: uuidv4(),
            name: name2, // 这可能是 imageId
            size: data2.file.size,
            type: data2.file.type,
            imageId: name2, // 假设文件名就是 imageId
          });
          processed.add(name2);
        }
      }
      
      if (similar.length > 1) {
        groups.push({
          id: uuidv4(),
          images: similar,
          similarity: threshold,
          hash: data1.hash,
        });
      }
      
      processed.add(name1);
    }
    
    return NextResponse.json(
      successResponse({
        groups,
        totalScanned: hashMap.size,
        duplicatesFound: groups.reduce((sum, g) => sum + g.images.length, 0),
      }),
      {
        headers: getRateLimitHeaders('duplicates'),
      }
    );
  } catch (error) {
    console.error('Duplicate detection error:', error);
    return NextResponse.json(
      errorResponse(ErrorCodes.DETECTION_FAILED, 'Duplicate detection failed. Please try again.'),
      { status: 500 }
    );
  }
}
