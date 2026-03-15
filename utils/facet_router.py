#!/usr/bin/env python3
"""
Facet router — determines which facet is most relevant for a given user query.
Returns one of the facet identifiers (lowercase, underscored).
"""

FACET_KEYWORDS = {
    'researcher': [
        'research', 'study', 'investigate', 'pattern', 'evidence', 'source', 'literature',
        'history', 'philosophy', 'theory', 'hypothesis', 'anomaly', 'data', 'analysis',
        'compare', 'contrast', 'review', 'survey', 'literature review'
    ],
    'designer': [
        'design', 'space', 'layout', 'floor plan', 'interior', 'furnishings',
        'finishes', 'material', 'palette', 'lighting', 'proportion', 'scale', 'geometry',
        'sacred geometry', 'vastu', 'feng shui', 'biogeometry', 'radiesthesia', 'energetic',
        'cosmic', 'harmony', 'aesthetic', 'venue', 'building', 'construction', 'renovation',
        'antique', 'vintage', 'milan', 'paris', 'jaipur', 'marrakech', 'high point',
        'urban planning', 'bioregional', 'landscape', 'MEP', 'structural', 'code compliance',
        'color theory', 'fabric', 'lighting design', 'space planning', 'concept', 'mockup',
        'schematic', 'design development', 'render', '3d model', 'cad', 'bim'
    ],
    'marketing_social_media_strategist': [
        'marketing', 'social media', 'campaign', 'audience', 'engagement', 'follower',
        'brand', 'content', 'story', 'narrative', 'viral', 'trend', 'platform', 'tiktok',
        'instagram', 'linkedin', 'x.com', 'thread', 'reels', 'fyp', 'micro-community',
        'authentic', 'voice', 'tone', 'strategy', 'analytics', 'conversion', 'kpi',
        'hashtag', 'influencer', 'community', 'algorithm', 'reach', 'impressions'
    ],
    'coder_mathematician': [
        'code', 'programming', 'algorithm', 'function', 'class', 'data structure',
        'mathematics', 'proof', 'invariant', 'theorem', 'complexity', 'performance',
        'optimization', 'test', 'type system', 'monad', 'fold', 'transform', 'fft',
        'backtesting', 'simulation', 'quantitative', 'statistics', 'probability',
        'bug', 'debug', 'refactor', 'clean code', 'readability', 'maintainability'
    ],
    'legal_researcher': [
        'legal', 'law', 'attorney', 'compliance', 'regulation', 'contract', 'clause',
        'liability', 'trust', 'estate', 'will', 'probate', 'tax', 'irs', 'sec', 'fda',
        'gdpr', 'privacy', 'policy', 'terms', 'license', 'intellectual property',
        'copyright', 'trademark', 'patent', 'incorporate', 'llc', 'corporation',
        'governance', 'risk', 'advocate', 'negotiate', 'settlement', 'dispute',
        'case law', 'statute', 'precedent', 'due process'
    ],
    'health_wellness_companion': [
        'medical', 'health', 'doctor', 'healer', 'therapy', 'counseling', 'symptom',
        'diagnosis', 'treatment', 'prescription', 'lab', 'test', 'results', 'wellness',
        'holistic', 'integrative', 'spiritual', 'energy', 'aura', 'subtle body',
        'emotion', 'trauma', 'healing', 'self-advocacy', 'patient', 'client',
        'referral', 'support group', 'mind-body', 'meditation', 'prayer', 'logion',
        'nutrition', 'exercise', 'longevity', 'preventive care', 'mental health'
    ],
    'financial_analyst': [
        'finance', 'financial', 'investment', 'invest', 'trading', 'trader', 'portfolio',
        'asset allocation', 'risk', 'return', 'diversification', 'tax', 'estate planning',
        'trust', 'inheritance', 'legacy', 'generation', 'wealth', 'abundance', 'money',
        'budget', 'cash flow', 'insurance', 'hedge', 'monte carlo', 'backtest',
        'scenario', 'probabilistic', 'longevity', 'charitable', 'gifting', '529',
        'roth', 'ira', '401k', 'stock', 'bond', 'real estate', 'crypto', 'tokenized',
        'analysis', 'model', 'forecast', 'cashflow', 'debt', 'savings'
    ]
}

def detect_facet(query: str) -> str:
    """Return the most likely facet identifier based on keyword matches."""
    query_lower = query.lower()
    scores = {facet: 0 for facet in FACET_KEYWORDS}
    for facet, keywords in FACET_KEYWORDS.items():
        for kw in keywords:
            if kw in query_lower:
                scores[facet] += 1
    # Pick the facet with highest score; if tie, default to 'researcher'
    best = max(scores, key=scores.get)
    if scores[best] == 0:
        return 'researcher'
    return best

if __name__ == "__main__":
    import sys
    q = " ".join(sys.argv[1:]) or "What is the derivative of x^2?"
    print(detect_facet(q))
