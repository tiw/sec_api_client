#!/usr/bin/env python3
"""
SEC API客户端测试用例

测试主要功能模块的基本功能
"""

import unittest
import sys
import os
from unittest.mock import Mock, patch, MagicMock
import pandas as pd

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src import SECClient, DocumentRetriever, XBRLFramesClient, FinancialAnalyzer


class TestSECClient(unittest.TestCase):
    """测试SEC客户端基础功能"""
    
    def setUp(self):
        """测试前准备"""
        self.client = SECClient(user_agent="test@example.com")
    
    def test_initialization(self):
        """测试客户端初始化"""
        self.assertIsNotNone(self.client)
        self.assertEqual(self.client.session.headers['User-Agent'], "test@example.com")
    
    def test_user_agent_required(self):
        """测试User-Agent是必需的"""
        with self.assertRaises(ValueError):
            SECClient()
    
    @patch('requests.Session.get')
    def test_rate_limiting(self, mock_get):
        """测试API频率限制"""
        mock_response = Mock()
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        # 连续调用应该有延迟
        import time
        start_time = time.time()
        self.client._make_request("http://test.com")
        self.client._make_request("http://test.com")
        end_time = time.time()
        
        # 验证有适当的延迟
        self.assertGreaterEqual(end_time - start_time, self.client.rate_limit_delay)
    
    @patch('requests.Session.get')
    def test_search_company_by_ticker(self, mock_get):
        """测试按股票代码搜索公司"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            "0": {"cik_str": 320193, "ticker": "AAPL", "title": "Apple Inc."}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        result = self.client.search_company_by_ticker('AAPL')
        
        self.assertIsNotNone(result)
        self.assertEqual(result['ticker'], 'AAPL')
        self.assertEqual(result['title'], 'Apple Inc.')
        self.assertEqual(result['cik'], '0000320193')
    
    def test_search_nonexistent_ticker(self):
        """测试搜索不存在的股票代码"""
        with patch.object(self.client, 'get_company_tickers', return_value={}):
            result = self.client.search_company_by_ticker('NONEXISTENT')
            self.assertIsNone(result)


class TestDocumentRetriever(unittest.TestCase):
    """测试文档获取器"""
    
    def setUp(self):
        """测试前准备"""
        self.sec_client = SECClient(user_agent="test@example.com")
        self.retriever = DocumentRetriever(self.sec_client)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.retriever)
        self.assertEqual(self.retriever.client, self.sec_client)
    
    @patch.object(SECClient, 'search_company_by_ticker')
    @patch.object(SECClient, 'get_recent_filings')
    def test_get_10k_10q_filings(self, mock_get_filings, mock_search):
        """测试获取10-K和10-Q文档"""
        # 模拟搜索结果
        mock_search.return_value = {
            'cik': '0000320193',
            'ticker': 'AAPL', 
            'title': 'Apple Inc.'
        }
        
        # 模拟文档数据
        mock_filings_data = pd.DataFrame({
            'accessionNumber': ['0000320193-23-000064'],
            'filingDate': ['2023-05-05'],
            'reportDate': ['2023-04-01'], 
            'form': ['10-Q'],
            'isXBRL': [1]
        })
        mock_filings_data['filingDate'] = pd.to_datetime(mock_filings_data['filingDate'])
        mock_filings_data['reportDate'] = pd.to_datetime(mock_filings_data['reportDate'])
        
        mock_get_filings.return_value = mock_filings_data
        
        result = self.retriever.get_10k_10q_filings('AAPL', years=1)
        
        self.assertFalse(result.empty)
        self.assertIn('ticker', result.columns)
        self.assertIn('company_name', result.columns)
        self.assertEqual(result.iloc[0]['ticker'], 'AAPL')


class TestXBRLFramesClient(unittest.TestCase):
    """测试XBRL/Frames客户端"""
    
    def setUp(self):
        """测试前准备"""
        self.sec_client = SECClient(user_agent="test@example.com")
        self.xbrl_client = XBRLFramesClient(self.sec_client)
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.xbrl_client)
        self.assertEqual(self.xbrl_client.client, self.sec_client)
    
    def test_build_frames_url(self):
        """测试构建Frames URL"""
        url = self.xbrl_client._build_frames_url(
            'us-gaap', 'Assets', 'USD', 'CY2023Q1I'
        )
        expected_url = "https://data.sec.gov/api/xbrl/frames/us-gaap/Assets/USD/CY2023Q1I.json"
        self.assertEqual(url, expected_url)
    
    def test_build_period_string(self):
        """测试构建期间字符串"""
        # 年度数据
        annual = self.xbrl_client.build_period_string(2023)
        self.assertEqual(annual, "CY2023")
        
        # 季度数据
        quarterly = self.xbrl_client.build_period_string(2023, 1)
        self.assertEqual(quarterly, "CY2023Q1")
        
        # 瞬时数据
        instant = self.xbrl_client.build_period_string(2023, 1, True)
        self.assertEqual(instant, "CY2023Q1I")
        
        # 无效季度
        with self.assertRaises(ValueError):
            self.xbrl_client.build_period_string(2023, 5)
    
    @patch.object(SECClient, '_make_request')
    def test_get_concept_data(self, mock_request):
        """测试获取概念数据"""
        # 模拟API响应
        mock_response = Mock()
        mock_response.json.return_value = {
            'taxonomy': 'us-gaap',
            'tag': 'Assets',
            'label': 'Assets',
            'description': 'Total Assets',
            'data': [
                {'entityName': 'APPLE INC', 'cik': 320193, 'val': 352755000000, 'end': '2023-03-31'},
                {'entityName': 'MICROSOFT CORP', 'cik': 789019, 'val': 411976000000, 'end': '2023-03-31'}
            ]
        }
        mock_request.return_value = mock_response
        
        result = self.xbrl_client.get_concept_data('Assets', 'CY2023Q1I')
        
        self.assertFalse(result.empty)
        self.assertIn('entityName', result.columns)
        self.assertIn('val', result.columns)
        self.assertEqual(len(result), 2)


class TestFinancialAnalyzer(unittest.TestCase):
    """测试财务分析器"""
    
    def setUp(self):
        """测试前准备"""
        self.analyzer = FinancialAnalyzer()
        
        # 创建测试数据
        self.test_data = pd.DataFrame({
            'ticker': ['AAPL', 'AAPL', 'AAPL', 'AAPL'],
            'concept': ['Assets', 'Liabilities', 'StockholdersEquity', 'Revenues'],
            'value': [400000, 200000, 200000, 100000],
            'end_date': pd.to_datetime(['2023-03-31'] * 4),
            'fiscal_year': [2023] * 4,
            'fiscal_period': ['Q2'] * 4
        })
    
    def test_initialization(self):
        """测试初始化"""
        self.assertIsNotNone(self.analyzer)
    
    def test_calculate_financial_ratios(self):
        """测试计算财务比率"""
        ratios = self.analyzer.calculate_financial_ratios(self.test_data)
        
        self.assertFalse(ratios.empty)
        self.assertIn('debt_to_assets', ratios.columns)
        self.assertIn('equity_ratio', ratios.columns)
        
        # 验证计算结果
        ratio_row = ratios.iloc[0]
        self.assertAlmostEqual(ratio_row['debt_to_assets'], 0.5, places=2)  # 200000/400000
        self.assertAlmostEqual(ratio_row['equity_ratio'], 0.5, places=2)     # 200000/400000
    
    def test_format_financial_number(self):
        """测试财务数字格式化"""
        # 测试自动缩放
        result_b = self.analyzer.format_financial_number(1500000000)  # 1.5B
        self.assertIn('B', result_b)
        self.assertIn('1.50', result_b)
        
        result_m = self.analyzer.format_financial_number(1500000)     # 1.5M
        self.assertIn('M', result_m)
        self.assertIn('1.50', result_m)
        
        result_k = self.analyzer.format_financial_number(1500)        # 1.5K
        self.assertIn('K', result_k)
        self.assertIn('1.50', result_k)
        
        # 测试NaN值
        result_nan = self.analyzer.format_financial_number(float('nan'))
        self.assertEqual(result_nan, 'N/A')
    
    def test_trend_analysis(self):
        """测试趋势分析"""
        # 创建时间序列数据
        trend_data = pd.DataFrame({
            'ticker': ['AAPL'] * 4,
            'concept': ['Revenues'] * 4,
            'value': [100000, 110000, 120000, 130000],  # 递增趋势
            'end_date': pd.to_datetime(['2022-03-31', '2022-06-30', '2022-09-30', '2022-12-31'])
        })
        
        trends = self.analyzer.trend_analysis(trend_data, ['Revenues'])
        
        self.assertIn('Revenues', trends)
        revenue_trend = trends['Revenues']
        self.assertEqual(revenue_trend['data_points'], 4)
        self.assertGreater(revenue_trend['overall_change_pct'], 0)  # 正增长
    
    def test_peer_comparison(self):
        """测试同行对比"""
        # 创建多公司数据
        companies_data = {
            'AAPL': pd.DataFrame({
                'concept': ['Revenues'],
                'value': [100000],
                'end_date': pd.to_datetime(['2023-03-31'])
            }),
            'MSFT': pd.DataFrame({
                'concept': ['Revenues'], 
                'value': [120000],
                'end_date': pd.to_datetime(['2023-03-31'])
            })
        }
        
        comparison = self.analyzer.peer_comparison(companies_data, 'Revenues')
        
        self.assertFalse(comparison.empty)
        self.assertEqual(len(comparison), 2)
        self.assertIn('rank', comparison.columns)
        self.assertIn('vs_average_pct', comparison.columns)
        
        # 验证排名（MSFT应该排名第一，因为收入更高）
        msft_row = comparison[comparison['ticker'] == 'MSFT'].iloc[0]
        self.assertEqual(msft_row['rank'], 1)


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def setUp(self):
        """测试前准备"""
        self.sec_client = SECClient(user_agent="integration_test@example.com")
    
    def test_full_workflow_mock(self):
        """测试完整工作流程（模拟数据）"""
        # 这个测试使用模拟数据验证整个工作流程
        
        # 1. 搜索公司
        with patch.object(self.sec_client, 'search_company_by_ticker') as mock_search:
            mock_search.return_value = {
                'cik': '0000320193',
                'ticker': 'AAPL',
                'title': 'Apple Inc.'
            }
            
            company = self.sec_client.search_company_by_ticker('AAPL')
            self.assertIsNotNone(company)
        
        # 2. 获取XBRL数据
        xbrl_client = XBRLFramesClient(self.sec_client)
        
        with patch.object(xbrl_client, 'get_financial_metrics') as mock_metrics:
            mock_data = pd.DataFrame({
                'ticker': ['AAPL'] * 3,
                'concept': ['Assets', 'Liabilities', 'Revenues'],
                'value': [400000, 200000, 100000],
                'end_date': pd.to_datetime(['2023-03-31'] * 3)
            })
            mock_metrics.return_value = mock_data
            
            metrics = xbrl_client.get_financial_metrics('AAPL')
            self.assertFalse(metrics.empty)
        
        # 3. 财务分析
        analyzer = FinancialAnalyzer()
        ratios = analyzer.calculate_financial_ratios(mock_data)
        self.assertFalse(ratios.empty)
        
        print("✅ 集成测试通过：完整工作流程正常")


if __name__ == '__main__':
    # 运行测试
    print("🧪 开始运行SEC API客户端测试...")
    print("=" * 50)
    
    # 创建测试套件
    test_suite = unittest.TestSuite()
    
    # 添加测试类
    test_classes = [
        TestSECClient,
        TestDocumentRetriever, 
        TestXBRLFramesClient,
        TestFinancialAnalyzer,
        TestIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # 测试结果总结
    print("\n" + "=" * 50)
    if result.wasSuccessful():
        print("🎉 所有测试通过！")
    else:
        print(f"❌ 测试失败: {len(result.failures)} 个失败, {len(result.errors)} 个错误")
        
    print(f"📊 测试统计: 运行 {result.testsRun} 个测试")
    print("🏁 测试完成")