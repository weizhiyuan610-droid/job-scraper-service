"""
批量计算现有职位的分数

从 Supabase 读取所有职位，使用 job_scorer 计算分数，然后更新回数据库
"""
import os
import sys
from datetime import datetime
from typing import Dict, List

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.job_scorer import JobScorer
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


# Supabase 配置（从环境变量读取）
SUPABASE_URL = os.getenv('NEXT_PUBLIC_SUPABASE_URL', 'https://zqxmsinbpkkqsggqukrv.supabase.co')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

if not SUPABASE_KEY:
    print("错误: SUPABASE_SERVICE_ROLE_KEY 环境变量未设置")
    sys.exit(1)


def fetch_jobs_from_supabase(limit: int = 1000, offset: int = 0) -> List[Dict]:
    """从 Supabase 获取职位数据"""
    try:
        import requests
    except ImportError:
        print("错误: 需要安装 requests 库")
        print("运行: pip install requests")
        sys.exit(1)

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

    # 获取职位
    params = {
        'select': '*',
        'limit': limit,
        'offset': offset
    }

    response = requests.get(
        f'{SUPABASE_URL}/rest/v1/jobs',
        headers=headers,
        params=params
    )

    if response.status_code != 200:
        print(f"错误: 获取职位失败 ({response.status_code})")
        print(response.text)
        return []

    return response.json()


def update_job_scores(job_id: str, scores: Dict) -> bool:
    """更新单个职位的分数"""
    try:
        import requests
    except ImportError:
        print("错误: 需要安装 requests 库")
        return False

    headers = {
        'apikey': SUPABASE_KEY,
        'Authorization': f'Bearer {SUPABASE_KEY}',
        'Content-Type': 'application/json'
    }

    # 只更新分数字段
    update_data = {
        'priority_score': scores.get('priority_score'),
        'urgency_score': scores.get('urgency_score'),
        'freshness_score': scores.get('freshness_score'),
        'quality_score': scores.get('quality_score'),
        'matchability_score': scores.get('matchability_score'),
        'scores_calculated_at': datetime.now().isoformat()
    }

    response = requests.patch(
        f'{SUPABASE_URL}/rest/v1/jobs?id=eq.{job_id}',
        headers=headers,
        json=update_data
    )

    return response.status_code in (200, 204)


def supabase_job_to_scorer_format(job: Dict) -> Dict:
    """将 Supabase 职位格式转换为 scorer 需要的格式"""
    return {
        'id': job.get('id'),
        'company': job.get('company_name') or job.get('company', ''),
        'title': job.get('job_title') or job.get('title', ''),
        'location': job.get('location_city') or '',
        'industry': job.get('company_industry') or '',
        'apply_link': job.get('application_url') or '',
        'deadline': job.get('application_deadline') or '',
        'opened': job.get('posted_date') or job.get('created_at') or '',
        'visa_mentioned': determine_visa_status(job),
        'visa_sponsorship': job.get('visa_sponsorship', False),
        'salary': job.get('salary') or '',
        'description': job.get('job_description') or '',
        'degree_min': '',  # 从现有数据无法获取
        'target_year': '',
        'skills_tags': job.get('job_skills') or [],
        'preferred_major': [],
        'company_info': {
            'tier': 'Unknown'  # 默认未知，后续可从 company_visa_history 获取
        }
    }


def determine_visa_status(job: Dict) -> str:
    """根据现有字段判断签证状态"""
    # 如果有明确的签证担保字段
    if job.get('visa_sponsorship'):
        return 'explicit_yes'

    # 可以从其他字段推断，这里简化处理
    return 'not_mentioned'


def batch_calculate_scores():
    """批量计算并更新职位分数"""
    logger.info("=" * 60)
    logger.info("批量计算职位分数")
    logger.info("=" * 60)

    # 1. 获取所有职位
    logger.info("\n[1/4] 从 Supabase 获取职位...")
    jobs = fetch_jobs_from_supabase()
    logger.info(f"获取到 {len(jobs)} 个职位")

    if not jobs:
        logger.error("没有找到职位，退出")
        return

    # 2. 初始化评分器
    logger.info("\n[2/4] 初始化评分器（含签证历史数据库）...")
    scorer = JobScorer()

    # 3. 计算分数
    logger.info("\n[3/4] 计算分数...")
    results = {
        'success': 0,
        'failed': 0,
        'skipped': 0
    }

    for i, job in enumerate(jobs):
        job_id = job.get('id')
        company_name = job.get('company_name', 'Unknown')

        # 跳过已有分数的
        if job.get('priority_score') is not None:
            results['skipped'] += 1
            continue

        # 转换格式
        job_data = supabase_job_to_scorer_format(job)

        # 计算分数
        try:
            scores = scorer.calculate_all_scores(job_data)

            # 更新到数据库
            if update_job_scores(job_id, scores):
                results['success'] += 1
                if (i + 1) % 20 == 0:
                    logger.info(f"  进度: {i + 1}/{len(jobs)} - 成功: {results['success']}")
            else:
                results['failed'] += 1
                logger.warning(f"  更新失败: {company_name}")
        except Exception as e:
            results['failed'] += 1
            logger.warning(f"  计算失败: {company_name} - {e}")

    # 4. 总结
    logger.info("\n" + "=" * 60)
    logger.info("[4/4] 完成！")
    logger.info("=" * 60)
    logger.info(f"成功: {results['success']}")
    logger.info(f"失败: {results['failed']}")
    logger.info(f"跳过: {results['skipped']}")
    logger.info("\n现在可以用以下查询验证:")
    logger.info('  SELECT company_name, job_title, priority_score, urgency_score')
    logger.info('  FROM jobs_with_scores')
    logger.info('  ORDER BY priority_score DESC')
    logger.info('  LIMIT 10;')


if __name__ == '__main__':
    batch_calculate_scores()
