import React, { useState } from 'react';

const ImageUploader = ({ uploadedImage, onImageUpload }) => {
  const [previewImage, setPreviewImage] = useState(uploadedImage);
  const [error, setError] = useState('');

  // 处理图片上传
  const handleImageUpload = (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // 验证文件类型
    const validTypes = ['image/jpeg', 'image/png'];
    if (!validTypes.includes(file.type)) {
      setError('只支持JPG和PNG格式的图片');
      return;
    }

    // 验证文件大小（限制为5MB）
    if (file.size > 5 * 1024 * 1024) {
      setError('图片大小不能超过5MB');
      return;
    }

    // 生成预览
    const reader = new FileReader();
    reader.onloadend = () => {
      setPreviewImage(reader.result);
      onImageUpload(reader.result);
      setError('');
    };
    reader.readAsDataURL(file);
  };

  // 处理拖拽上传
  const handleDragOver = (e) => {
    e.preventDefault();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files[0];
    if (file) {
      // 创建一个模拟的input事件
      const inputEvent = new Event('change', { bubbles: true });
      Object.defineProperty(e.target, 'files', {
        value: [file],
        writable: false
      });
      handleImageUpload({ target: { files: [file] } });
    }
  };

  return (
    <div className="card">
      <h3 className="font-serif font-bold text-lg mb-4">图片上传</h3>
      <p className="text-sm text-gray-600 mb-4">
        上传您的策略草图或其他参考图片，将与回测结果一起导出
      </p>

      {/* 上传区域 */}
      <div
        className="border-2 border-dashed border-gray-300 rounded-sm p-6 text-center hover:border-wsj-accent transition-colors"
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <input
          type="file"
          id="image-upload"
          accept="image/jpeg, image/png"
          onChange={handleImageUpload}
          className="hidden"
        />
        <label
          htmlFor="image-upload"
          className="cursor-pointer flex flex-col items-center justify-center gap-2"
        >
          <div className="text-gray-500">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-12 w-12 mx-auto"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
          </div>
          <p className="text-sm font-medium text-gray-700">点击或拖拽上传图片</p>
          <p className="text-xs text-gray-500">支持JPG和PNG格式，最大5MB</p>
        </label>
      </div>

      {/* 错误信息 */}
      {error && (
        <p className="text-red-500 text-sm mt-2">{error}</p>
      )}

      {/* 预览区域 */}
      {previewImage && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-700 mb-2">预览</h4>
          <div className="border border-gray-200 rounded-sm p-2">
            <img
              src={previewImage}
              alt="上传预览"
              className="w-full h-auto object-contain max-h-64"
            />
          </div>
        </div>
      )}
    </div>
  );
};

export default ImageUploader;