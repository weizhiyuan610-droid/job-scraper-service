"""
Job Scoring Algorithm - Pre-compute scores during scraping
避免实时AI调用，在爬取时计算并存储分数
"""
from datetime import datetime
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)


class JobScorer:
    """
    职位评分器 - 在爬取时预计算多个维度的分数
    所有分数都是基于客观属性，不需要AI实时计算

    Enhancement: 现在集成了公司签证历史数据库，用于更准确的签证赞助预测
    """

    def __init__(self, visa_history_db=None):
        # 评分权重配置
        self.weights = {
            'deadline_urgent': 30,        # 30分：截止日期（越近分数越高）
            'visa_sponsorship': 20,       # 20分：签证担保
            'company_tier': 25,           # 25分：公司层级
            'data_completeness': 15,      # 15分：数据完整度
            'salary_info': 10,            # 10分：薪资信息
        }

        # 延迟加载签证历史数据库（避免循环导入）
        self._visa_db = visa_history_db

    @property
    def visa_db(self):
        """延迟加载签证历史数据库"""
        if self._visa_db is None:
            try:
                from scraper.visa_history_manager import get_visa_history_db
                self._visa_db = get_visa_history_db()
            except ImportError:
                logger.warning("Unable to import visa_history_manager, visa scoring will use JD text only")
                self._visa_db = False  # 标记为加载失败
        return self._visa_db if self._visa_db is not False else None

    def calculate_all_scores(self, job_data: Dict) -> Dict[str, float]:
        """
        计算所有分数并返回

        Args:
            job_data: 从AI提取的职位数据

        Returns:
            包含所有分数的字典
        """
        return {
            'priority_score': self.calculate_priority_score(job_data),
            'urgency_score': self.calculate_urgency_score(job_data),
            'freshness_score': self.calculate_freshness_score(job_data),
            'quality_score': self.calculate_quality_score(job_data),
            'matchability_score': self.calculate_matchability_score(job_data),
        }

    def calculate_priority_score(self, job_data: Dict) -> float:
        """
        计算优先级分数 (0-100)
        用于职位列表排序：高分 = 高优先级展示

        因素：
        - deadline_urgent (30%): 截止日期越近分数越高
        - visa_sponsorship (20%): 是否提供签证担保
        - company_tier (25%): 公司层级（Tier 1 > Tier 2 > Tier 3）
        - data_completeness (15%): 数据完整度
        - salary_info (10%): 是否有薪资信息
        """
        score = 0.0

        # 1. Deadline 评分 (30分)
        score += self._score_deadline(job_data.get('deadline', ''), weight=30)

        # 2. 签证担保评分 (20分)
        # 优先使用历史数据库数据，其次使用 JD 文本分析
        score += self._score_visa_sponsorship(job_data, weight=20)

        # 3. 公司层级评分 (25分)
        # 优先从历史数据库获取公司层级，其次使用 AI 提取的数据
        score += self._score_company_tier(job_data, weight=25)

        # 4. 数据完整度评分 (15分)
        required_fields = ['company', 'title', 'location', 'industry', 'apply_link', 'description']
        filled_fields = sum(1 for field in required_fields if job_data.get(field))
        completeness_ratio = filled_fields / len(required_fields)
        score += completeness_ratio * 15

        # 5. 薪资信息评分 (10分)
        if job_data.get('salary') and job_data.get('salary') not in ['', 'Not specified', 'Competitive']:
            score += 10
        elif job_data.get('salary_range_normalized'):
            score += 8

        return round(min(100, max(0, score)), 2)

    def calculate_urgency_score(self, job_data: Dict) -> float:
        """
        计算紧急程度分数 (0-100)
        用于标记即将关闭的职位

        分数含义：
        - 80-100: 非常紧急（7天内截止）
        - 50-79: 紧急（30天内截止）
        - 20-49: 一般（60天内截止）
        - 0-19: 不急（60天以上或Rolling）
        """
        deadline_str = job_data.get('deadline', '')

        # Rolling/ongoing 基础分
        if not deadline_str or deadline_str.lower() in ['rolling', 'ongoing', 'asap', 'immediately']:
            return 10.0

        try:
            # 尝试解析日期
            deadline = self._parse_deadline(deadline_str)
            if not deadline:
                return 10.0

            days_until = (deadline - datetime.now()).days

            # 越近分数越高
            if days_until <= 0:
                return 100.0  # 已过期或今天截止
            elif days_until <= 7:
                return 90.0  # 7天内
            elif days_until <= 14:
                return 80.0
            elif days_until <= 30:
                return 60.0
            elif days_until <= 60:
                return 40.0
            else:
                return max(10.0, 100 - days_until)  # 线性衰减

        except Exception as e:
            logger.warning(f"Failed to calculate urgency score: {e}")
            return 10.0

    def calculate_freshness_score(self, job_data: Dict) -> float:
        """
        计算新鲜度分数 (0-100)
        基于职位发布时间

        分数含义：
        - 90-100: 7天内发布
        - 70-89: 30天内发布
        - 50-69: 60天内发布
        - 0-49: 更早或未知
        """
        opened_str = job_data.get('opened', '')

        if not opened_str or opened_str in ['', 'Unknown', 'Not specified']:
            return 30.0  # 默认分数

        try:
            opened_date = self._parse_deadline(opened_str)
            if not opened_date:
                return 30.0

            days_since_open = (datetime.now() - opened_date).days

            # 越新分数越高
            if days_since_open <= 7:
                return 95.0
            elif days_since_open <= 30:
                return 75.0
            elif days_since_open <= 60:
                return 55.0
            elif days_since_open <= 90:
                return 40.0
            else:
                return max(10.0, 100 - days_since_open)

        except Exception as e:
            logger.warning(f"Failed to calculate freshness score: {e}")
            return 30.0

    def calculate_quality_score(self, job_data: Dict) -> float:
        """
        计算职位质量分数 (0-100)
        基于数据完整度和公司层级

        这个分数用于过滤低质量职位
        """
        score = 0.0

        # 数据完整度 (50分)
        required_fields = ['company', 'title', 'location', 'industry', 'apply_link', 'description']
        preferred_fields = ['salary', 'preferred_major', 'skills_tags', 'department', 'job_level']

        required_filled = sum(1 for field in required_fields if job_data.get(field))
        preferred_filled = sum(1 for field in preferred_fields if job_data.get(field))

        score += (required_filled / len(required_fields)) * 35
        score += (preferred_filled / len(preferred_fields)) * 15

        # 公司层级 (30分)
        company_info = job_data.get('company_info', {})
        company_tier = company_info.get('tier', 'Unknown') if isinstance(company_info, dict) else 'Unknown'
        if company_tier == 'Tier 1':
            score += 30
        elif company_tier == 'Tier 2':
            score += 22
        elif company_tier == 'Tier 3':
            score += 15
        else:
            score += 10

        # 职位清晰度 (20分) - 有详细描述的职位加分
        description = job_data.get('description', '')
        if description and len(description) > 200:
            score += 20
        elif description and len(description) > 100:
            score += 12
        elif description:
            score += 5

        return round(min(100, max(0, score)), 2)

    def calculate_matchability_score(self, job_data: Dict) -> float:
        """
        计算可匹配性分数 (0-100)
        表示这个职位有多少信息可以用于个性化匹配

        分数越高，说明有更多字段可以用来判断是否适合特定用户
        """
        score = 0.0

        # 签证信息 (20分) - 对国际学生最重要
        visa_mentioned = job_data.get('visa_mentioned', 'not_mentioned').lower()
        if visa_mentioned in ['explicit_yes', 'explicit_no', 'case_by_case']:
            score += 20
        elif job_data.get('visa_sponsorship'):
            score += 20

        # 学位要求 (20分)
        degree_min = job_data.get('degree_min', 'any')
        if degree_min and degree_min != 'any':
            score += 20

        # 目标年份 (15分)
        target_year = job_data.get('target_year', 'Any')
        if target_year and target_year != 'Any':
            score += 15

        # 技能标签 (20分) - 用于技能匹配
        skills = job_data.get('skills_tags', [])
        if skills and len(skills) > 0:
            score += min(20, len(skills) * 4)  # 最多20分

        # 专业偏好 (15分)
        majors = job_data.get('preferred_major', [])
        if majors and len(majors) > 0:
            score += 15

        # 目标受众 (10分)
        target_audience = job_data.get('target_audience', 'Not specified')
        if target_audience and target_audience != 'Not specified':
            score += 10

        return round(min(100, max(0, score)), 2)

    # ============================================================
    # Helper Functions
    # ============================================================

    def _score_deadline(self, deadline_str: str, weight: float = 30) -> float:
        """计算截止日期分数"""
        if not deadline_str or deadline_str.lower() in ['rolling', 'ongoing', 'asap']:
            return weight * 0.3  # Rolling 基础分

        try:
            deadline = self._parse_deadline(deadline_str)
            if not deadline:
                return weight * 0.3

            days_until = (deadline - datetime.now()).days

            # 越近分数越高
            if days_until <= 7:
                return weight * 1.0
            elif days_until <= 30:
                return weight * 0.8
            elif days_until <= 60:
                return weight * 0.5
            else:
                return weight * 0.3

        except Exception:
            return weight * 0.3

    def _parse_deadline(self, date_str: str) -> Optional[datetime]:
        """解析各种日期格式"""
        if not date_str:
            return None

        date_str = date_str.strip().lower()

        # 处理常见的日期格式
        formats = [
            '%Y-%m-%d',
            '%d/%m/%Y',
            '%d/%m/%y',
            '%Y/%m/%d',
            '%B %d, %Y',
            '%b %d, %Y',
            '%d %B %Y',
            '%d %b %Y',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue

        # 尝试解析相对日期 (e.g., "2 weeks from now")
        # 这里简化处理，实际可以使用 dateparser 库
        return None

    def _score_visa_sponsorship(self, job_data: Dict, weight: float = 20) -> float:
        """
        计算签证担保评分 (增强版)

        评分逻辑（优先级从高到低）：
        1. JD 明确提到提供签证 → 满分
        2. JD 明确说不提供签证 → 0分
        3. 历史数据库有数据 → 使用历史可能性评分
        4. JD 说 "case by case" → 中等分数
        5. 公司层级作为代理 → Tier 1 高分，Tier 3 低分
        6. 完全未知 → 默认中等分数

        Args:
            job_data: 职位数据
            weight: 该项的满分权重

        Returns:
            签证评分 (0-weight)
        """
        company_name = job_data.get('company', '')
        visa_mentioned = job_data.get('visa_mentioned', 'not_mentioned').lower()

        # 1. 如果 JD 明确提到签证，优先使用 JD 信息
        if visa_mentioned == 'explicit_yes' or job_data.get('visa_sponsorship', False):
            logger.debug(f"[Visa Scoring] {company_name}: JD explicitly mentions visa sponsorship → Full score")
            return weight
        elif visa_mentioned == 'explicit_no':
            logger.debug(f"[Visa Scoring] {company_name}: JD explicitly states NO visa → 0 score")
            return 0.0

        # 2. 如果历史数据库有数据，使用历史可能性评分
        if self.visa_db and company_name:
            visa_score = self.visa_db.get_visa_score(company_name, jd_explicit_visa=False)
            # 将历史数据库的评分 (0-20) 映射到权重
            normalized_score = (visa_score / 20.0) * weight

            company_info = self.visa_db.get_company(company_name)
            if company_info:
                logger.debug(f"[Visa Scoring] {company_name}: Using historical data (likelihood={company_info.visa_likelihood}, generosity={company_info.visa_generosity}) → {normalized_score:.1f}/{weight}")
            return normalized_score

        # 3. JD 说 case by case → 中等分数
        if visa_mentioned == 'case_by_case':
            logger.debug(f"[Visa Scoring] {company_name}: JD says case by case → Medium score")
            return weight * 0.5

        # 4. 使用公司层级作为代理评分
        company_info = job_data.get('company_info', {})
        company_tier = company_info.get('tier', 'Unknown') if isinstance(company_info, dict) else 'Unknown'

        if company_tier == 'Tier 1':
            logger.debug(f"[Visa Scoring] {company_name}: Using Tier 1 as proxy for visa likelihood → High score")
            return weight * 0.8
        elif company_tier == 'Tier 2':
            logger.debug(f"[Visa Scoring] {company_name}: Using Tier 2 as proxy → Medium score")
            return weight * 0.5
        elif company_tier == 'Tier 3':
            logger.debug(f"[Visa Scoring] {company_name}: Using Tier 3 as proxy → Low score")
            return weight * 0.2

        # 5. 完全未知 → 默认较低分数（对签证需求用户来说，未知=风险）
        logger.debug(f"[Visa Scoring] {company_name}: No visa info available → Default low score")
        return weight * 0.3

    def _score_company_tier(self, job_data: Dict, weight: float = 25) -> float:
        """
        计算公司层级评分

        优先从历史数据库获取公司层级，其次使用 AI 提取的数据

        Args:
            job_data: 职位数据
            weight: 该项的满分权重

        Returns:
            公司层级评分 (0-weight)
        """
        company_name = job_data.get('company', '')

        # 优先使用历史数据库的公司层级
        if self.visa_db and company_name:
            db_tier = self.visa_db.get_company_tier(company_name)
            if db_tier != 'Unknown':
                if db_tier == 'Tier 1':
                    logger.debug(f"[Tier Scoring] {company_name}: Historical tier = Tier 1 → Full score")
                    return weight
                elif db_tier == 'Tier 2':
                    logger.debug(f"[Tier Scoring] {company_name}: Historical tier = Tier 2 → Good score")
                    return weight * 0.72  # 18/25
                elif db_tier == 'Tier 3':
                    logger.debug(f"[Tier Scoring] {company_name}: Historical tier = Tier 3 → Basic score")
                    return weight * 0.48  # 12/25

        # 回退到 AI 提取的公司层级
        company_info = job_data.get('company_info', {})
        company_tier = company_info.get('tier', 'Unknown') if isinstance(company_info, dict) else 'Unknown'

        if company_tier == 'Tier 1':
            logger.debug(f"[Tier Scoring] {company_name}: AI-extracted tier = Tier 1 → Full score")
            return weight
        elif company_tier == 'Tier 2':
            logger.debug(f"[Tier Scoring] {company_name}: AI-extracted tier = Tier 2 → Good score")
            return weight * 0.72
        elif company_tier == 'Tier 3':
            logger.debug(f"[Tier Scoring] {company_name}: AI-extracted tier = Tier 3 → Basic score")
            return weight * 0.48
        else:
            logger.debug(f"[Tier Scoring] {company_name}: Unknown tier → Minimal score")
            return weight * 0.32  # 8/25


def score_job_sync(job_data: Dict) -> Dict[str, float]:
    """
    Synchronous wrapper for scoring a job

    Args:
        job_data: Job data dictionary

    Returns:
        Dictionary containing all scores
    """
    scorer = JobScorer()
    return scorer.calculate_all_scores(job_data)


# ============================================================
# Integration with Job Schema
# ============================================================

def enhance_job_with_scores(job_extraction) -> Dict:
    """
    增强 JobExtraction 对象，添加预计算分数

    这个函数应该在写入 Google Sheets 之前调用

    Args:
        job_extraction: JobExtraction Pydantic model

    Returns:
        Dictionary with original data plus scores
    """
    # Convert to dict if it's a Pydantic model
    if hasattr(job_extraction, 'model_dump'):
        job_dict = job_extraction.model_dump()
    elif hasattr(job_extraction, 'dict'):
        job_dict = job_extraction.dict()
    else:
        job_dict = job_extraction

    # Calculate all scores
    scorer = JobScorer()
    scores = scorer.calculate_all_scores(job_dict)

    # Add scores to job data
    job_dict.update({
        'priority_score': scores['priority_score'],
        'urgency_score': scores['urgency_score'],
        'freshness_score': scores['freshness_score'],
        'quality_score': scores['quality_score'],
        'matchability_score': scores['matchability_score'],
        'scores_calculated_at': datetime.now().isoformat(),
    })

    return job_dict


if __name__ == '__main__':
    # 测试用例
    logging.basicConfig(level=logging.DEBUG)

    # 测试场景1: JD 明确提到签证的职位
    test_job_explicit_visa = {
        'company': 'McKinsey & Company',
        'title': 'Consulting Graduate',
        'location': 'London, UK',
        'industry': 'Consulting',
        'apply_link': 'https://example.com/apply',
        'deadline': '2025-02-15',
        'opened': '2025-01-20',
        'visa_mentioned': 'explicit_yes',
        'visa_sponsorship': True,
        'salary': '£60,000 - £75,000',
        'description': 'Join our consulting team as a graduate consultant...',
        'degree_min': 'bachelor',
        'target_year': '2025',
        'skills_tags': ['Analysis', 'Problem Solving'],
        'preferred_major': ['Business', 'Economics'],
        'department': 'Consulting',
        'job_level': 'Entry',
        'work_mode': 'Hybrid',
        'target_audience': 'New Grad',
        'company_info': {
            'tier': 'Tier 1',
            'size_category': 'Large',
            'funding_stage': 'Private',
        }
    }

    # 测试场景2: JD 没有提到签证，但公司在历史数据库中（如 KPMG）
    test_job_historical_visa = {
        'company': 'KPMG',
        'title': 'Technology Consulting Graduate',
        'location': 'London, UK',
        'industry': 'Accounting/Consulting',
        'apply_link': 'https://example.com/apply',
        'deadline': '2025-03-01',
        'opened': '2025-01-15',
        'visa_mentioned': 'not_mentioned',  # JD 没有提到签证
        'visa_sponsorship': False,
        'salary': '£35,000 - £45,000',
        'description': 'Join KPMG as a technology consultant...',
        'degree_min': 'bachelor',
        'target_year': '2025',
        'skills_tags': ['Python', 'SQL', 'Communication'],
        'preferred_major': ['Computer Science', 'Information Systems'],
        'department': 'Technology',
        'job_level': 'Entry',
        'work_mode': 'Hybrid',
        'target_audience': 'New Grad',
        'company_info': {
            'tier': 'Unknown',  # AI 未能识别层级
            'size_category': 'Large',
        }
    }

    # 测试场景3: 未知公司，没有签证信息
    test_job_unknown_company = {
        'company': 'Unknown Startup Ltd',
        'title': 'Junior Developer',
        'location': 'London, UK',
        'industry': 'Technology',
        'apply_link': 'https://example.com/apply',
        'deadline': '2025-04-01',
        'opened': '2025-01-10',
        'visa_mentioned': 'not_mentioned',
        'visa_sponsorship': False,
        'salary': 'Competitive',
        'description': 'Join our startup as a junior developer...',
        'degree_min': 'any',
        'target_year': 'Any',
        'skills_tags': ['JavaScript', 'React'],
        'preferred_major': [],
        'department': 'Engineering',
        'job_level': 'Entry',
        'work_mode': 'On-site',
        'target_audience': 'Not specified',
        'company_info': {
            'tier': 'Unknown',
        }
    }

    print("=" * 70)
    print("Job Scoring with Visa History Database Integration")
    print("=" * 70)

    for i, (job, description) in enumerate([
        (test_job_explicit_visa, "JD Explicit Visa + McKinsey (Tier 1)"),
        (test_job_historical_visa, "No JD Visa + KPMG (Historical High)"),
        (test_job_unknown_company, "No JD Visa + Unknown Company (Fallback)"),
    ], 1):
        print(f"\n--- Test {i}: {description} ---")
        print(f"Company: {job['company']}")
        print(f"JD Visa: {job.get('visa_mentioned', 'N/A')}")

        scorer = JobScorer()
        scores = scorer.calculate_all_scores(job)

        print(f"\nScores:")
        print(f"  Priority Score:    {scores['priority_score']:.1f}/100 (排序用)")
        print(f"  Urgency Score:     {scores['urgency_score']:.1f}/100 (紧急程度)")
        print(f"  Freshness Score:   {scores['freshness_score']:.1f}/100 (新鲜度)")
        print(f"  Quality Score:     {scores['quality_score']:.1f}/100 (数据质量)")
        print(f"  Matchability Score:{scores['matchability_score']:.1f}/100 (匹配能力)")

    print("\n" + "=" * 70)
    print("Visa History Database Lookup Test")
    print("=" * 70)

    # 测试签证历史数据库查询
    try:
        from scraper.visa_history_manager import get_visa_history_db
        visa_db = get_visa_history_db()

        test_companies = ['McKinsey & Company', 'BCG', 'KPMG', 'Google', 'Unknown']
        print(f"\n{'Company':<30} {'Likelihood':<12} {'Tier':<10} {'Score (0-20)'}")
        print("-" * 70)
        for company in test_companies:
            company_info = visa_db.get_company(company)
            if company_info:
                print(f"{company:<30} {company_info.visa_likelihood:<12} {company_info.company_tier:<10} {visa_db.get_visa_score(company):.1f}")
            else:
                print(f"{company:<30} {'Unknown':<12} {'Unknown':<10} {visa_db.get_visa_score(company):.1f}")
    except ImportError as e:
        print(f"\nWarning: Could not import visa_history_manager: {e}")
