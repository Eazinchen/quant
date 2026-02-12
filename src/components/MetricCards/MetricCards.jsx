import React from 'react';

const MetricCards = ({ metrics }) => {
  // 定义指标配置，包含显示名称、值和格式化函数
  const metricConfigs = [
    {
      key: '年化收益率',
      label: '年化收益率',
      format: (value) => `${(value * 100).toFixed(2)}%`,
      value: metrics['年化收益率'] || 0
    },
    {
      key: '累计收益率',
      label: '累计收益率',
      format: (value) => `${(value * 100).toFixed(2)}%`,
      value: metrics['累计收益率'] || 0
    },
    {
      key: '最大回撤',
      label: '最大回撤',
      format: (value) => `${(value * 100).toFixed(2)}%`,
      value: metrics['最大回撤'] || 0
    },
    {
      key: '夏普比率',
      label: '夏普比率',
      format: (value) => value.toFixed(2),
      value: metrics['夏普比率'] || 0
    },
    {
      key: '胜率',
      label: '胜率',
      format: (value) => `${(value * 100).toFixed(2)}%`,
      value: metrics['胜率'] || 0
    },
    {
      key: '盈亏比',
      label: '盈亏比',
      format: (value) => value.toFixed(2),
      value: metrics['盈亏比'] || 0
    }
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
      {metricConfigs.map((config) => (
        <div key={config.key} className="card">
          <div className="metric-label">{config.label}</div>
          <div className="metric-value">{config.format(config.value)}</div>
        </div>
      ))}
    </div>
  );
};

export default MetricCards;