import React from 'react';
import html2canvas from 'html2canvas';

const ExportButton = () => {
  // 处理导出为图片
  const handleExport = async () => {
    try {
      // 获取要截图的元素（这里假设main标签包含了所有要导出的内容）
      const element = document.querySelector('main');
      if (!element) {
        console.error('未找到要导出的元素');
        return;
      }

      // 使用html2canvas生成截图
      const canvas = await html2canvas(element, {
        scale: 2, // 提高清晰度
        useCORS: true, // 允许加载跨域图片
        logging: false,
        backgroundColor: '#ffffff'
      });

      // 将canvas转换为图片URL
      const image = canvas.toDataURL('image/png');

      // 创建下载链接并触发下载
      const link = document.createElement('a');
      link.download = `回测结果_${new Date().toISOString().slice(0, 10)}.png`;
      link.href = image;
      link.click();
    } catch (error) {
      console.error('导出失败:', error);
      alert('导出失败，请重试');
    }
  };

  return (
    <div className="flex justify-center">
      <button
        className="btn flex items-center gap-2"
        onClick={handleExport}
      >
        <svg
          xmlns="http://www.w3.org/2000/svg"
          className="h-5 w-5"
          fill="none"
          viewBox="0 0 24 24"
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"
          />
        </svg>
        导出为图片
      </button>
    </div>
  );
};

export default ExportButton;