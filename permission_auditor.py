#!/usr/bin/env python3
"""
Permission Auditor - 权限检查器
扫描和审计 OpenClaw Skill 的权限配置

Author: xuzhiwei0217-doctor
Version: 1.0.0
"""

import os
import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# 风险规则配置
RISK_RULES = {
    "high_risk": [
        "file_delete",
        "system_command", 
        "browser_automation",
        "network_request",
        "shell_exec",
        "sudo_access"
    ],
    "medium_risk": [
        "file_write",
        "env_variable_access",
        "clipboard_access",
        "screenshot"
    ],
    "low_risk": [
        "file_read",
        "text_processing",
        "search",
        "calculation"
    ]
}

# 权限说明
PERMISSION_DESCRIPTIONS = {
    "file_delete": "可以删除你的文件",
    "system_command": "可以执行任意系统命令",
    "browser_automation": "可以控制你的浏览器",
    "network_request": "可以发送网络请求（可能泄露数据）",
    "shell_exec": "可以执行 shell 命令",
    "sudo_access": "可以获取管理员权限",
    "file_write": "可以写入文件（可能修改配置）",
    "env_variable_access": "可以访问环境变量（可能包含密钥）",
    "clipboard_access": "可以读取/写入剪贴板",
    "screenshot": "可以截取屏幕",
    "file_read": "只能读取文件",
    "text_processing": "文本处理，无风险",
    "search": "搜索功能，无风险",
    "calculation": "计算功能，无风险"
}


