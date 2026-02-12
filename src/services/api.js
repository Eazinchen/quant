import axios from 'axios';

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
});

// 获取策略列表
export const fetchStrategies = async () => {
  try {
    const response = await api.get('/strategies');
    return response.data;
  } catch (error) {
    console.error('Error fetching strategies:', error);
    // 返回默认策略列表，用于前端开发测试
    return [
      {
        id: 1,
        name: '双均线金叉死叉',
        description: '基于短期和长期移动平均线的交叉信号进行交易',
        params: {
          short_window: 50,
          long_window: 200
        }
      },
      {
        id: 2,
        name: 'RSI超卖反转',
        description: '当RSI指标低于超卖阈值后反弹时买入，高于超买阈值后回落时卖出',
        params: {
          rsi_period: 14,
          overbought: 70,
          oversold: 30
        }
      },
      {
        id: 3,
        name: '布林带突破',
        description: '基于价格突破布林带上下轨的信号进行交易',
        params: {
          window: 20,
          num_std: 2
        }
      }
    ];
  }
};

// 运行回测
export const runBacktest = async (strategyId, stockCode = '000001', startDate = '20240101', endDate = new Date().toISOString().slice(0, 10).replace(/-/g, '')) => {
  try {
    const response = await api.post('/backtest', { 
      strategy_id: strategyId, 
      stock_code: stockCode,
      start_date: startDate,
      end_date: endDate
    });
    return response.data;
  } catch (error) {
    console.error('Error running backtest:', error);
    // 抛出错误，让前端处理
    throw new Error('回测失败，请检查股票代码是否正确或稍后重试');
  }
};