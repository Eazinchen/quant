from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd
import numpy as np
import base64
from io import BytesIO

from strategies import moving_average_crossover_strategy, bollinger_band_strategy, rsi_strategy
from backtest import BacktestEngine
from data import get_stock_data
from charts import generate_equity_curve, generate_heatmap

# 创建FastAPI应用
app = FastAPI(
    title="A股量化交易回测API",
    description="基于WSJ风格设计的专业量化策略分析工具",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # 前端地址
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 策略列表
strategies = [
    {
        "id": 1,
        "name": "双均线金叉死叉",
        "description": "基于短期和长期移动平均线的交叉信号进行交易",
        "params": {
            "short_window": 50,
            "long_window": 200
        }
    },
    {
        "id": 2,
        "name": "RSI超卖反转",
        "description": "当RSI指标低于超卖阈值后反弹时买入，高于超买阈值后回落时卖出",
        "params": {
            "rsi_period": 14,
            "overbought": 70,
            "oversold": 30
        }
    },
    {
        "id": 3,
        "name": "布林带突破",
        "description": "基于价格突破布林带上下轨的信号进行交易",
        "params": {
            "window": 20,
            "num_std": 2
        }
    }
]

# 获取策略列表
@app.get("/api/strategies")
def get_strategies():
    return strategies

class BacktestRequest(BaseModel):
    strategy_id: int
    stock_code: str = "000001"
    start_date: str = "20240101"
    end_date: str = None

# 运行回测
@app.post("/api/backtest")
def run_backtest(request: BacktestRequest):
    strategy_id = request.strategy_id
    stock_code = request.stock_code
    start_date = request.start_date
    end_date = request.end_date
    try:
        # 验证策略ID
        if strategy_id not in [s["id"] for s in strategies]:
            raise HTTPException(status_code=400, detail="无效的策略ID")

        # 获取股票数据
        try:
            data = get_stock_data(symbol=stock_code, start_date=start_date, end_date=end_date)
            print(f"股票数据形状: {data.shape}")
            print(f"股票数据日期范围: {data.index.min()} 到 {data.index.max()}")
            print(f"股票数据前5行:\n{data.head()}")
        except Exception as e:
            print(f"获取股票数据失败: {e}")
            # 注意：get_stock_data函数在获取真实数据失败时会返回模拟数据，所以这里不应该抛出异常
            # 只有当get_stock_data函数本身出现严重错误时，才会进入这里
            raise HTTPException(status_code=500, detail=f"获取股票数据失败: {e}")

        # 根据策略ID选择策略
        try:
            if strategy_id == 1:
                # 双均线金叉死叉策略
                print("使用双均线金叉死叉策略")
                data_with_signals = moving_average_crossover_strategy(data)
            elif strategy_id == 2:
                # RSI超卖反转策略
                print("使用RSI超卖反转策略")
                data_with_signals = rsi_strategy(data)
            elif strategy_id == 3:
                # 布林带突破策略
                print("使用布林带突破策略")
                data_with_signals = bollinger_band_strategy(data)
            else:
                raise HTTPException(status_code=400, detail="无效的策略ID")
            
            # 检查信号数量
            buy_signals = (data_with_signals['信号'] == 1).sum()
            sell_signals = (data_with_signals['信号'] == -1).sum()
            print(f"买入信号数量: {buy_signals}")
            print(f"卖出信号数量: {sell_signals}")
            print(f"信号列统计:\n{data_with_signals['信号'].describe()}")
            
        except Exception as e:
            print(f"生成交易信号失败: {e}")
            raise HTTPException(status_code=500, detail=f"生成交易信号失败: {e}")

        # 创建回测引擎实例
        try:
            backtest_engine = BacktestEngine(
                data_with_signals,
                initial_capital=100000,
                transaction_cost=0.001,
                slippage=0.0005
            )
            print("回测引擎实例创建成功")
        except Exception as e:
            print(f"创建回测引擎实例失败: {e}")
            raise HTTPException(status_code=500, detail=f"创建回测引擎实例失败: {e}")

        # 执行回测
        try:
            results = backtest_engine.run(trade_logic='full')
            print(f"回测结果: {results}")
            
            # 检查回测数据
            backtest_data = backtest_engine.backtest_data
            print(f"回测数据形状: {backtest_data.shape}")
            print(f"回测数据前5行:\n{backtest_data.head()}")
            print(f"策略收益率统计:\n{backtest_data['策略收益率'].describe()}")
            print(f"策略累计收益率统计:\n{backtest_data['策略累计收益率'].describe()}")
            print(f"总资金统计:\n{backtest_data['总资金'].describe()}")
            
        except Exception as e:
            print(f"执行回测失败: {e}")
            raise HTTPException(status_code=500, detail=f"执行回测失败: {e}")

        # 生成图表
        equity_curve_img = generate_equity_curve(backtest_engine.backtest_data)
        heatmap_img = generate_heatmap(backtest_engine.backtest_data)

        # 构建响应
        response = {
            "metrics": results,
            "charts": {
                "equity_curve": equity_curve_img,
                "heatmap": heatmap_img
            }
        }

        return response

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# 健康检查
@app.get("/api/health")
def health_check():
    return {"status": "ok"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)
