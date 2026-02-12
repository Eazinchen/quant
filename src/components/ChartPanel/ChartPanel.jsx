import React from 'react';

const ChartPanel = ({ title, chartData }) => {
  return (
    <div className="chart-container p-4">
      <h3 className="font-serif font-bold text-lg mb-4">{title}</h3>
      <div className="relative">
        {chartData ? (
          <img 
            src={chartData} 
            alt={title} 
            className="w-full h-auto"
          />
        ) : (
          <div className="flex justify-center items-center h-64 bg-gray-50">
            <p>图表数据加载中...</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChartPanel;