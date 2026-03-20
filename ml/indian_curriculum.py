# ml/indian_curriculum.py
# Complete Indian curriculum map for LearnFlow
# Covers all major streams: PCM (JEE), PCB (NEET), Commerce, Arts, University
# Difficulty scale: 1.0 (easiest) → 5.0 (hardest)
# Chapter counts based on NCERT + CBSE/ISC syllabus

INDIAN_CURRICULUM = {

    # ─────────────────────────────────────────
    # PCM — Science stream (JEE aspirants)
    # ─────────────────────────────────────────
    "PCM": {
        "Physics": {
            "Physical World":                   1.5,
            "Units and Measurements":           2.0,
            "Kinematics":                       3.8,
            "Laws of Motion":                   4.0,
            "Work Energy Power":                3.5,
            "System of Particles":              3.8,
            "Rotational Motion":                4.8,
            "Gravitation":                      3.2,
            "Properties of Matter":             3.0,
            "Thermodynamics":                   4.2,
            "Kinetic Theory of Gases":          3.5,
            "Oscillations":                     4.0,
            "Waves":                            3.8,
            "Electrostatics":                   4.5,
            "Current Electricity":              4.2,
            "Magnetic Effects of Current":      4.0,
            "Magnetism":                        3.5,
            "Electromagnetic Induction":        4.5,
            "Alternating Current":              4.0,
            "Electromagnetic Waves":            2.8,
            "Ray Optics":                       3.8,
            "Wave Optics":                      4.2,
            "Dual Nature of Matter":            3.8,
            "Atoms and Nuclei":                 4.0,
            "Semiconductors":                   3.5,
            "Communication Systems":            2.5,
        },
        "Chemistry": {
            "Basic Concepts of Chemistry":      3.0,
            "Structure of Atom":                3.5,
            "Classification of Elements":       3.2,
            "Chemical Bonding":                 4.0,
            "States of Matter":                 3.2,
            "Thermodynamics":                   4.2,
            "Equilibrium":                      4.5,
            "Redox Reactions":                  3.8,
            "Hydrogen":                         2.5,
            "s-Block Elements":                 2.8,
            "p-Block Elements":                 4.0,
            "Organic Chemistry Basics":         4.0,
            "Hydrocarbons":                     3.8,
            "Environmental Chemistry":          2.0,
            "Solid State":                      3.8,
            "Solutions":                        3.5,
            "Electrochemistry":                 4.3,
            "Chemical Kinetics":                4.2,
            "Surface Chemistry":                3.0,
            "d and f Block Elements":           4.0,
            "Coordination Compounds":           4.5,
            "Haloalkanes and Haloarenes":       3.8,
            "Alcohols Phenols Ethers":          3.8,
            "Aldehydes and Ketones":            4.5,
            "Carboxylic Acids":                 3.8,
            "Amines":                           4.0,
            "Biomolecules":                     3.2,
            "Polymers":                         2.8,
            "Chemistry in Everyday Life":       2.0,
        },
        "Mathematics": {
            "Sets and Relations":               2.8,
            "Complex Numbers":                  4.2,
            "Quadratic Equations":              3.8,
            "Sequences and Series":             3.5,
            "Permutation and Combination":      4.0,
            "Binomial Theorem":                 3.8,
            "Straight Lines":                   3.5,
            "Circles":                          3.8,
            "Conic Sections":                   4.5,
            "Limits and Continuity":            4.0,
            "Differentiation":                  4.2,
            "Application of Derivatives":       4.3,
            "Integration":                      4.8,
            "Application of Integrals":         4.2,
            "Differential Equations":           4.5,
            "Matrices":                         3.8,
            "Determinants":                     4.0,
            "Vectors":                          4.0,
            "3D Geometry":                      4.3,
            "Probability":                      4.2,
            "Statistics":                       3.0,
            "Mathematical Reasoning":           2.5,
            "Linear Programming":               3.2,
            "Trigonometry":                     3.8,
            "Inverse Trigonometry":             3.5,
        }
    },

    # ─────────────────────────────────────────
    # PCB — Science stream (NEET aspirants)
    # ─────────────────────────────────────────
    "PCB": {
        "Physics": {
            "Physical World":                   1.5,
            "Kinematics":                       3.5,
            "Laws of Motion":                   3.8,
            "Work Energy Power":                3.2,
            "Rotational Motion":                4.0,
            "Gravitation":                      3.0,
            "Properties of Bulk Matter":        3.2,
            "Thermodynamics":                   3.8,
            "Oscillations":                     3.5,
            "Waves":                            3.5,
            "Electrostatics":                   4.2,
            "Current Electricity":              4.0,
            "Magnetic Effects":                 3.8,
            "Electromagnetic Induction":        4.0,
            "Ray Optics":                       4.0,
            "Wave Optics":                      3.8,
            "Modern Physics":                   4.2,
            "Semiconductors":                   3.0,
        },
        "Chemistry": {
            "Basic Concepts":                   3.0,
            "Atomic Structure":                 3.5,
            "Chemical Bonding":                 3.8,
            "States of Matter":                 3.0,
            "Thermodynamics":                   3.8,
            "Equilibrium":                      4.2,
            "Redox":                            3.5,
            "Hydrogen":                         2.5,
            "s-Block Elements":                 2.8,
            "p-Block Elements":                 4.0,
            "d and f Block":                    4.0,
            "Coordination Compounds":           4.3,
            "Organic Chemistry Basics":         3.8,
            "Hydrocarbons":                     3.5,
            "Haloalkanes":                      3.8,
            "Alcohols and Phenols":             3.5,
            "Aldehydes and Ketones":            4.0,
            "Carboxylic Acids":                 3.5,
            "Amines":                           3.8,
            "Biomolecules":                     3.0,
            "Polymers":                         2.8,
            "Chemistry in Everyday Life":       2.0,
        },
        "Biology": {
            "The Living World":                 2.5,
            "Biological Classification":        3.0,
            "Plant Kingdom":                    3.5,
            "Animal Kingdom":                   3.8,
            "Morphology of Plants":             3.2,
            "Anatomy of Plants":                3.5,
            "Structural Organisation Animals":  3.2,
            "Cell Structure and Function":      3.5,
            "Biomolecules":                     3.8,
            "Cell Division":                    4.0,
            "Transport in Plants":              3.5,
            "Mineral Nutrition":                3.2,
            "Photosynthesis":                   4.0,
            "Respiration in Plants":            3.8,
            "Plant Growth":                     3.0,
            "Digestion and Absorption":         3.2,
            "Breathing and Gas Exchange":       3.5,
            "Body Fluids and Circulation":      3.8,
            "Excretion":                        3.5,
            "Locomotion and Movement":          3.2,
            "Neural Control":                   4.2,
            "Chemical Coordination":            4.0,
            "Reproduction in Plants":           3.5,
            "Human Reproduction":               3.8,
            "Reproductive Health":              3.0,
            "Genetics and Mendel":              4.5,
            "Molecular Basis of Inheritance":   4.8,
            "Evolution":                        3.5,
            "Human Health and Disease":         3.2,
            "Microbes in Human Welfare":        3.0,
            "Biotechnology Principles":         4.0,
            "Biotechnology Applications":       3.8,
            "Ecosystem":                        3.2,
            "Biodiversity":                     2.8,
            "Environmental Issues":             2.5,
        }
    },

    # ─────────────────────────────────────────
    # Commerce stream
    # ─────────────────────────────────────────
    "Commerce": {
        "Accountancy": {
            "Introduction to Accounting":       2.5,
            "Theory Base of Accounting":        3.0,
            "Journal and Ledger":               3.2,
            "Trial Balance":                    3.5,
            "Depreciation":                     3.8,
            "Provisions and Reserves":          3.5,
            "Bills of Exchange":                4.0,
            "Financial Statements":             4.0,
            "Accounts from Incomplete Records": 4.2,
            "Partnership Accounts":             4.5,
            "Reconstitution of Partnership":    4.8,
            "Dissolution of Partnership":       4.5,
            "Company Accounts":                 4.2,
            "Issue of Shares":                  4.0,
            "Issue of Debentures":              4.2,
            "Cash Flow Statement":              4.0,
            "Financial Analysis":               3.8,
            "Ratio Analysis":                   3.8,
        },
        "Business Studies": {
            "Nature and Purpose of Business":   2.5,
            "Forms of Business Organisation":   3.0,
            "Private Public and Global":        3.0,
            "Business Services":                2.8,
            "Emerging Modes of Business":       2.5,
            "Social Responsibility":            2.8,
            "Formation of Company":             3.5,
            "Sources of Business Finance":      3.8,
            "Small Business":                   3.0,
            "Internal Trade":                   3.2,
            "International Business":           3.5,
            "Nature of Management":             3.0,
            "Planning":                         3.2,
            "Organising":                       3.5,
            "Staffing":                         3.0,
            "Directing":                        3.2,
            "Controlling":                      3.5,
            "Financial Management":             4.0,
            "Financial Markets":                3.8,
            "Marketing Management":             3.5,
            "Consumer Protection":              2.8,
        },
        "Economics": {
            "Introduction to Microeconomics":   2.5,
            "Consumer Equilibrium":             3.5,
            "Demand":                           3.2,
            "Elasticity of Demand":             3.8,
            "Production Function":              3.8,
            "Cost":                             4.0,
            "Revenue":                          3.5,
            "Producer Equilibrium":             4.0,
            "Supply and Elasticity":            3.5,
            "Market Equilibrium":               4.2,
            "Non Competitive Markets":          4.2,
            "Introduction to Macroeconomics":   2.5,
            "National Income":                  4.0,
            "Money and Banking":                3.8,
            "Income Determination":             4.2,
            "Government Budget":                3.5,
            "Balance of Payments":              4.0,
            "Foreign Exchange":                 3.8,
        },
        "Mathematics": {
            "Relations and Functions":          3.0,
            "Logarithm":                        2.8,
            "Matrices":                         3.5,
            "Determinants":                     3.8,
            "Differentiation":                  4.0,
            "Application of Derivatives":       3.8,
            "Integration":                      4.2,
            "Application of Integrals":         4.0,
            "Differential Equations":           4.0,
            "Linear Programming":               3.5,
            "Probability":                      4.0,
            "Index Numbers":                    3.2,
            "Time Series":                      3.5,
            "Linear Regression":                3.8,
        }
    },

    # ─────────────────────────────────────────
    # Arts / Humanities stream
    # ─────────────────────────────────────────
    "Arts": {
        "History": {
            "Bricks Beads and Bones":           3.0,
            "Kings Farmers and Towns":          3.2,
            "Kinship Caste and Class":          3.5,
            "Thinkers Beliefs and Buildings":   3.2,
            "Through the Eyes of Travellers":   3.0,
            "Bhakti Sufi Traditions":           3.2,
            "An Imperial Capital Vijayanagara": 3.5,
            "Peasants Zamindars and State":     3.5,
            "Kings and Chronicles":             3.2,
            "Colonialism and Countryside":      3.8,
            "Rebels and the Raj":               3.8,
            "Colonial Cities":                  3.5,
            "Mahatma Gandhi and Nationalism":   4.0,
            "Understanding Partition":          4.0,
            "Framing the Constitution":         4.2,
        },
        "Political Science": {
            "Cold War Era":                     3.5,
            "End of Bipolarity":                3.2,
            "US Hegemony":                      3.5,
            "Alternative Centres of Power":     3.2,
            "South Asia and Neighbours":        3.5,
            "International Organisations":      3.2,
            "Security in Contemporary World":   3.5,
            "Environment and Natural Resources":3.2,
            "Globalisation":                    3.8,
            "Nation Building":                  3.8,
            "Era of One Party Dominance":       3.5,
            "Politics of Planned Development":  3.8,
            "India External Relations":         3.5,
            "Challenges to Congress System":    3.8,
            "Crisis of Democratic Order":       4.0,
            "Rise of Popular Movements":        3.5,
            "Regional Aspirations":             3.8,
            "Recent Developments":              3.5,
        },
        "Geography": {
            "Human Geography":                  3.0,
            "World Population":                 3.2,
            "Human Development":                3.5,
            "Primary Activities":               3.2,
            "Secondary Activities":             3.5,
            "Tertiary and Quaternary":          3.2,
            "Transport and Communication":      3.5,
            "International Trade":              3.8,
            "India Population":                 3.5,
            "Migration":                        3.2,
            "Human Settlements":                3.0,
            "Land Resources":                   3.2,
            "Water Resources":                  3.5,
            "Mineral and Energy Resources":     3.8,
            "Manufacturing Industries":         3.5,
            "Planning and Sustainable Dev":     3.8,
        },
        "Psychology": {
            "What is Psychology":               2.5,
            "Methods of Enquiry":               3.0,
            "Human Development":                3.2,
            "Sensory Processes":                3.5,
            "States of Consciousness":          3.2,
            "Learning":                         3.8,
            "Human Memory":                     4.0,
            "Thinking and Problem Solving":     4.0,
            "Motivation and Emotion":           3.5,
            "Intelligence Testing":             3.8,
            "Personality":                      3.5,
            "Psychological Disorders":          4.0,
            "Therapeutic Approaches":           3.8,
            "Attitudes and Social Cognition":   3.5,
            "Social Influence and Group":       3.5,
        }
    },

    # ─────────────────────────────────────────
    # University — Engineering / CS (Placements)
    # ─────────────────────────────────────────
    "University": {
        "Data Structures": {
            "Arrays and Strings":               3.0,
            "Linked Lists":                     3.5,
            "Stacks and Queues":                3.2,
            "Trees":                            4.3,
            "Binary Search Trees":              4.2,
            "Heaps":                            4.0,
            "Graphs":                           4.7,
            "Hashing":                          3.8,
            "Tries":                            4.2,
            "Segment Trees":                    4.8,
        },
        "Algorithms": {
            "Time and Space Complexity":        3.5,
            "Sorting Algorithms":               3.8,
            "Searching Algorithms":             3.2,
            "Recursion and Backtracking":       4.5,
            "Divide and Conquer":               4.2,
            "Greedy Algorithms":                4.3,
            "Dynamic Programming":              4.9,
            "Graph Algorithms":                 4.7,
            "String Algorithms":                4.3,
            "Bit Manipulation":                 4.0,
        },
        "DBMS": {
            "ER Model":                         3.2,
            "Relational Model":                 3.5,
            "SQL Basics":                       3.0,
            "Advanced SQL":                     3.8,
            "Normalization":                    4.2,
            "Transactions and ACID":            4.0,
            "Concurrency Control":              4.3,
            "Indexing and Hashing":             4.0,
            "Query Optimization":               4.5,
        },
        "Operating Systems": {
            "Process Management":               4.0,
            "CPU Scheduling":                   4.2,
            "Process Synchronization":          4.5,
            "Deadlocks":                        4.3,
            "Memory Management":                4.2,
            "Virtual Memory":                   4.5,
            "File Systems":                     3.8,
            "IO Systems":                       3.5,
        },
        "Computer Networks": {
            "Network Models OSI TCP":           3.5,
            "Physical Layer":                   3.0,
            "Data Link Layer":                  3.8,
            "Network Layer IP":                 4.0,
            "Transport Layer TCP UDP":          4.2,
            "Application Layer HTTP DNS":       3.8,
            "Network Security":                 4.0,
            "Socket Programming":               4.2,
        },
        "System Design": {
            "Scalability Basics":               4.0,
            "Load Balancing":                   4.2,
            "Caching":                          4.3,
            "Database Design":                  4.5,
            "Microservices":                    4.5,
            "Message Queues":                   4.3,
            "CAP Theorem":                      4.5,
            "Distributed Systems":              4.8,
            "API Design":                       4.0,
            "Rate Limiting":                    4.0,
        }
    }
}

# ─────────────────────────────────────────────────────────────
# Helper functions — used throughout the app
# ─────────────────────────────────────────────────────────────

def get_all_streams() -> list:
    """Returns list of all available streams."""
    return list(INDIAN_CURRICULUM.keys())


def get_subjects_for_stream(stream: str) -> list:
    """Returns list of subjects for a given stream."""
    return list(INDIAN_CURRICULUM.get(stream, {}).keys())


def get_topics_for_subject(stream: str, subject: str) -> list:
    """Returns list of topics for a given subject in a stream."""
    return list(INDIAN_CURRICULUM.get(stream, {}).get(subject, {}).keys())


def get_difficulty(stream: str, subject: str, topic: str) -> float:
    """
    Returns difficulty score (1.0-5.0) for a topic.
    Defaults to 3.0 (medium) if topic not found.
    """
    return INDIAN_CURRICULUM.get(stream, {}).get(subject, {}).get(topic, 3.0)


def get_total_chapters(stream: str, subject: str) -> int:
    """Returns total number of topics/chapters for a subject."""
    return len(INDIAN_CURRICULUM.get(stream, {}).get(subject, {}))


def get_hard_topics(stream: str, subject: str, threshold: float = 4.0) -> list:
    """
    Returns list of topics harder than the threshold.
    Useful for flagging high-risk chapters in the UI.
    """
    subject_map = INDIAN_CURRICULUM.get(stream, {}).get(subject, {})
    return [
        topic for topic, diff in subject_map.items()
        if diff >= threshold
    ]


