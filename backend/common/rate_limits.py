RATE_LIMITS = {
    "DEVELOPER": {
        "read": 100,
        "write": 20,
    },
    "MANAGER": {
        "read": 200,
        "write": 50,
    },
    "AUDITOR": {
        "read": None,  # unlimited
        "write": 0,
    },
}
