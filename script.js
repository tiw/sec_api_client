// 从苹果2024年10-K真实财务数据中提取的数据
const financialData = {
    // 损益表数据
    revenue: 391.035, // 十亿美元 - 客户合同收入
    costOfRevenue: 210.352, // 成本收入
    grossProfit: 180.683, // 毛利润
    operatingExpenses: 57.467, // 营业费用
    researchDevelopment: 31.370, // 研发费用
    operatingIncome: 123.216, // 营业利润
    nonOperatingIncome: 0.269, // 非营业收益
    pretaxIncome: 123.485, // 税前利润
    incomeTax: 29.749, // 所得税费用
    netIncome: 93.736, // 净利润
    epsBasic: 6.11, // 基本每股收益
    epsDiluted: 6.08, // 稀释每股收益
    sharesOutstandingBasic: 15.344, // 基本加权平均股数（十亿股）
    sharesOutstandingDiluted: 15.408, // 稀释加权平均股数（十亿股）
    
    // 资产负债表数据
    totalAssets: 364.980, // 总资产
    currentAssets: 152.987, // 流动资产
    cashAndEquivalents: 29.943, // 现金及现金等价物
    marketableSecuritiesCurrent: 35.228, // 流动有价证券
    accountsReceivable: 33.410, // 应收账款净额
    inventory: 7.286, // 存货净额
    nonCurrentAssets: 211.993, // 非流动资产
    marketableSecuritiesNonCurrent: 91.479, // 非流动有价证券
    propertyPlantEquipment: 45.680, // 固定资产净额
    otherNonCurrentAssets: 74.834, // 其他非流动资产
    
    totalLiabilities: 308.030, // 总负债
    currentLiabilities: 176.392, // 流动负债
    accountsPayable: 68.960, // 应付账款
    commercialPaper: 9.967, // 商业票据
    longTermDebtCurrent: 10.912, // 一年内到期的长期债务
    nonCurrentLiabilities: 131.638, // 非流动负债
    longTermDebt: 85.750, // 长期债务
    otherNonCurrentLiabilities: 45.888, // 其他非流动负债
    
    stockholdersEquity: 56.950, // 股东权益
    commonStockShares: 15.117, // 发行的普通股股数（十亿股）
    retainedEarnings: -19.154, // 留存收益
    accumulatedOCI: -7.172, // 其他综合收益累计额
    
    // 现金流量表数据
    operatingCashFlow: 118.254, // 经营活动现金流
    investingCashFlow: 2.935, // 投资活动现金流
    financingCashFlow: -121.983, // 融资活动现金流
    netCashChange: -0.794, // 现金及现金等价物净增加
    depreciation: 11.445, // 折旧摊销
    shareBasedCompensation: 11.688, // 股权激励费用
    capex: 9.447, // 购建固定资产支出
    dividendsPaid: 15.234, // 支付股息
    shareRepurchase: 94.949 // 回购股票支出
};

// 模拟历史股价数据（基于图片趋势）
const stockPriceData = {
    labels: ['2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024'],
    prices: [20, 25, 27, 30, 45, 55, 75, 130, 150, 140, 180, 227.48],
    volumes: [60, 65, 70, 75, 80, 85, 90, 95, 85, 80, 75, 70] // 模拟成交量百分比
};

// 计算财务指标
function calculateMetrics() {
    const currentPrice = 227.48; // 当前股价
    
    const metrics = {
        // 每股指标 (使用基本股数)
        salesPerShare: (financialData.revenue * 1000 / financialData.sharesOutstandingBasic).toFixed(2),
        cashFlowPerShare: (financialData.operatingCashFlow * 1000 / financialData.sharesOutstandingBasic).toFixed(2),
        eps: financialData.epsDiluted.toFixed(2),
        dividendsPerShare: (financialData.dividendsPaid * 1000 / financialData.sharesOutstandingBasic).toFixed(2),
        capexPerShare: (financialData.capex * 1000 / financialData.sharesOutstandingBasic).toFixed(2),
        bookValuePerShare: (financialData.stockholdersEquity * 1000 / financialData.commonStockShares).toFixed(2),
        
        // 估值指标
        peRatio: (currentPrice / financialData.epsDiluted).toFixed(1),
        relativePE: '1.15', // 相对市场PE比率（估算）
        dividendYield: ((financialData.dividendsPaid * 1000 / financialData.sharesOutstandingBasic) / currentPrice * 100).toFixed(2) + '%',
        
        // 盈利能力指标
        grossMargin: (financialData.grossProfit / financialData.revenue * 100).toFixed(1) + '%',
        operatingMargin: (financialData.operatingIncome / financialData.revenue * 100).toFixed(1) + '%',
        netProfitMargin: (financialData.netIncome / financialData.revenue * 100).toFixed(1) + '%',
        
        // 财务健康度
        workingCapital: (financialData.currentAssets - financialData.currentLiabilities).toFixed(1),
        totalDebt: (financialData.longTermDebt + financialData.longTermDebtCurrent).toFixed(1),
        debtToEquity: ((financialData.longTermDebt + financialData.longTermDebtCurrent) / financialData.stockholdersEquity).toFixed(2),
        
        // 回报率 (使用税后营业利润计算ROTC)
        roe: (financialData.netIncome / financialData.stockholdersEquity * 100).toFixed(1) + '%',
        rotc: ((financialData.operatingIncome * (1 - financialData.incomeTax / financialData.pretaxIncome)) / 
               (financialData.stockholdersEquity + financialData.longTermDebt + financialData.longTermDebtCurrent) * 100).toFixed(1) + '%',
        
        // 税务和分配指标
        taxRate: (financialData.incomeTax / financialData.pretaxIncome * 100).toFixed(1) + '%',
        dividendPayoutRatio: (financialData.dividendsPaid / financialData.netIncome * 100).toFixed(1) + '%',
        retentionRatio: ((financialData.netIncome - financialData.dividendsPaid) / financialData.netIncome * 100).toFixed(1) + '%'
    };
    
    return metrics;
}

