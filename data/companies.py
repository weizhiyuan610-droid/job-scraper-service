"""
Pre-built company database for common employers
Contains company info for major companies that international students often apply to
"""

# Pre-built company database with common employers
KNOWN_COMPANIES = {
    # --- Consulting ---
    "McKinsey & Company": {
        "domain": "mckinsey.com",
        "size_category": "Large",
        "employee_count": "30,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "New York, NY",
        "year_founded": "1926",
        "tier": "Tier 1",
        "website": "https://www.mckinsey.com"
    },
    "Boston Consulting Group": {
        "domain": "bcg.com",
        "size_category": "Large",
        "employee_count": "25,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "Boston, MA",
        "year_founded": "1963",
        "tier": "Tier 1",
        "website": "https://www.bcg.com"
    },
    "Bain & Company": {
        "domain": "bain.com",
        "size_category": "Large",
        "employee_count": "13,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "Boston, MA",
        "year_founded": "1973",
        "tier": "Tier 1",
        "website": "https://www.bain.com"
    },
    "Deloitte": {
        "domain": "deloitte.com",
        "size_category": "Enterprise",
        "employee_count": "400,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "London, UK",
        "year_founded": "1845",
        "tier": "Tier 1",
        "website": "https://www.deloitte.com"
    },
    "KPMG": {
        "domain": "kpmg.com",
        "size_category": "Enterprise",
        "employee_count": "265,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "Amstelveen, Netherlands",
        "year_founded": "1987",
        "tier": "Tier 1",
        "website": "https://www.kpmg.com"
    },
    "PwC": {
        "domain": "pwc.com",
        "size_category": "Enterprise",
        "employee_count": "360,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "London, UK",
        "year_founded": "1998",
        "tier": "Tier 1",
        "website": "https://www.pwc.com"
    },
    "EY": {
        "domain": "ey.com",
        "size_category": "Enterprise",
        "employee_count": "365,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "London, UK",
        "year_founded": "1989",
        "tier": "Tier 1",
        "website": "https://www.ey.com"
    },
    "Accenture": {
        "domain": "accenture.com",
        "size_category": "Enterprise",
        "employee_count": "700,000+",
        "funding_stage": "Public",
        "industry": "Consulting",
        "hq_location": "Dublin, Ireland",
        "year_founded": "1989",
        "tier": "Tier 2",
        "website": "https://www.accenture.com"
    },
    "Kearney": {
        "domain": "kearney.com",
        "size_category": "Large",
        "employee_count": "4,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "Chicago, IL",
        "year_founded": "1926",
        "tier": "Tier 2",
        "website": "https://www.kearney.com"
    },
    "Oliver Wyman": {
        "domain": "oliverwyman.com",
        "size_category": "Large",
        "employee_count": "6,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "New York, NY",
        "year_founded": "1983",
        "tier": "Tier 2",
        "website": "https://www.oliverwyman.com"
    },
    "L.E.K. Consulting": {
        "domain": "lek.com",
        "size_category": "Large",
        "employee_count": "2,000+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "London, UK",
        "year_founded": "1983",
        "tier": "Tier 2",
        "website": "https://www.lek.com"
    },
    "Roland Berger": {
        "domain": "rolandberger.com",
        "size_category": "Large",
        "employee_count": "2,500+",
        "funding_stage": "Private",
        "industry": "Consulting",
        "hq_location": "Munich, Germany",
        "year_founded": "1967",
        "tier": "Tier 2",
        "website": "https://www.rolandberger.com"
    },

    # --- Investment Banking ---
    "Goldman Sachs": {
        "domain": "goldmansachs.com",
        "size_category": "Enterprise",
        "employee_count": "40,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "New York, NY",
        "year_founded": "1869",
        "tier": "Tier 1",
        "website": "https://www.goldmansachs.com"
    },
    "JPMorgan Chase": {
        "domain": "jpmorganchase.com",
        "size_category": "Enterprise",
        "employee_count": "290,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "New York, NY",
        "year_founded": "1871",
        "tier": "Tier 1",
        "website": "https://www.jpmorgan.com"
    },
    "Morgan Stanley": {
        "domain": "morganstanley.com",
        "size_category": "Enterprise",
        "employee_count": "80,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "New York, NY",
        "year_founded": "1935",
        "tier": "Tier 1",
        "website": "https://www.morganstanley.com"
    },
    "Bank of America": {
        "domain": "bankofamerica.com",
        "size_category": "Enterprise",
        "employee_count": "210,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "Charlotte, NC",
        "year_founded": "1904",
        "tier": "Tier 1",
        "website": "https://www.bankofamerica.com"
    },
    "Citi": {
        "domain": "citi.com",
        "size_category": "Enterprise",
        "employee_count": "230,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "New York, NY",
        "year_founded": "1812",
        "tier": "Tier 1",
        "website": "https://www.citi.com"
    },
    "Credit Suisse": {
        "domain": "credit-suisse.com",
        "size_category": "Enterprise",
        "employee_count": "45,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "Zurich, Switzerland",
        "year_founded": "1856",
        "tier": "Tier 2",
        "website": "https://www.credit-suisse.com"
    },
    "UBS": {
        "domain": "ubs.com",
        "size_category": "Enterprise",
        "employee_count": "70,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "Zurich, Switzerland",
        "year_founded": "1862",
        "tier": "Tier 2",
        "website": "https://www.ubs.com"
    },
    "Barclays": {
        "domain": "barclays.com",
        "size_category": "Enterprise",
        "employee_count": "85,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "London, UK",
        "year_founded": "1690",
        "tier": "Tier 2",
        "website": "https://www.barclays.com"
    },
    "Deutsche Bank": {
        "domain": "db.com",
        "size_category": "Enterprise",
        "employee_count": "85,000+",
        "funding_stage": "Public",
        "industry": "Investment Banking",
        "hq_location": "Frankfurt, Germany",
        "year_founded": "1870",
        "tier": "Tier 2",
        "website": "https://www.db.com"
    },

    # --- Private Equity ---
    "Blackstone": {
        "domain": "blackstone.com",
        "size_category": "Large",
        "employee_count": "3,500+",
        "funding_stage": "Public",
        "industry": "Private Equity",
        "hq_location": "New York, NY",
        "year_founded": "1985",
        "tier": "Tier 1",
        "website": "https://www.blackstone.com"
    },
    "KKR": {
        "domain": "kkr.com",
        "size_category": "Large",
        "employee_count": "1,500+",
        "funding_stage": "Public",
        "industry": "Private Equity",
        "hq_location": "New York, NY",
        "year_founded": "1976",
        "tier": "Tier 1",
        "website": "https://www.kkr.com"
    },
    "Carlyle": {
        "domain": "carlyle.com",
        "size_category": "Large",
        "employee_count": "2,000+",
        "funding_stage": "Public",
        "industry": "Private Equity",
        "hq_location": "Washington, DC",
        "year_founded": "1987",
        "tier": "Tier 1",
        "website": "https://www.carlyle.com"
    },
    "TPG": {
        "domain": "tpg.com",
        "size_category": "Large",
        "employee_count": "1,000+",
        "funding_stage": "Public",
        "industry": "Private Equity",
        "hq_location": "Fort Worth, TX",
        "year_founded": "1992",
        "tier": "Tier 2",
        "website": "https://www.tpg.com"
    },
    "Apollo Global Management": {
        "domain": "apolloglobal.com",
        "size_category": "Large",
        "employee_count": "1,500+",
        "funding_stage": "Public",
        "industry": "Private Equity",
        "hq_location": "New York, NY",
        "year_founded": "1990",
        "tier": "Tier 2",
        "website": "https://www.apolloglobal.com"
    },
    "Bain Capital": {
        "domain": "baincapital.com",
        "size_category": "Large",
        "employee_count": "1,500+",
        "funding_stage": "Private",
        "industry": "Private Equity",
        "hq_location": "Boston, MA",
        "year_founded": "1984",
        "tier": "Tier 2",
        "website": "https://www.baincapital.com"
    },

    # --- Venture Capital ---
    "Sequoia Capital": {
        "domain": "sequoiacap.com",
        "size_category": "Mid",
        "employee_count": "200+",
        "funding_stage": "Private",
        "industry": "Venture Capital",
        "hq_location": "Menlo Park, CA",
        "year_founded": "1972",
        "tier": "Tier 1",
        "website": "https://www.sequoiacap.com"
    },
    "Andreessen Horowitz": {
        "domain": "a16z.com",
        "size_category": "Mid",
        "employee_count": "250+",
        "funding_stage": "Private",
        "industry": "Venture Capital",
        "hq_location": "Menlo Park, CA",
        "year_founded": "2009",
        "tier": "Tier 1",
        "website": "https://a16z.com"
    },
    "Accel": {
        "domain": "accel.com",
        "size_category": "Mid",
        "employee_count": "150+",
        "funding_stage": "Private",
        "industry": "Venture Capital",
        "hq_location": "Palo Alto, CA",
        "year_founded": "1983",
        "tier": "Tier 1",
        "website": "https://www.accel.com"
    },
    "Benchmark": {
        "domain": "benchmark.com",
        "size_category": "Small",
        "employee_count": "50+",
        "funding_stage": "Private",
        "industry": "Venture Capital",
        "hq_location": "San Francisco, CA",
        "year_founded": "1995",
        "tier": "Tier 2",
        "website": "https://www.benchmark.com"
    },
    "Index Ventures": {
        "domain": "indexventures.com",
        "size_category": "Mid",
        "employee_count": "100+",
        "funding_stage": "Private",
        "industry": "Venture Capital",
        "hq_location": "San Francisco, CA",
        "year_founded": "1996",
        "tier": "Tier 2",
        "website": "https://www.indexventures.com"
    },

    # --- Technology (Big Tech) ---
    "Google": {
        "domain": "google.com",
        "size_category": "Enterprise",
        "employee_count": "180,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Mountain View, CA",
        "year_founded": "1998",
        "tier": "Tier 1",
        "website": "https://www.google.com"
    },
    "Microsoft": {
        "domain": "microsoft.com",
        "size_category": "Enterprise",
        "employee_count": "220,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Redmond, WA",
        "year_founded": "1975",
        "tier": "Tier 1",
        "website": "https://www.microsoft.com"
    },
    "Amazon": {
        "domain": "amazon.com",
        "size_category": "Enterprise",
        "employee_count": "1,500,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Seattle, WA",
        "year_founded": "1994",
        "tier": "Tier 1",
        "website": "https://www.amazon.com"
    },
    "Apple": {
        "domain": "apple.com",
        "size_category": "Enterprise",
        "employee_count": "150,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Cupertino, CA",
        "year_founded": "1976",
        "tier": "Tier 1",
        "website": "https://www.apple.com"
    },
    "Meta": {
        "domain": "meta.com",
        "size_category": "Enterprise",
        "employee_count": "70,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Menlo Park, CA",
        "year_founded": "2004",
        "tier": "Tier 1",
        "website": "https://www.meta.com"
    },
    "Netflix": {
        "domain": "netflix.com",
        "size_category": "Large",
        "employee_count": "14,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Los Gatos, CA",
        "year_founded": "1997",
        "tier": "Tier 1",
        "website": "https://www.netflix.com"
    },
    "Tesla": {
        "domain": "tesla.com",
        "size_category": "Large",
        "employee_count": "140,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Austin, TX",
        "year_founded": "2003",
        "tier": "Tier 1",
        "website": "https://www.tesla.com"
    },
    "NVIDIA": {
        "domain": "nvidia.com",
        "size_category": "Large",
        "employee_count": "30,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Santa Clara, CA",
        "year_founded": "1993",
        "tier": "Tier 1",
        "website": "https://www.nvidia.com"
    },
    "Salesforce": {
        "domain": "salesforce.com",
        "size_category": "Enterprise",
        "employee_count": "80,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "San Francisco, CA",
        "year_founded": "1999",
        "tier": "Tier 1",
        "website": "https://www.salesforce.com"
    },
    "Adobe": {
        "domain": "adobe.com",
        "size_category": "Large",
        "employee_count": "25,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "San Jose, CA",
        "year_founded": "1982",
        "tier": "Tier 1",
        "website": "https://www.adobe.com"
    },
    "Oracle": {
        "domain": "oracle.com",
        "size_category": "Enterprise",
        "employee_count": "160,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Austin, TX",
        "year_founded": "1977",
        "tier": "Tier 1",
        "website": "https://www.oracle.com"
    },
    "IBM": {
        "domain": "ibm.com",
        "size_category": "Enterprise",
        "employee_count": "280,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Armonk, NY",
        "year_founded": "1911",
        "tier": "Tier 2",
        "website": "https://www.ibm.com"
    },
    "Intel": {
        "domain": "intel.com",
        "size_category": "Enterprise",
        "employee_count": "130,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Santa Clara, CA",
        "year_founded": "1968",
        "tier": "Tier 1",
        "website": "https://www.intel.com"
    },
    "AMD": {
        "domain": "amd.com",
        "size_category": "Large",
        "employee_count": "26,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Santa Clara, CA",
        "year_founded": "1969",
        "tier": "Tier 2",
        "website": "https://www.amd.com"
    },

    # --- Fintech ---
    "Stripe": {
        "domain": "stripe.com",
        "size_category": "Large",
        "employee_count": "8,000+",
        "funding_stage": "Series I",
        "industry": "Fintech",
        "hq_location": "San Francisco, CA",
        "year_founded": "2010",
        "tier": "Tier 1",
        "website": "https://www.stripe.com"
    },
    "Square": {
        "domain": "block.xyz",
        "size_category": "Large",
        "employee_count": "5,000+",
        "funding_stage": "Public",
        "industry": "Fintech",
        "hq_location": "San Francisco, CA",
        "year_founded": "2009",
        "tier": "Tier 1",
        "website": "https://www.squareup.com"
    },
    "PayPal": {
        "domain": "paypal.com",
        "size_category": "Enterprise",
        "employee_count": "30,000+",
        "funding_stage": "Public",
        "industry": "Fintech",
        "hq_location": "San Jose, CA",
        "year_founded": "1998",
        "tier": "Tier 2",
        "website": "https://www.paypal.com"
    },
    "Coinbase": {
        "domain": "coinbase.com",
        "size_category": "Large",
        "employee_count": "5,000+",
        "funding_stage": "Public",
        "industry": "Fintech",
        "hq_location": "Remote",
        "year_founded": "2012",
        "tier": "Tier 2",
        "website": "https://www.coinbase.com"
    },
    "Chime": {
        "domain": "chime.com",
        "size_category": "Large",
        "employee_count": "1,500+",
        "funding_stage": "Series E",
        "industry": "Fintech",
        "hq_location": "San Francisco, CA",
        "year_founded": "2012",
        "tier": "Tier 2",
        "website": "https://www.chime.com"
    },
    "Plaid": {
        "domain": "plaid.com",
        "size_category": "Mid",
        "employee_count": "1,000+",
        "funding_stage": "Series D",
        "industry": "Fintech",
        "hq_location": "San Francisco, CA",
        "year_founded": "2013",
        "tier": "Tier 2",
        "website": "https://www.plaid.com"
    },
    "Robinhood": {
        "domain": "robinhood.com",
        "size_category": "Large",
        "employee_count": "2,000+",
        "funding_stage": "Public",
        "industry": "Fintech",
        "hq_location": "Menlo Park, CA",
        "year_founded": "2013",
        "tier": "Tier 2",
        "website": "https://www.robinhood.com"
    },
    "Revolut": {
        "domain": "revolut.com",
        "size_category": "Large",
        "employee_count": "7,000+",
        "funding_stage": "Series F",
        "industry": "Fintech",
        "hq_location": "London, UK",
        "year_founded": "2015",
        "tier": "Tier 2",
        "website": "https://www.revolut.com"
    },
    "Wise": {
        "domain": "wise.com",
        "size_category": "Large",
        "employee_count": "4,000+",
        "funding_stage": "Public",
        "industry": "Fintech",
        "hq_location": "London, UK",
        "year_founded": "2011",
        "tier": "Tier 2",
        "website": "https://www.wise.com"
    },

    # --- FMCG ---
    "Procter & Gamble": {
        "domain": "pg.com",
        "size_category": "Enterprise",
        "employee_count": "100,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Cincinnati, OH",
        "year_founded": "1837",
        "tier": "Tier 1",
        "website": "https://www.pg.com"
    },
    "Unilever": {
        "domain": "unilever.com",
        "size_category": "Enterprise",
        "employee_count": "150,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "London, UK",
        "year_founded": "1929",
        "tier": "Tier 1",
        "website": "https://www.unilever.com"
    },
    "Nestlé": {
        "domain": "nestle.com",
        "size_category": "Enterprise",
        "employee_count": "270,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Vevey, Switzerland",
        "year_founded": "1866",
        "tier": "Tier 1",
        "website": "https://www.nestle.com"
    },
    "Coca-Cola": {
        "domain": "coca-colacompany.com",
        "size_category": "Enterprise",
        "employee_count": "700,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Atlanta, GA",
        "year_founded": "1892",
        "tier": "Tier 1",
        "website": "https://www.coca-colacompany.com"
    },
    "PepsiCo": {
        "domain": "pepsico.com",
        "size_category": "Enterprise",
        "employee_count": "300,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Purchase, NY",
        "year_founded": "1898",
        "tier": "Tier 1",
        "website": "https://www.pepsico.com"
    },
    "L'Oréal": {
        "domain": "loreal.com",
        "size_category": "Enterprise",
        "employee_count": "88,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Clichy, France",
        "year_founded": "1909",
        "tier": "Tier 1",
        "website": "https://www.loreal.com"
    },
    "Nike": {
        "domain": "nike.com",
        "size_category": "Enterprise",
        "employee_count": "80,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Beaverton, OR",
        "year_founded": "1964",
        "tier": "Tier 1",
        "website": "https://www.nike.com"
    },
    "Adidas": {
        "domain": "adidas.com",
        "size_category": "Enterprise",
        "employee_count": "60,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Herzogenaurach, Germany",
        "year_founded": "1949",
        "tier": "Tier 1",
        "website": "https://www.adidas.com"
    },

    # --- Engineering ---
    "Boeing": {
        "domain": "boeing.com",
        "size_category": "Enterprise",
        "employee_count": "150,000+",
        "funding_stage": "Public",
        "industry": "Engineering",
        "hq_location": "Arlington, VA",
        "year_founded": "1916",
        "tier": "Tier 1",
        "website": "https://www.boeing.com"
    },
    "Lockheed Martin": {
        "domain": "lockheedmartin.com",
        "size_category": "Enterprise",
        "employee_count": "115,000+",
        "funding_stage": "Public",
        "industry": "Engineering",
        "hq_location": "Bethesda, MD",
        "year_founded": "1995",
        "tier": "Tier 1",
        "website": "https://www.lockheedmartin.com"
    },
    "General Electric": {
        "domain": "ge.com",
        "size_category": "Enterprise",
        "employee_count": "170,000+",
        "funding_stage": "Public",
        "industry": "Engineering",
        "hq_location": "Boston, MA",
        "year_founded": "1892",
        "tier": "Tier 1",
        "website": "https://www.ge.com"
    },
    "Siemens": {
        "domain": "siemens.com",
        "size_category": "Enterprise",
        "employee_count": "300,000+",
        "funding_stage": "Public",
        "industry": "Engineering",
        "hq_location": "Munich, Germany",
        "year_founded": "1847",
        "tier": "Tier 1",
        "website": "https://www.siemens.com"
    },
    "SpaceX": {
        "domain": "spacex.com",
        "size_category": "Large",
        "employee_count": "12,000+",
        "funding_stage": "Private",
        "industry": "Engineering",
        "hq_location": "Hawthorne, CA",
        "year_founded": "2002",
        "tier": "Tier 1",
        "website": "https://www.spacex.com"
    },

    # --- Chinese Companies ---
    "Tencent": {
        "domain": "tencent.com",
        "size_category": "Enterprise",
        "employee_count": "110,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Shenzhen, China",
        "year_founded": "1998",
        "tier": "Tier 1",
        "website": "https://www.tencent.com"
    },
    "Alibaba": {
        "domain": "alibaba.com",
        "size_category": "Enterprise",
        "employee_count": "250,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Hangzhou, China",
        "year_founded": "1999",
        "tier": "Tier 1",
        "website": "https://www.alibaba.com"
    },
    "ByteDance": {
        "domain": "bytedance.com",
        "size_category": "Enterprise",
        "employee_count": "150,000+",
        "funding_stage": "Private",
        "industry": "Technology",
        "hq_location": "Beijing, China",
        "year_founded": "2012",
        "tier": "Tier 1",
        "website": "https://www.bytedance.com"
    },
    "Huawei": {
        "domain": "huawei.com",
        "size_category": "Enterprise",
        "employee_count": "200,000+",
        "funding_stage": "Private",
        "industry": "Technology",
        "hq_location": "Shenzhen, China",
        "year_founded": "1987",
        "tier": "Tier 1",
        "website": "https://www.huawei.com"
    },
    "Baidu": {
        "domain": "baidu.com",
        "size_category": "Enterprise",
        "employee_count": "45,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Beijing, China",
        "year_founded": "2000",
        "tier": "Tier 2",
        "website": "https://www.baidu.com"
    },
    "Xiaomi": {
        "domain": "mi.com",
        "size_category": "Enterprise",
        "employee_count": "35,000+",
        "funding_stage": "Public",
        "industry": "Technology",
        "hq_location": "Beijing, China",
        "year_founded": "2010",
        "tier": "Tier 2",
        "website": "https://www.mi.com"
    },
    "Shein": {
        "domain": "shein.com",
        "size_category": "Enterprise",
        "employee_count": "10,000+",
        "funding_stage": "Private",
        "industry": "FMCG",
        "hq_location": "Singapore",
        "year_founded": "2008",
        "tier": "Tier 2",
        "website": "https://www.shein.com"
    },
    "Temu": {
        "domain": "temu.com",
        "size_category": "Large",
        "employee_count": "10,000+",
        "funding_stage": "Public",
        "industry": "FMCG",
        "hq_location": "Boston, MA",
        "year_founded": "2022",
        "tier": "Tier 2",
        "website": "https://www.temu.com"
    },
    "TikTok": {
        "domain": "tiktok.com",
        "size_category": "Enterprise",
        "employee_count": "50,000+",
        "funding_stage": "Private",
        "industry": "Technology",
        "hq_location": "Los Angeles, CA / Singapore",
        "year_founded": "2016",
        "tier": "Tier 1",
        "website": "https://www.tiktok.com"
    },
}

