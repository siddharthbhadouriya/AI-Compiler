def design_system(intent):
    entities = []
    flows = []
    permissions = []

    features = intent.get("features", [])
    roles = intent.get("roles", [])

    # Authentication
    if "auth" in features:
        entities.append("User")
        flows.append("login")
        flows.append("signup")

    # CRM / Contacts
    if "contacts" in features:
        entities.append("Contact")
        flows.append("manage_contacts")

    # Dashboard
    if "dashboard" in features:
        flows.append("view_dashboard")

    # Analytics
    if "analytics" in features:
        flows.append("view_analytics")

    # Payments
    if "payments" in features:
        entities.append("Subscription")
        flows.append("process_payment")

    # Roles & permissions
    if "admin" in roles:
        permissions.append({
            "role": "admin",
            "access": ["analytics", "dashboard"]
        })

    permissions.append({
        "role": "user",
        "access": ["basic_features"]
    })

    return {
        "entities": list(set(entities)),
        "flows": list(set(flows)),
        "roles": roles,
        "permissions": permissions
    }