// 更新页面数据
function updateFinancialMetrics() {
    const metrics = calculateMetrics();
    
    // 更新股东价值变化指标
    document.getElementById('sales-per-sh').textContent = '$' + metrics.salesPerShare;
    document.getElementById('cash-flow-per-sh').textContent = '$' + metrics.cashFlowPerShare;
    document.getElementById('eps').textContent = '$' + metrics.eps;
    document.getElementById('dividends-per-sh').textContent = '$' + metrics.dividendsPerShare;
    document.getElementById('capex-per-sh').textContent = '$' + metrics.capexPerShare;
    document.getElementById('book-value-per-sh').textContent = '$' + metrics.bookValuePerShare;
    document.getElementById('shares-outstanding').textContent = financialData.commonStockShares.toFixed(2) + 'B';
    
    // 更新估值水平
    document.getElementById('avg-pe').textContent = metrics.peRatio;
    document.getElementById('relative-pe').textContent = metrics.relativePE;
    document.getElementById('avg-dividend-yield').textContent = metrics.dividendYield;
    
    // 更新营收水平
    document.getElementById('sales-revenue').textContent = '$' + financialData.revenue.toFixed(2) + 'B';
    document.getElementById('operating-margin').textContent = metrics.operatingMargin;
    
    // 更新现金流
    document.getElementById('depreciation').textContent = '$' + financialData.depreciation.toFixed(2) + 'B';
    document.getElementById('net-profit').textContent = '$' + financialData.netIncome.toFixed(2) + 'B';
    
    // 更新净利润率
    document.getElementById('tax-rate').textContent = metrics.taxRate;
    document.getElementById('net-profit-margin').textContent = metrics.netProfitMargin;
    
    // 更新资本安全性
    document.getElementById('working-capital').textContent = '$' + metrics.workingCapital + 'B';
    document.getElementById('lt-debt').textContent = '$' + metrics.totalDebt + 'B';
    document.getElementById('shareholders-equity').textContent = '$' + financialData.stockholdersEquity.toFixed(2) + 'B';
    
    // 更新资本回报率
    document.getElementById('rotc').textContent = metrics.rotc;
    document.getElementById('roe').textContent = metrics.roe;
    
    // 更新资本分配
    document.getElementById('retained-earnings').textContent = metrics.retentionRatio;
    document.getElementById('dividend-payout').textContent = metrics.dividendPayoutRatio;
}

// 创建股价图表
function createStockChart() {
    const ctx = document.getElementById('stockChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: stockPriceData.labels,
            datasets: [{
                label: '股价 ($)',
                data: stockPriceData.prices,
                borderColor: '#333',
                backgroundColor: 'rgba(51, 51, 51, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.1,
                pointBackgroundColor: '#333',
                pointBorderColor: '#333',
                pointRadius: 3
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    },
                    ticks: {
                        font: {
                            size: 10
                        }
                    }
                },
                y: {
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    },
                    ticks: {
                        font: {
                            size: 10
                        },
                        callback: function(value) {
                            return '$' + value;
                        }
                    }
                }
            },
            elements: {
                point: {
                    hoverRadius: 6
                }
            }
        }
    });
}

// 创建成交量图表
function createVolumeChart() {
    const ctx = document.getElementById('volumeChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'bar',
        data: {
            labels: stockPriceData.labels,
            datasets: [{
                label: '成交量 (%)',
                data: stockPriceData.volumes,
                backgroundColor: 'rgba(102, 102, 102, 0.6)',
                borderColor: '#666',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        display: false
                    },
                    ticks: {
                        display: false
                    }
                },
                y: {
                    grid: {
                        display: true,
                        color: '#e0e0e0'
                    },
                    ticks: {
                        font: {
                            size: 9
                        },
                        max: 100,
                        min: 0
                    }
                }
            }
        }
    });
}

// 添加数值颜色标识
function addValueColorCoding() {
    const positiveElements = document.querySelectorAll('[id$="-margin"], [id$="-roe"], [id$="-rotc"]');
    const negativeElements = document.querySelectorAll('[id$="-debt"]');
    
    positiveElements.forEach(el => {
        if (el.textContent && parseFloat(el.textContent) > 0) {
            el.classList.add('positive');
        }
    });
    
    negativeElements.forEach(el => {
        if (el.textContent && el.textContent.includes('B')) {
            el.classList.add('neutral');
        }
    });
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', function() {
    // 更新财务指标
    updateFinancialMetrics();
    
    // 创建图表
    createStockChart();
    createVolumeChart();
    
    // 添加颜色编码
    setTimeout(addValueColorCoding, 100);
    
    console.log('苹果公司基本面投资分析页面已加载完成');
});

// 格式化数字显示
function formatNumber(num, decimals = 2) {
    if (num >= 1000000000) {
        return (num / 1000000000).toFixed(decimals) + 'B';
    } else if (num >= 1000000) {
        return (num / 1000000).toFixed(decimals) + 'M';
    } else if (num >= 1000) {
        return (num / 1000).toFixed(decimals) + 'K';
    }
    return num.toFixed(decimals);
}

// 响应式图表调整
window.addEventListener('resize', function() {
    // Chart.js 会自动处理响应式调整
});