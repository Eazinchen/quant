import React, { useState, useEffect } from 'react';
import StrategySelector from './components/StrategySelector/StrategySelector';
import MetricCards from './components/MetricCards/MetricCards';
import ChartPanel from './components/ChartPanel/ChartPanel';
import ImageUploader from './components/ImageUploader/ImageUploader';
import ExportButton from './components/ExportButton/ExportButton';
import { fetchStrategies, runBacktest } from './services/api';

function App() {
  const [strategies, setStrategies] = useState([]);
  const [selectedStrategy, setSelectedStrategy] = useState(null);
  const [stockCode, setStockCode] = useState('000001'); // 默认股票代码
  const [startDate, setStartDate] = useState('20240101'); // 默认起始时间
  const [endDate, setEndDate] = useState(new Date().toISOString().slice(0, 10).replace(/-/g, '')); // 默认结束时间
  const [backtestResults, setBacktestResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(''); // 错误信息
  const [uploadedImage, setUploadedImage] = useState(null);

  // 当策略、股票代码或日期范围变化时，清除回测结果
  useEffect(() => {
    setBacktestResults(null);
    setError('');
  }, [selectedStrategy, stockCode, startDate, endDate]);

  // 加载策略列表
  useEffect(() => {
    const loadStrategies = async () => {
      try {
        const data = await fetchStrategies();
        setStrategies(data);
        if (data.length > 0) {
          setSelectedStrategy(data[0].id);
        }
      } catch (error) {
        console.error('Failed to load strategies:', error);
      }
    };
    loadStrategies();
  }, []);

  // 移除自动运行回测的功能，只在用户点击"确认回测"按钮时才运行回测

  return (
    <div className="min-h-screen bg-white">
      {/* 头部 */}
      <header className="border-b border-gray-200 py-6 px-4 md:px-8">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl md:text-4xl font-serif font-bold">A股量化交易回测可视化系统</h1>
          <p className="text-gray-600 mt-2">基于WSJ风格设计的专业量化策略分析工具</p>
        </div>
      </header>

      {/* 主内容 */}
      <main className="max-w-7xl mx-auto py-8 px-4 md:px-8">
        {/* 策略选择和股票代码输入区域 */}
        <section className="mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* 股票代码和时间范围输入 */}
            <div className="card">
              <label className="block text-sm font-medium text-gray-700 mb-1">股票代码</label>
              <div className="flex gap-2 mb-4">
                <input
                  type="text"
                  value={stockCode}
                  onChange={(e) => setStockCode(e.target.value)}
                  placeholder="请输入A股股票代码，例如：000001"
                  className="flex-1 p-2 border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-wsj-accent"
                />
              </div>

              {/* 时间范围选择 */}
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-1">时间范围</label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={startDate}
                    onChange={(e) => setStartDate(e.target.value)}
                    placeholder="起始时间，格式：YYYYMMDD"
                    className="flex-1 p-2 border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-wsj-accent"
                  />
                  <input
                    type="text"
                    value={endDate}
                    onChange={(e) => setEndDate(e.target.value)}
                    placeholder="结束时间，格式：YYYYMMDD"
                    className="flex-1 p-2 border border-gray-300 rounded-sm focus:outline-none focus:ring-1 focus:ring-wsj-accent"
                  />
                </div>
                <p className="text-xs text-gray-500 mt-1">示例：20240101（2024年1月1日）</p>
              </div>

              {/* 确认按钮 */}
              <button
                className={`btn w-full ${!selectedStrategy ? 'opacity-50 cursor-not-allowed' : ''}`}
                disabled={!selectedStrategy}
                onClick={() => {
                  // 手动触发回测
                  if (selectedStrategy) {
                    setLoading(true);
                    setError(''); // 清除之前的错误
                    console.log('开始回测:', { strategyId: selectedStrategy, stockCode, startDate, endDate });
                    runBacktest(selectedStrategy, stockCode, startDate, endDate)
                      .then(results => {
                        console.log('回测成功:', results);
                        setBacktestResults(results);
                      })
                      .catch(error => {
                        console.error('回测失败:', error);
                        setError(error.message || '回测失败，请检查股票代码是否正确或稍后重试');
                        setBacktestResults(null); // 清除之前的结果
                      })
                      .finally(() => setLoading(false));
                  }
                }}
              >
                确认回测
              </button>
              <p className="text-xs text-gray-500 mt-1">示例股票代码：000001（平安银行）、600519（贵州茅台）</p>
            </div>

            {/* 策略选择 */}
            <StrategySelector 
              strategies={strategies} 
              selectedStrategy={selectedStrategy} 
              onSelectStrategy={setSelectedStrategy} 
            />
          </div>
        </section>

        {/* 回测结果区域 */}
        {loading ? (
          <div className="flex justify-center items-center h-64">
            <p>正在运行回测，请稍候...</p>
          </div>
        ) : error ? (
          <div className="flex justify-center items-center h-64">
            <div className="text-center">
              <p className="text-red-500 mb-4">{error}</p>
              <button
                className="btn"
                onClick={() => {
                  setError('');
                  // 重新尝试回测
                  if (selectedStrategy) {
                    setLoading(true);
                    runBacktest(selectedStrategy, stockCode)
                      .then(results => setBacktestResults(results))
                      .catch(error => {
                        console.error('Failed to run backtest:', error);
                        setError(error.message || '回测失败，请检查股票代码是否正确或稍后重试');
                      })
                      .finally(() => setLoading(false));
                  }
                }}
              >
                重新尝试
              </button>
            </div>
          </div>
        ) : backtestResults ? (
          <>
            {/* 绩效指标卡片 */}
            <section className="mb-8">
              <MetricCards metrics={backtestResults.metrics} />
            </section>

            {/* 图表和上传区域 */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
              {/* 图表区域 */}
              <div className="lg:col-span-2 space-y-6">
                <ChartPanel 
                  title="净值曲线 vs 基准" 
                  chartData={backtestResults.charts.equity_curve} 
                />
                <ChartPanel 
                  title="月度收益热力图" 
                  chartData={backtestResults.charts.heatmap} 
                />
              </div>

              {/* 图片上传区域 */}
              <div className="space-y-6">
                <ImageUploader 
                  uploadedImage={uploadedImage} 
                  onImageUpload={setUploadedImage} 
                />
              </div>
            </div>

            {/* 导出按钮 */}
            <section className="mb-8">
              <ExportButton />
            </section>
          </>
        ) : (
          <div className="flex justify-center items-center h-64">
            <p>请选择一个策略开始回测</p>
          </div>
        )}
      </main>

      {/* 页脚 */}
      <footer className="border-t border-gray-200 py-6 px-4 md:px-8">
        <div className="max-w-7xl mx-auto text-center text-gray-500 text-sm">
          <p>© {new Date().getFullYear()} A股量化交易回测可视化系统 | WSJ风格设计</p>
        </div>
      </footer>
    </div>
  );
}

export default App;