# Company aliases for matching (common variations)
COMPANY_ALIASES = {
    # Google
    "Google": ["Google", "Alphabet", "Google Cloud"],
    # Meta
    "Meta": ["Meta", "Facebook", "Instagram", "WhatsApp"],
    # Amazon
    "Amazon": ["Amazon", "Amazon Web Services", "AWS"],
    # Microsoft
    "Microsoft": ["Microsoft", "MSFT", "Azure"],
    # Investment Banks
    "Goldman Sachs": ["Goldman Sachs", "Goldman", "GS"],
    "JPMorgan Chase": ["JPMorgan", "JPMorgan Chase", "J.P. Morgan", "JP Morgan"],
    "Morgan Stanley": ["Morgan Stanley", "MS"],
    "Credit Suisse": ["Credit Suisse", "CS"],
    # Consulting
    "McKinsey & Company": ["McKinsey", "McKinsey & Company"],
    "Boston Consulting Group": ["BCG", "Boston Consulting Group"],
    "Bain & Company": ["Bain", "Bain & Company"],
    "Deloitte": ["Deloitte", "Deloitte Touche Tohmatsu"],
    "KPMG": ["KPMG", "KPMG International", "Klynveld Peat Marwick Goerdeler"],
    "PwC": ["PwC", "PricewaterhouseCoopers", "Pricewaterhouse Coopers", "Price Waterhouse Coopers"],
    "EY": ["EY", "Ernst & Young", "Ernst Young"],
    # Tech
    "Stripe": ["Stripe", "Stripe, Inc"],
    "Square": ["Square", "Block, Inc (Square)"],
    # Chinese
    "ByteDance": ["ByteDance", "ByteDance Ltd", "TikTok"],
    "Alibaba": ["Alibaba Group", "Alibaba"],
}


