#!/usr/bin/env python3
"""
SEC API合规性检查工具

检查SEC API使用是否符合官方要求：
- User-Agent设置检查
- 频率限制验证
- 请求头检查
- 错误处理机制验证

使用示例:
    python sec_compliance_checker.py --check-all
    python sec_compliance_checker.py --check-user-agent "Your Name <your@email.com>"
    python sec_compliance_checker.py --test-rate-limit
"""

import argparse
import sys
import os
import time
import re
from typing import Dict, List, Optional, Tuple
import requests

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

from src import SECClient


class SECComplianceChecker:
    """SEC API合规性检查器"""
    
    def __init__(self):
        """初始化检查器"""
        self.test_results = []
        self.compliance_score = 0
        self.total_checks = 0
    
    def check_user_agent_format(self, user_agent: str) -> Tuple[bool, str]:
        """
        检查User-Agent格式是否符合SEC要求
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            (是否符合要求, 检查结果说明)
        """
        print("📧 检查User-Agent格式...")
        
        if not user_agent:
            return False, "❌ User-Agent不能为空"
        
        # 检查长度
        if len(user_agent) < 10:
            return False, "❌ User-Agent过短，应包含有意义的联系信息"
        
        # 检查是否包含邮箱
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        has_email = re.search(email_pattern, user_agent)
        
        if not has_email:
            return False, "❌ User-Agent应包含有效的邮箱地址"
        
        # 检查是否使用了示例邮箱
        example_domains = ['example.com', 'test.com', 'demo.com']
        email_match = has_email.group()
        domain = email_match.split('@')[1]
        
        if domain in example_domains:
            return False, f"⚠️ 建议使用真实邮箱，而不是示例邮箱 ({email_match})"
        
        return True, f"✅ User-Agent格式正确: {user_agent}"
    
    def test_rate_limiting(self, user_agent: str) -> Tuple[bool, str]:
        """
        测试频率限制实现
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            (是否正确实现, 测试结果说明)
        """
        print("⏱️ 测试频率限制实现...")
        
        try:
            client = SECClient(user_agent=user_agent)
            
            # 测试连续请求的时间间隔
            start_time = time.time()
            
            # 模拟两次连续请求（不实际发送）
            client._rate_limit()
            time1 = time.time()
            client._rate_limit()
            time2 = time.time()
            
            # 检查是否有适当的延迟
            delay = time2 - time1
            expected_delay = client.rate_limit_delay
            
            if delay >= expected_delay * 0.9:  # 允许10%的误差
                return True, f"✅ 频率限制正确实现，延迟: {delay:.3f}s (预期: {expected_delay}s)"
            else:
                return False, f"❌ 频率限制可能未正确实现，延迟: {delay:.3f}s (预期: {expected_delay}s)"
                
        except Exception as e:
            return False, f"❌ 频率限制测试失败: {e}"
    
    def check_request_headers(self, user_agent: str) -> Tuple[bool, str]:
        """
        检查HTTP请求头设置
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            (是否正确设置, 检查结果说明)
        """
        print("🌐 检查HTTP请求头设置...")
        
        try:
            client = SECClient(user_agent=user_agent)
            headers = client.session.headers
            
            # 检查必需的头
            required_headers = {
                'User-Agent': user_agent,
                'Host': 'data.sec.gov'
            }
            
            missing_headers = []
            for header, expected_value in required_headers.items():
                if header not in headers:
                    missing_headers.append(header)
                elif header == 'User-Agent' and headers[header] != expected_value:
                    missing_headers.append(f"{header} (值不匹配)")
            
            if missing_headers:
                return False, f"❌ 缺少或错误的请求头: {', '.join(missing_headers)}"
            
            # 检查推荐的头
            if 'Accept-Encoding' in headers:
                encoding_check = "✅ 包含Accept-Encoding"
            else:
                encoding_check = "⚠️ 建议添加Accept-Encoding"
            
            return True, f"✅ 请求头设置正确. {encoding_check}"
            
        except Exception as e:
            return False, f"❌ 请求头检查失败: {e}"
    
    def check_timeout_settings(self, user_agent: str) -> Tuple[bool, str]:
        """
        检查超时设置
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            (是否设置超时, 检查结果说明)
        """
        print("⏰ 检查超时设置...")
        
        try:
            # 检查源代码中是否有超时设置
            with open('src/sec_client.py', 'r', encoding='utf-8') as f:
                content = f.read()
                
            if 'timeout=' in content:
                import re
                timeout_match = re.search(r'timeout=(\d+)', content)
                if timeout_match:
                    timeout_value = int(timeout_match.group(1))
                    if timeout_value >= 10:
                        return True, f"✅ 设置了合理的超时时间: {timeout_value}秒"
                    else:
                        return False, f"❌ 超时时间过短: {timeout_value}秒，建议至少10秒"
                else:
                    return True, "✅ 设置了超时，但无法确定具体值"
            else:
                return False, "❌ 未设置请求超时，可能导致请求挂起"
                
        except Exception as e:
            return False, f"❌ 超时设置检查失败: {e}"
    
    def check_error_handling(self, user_agent: str) -> Tuple[bool, str]:
        """
        检查错误处理机制
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            (是否有适当的错误处理, 检查结果说明)
        """
        print("🛡️ 检查错误处理机制...")
        
        try:
            # 检查源代码中的错误处理
            with open('src/sec_client.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 检查关键的错误处理元素
            error_handling_elements = [
                ('raise_for_status', '检查HTTP状态码'),
                ('except', '异常捕获'),
                ('RequestException', '网络异常处理'),
                ('try:', '错误处理块')
            ]
            
            found_elements = []
            missing_elements = []
            
            for element, description in error_handling_elements:
                if element in content:
                    found_elements.append(description)
                else:
                    missing_elements.append(description)
            
            if len(found_elements) >= 3:  # 至少要有3个关键元素
                return True, f"✅ 错误处理机制完善: {', '.join(found_elements)}"
            else:
                return False, f"❌ 错误处理不够完善，缺少: {', '.join(missing_elements)}"
                
        except Exception as e:
            return False, f"❌ 错误处理检查失败: {e}"
    
    def check_sec_best_practices(self, user_agent: str) -> Tuple[bool, str]:
        """
        检查SEC最佳实践
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            (是否遵循最佳实践, 检查结果说明)
        """
        print("📋 检查SEC最佳实践...")
        
        best_practices = []
        warnings = []
        
        # 检查User-Agent格式
        if '<' in user_agent and '>' in user_agent:
            best_practices.append("User-Agent使用推荐的 '<email>' 格式")
        else:
            warnings.append("建议User-Agent使用 'Name <email>' 格式")
        
        # 检查是否使用官方API端点
        try:
            client = SECClient(user_agent=user_agent)
            if 'data.sec.gov' in client.BASE_URL:
                best_practices.append("使用官方API端点")
            else:
                warnings.append("未使用官方API端点")
        except:
            warnings.append("无法验证API端点")
        
        # 检查文档和注释
        try:
            with open('src/sec_client.py', 'r', encoding='utf-8') as f:
                content = f.read()
            
            if '每秒最多10次请求' in content or '10次/秒' in content:
                best_practices.append("代码中明确说明频率限制")
            else:
                warnings.append("建议在代码中明确说明频率限制")
        except:
            pass
        
        result_msg = f"✅ 遵循的最佳实践: {len(best_practices)} 项"
        if best_practices:
            result_msg += f" ({', '.join(best_practices)})"
        
        if warnings:
            result_msg += f" ⚠️ 建议改进: {', '.join(warnings)}"
        
        return len(warnings) <= 1, result_msg  # 最多允许1个警告
    
    def run_comprehensive_check(self, user_agent: str) -> Dict:
        """
        运行综合合规性检查
        
        Args:
            user_agent: 用户代理字符串
            
        Returns:
            检查结果字典
        """
        print("🔍 开始SEC API合规性检查")
        print("=" * 60)
        
        checks = [
            ("User-Agent格式", self.check_user_agent_format),
            ("频率限制", self.test_rate_limiting),
            ("请求头设置", self.check_request_headers),
            ("超时设置", self.check_timeout_settings),
            ("错误处理", self.check_error_handling),
            ("最佳实践", self.check_sec_best_practices)
        ]
        
        results = {}
        passed_checks = 0
        total_checks = len(checks)
        
        for check_name, check_function in checks:
            try:
                passed, message = check_function(user_agent)
                results[check_name] = {
                    'passed': passed,
                    'message': message
                }
                if passed:
                    passed_checks += 1
                print(f"  {message}")
            except Exception as e:
                results[check_name] = {
                    'passed': False,
                    'message': f"❌ 检查失败: {e}"
                }
                print(f"  ❌ {check_name} 检查失败: {e}")
            print()
        
        # 计算合规性分数
        compliance_score = (passed_checks / total_checks) * 100
        
        print("=" * 60)
        print("📊 合规性检查结果")
        print("=" * 60)
        print(f"通过检查: {passed_checks}/{total_checks}")
        print(f"合规性分数: {compliance_score:.1f}%")
        
        if compliance_score >= 90:
            print("🎉 优秀！完全符合SEC API使用要求")
        elif compliance_score >= 75:
            print("✅ 良好！基本符合SEC API使用要求")
        elif compliance_score >= 50:
            print("⚠️ 一般！需要改进以更好地符合要求")
        else:
            print("❌ 不合格！需要重大改进")
        
        return {
            'results': results,
            'passed_checks': passed_checks,
            'total_checks': total_checks,
            'compliance_score': compliance_score
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="SEC API合规性检查工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  python sec_compliance_checker.py --check-all
  python sec_compliance_checker.py --check-user-agent "Your Name <your@email.com>"
  python sec_compliance_checker.py --test-rate-limit
        """
    )
    
    parser.add_argument('--check-all', action='store_true',
                       help='运行所有合规性检查')
    
    parser.add_argument('--check-user-agent', 
                       help='检查指定的User-Agent格式')
    
    parser.add_argument('--test-rate-limit', action='store_true',
                       help='测试频率限制实现')
    
    parser.add_argument('--user-agent',
                       default="SEC Compliance Test <test@example.com>",
                       help='用于测试的User-Agent字符串')
    
    args = parser.parse_args()
    
    if not any([args.check_all, args.check_user_agent, args.test_rate_limit]):
        parser.print_help()
        return 1
    
    checker = SECComplianceChecker()
    
    try:
        if args.check_all:
            results = checker.run_comprehensive_check(args.user_agent)
            return 0 if results['compliance_score'] >= 75 else 1
        
        elif args.check_user_agent:
            passed, message = checker.check_user_agent_format(args.check_user_agent)
            print(message)
            return 0 if passed else 1
        
        elif args.test_rate_limit:
            passed, message = checker.test_rate_limiting(args.user_agent)
            print(message)
            return 0 if passed else 1
    
    except Exception as e:
        print(f"❌ 检查过程中出错: {e}")
        return 1


if __name__ == "__main__":
    exit(main())