"""
Golden evaluation set for the Medic RAG chatbot.

Each entry is one turn: a realistic user question plus the "reference" (ground
truth) answer a correct system should give. RAGAS uses `reference` for the
metrics that need a ground truth (LLMContextRecall, LLMContextPrecisionWithReference,
AnswerCorrectness); metrics that don't need one (Faithfulness, ResponseRelevancy)
simply ignore it.

Questions are drawn from the three knowledge sources the app actually embeds:
  - documents/Medical_list_with_specs.csv (device catalogue / pricing)
  - documents/FAQ.docx
  - documents/Log and sign.docx

Keep this file editable so the eval set can grow as the product grows. Every
sample should be independently answerable from the retrieved documents alone
(single-turn, no dependency on prior chat history) since `rag.chatbot.chat`
is evaluated turn-by-turn.
"""

GOLDEN_SET = [
    # --- CSV: device catalogue -------------------------------------------------
    {
        "question": "What is the price in INR of the Defib-Max defibrillator, model Defib-7456X?",
        "reference": "The Defib-Max (model Defib-7456X) defibrillator is priced at INR 110,000.",
    },
    {
        "question": "Which device class does the Defibrillator category fall under?",
        "reference": "Defibrillators in the catalogue are listed as Class C devices.",
    },
    {
        "question": "What is a Digital Blood Pressure Monitor used for and what class is it?",
        "reference": (
            "A Digital Blood Pressure Monitor is a Class B device used to measure a "
            "patient's blood pressure."
        ),
    },
    {
        "question": "What is the price of the BP-Basic blood pressure monitor with model number BP-9962A?",
        "reference": "The BP-Basic (model BP-9962A) blood pressure monitor is priced at INR 1,200.",
    },
    {
        "question": "How many different coagulation analyzer listings are in the catalogue?",
        "reference": "There are 13 Coagulation Analyzer (Class C) listings in the catalogue.",
    },

    # --- FAQ.docx ---------------------------------------------------------------
    {
        "question": "Do I need a prescription to buy items from the store?",
        "reference": (
            "It depends on the product. Over-the-counter items, basic first-aid "
            "supplies, and standard mobility aids don't need a prescription, but "
            "restricted devices like CPAP machines or prescription medications "
            "require a valid prescription uploaded before checkout."
        ),
    },
    {
        "question": "How long does prescription verification take after I upload it?",
        "reference": "The verification team reviews uploaded prescriptions within 1-2 business days.",
    },
    {
        "question": "Can a clinic or hospital place bulk orders?",
        "reference": (
            "Yes, healthcare facilities can register for a B2B/Business-Institutional "
            "account with wholesale pricing, providing their medical license or tax "
            "ID for verification."
        ),
    },
    {
        "question": "Is the shipping packaging discreet for medical orders?",
        "reference": (
            "Yes, all consumer orders ship in standard, unbranded boxes or mailers "
            "with no logos or descriptions indicating the medical contents."
        ),
    },
    {
        "question": "What is the return policy for opened sterile wound care items?",
        "reference": (
            "Opened sanitary products, sterile supplies, wound care items, and "
            "prescription products cannot be returned due to health and hygiene "
            "regulations."
        ),
    },
    {
        "question": "What should I do if my medical device arrives damaged?",
        "reference": (
            "Contact support within 48 hours of delivery and keep the original "
            "packaging; a prepaid return label will be issued and a replacement or "
            "full refund processed."
        ),
    },

    # --- Log and sign.docx -------------------------------------------------------
    {
        "question": "What information is required to sign up for an account?",
        "reference": (
            "Sign up requires first and last name, email address, a username if "
            "applicable, and a secure password that is confirmed, plus accepting "
            "the Terms of Service and Privacy Policy."
        ),
    },
    {
        "question": "What should I do if I forget my password?",
        "reference": (
            "Click 'Forgot Password?' on the login page, enter your account email, "
            "then use the password reset link sent to your email to set a new "
            "secure password."
        ),
    },
    {
        "question": "Is two-factor authentication required to log in?",
        "reference": (
            "Two-factor authentication is optional; if enabled, you must enter the "
            "security code sent to your device or authenticator app after entering "
            "your credentials."
        ),
    },

    # --- Out-of-scope: should trigger the "no info" fallback ---------------------
    {
        "question": "What is the current weather forecast for Mumbai?",
        "reference": (
            "The assistant should state it does not have that information, since "
            "weather is unrelated to the medical equipment and account documents it "
            "has access to."
        ),
    },
]
