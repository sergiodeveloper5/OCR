{
    "name": "Base LLM",
    "version": "18.0.1.0.0",
    "category": "Technical",
    "summary": "Base module for LLM integrations",
    "sequence": 10,
    "description": """
        Base module for Large Language Model integrations.
        Provides a unified interface for different LLM providers like:
        - Groq
        - OpenAI
        - Anthropic
        - Custom providers
    """,
    "author": "Sergio Vadillo",
    "website": "https://www.yourcompany.com",
    "depends": ["base", "mail"],
    "data": [
        "security/ir.model.access.csv",
        "views/llm_provider_views.xml",
        "data/llm_provider_data.xml",
    ],
    "external_dependencies": {
        "python": ["requests"],
    },
    "installable": True,
    "application": False,
    "auto_install": False,
}