def get_company_info(company_name: str) -> dict:
    """
    Get company info from pre-built database

    Args:
        company_name: Company name to search for

    Returns:
        Company info dict or None if not found
    """
    if not company_name:
        return None

    # Try exact match first
    if company_name in KNOWN_COMPANIES:
        return KNOWN_COMPANIES[company_name]

    # Try alias matching
    for canonical_name, aliases in COMPANY_ALIASES.items():
        if company_name in aliases:
            return KNOWN_COMPANIES[canonical_name]

    # Try partial match (for variations like "Google Cloud" → "Google")
    for known_name, info in KNOWN_COMPANIES.items():
        if company_name in known_name or known_name in company_name:
            return info

    return None


def find_similar_company(company_name: str, threshold: float = 0.6) -> list:
    """
    Find similar companies using fuzzy matching

    Args:
        company_name: Company name to search for
        threshold: Similarity threshold (0-1)

    Returns:
        List of (company_name, similarity_score, company_info) tuples
    """
    from difflib import SequenceMatcher

    results = []
    for known_name, info in KNOWN_COMPANIES.items():
        similarity = SequenceMatcher(None, company_name.lower(), known_name.lower()).ratio()
        if similarity >= threshold:
            results.append((known_name, similarity, info))

    # Sort by similarity descending
    results.sort(key=lambda x: x[1], reverse=True)
    return results


# Company size categories for AI inference
SIZE_CATEGORIES = {
    "Startup": "1-50 employees",
    "Small": "51-200 employees",
    "Mid": "201-1000 employees",
    "Large": "1001-10000 employees",
    "Enterprise": "10000+ employees"
}

# Funding stages for AI inference
FUNDING_STAGES = {
    "Pre-seed": "Pre-revenue, idea stage",
    "Seed": "Early stage, first funding",
    "Series A": "Product-market fit",
    "Series B": "Scaling",
    "Series C": "Expansion",
    "Series D+": "Late stage",
    "Public": "Publicly traded",
    "Private": "Privately held"
}
