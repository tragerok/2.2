def get_subscription_status(user_id):
    # Заглушка для API: статус подписки
    return {"active": True, "till": "2025-12-31"}

def buy_subscription(user_id, sub_code):
    # Заглушка для покупки подписки
    return True

def activate_hwid_code(user_id, code):
    # Заглушка для активации HWID/кода: успех только для "TESTCODE"
    if code == "TESTCODE":
        return {"success": True}
    return {"success": False}
