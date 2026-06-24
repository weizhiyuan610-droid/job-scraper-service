"""
添加新公司到签证历史数据库

用法：
python add_visa_companies.py
"""
from scraper.visa_history_manager import CompanyVisaHistory, get_visa_history_db

# 新公司列表
NEW_COMPANIES = [
    {
        'company_name': 'Netflix',
        'company_name_variants': [],
        'industry': 'Technology',
        'company_tier': 'Tier 1',
        'visa_likelihood': 'high',
        'visa_generosity': '大方',
        'visa_reliability': 'proven',
        'core_visa_departments': ['Engineering', 'Product', 'Data Science'],
        'historical_notes': 'Known for sponsoring visas for technical roles.',
    },
    # 在这里添加更多公司...
]

def add_companies():
    db = get_visa_history_db()
    
    added_count = 0
    for company_data in NEW_COMPANIES:
        company = CompanyVisaHistory.from_dict(company_data)
        
        # 检查是否已存在
        existing = db.get_company(company.company_name)
        if existing:
            print(f"⚠️  {company.company_name} 已存在，跳过")
            continue
        
        db.add_company(company)
        print(f"✅ 添加: {company.company_name} ({company.visa_likelihood}, {company.company_tier})")
        added_count += 1
    
    if added_count > 0:
        # 导出更新后的数据
        db.export_to_json('company_visa_history.json')
        print(f"\n📝 已导出 company_visa_history.json ({added_count} 家新公司)")
    else:
        print("\n没有添加新公司")

if __name__ == '__main__':
    add_companies()
