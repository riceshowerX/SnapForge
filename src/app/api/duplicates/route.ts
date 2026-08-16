import { NextRequest, NextResponse } from 'next/server';
import {
  calculateImageHash,
  calculateHashSimilarity,
} from '@/lib/image-processor';
import { v4 as uuidv4 } from 'uuid';
import {
  successResponse,
  errorResponse,
  ErrorCodes,
} from '@/lib/api-response';
import { checkRateLimit, getRateLimitHeaders } from '@/lib/rate-limit';
import {
  ALLOWED_TYPES,
  MAX_FILE_SIZE,
  MAX_DUPLICATES_BODY_SIZE,
  detectImageMime,
} from '@/lib/file-validation';
import { enforceContentLength } from '@/lib/request-guard';

// =============================================
// POST /api/duplicates - 检测重复图片
// =============================================
// S-03：Content-Length 强校验（上限降至 105MB）；
// S-04：逐文件 magic number 校验；
// F-10：hashMap 键改为显式 imageId（客户端通过并行字段 `id` 传入，
//       缺失时回退到文件名+下标），组内 similarity 取真实最小相似度。

const MAX_TOTAL_SIZE = 100 * 1024 * 1024; // 100MB total（服务端再收紧一道）
const MAX_FILES = 100;
const MIN_THRESHOLD = 0.5;
const MAX_THRESHOLD = 1.0;

// 扩展的重复图片信息，支持 imageId
interface DuplicateImage {
  id: string;
  name: string; // 展示用文件名（可能是 imageId 或原始文件名）
  size: number;
  type: string;
  imageId?: string; // 原始图片 ID（前端精确匹配用）
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
        errorResponse(
          ErrorCodes.INVALID_REQUEST,
          'Invalid content type. Expected multipart/form-data'
        ),
        { status: 400 }
      );
    }

    // S-03：在 request.formData() 之前做强 Content-Length 校验
    const bodyTooLarge = enforceContentLength(
      request,
      MAX_DUPLICATES_BODY_SIZE
    );
    if (bodyTooLarge) {
      return bodyTooLarge;
    }

    const formData = await request.formData();
    const files = formData.getAll('files') as File[];
    // F-10：显式 imageId 列表，与 files 按下标一一对应
    const ids = formData.getAll('id') as string[];
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
    if (
      Number.isNaN(threshold) ||
      threshold < MIN_THRESHOLD ||
      threshold > MAX_THRESHOLD
    ) {
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

      // S-04：magic number 校验（不信任客户端 MIME）
      const fileBuffer = Buffer.from(await file.arrayBuffer());
      const detectedMime = detectImageMime(fileBuffer);
      if (
        !detectedMime ||
        !ALLOWED_TYPES.includes(
          detectedMime as (typeof ALLOWED_TYPES)[number]
        )
      ) {
        return NextResponse.json(
          errorResponse(
            ErrorCodes.INVALID_FILE_TYPE,
            `File ${file.name} has unsupported or invalid type`,
            { filename: file.name, allowedTypes: ALLOWED_TYPES, detectedMime: detectedMime || null }
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

    // 计算所有图片的哈希（键：显式 imageId；回退：文件名 + 下标）
    const hashMap = new Map<
      string,
      { file: File; hash: string; index: number }
    >();

    for (let i = 0; i < files.length; i++) {
      const file = files[i];
      const imageId = (ids[i] && ids[i].trim()) || file.name;
      const uniqueKey = `${imageId}__${i}`;
      try {
        const buffer = Buffer.from(await file.arrayBuffer());
        const hash = await calculateImageHash(buffer);
        hashMap.set(uniqueKey, { file, hash, index: i });
      } catch (error) {
        console.warn(`Failed to hash file ${file.name}:`, error);
        // 跳过无法处理的文件
      }
    }

    // 找出相似的图片组
    const groups: DuplicateGroup[] = [];
    const processed = new Set<string>();

    for (const [key1, data1] of hashMap) {
      if (processed.has(key1)) continue;

      const imageId1 = (ids[data1.index] && ids[data1.index].trim()) || data1.file.name;
      const similar: DuplicateImage[] = [
        {
          id: uuidv4(),
          name: data1.file.name,
          size: data1.file.size,
          type: data1.file.type,
          imageId: imageId1,
        },
      ];

      const groupHashes: { key: string; imageId: string; hash: string }[] = [
        { key: key1, imageId: imageId1, hash: data1.hash },
      ];

      for (const [key2, data2] of hashMap) {
        if (key1 === key2 || processed.has(key2)) continue;

        const similarity = calculateHashSimilarity(data1.hash, data2.hash);

        if (similarity >= threshold) {
          const imageId2 =
            (ids[data2.index] && ids[data2.index].trim()) || data2.file.name;
          similar.push({
            id: uuidv4(),
            name: data2.file.name,
            size: data2.file.size,
            type: data2.file.type,
            imageId: imageId2,
          });
          groupHashes.push({ key: key2, imageId: imageId2, hash: data2.hash });
          processed.add(key2);
        }
      }

      if (similar.length > 1) {
        // F-10：组内 similarity 取真实两两最小相似度（而非阈值）
        let minSimilarity = 1;
        for (let i = 0; i < groupHashes.length; i++) {
          for (let j = i + 1; j < groupHashes.length; j++) {
            const sim = calculateHashSimilarity(
              groupHashes[i].hash,
              groupHashes[j].hash
            );
            if (sim < minSimilarity) minSimilarity = sim;
          }
        }

        groups.push({
          id: uuidv4(),
          images: similar,
          similarity: minSimilarity,
          hash: data1.hash,
        });
      }

      processed.add(key1);
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
      errorResponse(
        ErrorCodes.DETECTION_FAILED,
        'Duplicate detection failed. Please try again.'
      ),
      { status: 500 }
    );
  }
}
