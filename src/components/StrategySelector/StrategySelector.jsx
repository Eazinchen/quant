import React from 'react';

const StrategySelector = ({ strategies, selectedStrategy, onSelectStrategy }) => {
  // 根据选中的策略ID找到对应的策略对象
  const selectedStrategyObj = strategies.find(strategy => strategy.id === selectedStrategy);

  return (
    <div className="card">
      <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
        {/* 策略选择下拉框 */}
        <div className="w-full md:w-auto">
          <label className="block text-sm font-medium text-gray-700 mb-1">选择量化策略</label>
          <select
            className="w-full md:w-64 p-2 border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-wsj-accent"
            value={selectedStrategy || ''}
            onChange={(e) => onSelectStrategy(e.target.value ? parseInt(e.target.value) : null)}
          >
            <option value="" disabled>请选择策略</option>
            {strategies.map(strategy => (
              <option key={strategy.id} value={strategy.id}>
                {strategy.name}
              </option>
            ))}
          </select>
        </div>

        {/* 策略说明卡片 */}
        {selectedStrategyObj && (
          <div className="w-full md:w-auto flex-1 p-4 border border-gray-200 rounded-sm bg-gray-50">
            <h3 className="font-serif font-bold text-lg mb-2">{selectedStrategyObj.name}</h3>
            <p className="text-gray-700 mb-3">{selectedStrategyObj.description}</p>
            <div className="text-sm text-gray-600">
              <h4 className="font-medium mb-1">参数设置：</h4>
              <ul className="list-disc list-inside space-y-1">
                {Object.entries(selectedStrategyObj.params).map(([key, value]) => (
                  <li key={key}>
                    {key.replace('_', ' ')}: {value}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default StrategySelector;