def get_subject_avg_difficulty(stream: str, subject: str) -> float:
    """Returns average difficulty of all topics in a subject."""
    subject_map = INDIAN_CURRICULUM.get(stream, {}).get(subject, {})
    if not subject_map:
        return 3.0
    return round(sum(subject_map.values()) / len(subject_map), 2)


def get_stream_summary(stream: str) -> dict:
    """
    Returns a full summary of a stream:
    subjects, total chapters, avg difficulty per subject.
    """
    summary = {}
    for subject in get_subjects_for_stream(stream):
        summary[subject] = {
            "total_chapters":   get_total_chapters(stream, subject),
            "avg_difficulty":   get_subject_avg_difficulty(stream, subject),
            "hardest_topics":   get_hard_topics(stream, subject, threshold=4.5)
        }
    return summary


# ─────────────────────────────────────────────────────────────
# Exam date context — used by backlog model
# ─────────────────────────────────────────────────────────────

INDIAN_EXAM_CALENDAR = {
    "JEE Mains Session 1":   {"month": 1,  "typical_day": 20},
    "JEE Mains Session 2":   {"month": 4,  "typical_day": 5},
    "JEE Advanced":          {"month": 5,  "typical_day": 25},
    "NEET UG":               {"month": 5,  "typical_day": 5},
    "CBSE Board Class 12":   {"month": 2,  "typical_day": 15},
    "CBSE Board Class 10":   {"month": 2,  "typical_day": 20},
    "ISC Class 12":          {"month": 2,  "typical_day": 12},
    "University Semester 1": {"month": 11, "typical_day": 15},
    "University Semester 2": {"month": 4,  "typical_day": 20},
}


def get_exam_calendar() -> dict:
    """Returns the full Indian exam calendar."""
    return INDIAN_EXAM_CALENDAR