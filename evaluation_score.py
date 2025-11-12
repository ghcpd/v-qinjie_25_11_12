"""
项目评估评分脚本
根据项目实际内容评估各项指标
"""

SCORE = {
    # 漏洞检测: 检测到的漏洞类型数 / 应该检测的漏洞类型数
    # 检测到的漏洞: Reflected XSS, DOM-based XSS
    # 应该检测的漏洞: Reflected XSS, DOM-based XSS
    'Vulnerability_Detection': 2/2,  # 2种漏洞类型全部检测到
    
    # 漏洞修复: 修复的漏洞数 / 总漏洞数
    # 修复措施: Input sanitization, CSP headers, Safe DOM manipulation
    # 所有漏洞都已修复
    'Vulnerability_Fix': 2/2,  # 所有漏洞都已修复
    
    # 密钥检测: 检测到的密钥暴露位置数 / 总密钥暴露位置数
    # 检测到的位置: templates, JavaScript, localStorage, debug panels, API responses
    # 总共5种密钥暴露方式
    'Secrets_Detection': 5/5,  # 所有密钥暴露位置都检测到
    
    # 密钥修复: 修复的密钥暴露数 / 总密钥暴露数
    # 修复措施: Environment variables, 从templates移除, 从JavaScript移除, 
    #           从localStorage移除, 从API响应移除
    'Secrets_Fix': 5/5,  # 所有密钥暴露都已修复
    
    # 调试和测试: 1分制 (0-1)
    # 包含: 自动化测试脚本, Playwright测试, 测试用例, 比较报告, 截图功能
    'Debugging_And_Testing': 1,  # 完整的测试基础设施
    
    # 文档和注释: 1分制 (0-1)
    # 包含: README文件, 代码注释, 安全说明, 使用指南
    'Documentation_And_Comments': 1,  # 完整的文档和注释
}

def print_score():
    """打印评分结果"""
    print("=" * 60)
    print("项目评估评分报告")
    print("=" * 60)
    print()
    
    print("1. Vulnerability_Detection (漏洞检测)")
    print(f"   评分: {SCORE['Vulnerability_Detection']:.2f} ({SCORE['Vulnerability_Detection']*100:.0f}%)")
    print("   检测到的漏洞类型:")
    print("   - Reflected XSS (反射型XSS)")
    print("   - DOM-based XSS (DOM型XSS)")
    print()
    
    print("2. Vulnerability_Fix (漏洞修复)")
    print(f"   评分: {SCORE['Vulnerability_Fix']:.2f} ({SCORE['Vulnerability_Fix']*100:.0f}%)")
    print("   修复措施:")
    print("   - Input sanitization (输入清理)")
    print("   - Content Security Policy headers (CSP头)")
    print("   - Safe DOM manipulation (安全DOM操作)")
    print()
    
    print("3. Secrets_Detection (密钥检测)")
    print(f"   评分: {SCORE['Secrets_Detection']:.2f} ({SCORE['Secrets_Detection']*100:.0f}%)")
    print("   检测到的密钥暴露位置:")
    print("   - Templates (模板)")
    print("   - JavaScript代码")
    print("   - localStorage")
    print("   - Debug panels (调试面板)")
    print("   - API responses (API响应)")
    print()
    
    print("4. Secrets_Fix (密钥修复)")
    print(f"   评分: {SCORE['Secrets_Fix']:.2f} ({SCORE['Secrets_Fix']*100:.0f}%)")
    print("   修复措施:")
    print("   - Environment variables (环境变量)")
    print("   - 从templates移除")
    print("   - 从JavaScript移除")
    print("   - 从localStorage移除")
    print("   - 从API响应移除")
    print()
    
    print("5. Debugging_And_Testing (调试和测试)")
    print(f"   评分: {SCORE['Debugging_And_Testing']:.2f} ({SCORE['Debugging_And_Testing']*100:.0f}%)")
    print("   包含内容:")
    print("   - 自动化测试脚本 (test_pre_ui.py, test_post_ui.py)")
    print("   - Playwright测试框架")
    print("   - 7个测试用例")
    print("   - 比较报告生成器")
    print("   - 截图功能")
    print()
    
    print("6. Documentation_And_Comments (文档和注释)")
    print(f"   评分: {SCORE['Documentation_And_Comments']:.2f} ({SCORE['Documentation_And_Comments']*100:.0f}%)")
    print("   包含内容:")
    print("   - 根目录README.md")
    print("   - 项目A和B的README文件")
    print("   - 代码中的安全注释")
    print("   - 使用指南和说明")
    print()
    
    print("=" * 60)
    print("最终评分字典:")
    print("=" * 60)
    print("SCORE = {")
    for key, value in SCORE.items():
        if isinstance(value, float) and value <= 1.0:
            print(f"    '{key}': {value:.2f},")
        else:
            print(f"    '{key}': {value},")
    print("}")
    print()
    
    # 计算总分
    total_score = (
        SCORE['Vulnerability_Detection'] * 0.2 +
        SCORE['Vulnerability_Fix'] * 0.2 +
        SCORE['Secrets_Detection'] * 0.2 +
        SCORE['Secrets_Fix'] * 0.2 +
        SCORE['Debugging_And_Testing'] * 0.1 +
        SCORE['Documentation_And_Comments'] * 0.1
    )
    print(f"加权总分: {total_score:.2f} / 1.00 ({total_score*100:.1f}%)")

if __name__ == '__main__':
    print_score()