class PermissionAuditor:
    """权限检查器主类"""
    
    def __init__(self, skills_dir: str = None):
        """
        初始化检查器
        
        Args:
            skills_dir: Skill 目录路径，默认 ~/.openclaw/skills/
        """
        if skills_dir is None:
            self.skills_dir = Path.home() / ".openclaw" / "skills"
        else:
            self.skills_dir = Path(skills_dir)
        
        self.results = {
            "scan_time": datetime.now().isoformat(),
            "total_skills": 0,
            "high_risk": [],
            "medium_risk": [],
            "low_risk": [],
            "no_risk": []
        }
    
    def scan_skills(self) -> Dict[str, Any]:
        """
        扫描所有 Skill
        
        Returns:
            扫描结果字典
        """
        print(f"🦞 开始扫描 Skill 目录：{self.skills_dir}")
        
        if not self.skills_dir.exists():
            print(f"❌ Skill 目录不存在：{self.skills_dir}")
            return self.results
        
        # 遍历所有子目录
        skill_dirs = [d for d in self.skills_dir.iterdir() if d.is_dir()]
        self.results["total_skills"] = len(skill_dirs)
        
        print(f"📂 发现 {len(skill_dirs)} 个 Skill")
        
        for skill_dir in skill_dirs:
            self._audit_skill(skill_dir)
        
        return self.results
    
    def _audit_skill(self, skill_dir: Path) -> None:
        """
        审计单个 Skill
        
        Args:
            skill_dir: Skill 目录路径
        """
        skill_file = skill_dir / "SKILL.md"
        
        if not skill_file.exists():
            return
        
        try:
            # 解析 SKILL.md
            with open(skill_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 提取 YAML front matter
            permissions = self._extract_permissions(content)
            
            # 评估风险
            risk_level = self._evaluate_risk(permissions)
            
            # 记录结果
            skill_info = {
                "name": skill_dir.name,
                "path": str(skill_dir),
                "permissions": permissions,
                "risk_level": risk_level
            }
            
            if risk_level == "high":
                self.results["high_risk"].append(skill_info)
            elif risk_level == "medium":
                self.results["medium_risk"].append(skill_info)
            elif risk_level == "low":
                self.results["low_risk"].append(skill_info)
            else:
                self.results["no_risk"].append(skill_info)
                
        except Exception as e:
            print(f"⚠️ 审计 {skill_dir.name} 失败：{e}")
    
    def _extract_permissions(self, content: str) -> List[str]:
        """
        从 SKILL.md 提取权限信息
        
        Args:
            content: SKILL.md 内容
            
        Returns:
            权限列表
        """
        permissions = []
        
        try:
            # 分割 YAML front matter
            if content.startswith('---'):
                parts = content.split('---', 2)
                if len(parts) >= 2:
                    yaml_content = parts[1]
                    # 移除 emoji 等特殊字符（YAML 解析器不支持）
                    yaml_content = ''.join(c for c in yaml_content if ord(c) < 128 or c.isalnum() or c in ' \n\t:-_.,')
                    metadata = yaml.safe_load(yaml_content)
                    
                    # 从 metadata 提取权限
                    if metadata and isinstance(metadata, dict) and 'metadata' in metadata:
                        meta = metadata['metadata']
                        
                        # 检查 requires
                        if meta and isinstance(meta, dict) and 'requires' in meta:
                            requires = meta['requires']
                            if isinstance(requires, dict) and 'bins' in requires:
                                for bin_name in requires['bins']:
                                    if bin_name in ['bash', 'sh', 'python3']:
                                        permissions.append('system_command')
                        
                        # 检查 tags
                        if meta and isinstance(meta, dict) and 'tags' in meta:
                            tags = meta['tags']
                            if isinstance(tags, list):
                                for tag in tags:
                                    if tag == 'browser':
                                        permissions.append('browser_automation')
                                    elif tag == 'network':
                                        permissions.append('network_request')
                                    elif tag == 'security':
                                        permissions.append('env_variable_access')
                    
                    # 检查 triggers
                    if metadata and isinstance(metadata, dict) and 'triggers' in metadata:
                        triggers = metadata['triggers']
                        if isinstance(triggers, list):
                            for trigger in triggers:
                                if isinstance(trigger, str):
                                    if '删除' in trigger or 'delete' in trigger.lower():
                                        permissions.append('file_delete')
                                    if '搜索' in trigger.lower() or 'search' in trigger.lower():
                                        permissions.append('network_request')
        
        except Exception as e:
            # 静默失败，不影响其他 Skill 的扫描
            pass
        
        # 去重
        return list(set(permissions))
    
    def _evaluate_risk(self, permissions: List[str]) -> str:
        """
        评估风险等级
        
        Args:
            permissions: 权限列表
            
        Returns:
            风险等级：high/medium/low/none
        """
        if not permissions:
            return "none"
        
        # 检查高风险
        for perm in permissions:
            if perm in RISK_RULES["high_risk"]:
                return "high"
        
        # 检查中风险
        for perm in permissions:
            if perm in RISK_RULES["medium_risk"]:
                return "medium"
        
        # 检查低风险
        for perm in permissions:
            if perm in RISK_RULES["low_risk"]:
                return "low"
        
        return "none"
    
    def generate_report(self, output_file: str = None) -> str:
        """
        生成审计报告
        
        Args:
            output_file: 输出文件路径（可选）
            
        Returns:
            报告文本
        """
        report = []
        report.append("=" * 60)
        report.append("🦞 权限审计报告")
        report.append("=" * 60)
        report.append(f"扫描时间：{self.results['scan_time']}")
        report.append(f"总 Skill 数：{self.results['total_skills']}")
        report.append("")
        
        # 高风险
        if self.results["high_risk"]:
            report.append("🔴 高风险 Skill:")
            report.append("-" * 40)
            for skill in self.results["high_risk"]:
                report.append(f"  • {skill['name']}")
                report.append(f"    路径：{skill['path']}")
                report.append(f"    权限：{', '.join(skill['permissions'])}")
                report.append(f"    说明：")
                for perm in skill['permissions']:
                    desc = PERMISSION_DESCRIPTIONS.get(perm, "未知权限")
                    report.append(f"      - {perm}: {desc}")
                report.append("")
        
        # 中风险
        if self.results["medium_risk"]:
            report.append("🟡 中风险 Skill:")
            report.append("-" * 40)
            for skill in self.results["medium_risk"]:
                report.append(f"  • {skill['name']}")
                report.append(f"    权限：{', '.join(skill['permissions'])}")
                report.append("")
        
        # 低风险
        if self.results["low_risk"]:
            report.append("🟢 低风险 Skill:")
            report.append("-" * 40)
            for skill in self.results["low_risk"]:
                report.append(f"  • {skill['name']}")
                report.append("")
        
        # 无风险
        if self.results["no_risk"]:
            report.append("✅ 无风险 Skill:")
            report.append("-" * 40)
            report.append(f"  共 {len(self.results['no_risk'])} 个")
            report.append("")
        
        # 建议
        report.append("💡 安全建议:")
        report.append("-" * 40)
        if self.results["high_risk"]:
            report.append("  1. ⚠️ 立即审查所有高风险 Skill")
            report.append("  2. 禁用或删除不信任的 Skill")
            report.append("  3. 定期运行安全审计")
        else:
            report.append("  ✅ 未发现高风险 Skill，继续保持！")
        
        report.append("")
        report.append("=" * 60)
        
        report_text = "\n".join(report)
        
        # 保存到文件
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_text)
            print(f"📄 报告已保存：{output_file}")
        
        return report_text
    
    def print_summary(self) -> None:
        """打印摘要信息"""
        print("")
        print("=" * 60)
        print(f"🔴 高风险：{len(self.results['high_risk'])} 个")
        print(f"🟡 中风险：{len(self.results['medium_risk'])} 个")
        print(f"🟢 低风险：{len(self.results['low_risk'])} 个")
        print(f"✅ 无风险：{len(self.results['no_risk'])} 个")
        print("=" * 60)


def main():
    """主函数"""
    import sys
    
    print("🦞 Permission Auditor v1.0.0")
    print("正在启动权限检查器...")
    print("")
    
    # 支持命令行参数指定目录
    if len(sys.argv) > 1:
        skills_dir = sys.argv[1]
        auditor = PermissionAuditor(skills_dir)
    else:
        auditor = PermissionAuditor()
    
    # 扫描
    results = auditor.scan_skills()
    
    # 打印摘要
    auditor.print_summary()
    
    # 生成报告
    report_file = f"permission_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    report = auditor.generate_report(report_file)
    
    # 打印完整报告
    print("")
    print(report)


if __name__ == "__main__":
    main()
